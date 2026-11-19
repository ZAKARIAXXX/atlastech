# Runbook — Environment variables and secrets

How AtlasTech configuration is supplied, checked, and rotated in the
local environment.

## Principles

- `.env` is local-only and never committed. `.env.example` documents
  every variable with safe placeholder values and is always committed.
- Required secrets fail fast: the API refuses to start when a required
  variable is missing or empty. A service that starts with a silent
  default password is a vulnerability, not a convenience.
- One variable, one purpose. Reusing the same password for the
  database, the API, and an admin account defeats rotation.

## Adding a variable

1. Add it to `.env.example` with a placeholder and a one-line comment
   stating what it is for.
2. Add the real value to your local `.env` only.
3. If the variable is required, make the startup check fail without
   it — and say so in the pull request.
4. Document it here if it changes how the system is operated.

## Checking the current setup

```bash
# which variables exist (names only — never print values into logs,
# tickets, or chat)
cut -d= -f1 .env | sort

# confirm .env is ignored
git check-ignore .env
```

If `git check-ignore` prints nothing, `.env` is NOT ignored — stop
and fix `.gitignore` before committing anything.

## Rotation

Rotate a secret when: it was pasted somewhere it should not have
been, a collaborator leaves, or it is older than the project phase it
was created for.

1. Generate the new value locally.
2. Update the service that owns the secret (for example the database
   user password inside PostgreSQL).
3. Update `.env` for every consumer of that secret.
4. Restart the affected services and run their health checks
   (`api-operations.md`, `postgres-operations.md`).
5. Confirm the old value no longer works.

## If a secret is committed

Treat it as compromised, not as a typo:

1. Rotate it immediately (procedure above) — deleting the commit does
   not un-leak it.
2. Rewrite history only after rotation, and note the incident in the
   changelog.
3. Check what the secret could reach: a database password committed
   alongside a public hostname is worse than one for a localhost-only
   service. Scope the response to the actual exposure.
