# Freelance

Freelance income/expense tracking and tax summaries.

## Setup

```bash
uv sync
cp .env.example .env   # fill in secrets
make migrate
make run
```

### Default superuser

When running via Docker, the entrypoint automatically creates a superuser on first launch:

- **Username**: `admin`
- **Password**: `supersecret`

Change the password immediately after first login via the admin panel at `/room/`.

## Stack

- **Backend**: Django 5.x, Django Channels, Daphne (ASGI)
- **Task queue**: Procrastinate
- **Frontend**: Tailwind CSS (CDN), HTMX, jQuery
- **Admin**: Django Admin with Unfold theme (`/room/`)
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Package manager**: uv
