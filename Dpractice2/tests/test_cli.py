import subprocess, tempfile, json
from pathlib import Path


def test_cli_type_mode():
    """测试命令行 按类型整理"""
    with tempfile.TemporaryDirectory() as tmp:
        # 造文件
        Path(tmp, "a.jpg").write_text("a")
        Path(tmp, "b.png").write_text("b")

        # 执行命令行
        cmd = f'python src/main.py {tmp} -m type -dr'
        rc = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        assert rc.returncode == 0
        assert "a.jpg -> 图片/" in rc.stdout