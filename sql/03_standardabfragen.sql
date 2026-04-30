USE bbsliothek;

-- 1. Aggregation: Anzahl der Materialien pro Themengebiet
SELECT
    tg.name AS themengebiet,
    COUNT(m.material_id) AS anzahl_materialien
FROM themengebiete tg
LEFT JOIN materialien m ON m.themengebiet_id = tg.themengebiet_id
GROUP BY tg.themengebiet_id, tg.name
ORDER BY tg.name;

-- 2. Aggregation: Anzahl der Kommentare pro Material
SELECT
    m.material_id,
    m.titel,
    COUNT(k.kommentar_id) AS anzahl_kommentare
FROM materialien m
INNER JOIN material_versionen mv ON mv.version_id = m.aktuelle_version_id
LEFT JOIN kommentare k ON k.material_id = m.material_id
GROUP BY m.material_id, m.titel
ORDER BY anzahl_kommentare DESC, m.titel;

-- 3. Inner Join: Materialien mit Themengebiet
SELECT
    m.material_id,
    m.titel,
    mv.dateiname,
    tg.name AS themengebiet
FROM materialien m
INNER JOIN material_versionen mv ON mv.version_id = m.aktuelle_version_id
INNER JOIN themengebiete tg ON tg.themengebiet_id = m.themengebiet_id
ORDER BY m.titel;

-- 4. Inner Join: Materialien mit Autor
SELECT
    m.material_id,
    m.titel,
    mv.dateiname,
    b.anzeigename AS autor
FROM materialien m
INNER JOIN material_versionen mv ON mv.version_id = m.aktuelle_version_id
INNER JOIN benutzer b ON b.benutzer_id = m.erstellt_von
ORDER BY b.anzeigename, m.titel;

-- 5. Join + Aggregation: Anzahl Materialien pro Autor
SELECT
    b.anzeigename AS autor,
    COUNT(m.material_id) AS anzahl_materialien
FROM benutzer b
INNER JOIN materialien m ON m.erstellt_von = b.benutzer_id
GROUP BY b.benutzer_id, b.anzeigename
ORDER BY anzahl_materialien DESC, autor;

-- 6. Mehrtabellen-Join: Material + Themengebiet + Autor
SELECT
    m.material_id,
    m.titel,
    mv.dateiname,
    tg.name AS themengebiet,
    b.anzeigename AS autor
FROM materialien m
INNER JOIN material_versionen mv ON mv.version_id = m.aktuelle_version_id
INNER JOIN themengebiete tg ON tg.themengebiet_id = m.themengebiet_id
INNER JOIN benutzer b ON b.benutzer_id = m.erstellt_von
ORDER BY tg.name, b.anzeigename, m.titel;

-- 7. Mehrtabellen-Join: Material + Kommentare + Kommentarautor
SELECT
    m.material_id,
    m.titel,
    mv.dateiname,
    k.kommentar_id,
    k.kommentartext,
    b.anzeigename AS kommentarautor
FROM materialien m
INNER JOIN material_versionen mv ON mv.version_id = m.aktuelle_version_id
INNER JOIN kommentare k ON k.material_id = m.material_id
INNER JOIN benutzer b ON b.benutzer_id = k.autor_id
ORDER BY m.titel, k.erstellt_am;
