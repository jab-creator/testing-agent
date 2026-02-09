from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import os
import pytest
import socket

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
        cmd = self.config["run"]["command"]
        wait_for = self.config["run"]["wait_for"]
        timeout = int(self.config["run"].get("timeout", 20))
        # Preflight: if port is in use, it's almost always a leaked server.
        # Fail fast so we don't accidentally test against the wrong instance.
        host, port = "127.0.0.1", 8000
        s = socket.socket()
        try:
            s.bind((host, port))
        finally:
            s.close()

        self.proc = ProcessRunner.start(cmd, cwd=str(self.repo_path))
        wait_for_url(wait_for, timeout_s=timeout)

    def run_tests(self) -> SeleniumRunResult:
        env = self.config.get("env", {})
        for k, v in env.items():
            os.environ[str(k)] = str(v)

        target_folder = self.config["test"]["target_folder"]
        test_path = self.agent_repo_root / "tests" / target_folder
        exit_code = pytest.main([str(test_path), "-q"])
        return SeleniumRunResult(pytest_exit_code=int(exit_code))

    def stop_app(self):
        if self.proc:
            ProcessRunner.stop(self.proc)
            self.proc = None
