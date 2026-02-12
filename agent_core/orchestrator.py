from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path

from agent_core.repo_manager import RepoManager
from agent_core.config_loader import load_config
from agent_core.adapter_factory import AdapterFactory

@dataclass
class OrchestratorResult:
    repo_path: str
    pytest_exit_code: int

class Orchestrator:
    def __init__(self, repo_url: str, ref: str | None = None, workspace_dir: str = "workspace"):
        self.repo_url = repo_url
        self.ref = ref
        self.workspace_dir = workspace_dir
        # Resolve against installed package/source tree, not process CWD.
        self.agent_repo_root = Path(__file__).resolve().parents[1]

    def run(self) -> OrchestratorResult:
        repo_path = RepoManager.clone(self.repo_url, self.ref, self.workspace_dir)
        try:
            cfg = load_config(repo_path)
            project_type = cfg["project"]["type"]
            adapter = AdapterFactory.get_adapter(project_type)

            runner = adapter.make_runner(cfg, str(repo_path), agent_repo_root=str(self.agent_repo_root))
            try:
                runner.start_app()
                result = runner.run_tests()
            finally:
                runner.stop_app()

            return OrchestratorResult(repo_path=str(repo_path), pytest_exit_code=result.pytest_exit_code)
        finally:
            # For MVP we keep workspace around for debugging; later we can auto-cleanup.
            pass
