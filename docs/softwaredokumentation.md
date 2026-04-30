# Softwaredokumentation

## 1. Zielsetzung

Die Anwendung BBSliothek stellt eine einfache, pruefungstaugliche Lernmaterialverwaltung fuer die Konsole bereit. Sie richtet sich an Lehrkraefte und Auszubildende, die Materialien hochladen, suchen, kommentieren und herunterladen wollen.

## 2. Architektur

Die Anwendung ist in drei Schichten gegliedert:

- `db`: Verbindungsaufbau, SQL-Skripte und Repository fuer MySQL
- `services`: Fachlogik fuer Upload, Download, Kommentarpruefung und Suchlogik
- `ui`: textbasierte Benutzeroberflaeche mit Menues und Tabellenanzeige

Zusaetzliche Module:

- `config.py`: liest Umgebungsvariablen und verwaltet lokale Pfade
- `models.py`: gemeinsame Datenstrukturen
- `exceptions.py`: fachliche und technische Fehlertypen

## 3. Benutzeroberflaeche

Das Hauptmenue enthaelt acht Punkte:

1. Material hochladen oder neue Version anlegen
2. Material suchen
3. Material herunterladen oder oeffnen
4. Kommentare anzeigen
5. Kommentar hinzufuegen
6. Themengebiete verwalten
7. Stammdaten/Testdaten anzeigen
8. Programm beenden

### Upload

- Datei auswaehlen
- Benutzer festlegen
- optional vorhandene Material-ID fuer neue Version angeben
- bei neuem Material zusaetzlich Titel und Themengebiet angeben
- Speicherstrategie wird automatisch berechnet

### Suche

- freie Filtersuche nach Titel/Dateiname, Dateityp, Themengebiet und Autor
- sieben feste Standardabfragen gemaess Vorgabe

### Download

- Auswahl ueber Material-ID
- Export in den Standardordner `downloads/` oder in einen benutzerdefinierten Zielordner
- optionales Oeffnen der exportierten Datei mit dem Standardprogramm des Betriebssystems

### Kommentare

- Anzeige aller Kommentare eines Materials
- Hinzufuegen neuer Kommentare mit Autorzuordnung

## 4. Versionierung

Revisionssicherheit wird innerhalb des Projektrahmens so umgesetzt:

- Ein Material besitzt einen stabilen Stammdatensatz in `materialien`
- Jede neue Datei wird als neuer Datensatz in `material_versionen` gespeichert
- `materialien.aktuelle_version_id` zeigt auf die gerade gueltige Version
- Historische Versionen bleiben erhalten

## 5. Datenfluss

### Upload eines Materials

1. Die Benutzeroberflaeche nimmt Datei, Autor und weitere Eingaben entgegen.
2. Der `MaterialService` validiert Eingaben und berechnet Dateigroesse, Dateityp und SHA-256-Pruefsumme.
3. Der Service waehlt die Speicherstrategie.
4. Grosse Dateien werden in den verwalteten Speicherordner kopiert.
5. Das Repository speichert Material und Version transaktional in MySQL.

### Download eines Materials

1. Das Repository liefert die aktuelle Version.
2. Bei `DB_BLOB` wird die Datei aus der Datenbank in den Zielordner geschrieben.
3. Bei `DATEISYSTEM` wird die Quelldatei aus dem verwalteten Ordner kopiert.

## 6. Fehlerbehandlung

Das Projekt verwendet eigene Fehlertypen, damit Benutzereingaben und technische Stoerungen klar getrennt werden:

- `ValidationError` fuer falsche oder fehlende Eingaben
- `RepositoryError` fuer MySQL- oder Dateisystemprobleme
- `DependencyError` fuer fehlende Python-Abhaengigkeiten

Die Oberflaeche faengt diese Fehler ab und zeigt eine lesbare Meldung in der Konsole an.

## 7. Start und Betrieb

### Datenbank initialisieren

```bash
python3 main.py --init-db
```

### Anwendung starten

```bash
python3 main.py
```

## 8. Testkonzept

Die automatisierten Tests pruefen zentrale Geschaeftslogik ohne echte MySQL-Instanz:

- kleine Datei wird als BLOB behandelt
- grosse Datei wird im Dateisystem gespeichert
- neue Version erhoeht die Versionsnummer
- Download exportiert gespeicherte Inhalte korrekt
- leere Kommentare werden abgewiesen
- Standardabfrage-Katalog enthaelt alle sieben Pflichtabfragen
