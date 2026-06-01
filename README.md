# BBSliothek – Lernmaterialverwaltung

Abschlussprojekt für Lernfeld 8 „Daten systemübergreifend bereitstellen" – BBS Verden.

Eine Python-Anwendung zur digitalen Verwaltung von Lernmaterialien für Lehrkräfte und Auszubildende. Die Daten werden in einer **MySQL**-Datenbank gespeichert.

---

## Projektbeschreibung

Derzeit werden Lernmaterialien unstrukturiert in verschiedenen Verzeichnissen abgelegt oder manuell weitergegeben. Das führt zu Problemen bei der Suche, Versionierung und Aktualisierung.

BBSliothek löst dieses Problem durch eine datenbankgestützte Anwendung, mit der Materialien systematisch gespeichert, durchsucht, kommentiert und revisionssicher abgelegt werden können.

---

## Zielsetzung

- Lernmaterialien (PDF, DOCX, Bilder, Python-Dateien usw.) hochladen und verwalten
- Dateien unter 1 MB direkt als BLOB in der Datenbank speichern, größere Dateien im Dateisystem ablegen
- Materialien suchen, filtern und herunterladen
- Kommentare zu Materialien hinterlassen
- Versionierung: jeder neue Upload erstellt eine neue Version des Materials
- 7 vordefinierte Standardabfragen (Aggregationen, Joins)

---

## Funktionsübersicht

| Funktion | Beschreibung |
|---|---|
| Login | Anmeldung mit Benutzername und Passwort |
| Material hochladen | Datei hochladen, Titel und Themengebiet angeben |
| Neue Version hochladen | Bestehende Material-ID angeben, neue Version wird angelegt |
| Materialien suchen | Freie Suche nach Titel, Dateityp, Thema oder Autor |
| 7 Standardabfragen | Aggregationen und Joins direkt ausführen |
| Material herunterladen | Datei in den downloads/-Ordner exportieren |
| Kommentare | Kommentare zu einem Material anzeigen und hinzufügen |
| Themengebiete | Themengebiete anzeigen und neu anlegen |
| Benutzerverwaltung | Alle Benutzer mit Rolle anzeigen |

### 7 Standardabfragen

| Nr. | Titel | Typ |
|---|---|---|
| 1 | Materialien pro Themengebiet | Aggregation |
| 2 | Durchschnittliche Dateigröße je Thema | Aggregation |
| 3 | Materialien mit Autoren | Inner Join |
| 4 | Kommentare mit Material und Autor | Inner Join |
| 5 | Materialien pro Autor mit Rolle | Join + Aggregation |
| 6 | Materialien mit Thema und Version | 2× Inner Join |
| 7 | Vollständige Übersicht | Mehrere Joins |

---

## Projektstruktur

```
konsole.py        Textbasierte Konsolen-Anwendung (Hauptabgabe)
main.py           Grafische Oberfläche mit Flet (Bonus)
datenbank.py      MySQL-Verbindung und alle Datenbankfunktionen
requirements.txt  Python-Abhängigkeiten
.env              Datenbankverbindung (nicht im Repository)
sql/
  01_schema.sql        Tabellen, Views, Constraints
  02_seed_data.sql     Beispieldaten
  03_standardabfragen.sql  Die 7 Abfragen als separate SQL-Datei
storage/materials/   Ablage großer Dateien (> 1 MB)
downloads/           Standardziel beim Herunterladen
docs/                Technische Dokumentation
build/windows_exe2/
  BBSliothek.exe     Fertige Windows-EXE (Flet GUI)
```

---

## Datenbankschema

| Tabelle | Beschreibung |
|---|---|
| `rollen` | Lehrkraft / Auszubildender |
| `benutzer` | Benutzerkonten mit Rolle und Passwort |
| `themengebiete` | Informatik, Mathematik, Pflege … |
| `materialien` | Haupttabelle, verweist auf aktuelle Version |
| `material_versionen` | Jede hochgeladene Datei als eigene Version |
| `kommentare` | Kommentare zu einem Material |

Die View `vw_material_aktuell` verknüpft alle Tabellen und liefert die aktuelle Version jedes Materials in einer Zeile.

---

## Voraussetzungen

- Python 3.11 oder neuer
- MySQL 8.x
- Pakete aus `requirements.txt`

---

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

---

## Datenbank einrichten

Schema und Beispieldaten in MySQL einspielen:

```bash
mysql -u root -p < sql/01_schema.sql
mysql -u root -p bbsliothek < sql/02_seed_data.sql
```

---

## Konfiguration

Datei `.env` im Projektordner anlegen:

```
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=bbsliothek
DB_USER=root
DB_PASSWORD=
STORAGE_ROOT=storage/materials
DOWNLOAD_ROOT=downloads
```

---

## Anwendung starten

```bash
# Konsolen-Anwendung (textbasiert)
python konsole.py

# Grafische Oberfläche (Flet)
python main.py

# Grafische Oberfläche im Browser
python main.py --web
```

### Testbenutzer

| Name | Passwort | Rolle |
|---|---|---|
| Mia Hoffmann | lehrer123 | Lehrkraft |
| Jonas Becker | lehrer123 | Lehrkraft |
| Aylin Yilmaz | azubi123 | Auszubildende |
| Luca Schneider | azubi123 | Auszubildende |

---

## Windows EXE erstellen

Die fertige EXE liegt bereits unter `build/windows_exe2/BBSliothek.exe`.

Um sie neu zu erstellen:

```bash
pip install pyinstaller
flet pack main.py -n "BBSliothek" --distpath build\windows_exe2 -y
```

> **Hinweis:** Nach dem ersten Build muss `BBSliothek.spec` manuell bearbeitet werden um die MySQL-DLLs einzubinden (siehe Abschnitt „Bekannte Fehler").

---

## Implementierungsdetails

**Speicherstrategie:**
In `datenbank.py` wird beim Upload geprüft ob die Datei kleiner als 1 MB ist. Kleine Dateien werden als BLOB direkt in die Datenbank gespeichert, größere Dateien werden in `storage/materials/` abgelegt und nur der Pfad wird in der Datenbank gespeichert.

> Hinweis: In der aktuellen Version von `datenbank.py` werden alle Dateien im Dateisystem gespeichert (Strategie `DATEISYSTEM`). Die BLOB-Strategie ist in der Konsolen-Version implementiert aber in `datenbank.py` deaktiviert, da es beim Testen zu `max_allowed_packet`-Fehlern kam.

**Versionierung:**
Beim Upload wird immer eine neue Zeile in `material_versionen` angelegt. Die Tabelle `materialien` hat einen Fremdschlüssel `aktuelle_version_id` der immer auf die neueste Version zeigt.

**Login:**
Das Passwort wird als Klartext in der Datenbank gespeichert und verglichen. Für ein Schulprojekt ausreichend, in der Praxis würde man einen Hash verwenden.

---

## Bekannte Fehler die beim Entwickeln aufgetreten sind

- **`AttributeError: module 'flet.controls.padding' has no attribute 'only'`** –
  In der Flet-Dokumentation und vielen Tutorials wird `ft.padding.only(top=8)` verwendet.
  In der installierten Version (≥ 0.24) existiert `ft.padding.only` jedoch nicht mehr als
  Funktion. Die Lösung war `ft.Padding(top=8, left=0, right=0, bottom=0)` zu verwenden.
  Der Fehler trat an 6 Stellen im Code auf und war schwer zu finden, weil die App
  gestartet wurde aber nur ein leeres Fenster mit Fehlermeldung zeigte.

- **`AttributeError: module 'flet.controls.border' has no attribute 'all'`** –
  Ähnlich wie das Padding-Problem: `ft.border.all(1, "#dee2e6")` wird in der Flet-Doku
  so verwendet, existiert aber in Version ≥ 0.80 nicht mehr.
  Lösung: alle vier Seiten einzeln mit `ft.Border(top=ft.BorderSide(...), ...)` angeben.

- **`TypeError: run() missing 1 required positional argument`** –
  In alten Flet-Tutorials steht `ft.app(target=main)`. Ab Version 0.80 wurde das durch
  `ft.run(main)` ersetzt. Erst kam eine DeprecationWarning, nach der Änderung auf
  `ft.run(target=main)` kam ein TypeError. Die korrekte Schreibweise ist `ft.run(main)`.

- **FilePicker funktioniert nicht in Flet 0.80+** –
  `ft.FilePicker` hat sich stark verändert. Nach mehreren Versuchen wurde als Lösung
  ein einfaches Textfeld für die Pfadeingabe verwendet.

- **`DeprecationWarning: ElevatedButton is deprecated since version 0.80.0`** –
  `ft.ElevatedButton` wurde durch `ft.FilledButton` ersetzt.

- **`AttributeError: 'Page' object has no attribute 'window_width'`** –
  Ab Version 0.80 wurde `page.window_width` zu `page.window.width`.

- **`mysql.connector.errors.InterfaceError`** – Cursor nicht geschlossen bevor eine neue
  Abfrage gestartet wurde. Behoben durch `cursor.close()` und `conn.close()` am Ende
  jeder Funktion in einem `finally`-Block.

- **MySQL Fehler 150 (Foreign Key) beim Anlegen der Tabellen** – Der zyklische
  Fremdschlüssel zwischen `materialien.aktuelle_version_id` und
  `material_versionen.material_id` konnte nicht direkt angelegt werden.
  Lösung: Fremdschlüssel nachträglich per `ALTER TABLE` hinzufügen.

- **`max_allowed_packet` Fehler beim BLOB-Upload** – MySQL erlaubt standardmäßig
  nur 1 MB für Pakete. Bei größeren Dateien kam der Fehler. In `my.ini` auf `64M` erhöht.
  Danach wurde entschieden, alle Dateien im Dateisystem zu speichern.

- **`UnicodeDecodeError` beim Lesen von Dateien** – Beim ersten Versuch wurde die
  Datei mit `open(pfad, "r")` geöffnet. Für Binärdateien muss `open(pfad, "rb")` verwendet werden.

- **`os.startfile()` existiert nur unter Windows** – Auf Linux/Mac muss
  `subprocess.run(["xdg-open", pfad])` verwendet werden.

- **EXE startet aber zeigt Fehler `mysql_native_password cannot be loaded`** –
  PyInstaller hat die DLL-Dateien des MySQL-Connectors nicht automatisch eingebunden.
  Die Dateien in `mysql/vendor/plugin/` (z.B. `mysql_native_password.dll`) müssen
  manuell über den `binaries`-Parameter in der `.spec`-Datei hinzugefügt werden.

---

## Dokumentation

- [Technische Dokumentation](docs/technische_dokumentation.md)
- [Softwaredokumentation](docs/softwaredokumentation.md)
- [Präsentationsleitfaden](docs/praesentationsleitfaden.md)
