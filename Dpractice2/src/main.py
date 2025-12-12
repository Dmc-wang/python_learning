#!/usr/bin/env python3
"""
批量重命名图片脚本 - 主程序入口
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Optional

# 导入自定义模块
from file_finder import FileFinder
from renamer import Renamer


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='批量重命名图片文件工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s ./photos --pattern sequential --start 1
  %(prog)s ./images --pattern prefix --prefix "vacation_"
  %(prog)s ./pics --pattern replace --old "IMG" --new "Photo"
  %(prog)s ./photos --dry-run --verbose
        """
    )

    # 必需参数
    parser.add_argument(
        'directory',
        type=str,
        help='要处理的图片目录路径'
    )

    # 重命名模式参数
    parser.add_argument(
        '-p', '--pattern',
        type=str,
        choices=['sequential', 'prefix', 'suffix', 'replace', 'regex'],
        default='sequential',
        help='重命名模式 (默认: sequential)'
    )

    # 重命名选项
    parser.add_argument(
        '--prefix',
        type=str,
        default='',
        help='添加前缀'
    )

    parser.add_argument(
        '--suffix',
        type=str,
        default='',
        help='添加后缀'
    )

    parser.add_argument(
        '-s', '--start',
        type=int,
        default=1,
        help='起始编号 (默认: 1)'
    )

    parser.add_argument(
        '-d', '--digits',
        type=int,
        default=3,
        help='编号位数 (默认: 3)'
    )

    parser.add_argument(
        '--old',
        type=str,
        help='要替换的字符串（replace模式使用）'
    )

    parser.add_argument(
        '--new',
        type=str,
        help='替换后的字符串（replace模式使用）'
    )

    parser.add_argument(
        '--regex-pattern',
        type=str,
        help='正则表达式模式（regex模式使用）'
    )

    parser.add_argument(
        '--regex-replace',
        type=str,
        help='正则表达式替换文本（regex模式使用）'
    )

    # 文件筛选参数
    parser.add_argument(
        '-e', '--extensions',
        type=str,
        default='jpg,jpeg,png,gif,bmp,webp',
        help='支持的图片扩展名，用逗号分隔 (默认: jpg,jpeg,png,gif,bmp,webp)'
    )

    # 行为控制参数
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='预览模式，不实际执行重命名'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='显示详细输出'
    )

    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='递归处理子目录'
    )

    parser.add_argument(
        '--max-size',
        type=float,
        help='最大文件大小(MB)，超过此大小的文件将被忽略'
    )

    return parser.parse_args()


def validate_arguments(args):
    """验证命令行参数"""
    # 检查目录是否存在
    dir_path = Path(args.directory)
    if not dir_path.exists():
        print(f"错误: 目录 '{args.directory}' 不存在")
        sys.exit(1)

    if not dir_path.is_dir():
        print(f"错误: '{args.directory}' 不是目录")
        sys.exit(1)

    # 模式特定的参数验证
    if args.pattern == 'replace':
        if not args.old or not args.new:
            print("错误: replace模式需要 --old 和 --new 参数")
            sys.exit(1)

    if args.pattern == 'regex':
        if not args.regex_pattern:
            print("错误: regex模式需要 --regex-pattern 参数")
            sys.exit(1)
        if args.regex_replace is None:
            print("错误: regex模式需要 --regex-replace 参数")
            sys.exit(1)


def print_summary(results, dry_run=False):
    """打印操作摘要"""
    print("\n" + "=" * 50)
    if dry_run:
        print("预览模式摘要 (未实际执行重命名):")
    else:
        print("操作完成摘要:")

    print(f"  总文件数: {results['total']}")
    print(f"  成功重命名: {results['renamed']}")
    print(f"  跳过: {results['skipped']}")
    print(f"  错误: {results['errors']}")
    print("=" * 50)


def main():
    """主函数"""
    print("=== 批量图片重命名工具 ===")

    try:
        # 解析命令行参数
        args = parse_arguments()

        # 验证参数
        validate_arguments(args)

        # 显示参数信息
        if args.verbose:
            print(f"参数解析完成:")
            print(f"  目录: {args.directory}")
            print(f"  模式: {args.pattern}")
            print(f"  递归搜索: {args.recursive}")
            print(f"  预览模式: {args.dry_run}")

        print(f"\n正在处理目录: {Path(args.directory).absolute()}")

        # 1. 查找图片文件
        print("\n1. 查找图片文件...")
        file_finder = FileFinder(args.extensions)
        file_finder.verbose = args.verbose

        image_files = file_finder.find_image_files(args.directory, args.recursive)

        if args.max_size:
            image_files = file_finder.filter_files(image_files, args.max_size)

        if not image_files:
            print("警告: 未找到符合条件的图片文件")
            sys.exit(0)

        print(f"找到 {len(image_files)} 个图片文件")

        # 2. 创建重命名计划
        print("\n2. 创建重命名计划...")
        renamer = Renamer(args.verbose)

        rename_plan = []

        if args.pattern == 'sequential':
            rename_plan = renamer.rename_sequential(
                image_files, args.start, args.digits, args.prefix, args.suffix
            )

        elif args.pattern == 'prefix':
            if not args.prefix:
                print("错误: prefix模式需要 --prefix 参数")
                sys.exit(1)
            rename_plan = renamer.rename_with_prefix(image_files, args.prefix)

        elif args.pattern == 'suffix':
            if not args.suffix:
                print("错误: suffix模式需要 --suffix 参数")
                sys.exit(1)
            rename_plan = renamer.rename_with_suffix(image_files, args.suffix)

        elif args.pattern == 'replace':
            rename_plan = renamer.rename_replace(image_files, args.old, args.new)

        elif args.pattern == 'regex':
            rename_plan = renamer.rename_regex(
                image_files, args.regex_pattern, args.regex_replace
            )

        if not rename_plan:
            print("警告: 没有需要重命名的文件")
            sys.exit(0)

        # 3. 执行重命名
        print(f"\n3. {'预览' if args.dry_run else '执行'}重命名操作...")

        # 显示重命名计划
        print(f"\n重命名计划 ({len(rename_plan)} 个文件):")
        for old_path, new_path in rename_plan[:5]:  # 只显示前5个
            print(f"  {old_path.name} -> {new_path.name}")
        if len(rename_plan) > 5:
            print(f"  ... 还有 {len(rename_plan) - 5} 个文件")

        # 确认操作（如果不是预览模式）
        if not args.dry_run:
            confirm = input("\n确认执行重命名？(y/N): ")
            if confirm.lower() != 'y':
                print("操作已取消")
                sys.exit(0)

        # 执行重命名
        results = renamer.execute_rename(rename_plan, args.dry_run)

        # 4. 显示摘要
        print_summary(results, args.dry_run)

        if args.dry_run:
            print("\n提示: 使用 --dry-run 参数进行预览，移除该参数以实际执行")

    except KeyboardInterrupt:
        print("\n\n用户中断操作")
        sys.exit(0)
    except Exception as e:
        print(f"\n发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()