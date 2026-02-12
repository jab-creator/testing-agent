from __future__ import annotations
import argparse
import sys
from agent_core.orchestrator import Orchestrator

def main():
    p = argparse.ArgumentParser(prog="qa")
    p.add_argument("--repo", required=True, help="Git repo URL to test")
    p.add_argument("--ref", default=None, help="Git ref/branch/commit to checkout")
    args = p.parse_args()

    try:
        orch = Orchestrator(repo_url=args.repo, ref=args.ref)
        res = orch.run()
        print(f"Repo checked out to: {res.repo_path}")
        print(f"Pytest exit code: {res.pytest_exit_code}")
        if res.pytest_exit_code == 0:
            print("SMOKE_TEST: PASS")
        else:
            print("SMOKE_TEST: FAIL")
        raise SystemExit(res.pytest_exit_code)
    except SystemExit:
        raise
    except Exception as exc:
        print(f"qa failed: {exc}", file=sys.stderr)
        print("SMOKE_TEST: FAIL")
        raise SystemExit(2)
