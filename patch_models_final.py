with open("binance50/src/binance50/config/models.py", "r") as f:
    content = f.read()

import re
content = re.sub(
    r'ml_dataset:\s*MLDatasetConfig\s*=\s*Field\(default_factory=MLDatasetConfig\)',
    'ml_dataset: MLDatasetConfig = Field(default_factory=MLDatasetConfig)\n    ml_training: MLTrainingConfig = Field(default_factory=MLTrainingConfig)',
    content
)

with open("binance50/src/binance50/config/models.py", "w") as f:
    f.write(content)
