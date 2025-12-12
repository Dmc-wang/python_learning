# Dpractice2/tests/test_renamer_basicv2.py
# 理解 fixture（测试固件）

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from renamer import Renamer

def test_with_fixture(temp_image_dir):
    """使用fixture简化测试"""
    renamer = Renamer(verbose = True)
    files = sorted(temp_image_dir.glob("*.jpg"))

    plan = renamer.rename_sequential(files, start = 1)
    assert plan[0][1].name == "001.jpg"
