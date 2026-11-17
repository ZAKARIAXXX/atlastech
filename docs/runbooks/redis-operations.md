# Runbook — Redis Operations

How to inspect, maintain, and recover the Redis 7 instance that backs
AtlasTech's cache and transient state. Redis runs in Docker Compose,
bound to `127.0.0.1:6379` (localhost only — see ADR-005), with its data
in the named volume `redis_data`.

> **Golden rule:** PostgreSQL is the source of truth. Redis holds
> cache and transient data only (see ADR-006). Losing Redis data is an
> inconvenience; losing PostgreSQL data is an incident.

## Health checks

```bash
docker compose ps                 # redis should show (healthy)
docker compose exec redis redis-cli ping        # → PONG
docker compose exec redis redis-cli INFO server # version, uptime
docker compose exec redis redis-cli DBSIZE      # key count
docker compose exec redis redis-cli INFO memory # memory usage
```

The Compose healthcheck is `redis-cli ping`; the API only starts once
Redis reports healthy (`depends_on: condition: service_healthy`).

## Inspecting keys

```bash
docker compose exec redis redis-cli --scan --pattern 'atlas:*' | head -50
docker compose exec redis redis-cli TTL <key>        # expiry remaining
docker compose exec redis redis-cli TYPE <key>       # string/hash/list/…
docker compose exec redis redis-cli MONITOR          # live command feed (Ctrl-C to stop)
```

Use `--scan`, never `KEYS *`, on anything but an empty local instance —
`KEYS` blocks the server.

## Clearing the cache

Safe when the cache is stale or corrupted; the API rebuilds entries
from PostgreSQL on demand.

```bash
docker compose exec redis redis-cli FLUSHDB   # current database only
```

Do **not** use `FLUSHALL` unless every logical database is in scope,
and never as a first resort for an application bug — capture
`INFO keyspace` and a sample of the offending keys first.

## Persistence and restart behaviour

- Data survives `docker compose restart redis` and `docker compose down`
  via the `redis_data` volume.
- `docker compose down -v` **deletes** the volume. Cache loss is
  recoverable, but confirm no queue or session data is in flight first.
- After an unplanned restart, verify with `redis-cli ping` and watch the
  API logs for reconnect errors before declaring recovery.

## Common failures

| Symptom | Check | Fix |
| --- | --- | --- |
| API logs `Connection refused` to Redis | `docker compose ps` — is Redis up and healthy? | `docker compose up -d redis`, then re-check health |
| Healthcheck stuck on `starting` | `docker compose logs redis` | Look for volume permission or config errors at boot |
| Memory growing without bound | `INFO memory`, `DBSIZE`, sample TTLs | Keys without expiry are the usual cause — fix the writer, then flush |
| Everything slow, Redis CPU high | `redis-cli --latency`, `SLOWLOG GET 5` | Identify the blocking command; avoid `KEYS`/large scans |

## Related

- [ADR-003 — Postgres & Redis data layer](../adr/ADR-003-postgres-redis-data-layer.md)
- [ADR-006 — Redis usage boundaries](../adr/ADR-006-redis-usage-boundaries.md)
- [Database backup & restore](database-backup-restore.md)
- [Troubleshooting](TROUBLESHOOTING.md)
