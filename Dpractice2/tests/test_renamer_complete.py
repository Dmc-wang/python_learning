import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest, tempfile, shutil
from renamer import Renamer

@pytest.fixture
def temp_dir():
    tmp = Path(tempfile.mkdtemp())
    yield tmp
    shutil.rmtree(tmp)

def test_sequential(temp_dir):
    renamer = Renamer()
    (temp_dir / "a.jpg").write_text("x")
    files = [temp_dir / "a.jpg"]
    plan = renamer.rename_sequential(files, start=5, digits=3)
    assert plan[0][1].name == "005.jpg"

def test_prefix(temp_dir):
    renamer = Renamer()
    (temp_dir / "old.jpg").write_text("x")
    plan = renamer.rename_with_prefix([temp_dir / "old.jpg"], "new_")
    assert plan[0][1].name == "new_old.jpg"

def test_suffix_before_ext(temp_dir):
    renamer = Renamer()
    (temp_dir / "pic.jpg").write_text("x")
    plan = renamer.rename_with_suffix([temp_dir / "pic.jpg"], "_v2")
    assert plan[0][1].name == "pic_v2.jpg"

def test_replace_case_sensitive(temp_dir):
    renamer = Renamer()
    (temp_dir / "Test.jpg").write_text("x")
    plan = renamer.rename_replace([temp_dir / "Test.jpg"], "test", "photo")
    assert len(plan) == 0  # 区分大小写，没匹配到

def test_replace_case_insensitive(temp_dir):
    renamer = Renamer(verbose = True)
    (temp_dir / "Test.jpg").write_text("x")
    plan = renamer.rename_replace([temp_dir / "Test.jpg"], "test", "photo", case_sensitive=False)
    assert plan[0][1].name == "photo.jpg"

def test_regex(temp_dir):
    renamer = Renamer()
    (temp_dir / "img_001.jpg").write_text("x")
    plan = renamer.rename_regex([temp_dir / "img_001.jpg"], r"img_(\d+)", r"photo_\1")
    assert plan[0][1].name == "photo_001.jpg"

def test_execute_dry_run(temp_dir):
    renamer = Renamer()
    (temp_dir / "a.jpg").write_text("x")
    plan = renamer.rename_sequential([temp_dir / "a.jpg"], start=1)
    result = renamer.execute_rename(plan, dry_run=True)
    assert (temp_dir / "a.jpg").exists()  # 原文件还在
    assert result['renamed'] == 1  # 计划数

def test_execute_real(temp_dir):
    renamer = Renamer()
    (temp_dir / "a.jpg").write_text("x")
    plan = renamer.rename_sequential([temp_dir / "a.jpg"], start=1)
    result = renamer.execute_rename(plan, dry_run=False)
    assert not (temp_dir / "a.jpg").exists()  # 旧文件消失
    assert (temp_dir / "001.jpg").exists()    # 新文件出现
    assert result['renamed'] == 1