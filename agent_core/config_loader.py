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
    if not isinstance(data, dict):
        raise ConfigError(f"{CONFIG_FILENAME} must be a YAML mapping/object")
    _validate_required(data)
    return data


def _require_non_empty_str(cfg: dict, *path: str) -> str:
    cur = cfg
    for key in path[:-1]:
        val = cur.get(key)
        if not isinstance(val, dict):
            dotted = ".".join(path[:-1])
            raise ConfigError(f"Missing required object: {dotted}")
        cur = val
    leaf = path[-1]
    val = cur.get(leaf)
    dotted = ".".join(path)
    if not isinstance(val, str) or not val.strip():
        raise ConfigError(f"Missing required non-empty string: {dotted}")
    return val


def _validate_required(cfg: dict) -> None:
    _require_non_empty_str(cfg, "project", "type")
    _require_non_empty_str(cfg, "run", "command")
    _require_non_empty_str(cfg, "run", "wait_for")
    _require_non_empty_str(cfg, "test", "target_folder")

    env = cfg.get("env", {})
    if env is not None and not isinstance(env, dict):
        raise ConfigError("env must be an object/map if provided")

    base_url_env = cfg.get("test", {}).get("base_url_env")
    if base_url_env is not None and (not isinstance(base_url_env, str) or not base_url_env.strip()):
        raise ConfigError("test.base_url_env must be a non-empty string if provided")

    endpoints = cfg.get("test", {}).get("endpoints")
    if endpoints is not None:
        if not isinstance(endpoints, list):
            raise ConfigError("test.endpoints must be a list of URL paths if provided")
        for i, endpoint in enumerate(endpoints):
            if not isinstance(endpoint, str) or not endpoint.strip():
                raise ConfigError(f"test.endpoints[{i}] must be a non-empty string")

    default_suite = cfg.get("test", {}).get("default_suite")
    if default_suite is not None:
        valid_suites = {"smoke", "regression", "core", "all"}
        if not isinstance(default_suite, str) or default_suite.strip().lower() not in valid_suites:
            raise ConfigError("test.default_suite must be one of: smoke, regression, core, all")
