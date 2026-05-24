import os

def ensure_dir(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)

def write_file(path, content):
    ensure_dir(path)
    with open(path, 'w') as f:
        f.write(content)
