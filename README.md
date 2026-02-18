# testing-agent

Standalone test agent that can test multiple repos by reading a small `.qa-agent.yml` in each target repo.

## Goals (MVP)
- Clone a repo + checkout a branch/PR ref
- Read `.qa-agent.yml`
- Select an adapter (static_web first)
- Start the app
- Run tests stored in this agent repo under `tests/<target_folder>/`

## CLI
- `qa --repo <repo_url>`
- `qa --repo <repo_url> --ref <commit_or_ref>`
- `qa --repo <repo_url> --ref <commit_or_ref> --suite <smoke|regression|core|all>`

Defaults:
- `--suite smoke` if not provided
- `core` is an alias of `regression`

Exit behavior:
- exits `0` when selected suite passes
- exits non-zero when selected suite fails

Output markers:
- `TEST_SUITE(<suite>): PASS`
- `TEST_SUITE(<suite>): FAIL`
- `SMOKE_TEST: PASS|FAIL` (also printed for smoke compatibility)

## Test suites
Tests are organized under `tests/<target_folder>/`. For Canadian Citizenship Tracker this is:
- `tests/citizenship_tracker/test_smoke.py` (minimal)
- `tests/citizenship_tracker/test_regression.py` (HTTP-based core checks)

## Local usage
Run smoke:
```bash
qa --repo /home/mrjab/projects/canadian-citizen-progression --suite smoke
```

Run regression:
```bash
qa --repo /home/mrjab/projects/canadian-citizen-progression --suite regression
```

## CI usage
GitHub Actions can call:
```bash
qa --repo "$REPO" --ref "$SHA" --suite smoke
qa --repo "$REPO" --ref "$SHA" --suite regression
```
