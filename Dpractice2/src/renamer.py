"""
重命名器模块 - 核心重命名逻辑
"""

import re
import shutil
from pathlib import Path
from typing import List, Tuple, Dict
from datetime import datetime


class Renamer:
    """重命名器类"""

    def __init__(self, verbose: bool = False):
        """初始化重命名器"""
        self.verbose = verbose
        self.rename_log = []  # 记录重命名操作

    def rename_sequential(
            self,
            files: List[Path],
            start: int = 1,
            digits: int = 3,
            prefix: str = "",
            suffix: str = ""
    ) -> List[Tuple[Path, Path]]:
        """
        顺序重命名文件

        参数:
            files: 要重命名的文件列表
            start: 起始编号
            digits: 编号位数
            prefix: 前缀
            suffix: 后缀

        返回:
            重命名前后路径的元组列表
        """
        rename_plan = []

        for i, file_path in enumerate(files, start = start):
            # 获取文件扩展名
            extension = file_path.suffix

            # 生成序号
            number_str = str(i).zfill(digits)

            # 构建新文件名
            new_filename = f"{prefix}{number_str}{suffix}{extension}"
            new_path = file_path.parent / new_filename

            rename_plan.append((file_path, new_path))

            if self.verbose:
                print(f"  {file_path.name} -> {new_filename}")

        return rename_plan

    def rename_with_prefix(
            self,
            files: List[Path],
            prefix: str
    ) -> List[Tuple[Path, Path]]:
        """添加前缀重命名"""
        rename_plan = []

        for file_path in files:
            new_filename = f"{prefix}{file_path.name}"
            new_path = file_path.parent / new_filename

            rename_plan.append((file_path, new_path))

            if self.verbose:
                print(f"  {file_path.name} -> {new_filename}")

        return rename_plan

    def rename_with_suffix(
            self,
            files: List[Path],
            suffix: str,
            before_extension: bool = True
    ) -> List[Tuple[Path, Path]]:
        """添加后缀重命名"""
        rename_plan = []

        for file_path in files:
            if before_extension:
                # 在扩展名前添加后缀
                stem = file_path.stem  # 文件名（不含扩展名）
                extension = file_path.suffix
                new_filename = f"{stem}{suffix}{extension}"
            else:
                # 在整个文件名后添加后缀
                new_filename = f"{file_path.name}{suffix}"

            new_path = file_path.parent / new_filename
            rename_plan.append((file_path, new_path))

            if self.verbose:
                print(f"  {file_path.name} -> {new_filename}")

        return rename_plan

    def rename_replace(
            self,
            files: List[Path],
            old_str: str,
            new_str: str,
            case_sensitive: bool = True
    ) -> List[Tuple[Path, Path]]:
        """字符串替换重命名"""
        rename_plan = []

        for file_path in files:
            old_name = file_path.name

            if case_sensitive:
                new_name = old_name.replace(old_str, new_str)
            else:
                # 不区分大小写替换
                pattern = re.compile(re.escape(old_str), re.IGNORECASE)
                new_name = pattern.sub(new_str, old_name)

            if old_name != new_name:
                new_path = file_path.parent / new_name
                rename_plan.append((file_path, new_path))

                if self.verbose:
                    print(f"  {old_name} -> {new_name}")

        return rename_plan

    def rename_regex(
            self,
            files: List[Path],
            pattern: str,
            replacement: str
    ) -> List[Tuple[Path, Path]]:
        """正则表达式替换重命名"""
        rename_plan = []

        try:
            regex = re.compile(pattern)
        except re.error as e:
            raise ValueError(f"无效的正则表达式: {pattern}\n错误: {e}")

        for file_path in files:
            old_name = file_path.name
            new_name = regex.sub(replacement, old_name)

            if old_name != new_name:
                new_path = file_path.parent / new_name
                rename_plan.append((file_path, new_path))

                if self.verbose:
                    print(f"  {old_name} -> {new_name}")

        return rename_plan

    def execute_rename(
            self,
            rename_plan: List[Tuple[Path, Path]],
            dry_run: bool = False
    ) -> Dict[str, int]:
        """
        执行重命名操作

        参数:
            rename_plan: 重命名计划列表
            dry_run: 是否为预览模式

        返回:
            操作结果统计字典
        """
        results = {
            'total': len(rename_plan),
            'renamed': 0,
            'skipped': 0,
            'errors': 0
        }

        for old_path, new_path in rename_plan:
            try:
                # 检查目标文件是否已存在
                if new_path.exists():
                    print(f"警告: 目标文件已存在，跳过: {new_path.name}")
                    results['skipped'] += 1
                    continue

                if not dry_run:
                    # 实际执行重命名
                    old_path.rename(new_path)
                    results['renamed'] += 1

                    # 记录操作日志
                    self.rename_log.append({
                        'old_path': str(old_path),
                        'new_path': str(new_path),
                        'timestamp': datetime.now().isoformat()
                    })

                    if self.verbose:
                        print(f"✓ 已重命名: {old_path.name} -> {new_path.name}")
                else:
                    # 预览模式，只显示计划
                    results['renamed'] += 1
                    if self.verbose:
                        print(f"计划: {old_path.name} -> {new_path.name}")

            except Exception as e:
                print(f"错误: 重命名失败 {old_path} -> {new_path}: {e}")
                results['errors'] += 1

        return results

