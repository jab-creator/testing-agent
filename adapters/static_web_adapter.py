from __future__ import annotations
from adapters.shared.base_adapter import BaseAdapter
from runners.selenium_runner import SeleniumRunner

class StaticWebAdapter(BaseAdapter):
    def make_runner(self, config: dict, repo_path: str, agent_repo_root: str):
        return SeleniumRunner(config=config, repo_path=repo_path, agent_repo_root=agent_repo_root)
