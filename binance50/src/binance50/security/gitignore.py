from pathlib import Path

from binance50.core.exceptions import GitIgnorePolicyError


def load_gitignore(repo_root: Path) -> list[str]:
    gitignore_path = repo_root / ".gitignore"
    if not gitignore_path.exists():
        return []
    with open(gitignore_path, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


def gitignore_contains_env_patterns(repo_root: Path) -> bool:
    patterns = load_gitignore(repo_root)
    has_env = ".env" in patterns
    has_env_wildcard = ".env.*" in patterns

    return has_env and has_env_wildcard


def assert_env_ignored(repo_root: Path) -> None:
    if not gitignore_contains_env_patterns(repo_root):
        raise GitIgnorePolicyError(
            "The .gitignore file does not adequately protect environment files. "
            "It must contain '.env' and '.env.*'."
        )


def suggest_gitignore_env_patterns() -> list[str]:
    return [".env", ".env.*", "!.env.example"]
