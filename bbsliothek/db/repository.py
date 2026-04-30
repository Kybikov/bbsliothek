from __future__ import annotations

from dataclasses import asdict
from typing import Any

from bbsliothek.config import AppConfig
from bbsliothek.db.connection import MySQLError, create_connection
from bbsliothek.db.query_catalog import STANDARD_QUERIES
from bbsliothek.exceptions import RepositoryError, ValidationError
from bbsliothek.models import (
    CommentRecord,
    MaterialDownloadRecord,
    MaterialRecord,
    MaterialSummary,
    RoleRecord,
    TopicRecord,
    UploadPayload,
    UploadResult,
    UserRecord,
)


class MySQLRepository:
    def __init__(self, config: AppConfig) -> None:
        self.config = config

    def _fetchall(self, query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        connection = create_connection(self.config)
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(query, params)
            return list(cursor.fetchall())
        except MySQLError as exc:  # pragma: no cover - benötigt echte Datenbank
            raise RepositoryError(f"Daten konnten nicht gelesen werden: {exc}") from exc
        finally:
            cursor.close()
            connection.close()

    def _fetchone(self, query: str, params: tuple[Any, ...] = ()) -> dict[str, Any] | None:
        rows = self._fetchall(query, params)
        return rows[0] if rows else None

    def list_roles(self) -> list[RoleRecord]:
        rows = self._fetchall(
            """
            SELECT rollen_id, name, beschreibung
            FROM rollen
            ORDER BY rollen_id
            """
        )
        return [RoleRecord(**row) for row in rows]

    def list_users(self) -> list[UserRecord]:
        rows = self._fetchall(
            """
            SELECT
                b.benutzer_id,
                b.anzeigename,
                b.email,
                r.name AS rollenname
            FROM benutzer b
            INNER JOIN rollen r ON r.rollen_id = b.rollen_id
            ORDER BY b.anzeigename
            """
        )
        return [UserRecord(**row) for row in rows]

    def list_topics(self) -> list[TopicRecord]:
        rows = self._fetchall(
            """
            SELECT themengebiet_id, name, beschreibung
            FROM themengebiete
            ORDER BY name
            """
        )
        return [TopicRecord(**row) for row in rows]

    def create_topic(self, name: str, beschreibung: str) -> int:
        connection = create_connection(self.config)
        cursor = connection.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO themengebiete (name, beschreibung)
                VALUES (%s, %s)
                """,
                (name, beschreibung),
            )
            connection.commit()
            return int(cursor.lastrowid)
        except MySQLError as exc:  # pragma: no cover - benötigt echte Datenbank
            connection.rollback()
            raise RepositoryError(f"Themengebiet konnte nicht angelegt werden: {exc}") from exc
        finally:
            cursor.close()
            connection.close()

    def user_exists(self, user_id: int) -> bool:
        return self._fetchone("SELECT benutzer_id FROM benutzer WHERE benutzer_id = %s", (user_id,)) is not None

    def topic_exists(self, topic_id: int) -> bool:
        return (
            self._fetchone(
                "SELECT themengebiet_id FROM themengebiete WHERE themengebiet_id = %s",
                (topic_id,),
            )
            is not None
        )

    def get_material(self, material_id: int) -> MaterialRecord:
        row = self._fetchone(
            """
            SELECT material_id, titel, themengebiet_id, erstellt_von, aktuelle_version_id
            FROM materialien
            WHERE material_id = %s
            """,
            (material_id,),
        )
        if row is None:
            raise ValidationError(f"Material-ID {material_id} wurde nicht gefunden.")
        return MaterialRecord(**row)

    def list_materials(
        self,
        title_filter: str | None = None,
        file_type: str | None = None,
        topic_id: int | None = None,
        author_id: int | None = None,
    ) -> list[MaterialSummary]:
        query = """
            SELECT
                material_id,
                titel,
                dateiname,
                dateityp,
                themengebiet_name AS themengebiet,
                material_autor_name AS autor,
                versionsnummer AS version,
                dateigroesse_bytes,
                speicherstrategie,
                material_erstellt_am AS erstellt_am,
                material_geaendert_am AS geaendert_am
            FROM vw_material_aktuell
            WHERE 1 = 1
        """
        params: list[Any] = []
        if title_filter:
            query += " AND (titel LIKE %s OR dateiname LIKE %s)"
            like_value = f"%{title_filter}%"
            params.extend([like_value, like_value])
        if file_type:
            query += " AND dateityp LIKE %s"
            params.append(f"%{file_type}%")
        if topic_id:
            query += " AND themengebiet_id = %s"
            params.append(topic_id)
        if author_id:
            query += " AND material_autor_id = %s"
            params.append(author_id)
        query += " ORDER BY titel, versionsnummer DESC"

        rows = self._fetchall(query, tuple(params))
        return [MaterialSummary(**row) for row in rows]

    def save_material_upload(self, payload: UploadPayload) -> UploadResult:
        connection = create_connection(self.config)
        cursor = connection.cursor(dictionary=True)
        try:
            connection.start_transaction()
            if payload.material_id is None:
                if payload.titel is None or payload.themengebiet_id is None:
                    raise ValidationError("Neues Material benötigt Titel und Themengebiet.")

                cursor.execute(
                    """
                    INSERT INTO materialien (
                        titel,
                        themengebiet_id,
                        erstellt_von,
                        erstellt_am,
                        geaendert_am
                    )
                    VALUES (%s, %s, %s, NOW(), NOW())
                    """,
                    (payload.titel, payload.themengebiet_id, payload.autor_id),
                )
                material_id = int(cursor.lastrowid)
            else:
                material = self.get_material(payload.material_id)
                material_id = material.material_id

            cursor.execute(
                """
                SELECT COALESCE(MAX(versionsnummer), 0) + 1 AS naechste_version
                FROM material_versionen
                WHERE material_id = %s
                """,
                (material_id,),
            )
            row = cursor.fetchone()
            version_number = int(row["naechste_version"])

            cursor.execute(
                """
                INSERT INTO material_versionen (
                    material_id,
                    versionsnummer,
                    dateiname,
                    dateityp,
                    dateigroesse_bytes,
                    speicherstrategie,
                    blob_inhalt,
                    dateipfad,
                    checksumme_sha256,
                    erstellt_von,
                    erstellt_am
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                """,
                (
                    material_id,
                    version_number,
                    payload.dateiname,
                    payload.dateityp,
                    payload.dateigroesse_bytes,
                    payload.speicherstrategie.value,
                    payload.blob_inhalt,
                    payload.dateipfad,
                    payload.checksumme_sha256,
                    payload.autor_id,
                ),
            )
            version_id = int(cursor.lastrowid)

            cursor.execute(
                """
                UPDATE materialien
                SET aktuelle_version_id = %s,
                    geaendert_am = NOW()
                WHERE material_id = %s
                """,
                (version_id, material_id),
            )

            connection.commit()
            return UploadResult(
                material_id=material_id,
                version_id=version_id,
                versionsnummer=version_number,
                speicherstrategie=payload.speicherstrategie.value,
                dateiname=payload.dateiname,
            )
        except (MySQLError, ValidationError) as exc:  # pragma: no cover - benötigt echte Datenbank
            connection.rollback()
            if isinstance(exc, ValidationError):
                raise
            raise RepositoryError(f"Upload konnte nicht gespeichert werden: {exc}") from exc
        finally:
            cursor.close()
            connection.close()

    def get_material_download(self, material_id: int) -> MaterialDownloadRecord:
        row = self._fetchone(
            """
            SELECT
                material_id,
                titel,
                dateiname,
                dateityp,
                speicherstrategie,
                blob_inhalt,
                dateipfad
            FROM vw_material_aktuell
            WHERE material_id = %s
            """,
            (material_id,),
        )
        if row is None:
            raise ValidationError(f"Material-ID {material_id} wurde nicht gefunden.")
        return MaterialDownloadRecord(**row)

    def list_comments(self, material_id: int) -> list[CommentRecord]:
        rows = self._fetchall(
            """
            SELECT
                k.kommentar_id,
                b.anzeigename AS autor,
                k.kommentartext,
                k.erstellt_am,
                k.geaendert_am
            FROM kommentare k
            INNER JOIN benutzer b ON b.benutzer_id = k.autor_id
            WHERE k.material_id = %s
            ORDER BY k.erstellt_am
            """,
            (material_id,),
        )
        return [CommentRecord(**row) for row in rows]

    def add_comment(self, material_id: int, author_id: int, text: str) -> int:
        connection = create_connection(self.config)
        cursor = connection.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO kommentare (
                    material_id,
                    autor_id,
                    kommentartext,
                    erstellt_am,
                    geaendert_am
                )
                VALUES (%s, %s, %s, NOW(), NOW())
                """,
                (material_id, author_id, text),
            )
            connection.commit()
            return int(cursor.lastrowid)
        except MySQLError as exc:  # pragma: no cover - benötigt echte Datenbank
            connection.rollback()
            raise RepositoryError(f"Kommentar konnte nicht gespeichert werden: {exc}") from exc
        finally:
            cursor.close()
            connection.close()

    def run_standard_query(self, query_key: str) -> tuple[str, str, list[dict[str, Any]]]:
        definition = STANDARD_QUERIES.get(query_key)
        if definition is None:
            raise ValidationError("Unbekannte Standardabfrage.")
        return definition.title, definition.description, self._fetchall(definition.sql)

    def as_row_dicts(self, records: list[Any]) -> list[dict[str, Any]]:
        return [asdict(record) for record in records]
