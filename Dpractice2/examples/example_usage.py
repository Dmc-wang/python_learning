# examples/example_usage.py
"""
使用示例
"""

import os
import sys

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import main as rename_main

# 示例1: 基本顺序重命名
print("示例1: 顺序重命名")
print("python src/main.py ./photos --pattern sequential --start 1 --digits 3")

# 示例2: 添加前缀
print("\n示例2: 添加前缀")
print("python src/main.py ./vacation --pattern prefix --prefix 'summer2023_'")

# 示例3: 替换字符串
print("\n示例3: 替换文件名中的字符串")
print("python src/main.py ./images --pattern replace --old 'IMG_' --new 'Photo_'")

# 示例4: 使用正则表达式
print("\n示例4: 使用正则表达式删除数字")
print("python src/main.py ./pics --pattern regex --regex-pattern '\\\\d+' --regex-replace ''")

# 示例5: 预览模式
print("\n示例5: 预览模式（不实际执行）")
print("python src/main.py ./photos --pattern sequential --dry-run --verbose")