# ✔ 小练习 2：模拟“自动生成项目目录脚本”
# 功能类似于脚手架工具（scaffold）。

import os
import sys

def create_project(name):
    structure = ["src", "docs", "assets", "tests"]
    for folder in structure:
        path = os.path.join(name, folder)
        os.makedirs(path, exist_ok=True)
        print(f"创建: {path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python project_scaffold.py <project_name>")
        sys.exit(1)

    project_name = sys.argv[1]
    create_project(project_name)
