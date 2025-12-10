# !/usr/bin/env python3
"""
自动整理文件脚本
支持按扩展名、日期、类型等多种方式整理文件
"""

import os
import shutil
import sys
import re
import datetime
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import argparse
import json
import logging
from collections import defaultdict

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FileOrganizer:
    """文件整理器"""

    # 默认文件类型分类
    DEFAULT_CATEGORIES = {
        '文档': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.xls', '.xlsx', '.ppt', '.pptx'],
        '图片': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.tiff'],
        '视频': ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm'],
        '音频': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'],
        '压缩文件': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
        '程序代码': ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.php', '.json', '.xml'],
        '可执行文件': ['.exe', '.msi', '.bat', '.sh', '.app'],
        '字体文件': ['.ttf', '.otf', '.woff', '.woff2'],
        '配置文件': ['.ini', '.cfg', '.conf', '.yaml', '.yml'],
        '电子书': ['.epub', '.mobi', '.azw3']
    }

    def __init__(self, source_dir: str, target_dir: str = None):
        """
        初始化整理器

        Args:
            source_dir: 源目录路径
            target_dir: 目标目录路径（默认为源目录）
        """
        self.source_dir = Path(source_dir).expanduser().resolve()
        self.target_dir = Path(target_dir).expanduser().resolve() if target_dir else self.source_dir

        if not self.source_dir.exists():
            raise FileNotFoundError(f"源目录不存在: {self.source_dir}")

        if not self.target_dir.exists():
            self.target_dir.mkdir(parents=True, exist_ok=True)

        self.categories = self.DEFAULT_CATEGORIES.copy()
        self.duplicates = []

    def load_custom_categories(self, config_file: str):
        """加载自定义分类配置"""
        config_path = Path(config_file)
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    custom_categories = json.load(f)
                self.categories.update(custom_categories)
                logger.info(f"已加载自定义分类配置: {config_file}")
            except Exception as e:
                logger.error(f"加载配置文件失败: {e}")

    def get_file_category(self, file_path: Path) -> str:
        """根据扩展名获取文件分类"""
        suffix = file_path.suffix.lower()

        for category, extensions in self.categories.items():
            if suffix in extensions:
                return category

        # 未分类的文件
        return '其他文件'

    def get_file_hash(self, file_path: Path) -> str:
        """计算文件的MD5哈希值"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.error(f"计算文件哈希失败 {file_path}: {e}")
            return ""

    def organize_by_category(self, dry_run: bool = False, delete_duplicates: bool = False):
        """
        按文件类型整理

        Args:
            dry_run: 试运行，不实际移动文件
            delete_duplicates: 删除重复文件
        """
        logger.info(f"开始按类型整理文件: {self.source_dir}")

        file_count = 0
        duplicate_count = 0
        moved_count = 0
        hashes = {}

        # 遍历源目录
        for item in self.source_dir.rglob('*'):
            if item.is_file() and not item.name.startswith('.'):
                file_count += 1

                # 跳过目标目录中的文件（避免循环）
                if self.target_dir in item.parents:
                    continue

                # 计算文件哈希（用于去重）
                file_hash = self.get_file_hash(item)

                # 检查重复文件
                if delete_duplicates and file_hash:
                    if file_hash in hashes:
                        duplicate_count += 1
                        self.duplicates.append((item, hashes[file_hash]))
                        if not dry_run:
                            try:
                                item.unlink()
                                logger.info(f"删除重复文件: {item}")
                            except Exception as e:
                                logger.error(f"删除文件失败 {item}: {e}")
                        continue
                    hashes[file_hash] = item

                # 获取分类
                category = self.get_file_category(item)
                target_folder = self.target_dir / category

                # 创建目标文件夹
                if not target_folder.exists() and not dry_run:
                    target_folder.mkdir(parents=True, exist_ok=True)

                # 构建目标路径
                target_path = target_folder / item.name

                # 处理文件名冲突
                counter = 1
                while target_path.exists():
                    stem = item.stem
                    suffix = item.suffix
                    target_path = target_folder / f"{stem}_{counter}{suffix}"
                    counter += 1

                # 移动文件
                if not dry_run:
                    try:
                        shutil.move(str(item), str(target_path))
                        moved_count += 1
                        logger.info(f"移动文件: {item.name} -> {category}/")
                    except Exception as e:
                        logger.error(f"移动文件失败 {item}: {e}")
                else:
                    logger.info(f"[试运行] 将移动: {item.name} -> {category}/")

        logger.info(f"整理完成！共处理 {file_count} 个文件，移动 {moved_count} 个，发现 {duplicate_count} 个重复文件")
        return moved_count

    def organize_by_date(self, date_format: str = "%Y-%m", dry_run: bool = False):
        """
        按日期整理文件

        Args:
            date_format: 日期格式，如 "%Y-%m" (年-月), "%Y-%m-%d" (年-月-日)
            dry_run: 试运行
        """
        logger.info(f"开始按日期整理文件: {self.source_dir}")

        moved_count = 0

        for item in self.source_dir.rglob('*'):
            if item.is_file() and not item.name.startswith('.'):
                # 获取文件修改时间
                mtime = item.stat().st_mtime
                date_str = datetime.datetime.fromtimestamp(mtime).strftime(date_format)

                # 创建日期文件夹
                target_folder = self.target_dir / date_str
                if not target_folder.exists() and not dry_run:
                    target_folder.mkdir(parents=True, exist_ok=True)

                # 移动文件
                target_path = target_folder / item.name

                # 处理文件名冲突
                counter = 1
                while target_path.exists():
                    stem = item.stem
                    suffix = item.suffix
                    target_path = target_folder / f"{stem}_{counter}{suffix}"
                    counter += 1

                if not dry_run:
                    try:
                        shutil.move(str(item), str(target_path))
                        moved_count += 1
                        logger.info(f"移动文件: {item.name} -> {date_str}/")
                    except Exception as e:
                        logger.error(f"移动文件失败 {item}: {e}")
                else:
                    logger.info(f"[试运行] 将移动: {item.name} -> {date_str}/")

        logger.info(f"按日期整理完成！共移动 {moved_count} 个文件")
        return moved_count

    def organize_by_size(self, size_limits: List[int] = None, dry_run: bool = False):
        """
        按文件大小整理

        Args:
            size_limits: 大小阈值列表 [小文件上限, 中文件上限]，单位MB
            dry_run: 试运行
        """
        if size_limits is None:
            size_limits = [10, 100]  # 10MB以下为小文件，10-100MB为中文件，100MB以上为大文件

        logger.info(f"开始按大小整理文件: {self.source_dir}")

        size_categories = ['小文件', '中文件', '大文件']
        moved_count = 0

        for item in self.source_dir.rglob('*'):
            if item.is_file() and not item.name.startswith('.'):
                size_mb = item.stat().st_size / (1024 * 1024)

                # 确定分类
                if size_mb <= size_limits[0]:
                    category = size_categories[0]
                elif size_mb <= size_limits[1]:
                    category = size_categories[1]
                else:
                    category = size_categories[2]

                # 创建目标文件夹
                target_folder = self.target_dir / category
                if not target_folder.exists() and not dry_run:
                    target_folder.mkdir(parents=True, exist_ok=True)

                # 移动文件
                target_path = target_folder / item.name

                # 处理文件名冲突
                counter = 1
                while target_path.exists():
                    stem = item.stem
                    suffix = item.suffix
                    target_path = target_folder / f"{stem}_{counter}{suffix}"
                    counter += 1

                if not dry_run:
                    try:
                        shutil.move(str(item), str(target_path))
                        moved_count += 1
                        logger.info(f"移动文件: {item.name} ({size_mb:.1f}MB) -> {category}/")
                    except Exception as e:
                        logger.error(f"移动文件失败 {item}: {e}")
                else:
                    logger.info(f"[试运行] 将移动: {item.name} ({size_mb:.1f}MB) -> {category}/")

        logger.info(f"按大小整理完成！共移动 {moved_count} 个文件")
        return moved_count

    def clean_empty_folders(self, dry_run: bool = False):
        """清理空文件夹"""
        logger.info("开始清理空文件夹...")

        deleted_count = 0
        for root, dirs, files in os.walk(self.source_dir, topdown=False):
            for dir_name in dirs:
                dir_path = Path(root) / dir_name
                try:
                    if not any(dir_path.iterdir()):  # 文件夹为空
                        if not dry_run:
                            dir_path.rmdir()
                            logger.info(f"删除空文件夹: {dir_path}")
                        else:
                            logger.info(f"[试运行] 将删除空文件夹: {dir_path}")
                        deleted_count += 1
                except Exception as e:
                    logger.error(f"删除文件夹失败 {dir_path}: {e}")

        logger.info(f"清理完成！共删除 {deleted_count} 个空文件夹")
        return deleted_count

    def create_symlinks(self, organize_dir: str):
        """
        创建符号链接（适用于已整理的目录）

        Args:
            organize_dir: 已整理的目录
        """
        organize_path = Path(organize_dir)
        if not organize_path.exists():
            logger.error(f"整理目录不存在: {organize_dir}")
            return

        links_dir = self.source_dir / "文件索引"
        links_dir.mkdir(exist_ok=True)

        for item in organize_path.rglob('*'):
            if item.is_file():
                link_path = links_dir / item.name

                # 处理文件名冲突
                counter = 1
                while link_path.exists():
                    stem = item.stem
                    suffix = item.suffix
                    link_path = links_dir / f"{stem}_{counter}{suffix}"
                    counter += 1

                try:
                    link_path.symlink_to(item)
                    logger.info(f"创建符号链接: {link_path.name}")
                except Exception as e:
                    logger.error(f"创建符号链接失败 {item.name}: {e}")


def create_config_file(config_path: str = "file_organizer_config.json"):
    """创建配置文件模板"""
    config = {
        "自定义分类": {
            "设计文件": [".psd", ".ai", ".sketch", ".fig"],
            "数据库文件": [".db", ".sqlite", ".mdb"],
            "日志文件": [".log", ".txt"]
        },
        "整理规则": {
            "按类型整理": True,
            "按日期整理": False,
            "日期格式": "%Y-%m",
            "删除重复文件": True,
            "清理空文件夹": True
        }
    }

    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    logger.info(f"配置文件已创建: {config_path}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='自动整理文件脚本')
    parser.add_argument('source', help='源目录路径')
    parser.add_argument('-t', '--target', help='目标目录路径（默认同源目录）')
    parser.add_argument('-m', '--mode', choices=['type', 'date', 'size', 'all'],
                        default='type', help='整理模式: type(按类型), date(按日期), size(按大小), all(全部)')
    parser.add_argument('-c', '--config', help='配置文件路径')
    parser.add_argument('-d', '--date-format', default='%Y-%m',
                        help='日期格式 (默认: %%Y-%%m, 如 2024-01)')
    parser.add_argument('-s', '--size-limits', type=int, nargs=2,
                        default=[10, 100], help='大小阈值 [小文件上限 中文件上限] MB')
    parser.add_argument('--dry-run', action='store_true',
                        help='试运行，不实际移动文件')
    parser.add_argument('--delete-duplicates', action='store_true',
                        help='删除重复文件')
    parser.add_argument('--clean-empty', action='store_true',
                        help='清理空文件夹')
    parser.add_argument('--create-config', action='store_true',
                        help='创建配置文件模板')
    parser.add_argument('--create-links', help='为已整理的目录创建符号链接')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='详细输出')

    args = parser.parse_args()

    # 设置日志级别
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # 创建配置文件
    if args.create_config:
        create_config_file()
        return

    try:
        # 初始化整理器
        organizer = FileOrganizer(args.source, args.target)

        # 加载配置文件
        if args.config:
            organizer.load_custom_categories(args.config)

        # 执行整理
        if args.mode in ['type', 'all']:
            organizer.organize_by_category(
                dry_run=args.dry_run,
                delete_duplicates=args.delete_duplicates
            )

        if args.mode in ['date', 'all']:
            organizer.organize_by_date(
                date_format=args.date_format,
                dry_run=args.dry_run
            )

        if args.mode in ['size', 'all']:
            organizer.organize_by_size(
                size_limits=args.size_limits,
                dry_run=args.dry_run
            )

        # 清理空文件夹
        if args.clean_empty:
            organizer.clean_empty_folders(dry_run=args.dry_run)

        # 创建符号链接
        if args.create_links:
            organizer.create_symlinks(args.create_links)

        if not args.dry_run:
            logger.info("文件整理完成！")
        else:
            logger.info("试运行完成！")

    except Exception as e:
        logger.error(f"整理过程中出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()