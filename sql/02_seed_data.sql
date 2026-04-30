USE bbsliothek;

INSERT IGNORE INTO rollen (rollen_id, name, beschreibung) VALUES
    (1, 'Lehrkraft', 'Lehrkräfte verwalten und kommentieren Lernmaterialien.'),
    (2, 'Auszubildende', 'Auszubildende laden Materialien herunter und kommentieren Inhalte.');

INSERT IGNORE INTO benutzer (benutzer_id, rollen_id, anzeigename, email) VALUES
    (1, 1, 'Mia Hoffmann', 'mia.hoffmann@example.org'),
    (2, 1, 'Jonas Becker', 'jonas.becker@example.org'),
    (3, 2, 'Aylin Yilmaz', 'aylin.yilmaz@example.org'),
    (4, 2, 'Luca Schneider', 'luca.schneider@example.org');

INSERT IGNORE INTO themengebiete (themengebiet_id, name, beschreibung) VALUES
    (1, 'Informatik', 'Programmier- und Datenbankthemen'),
    (2, 'Mathematik', 'Rechen- und Statistikmaterialien'),
    (3, 'Pflege', 'Dokumente und Lernhilfen für Pflegeberufe'),
    (4, 'Wirtschaft', 'Materialien zu Organisation und Rechnungswesen');
