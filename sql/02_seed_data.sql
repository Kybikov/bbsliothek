USE bbsliothek;

INSERT INTO rollen (rollen_id, name, beschreibung) VALUES
    (1, 'Lehrkraft',     'Lehrkräfte verwalten und kommentieren Lernmaterialien.'),
    (2, 'Auszubildende', 'Auszubildende laden Materialien herunter und kommentieren Inhalte.');

-- Passwörter werden als Klartext gespeichert (Schulprojekt)
INSERT INTO benutzer (benutzer_id, rollen_id, anzeigename, email, passwort) VALUES
    (1, 1, 'Mia Hoffmann',   'mia.hoffmann@example.org',   'lehrer123'),
    (2, 1, 'Jonas Becker',   'jonas.becker@example.org',   'lehrer123'),
    (3, 2, 'Aylin Yilmaz',   'aylin.yilmaz@example.org',   'azubi123'),
    (4, 2, 'Luca Schneider', 'luca.schneider@example.org', 'azubi123');

INSERT INTO themengebiete (themengebiet_id, name, beschreibung) VALUES
    (1, 'Informatik',  'Programmier- und Datenbankthemen'),
    (2, 'Mathematik',  'Rechen- und Statistikmaterialien'),
    (3, 'Pflege',      'Dokumente und Lernhilfen für Pflegeberufe'),
    (4, 'Wirtschaft',  'Materialien zu Organisation und Rechnungswesen'),
    (5, 'Sonstiges',   'Andere Materialien');

-- Materialien ohne aktuelle_version_id anlegen (wird danach gesetzt)
INSERT INTO materialien (material_id, titel, themengebiet_id, erstellt_von, aktuelle_version_id) VALUES
    (1, 'Python Einführung',     1, 1, NULL),
    (2, 'Mathe Grundlagen',      2, 2, NULL),
    (3, 'Datenbanken Skript',    1, 1, NULL),
    (4, 'Erste Hilfe Leitfaden', 3, 2, NULL);

-- Versionen anlegen
-- Kleine Dateien (unter 1 MB) werden als BLOB direkt in der Datenbank gespeichert
-- Große Dateien werden nur als Pfad gespeichert
INSERT INTO material_versionen (version_id, material_id, versionsnummer, dateiname, dateityp, dateigroesse_bytes, speicherstrategie, blob_inhalt, dateipfad, erstellt_von) VALUES
    (1, 1, 1, 'python_einfuehrung.py',   '.py',  512,     'DB_BLOB',    'print("Hallo Welt!")\nname = input("Dein Name: ")\nprint("Hallo " + name)', NULL, 1),
    (2, 2, 1, 'mathe_grundlagen.txt',    '.txt', 256,     'DB_BLOB',    'Grundlagen der Mathematik\n1. Addition\n2. Subtraktion\n3. Multiplikation', NULL, 2),
    (3, 3, 1, 'datenbanken_skript.pdf',  '.pdf', 3200000, 'DATEISYSTEM', NULL, 'storage/materials/datenbanken_skript.pdf', 1),
    (4, 4, 1, 'erste_hilfe.pdf',         '.pdf', 1500000, 'DATEISYSTEM', NULL, 'storage/materials/erste_hilfe.pdf', 2);

-- Zeiger auf aktuelle Version setzen
UPDATE materialien SET aktuelle_version_id = 1 WHERE material_id = 1;
UPDATE materialien SET aktuelle_version_id = 2 WHERE material_id = 2;
UPDATE materialien SET aktuelle_version_id = 3 WHERE material_id = 3;
UPDATE materialien SET aktuelle_version_id = 4 WHERE material_id = 4;

-- Kommentare
INSERT INTO kommentare (material_id, autor_id, kommentartext) VALUES
    (1, 3, 'Sehr hilfreich für den Einstieg, danke!'),
    (1, 4, 'Kann man noch mehr Beispiele hinzufügen?'),
    (2, 3, 'Die Erklärungen sind gut verständlich.'),
    (3, 4, 'Wann gibt es eine aktualisierte Version?');
