#将指定文件夹内的所有文件按统一规则批量重命名（如 img_1.jpg、img_2.jpg），
#并支持通过参数灵活控制行为。
import os
from pathlib import Path

"""
        批量重命名文件夹中的文件。
        
        参数:
            Folder_path：目录路径
            前缀：新的文件名前缀
            Start：起始编号索引
            Ext：只重命名带有此扩展名的文件，例如：“jpg”
            dry_run：如果为True，只打印操作
"""
def batch_rename(
        folfer: str,
        prefix: str = "file_",
        start: int = 1,
        ext: str | None = None,
        dry_run: bool = False
):
    # 把字符串路径转成 Path 对象
    folder = Path(folfer)
    # 检查文件夹是否存在
    if not folder.exists():
        # 不存在直接报错并终止程序
        raise FileNotFoundError("Folder does not exist")

    #初始化计数器 index，从 start 指定的数字开始
    index = start

    # 遍历文件夹内所有条目（文件和子文件夹）
    for file in folder.iterdir():

        # 只处理文件，跳过子文件夹
        if file.is_file():

            #扩展名过滤：如果指定了 ext 且当前文件后缀不匹配，跳过此文件
            if ext and file.suffix != ext:
                continue

            #构造新文件名，格式：前缀 + 编号 + 原扩展名
            #例：file_1.jpg, file_2.jpg
            new_name = f"{prefix}{index}.{file.suffix}"

            #构造新文件的完整路径（folder / new_name 是 Path 的优雅写法）
            new_path = folder / new_name

            #打印预览：显示每个文件的重命名操作（旧名 → 新名）
            print(f"Rename {file.name} -> {new_path}")

            #执行重命名：只有当 dry_run=False 时才真正修改文件名
            #file.rename(): Path 对象的重命名方法
            if not dry_run:
                file.rename(new_path)

            #编号递增：每处理一个文件，序号 +1
            index += 1

#示例：
if __name__ == "__main__":
    batch_rename("./photos",prefix = "img_",ext = ".png",dry_run = True)
    batch_rename("./photos", prefix = "img_",start = 1, ext = ".png", dry_run = False)





