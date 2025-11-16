# 编写 “自动创建多级目录脚本”
# 输入：项目名 my_project
# 自动生成结构：
# my_project/
#     src/
#     data/
#     logs/
#     tests/

import os

project_name = input("请输入项目名: ")
subdirs = ["src", "data", "logs", "tests"]

os.makedirs(project_name, exist_ok = True)

for subdir in subdirs:
    path = os.path.join(project_name, subdir)
    os.makedirs(path, exist_ok = True)
    print(f"已创建目录：{path}")

print("多级目录已创建完毕。")