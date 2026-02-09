from __future__ import annotations
from pathlib import Path
import yaml

CONFIG_FILENAME = ".qa-agent.yml"

class ConfigError(Exception):
    pass

def load_config(repo_path: str | Path) -> dict:
    repo_path = Path(repo_path)
    cfg_path = repo_path / CONFIG_FILENAME
    if not cfg_path.exists():
        raise ConfigError(f"Missing {CONFIG_FILENAME} in target repo: {repo_path}")
    data = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
    return data
