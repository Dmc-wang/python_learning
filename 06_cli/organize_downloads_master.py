#!/usr/bin/env python3
"""
organize_downloads.py

最小可用 CLI：将下载文件夹内常见文件按类型自动分类到子文件夹。

功能：
- 支持递归或非递归扫描
- 支持 dry-run（只打印，不执行）
- 安全移动（避免覆盖，遇到冲突则自动重命名）
- 日志记录与异常处理
- 可配置分类扩展名（默认内置常用类型）
"""

from pathlib import Path
import shutil
import argparse
import logging
import sys
import time
from typing import Dict, List, Iterable, Tuple

# ----------------------------
# 默认分类映射（可按需扩展）
# ----------------------------
DEFAULT_CATEGORIES: Dict[str, List[str]] = {
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
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("organize")

# ----------------------------
# 工具函数
# ----------------------------
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Batch organize download folder by file type.")
    p.add_argument("--src", "-s", required=True, help="Source folder path to organize.")
    p.add_argument("--dest", "-d", required=False, help="Destination folder (defaults to src/_sorted).")
    p.add_argument("--recursive", "-r", action="store_true", help="Recursively walk subdirectories.")
    p.add_argument("--dry-run", action="store_true", help="Only print actions without moving files.")
    p.add_argument("--extensions", "-e", help="Comma-separated list of extensions to process (e.g. jpg,pdf,zip).")
    p.add_argument("--top", type=int, default=0, help="Only process top N files (0 means all).")
    return p.parse_args()

def build_extension_map(categories: Dict[str, List[str]]) -> Dict[str, str]:
    """Build a reverse map ext -> category for quick lookup."""
    ext_map: Dict[str, str] = {}
    for cat, exts in categories.items():
        for ext in exts:
            ext_map[ext.lower()] = cat
    return ext_map

def normalize_ext(ext: str) -> str:
    return ext.lower().lstrip(".")

def safe_move_file(src: Path, dest_dir: Path, dry_run: bool = False) -> Path:
    """
    Move a file to dest_dir in a safe manner:
    - create dest_dir if not exists
    - if filename exists, append counter suffix: name (1).ext
    - preserve mtime by copying metadata (shutil.move keeps metadata on same FS)
    Returns the final destination path (would be or was moved to).
    """
    dest_dir.mkdir(parents=True, exist_ok=True)
    target = dest_dir / src.name

    if target.exists():
        base = src.stem
        suffix = src.suffix
        counter = 1
        # find a free name
        while True:
            candidate = dest_dir / f"{base} ({counter}){suffix}"
            if not candidate.exists():
                target = candidate
                break
            counter += 1

    logger.debug(f"Moving: {src} -> {target}")
    if dry_run:
        logger.info(f"[DRY-RUN] Would move: {src} -> {target}")
    else:
        try:
            # Use shutil.move which handles cross-device moves
            shutil.move(str(src), str(target))
            # Ensure timestamps preserved when possible
            shutil.copystat(target, target, follow_symlinks=False)
            logger.info(f"Moved: {src} -> {target}")
        except PermissionError as e:
            logger.error(f"Permission denied moving {src} -> {target}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error moving {src} -> {target}: {e}")
            raise
    return target

def categorize_by_extension(ext: str, ext_map: Dict[str, str]) -> str:
    """Return category for a file extension; 'others' if no mapping."""
    ext_norm = normalize_ext(ext)
    return ext_map.get(ext_norm, "others")

def list_files(src: Path, recursive: bool) -> Iterable[Path]:
    """Yield files to process. Excludes directories."""
    if recursive:
        for p in src.rglob("*"):
            if p.is_file():
                yield p
    else:
        for p in src.iterdir():
            if p.is_file():
                yield p

# ----------------------------
# 主功能：组织函数
# ----------------------------
def organize_folder(
    src: Path,
    dest: Path,
    categories: Dict[str, List[str]],
    recursive: bool = False,
    dry_run: bool = False,
    only_exts: List[str] = None,
    top_n: int = 0
) -> Tuple[int, int]:
    """
    Organize files from src into dest according to categories.
    Returns (moved_count, total_processed).
    """
    if not src.exists() or not src.is_dir():
        logger.error(f"Source folder does not exist or is not a directory: {src}")
        return 0, 0

    ext_map = build_extension_map(categories)

    # if user specified only_exts, build a filter set
    filter_exts = None
    if only_exts:
        filter_exts = set(normalize_ext(e) for e in only_exts)

    moved = 0
    processed = 0

    try:
        files_iter = list_files(src, recursive)
        for file_path in files_iter:
            # don't move files from the destination folder into itself if dest is inside src
            try:
                if dest.resolve().is_relative_to(file_path.parent.resolve()):
                    # skip files that are already inside dest
                    logger.debug(f"Skipping file inside destination: {file_path}")
                    continue
            except Exception:
                # resolve().is_relative_to available py3.9+; safe fallback if not available
                pass

            processed += 1
            if top_n and processed > top_n:
                logger.info("Reached top_n limit, stopping.")
                break

            ext = normalize_ext(file_path.suffix)
            if not ext:
                category = "noext"
            else:
                category = categorize_by_extension(ext, ext_map)

            # filter by only_exts if provided
            if filter_exts and ext not in filter_exts:
                logger.debug(f"Skipping (ext not in filter): {file_path}")
                continue

            dest_dir = dest / category
            try:
                safe_move_file(file_path, dest_dir, dry_run=dry_run)
                moved += 1
            except Exception as e:
                logger.warning(f"Failed to move {file_path}: {e}")
                # continue processing other files

    except Exception as e:
        logger.error(f"Failed while scanning files: {e}")

    logger.info(f"Processed: {processed} files. Moved: {moved} files.")
    return moved, processed

# ----------------------------
# CLI 主入口
# ----------------------------
def main():
    args = parse_args()

    src = Path(args.src).expanduser().resolve()
    if args.dest:
        dest = Path(args.dest).expanduser().resolve()
    else:
        dest = src / "_sorted"

    # prepare categories; we can allow user to override by --extensions
    categories = DEFAULT_CATEGORIES.copy()

    only_exts = None
    if args.extensions:
        only_exts = [e.strip().lower().lstrip(".") for e in args.extensions.split(",") if e.strip()]

    logger.info(f"Source: {src}")
    logger.info(f"Destination: {dest}")
    logger.info(f"Recursive: {args.recursive}    Dry-run: {args.dry_run}")
    if only_exts:
        logger.info(f"Filtering to extensions: {only_exts}")

    start = time.time()
    try:
        moved, processed = organize_folder(
            src=src,
            dest=dest,
            categories=categories,
            recursive=args.recursive,
            dry_run=args.dry_run,
            only_exts=only_exts,
            top_n=args.top
        )
    except Exception as e:
        logger.error(f"Unhandled error: {e}")
        sys.exit(2)

    elapsed = time.time() - start
    logger.info(f"Done in {elapsed:.2f}s. Processed: {processed}, Moved: {moved}")

if __name__ == "__main__":
    main()
