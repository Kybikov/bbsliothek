# BBSliothek – Präsentationsskript
### Слайди + що говорити (слово в слово)

---

## Слайд 1 — Titelfolie

**Що показати на слайді:**
- Великий заголовок: **BBSliothek**
- Підзаголовок: *Lernmaterialverwaltung für die BBS*
- Імена команди
- Дата

**Що говорити:**
> „Guten Tag. Wir präsentieren heute unser Projekt: BBSliothek –
> eine Lernmaterialverwaltung, die wir speziell für die BBS entwickelt haben.
> BBSliothek – das ist BBS plus Bibliothek.
> Unser System läuft live auf unserem eigenen Linux-Server
> und ist über eine echte .dev-Domain erreichbar."

---

## Слайд 2 — Das Problem / Die Idee

**Що показати на слайді:**
- Заголовок: „Warum BBSliothek?"
- 3 пункти:
  - 📁 Lernmaterialien liegen überall verteilt (USB, E-Mail, Ordner)
  - 🔍 Keine zentrale Suche, keine Versionierung
  - 💬 Kein Feedback-System für Materialien

**Що говорити:**
> „Das Problem kennen wir alle aus dem Schulalltag:
> Materialien werden per USB-Stick weitergegeben, per E-Mail verschickt
> oder irgendwo auf dem Laufwerk abgelegt.
> Es gibt keine zentrale Stelle, keine Versionskontrolle
> und keinen Weg, Feedback zu einem Material zu geben.
> Genau das wollten wir lösen."

---

## Слайд 3 — Technologie-Stack

**Що показати на слайді:**
- Заголовок: „Womit haben wir es gebaut?"
- Три колонки або іконки:
  - 🐍 **Python** — Programmiersprache
  - 🎨 **Flet** — GUI-Framework
  - 🗄️ **MySQL** — Datenbank

**Що говорити:**
> „Wir haben das Projekt in Python entwickelt.
> Für die Oberfläche nutzen wir Flet – dazu gleich mehr.
> Die Daten werden in einer MySQL-Datenbank gespeichert,
> die auf unserem Linux-Server läuft.
> Die Verbindung zwischen Python und MySQL erfolgt
> über das mysql-connector-python Paket."

---

## Слайд 4 — Warum Flet?

**Що показати на слайді:**
- Заголовок: „Warum Flet?"
- Велика цитата або схема:
  - **1 Code → Desktop + Web + Mobile**
- Список:
  - ✅ Windows / Mac / Linux Desktop-App
  - ✅ Webbrowser (auch vom Handy erreichbar)
  - ✅ In Python geschrieben – keine neue Sprache
  - ✅ Material Design – modernes Aussehen

**Що говорити:**
> „Wir haben Flet gewählt, weil es eine universelle Plattform ist.
> Man schreibt einmal Code – und die App läuft als Desktop-Programm,
> im Webbrowser, und sogar auf dem Handy.
> Das ist der große Vorteil: Mit Flet kann man eine App für alles bauen –
> egal ob es eine Schülerverwaltung, ein Kassensystem oder
> eben unsere BBSliothek ist.
> Wir mussten keine neue Sprache lernen – alles läuft in Python."

---

## Слайд 5 — Datenbankstruktur (ERD)

**Що показати на слайді:**
- Заголовок: „Datenbankstruktur"
- ERD-діаграма (та що ви зробили)
- Або список таблиць:
  - `benutzer` · `rollen` · `materialien`
  - `material_versionen` · `themengebiete` · `kommentare`

**Що говорити:**
> „Die Datenbank besteht aus 6 Tabellen.
> Im Mittelpunkt steht die Tabelle 'materialien'.
> Jedes Material gehört zu einem Themengebiet
> und wurde von einem Benutzer erstellt.
> Dateien unter 1 MB speichern wir direkt in der Datenbank als BLOB.
> Größere Dateien landen im Dateisystem – nur der Pfad wird gespeichert.
> Das nennt sich hybride Speicherstrategie.
> Außerdem unterstützen wir Versionierung:
> jede neue Version einer Datei wird als eigener Eintrag gespeichert."

---

## Слайд 6 — Systemarchitektur

**Що показати на слайді:**
- Схема з трьох шарів:
```
[ Benutzer ]
     ↓
[ Flet GUI (main.py) ]  ←→  [ Konsole (konsole.py) ]
     ↓
[ datenbank.py ]
     ↓
[ MySQL Server ]
```

**Що говорити:**
> „Die Architektur ist klar getrennt.
> Es gibt zwei Interfaces: die grafische Oberfläche mit Flet
> und eine Konsolen-Version – beide nutzen exakt dieselbe datenbank.py.
> Das ist wichtig: die Datenbanklogik ist nur einmal geschrieben.
> Egal ob der Benutzer die GUI oder die Konsole benutzt –
> er ruft dieselben Funktionen auf."

---

## Слайд 7 — Login

**Що показати на слайді:**
- Screenshot der Login-Seite
- Або: Bullet-Points:
  - Benutzername + Passwort
  - Fehlermeldung bei falschen Daten
  - Enter-Taste löst Login aus
  - Zwei Rollen: Lehrkraft / Auszubildende

**Що говорити:**
> „Nach dem Start sieht man die Login-Seite.
> Der Benutzer gibt seinen Benutzernamen und sein Passwort ein.
> Bei falschen Daten erscheint eine Fehlermeldung.
> Es gibt zwei Rollen im System: Lehrkraft und Auszubildende.
> Der Benutzername wird automatisch generiert:
> erster Buchstabe des Vornamens, Punkt, Nachname –
> zum Beispiel m.hoffmann für Mia Hoffmann."

---

## Слайд 8 — Materialien & Suche

**Що показати на слайді:**
- Screenshot der Materialienseite
- Highlights einkreisen:
  - Suchfelder (Titel, Typ, Autor)
  - Tabelle mit Materialien
  - Aktions-Buttons (Download, neue Version, Löschen)

**Що говорити:**
> „Nach dem Login landet man auf der Materialien-Seite.
> Hier sieht man alle Lernmaterialien mit Titel, Dateityp,
> Thema, Autor, Version und Dateigröße.
> Man kann nach Titel, Dateityp und Autor filtern.
> Für jedes Material gibt es drei Aktionen:
> Herunterladen, eine neue Version hochladen, oder Löschen."

---

## Слайд 9 — Upload & Versionierung

**Що показати на слайді:**
- Screenshot der Upload-Seite
- Schema Versionierung:
  - V1 → V2 → V3 (gleiche Material-ID, neue Version)

**Що говорити:**
> „Auf der Upload-Seite kann man eine Datei auswählen,
> einen Titel vergeben und ein Themengebiet zuweisen.
> Das System entscheidet automatisch:
> Dateien unter 1 MB werden als BLOB in der Datenbank gespeichert,
> größere Dateien landen im Dateisystem.
> Besonders wichtig ist die Versionierung:
> wenn zu einem bestehenden Material eine neue Datei hochgeladen wird,
> wird eine neue Version angelegt – die alte bleibt erhalten."

---

## Слайд 10 — Kommentare

**Що показати на слайді:**
- Screenshot der Kommentare-Seite
- Features:
  - Material auswählen
  - Kommentare anzeigen
  - Neuen Kommentar schreiben
  - Bearbeiten & Löschen

**Що говорити:**
> „Auf der Kommentare-Seite kann man zu jedem Material
> Feedback schreiben.
> Man wählt das Material aus, sieht alle vorhandenen Kommentare
> mit Autor und Datum, und kann einen neuen Kommentar verfassen.
> Eigene Kommentare lassen sich bearbeiten und löschen."

---

## Слайд 11 — Standardabfragen

**Що показати на слайді:**
- Screenshot der Abfragen-Seite
- Liste der Abfragen (1-7)
- Beispiel-Ergebnis einer Abfrage

**Що говорити:**
> „Die Standardabfragen-Seite zeigt vorgefertigte SQL-Abfragen.
> Hier sieht man zum Beispiel:
> wie viele Materialien jedes Themengebiet hat,
> welche Autoren wie viele Materialien hochgeladen haben,
> oder die durchschnittliche Dateigröße je Thema.
> Diese Abfragen demonstrieren JOINs und Aggregationen
> direkt in der Anwendung."

---

## Слайд 12 — Konsolen-Interface

**Що показати на слайді:**
- Screenshot des Konsolenprogramms
- Menü-Optionen sichtbar

**Що говорити:**
> „Parallel zur grafischen Oberfläche gibt es auch
> eine vollständige Konsolen-Version.
> Sie bietet dieselben Funktionen: Login, Materialien,
> Upload, Download, Kommentare und Themen.
> Das zeigt die saubere Trennung unserer Architektur:
> die Datenbanklogik funktioniert unabhängig vom Interface."

---

## Слайд 13 — Deployment: Linux-Server & .dev-Domain

**Що показати на слайді:**
- Schema або Bild:
```
Internet
   ↓
bbsliothek.dev
   ↓
Linux-Server (Port 3000)
   ↓
Flet Web-App
   ↓
MySQL Datenbank
```
- URL groß anzeigen: **bbsliothek.dev**

**Що говорити:**
> „Das Besondere an unserem Projekt: es läuft nicht nur lokal.
> Wir haben die App auf unserem eigenen Linux-Server deployed
> und eine echte .dev-Domain registriert.
> Flet hat einen integrierten Web-Modus:
> mit dem Parameter --web startet die App als Webserver.
> Jeder kann die BBSliothek jetzt über den Browser aufrufen –
> vom PC, vom Tablet, vom Handy.
> Sie können das gleich live ausprobieren."

---

## Слайд 14 — Live-Demo

**Що показати на слайді:**
- Nur der Link groß: **bbsliothek.dev**
- Oder QR-Code zur Domain

**Що говорити:**
> „Und jetzt zeigen wir das Ganze live.
> Wir öffnen bbsliothek.dev im Browser.
> [Login: m.hoffmann / lehrer123]
> Sie sehen: Login-Seite, Materialien, Upload, Kommentare.
> Das läuft alles auf unserem Linux-Server,
> live, in Echtzeit, mit echter Datenbank."

*(Тут просто демонструєте живу систему в браузері)*

---

## Слайд 15 — Was haben wir gelernt?

**Що показати на слайді:**
- Заголовок: „Was haben wir gelernt?"
- 5-6 Punkte:
  - ✅ Python + MySQL Anbindung
  - ✅ GUI-Entwicklung mit Flet
  - ✅ Datenbankdesign (ERD, Normalisierung)
  - ✅ SQL: JOINs, Aggregationen, Views
  - ✅ Linux-Server, Deployment, Domain
  - ✅ Versionsverwaltung mit Git

**Що говорити:**
> „In diesem Projekt haben wir sehr viel gelernt.
> Angefangen bei der Datenbankplanung mit ERD und Normalisierung,
> über SQL mit JOINs und Aggregationen,
> bis hin zur kompletten Anwendungsentwicklung in Python.
> Besonders wichtig war für uns das Deployment:
> wir haben einen echten Linux-Server aufgesetzt,
> eine Domain konfiguriert und die App live geschaltet.
> Das ist etwas, das wir so vorher noch nie gemacht haben."

---

## Слайд 16 — Danke / Fragen

**Що показати на слайді:**
- Großes: **Danke für Ihre Aufmerksamkeit!**
- Link: bbsliothek.dev
- Team-Namen
- Optional: QR-Code

**Що говорити:**
> „Das war unsere Präsentation der BBSliothek.
> Vielen Dank für Ihre Aufmerksamkeit.
> Haben Sie Fragen?"

---

## Порядок слайдів (підсумок)

| # | Слайд | Хто говорить |
|---|---|---|
| 1 | Titelfolie | Alle |
| 2 | Problem / Idee | Person 1 |
| 3 | Technologie-Stack | Person 1 |
| 4 | Warum Flet? | Person 1 |
| 5 | Datenbankstruktur (ERD) | Person 2 |
| 6 | Systemarchitektur | Person 2 |
| 7 | Login | Person 2 |
| 8 | Materialien & Suche | Person 3 |
| 9 | Upload & Versionierung | Person 3 |
| 10 | Kommentare | Person 3 |
| 11 | Standardabfragen | Person 1 |
| 12 | Konsolen-Interface | Person 2 |
| 13 | Deployment & Domain | Person 3 |
| 14 | Live-Demo | Alle |
| 15 | Was haben wir gelernt? | Alle |
| 16 | Danke / Fragen | Alle |

**Загальний час:** ~15-20 хвилин з демо
