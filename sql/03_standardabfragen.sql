USE bbsliothek;

-- 1. Aggregation: Anzahl der Materialien pro Themengebiet
SELECT
    tg.name AS Themengebiet,
    COUNT(m.material_id) AS Anzahl_Materialien
FROM themengebiete tg
LEFT JOIN materialien m ON m.themengebiet_id = tg.themengebiet_id
GROUP BY tg.themengebiet_id, tg.name
ORDER BY Anzahl_Materialien DESC;

-- 2. Aggregation: Durchschnittliche Dateigröße je Thema in KB
SELECT
    tg.name AS Themengebiet,
    ROUND(AVG(mv.dateigroesse_bytes) / 1024, 2) AS Durchschnitt_KB,
    COUNT(mv.version_id) AS Anzahl_Versionen
FROM themengebiete tg
INNER JOIN materialien m ON m.themengebiet_id = tg.themengebiet_id
INNER JOIN material_versionen mv ON mv.material_id = m.material_id
GROUP BY tg.themengebiet_id, tg.name;

-- 3. Inner Join: Materialien mit Autoren
SELECT
    m.material_id,
    m.titel,
    b.anzeigename AS Autor,
    b.email
FROM materialien m
INNER JOIN benutzer b ON b.benutzer_id = m.erstellt_von
ORDER BY m.titel;

-- 4. Inner Join: Kommentare mit Material und Autor
SELECT
    m.titel AS Material,
    b.anzeigename AS Kommentiert_von,
    LEFT(k.kommentartext, 60) AS Kommentar,
    k.erstellt_am
FROM kommentare k
INNER JOIN materialien m ON m.material_id = k.material_id
INNER JOIN benutzer b ON b.benutzer_id = k.autor_id
ORDER BY k.erstellt_am DESC;

-- 5. Join + Aggregation: Materialien pro Autor mit Rolle
SELECT
    b.anzeigename AS Autor,
    r.name AS Rolle,
    COUNT(m.material_id) AS Anzahl_Materialien
FROM benutzer b
INNER JOIN rollen r ON r.rollen_id = b.rollen_id
INNER JOIN materialien m ON m.erstellt_von = b.benutzer_id
GROUP BY b.benutzer_id, b.anzeigename, r.name
ORDER BY Anzahl_Materialien DESC;

-- 6. 2x Inner Join: Materialien mit Thema und Version
SELECT
    m.titel,
    tg.name AS Themengebiet,
    mv.versionsnummer AS Version,
    mv.dateiname,
    ROUND(mv.dateigroesse_bytes / 1024, 1) AS Groesse_KB,
    mv.speicherstrategie
FROM materialien m
INNER JOIN themengebiete tg ON tg.themengebiet_id = m.themengebiet_id
INNER JOIN material_versionen mv ON mv.version_id = m.aktuelle_version_id
ORDER BY tg.name, m.titel;

-- 7. Mehrere Joins: Vollständige Übersicht
SELECT
    m.titel,
    b.anzeigename AS Autor,
    tg.name AS Themengebiet,
    mv.versionsnummer AS Version,
    mv.dateityp,
    ROUND(mv.dateigroesse_bytes / 1024, 1) AS Groesse_KB,
    m.erstellt_am
FROM materialien m
INNER JOIN benutzer b ON b.benutzer_id = m.erstellt_von
INNER JOIN themengebiete tg ON tg.themengebiet_id = m.themengebiet_id
INNER JOIN material_versionen mv ON mv.version_id = m.aktuelle_version_id
ORDER BY m.erstellt_am DESC;
