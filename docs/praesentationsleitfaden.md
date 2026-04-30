# Praesentationsleitfaden

## Ziel

Die Praesentation soll in 10 bis 15 Minuten zeigen, dass die Anforderungen des Arbeitsauftrags fachlich verstanden und technisch sauber umgesetzt wurden.

## Empfohlener Ablauf

### 1. Ausgangsproblem und Zielsetzung

- Unstrukturierte Dateiablage war fehleranfaellig
- BBSliothek loest Suche, Versionierung und Kommentierung zentral
- MySQL und Python-Konsole wurden gemaess Vorgabe verwendet

### 2. Datenmodell

- ERM und finales ERD kurz vorstellen
- wichtige Entitaeten nennen: Benutzer, Rollen, Themengebiete, Materialien, Versionen, Kommentare
- erklaeren, warum `material_versionen` fuer Revisionssicherheit notwendig ist

### 3. Kernfunktionen live zeigen

- Upload eines neuen Materials
- Anzeige der automatischen Speicherstrategie
- Suche ueber freie Filter
- mindestens eine Standardabfrage ausfuehren
- Kommentar hinzufuegen
- Material herunterladen

### 4. Reflexion des Arbeitsprozesses

- Anforderungen analysiert und in Tabellen ueberfuehrt
- Datenmodell normalisiert
- SQL-Schema erstellt
- Python-Anwendung schrittweise implementiert und getestet

### 5. Abschluss

- wichtigste Projektergebnisse zusammenfassen
- kurz auf moegliche Erweiterungen hinweisen, zum Beispiel Benutzeranmeldung oder Weboberflaeche
