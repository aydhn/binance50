from pathlib import Path


def get_profile_runtime_dir(profile_name: str) -> Path:
    """Get the runtime directory for a specific profile."""
    p = Path("runtime") / profile_name
    p.mkdir(parents=True, exist_ok=True)
    return p


def get_profile_log_dir(profile_name: str) -> Path:
    """Get the log directory for a specific profile."""
    p = Path("logs") / profile_name
    p.mkdir(parents=True, exist_ok=True)
    return p


def get_profile_data_dir(profile_name: str) -> Path:
    """Get the data directory for a specific profile."""
    p = Path("data") / profile_name
    p.mkdir(parents=True, exist_ok=True)
    return p

def get_root_dir() -> Path:
    import os
    # Root is typically where src/ is located
    return Path(os.path.abspath(__file__)).parent.parent.parent.parent
