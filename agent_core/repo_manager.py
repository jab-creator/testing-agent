from __future__ import annotations
from pathlib import Path
import subprocess
import shutil
import uuid
import re

class RepoManager:
    _SHA_RE = re.compile(r"^[0-9a-fA-F]{7,40}$")

    @staticmethod
    def clone(repo_url: str, ref: str | None = None, workspace_dir: str | Path = "workspace") -> Path:
        workspace_dir = Path(workspace_dir)
        workspace_dir.mkdir(parents=True, exist_ok=True)

        target = workspace_dir / f"repo_{uuid.uuid4().hex[:8]}"
        if ref:
            # Deterministic ref-pinned checkout for CI.
            subprocess.check_call(["git", "clone", "--no-tags", repo_url, str(target)])
            subprocess.check_call(["git", "fetch", "--no-tags", "--depth", "1", "origin", ref], cwd=target)
            subprocess.check_call(["git", "checkout", "--detach", "FETCH_HEAD"], cwd=target)
            RepoManager._verify_ref(target, ref)
        else:
            subprocess.check_call(["git", "clone", "--depth", "1", repo_url, str(target)])

        return target

    @staticmethod
    def cleanup(path: str | Path) -> None:
        path = Path(path)
        if path.exists():
            shutil.rmtree(path, ignore_errors=True)

    @staticmethod
    def _verify_ref(repo_path: Path, requested_ref: str) -> None:
        """Validate sha-like refs resolve to the exact commit requested."""
        if not RepoManager._SHA_RE.fullmatch(requested_ref):
            return

        head = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_path,
            text=True,
        ).strip()
        req = requested_ref.lower()
        if not head.lower().startswith(req):
            raise RuntimeError(f"Checked out commit {head} does not match requested ref {requested_ref}")
