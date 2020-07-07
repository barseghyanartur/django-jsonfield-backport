import functools
import json

import django
from django.core.exceptions import ImproperlyConfigured
from django.db import transaction
from django.db.backends.signals import connection_created
from django.db.backends.sqlite3.base import none_guard
from django.db.utils import OperationalError
from django.dispatch import receiver
from django.utils.version import PY38


class MySQLFeatures:
    def supports_json_field(self):
        if self.connection.mysql_is_mariadb:
            return self.connection.mysql_version >= (10, 2, 7)
        return self.connection.mysql_version >= (5, 7, 8)

    supports_primitives_in_json_field = True
    has_native_json_field = False
    has_json_operators = False


class OracleFeatures:
    supports_json_field = True
    supports_primitives_in_json_field = False
    has_native_json_field = False
    has_json_operators = False


class PostgresFeatures:
    supports_json_field = True
    supports_primitives_in_json_field = True
    has_native_json_field = True
    has_json_operators = True


class SQLiteFeatures:
    def supports_json_field(self):
        try:
            with self.connection.cursor() as cursor, transaction.atomic():
                cursor.execute('SELECT JSON(\'{"a": "b"}\')')
        except OperationalError:
            return False
        return True

    supports_primitives_in_json_field = True
    has_native_json_field = False
    has_json_operators = False


feature_classes = {
    "mysql": MySQLFeatures,
    "oracle": OracleFeatures,
    "postgresql": PostgresFeatures,
    "sqlite": SQLiteFeatures,
}


feature_names = [
    "supports_json_field",
    "supports_primitives_in_json_field",
    "has_native_json_field",
    "has_json_operators",
]


@receiver(connection_created)
def extend_features(connection=None, **kwargs):
    if django.VERSION >= (3, 1):
        return
    for name in feature_names:
        value = feature = getattr(feature_classes[connection.vendor], name)
        if callable(feature):
            value = feature(connection.features)
        setattr(connection.features, name, value)


@none_guard
def _sqlite_json_contains(haystack, needle):
    target, candidate = json.loads(haystack), json.loads(needle)
    if isinstance(target, dict) and isinstance(candidate, dict):
        return target.items() >= candidate.items()
    return target == candidate


@receiver(connection_created)
def extend_sqlite(connection=None, **kwargs):
    if connection.vendor == "sqlite":
        if PY38:
            create_deterministic_function = functools.partial(
                connection.connection.create_function, deterministic=True,
            )
        else:
            create_deterministic_function = connection.connection.create_function
        create_deterministic_function("JSON_CONTAINS", 2, _sqlite_json_contains)
