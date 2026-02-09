from __future__ import annotations
import argparse
from agent_core.orchestrator import Orchestrator

def main():
    p = argparse.ArgumentParser(prog="qa")
    p.add_argument("--repo", required=True, help="Git repo URL to test")
    p.add_argument("--ref", default=None, help="Git ref/branch/commit to checkout")
    args = p.parse_args()

    orch = Orchestrator(repo_url=args.repo, ref=args.ref)
    res = orch.run()

    print(f"Repo checked out to: {res.repo_path}")
    print(f"Pytest exit code: {res.pytest_exit_code}")

    raise SystemExit(res.pytest_exit_code)
