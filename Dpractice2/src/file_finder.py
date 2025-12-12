"""
文件查找模块 - 用于查找和筛选图片文件
"""

import os
from pathlib import Path
from typing import List

class FileFinder:
    """文件查找器类"""
    # 支持的图片扩展名
    DEFAULT_EXTENSIONS = {
        '.jpg', '.jpeg', '.png',
        '.gif', '.bmp', '.webp',
        '.tiff', '.tif', '.ico'
    }

    def __init__(self, extensions: str = None, verbose: bool = False):
        self.verbose = verbose

        if extensions:
            # 将逗号分隔的扩展名字符串转换为集合
            ext_list = extensions.lower().split(',')  #'png,jpg' -> ['png', 'jpg']
            self.extensions = {f'.{ext.strip()}' for ext in ext_list} #集合（无序，无重复）['png', 'jpg']->{'.png', '.jpg'}
        else:
            self.extensions = self.DEFAULT_EXTENSIONS

        if self.verbose:
            print(f"支持的扩展名: {self.extensions}")

    def find_image_files(self, directory: str,recursive: bool = False) -> List[Path]:
        """
        查找指定目录下的图片文件
        参数:
            directory: 要搜索的目录路径
            recursive: 是否递归搜索子目录

        返回:
            图片文件的Path对象列表
        """
        dir_path = Path(directory).expanduser().resolve() #Path对象

        # 如果目录不存在
        if not dir_path.exists():
            raise FileNotFoundError(f"目录不存在: {directory}")

        # 如果不是目录
        if not dir_path.is_dir():
            raise NotADirectoryError(f"不是目录: {directory}")

        # 选择文件扫描模式，递归搜索子目录或不递归
        search_method = dir_path.rglob if recursive else dir_path.glob

        # 一次遍历即可
        images = [p for p in search_method('*')
                  if p.is_file() and p.suffix.lower() in self.extensions]

        # for p in search_method('*'):
        #     if p.is_file() and p.suffix.lower() in self.extensions:
        #         images.append(p)

        if self.verbose:
            print(f"共找到 {len(images)} 张图片")

        return sorted(images)  # 直接排序，无需 set

    def filter_files(self, files: List[Path],min_size_mb: float = None,max_size_mb: float = None) -> List[Path]:
        """
        筛选文件列表

        参数:
            files: 要筛选的文件路径列表
            min_size_mb: 最小文件大小(MB)，None表示不限制
            max_size_mb: 最大文件大小(MB)，None表示不限制

        返回:
            筛选后的文件列表
        """
        filtered = []

        for p in files:
            size_mb = p.stat().st_size / (1024 * 1024)  # MB

            if min_size_mb is not None and size_mb < min_size_mb:
                if self.verbose:
                    print(f"跳过过小文件: {p.name} ({size_mb:.2f} MB)")
                continue

            if max_size_mb is not None and size_mb > max_size_mb:
                if self.verbose:
                    print(f"跳过大文件: {p.name} ({size_mb:.2f} MB)")
                continue

            if p.name.startswith('.'):
                if self.verbose:
                    print(f"跳过隐藏文件: {p}")
                continue

            filtered.append(p)

        return filtered

if __name__ == '__main__':
    pf = FileFinder(verbose = True)
    image = pf.find_image_files('~/Downloads')
    for p in image:
        print(f'{p.stat().st_size / (1024 * 1024):.02f}MB')
    l = pf.filter_files(image,1)
    print(l)

