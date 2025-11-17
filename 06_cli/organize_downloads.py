#!/usr/bin/env python3
"""
organize_downloads.py

最小可用版本：只打印参数，不移动文件
"""

import sys
import argparse
from pathlib import Path
import shutil
import logging
import time
from unittest.mock import DEFAULT

# 在文件顶部定义分类表
DEFAULT_CATEGORIES = {
    "images": ["jpg","png"],
    "pdf": ["pdf"],
    "other": []
}

logging.basicConfig(
    level = logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# def parse_args():
#     """解析命令行参数"""
#     p = argparse.ArgumentParser(description="整理下载文件夹")
#     p.add_argument("--src", "-s", required = True
#                    , help="源文件路径")
#     return p.parse_args()

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--src", "-s", required=True)
    p.add_argument("--dry-run", action = "store_true",
                   help = "只打印，不移动")
    p.add_argument("--recursive", "-r", action = "store_true",
                   help = "递归子文件夹")
    return p.parse_args()

def list_files(src:Path, recursive:bool = False):
    """返回文件生成器"""
    logger.info(f"\n正在扫描{src}")
    # 遍历目录下所有文件和子目录
    # for p in src.iterdir():
    #     # 如果是文件
    #     if p.is_file():
    #         logger.info(f"  发现文件{p.name}")

    if recursive:
        # 递归模式：使用 rglob 遍历所有子目录
        for p in src.rglob("*"):
            if p.is_file():
                logger.debug(f"  发现文件: {p.relative_to(src)}")
                yield p  # ← 关键：yield 产生值
    else:
        # 非递归：只遍历当前目录
        for p in src.iterdir():
            if p.is_file():
                logger.debug(f"  发现文件: {p.name}")
                yield p  # ← 关键：yield 产生值

def build_extension_map(categories):
    """构建反向映射：ext -> category"""
    # 初始化一个空字典，用于存储扩展名和类别的映射关系
    ext_map = {}
    # 遍历类别和扩展名列表
    for cat, exts in categories.items():
        # 遍历每个类别下的所有扩展名
        for ext in exts:
            # 以扩展名（统一为小写）为键，类别为值，添加到字典
            ext_map[ext.lower()] = cat
    # 返回扩展名到类别的映射字典
    return ext_map

def categorize_by_extension(ext: str,ext_map:dict):
    """根据扩展名返回类别"""
    # 将扩展名转小写，并去除左侧的点号
    ext = ext.lower().lstrip(".")
    # 在扩展名映射字典中查找类别。找不到则返回"other"
    return ext_map.get(ext, "other")

def safe_move_file(src: Path, dest_dir: Path, dry_run: bool = False):
    """
    安全移动：如果目标文件已存在，自动加(1)、(2)后缀
    """
    #创建类别文件夹
    dest_dir.mkdir(parents = True, exist_ok = True)

    target = dest_dir / src.name

    #处理文件名冲突
    if target.exists():
        # 文件名不带扩展名
        base = src.stem
        suffix = src.suffix
        counter = 1

        while True:
            new_name = f"{base}({counter}){suffix}"
            candidate = dest_dir / new_name
            if not candidate.exists():
                target = candidate
                break
            counter += 1

    if dry_run:
        logger.info(f"[DRY-RUN] 将移动: {src.name} -> {target.parent.name}/{target.name}")
    else:
        shutil.move(str(src), str(target))
        logger.info(f"已移动: {src.name} -> {target.parent.name}/{target.name}")

    return target

# def organize_folder(src: Path,categories:dict):
#     """核心函数：分类文件"""
#     # 构建扩展名到类别的映射字典
#     ext_map = build_extension_map(categories)
#     # 遍历源目录下所有文件和子目录
#     for file_path in src.iterdir():
#         # 如果不是文件（是文件夹等），则跳过
#         if not file_path.is_file():
#             continue
#
#         #获取文件扩展名（包括点号，如'.jpg'）
#         ext = file_path.suffix
#         # 根据扩展名获取类别
#         category = categorize_by_extension(ext,ext_map)
#
#         print(f"文件{file_path} -> 类别{category}")

def organize_folder(src: Path, categories: dict, dry_run: bool = False,
                    recursive: bool = False) -> tuple[int, int]:
    """核心函数：分类文件"""
    # 构建扩展名映射
    ext_map = build_extension_map(categories)

    files_iter = list_files(src, recursive)
    moved = 0
    processed = 0

    # for file_path in src.iterdir():
    #     if not file_path.is_file():
    #         continue

    for file_path in files_iter:
        processed += 1

        ext = file_path.suffix
        category = categorize_by_extension(ext,categories)

        dest_dir = src / "_sorted" / category

        try:
            safe_move_file(file_path, dest_dir, dry_run = dry_run)
            moved += 1
        except Exception as e:
            logger.error(f"移动失败 {file_path}: {e}")

    logger.info(f"处理完成: {processed} 个文件，移动 {moved} 个")
    return moved, processed

def main():
    class Args:
        src = "C:/Users./Administrator./Downloads"
        dry_run = True
        recursive = True

    # args = parse_args()
    args = Args()
    # 处理~路径
    #src = Path(args.src)
    src = Path(args.src).expanduser().resolve()

    if not src.exists():
        logger.error(f"文件夹不存在: {src}")
        sys.exit(1)
    #记时
    start = time.time()

    # logger.info(f"你要整理的文件夹是: {args.src}")
    # if not src.exists():
    #     logger.info(f"错误：文件夹不存在！")
    #     return
    #
    # list_files(src)

    moved, processed = organize_folder(src, DEFAULT_CATEGORIES,
                                       dry_run=args.dry_run,
                                       recursive=args.recursive)
    elapsed = time.time() - start
    logger.info(f"总耗时: {elapsed:.2f} 秒")

if __name__ == "__main__":
    main()