from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class QueryDefinition:
    key: str
    title: str
    description: str
    sql: str


STANDARD_QUERIES: dict[str, QueryDefinition] = {
    "1": QueryDefinition(
        key="1",
        title="Aggregation 1: Anzahl der Materialien pro Themengebiet",
        description="Zeigt, wie viele Materialien je Themengebiet aktuell vorhanden sind.",
        sql="""
            SELECT
                tg.name AS themengebiet,
                COUNT(m.material_id) AS anzahl_materialien
            FROM themengebiete tg
            LEFT JOIN materialien m ON m.themengebiet_id = tg.themengebiet_id
            GROUP BY tg.themengebiet_id, tg.name
            ORDER BY tg.name
        """,
    ),
    "2": QueryDefinition(
        key="2",
        title="Aggregation 2: Anzahl der Kommentare pro Material",
        description="Ermittelt die Anzahl der Kommentare zu jedem Material.",
        sql="""
            SELECT
                m.material_id,
                m.titel,
                COUNT(k.kommentar_id) AS anzahl_kommentare
            FROM materialien m
            INNER JOIN material_versionen mv ON mv.version_id = m.aktuelle_version_id
            LEFT JOIN kommentare k ON k.material_id = m.material_id
            GROUP BY m.material_id, m.titel
            ORDER BY anzahl_kommentare DESC, m.titel
        """,
    ),
    "3": QueryDefinition(
        key="3",
        title="Inner Join 1: Materialien mit Themengebiet",
        description="Listet Materialien zusammen mit ihrem Themengebiet.",
        sql="""
            SELECT
                m.material_id,
                m.titel,
                mv.dateiname,
                tg.name AS themengebiet
            FROM materialien m
            INNER JOIN material_versionen mv ON mv.version_id = m.aktuelle_version_id
            INNER JOIN themengebiete tg ON tg.themengebiet_id = m.themengebiet_id
            ORDER BY m.titel
        """,
    ),
    "4": QueryDefinition(
        key="4",
        title="Inner Join 2: Materialien mit Autor",
        description="Listet Materialien zusammen mit dem verantwortlichen Autor.",
        sql="""
            SELECT
                m.material_id,
                m.titel,
                mv.dateiname,
                b.anzeigename AS autor
            FROM materialien m
            INNER JOIN material_versionen mv ON mv.version_id = m.aktuelle_version_id
            INNER JOIN benutzer b ON b.benutzer_id = m.erstellt_von
            ORDER BY b.anzeigename, m.titel
        """,
    ),
    "5": QueryDefinition(
        key="5",
        title="Join + Aggregation: Anzahl Materialien pro Autor",
        description="Zählt, wie viele Materialien pro Autor angelegt wurden.",
        sql="""
            SELECT
                b.anzeigename AS autor,
                COUNT(m.material_id) AS anzahl_materialien
            FROM benutzer b
            INNER JOIN materialien m ON m.erstellt_von = b.benutzer_id
            GROUP BY b.benutzer_id, b.anzeigename
            ORDER BY anzahl_materialien DESC, autor
        """,
    ),
    "6": QueryDefinition(
        key="6",
        title="Mehrtabellen-Join 1: Material + Themengebiet + Autor",
        description="Verknüpft Material, Themengebiet und Autor in einer Übersicht.",
        sql="""
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
            ORDER BY tg.name, b.anzeigename, m.titel
        """,
    ),
    "7": QueryDefinition(
        key="7",
        title="Mehrtabellen-Join 2: Material + Kommentare + Kommentarautor",
        description="Zeigt Materialien mit ihren Kommentaren und dem jeweiligen Kommentarautor.",
        sql="""
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
            ORDER BY m.titel, k.erstellt_am
        """,
    ),
}
