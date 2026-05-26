import re

with open("binance50/src/binance50/config/models.py", "r") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    new_lines.append(line)
    if "ml_dataset: MLDatasetConfig = Field(default_factory=MLDatasetConfig)" in line:
        if not any("ml_training: MLTrainingConfig = Field(default_factory=MLTrainingConfig)" in l for l in lines):
            new_lines.append("    ml_training: MLTrainingConfig = Field(default_factory=MLTrainingConfig)\n")

with open("binance50/src/binance50/config/models.py", "w") as f:
    f.writelines(new_lines)
