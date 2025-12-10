#!/usr/bin/env python3
"""
自动整理文件脚本 - 重复文件检测
"""

import hashlib
from pathlib import Path
import logging

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
        '文档': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt'],
        '图片': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg'],
        '视频': ['.mp4', '.avi', '.mov', '.wmv', '.flv'],
        '音频': ['.mp3', '.wav', '.flac', '.aac'],
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

        # 验证源目录存在性
        if not self.source_dir.exists():
            raise FileNotFoundError(f'源目录不存在：{self.source_dir}')

        if not self.target_dir.exists():
            self.target_dir.mkdir(parents=True, exist_ok=True)

        # 实例属性：分类规则和重复文件记录
        self.categories = self.DEFAULT_CATEGORIES.copy()
        self.duplicates= []

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

    # def get_file_hash(self, file_path: Path) -> str:
    #     """
    #     计算文件的MD5哈希值
    #     Args:
    #         file_path: 文件路径
    #     Returns:
    #         MD5哈希字符串（32位十六进制）
    #     """
    #     # 创建MD5哈希对象
    #     hash_md5 = hashlib.md5()
    #     try:
    #         # 以二进制只读模式打开文件
    #         with open(file_path, "rb") as f:
    #             # 分块读取文件（避免大文件占用过多内存）
    #             for chunk in iter(lambda: f.read(4096), b""):
    #                 hash_md5.update(chunk)
    #
    #         return hash_md5.hexdigest()
    #
    #     except Exception as e:
    #         logger.error(f"计算哈希失败 {file_path}: {e}")
    #         return ""

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


if __name__ == "__main__":
    organizer = FileOrganizer("~/Downloads")
    dup_dict = organizer.find_duplicates()

    for file_hash, file_list in dup_dict.items():
        print(f"\n发现重复文件组 (哈希: {file_hash}):")
        for f in file_list:
            print(f"  - {f} ({f.stat().st_size} bytes)")