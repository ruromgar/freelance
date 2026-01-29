#!/bin/sh

echo "📦 Collecting static files..."
uv run manage.py collectstatic --noinput

echo "🚀 Running migrations..."
uv run manage.py migrate

echo "👤 Ensuring superuser exists..."
uv run manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', '', 'supersecret')
    print('Superuser \"admin\" created.')
else:
    print('Superuser \"admin\" already exists.')
"

echo "🎬 Starting: $*"
exec "$@"
