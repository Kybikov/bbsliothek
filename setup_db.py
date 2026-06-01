# setup_db.py - Datenbank einmalig initialisieren
# Aufruf: python setup_db.py
# Achtung: loescht alle vorhandenen Tabellen und legt sie neu an!

import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST     = os.getenv("DB_HOST",     "127.0.0.1")
DB_PORT     = int(os.getenv("DB_PORT", "3306"))
DB_NAME     = os.getenv("DB_NAME",     "bbsliothek")
DB_USER     = os.getenv("DB_USER",     "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

SQL_DATEIEN = [
    "sql/01_schema.sql",
    "sql/02_seed_data.sql",
]


def sql_ausfuehren(cursor, sql_text):
    # Mehrere SQL-Anweisungen nacheinander ausführen
    # multi=True ist nötig weil die Dateien mehrere Statements enthalten
    ergebnisse = cursor.execute(sql_text, multi=True)
    for ergebnis in ergebnisse:
        if ergebnis.with_rows:
            ergebnis.fetchall()


def main():
    print("BBSliothek - Datenbankinitialisierung")
    print("=" * 40)

    try:
        # Zuerst ohne Datenbank verbinden um CREATE DATABASE ausführen zu können
        print(f"Verbinde mit {DB_HOST}:{DB_PORT} als {DB_USER} ...")
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
        )
        cursor = conn.cursor()
        print("Verbindung erfolgreich.")

        for datei in SQL_DATEIEN:
            print(f"\nFühre {datei} aus ...")
            with open(datei, "r", encoding="utf-8") as f:
                inhalt = f.read()

            sql_ausfuehren(cursor, inhalt)
            conn.commit()
            print(f"{datei} erfolgreich ausgefuehrt.")

        cursor.close()
        conn.close()

        print("\n" + "=" * 40)
        print("Datenbank erfolgreich initialisiert!")
        print(f"Datenbank: {DB_NAME}")
        print("Testbenutzer:")
        print("  Mia Hoffmann   / lehrer123  (Lehrkraft)")
        print("  Jonas Becker   / lehrer123  (Lehrkraft)")
        print("  Aylin Yilmaz   / azubi123   (Auszubildende)")
        print("  Luca Schneider / azubi123   (Auszubildende)")

    except Error as e:
        print(f"\nFehler: {e}")
        print("\nMoegliche Ursachen:")
        print("  - Datenbankverbindung fehlgeschlagen (Host/Port/Passwort pruefen)")
        print("  - Benutzer hat keine CREATE DATABASE Berechtigung")
        print("  - .env Datei fehlt oder Variablen nicht gesetzt")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
