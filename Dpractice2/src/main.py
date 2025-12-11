#!/usr/bin/env python3
"""
批量重命名图片脚本 - 主程序入口
"""

import os
import sys
import argparse
from pathlib import Path
import logging

logging.basicConfig(
    level = logging.INFO,
    format = '%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description = '批量重命名图片文件工具',
        formatter_class = argparse.ArgumentDefaultsHelpFormatter,
        epilog = """
        示例:
          %(prog)s ./photos --pattern sequential --start 1
          %(prog)s ./images --pattern prefix --prefix "vacation_"
          %(prog)s ./pics --dry-run --verbose 
        """
    )
    # 必需参数
    parser.add_argument(
        'directory',
        type = str,
        help = '要处理的图片目录路径')
    # 重命名模式参数
    parser.add_argument(
        '-p','--pattern',
        type = str,
        choices = ['sequential', 'prefix', 'suffix', 'replace', 'regex'],
        default = 'sequential',
        help = '重命名模式 (默认: sequential)'
    )
    # 可选参数
    parser.add_argument(
        '--prefix',
        type = str,
        default = '',
        help = '添加前缀'
    )
    parser.add_argument(
        '--suffix',
        type = str,
        default = '',
        help = '添加后缀'
    )
    parser.add_argument(
        '-s', '--start',
        type = int,
        default= 1 ,
        help='起始编号 (默认: 1)'
    )
    parser.add_argument(
        '-d', '--digits',
        type = int,
        default = 3,
        help = '编号位数 (默认: 3)'
    )
    parser.add_argument(
        '-e', '--extensions',
        type = str,
        default = 'jpg, jpeg, png, gif, bmp, webp',
        help = '支持的图片扩展名，用逗号分隔 (默认: jpg, jpeg, png, gif, bmp, webp)'
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

    return parser.parse_args()


def main():
    """主函数"""
    logger.info("=== 批量图片重命名工具 ===")
    try:
        args = parse_arguments()

        if args.verbose:
            logger.info(f"参数解析完成:")
            logger.info(f"  目录: {args.directory}")
            logger.info(f"  模式: {args.pattern}")
            logger.info(f"  起始编号: {args.start}")
            logger.info(f"  编号位数: {args.digits}")
            logger.info(f"  预览模式: {args.dry_run}")

        # 检查目录是否存在
        dir_path = Path(args.directory).expanduser().resolve()
        if not dir_path.exists():
            logger.info(f"错误:目录 {args.directory}不存在")
            sys.exit(1)
        if not dir_path.is_dir():
            logger.info(f"错误:{args.directory}不是目录")

        logger.info(f"正在处理目录：{dir_path.absolute()}")
        logger.info("脚本准备就绪！")

    except KeyboardInterrupt:
        logger.error("\n\n用户中断操作")
        sys.exit(0)
    except Exception as e:
        logger.error(f"发生错误：{e}")

if __name__ == "__main__":
# python Dpractice2/src/main.py ~/Downloads
# python Dpractice2/src/main.py D:\Automation_Test_Engineer\python_learning\test --dry-run --verbose
    main()