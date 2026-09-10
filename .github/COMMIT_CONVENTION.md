# AtlasTech Commit Convention

All commits in AtlasTech follow the [Conventional Commits](https://www.conventionalcommits.org/) specification. This ensures automated changelog generation, clean semantic versioning, and clear git history.

## Structure

```
<type>(<scope>): <subject>

[optional body]

[optional footer(s)]
```

### 1. Header Format

- **Type**: lowercase verb describing the nature of the change (see below).
- **Scope**: optional (but strongly encouraged) lowercase identifier of the monorepo component.
- **Subject**: concise summary in imperative, present tense ("add", not "added" or "adds"). Do not capitalize the first letter and do not end with a period. Maximum 72 characters.

### 2. Allowed Types

| Type | Description |
| :--- | :--- |
| `feat` | New feature or capability for the user or platform |
| `fix` | Bug fix or issue resolution |
| `security` | Security hardening, vulnerability fix, or credential protection |
| `docs` | Documentation-only updates (README, ADRs, runbooks, comments) |
| `refactor` | Code restructuring without behavioral change or bug fix |
| `perf` | Performance improvement or optimization |
| `test` | Adding missing tests or fixing test suites |
| `build` | Changes to build tooling, dependencies, or package configs |
| `ci` | Modifications to CI/CD workflows (GitHub Actions, lint scripts) |
| `chore` | Maintenance tasks, repository templates, git configs, tooling |
| `revert` | Reverts a previous commit |

### 3. Allowed Scopes

| Scope | Path / Purpose |
| :--- | :--- |
| `api` | `services/api` — FastAPI, SQLAlchemy models, Alembic, telemetry engine |
| `web` | `apps/web` — Next.js 15 frontend, Tailwind CSS, components, pages |
| `collector` | `agents/collector` — PowerShell telemetry script and scheduled task installer |
| `infra` | `infra/` — Docker, Vagrant, AD, DNS, domain scripts |
| `lab` | `infra/lab` — Virtual lab setup and environment provisioning |
| `chaos` | `infra/chaos` — Fault injection playbooks and reset scripts |
| `schemas` | `packages/schemas` — Shared TypeScript types and telemetry contracts |
| `docs` | `docs/` or `README.md` — ADRs, architecture docs, plans, runbooks |
| `git` | Repository git settings, hooks, `.gitmessage` template |
| `deps` | Monorepo dependency upgrades |

### 4. Examples

- `feat(lab): add Vagrantfile and automated Domain Controller provisioning`
- `feat(api): implement telemetry ingestion threshold evaluation engine`
- `feat(web): build interactive operations console and incident desk`
- `fix(collector): resolve DNS query timeout handling on Windows 10`
- `security(api): enforce API key verification on ingestion endpoints`
- `docs(readme): fix repository URLs and sync roadmap progress`
- `chore(git): add commit message template and convention guide`

## Using the Git Message Template

A `.gitmessage` template is included in the root directory. To enable it locally:

```bash
git config --local commit.template .gitmessage
```
