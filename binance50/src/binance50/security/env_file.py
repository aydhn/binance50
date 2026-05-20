import os
import stat
from pathlib import Path
from typing import Any


def find_env_file(repo_root: Path) -> Path | None:
    env_path = repo_root / ".env"
    if env_path.exists():
        return env_path
    return None


def parse_env_file_safely(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}

    result = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("=", 1)
            if len(parts) == 2:
                result[parts[0].strip()] = parts[1].strip()
    return result


def write_env_template_if_missing(repo_root: Path) -> Path:
    env_path = repo_root / ".env"
    if not env_path.exists():
        example_path = repo_root / ".env.example"
        if example_path.exists():
            content = example_path.read_text(encoding="utf-8")
            env_path.write_text(content, encoding="utf-8")
        else:
            env_path.touch()
    return env_path


def validate_env_file_permissions(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"status": "missing", "warnings": []}

    warnings = []
    try:
        st = os.stat(path)
        # basic check: check if it is world-readable
        if st.st_mode & stat.S_IROTH:
            warnings.append(
                "File is world-readable. Consider restricting permissions (e.g. chmod 600)."
            )
    except Exception as e:
        warnings.append(f"Could not check permissions: {e}")

    status = "unsafe" if warnings else "safe"
    return {"status": status, "warnings": warnings}


def list_env_keys_without_values(path: Path) -> list[str]:
    data = parse_env_file_safely(path)
    return [k for k, v in data.items() if not v]


def list_present_secret_keys(path: Path) -> list[str]:
    data = parse_env_file_safely(path)
    # We define what keys are secret based on name matching
    secret_patterns = ["SECRET", "KEY", "TOKEN", "PASSWORD"]
    return [k for k, v in data.items() if v and any(p in k.upper() for p in secret_patterns)]
