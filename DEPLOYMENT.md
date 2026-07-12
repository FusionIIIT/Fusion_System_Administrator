# Deployment — hosting the System Administrator under a sub-path

The tool is designed to run **beside the main Fusion app on the same domain** behind a
reverse proxy, at a sub-path (e.g. `https://fusion.iiitdmj.ac.in/sysadmin/`). It does
**not** require any change to the main Fusion app.

The mount path is a single knob — the Vite `base`. The React Router `basename`, the API
base URL, and the auth-cookie path all derive from it, so `/sysadmin/` (or any path) is
just a build/env setting.

## 1. Build the SPA for the sub-path

```bash
cd client
npm ci
APP_BASE_PATH=/sysadmin/ npm run build      # emits client/dist/ served at /sysadmin/
```

The build hard-codes the base, so `dist/index.html` references `/sysadmin/assets/…`,
routes become `/sysadmin/login`, and the API base becomes `/sysadmin/api`.

## 2. One `.env` at the repo root (all config lives here)

Put a single `.env` at the **repository root** (`Fusion_System_Administrator/.env`).
It's git-ignored, so you never edit tracked source on the server — `settings.py` and
`vite.config.js` read everything from it (Django loads root `.env`, falling back to
`Backend/.env`; the frontend build reads `APP_BASE_PATH` from the same file). Real
process env vars still override it.

```ini
DEBUG=False
SECRET_KEY=<strong random secret>
ALLOWED_HOSTS=fusion.iiitdmj.ac.in
APP_BASE_PATH=/sysadmin/     # sub-path the SPA is served under (also used by the build)
AUTH_COOKIE_PATH=/sysadmin   # scope the auth cookie to the mount path

# Main ERP database (managed=False models read/write here)
DB_NAME=fusion_newui_prod
DB_USER=fusion_admin
DB_PASSWORD=...
DB_HOST=127.0.0.1
DB_PORT=5432

# This tool's own database (operators/auth + backup-restore-schedule-health logs)
SYSTEM_DB_NAME=fusion_system_db
SYSTEM_DB_USER=fusion_admin
SYSTEM_DB_PASSWORD=...
SYSTEM_DB_HOST=127.0.0.1
SYSTEM_DB_PORT=5432

# Optional
# REDIS_URL=redis://127.0.0.1:6379/0     # shared login-throttle counter across workers
# BACKUP_ENCRYPTION_KEY=<Fernet key>     # encrypt backup dumps at rest
```

`DEBUG=False` auto-enables `Secure` cookies + HTTPS security headers. The SPA and API are
same-origin, so no CORS config is needed.

## 3. Prepare and run the backend

```bash
cd Backend/backend
python manage.py migrate --database=system_db          # build system_db schema
python manage.py createsuperuser --database=system_db  # create an operator account
gunicorn backend.wsgi:application --bind 127.0.0.1:8001 --workers 3
```

Requirements on the box: `pg_dump`/`pg_restore` on `PATH` (backup/restore), and both
`fusion_newui_prod` and `fusion_system_db` present on the Postgres server.

## 4. nginx — add to the existing `fusion.iiitdmj.ac.in` server block

```nginx
# System Administrator tool — API
location /sysadmin/api/ {
    proxy_pass http://127.0.0.1:8001/api/;     # strips the /sysadmin prefix
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}

# System Administrator tool — SPA (static build from step 1)
location /sysadmin/ {
    alias /var/www/fusion-admin/dist/;
    try_files $uri $uri/ /sysadmin/index.html;
}

# ...existing main Fusion locations unchanged (/, /accounts/, /admin/, /api, ...)
```

The tool is then live at **`https://fusion.iiitdmj.ac.in/sysadmin/login`**. The main
Fusion's `/admin/` (its Django admin), `/accounts/`, and API are untouched.

## Notes

- **Same-origin is required for the cookie.** The httpOnly auth cookie is only sent when
  the SPA and API share an origin — which the nginx layout above guarantees (both under
  `fusion.iiitdmj.ac.in`). Don't split them across hosts/ports.
- **Operators are separate from ERP users.** Admin login authenticates against
  `fusion_system_db` (operators you create), not the ERP `auth_user`. See the two-DB
  design in the codebase (`backend/routers.py`).
- **To use a different path**, just change `APP_BASE_PATH`, `AUTH_COOKIE_PATH`, and the
  two nginx `location` blocks consistently.
