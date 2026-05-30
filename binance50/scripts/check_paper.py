import sys
import yaml

with open("binance50/config/default.yaml") as f:
    config = yaml.safe_load(f)
    if "paper_execution" not in config:
        print("Missing paper_execution in default.yaml")
        sys.exit(1)
print("paper_execution block added correctly")
