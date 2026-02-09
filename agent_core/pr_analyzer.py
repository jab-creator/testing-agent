from __future__ import annotations
from pathlib import Path
import subprocess

def changed_files(repo_path: str | Path, base_ref: str = "origin/main") -> list[str]:
    """
    Basic diff helper. For MVP, compare current HEAD to base_ref.
    """
    repo_path = Path(repo_path)
    try:
        subprocess.check_call(["git", "fetch", "--all", "--prune"], cwd=repo_path)
    except Exception:
        pass
    out = subprocess.check_output(
        ["git", "diff", "--name-only", f"{base_ref}...HEAD"],
        cwd=repo_path,
        text=True,
    )
    return [line.strip() for line in out.splitlines() if line.strip()]
