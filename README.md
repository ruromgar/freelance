# Freelance

Gestión fiscal para autónomos: control de ingresos, gastos y cálculo de modelos trimestrales (303, 130) y anuales (390).

## Setup

```bash
uv sync
cp .env.example .env   # rellenar con tus datos
make migrate
make run
```

### Superusuario por defecto

Al ejecutar con Docker, el entrypoint crea automáticamente un superusuario en el primer arranque:

- **Usuario**: `admin`
- **Contraseña**: `supersecret`

Cambia la contraseña tras el primer inicio de sesión desde el panel de admin en `/room/`.

## Stack

- **Backend**: Django 5.x
- **Frontend**: Tailwind CSS (CDN), HTMX
- **Admin**: Django Admin con tema Unfold (`/room/`)
- **Base de datos**: SQLite (dev) / PostgreSQL (prod)
- **Gestor de paquetes**: uv
