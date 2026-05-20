from pathlib import Path
import re

content = Path("binance50/scripts/check_project.py").read_text()
# We need to run CLI with PYTHONPATH set so it can find binance50 package
content = content.replace(
    '        env = os.environ.copy()\n        env["PYTHONPATH"] = str(Path(__file__).resolve().parent.parent / "src")\n        result = subprocess.run(\n            cmd,',
    '        env = os.environ.copy()\n        env["PYTHONPATH"] = str(Path(__file__).resolve().parent.parent / "src")\n        result = subprocess.run(\n            cmd,\n            env=env,'
)
Path("binance50/scripts/check_project.py").write_text(content)
