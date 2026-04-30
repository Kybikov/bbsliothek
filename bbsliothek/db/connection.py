from __future__ import annotations

from typing import Any

from bbsliothek.config import AppConfig
from bbsliothek.exceptions import DependencyError, RepositoryError

try:
    import mysql.connector as mysql_connector
    from mysql.connector import Error as MySQLError
except ImportError:  # pragma: no cover - wird in Tests bewusst nicht benötigt
    mysql_connector = None
    MySQLError = Exception


def create_connection(config: AppConfig, use_database: bool = True) -> Any:
    if mysql_connector is None:
        raise DependencyError(
            "Das Paket 'mysql-connector-python' fehlt. Bitte installiere die Abhängigkeiten "
            "mit 'pip install -r requirements.txt'."
        )

    connection_options: dict[str, Any] = {
        "host": config.db_host,
        "port": config.db_port,
        "user": config.db_user,
        "password": config.db_password,
    }
    if use_database:
        connection_options["database"] = config.db_name

    try:
        return mysql_connector.connect(**connection_options)
    except MySQLError as exc:  # pragma: no cover - benötigt echte Datenbank
        raise RepositoryError(f"MySQL-Verbindung fehlgeschlagen: {exc}") from exc
