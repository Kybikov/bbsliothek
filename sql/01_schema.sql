CREATE DATABASE bbsliothek
    CHARACTER SET utf8mb4;

USE bbsliothek;

CREATE TABLE rollen (
    rollen_id    INT AUTO_INCREMENT PRIMARY KEY,
    name         VARCHAR(50)  NOT NULL UNIQUE,
    beschreibung VARCHAR(255) NOT NULL
);

-- Passwort wird als Klartext gespeichert (vereinfachte Lösung für das Schulprojekt)
-- In einer echten Anwendung würde man bcrypt oder ähnliches verwenden
CREATE TABLE benutzer (
    benutzer_id  INT AUTO_INCREMENT PRIMARY KEY,
    rollen_id    INT          NOT NULL,
    benutzername VARCHAR(60)  NOT NULL UNIQUE,
    vorname      VARCHAR(60)  NOT NULL,
    nachname     VARCHAR(60)  NOT NULL,
    email        VARCHAR(255) NOT NULL UNIQUE,
    passwort     VARCHAR(255) NOT NULL DEFAULT 'password123',
    erstellt_am  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rollen_id) REFERENCES rollen (rollen_id)
);

CREATE TABLE themengebiete (
    themengebiet_id INT AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(120) NOT NULL UNIQUE,
    beschreibung    VARCHAR(255) NOT NULL DEFAULT '',
    erstellt_am     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE materialien (
    material_id         INT AUTO_INCREMENT PRIMARY KEY,
    titel               VARCHAR(255) NOT NULL,
    themengebiet_id     INT          NOT NULL,
    erstellt_von        INT          NOT NULL,
    aktuelle_version_id INT          NULL,
    erstellt_am         DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    geaendert_am        DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (themengebiet_id) REFERENCES themengebiete (themengebiet_id),
    FOREIGN KEY (erstellt_von)    REFERENCES benutzer (benutzer_id)
);

-- Dateien unter 1 MB werden als BLOB direkt in der Datenbank gespeichert
-- Dateien ab 1 MB werden im Dateisystem abgelegt, dateipfad zeigt auf die Datei
CREATE TABLE material_versionen (
    version_id         INT AUTO_INCREMENT PRIMARY KEY,
    material_id        INT          NOT NULL,
    versionsnummer     INT          NOT NULL,
    dateiname          VARCHAR(255) NOT NULL,
    dateityp           VARCHAR(120) NOT NULL,
    dateigroesse_bytes BIGINT       NOT NULL,
    speicherstrategie  ENUM('DB_BLOB', 'DATEISYSTEM') NOT NULL DEFAULT 'DATEISYSTEM',
    blob_inhalt        LONGBLOB     NULL,
    dateipfad          VARCHAR(1024) NULL,
    erstellt_von       INT          NOT NULL,
    erstellt_am        DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (material_id, versionsnummer),
    FOREIGN KEY (material_id)  REFERENCES materialien (material_id),
    FOREIGN KEY (erstellt_von) REFERENCES benutzer (benutzer_id)
);

-- Fremdschlüssel nachträglich hinzufügen wegen dem zyklischen Verweis
-- (materialien -> material_versionen -> materialien)
-- Das war ein Fehler beim ersten Entwurf der Datenbank
ALTER TABLE materialien
    ADD FOREIGN KEY (aktuelle_version_id) REFERENCES material_versionen (version_id);

CREATE TABLE kommentare (
    kommentar_id  INT AUTO_INCREMENT PRIMARY KEY,
    material_id   INT  NOT NULL,
    autor_id      INT  NOT NULL,
    kommentartext TEXT NOT NULL,
    erstellt_am   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    geaendert_am  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (material_id) REFERENCES materialien (material_id),
    FOREIGN KEY (autor_id)    REFERENCES benutzer (benutzer_id)
);

CREATE INDEX idx_materialien_themengebiet ON materialien (themengebiet_id);
CREATE INDEX idx_materialien_autor        ON materialien (erstellt_von);
CREATE INDEX idx_versionen_dateiname      ON material_versionen (dateiname);
CREATE INDEX idx_versionen_dateityp       ON material_versionen (dateityp);
CREATE INDEX idx_kommentare_material      ON kommentare (material_id);

-- View für die aktuelle Version jedes Materials
CREATE VIEW vw_material_aktuell AS
SELECT
    m.material_id,
    m.titel,
    m.themengebiet_id,
    m.erstellt_von                          AS material_autor_id,
    CONCAT(a.vorname, ' ', a.nachname)      AS material_autor_name,
    tg.name                AS themengebiet_name,
    m.erstellt_am          AS material_erstellt_am,
    m.geaendert_am         AS material_geaendert_am,
    mv.version_id,
    mv.versionsnummer,
    mv.dateiname,
    mv.dateityp,
    mv.dateigroesse_bytes,
    mv.speicherstrategie,
    mv.blob_inhalt,
    mv.dateipfad,
    mv.erstellt_von                         AS version_autor_id,
    CONCAT(va.vorname, ' ', va.nachname)    AS version_autor_name,
    mv.erstellt_am         AS version_erstellt_am
FROM materialien m
INNER JOIN material_versionen mv ON mv.version_id      = m.aktuelle_version_id
INNER JOIN themengebiete tg      ON tg.themengebiet_id = m.themengebiet_id
INNER JOIN benutzer a            ON a.benutzer_id      = m.erstellt_von
INNER JOIN benutzer va           ON va.benutzer_id     = mv.erstellt_von;
