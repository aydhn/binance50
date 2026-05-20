from pathlib import Path

content = Path("binance50/scripts/check_project.py").read_text()
content = content.replace(
    'env = os.environ.copy()\n        env["PYTHONPATH"] = str(repo_root / "src")\n        result = subprocess.run(',
    'env = os.environ.copy()\n        env["PYTHONPATH"] = str(Path(__file__).resolve().parent.parent / "src")\n        result = subprocess.run('
)
Path("binance50/scripts/check_project.py").write_text(content)
