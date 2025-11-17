import argparse
import logging
import shutil
import sys
import time
from typing import Iterable, Dict, List, Tuple
from pathlib import Path

# ----------------------------
# 默认分类映射（可按需扩展）
# ----------------------------
DEFAULT_CATEGORIES: Dict[str, list[str]] = {
    "pdf": ["pdf"],
    "images": ["jpg", "jpeg", "png", "gif", "bmp", "webp", "tiff"],
    "archives": ["zip", "tar", "gz", "tar.gz", "rar", "7z"],
    "documents": ["doc", "docx", "xls", "xlsx", "ppt", "pptx", "txt", "md"],
    "videos": ["mp4", "avi", "mkv", "mov", "wmv"],
    "audio": ["mp3", "wav", "flac", "aac"],
    "code": ["py", "js", "java", "c", "cpp", "go", "rs", "sh"],
    "installers": ["exe", "msi", "deb", "rpm"],
    # 未匹配的放到 "others"
}

# ----------------------------
# 日志初始化
# ----------------------------
logging.basicConfig(
    level = logging.INFO,
    format = "%(asctime)s - %(levelname)s - %(message)s",
    datefmt = "%Y/%m/%d %H:%M:%S"
)
logger = logging.getLogger("organize")

# 命令行参数解析函数
def parse_args() -> argparse.Namespace:
    """
        功能：定义参数解析函数，返回类型为 argparse.Namespace
        作用：封装所有命令行参数的解析逻辑
    """
    # 参数解析器初始化
    p = argparse.ArgumentParser(description = "按文件类型批量组织下载文件夹。")
    # 源文件路径
    p.add_argument("--src", "-s", required = True,
                   help = "要组织的源文件夹路径。") #作用：指定要整理的文件所在的源文件夹路径
    # 目标文件夹路径（可选）
    p.add_argument("--dst", "-d", required = False,
                   help = "目标文件夹（默认为src/_sorted）。") #作用：指定整理后文件的存放位置
    # 递归处理
    p.add_argument("--recursive", "-r", action = "store_true",
                   help = "递归遍历子目录。") #作用：是否递归处理子文件夹中的文件

    # 试运行模式
    p.add_argument("--dry-run", action = "store_true",
                   help = "只打印操作而不移动文件。") #作用：只显示将要执行的操作，但不实际移动文件，用于测试和预览

    # 文件名扩展过滤
    p.add_argument("--extensions", "-e",
                   help = "以逗号分隔的要处理的扩展列表（例如jpg，pdf,zip）。") #作用：只处理指定扩展名的文件

    # 处理文件数量限制
    p.add_argument("--top", default = 0,
                   help = "只处理前N个文件（0表示全部）。") #作用：只处理前 N 个文件，0 表示处理全部

    return p.parse_args() #解析命令行参数并返回
    #返回类型：argparse.Namespace 对象，可以通过属性访问各个参数值

# 文件扫描(递归/非递归)
def list_file(src: Path, recursive: bool) -> Iterable[Path]: #功能：生成文件路径的生成器函数
    # 递归模式
    if recursive:
        for p in src.rglob("*"):
            if p.is_file():
                yield p
    else:
        for p in src.glob("*"):
            if p.is_file():
                yield p

# 构建文件扩展名到分类映射的函数
def build_extension_map(categories: Dict[str, list[str]]) -> Dict[str, str]: #功能：构建扩展名到分类名称的反向映射字典
    # 初始化空字典
    ext_map: Dict[str, str] = {} # 创建一个空字典来存储扩展名到分类的映射
    # 双重循环构建映射
    for cat, exts in categories.items(): # 遍历每个分类
        """
        cat - 分类名称（如："images", "documents"）
        exts - 该分类对应的扩展名列表（如：["jpg", "png", "gif"]）
        """
        for ext in exts: # 遍历每个扩展名
            ext_map[ext.lower()] = cat
    return ext_map

# 规范化文件扩展名字符串，确保扩展名格式统一。
def normalize_ext(ext: str) -> str: #功能：规范化文件扩展名
    return ext.lower().lstrip(".") #将扩展名统一转换为小写

# 根据文件扩展名确定其所属的分类
def categorize_by_extension(ext: str, ext_map: Dict[str, str]) -> str: # 功能：根据扩展名获取文件分类
    ext_norm = normalize_ext(ext)
    return ext_map.get(ext_norm, "others")

# 安全移动文件的功能，包含目录创建、文件名冲突处理和元数据保留等特性。
def safe_move_file(src: Path, dest_dir: Path, dry_run: bool = False) -> Path: #功能：安全地将文件移动到目标目录
    dest_dir.mkdir(parents = True, exist_ok = True) # 创建目标目录
    target = dest_dir / src.name # 确定初始目标路径

    #处理文件名冲突
    if target.exists():
        base = src.stem
        suffix = src.suffix
        counter = 1
        #循环查找可用的文件名
        while True:
            candidate = dest_dir / f"{base} ({counter}){suffix}"
            if not candidate.exists():
                target = candidate
                break
            counter += 1

    # 执行移动操作
    logger.debug(f"Moving: {src} -> {target}")
    if dry_run:
        logger.info(f"[DRY-RUN] Would move {src} -> {target}")
    else:
        try:
            # 使用shutil.move 处理跨设备移动
            shutil.move(str(src), str(target))
            # 确保时间戳保留
            shutil.copystat(target, target, follow_symlinks = False)
            logger.info(f"Moved: {src} -> {target}")
        except PermissionError as e:
            logger.error(f"Permission denied moving {src} -> {target}: {e}")

            raise
        except Exception as e:
            logger.error(f"Error moving {src} -> {target}: {e}")
            raise

    return target

# ----------------------------
# 主功能：组织函数
# ----------------------------
# 文件整理工具的核心函数，负责协调整个文件整理流程。
def organize_folder(
        src: Path,
        dest: Path,
        categories: Dict[str, list[str]],
        recursive: bool = False,
        dry_run: bool = False,
        only_exts: List[str] = None,
        top_n: int = 0
) -> Tuple[int, int]: #功能：根据分类规则整理源目录中的文件到目标目录
    # 返回：(moved_count, total_processed) - 移动的文件数和总处理文件数

    # 输入验证
    if not src.exists() or not src.is_dir():
        logger.error(f"源文件夹不存在或不是目录：{src}")
        return 0, 0

    # 构建扩展名映射
    ext_map = build_extension_map(categories) # 将分类字典转换为扩展名→分类的快速查找表

    # 扩展名过滤设置
    filter_exts = None
    if only_exts:
        filter_exts = set(normalize_ext(e) for e in only_exts) #如果指定了 only_exts，创建扩展名过滤集合
                                                                # 使用集合提高查找效率
    moved = 0
    processed = 0

    try:
        #文件遍历和处理
        files_iter = list_file(src, recursive)
        for file_path in files_iter:
            # 防止循环移动：跳过目标目录中的文件
            try:
                if dest.resolve().is_relative_to(file_path.parent.resolve()):
                    logger.debug(f"跳过目标内的文件：{file_path}")
                    continue
            except Exception:
                pass

            # 处理限制检查
            #统计处理文件数,达到top_n限制时提前终止
            processed += 1
            if top_n and processed > top_n:
                logger.info("Reached top_n limit, stopping.")
                break

            #文件分类
            ext = normalize_ext(file_path.suffix)
            if not ext:
                category = "noext"
            else:
                category = categorize_by_extension(ext, ext_map)

            #扩展名过滤
            if filter_exts and ext not in filter_exts:
                logger.info(f"Skipping (ext not in filter):{file_path}")
                continue

            #文件移动
            dest_dir = dest / category
            try:
                safe_move_file(file_path, dest_dir, dry_run = dry_run)
                moved += 1
            except Exception as e:
                logger.error(f"Failed to move {file_path}: {e}")

    except Exception as e:
        logger.error(f"Failed while scanning files: {e}")

    logger.info(f"Processed: {processed} files. Moved: {moved} files.")
    return moved, processed

def main():
    # 参数解析和路径处理
    args = parse_args()

    src = Path(args.src).expanduser().resolve()
    if args.dst:
        dest = Path(args.dest).expanduser().resolve()
    else:
        dest = src / "_sorted" #如果没有指定目标目录，默认使用源目录下的 _sorted 子目录

    # 分类配置和扩展名过滤
    # 准备类别；我们可以允许用户通过——extensions来重写
    categories = DEFAULT_CATEGORIES.copy()

    only_exts = None
    if args.extensions:
        only_exts = [e.strip().lower().lstrip(".") for e in args.extensions.split(",") if e.strip()]
        # 如果用户提供了 - -extensions参数，解析逗号分隔的扩展名列表
        # 对每个扩展名进行清理：去除空格、转小写、移除前导点号

    # 运行信息日志
    logger.info(f"Source: {src}")
    logger.info(f"Destination: {dest}")
    logger.info(f"Recursive: {args.recursive}    Dry-run: {args.dry_run}")
    if only_exts:
        logger.info(f"Filtering to extensions: {only_exts}") #记录关键运行参数，便于用户确认和调试

    #执行文件整理
    start = time.time()
    try:
        moved, processed = organize_folder(
            src = src,
            dest = dest,
            categories = categories,
            recursive = args.recursive,
            dry_run = args.dry_run,
            only_exts = only_exts,
            top_n = args.top
        )
    except Exception as e:
        logger.error(f"Unhandled error: {e}")
        sys.exit(2)

    elapsed = time.time() - start
    logger.info(f"Done in {elapsed:.2f}s. Processed: {processed}, Moved: {moved}")

if __name__ == "__main__":  # main()
    p = list_file(Path("C:/Users/Administrator/Downloads"),recursive = True)
    for file_path in p:
        print(file_path)