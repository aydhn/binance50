with open("binance50/src/binance50/ml/inference/feature_matrix.py", "r") as f:
    content = f.read()

content = content.replace("from typing import Any, Dict, List", "from typing import Any, Dict, List, Optional")

with open("binance50/src/binance50/ml/inference/feature_matrix.py", "w") as f:
    f.write(content)
