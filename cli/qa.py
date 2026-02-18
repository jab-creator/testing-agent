from __future__ import annotations
import argparse
import sys
from agent_core.orchestrator import Orchestrator


VALID_SUITES = ("smoke", "regression", "core", "all")


def main():
    p = argparse.ArgumentParser(prog="qa")
    p.add_argument("--repo", required=True, help="Git repo URL to test")
    p.add_argument("--ref", default=None, help="Git ref/branch/commit to checkout")
    p.add_argument(
        "--suite",
        default="smoke",
        choices=VALID_SUITES,
        help="Test suite to run: smoke, regression (or core alias), or all",
    )
    args = p.parse_args()

    suite = "regression" if args.suite == "core" else args.suite

    try:
        orch = Orchestrator(repo_url=args.repo, ref=args.ref)
        res = orch.run(suite=suite)
        print(f"Repo checked out to: {res.repo_path}")
        print(f"Suite: {suite}")
        print(f"Pytest exit code: {res.pytest_exit_code}")
        if res.pytest_exit_code == 0:
            print(f"TEST_SUITE({suite}): PASS")
            if suite == "smoke":
                print("SMOKE_TEST: PASS")
        else:
            print(f"TEST_SUITE({suite}): FAIL")
            if suite == "smoke":
                print("SMOKE_TEST: FAIL")
        raise SystemExit(res.pytest_exit_code)
    except SystemExit:
        raise
    except Exception as exc:
        print(f"qa failed: {exc}", file=sys.stderr)
        print(f"TEST_SUITE({suite}): FAIL")
        if suite == "smoke":
            print("SMOKE_TEST: FAIL")
        raise SystemExit(2)
