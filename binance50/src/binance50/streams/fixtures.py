import json
from pathlib import Path


def get_stream_fixture_path(name: str) -> Path:
    from binance50.core.paths import get_root_dir
    return get_root_dir() / "src" / "binance50" / "data" / "fixtures" / "streams" / name

def list_stream_fixtures() -> list[str]:
    from binance50.core.paths import get_root_dir
    d = get_root_dir() / "src" / "binance50" / "data" / "fixtures" / "streams"
    if not d.exists():
        return []
    return [f.name for f in d.glob("*.json")]

def load_stream_fixture(name: str) -> dict:
    p = get_stream_fixture_path(name)
    if not p.exists():
        raise FileNotFoundError(f"Stream fixture {name} not found at {p}")
    with open(p, encoding="utf-8") as f:
        return json.load(f)

def load_stream_fixture_sequence(names: list[str]) -> list[dict]:
    res = []
    for n in names:
        data = load_stream_fixture(n)
        if isinstance(data, list):
            res.extend(data)
        else:
            res.append(data)
    return res
