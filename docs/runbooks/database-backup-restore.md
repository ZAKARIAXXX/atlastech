# Runbook — Database Backup & Restore

AtlasTech's source of truth is PostgreSQL 16 (container
`atlastech-postgres`, data in the named Docker volume `postgres_data`).
Redis 7 is the cache layer (see ADR-003) and is treated as disposable — this
runbook backs up PostgreSQL only.

Take a backup before running migrations, changing `docker-compose.yml`, or
any `docker compose down -v` (which permanently deletes the volumes).

## Backup

With the stack running (`make up` or `make dev`):

```bash
mkdir -p backups
docker compose exec -T postgres \
  pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" \
  > "backups/atlastech-$(date +%F-%H%M).sql"
```

`POSTGRES_USER` and `POSTGRES_DB` are the values from your local `.env`.
For a compressed custom-format dump instead:

```bash
docker compose exec -T postgres \
  pg_dump -Fc -U "$POSTGRES_USER" "$POSTGRES_DB" \
  > "backups/atlastech-$(date +%F-%H%M).dump"
```

Verify the backup before trusting it: the file must be non-empty, and for
the plain format `head` should show `PostgreSQL database dump` header lines.

## Restore (plain SQL format)

```bash
# Stop writers so nothing writes during the restore
docker compose stop api web

cat backups/<file>.sql | docker compose exec -T postgres \
  psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"

docker compose start api web
curl http://localhost:8000/health
```

For a custom-format (`.dump`) backup, restore with `pg_restore`:

```bash
cat backups/<file>.dump | docker compose exec -T postgres \
  pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists
```

## Warnings

- `docker compose down -v` deletes `postgres_data` **and** `redis_data`.
  There is no undo. It is a data-destroying command, not a cleanup command.
- Losing `redis_data` alone is not data loss: expect a cold cache, nothing
  more. Losing `postgres_data` without a backup **is** total data loss.
- Backups contain real data and credentials-adjacent material. Keep them out
  of git (they are plain files under `backups/` — never force-add them).
