# AtlasTech — Status

Active development. See the Roadmap in README.md for the current phase.

## CI (2026-11-13)

- Main is red: the Security Scan job fails because `aquasecurity/trivy-action@0.28.0` no longer resolves (tag deleted after the March 2026 Trivy compromise; fix is the `v0.36.0` bump in `.github/workflows/ci.yml`).
- API Lint & Type Check also fails (exit 1); cause still under investigation — triage procedure in `docs/runbooks/api-lint-typecheck.md`.
- See `docs/runbooks/TROUBLESHOOTING.md` (CI section) for details.

## Next actions

- [ ] Bump `aquasecurity/trivy-action` to `v0.36.0` in `.github/workflows/ci.yml` (one line).
- [ ] Run the API lint/type check locally from `services/api` and record the first error here.
