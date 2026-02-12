import argparse
import sys
from pathlib import Path
import subprocess

from agent_core.orchestrator import Orchestrator


TARGET_WORKFLOW_PATH = Path(".github/workflows/qa-agent.yml")

TARGET_WORKFLOW_TEMPLATE = """\
name: QA Agent

on:
  pull_request:
  workflow_dispatch:

permissions:
  contents: read
  pull-requests: write

jobs:
  qa:
    uses: jab-creator/testing-agent/.github/workflows/run-agent.yml@main
    with:
      target_repo: ${{ github.repository }}
      target_ref: ${{ github.event.pull_request.head.sha || github.sha }}
"""

QA_AGENT_YML_TEMPLATE = """\
project:
  name: "CHANGE_ME"
  type: "static_web"

run:
  command: "python3 -m http.server 8000"
  wait_for: "http://localhost:8000/"
  timeout: 15

test:
  target_folder: "CHANGE_ME"
  strategy: "selenium"

env:
  APP_BASE_URL: "http://localhost:8000/"
"""


def _run(cmd: list[str], cwd: Path | None = None) -> None:
    subprocess.run(cmd, cwd=str(cwd) if cwd else None, check=True)


def enroll(repo_url: str, force: bool = False) -> int:
    """
    Enroll a target repo by adding:
      - .github/workflows/qa-agent.yml
      - .qa-agent.yml (template) if missing
    Commits & pushes to default branch.
    """
    # Clone to a temp workspace folder
    workspace = Path("workspace") / "enroll"
    workspace.mkdir(parents=True, exist_ok=True)

    # Convert URL -> owner/name
    # Expect: https://github.com/owner/repo(.git)
    parts = repo_url.rstrip("/").split("/")
    owner, repo = parts[-2], parts[-1].removesuffix(".git")
    full = f"{owner}/{repo}"

    repo_dir = workspace / repo
    if repo_dir.exists():
        _run(["rm", "-rf", str(repo_dir)])

    # gh clone (uses your gh auth)
    _run(["gh", "repo", "clone", full, str(repo_dir)])

    # Determine default branch
    default_branch = subprocess.check_output(
        ["gh", "repo", "view", full, "--json", "defaultBranchRef", "-q", ".defaultBranchRef.name"],
        text=True
    ).strip()

    # Checkout default branch
    _run(["git", "checkout", default_branch], cwd=repo_dir)

    # Ensure workflow dir exists
    (repo_dir / ".github" / "workflows").mkdir(parents=True, exist_ok=True)

    workflow_file = repo_dir / TARGET_WORKFLOW_PATH
    if workflow_file.exists() and not force:
        print(f"[enroll] {TARGET_WORKFLOW_PATH} already exists (use --force to overwrite).")
    else:
        workflow_file.write_text(TARGET_WORKFLOW_TEMPLATE, encoding="utf-8")
        print(f"[enroll] wrote {TARGET_WORKFLOW_PATH}")

    qa_agent_file = repo_dir / ".qa-agent.yml"
    if qa_agent_file.exists() and not force:
        print("[enroll] .qa-agent.yml already exists (leaving as-is).")
    else:
        qa_agent_file.write_text(QA_AGENT_YML_TEMPLATE, encoding="utf-8")
        print("[enroll] wrote .qa-agent.yml (template)")

    # Ensure SSH remote so pushes don't prompt for HTTPS creds
    _run(["git", "remote", "set-url", "origin", f"git@github.com:{full}.git"], cwd=repo_dir)

    # Create a branch for the enroll changes (avoid protected main)
    branch = "qa-agent/enroll"
    _run(["git", "checkout", "-B", branch], cwd=repo_dir)

    status = subprocess.check_output(["git", "status", "--porcelain"], cwd=repo_dir, text=True).strip()
    if not status:
        print("[enroll] no changes to commit.")
        return 0

    _run(["git", "add", ".github/workflows/qa-agent.yml", ".qa-agent.yml"], cwd=repo_dir)
    _run(["git", "commit", "-m", "Add QA Agent workflow + config"], cwd=repo_dir)
    _run(["git", "push", "-u", "origin", branch], cwd=repo_dir)

    # Open PR (idempotent-ish: if PR already exists, gh will error; that's OK for v1)
    _run([
        "gh", "pr", "create",
        "--repo", full,
        "--base", default_branch,
        "--head", branch,
        "--title", "Add QA Agent workflow",
        "--body", "This PR enrolls the repo into the testing-agent QA system by adding the QA Agent workflow and config."
    ], cwd=repo_dir)

    print(f"[enroll] opened PR to enroll {full}")
    return 0


def main():
    parser = argparse.ArgumentParser(prog="qa")
    sub = parser.add_subparsers(dest="cmd")

    # run (default)
    runp = sub.add_parser("run", help="Run QA against a repo")
    runp.add_argument("--repo", required=True, help="Git repo URL to test")
    runp.add_argument("--ref", required=False, help="Git ref/branch/commit to checkout")

    # backward compatible flags (qa --repo ...)
    parser.add_argument("--repo", required=False, help=argparse.SUPPRESS)
    parser.add_argument("--ref", required=False, help=argparse.SUPPRESS)

    # enroll
    enp = sub.add_parser("enroll", help="Enroll a repo (adds workflow + .qa-agent.yml)")
    enp.add_argument("--repo", required=True, help="Git repo URL to enroll")
    enp.add_argument("--force", action="store_true", help="Overwrite existing files")

    args = parser.parse_args()

    # Back-compat: if user ran `qa --repo ...`, treat it as run
    if args.cmd is None and getattr(args, "repo", None):
        args.cmd = "run"
        args = argparse.Namespace(cmd="run", repo=args.repo, ref=getattr(args, "ref", None))

    if args.cmd == "run":
        orch = Orchestrator(repo_url=args.repo, ref=getattr(args, "ref", None))
        res = orch.run()
        return res.exit_code

    if args.cmd == "enroll":
        return enroll(args.repo, force=args.force)

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
