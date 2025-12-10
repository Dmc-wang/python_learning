#!/usr/bin/env python3
"""
自动整理文件脚本 - 基础框架
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
        '文档': ['.pdf', '.doc', '.docx', 'txt'],
        '图片': ['.jpg', '.jpeg', '.png', '.gif']
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

if __name__ == "__main__":
    try:
        organizer = FileOrganizer("D:\Automation_Test_Engineer\python_learning/test")
        logger.info(f"初始化成功！源目录: {organizer.source_dir}")
        logger.info(f"目标目录: {organizer.target_dir}")
    except Exception as e:
        logger.info(f"初始化失败: {e}")

