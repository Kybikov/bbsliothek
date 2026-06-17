USE bbsliothek;

INSERT INTO rollen (name, beschreibung)
VALUES
    ('Auszubildende', 'Auszubildende laden Materialien herunter und kommentieren Inhalte.')
ON DUPLICATE KEY UPDATE
    beschreibung = VALUES(beschreibung);

SET @azubi_rolle = (
    SELECT rollen_id
    FROM rollen
    WHERE name = 'Auszubildende'
    LIMIT 1
);

-- Passwort fuer alle Praesentationszugänge: azubi123
INSERT INTO benutzer (rollen_id, username, vorname, nachname, email, passwort) VALUES
    (@azubi_rolle, 'a.ergeson.nitonde', 'Auric', 'Ergeson Nitonde', 'a.ergeson.nitonde@bbsliothek.local', 'azubi123'),
    (@azubi_rolle, 'b.szovga', 'Bogdan', 'Szovga', 'b.szovga@bbsliothek.local', 'azubi123'),
    (@azubi_rolle, 'd.sabelinski', 'Daniel', 'Sabelinski', 'd.sabelinski@bbsliothek.local', 'azubi123'),
    (@azubi_rolle, 'd.litau', 'Dennis', 'Litau', 'd.litau@bbsliothek.local', 'azubi123'),
    (@azubi_rolle, 'd.khalaf', 'Diyar', 'Khalaf', 'd.khalaf@bbsliothek.local', 'azubi123'),
    (@azubi_rolle, 'f.kauly', 'Finn Elias', 'Kauly', 'f.kauly@bbsliothek.local', 'azubi123'),
    (@azubi_rolle, 'h.grobe', 'Henner', 'Grobe', 'h.grobe@bbsliothek.local', 'azubi123'),
    (@azubi_rolle, 'j.bammann', 'Jan', 'Bammann', 'j.bammann@bbsliothek.local', 'azubi123'),
    (@azubi_rolle, 'j.jodeit', 'Janek', 'Jodeit', 'j.jodeit@bbsliothek.local', 'azubi123'),
    (@azubi_rolle, 'j.mansholt', 'Janes', 'Mansholt', 'j.mansholt@bbsliothek.local', 'azubi123'),
    (@azubi_rolle, 'j.lange', 'Jasper', 'Lange', 'j.lange@bbsliothek.local', 'azubi123'),
    (@azubi_rolle, 'j.siemer', 'Josefa', 'Siemer', 'j.siemer@bbsliothek.local', 'azubi123'),
    (@azubi_rolle, 'k.detjen', 'Kolja Lian', 'Detjen', 'k.detjen@bbsliothek.local', 'azubi123'),
    (@azubi_rolle, 'l.waldmann', 'Lea', 'Waldmann', 'l.waldmann@bbsliothek.local', 'azubi123'),
    (@azubi_rolle, 'l.seifert', 'Leif Erik', 'Seifert', 'l.seifert@bbsliothek.local', 'azubi123'),
    (@azubi_rolle, 'm.droehne', 'Madleen', 'Dröhne', 'm.droehne@bbsliothek.local', 'azubi123'),
    (@azubi_rolle, 'm.hrebinec', 'Marcello', 'Hrebinec', 'm.hrebinec@bbsliothek.local', 'azubi123'),
    (@azubi_rolle, 'm.toepfer', 'Max', 'Töpfer', 'm.toepfer@bbsliothek.local', 'azubi123'),
    (@azubi_rolle, 'm.dzhavid', 'Mert', 'Dzhavid', 'm.dzhavid@bbsliothek.local', 'azubi123'),
    (@azubi_rolle, 'p.fleddermann', 'Pascal', 'Fleddermann', 'p.fleddermann@bbsliothek.local', 'azubi123'),
    (@azubi_rolle, 'p.batroff', 'Philipp', 'Batroff', 'p.batroff@bbsliothek.local', 'azubi123'),
    (@azubi_rolle, 'r.frese', 'Ramona', 'Frese', 'r.frese@bbsliothek.local', 'azubi123'),
    (@azubi_rolle, 's.stopat', 'Simon Paul', 'Stopat', 's.stopat@bbsliothek.local', 'azubi123'),
    (@azubi_rolle, 't.carstens', 'Thorge', 'Carstens', 't.carstens@bbsliothek.local', 'azubi123'),
    (@azubi_rolle, 't.trost', 'Tim', 'Trost', 't.trost@bbsliothek.local', 'azubi123'),
    (@azubi_rolle, 't.guennemann-koerber', 'Tino', 'Günnemann-Körber', 't.guennemann-koerber@bbsliothek.local', 'azubi123')
ON DUPLICATE KEY UPDATE
    rollen_id = VALUES(rollen_id),
    vorname = VALUES(vorname),
    nachname = VALUES(nachname),
    email = VALUES(email),
    passwort = VALUES(passwort);
