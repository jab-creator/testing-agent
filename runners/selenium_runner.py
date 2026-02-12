from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import os
import subprocess
import sys

from runners.process_runner import ProcessRunner, ProcessHandle
from agent_core.utils.http_wait import wait_for_url

@dataclass
class SeleniumRunResult:
    pytest_exit_code: int

class SeleniumRunner:
    def __init__(self, config: dict, repo_path: str | Path, agent_repo_root: str | Path):
        self.config = config
        self.repo_path = Path(repo_path)
        self.agent_repo_root = Path(agent_repo_root)
        self.proc: ProcessHandle | None = None

    def start_app(self):
        run_cfg = self.config["run"]
        cmd = run_cfg["command"]
        wait_for = run_cfg["wait_for"]
        timeout = int(run_cfg.get("timeout", 20))

        self.proc = ProcessRunner.start(cmd, cwd=str(self.repo_path))
        wait_for_url(wait_for, timeout_s=timeout)

    def run_tests(self) -> SeleniumRunResult:
        env_overrides = self.config.get("env", {}) or {}
        merged_env = os.environ.copy()
        for k, v in env_overrides.items():
            merged_env[str(k)] = str(v)

        test_cfg = self.config["test"]
        base_url_env = test_cfg.get("base_url_env")
        base_url_env = base_url_env or "APP_BASE_URL"
        merged_env["QA_BASE_URL_ENV"] = base_url_env
        if base_url_env not in merged_env:
            merged_env[base_url_env] = self.config["run"]["wait_for"]

        smoke_endpoints = test_cfg.get("endpoints")
        if isinstance(smoke_endpoints, list):
            clean = [str(x).strip() for x in smoke_endpoints if str(x).strip()]
            if clean:
                merged_env["QA_SMOKE_ENDPOINTS"] = ",".join(clean)

        target_folder = test_cfg["target_folder"]
        test_path = self.agent_repo_root / "tests" / target_folder
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", str(test_path), "-q", "--maxfail=1"],
            cwd=str(self.agent_repo_root),
            env=merged_env,
            check=False,
        )
        return SeleniumRunResult(pytest_exit_code=int(proc.returncode))

    def stop_app(self):
        if self.proc:
            ProcessRunner.stop(self.proc)
            self.proc = None
