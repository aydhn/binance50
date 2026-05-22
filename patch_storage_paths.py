with open('binance50/src/binance50/storage/paths.py', 'r') as f:
    content = f.read()

content = content.replace("safe_value = re.sub(r'[^a-zA-Z0-9_-]', '_', value)\n    if not safe_value or safe_value.startswith('.'):", "safe_value = re.sub(r'[^a-zA-Z0-9_-]', '_', value)\n    if value.startswith('.'):\n         raise StoragePathError(f\"Invalid path component: {value}\")\n    if not safe_value:")

with open('binance50/src/binance50/storage/paths.py', 'w') as f:
    f.write(content)
