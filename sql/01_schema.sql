CREATE DATABASE IF NOT EXISTS bbsliothek
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE bbsliothek;

DROP VIEW IF EXISTS vw_material_aktuell;
DROP TABLE IF EXISTS kommentare;
DROP TABLE IF EXISTS material_versionen;
DROP TABLE IF EXISTS materialien;
DROP TABLE IF EXISTS benutzer;
DROP TABLE IF EXISTS themengebiete;
DROP TABLE IF EXISTS rollen;

CREATE TABLE IF NOT EXISTS rollen (
    rollen_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    beschreibung VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS benutzer (
    benutzer_id INT AUTO_INCREMENT PRIMARY KEY,
    rollen_id INT NOT NULL,
    anzeigename VARCHAR(120) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    erstellt_am DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_benutzer_rolle
        FOREIGN KEY (rollen_id) REFERENCES rollen (rollen_id)
);

CREATE TABLE IF NOT EXISTS themengebiete (
    themengebiet_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL UNIQUE,
    beschreibung VARCHAR(255) NOT NULL DEFAULT '',
    erstellt_am DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS materialien (
    material_id INT AUTO_INCREMENT PRIMARY KEY,
    titel VARCHAR(255) NOT NULL,
    themengebiet_id INT NOT NULL,
    erstellt_von INT NOT NULL,
    aktuelle_version_id INT NULL,
    erstellt_am DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    geaendert_am DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_material_themengebiet
        FOREIGN KEY (themengebiet_id) REFERENCES themengebiete (themengebiet_id),
    CONSTRAINT fk_material_autor
        FOREIGN KEY (erstellt_von) REFERENCES benutzer (benutzer_id)
);

CREATE TABLE IF NOT EXISTS material_versionen (
    version_id INT AUTO_INCREMENT PRIMARY KEY,
    material_id INT NOT NULL,
    versionsnummer INT NOT NULL,
    dateiname VARCHAR(255) NOT NULL,
    dateityp VARCHAR(120) NOT NULL,
    dateigroesse_bytes BIGINT NOT NULL,
    speicherstrategie ENUM('DB_BLOB', 'DATEISYSTEM') NOT NULL,
    blob_inhalt LONGBLOB NULL,
    dateipfad VARCHAR(1024) NULL,
    checksumme_sha256 CHAR(64) NOT NULL,
    erstellt_von INT NOT NULL,
    erstellt_am DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_material_version UNIQUE (material_id, versionsnummer),
    CONSTRAINT fk_version_material
        FOREIGN KEY (material_id) REFERENCES materialien (material_id),
    CONSTRAINT fk_version_autor
        FOREIGN KEY (erstellt_von) REFERENCES benutzer (benutzer_id)
);

ALTER TABLE materialien
    ADD CONSTRAINT fk_material_aktuelle_version
    FOREIGN KEY (aktuelle_version_id) REFERENCES material_versionen (version_id);

CREATE TABLE IF NOT EXISTS kommentare (
    kommentar_id INT AUTO_INCREMENT PRIMARY KEY,
    material_id INT NOT NULL,
    autor_id INT NOT NULL,
    kommentartext TEXT NOT NULL,
    erstellt_am DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    geaendert_am DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_kommentar_material
        FOREIGN KEY (material_id) REFERENCES materialien (material_id),
    CONSTRAINT fk_kommentar_autor
        FOREIGN KEY (autor_id) REFERENCES benutzer (benutzer_id)
);

CREATE INDEX idx_materialien_themengebiet ON materialien (themengebiet_id);
CREATE INDEX idx_materialien_autor ON materialien (erstellt_von);
CREATE INDEX idx_versionen_dateiname ON material_versionen (dateiname);
CREATE INDEX idx_versionen_dateityp ON material_versionen (dateityp);
CREATE INDEX idx_kommentare_material ON kommentare (material_id);

CREATE OR REPLACE VIEW vw_material_aktuell AS
SELECT
    m.material_id,
    m.titel,
    m.themengebiet_id,
    m.erstellt_von AS material_autor_id,
    a.anzeigename AS material_autor_name,
    tg.name AS themengebiet_name,
    m.erstellt_am AS material_erstellt_am,
    m.geaendert_am AS material_geaendert_am,
    mv.version_id,
    mv.versionsnummer,
    mv.dateiname,
    mv.dateityp,
    mv.dateigroesse_bytes,
    mv.speicherstrategie,
    mv.blob_inhalt,
    mv.dateipfad,
    mv.checksumme_sha256,
    mv.erstellt_von AS version_autor_id,
    va.anzeigename AS version_autor_name,
    mv.erstellt_am AS version_erstellt_am
FROM materialien m
INNER JOIN material_versionen mv ON mv.version_id = m.aktuelle_version_id
INNER JOIN themengebiete tg ON tg.themengebiet_id = m.themengebiet_id
INNER JOIN benutzer a ON a.benutzer_id = m.erstellt_von
INNER JOIN benutzer va ON va.benutzer_id = mv.erstellt_von;
