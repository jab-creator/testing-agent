from __future__ import annotations
from pathlib import Path
import subprocess
import shutil
import uuid

class RepoManager:
    @staticmethod
    def clone(repo_url: str, ref: str | None = None, workspace_dir: str | Path = "workspace") -> Path:
        workspace_dir = Path(workspace_dir)
        workspace_dir.mkdir(parents=True, exist_ok=True)

        target = workspace_dir / f"repo_{uuid.uuid4().hex[:8]}"
        subprocess.check_call(["git", "clone", "--depth", "1", repo_url, str(target)])

        if ref:
            # fetch + checkout for branches, tags, or PR refs if provided
            subprocess.check_call(["git", "fetch", "--all", "--prune"], cwd=target)
            subprocess.check_call(["git", "checkout", ref], cwd=target)

        return target

    @staticmethod
    def cleanup(path: str | Path) -> None:
        path = Path(path)
        if path.exists():
            shutil.rmtree(path, ignore_errors=True)
