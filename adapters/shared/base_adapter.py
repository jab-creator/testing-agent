from __future__ import annotations
from abc import ABC, abstractmethod

class BaseAdapter(ABC):
    @abstractmethod
    def make_runner(self, config: dict, repo_path: str, agent_repo_root: str):
        raise NotImplementedError
