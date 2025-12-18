# test_fetcher_basic.py - 快速验证
import os
from pathlib import Path
import pandas as pd

# 方法1：使用pathlib（更现代）
base_dir = Path.home() / "python_learning" / "python_learning" / "Project1"
file_path = base_dir / "data" / "raw" / "movies_top250_20251216_095936.csv"
df = pd.read_csv(file_path)

print("✅ 数据加载成功！")
print(f"数据形状: {df.shape}")
print("\n📊 数据预览:")
print(df.head())

print("\n📈 基本信息:")
print(df.info())

print("\n⭐ 评分统计:")
print(df['rating'].describe())