# BBSliothek

BBSliothek ist eine textbasierte Python-Anwendung zur Verwaltung von Lernmaterialien in einer MySQL-Datenbank. Das Projekt setzt die Abschlussaufgabe aus Lernfeld 8 um und unterstützt Upload, Suche, Download, Kommentare, Themengebiete und versionierte Ablage von Materialien.

## Funktionsumfang

- Lernmaterialien hochladen und versionieren
- Automatische Speicherstrategie:
  - Dateien kleiner als `1_000_000` Byte werden als BLOB in MySQL gespeichert
  - größere Dateien werden im Dateisystem abgelegt und per Pfad referenziert
- Sieben feste Standardabfragen gemäß Aufgabenstellung
- Freie Filtersuche nach Titel, Dateityp, Themengebiet und Autor
- Kommentare zu Materialien
- Verwaltung von Themengebieten
- Textbasierte Menüoberfläche für die Konsole

## Projektstruktur

- `main.py`: Programmeinstieg
- `bbsliothek/`: Python-Paket mit Konfiguration, Datenzugriff, Services und UI
- `sql/`: MySQL-Schema, Seed-Daten und Standardabfragen
- `docs/`: technische und softwarebezogene Dokumentation
- `tests/`: Unit-Tests für zentrale Geschäftslogik
- `storage/materials/`: Ablage großer Dateien
- `downloads/`: Standardziel für Exporte
- `downloads/`: Standardziel für Exporte
- `downloads/`: Standardziel für Exporte
- `downloads/`: Standardziel für Exporte


## Voraussetzungen

- Python 3.12 oder neuer
- MySQL 8.x
- Paket `mysql-connector-python`

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Konfiguration

Die Anwendung liest ihre Konfiguration aus Umgebungsvariablen.

```bash
export BBSLIOTHEK_DB_HOST=127.0.0.1
export BBSLIOTHEK_DB_PORT=3306
export BBSLIOTHEK_DB_NAME=bbsliothek
export BBSLIOTHEK_DB_USER=root
export BBSLIOTHEK_DB_PASSWORD=secret
export BBSLIOTHEK_STORAGE_ROOT=/absolute/path/to/storage/materials
export BBSLIOTHEK_DOWNLOAD_ROOT=/absolute/path/to/downloads
```

Ohne gesetzte Pfade werden lokale Standardordner im Projekt verwendet.

## Datenbank einrichten

```bash
python3 main.py --init-db
```

Mit `--skip-seed` wird nur das Schema angelegt.

## Anwendung starten

```bash
python3 main.py
```

## Dokumentation

- [Technische Dokumentation](docs/technische_dokumentation.md)
- [Softwaredokumentation](docs/softwaredokumentation.md)
- [Präsentationsleitfaden](docs/praesentationsleitfaden.md)

## Tests

```bash
python3 -m unittest discover -s tests
```
