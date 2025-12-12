#!/usr/bin/env python3
"""
Renamer 单元测试
"""
import sys
from pathlib import Path
import tempfile, shutil, pytest

# 将 src 目录添加到 sys.path（临时但有效）
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from renamer import Renamer


@pytest.fixture
def temp_images():
    """创建临时图片目录，测试后自动清理"""
    tmp = Path(tempfile.mkdtemp())
    # 创建测试文件：1.jpg, 2.png, 3.gif
    (tmp / "photo1.jpg").write_text("fake")
    (tmp / "image2.png").write_text("fake")
    (tmp / "pic3.gif").write_text("fake")
    yield tmp
    shutil.rmtree(tmp)


def test_rename_sequential(temp_images):
    """测试顺序重命名"""
    renamer = Renamer(verbose=True)
    files = sorted(temp_images.glob("*"))  # 按名称排序
    plan = renamer.rename_sequential(files, start=100, digits=4, prefix="vacation_")

    # 验证计划生成正确
    assert len(plan) == 3
    assert plan[0][1].name == "vacation_0100.jpg"  # 原 1.jpg
    assert plan[1][1].name == "vacation_0101.png"  # 原 2.png
    assert plan[2][1].name == "vacation_0102.gif"  # 原 3.gif


def test_rename_with_prefix(temp_images):
    """测试前缀重命名"""
    renamer = Renamer()
    files = list(temp_images.glob("*"))
    plan = renamer.rename_with_prefix(files, prefix="pre_")

    names = [p[1].name for p in plan]
    assert "pre_photo1.jpg" in names
    assert "pre_image2.png" in names
    assert "pre_pic3.gif" in names


def test_rename_replace(temp_images):
    """测试字符串替换"""
    renamer = Renamer()
    files = list(temp_images.glob("*"))
    plan = renamer.rename_replace(files, old_str="photo", new_str="img")

    # 只有 photo1.jpg 被改名
    assert len(plan) == 1
    assert plan[0][1].name == "img1.jpg"


def test_rename_regex(temp_images):
    """测试正则表达式"""
    renamer = Renamer(verbose=True)
    files = list(temp_images.glob("*"))
    # 把数字开头的部分替换成 "new"
    plan = renamer.rename_regex(files, pattern=r"^\w+(\d)", replacement=r"new\1")

    names = [p[1].name for p in plan]
    assert "new1.jpg" in names
    assert "new2.png" in names
    assert "new3.gif" in names


def test_execute_rename_dry_run(temp_images):
    """测试 execute_rename 预览模式"""
    renamer = Renamer(verbose=True)
    files = list(temp_images.glob("*"))
    plan = renamer.rename_sequential(files, start=1)

    # 试运行
    result = renamer.execute_rename(plan, dry_run=True)

    # 文件还在原位
    assert (temp_images / "photo1.jpg").exists()
    assert result['renamed'] == 3  # 计划数
    assert result['errors'] == 0


def test_execute_rename_real(temp_images):
    """测试真实重命名"""
    renamer = Renamer(verbose=True)
    files = list(temp_images.glob("*"))
    plan = renamer.rename_sequential(files, start=1)

    # 真实执行
    result = renamer.execute_rename(plan, dry_run=False)

    # 旧文件消失，新文件出现
    assert not (temp_images / "photo1.jpg").exists()
    assert (temp_images / "001.jpg").exists()
    assert len(renamer.rename_log) == 3  # 日志已记录


def test_target_exists(temp_images):
    """测试目标文件已存在的情况"""
    renamer = Renamer()
    # 预先创建目标文件
    (temp_images / "001.jpg").write_text("existing")
    files = [temp_images / "photo1.jpg"]
    plan = renamer.rename_sequential(files, start=1)

    result = renamer.execute_rename(plan, dry_run=False)
    assert result['skipped'] == 1  # 跳过冲突


def test_invalid_regex():
    """测试无效正则表达式"""
    renamer = Renamer()
    files = [Path("dummy.jpg")]

    with pytest.raises(ValueError, match="无效的正则表达式"):
        renamer.rename_regex(files, pattern="[invalid", replacement="x")