# Dpractice2/tests/test_renamer_basicv1.py
# 使用 tempfile 创建临时测试数据

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from renamer import Renamer

import tempfile, shutil
from pathlib import Path


def test_rename_sequential_plan():
    """测试顺序重命名计划生成"""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = Path(tmpdir)

        # 创建文件
        jpg_path = test_dir / "photo1.jpg"
        png_path = test_dir / "image2.png"
        jpg_path.write_text("fake")
        png_path.write_text("fake")

        # 手动指定顺序：先 jpg 再 png
        files = [jpg_path, png_path]  # ← 关键：不依赖 sorted()

        renamer = Renamer(verbose = True)
        plan = renamer.rename_sequential(files, start=100, digits=4, prefix="vacation_")

        # 现在断言与手动顺序一致，不会出错
        assert len(plan) == 2
        assert plan[0][1].name == "vacation_0100.jpg"
        assert plan[1][1].name == "vacation_0101.png"

# def test_rename_sequential_plan():
#     """测试顺序重命名计划生成"""
#     # 1. 创建临时目录
#     with tempfile.TemporaryDirectory() as tmpdir:
#         # 2. 在临时目录里创建测试文件
#         test_dir = Path(tmpdir)
#         (test_dir / "photo1.jpg").write_text("fake")
#         (test_dir / "image2.png").write_text("fake")
#
#         # 3. 实例化 Renamer
#         renamer = Renamer(verbose = True)
#         files = sorted(test_dir.glob("*"))
#
#         # 4. 生成重命名计划
#         plan = renamer.rename_sequential(files, start = 100, digits = 4, prefix = "vacation_")
#
#         # 5. 断言检查
#         assert len(plan) == 2, "应该有 2 个文件的重命名计划"
#         assert plan[0][1].name == "vacation_0100.jpg"
#         assert plan[1][1].name == "vacation_0101.png"
#
#         # 6. 验证原文件还在（dry_run 模式）
#         renamer.execute_rename(plan, dry_run = True)
#         assert (test_dir / "photo1.jpg").exists()