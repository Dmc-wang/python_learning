# 小练习
# 小练习 1：用 os.walk 遍历目录
# 目标：打印某个目录下所有文件与子文件夹。

import os

def walk_dir(path):
    for root, dirs, files in os.walk(path):
        print(f"当前目录: {root}")

        for d in dirs:
            print(f"  [目录] {d}")

        for f in files:
            print(f"  [文件] {f}")

if __name__ == '__main__':
    walk_dir("project_my")