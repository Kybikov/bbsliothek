from __future__ import annotations

import argparse
import sys

from bbsliothek.config import AppConfig
from bbsliothek.db.bootstrap import initialize_database
from bbsliothek.db.repository import MySQLRepository
from bbsliothek.exceptions import AppError
from bbsliothek.services.material_service import MaterialService
from bbsliothek.services.query_service import QueryService
from bbsliothek.ui.console import ConsoleApp


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="BBSliothek - Lernmaterialverwaltung")
    parser.add_argument(
        "--init-db",
        action="store_true",
        help="Initialisiert die MySQL-Datenbank anhand der SQL-Skripte.",
    )
    parser.add_argument(
        "--skip-seed",
        action="store_true",
        help="Legt nur das Schema an, aber keine Seed-Daten.",
    )
    parser.add_argument(
        "--no-ui",
        action="store_true",
        help="Beendet das Programm nach der optionalen Datenbankinitialisierung.",
    )
    return parser.parse_args()


def build_console_app(config: AppConfig) -> ConsoleApp:
    repository = MySQLRepository(config)
    material_service = MaterialService(repository, config)
    query_service = QueryService(repository)
    return ConsoleApp(material_service, query_service, config)


def main() -> int:
    args = parse_args()
    config = AppConfig.from_env()
    config.ensure_directories()

    try:
        if args.init_db:
            initialize_database(config, load_seed=not args.skip_seed)
            print("Datenbank wurde erfolgreich initialisiert.")

        if args.no_ui:
            return 0

        app = build_console_app(config)
        app.run()
        return 0
    except AppError as exc:
        print(f"Fehler: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nProgramm wurde durch den Benutzer beendet.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
