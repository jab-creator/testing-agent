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

The command exits with `0` on smoke test success and non-zero on failure, and prints:
- `SMOKE_TEST: PASS`
- `SMOKE_TEST: FAIL`
