from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from bbsliothek.config import AppConfig
from bbsliothek.exceptions import ValidationError
from bbsliothek.models import (
    CommentRecord,
    MaterialDownloadRecord,
    MaterialRecord,
    StorageStrategy,
    UploadResult,
)
from bbsliothek.services.material_service import MaterialService


class FakeRepository:
    def __init__(self) -> None:
        self.users = {1: "Mia", 2: "Luca"}
        self.topics = {1: "Informatik", 2: "Mathematik"}
        self.materials: dict[int, dict] = {}
        self.downloads: dict[int, MaterialDownloadRecord] = {}
        self.comments: dict[int, list[CommentRecord]] = {}
        self.saved_payloads = []
        self.next_material_id = 1
        self.next_version_id = 1
        self.next_comment_id = 1

    def list_roles(self):
        return []

    def list_users(self):
        return []

    def list_topics(self):
        return []

    def list_materials(self, **kwargs):
        return []

    def create_topic(self, name: str, beschreibung: str) -> int:
        topic_id = max(self.topics, default=0) + 1
        self.topics[topic_id] = name
        return topic_id

    def user_exists(self, user_id: int) -> bool:
        return user_id in self.users

    def topic_exists(self, topic_id: int) -> bool:
        return topic_id in self.topics

    def get_material(self, material_id: int) -> MaterialRecord:
        if material_id not in self.materials:
            raise ValidationError("Material nicht gefunden.")
        item = self.materials[material_id]
        return MaterialRecord(
            material_id=material_id,
            titel=item["titel"],
            themengebiet_id=item["themengebiet_id"],
            erstellt_von=item["erstellt_von"],
            aktuelle_version_id=item["aktuelle_version_id"],
        )

    def save_material_upload(self, payload):
        self.saved_payloads.append(payload)
        if payload.material_id is None:
            material_id = self.next_material_id
            self.next_material_id += 1
            version_number = 1
            self.materials[material_id] = {
                "titel": payload.titel,
                "themengebiet_id": payload.themengebiet_id,
                "erstellt_von": payload.autor_id,
                "aktuelle_version_id": self.next_version_id,
            }
        else:
            material_id = payload.material_id
            version_number = self.materials[material_id].get("version_number", 1) + 1
            self.materials[material_id]["aktuelle_version_id"] = self.next_version_id

        version_id = self.next_version_id
        self.next_version_id += 1
        self.materials[material_id]["version_number"] = version_number
        self.downloads[material_id] = MaterialDownloadRecord(
            material_id=material_id,
            titel=self.materials[material_id]["titel"],
            dateiname=payload.dateiname,
            dateityp=payload.dateityp,
            speicherstrategie=payload.speicherstrategie.value,
            blob_inhalt=payload.blob_inhalt,
            dateipfad=payload.dateipfad,
        )
        return UploadResult(
            material_id=material_id,
            version_id=version_id,
            versionsnummer=version_number,
            speicherstrategie=payload.speicherstrategie.value,
            dateiname=payload.dateiname,
        )

    def get_material_download(self, material_id: int) -> MaterialDownloadRecord:
        return self.downloads[material_id]

    def list_comments(self, material_id: int):
        return self.comments.get(material_id, [])

    def add_comment(self, material_id: int, author_id: int, text: str) -> int:
        comment_id = self.next_comment_id
        self.next_comment_id += 1
        self.comments.setdefault(material_id, []).append(
            CommentRecord(
                kommentar_id=comment_id,
                autor=self.users[author_id],
                kommentartext=text,
                erstellt_am=None,
                geaendert_am=None,
            )
        )
        return comment_id


class MaterialServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        root = Path(self.temp_dir.name)
        self.config = AppConfig(
            db_host="localhost",
            db_port=3306,
            db_name="bbsliothek",
            db_user="root",
            db_password="",
            storage_root=root / "storage",
            download_root=root / "downloads",
            blob_limit_bytes=1_000_000,
        )
        self.config.ensure_directories()
        self.repository = FakeRepository()
        self.service = MaterialService(self.repository, self.config)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_small_file_is_saved_as_blob(self) -> None:
        source = self.config.download_root / "skript.py"
        source.write_text("print('hallo')", encoding="utf-8")

        result = self.service.upload_material(
            source_path=str(source),
            author_id=1,
            title="Python-Skript",
            topic_id=1,
        )

        self.assertEqual(result.versionsnummer, 1)
        payload = self.repository.saved_payloads[-1]
        self.assertEqual(payload.speicherstrategie, StorageStrategy.DB_BLOB)
        self.assertIsNotNone(payload.blob_inhalt)
        self.assertIsNone(payload.dateipfad)

    def test_large_file_is_saved_in_filesystem(self) -> None:
        source = self.config.download_root / "grosse_datei.bin"
        source.write_bytes(b"a" * 1_000_000)

        result = self.service.upload_material(
            source_path=str(source),
            author_id=1,
            title="Große Datei",
            topic_id=1,
        )

        self.assertEqual(result.versionsnummer, 1)
        payload = self.repository.saved_payloads[-1]
        self.assertEqual(payload.speicherstrategie, StorageStrategy.DATEISYSTEM)
        self.assertIsNone(payload.blob_inhalt)
        self.assertTrue(Path(payload.dateipfad).exists())

    def test_new_version_increments_version_number(self) -> None:
        source = self.config.download_root / "blatt.pdf"
        source.write_bytes(b"123")
        initial = self.service.upload_material(
            source_path=str(source),
            author_id=1,
            title="Arbeitsblatt",
            topic_id=1,
        )

        source.write_bytes(b"4567")
        second = self.service.upload_material(
            source_path=str(source),
            author_id=2,
            material_id=initial.material_id,
        )

        self.assertEqual(second.versionsnummer, 2)

    def test_download_blob_material(self) -> None:
        source = self.config.download_root / "notiz.txt"
        source.write_text("Testinhalt", encoding="utf-8")
        upload = self.service.upload_material(
            source_path=str(source),
            author_id=1,
            title="Notiz",
            topic_id=1,
        )

        export_path = self.service.download_material(upload.material_id)
        self.assertTrue(export_path.exists())
        self.assertEqual(export_path.read_text(encoding="utf-8"), "Testinhalt")

    def test_rejects_empty_comment(self) -> None:
        source = self.config.download_root / "note.txt"
        source.write_text("Kommentargrundlage", encoding="utf-8")
        upload = self.service.upload_material(
            source_path=str(source),
            author_id=1,
            title="Dokument",
            topic_id=1,
        )

        with self.assertRaises(ValidationError):
            self.service.add_comment(upload.material_id, 1, "   ")


if __name__ == "__main__":
    unittest.main()
