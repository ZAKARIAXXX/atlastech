# Contributing to AtlasTech

AtlasTech is developed as a small, disciplined project: every change is
reviewable, documented, and verified locally before it is pushed.

## Workflow

1. Branch from `main` — do not commit directly to `main` for feature work.
2. Make the smallest change that solves the problem.
3. Run the local checks (below) and confirm the stack still starts.
4. Update the docs in the same change when behaviour, configuration, or
   operations are affected.
5. Open a pull request describing **what** changed and **why**.

## Branch and commit conventions

- Branch names: `feat/<topic>`, `fix/<topic>`, `docs/<topic>`,
  `chore/<topic>` — lowercase, hyphens, no spaces.
- Commit messages: imperative mood, one line summary
  (e.g. `Add Redis operations runbook`), body explaining the reason when
  the change is not self-evident.
- One logical change per commit. A refactor and a behaviour change are
  two commits.

## Local checks before pushing

- Stack starts clean: `make up` (see
  [local development runbook](docs/runbooks/local-development.md)).
- API lint & type check passes from `services/api` (triage procedure:
  [API lint & type check runbook](docs/runbooks/api-lint-typecheck.md)).
- Web app builds without type errors.
- CI must be green on the pull request before merge — see the
  [CI runbook](docs/runbooks/CI.md) for what each job enforces.

## Documentation rules

- **Decisions** go in an ADR under `docs/adr/` (next free number,
  format follows the existing ADRs: Status, Context, Decision,
  Consequences).
- **Procedures** go in a runbook under `docs/runbooks/`.
- Every new doc is linked from the
  [documentation index](docs/README.md) in the same change.
- `docs/STATUS.md` and `CHANGELOG.md` are updated when a change is
  notable; the changelog entry is dated.

## Configuration

- Never commit a real `.env` file or any secret. Required variables are
  declared in the Compose file and templated in `.env.example`
  (see ADR-005).
- Adding a required variable means updating `.env.example` and the
  local development runbook in the same change.

## Reporting problems

- Security issues: follow [SECURITY.md](SECURITY.md) — do not open a
  public issue for a vulnerability.
- Operational problems: reproduce with the stack running, then check the
  [troubleshooting runbook](docs/runbooks/TROUBLESHOOTING.md) before
  filing.
