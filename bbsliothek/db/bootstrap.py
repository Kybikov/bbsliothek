from __future__ import annotations

from pathlib import Path

from bbsliothek.config import AppConfig
from bbsliothek.db.connection import create_connection
from bbsliothek.exceptions import RepositoryError


def _split_sql_script(script: str) -> list[str]:
    statements: list[str] = []
    current: list[str] = []
    in_single_quote = False
    in_double_quote = False

    for line in script.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("--"):
            continue

        current_line = []
        for char in line:
            if char == "'" and not in_double_quote:
                in_single_quote = not in_single_quote
            elif char == '"' and not in_single_quote:
                in_double_quote = not in_double_quote

            if char == ";" and not in_single_quote and not in_double_quote:
                statement = "".join(current + current_line).strip()
                if statement:
                    statements.append(statement)
                current = []
                current_line = []
            else:
                current_line.append(char)

        if current_line:
            current.append("".join(current_line) + "\n")

    remainder = "".join(current).strip()
    if remainder:
        statements.append(remainder)
    return statements


def _execute_sql_file(config: AppConfig, file_path: Path) -> None:
    connection = create_connection(config, use_database=False)
    cursor = connection.cursor()

    try:
        for statement in _split_sql_script(file_path.read_text(encoding="utf-8")):
            cursor.execute(statement)
        connection.commit()
    except Exception as exc:  # pragma: no cover - benötigt echte Datenbank
        connection.rollback()
        raise RepositoryError(f"SQL-Skript konnte nicht ausgeführt werden: {file_path.name}: {exc}") from exc
    finally:
        cursor.close()
        connection.close()


def initialize_database(config: AppConfig, load_seed: bool = True) -> None:
    schema_path = config.sql_root / "01_schema.sql"
    seed_path = config.sql_root / "02_seed_data.sql"

    _execute_sql_file(config, schema_path)
    if load_seed:
        _execute_sql_file(config, seed_path)
