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

def batch_rename_meo(
        folfer: str,
        prefix: str = "file_",
        start: int = 1,
        ext: str | None = None,
        dry_run: bool = False
):
    folder = Path(folfer)

    if not folder.exists():
        raise FileNotFoundError("Folder does not exist")

    index = start

    for file in folder.iterdir():
        if file.is_file():
            if ext and ext != file.suffix:
                continue

            new_name = f"{prefix}{index}{file.suffix}"
            new_path = folder / new_name

            print(f"rename{file.name} -> {new_path}")

            if not dry_run:
                file.rename(new_path)

            index += 1

if __name__ == "__main__":
    batch_rename_meo("./photos", prefix = "im_",start = 1, ext = ".png", dry_run = True)
    batch_rename_meo("./photos", prefix="im_", start=1, ext=".png", dry_run = False)
