from pathlib import Path
import re

content = Path("binance50/scripts/check_project.py").read_text()
# We need to run CLI with PYTHONPATH set so it can find binance50 package
content = content.replace(
    '        result = subprocess.run(',
    '        env = os.environ.copy()\n        env["PYTHONPATH"] = str(repo_root / "src")\n        result = subprocess.run('
)
content = content.replace('import sys', 'import sys\nimport os')
Path("binance50/scripts/check_project.py").write_text(content)
