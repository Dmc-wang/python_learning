import os

# 功能：判断指定路径的文件或文件夹
# 是否存在，存在返回 True，不存在返回 False。
def file_exists(path):
    return os.path.exists(path)

#功能：返回文件的大小（单位：字节），文件不存在会报错。
def get_size(path):
    return os.stat(path).st_size