#!/usr/bin/env python3
"""
自动整理文件脚本 - 整体完善
"""

from typing import List
import datetime
import shutil
import hashlib
from pathlib import Path
import logging
import os
from tqdm import tqdm
import argparse

# 设置日志
logging.basicConfig(
    level = logging.INFO,
    format= '%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FileOrganizer:
    """文件整理器核心类"""

    #类常量：默认文件分类
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
                target_dir: 目标目录路径
        """
        # 将路径字符串转换为Path对象，并解析~和绝对路径,路径三件套
        self.source_dir = Path(source_dir).expanduser().resolve()
        self.target_dir = Path(target_dir).expanduser().resolve() if (
            target_dir) else self.source_dir

        fh = logging.FileHandler(self.target_dir / "organizer.log", encoding="utf-8")
        fh.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        logger.addHandler(fh)

        # 验证源目录存在性
        if not self.source_dir.exists():
            raise FileNotFoundError(f'源目录不存在：{self.source_dir}')

        if not self.target_dir.exists():
            self.target_dir.mkdir(parents=True, exist_ok=True)

        # 实例属性：分类规则和重复文件记录
        self.categories = self.DEFAULT_CATEGORIES.copy()
        self.duplicates= []

    def _move_atom(self, src: Path, dst: Path) -> None:
        """同盘用 rename，跨盘用 copy2+unlink，失败回滚"""
        try:
            if src.stat().st_dev == dst.stat().st_dev:  # 同盘设备号相同
                src.rename(dst)
            else:
                shutil.copy2(src, dst)
                src.unlink()
        except Exception:
            dst.unlink(missing_ok=True)
            raise

    def get_file_category(self, file_path: Path) -> str:
        """
        根据扩展名获取文件分类
        Args:
            file_path: 文件路径对象
        Returns:
            分类名称字符串
        """
        # 获取小写扩展名（如.pdf）
        suffix = file_path.suffix.lower()

        # 遍历分类字典，查找匹配的扩展名
        for category_n, extensions in self.categories.items():
            if suffix in extensions:
                return category_n

        return '其他文件'

    def organize_by_category(self, dry_run: bool = False):
        """
        按文件类型整理
        Args:
            dry_run: 为True时只记录日志，不实际移动文件
        """
        logger.info(f"{'[试运行]' if dry_run else ''}开始按类型整理:{self.source_dir}")
        moved_count = 0

        # 遍历所有文件
        for item in tqdm(list(self.source_dir.rglob('*')), desc="整理中"):
            # 只处理普通文件，并跳过隐藏文件
            if not (item.is_file() or not item.name.startswith('.')):
                continue

            # 跳过目标目录中的文件（防止循环移动）
            if self.target_dir in item.parents:
                logger.info(f"跳过目标目录中的文件：{item}")
                continue

            # 获取分类并构建目标路径
            category_n = self.get_file_category(item)
            target_folder = self.target_dir / category_n

            # ---------- 统一先算目标路径 ----------
            target_path = target_folder / item.name
            counter = 1

            while target_path.exists():  # 重名自动加序号
                stem, suffix = item.stem, item.suffix
                target_path = target_folder / f"{stem}_{counter}{suffix}"
                counter += 1

            # ---------- 日志：无论 dry_run 都打印 ----------
            logger.info(f"{'[试运行] ' if dry_run else ''}将移动: {item} -> {target_path}")

            if dry_run:  # 只打印不干活
                continue

            # ---------- 真正移动 ----------
            target_folder.mkdir(parents=True, exist_ok=True)
            try:
                self._move_atom(item, target_path)
                moved_count += 1
            except Exception as e:
                    logger.error(f"移动失败 {item}: {e}")

        logger.info(f"整理完成！共移动 {moved_count} 个文件")
        return moved_count

    def organize_by_date(self, date_format: str = "%Y-%m-%d", dry_run: bool =False):
        """
        按文件修改日期整理
        Args:
            date_format: 日期格式字符串
                %Y: 年(4位)
                %m: 月(01-12)
                %d: 日(01-31)
            dry_run: 试运行模式
        """
        logger.info(f"{'[试运行]' if dry_run else ''}开始按日期整理:{self.source_dir}")
        moved_count = 0

        for item in tqdm(list(self.source_dir.rglob('*')), desc="整理中"):
            if not (item.is_file() and not item.name.startswith('.')):
                continue

            if self.target_dir in item.parents:
                continue

            # 获取文件修改时间
            m_time = item.stat().st_mtime # 返回时间戳（秒）

            # 将时间戳转换为datatime对象
            date_obj = datetime.datetime.fromtimestamp(m_time)

            # 格式化为字符串（如"2024-01"）
            date_str = date_obj.strftime(date_format)

            # 创建日期文件夹
            target_folder = self.target_dir / date_str

            # ---------- 统一先算目标路径 ----------
            target_path = target_folder / item.name
            counter = 1

            while target_path.exists():
                stem, suffix = item.stem, item.suffix
                target_path = target_folder / f"{stem}_{counter}{suffix}"
                counter += 1

            # ---------- 日志：无论 dry_run 都打印 ----------
            logger.info(f"{'[试运行] ' if dry_run else ''}将移动: {item} -> {target_path}")

            if dry_run: continue

            target_folder.mkdir(parents=True, exist_ok=True)

            try:
                self._move_atom(item, target_path)
                moved_count += 1
            except Exception as e:
                logger.error(f"移动失败 {item}: {e}")

        logger.info(f"按日期整理完成！共移动 {moved_count} 个文件")
        return moved_count

    def organize_by_size(self, size_limits: List[int] = None, dry_run: bool = False):
        """
        按文件大小整理
        Args:
            size_limits: 大小阈值列表[小文件上限, 中文件上限]，单位MB
                        默认[10, 100] -> 小文件(<10MB), 中文件(10-100MB), 大文件(>100MB)
            dry_run: 试运行模式
        """
        # 使用or提供默认值（注意：不要用mutable object作为默认参数）
        if size_limits is None:
            size_limits = [10, 100]

        # 验证参数有效性
        if len(size_limits) != 2 or size_limits[0] >= size_limits[1]:
            raise ValueError("size_limits必须是包含两个递增值的列表")

        logger.info(f"{'[试运行] ' if dry_run else ''}开始按大小整理: {self.source_dir}")

        # 定义大小分类
        size_categories = ['小文件', '中文件', '大文件']
        moved_count = 0

        for item in tqdm(list(self.source_dir.rglob('*')), desc="整理中"):
            if not (item.is_file() or not item.name.startswith('.')):
                continue

            if self.target_dir in item.parents:
                continue

            # 获取文件大小
            size_mb = item.stat().st_size / (1024*1024)

            # 根据阈值确定分类
            if size_mb <= size_limits[0]:
                category = size_categories[0]
            elif size_mb <= size_limits[1]:
                category = size_categories[1]
            else:
                category = size_categories[2]

            # 创建目标文件夹
            target_folder = self.target_dir / category

            # ---------- 统一先算目标路径 ----------
            target_path = target_folder / item.name
            counter = 1

            while target_path.exists():
                stem, suffix = item.stem, item.suffix
                target_path = target_folder / f"{stem}_{counter}{suffix}"
                counter += 1

            # ---------- 日志：无论 dry_run 都打印 ----------
            logger.info(f"{'[试运行] ' if dry_run else ''}将移动: {item} -> {target_path}")

            if dry_run: continue

            target_folder.mkdir(parents = True, exist_ok = True)
            try:
                self._move_atom(item, target_path)
                moved_count += 1
            except Exception as e:
                logger.error(f"移动失败 {item}: {e}")
        logger.info(f"按文件大小整理完成！共移动 {moved_count} 个文件")
        return moved_count

    def scan_files(self) -> list[Path]:
        """
        扫描源目录所有文件
        Returns:
            文件路径对象列表
        """
        file_list = []

        # 使用rglob递归遍历所有文件和目录
        for item in self.source_dir.rglob('*'):
        # 检查是否是文件且不以下划线开头
            if item.is_file() and not item.name.startswith('.'):
                file_list.append(item)

        logger.info(f"扫描完成，共找到{len(file_list)}个文件")
        return file_list

    def get_file_hash(self, file_path: Path, algorithm="sha256") -> str:
        """
        计算文件哈希
        :param file_path: 文件路径
        :param algorithm: 算法名  sha256 / md5 / blake2b ...
        :return: 十六进制哈希串；失败返回 None（与空串区分）
        """
        try:
            h = hashlib.new(algorithm)
            with file_path.open("rb") as f:
                for chunk in iter(lambda: f.read(1 << 16), b""):  # 64 KB 块
                    h.update(chunk)
            return h.hexdigest()
        except Exception as e:
            logger.error(f"计算哈希失败 {file_path}: {e}")
            return None

    def find_duplicates(self) -> dict[str, list[Path]]:
        """
        查找所有重复文件
        Returns:
            字典: {哈希值: [文件路径列表]}
        """
        hash_dict = {}
        duplicates = {}

        #扫描所有文件
        for file_path in self.source_dir.rglob('*'):
            if file_path.is_file() and not file_path.name.startswith('.'):
                # 计算哈希
                file_hash = self.get_file_hash(file_path)

                if not file_hash:
                    continue

                # 如果哈希已存在，说明是重复文件
                if file_hash in hash_dict:
                    if file_hash not in duplicates:
                        duplicates[file_hash] = [hash_dict[file_hash]]
                        duplicates[file_hash].append(file_path)
                else:
                    # 记录首次出现文件
                    hash_dict[file_hash] = file_path

        logger.info(f"扫描完成，发现{len(duplicates)}组重复文件")
        return duplicates

    def clean_empty_folders(self, dry_run: bool = False) -> List[Path]:
        """自底向上删空目录（含仅藏隐藏文件）"""
        emptied: List[Path] = []
        for root, dirs, _ in os.walk(self.source_dir, topdown=False):
            for dn in dirs:
                dp = Path(root) / dn
                if not dp.is_dir():
                    continue
                # 仅含隐藏文件也视为空
                if all(p.name.startswith('.') for p in dp.iterdir()):
                    if not dry_run:
                        try:
                            for p in dp.iterdir():  # 先删隐藏文件
                                p.unlink()
                            dp.rmdir()
                            emptied.append(dp)
                            logger.info(f"删除空目录：{dp}")
                        except Exception as e:
                            logger.debug(f"跳过 {dp}：{e}")
                    else:
                        logger.info(f"[试运行] 将删空目录：{dp}")
                        emptied.append(dp)
        return emptied

    def dedup(self, mode: str = "link", dry_run: bool = False) -> int:
        """
        mode: "link" 创建硬链接； "delete" 删除后者； "keep-longest" 保留路径最长的文件
        返回实际处理组数
        """
        groups = self.find_duplicates()
        done = 0
        for hash_v, files in groups.items():
            keeper, *rest = sorted(files, key=lambda p: (-len(p.parts), p))
            for victim in rest:
                if not dry_run:
                    try:
                        if mode == "link":
                            victim.unlink()
                            victim.hardlink_to(keeper)  # py3.10+
                        elif mode == "delete":
                            victim.unlink()
                        logger.info(f"[{mode}] {victim} -> {keeper}")
                    except Exception as e:
                        logger.error(f"处理失败 {victim}: {e}")
                else:
                    logger.info(f"[试运行] {mode} {victim} -> {keeper}")
            done += 1
        return done


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "自动整理文件脚本")
    parser.add_argument('src', help = "要整理的目录")
    parser.add_argument("-dst", "--dst", help = "整理后目录（默认同 src）")
    parser.add_argument("-dr", "--dry-run", action="store_true",
                        help="只预览，不真正移动")
    args = parser.parse_args()
    org = FileOrganizer(args.src, args.dst)
    org.organize_by_category(dry_run = args.dry_run)