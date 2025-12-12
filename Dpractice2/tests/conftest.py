# Dpractice2/tests/conftest.py
import pytest, tempfile, shutil
from pathlib import Path

@pytest.fixture
def temp_image_dir():
    """自动创建包含测试图片的临时目录，测试后自动删除"""
    tmp = Path(tempfile.mkdtemp())
    (tmp / "photo1.jpg").write_text("fake")
    (tmp / "image2.png").write_text("fake")
    (tmp / "doc.txt").write_text("not image")
    yield tmp  # 把 tmp 传给测试函数
    shutil.rmtree(tmp)  # 测试结束后删除