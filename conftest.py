"""Root conftest — patches procrastinate migrations to skip on SQLite."""

from django.db import connection
from procrastinate.contrib.django import migrations_utils

_original_sql = migrations_utils.RunProcrastinateSQL.database_forwards


def _patched_database_forwards(self, app_label, schema_editor, from_state, to_state):
    if connection.vendor == "sqlite":
        return
    _original_sql(self, app_label, schema_editor, from_state, to_state)


migrations_utils.RunProcrastinateSQL.database_forwards = _patched_database_forwards
