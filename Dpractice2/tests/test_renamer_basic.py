# Dpractice2/tests/test_renamer_basic.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from renamer import Renamer

def test_renamer_exists():
    """测试 Renamer 类能否被导入"""
    assert Renamer is not None

def test_renamer_instance():
    """测试能否创建 Renamer 实例"""
    renamer = Renamer()
    assert isinstance(renamer, Renamer)