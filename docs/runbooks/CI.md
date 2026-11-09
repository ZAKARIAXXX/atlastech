# CI

AtlasTech runs GitHub Actions on every push and pull request to `main`.

## Pipeline

Defined in `.github/workflows/ci.yml`. Concurrency cancels in-progress runs on the same ref.

| Job | What it does |
|---|---|
| API Lint & Type Check (`api-lint`) | `ruff check`, `ruff format --check`, `mypy` in `services/api` (Python 3.11) |
| API Tests (`api-test`) | `pytest` with coverage against Postgres 16 (needs `api-lint`) |
| Web Lint & Type Check (`web-lint`) | `npm run lint`, `npm run typecheck` in `apps/web` (Node 22) |
| Shared Schemas Type Check (`schemas-typecheck`) | `npm run typecheck` in `packages/schemas` |
| Security Scan (`security`) | Trivy filesystem scan (`scan-type: fs`, severity `CRITICAL,HIGH`) via `aquasecurity/trivy-action` — see TROUBLESHOOTING.md (CI section) for the current pin and a known tag-deletion issue |

## Re-running a failed job

- From the failed run on GitHub: **Re-run failed jobs** (or **Re-run all jobs** if the failure is environmental).
- A re-run uses the same commit — it does not pick up new pushes.

## Debugging locally

Reproduce a job failure on your machine before pushing a fix:

- API lint/typecheck: from `services/api`, with the venv active — `pip install -e ".[dev]"`, then `ruff check .`, `ruff format --check .`, `mypy .`.
- API tests: from `services/api` — `python -m pytest --cov=app --cov-report=xml -v` (needs Postgres running; see `docker compose`).
- Web lint/typecheck: from `apps/web` — `npm ci`, then `npm run lint` and `npm run typecheck`.
- Security scan: Trivy runs in CI only. If the scan fails on action resolution (e.g. a deleted tag), see the CI section in `TROUBLESHOOTING.md`.

## Known issues

- See the CI section in `docs/runbooks/TROUBLESHOOTING.md` for current known failures and their fixes.
