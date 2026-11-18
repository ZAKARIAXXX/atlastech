# Runbook — PostgreSQL operations

Day-2 operations for the AtlasTech PostgreSQL 16 service. Backup and
restore live in `database-backup-restore.md`; this runbook covers the
running database: health, connections, slow queries, and routine
maintenance.

## Service facts

- Container from Docker Compose; data in the named volume `postgres_data`.
- Reachable locally at `127.0.0.1:5432` only — never exposed publicly.
- The API is the only application client. Redis is never a data source
  (see ADR-006); if data looks wrong, PostgreSQL is where the truth is.

## Health checks

```bash
docker compose exec postgres pg_isready
docker compose exec postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "select 1;"
```

`pg_isready` is also the Compose healthcheck; a service that never
becomes healthy blocks its dependents, which is the intended behaviour.

## Connections

```sql
-- who is connected, from where, doing what
select pid, usename, client_addr, state, query
from pg_stat_activity
where datname = current_database();

-- connection budget
show max_connections;
```

Symptom: API returns 500s on every endpoint and logs connection
errors → check this view first. A pile of `idle in transaction`
sessions means a client is holding transactions open; identify the
pid before terminating anything.

## Slow queries

```sql
-- currently running queries, longest first
select pid, now() - query_start as duration, state, query
from pg_stat_activity
where state = 'active'
order by duration desc;
```

Rules:

- Read the query before killing it. Long analytical reads are not the
  same problem as a runaway write.
- A missing index shows up as repeated sequential scans on the same
  table; record the table and query in an issue instead of improvising
  schema changes during an incident.

## Routine maintenance

- `VACUUM (ANALYZE)` is handled by autovacuum under normal load; only
  run it manually after a bulk delete or import, and note that you did.
- Watch volume growth: `docker system df -v` shows the `postgres_data`
  volume size. Sudden growth usually means runaway logging or a bad
  import, not organic data.

## Failure table

| Symptom | Likely cause | First action |
| --- | --- | --- |
| `pg_isready` fails | Container down or still starting | `docker compose ps`, then container logs |
| API cannot connect | Wrong credentials in `.env`, or DB not healthy yet | Compare `.env` values with the Compose service definition; wait for healthy |
| Connections exhausted | Leaked sessions, `idle in transaction` | Inspect `pg_stat_activity`; fix the client, then restart the API |
| Disk full on the volume | Unbounded table or log growth | Identify the largest relations before deleting anything |
