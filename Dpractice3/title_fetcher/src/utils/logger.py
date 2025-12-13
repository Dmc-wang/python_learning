# utils/logger.py
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler


def setup_logger(name: str = "title_fetcher", log_file: str = "logs/crawl.log"):
    """
    生产级日志配置（全自动编码处理）
    """
    # 创建日志目录
    Path(log_file).parent.mkdir(exist_ok=True)

    # 格式化器
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # ==================== 关键修复 ====================
    # 控制台：自动检测并适应Windows编码
    if sys.platform == "win32":
        # Windows：使用GBK兼容的编码，错误时忽略
        console_handler = logging.StreamHandler(
            open(sys.stdout.fileno(), mode='w', encoding='gbk', errors='ignore', buffering=1)
        )
    else:
        # Linux/macOS：UTF-8
        console_handler = logging.StreamHandler(sys.stdout)

    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # 文件：强制UTF-8，支持所有Unicode字符
    file_handler = logging.FileHandler(log_file, encoding='utf-8', errors='backslashreplace')
    # errors='backslashreplace'：无法编码时用\uXXXX表示
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    # =================================================

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


# 全局实例
logger = setup_logger()

# 测试
if __name__ == "__main__":
    logger.info("✅ 程序启动")
    logger.debug("🐛 调试信息")
    logger.warning("⚠️ 警告")
    logger.error("❌ 错误")