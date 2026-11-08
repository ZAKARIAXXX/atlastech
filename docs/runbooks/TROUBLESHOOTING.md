# Troubleshooting

Common setup and runtime issues for AtlasTech.

## Docker

### `make up` fails / Docker not running

- Make sure Docker Desktop is running before `make up`.
- On Windows, confirm Docker Desktop is set to Linux containers.

### A service fails to start

- Check which service failed: `docker compose ps` and `docker compose logs <service>`.
- Rebuild after a dependency change: `docker compose up -d --build`.

## Ports

### Port 3000 or 8000 already in use

- Dashboard uses port 3000, API uses port 8000.
- Find what is using the port and stop it, or change the port mapping in `docker-compose.yml`.
- On Windows (PowerShell): `Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess`.

## Database

### API cannot connect to PostgreSQL

- Confirm Postgres is up: `docker compose ps postgres`.
- Wait for Postgres to finish initialising on first start, then restart the API: `docker compose restart api`.
- Check the database URL in `.env` matches `.env.example`.

### Redis connection errors

- Confirm Redis is up: `docker compose ps redis`.
- Restart Redis: `docker compose restart redis`.

## API

### `alembic upgrade head` fails

- Make sure Postgres is running and reachable before running migrations.
- Run migrations from `services/api` with the virtual environment activated.

### Module import errors in the API

- Install dependencies first: `pip install -e .` from `services/api`.
- Confirm Python 3.11+ is in use: `python --version`.

## Web dashboard

### `npm install` or `npm run dev` fails

- Confirm Node.js 22+ is in use: `node --version`.
- Delete `node_modules` and reinstall: `rm -rf node_modules && npm install` (from `apps/web`).

## Telemetry collector (Windows)

### Collector script is blocked

- PowerShell execution policy may block the script. Run PowerShell as Administrator and set the policy for the session, or use the installer: `.\agents\collector\install.ps1 -ApiUrl "http://YOUR_API:8000/api/v1/telemetry"`.
- Confirm the API URL is reachable from the endpoint before running the collector.
