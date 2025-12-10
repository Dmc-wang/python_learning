#!/usr/bin/env python3
"""
自动整理文件脚本 - 文件分类功能
"""

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


if __name__ == "__main__":
    try:
        organizer = FileOrganizer("~/Downloads")
        logger.info(f"初始化成功！源目录: {organizer.source_dir}")
        logger.info(f"目标目录: {organizer.target_dir}")
        files = organizer.scan_files()
        for file in files:
            category = organizer.get_file_category(file)
            logger.info(f"{file.name} -> {category}")
    except Exception as e:
        logger.info(f"初始化失败: {e}")