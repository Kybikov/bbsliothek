# BBSliothek – Lernmaterialverwaltung

Abschlussprojekt für Lernfeld 8 „Daten systemübergreifend bereitstellen".

Eine Python-Desktop-Anwendung zur digitalen Verwaltung von Lernmaterialien
für Lehrkräfte und Auszubildende. Die Oberfläche wurde mit **Flet** gebaut
(Flutter-basiertes Python-UI-Framework), die Daten liegen in einer **MySQL**-Datenbank.

## Was die Anwendung kann

- **Materialien hochladen** – kleine Dateien (< 1 MB) werden als BLOB direkt in der
  Datenbank gespeichert, größere Dateien werden im Dateisystem abgelegt und nur per
  Pfad referenziert
- **Suchen & Herunterladen** – Freitextsuche nach Titel und Dateityp, Datei öffnet sich
  nach dem Download automatisch
- **7 Standardabfragen** – direkt in der App ausführbar:
  1. Materialien pro Themengebiet (Aggregation)
  2. Durchschnittliche Dateigröße je Thema (Aggregation)
  3. Materialien mit Autoren (Inner Join)
  4. Kommentare mit Material und Autor (Inner Join)
  5. Materialien pro Autor (Join + Aggregation)
  6. Materialien mit Thema und Version (2× Inner Join)
  7. Vollständige Übersicht (mehrere Joins)
- **Kommentare** zu jedem Material hinzufügen und anzeigen
- **Themengebiete** verwalten (anlegen, auflisten)
- **Versionierung** – beim erneuten Upload derselben Material-ID wird eine neue
  Version angelegt

## Projektstruktur

```
main.py           Flet-Anwendung (komplette UI)
datenbank.py      MySQL-Verbindung und alle Datenbankfunktionen
requirements.txt  Python-Abhängigkeiten
sql/
  01_schema.sql   Tabellen, Views, Constraints
  02_seed_data.sql Beispieldaten
  03_standardabfragen.sql  Die 7 Abfragen als separate SQL-Datei
storage/materials/  Ablage großer Dateien (> 1 MB)
downloads/          Standardziel beim Herunterladen
docs/               Technische Dokumentation und Softwaredokumentation
```

## Datenbankschema (Kurzübersicht)

| Tabelle              | Beschreibung                                      |
|----------------------|---------------------------------------------------|
| `rollen`             | Lehrkraft / Auszubildender                        |
| `benutzer`           | Benutzerkonten mit Rolle                          |
| `themengebiete`      | Informatik, Mathematik, Pflege …                  |
| `materialien`        | Haupttabelle, verweist auf aktuelle Version       |
| `material_versionen` | Jede hochgeladene Datei als eigene Version        |
| `kommentare`         | Kommentare zu einem Material                      |

Die View `vw_material_aktuell` verknüpft alle Tabellen und liefert die aktuelle
Version jedes Materials in einer Zeile.

## Voraussetzungen

- Python 3.11 oder neuer
- MySQL 8.x
- Pakete aus `requirements.txt`

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

## Datenbank einrichten

Schema und Beispieldaten in MySQL einspielen:

```bash
mysql -u root -p < sql/01_schema.sql
mysql -u root -p bbsliothek < sql/02_seed_data.sql
```

## Konfiguration

Datenbankverbindung über Umgebungsvariablen (Standardwerte stehen in `datenbank.py`):

```
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=bbsliothek
DB_USER=root
DB_PASSWORD=
STORAGE_ROOT=storage/materials
DOWNLOAD_ROOT=downloads
```

## Anwendung starten

```bash
# Desktop-Modus (Standard)
python main.py

# Browser-Modus (auch vom Handy erreichbar)
python main.py --web
# Dann im Browser: http://localhost:8550
# Im lokalen Netzwerk (Handy): http://<IP-Adresse>:8550
```

### Testbenutzer (nach Seed-Daten)

| Name | Passwort | Rolle |
|---|---|---|
| Mia Hoffmann | lehrer123 | Lehrkraft |
| Jonas Becker | lehrer123 | Lehrkraft |
| Aylin Yilmaz | azubi123 | Auszubildende |
| Luca Schneider | azubi123 | Auszubildende |

## Funktionsumfang (aktuell)

- Login mit Benutzername und Passwort
- Lernmaterialien hochladen (Pfad eingeben oder Datei auswählen)
- Alle Dateien werden im Dateisystem gespeichert (`storage/materials/`)
- Versionierung: jeder Upload erstellt eine neue Version
- 7 Standardabfragen (Aggregation, Joins, mehrere Tabellen)
- Kommentare hinzufügen, bearbeiten (Dialog), löschen
- Filterbarer Materialien-Überblick (Titel, Typ, Autor)
- Benutzerverwaltung mit E-Mail-Validierung
- Themengebiete anlegen und anzeigen
- Cross-platform: Desktop (Windows/macOS/Linux) und Browser (`--web`)

## Bekannte Fehler die beim Entwickeln aufgetreten sind

> Diese Fehler sind beim Entwickeln tatsächlich aufgetreten und wurden im Laufe des Projekts behoben.

- **`AttributeError: module 'flet.controls.padding' has no attribute 'only'`** –
  In der Flet-Dokumentation und vielen Tutorials wird `ft.padding.only(top=8)` verwendet.
  In der installierten Version (≥ 0.24) existiert `ft.padding.only` jedoch nicht mehr als
  Funktion. Die Lösung war `ft.Padding(top=8, left=0, right=0, bottom=0)` zu verwenden.
  Gleiches gilt für `ft.padding.symmetric(vertical=8)` →
  `ft.Padding(top=8, left=0, right=0, bottom=8)`.
  Der Fehler trat an 6 Stellen im Code auf und war schwer zu finden, weil die App
  gestartet wurde aber nur ein leeres Fenster mit Fehlermeldung zeigte.

- **`AttributeError: module 'flet.controls.border' has no attribute 'all'`** –
  Ähnlich wie das Padding-Problem: `ft.border.all(1, "#dee2e6")` wird in der Flet-Doku
  und vielen Beispielen so verwendet, existiert aber in Version ≥ 0.80 nicht mehr.
  Lösung: alle vier Seiten einzeln mit `ft.Border(top=ft.BorderSide(...), bottom=..., left=..., right=...)` angeben.
  Trat an 4 Stellen auf.

- **`DeprecationWarning` + `TypeError: run() missing 1 required positional argument`** –
  In alten Flet-Tutorials steht `ft.app(target=main)`. Ab Version 0.80 wurde `ft.app()`
  durch `ft.run()` ersetzt — aber `target=` als Keyword-Argument existiert nicht mehr.
  Erst kam die DeprecationWarning (`ft.app` veraltet), nach der Änderung auf `ft.run(target=main)`
  kam ein TypeError. Die korrekte Schreibweise ist `ft.run(main)` ohne Keyword.

- **FilePicker — 5 Versuche bis zur Lösung:**
  1. `ft.FilePicker(on_result=handler)` im Konstruktor → `TypeError`
  2. `file_picker.on_result = handler` + `page.overlay.append()` beim Upload → `Unknown control`
  3. `page.overlay.append()` einmalig beim App-Start → `Unknown control` schon beim Login
  4. Temporär durch `TextField` für Pfadeingabe ersetzt (funktioniert, aber kein Dateidialog)
  5. Richtige Lösung gefunden (flet.app/gallery): FilePicker ist in 0.80 `async`:
  ```python
  async def datei_auswaehlen(e):
      picker = ft.FilePicker()           # kein page.overlay!
      files = await picker.pick_files()  # async/await
      if files and files[0].path:
          pfad_feld.value = files[0].path
  ```
  Im Browser-Modus ist `files[0].path` immer `None` (Browser-Sicherheitsbeschränkung)
  → Benutzer gibt den Pfad dort manuell ein.

- **`DeprecationWarning: ElevatedButton is deprecated since version 0.80.0`** –
  `ft.ElevatedButton` wurde durch `ft.FilledButton` ersetzt.
  Die App lief noch, aber in der Konsole erschienen viele Warnungen.
  Alle `ElevatedButton` wurden durch `FilledButton` ersetzt.

- **`AttributeError: 'Page' object has no attribute 'window_width'`** –
  In alten Flet-Tutorials wird `page.window_width = 1200` gesetzt.
  Ab Version 0.80 wurde das Fenster-Objekt ausgelagert:
  `page.window_width` → `page.window.width`, `page.window_height` → `page.window.height`.

- `mysql.connector.errors.InterfaceError` – Cursor nicht geschlossen bevor eine neue
  Abfrage gestartet wurde; behoben durch `finally: cur.close(); conn.close()`
- MySQL `errno 150` (Foreign Key) beim Anlegen der Tabellen – der zyklische Fremdschlüssel
  zwischen `materialien.aktuelle_version_id` und `material_versionen.material_id` musste
  nachträglich per `ALTER TABLE` hinzugefügt werden
- `max_allowed_packet` Fehler beim Upload großer BLOBs – in `my.ini` auf `64M` erhöht
- `UnicodeDecodeError` beim Lesen binärer Dateien – Datei muss mit `open(pfad, "rb")`
  geöffnet werden
- `os.startfile()` existiert nur unter Windows – auf Linux/Mac muss `subprocess.run(["xdg-open", pfad])` verwendet werden

## Dokumentation

- [Technische Dokumentation](docs/technische_dokumentation.md)
- [Softwaredokumentation](docs/softwaredokumentation.md)
- [Präsentationsleitfaden](docs/praesentationsleitfaden.md)
