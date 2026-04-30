from __future__ import annotations

import hashlib
import mimetypes
import os
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

from bbsliothek.config import AppConfig
from bbsliothek.exceptions import RepositoryError, ValidationError
from bbsliothek.models import StorageStrategy, UploadPayload


class MaterialService:
    def __init__(self, repository, config: AppConfig) -> None:
        self.repository = repository
        self.config = config

    def list_roles(self):
        return self.repository.list_roles()

    def list_users(self):
        return self.repository.list_users()

    def list_topics(self):
        return self.repository.list_topics()

    def list_materials(
        self,
        title_filter: str | None = None,
        file_type: str | None = None,
        topic_id: int | None = None,
        author_id: int | None = None,
    ):
        return self.repository.list_materials(
            title_filter=title_filter,
            file_type=file_type,
            topic_id=topic_id,
            author_id=author_id,
        )

    def create_topic(self, name: str, beschreibung: str) -> int:
        if not name.strip():
            raise ValidationError("Der Name des Themengebiets darf nicht leer sein.")
        return self.repository.create_topic(name.strip(), beschreibung.strip())

    def upload_material(
        self,
        source_path: str,
        author_id: int,
        title: str | None = None,
        topic_id: int | None = None,
        material_id: int | None = None,
    ):
        file_path = Path(source_path).expanduser().resolve()
        if not file_path.exists() or not file_path.is_file():
            raise ValidationError("Die angegebene Datei wurde nicht gefunden.")

        if not self.repository.user_exists(author_id):
            raise ValidationError(f"Benutzer-ID {author_id} wurde nicht gefunden.")

        if material_id is None:
            if topic_id is None or not self.repository.topic_exists(topic_id):
                raise ValidationError("Für ein neues Material muss ein gültiges Themengebiet gewählt werden.")
            if not title or not title.strip():
                raise ValidationError("Für ein neues Material muss ein Titel angegeben werden.")
        else:
            self.repository.get_material(material_id)

        file_size = file_path.stat().st_size
        checksum = self._calculate_checksum(file_path)
        file_type = self._detect_file_type(file_path)
        storage_strategy = self._choose_storage_strategy(file_size)

        blob_content: bytes | None = None
        stored_path: str | None = None
        created_file_path: Path | None = None

        try:
            if storage_strategy is StorageStrategy.DB_BLOB:
                blob_content = file_path.read_bytes()
            else:
                created_file_path = self._copy_to_managed_storage(file_path)
                stored_path = str(created_file_path)

            payload = UploadPayload(
                material_id=material_id,
                titel=title.strip() if title else None,
                themengebiet_id=topic_id,
                autor_id=author_id,
                dateiname=file_path.name,
                dateityp=file_type,
                dateigroesse_bytes=file_size,
                checksumme_sha256=checksum,
                speicherstrategie=storage_strategy,
                blob_inhalt=blob_content,
                dateipfad=stored_path,
            )
            return self.repository.save_material_upload(payload)
        except Exception:
            if created_file_path and created_file_path.exists():
                created_file_path.unlink(missing_ok=True)
            raise

    def download_material(
        self,
        material_id: int,
        destination_dir: str | None = None,
        auto_open: bool = False,
    ) -> Path:
        download_record = self.repository.get_material_download(material_id)
        target_dir = Path(destination_dir).expanduser().resolve() if destination_dir else self.config.download_root
        target_dir.mkdir(parents=True, exist_ok=True)

        target_path = target_dir / download_record.dateiname
        if target_path.exists():
            target_path = self._deduplicate_target_path(target_path)

        if download_record.speicherstrategie == StorageStrategy.DB_BLOB.value:
            if download_record.blob_inhalt is None:
                raise RepositoryError("Die BLOB-Daten des Materials fehlen in der Datenbank.")
            target_path.write_bytes(download_record.blob_inhalt)
        else:
            if not download_record.dateipfad:
                raise RepositoryError("Es ist kein Dateipfad für das Material hinterlegt.")
            source_path = Path(download_record.dateipfad)
            if not source_path.exists():
                raise RepositoryError(f"Die referenzierte Datei wurde nicht gefunden: {source_path}")
            shutil.copy2(source_path, target_path)

        if auto_open:
            self._open_file(target_path)
        return target_path

    def list_comments(self, material_id: int):
        self.repository.get_material(material_id)
        return self.repository.list_comments(material_id)

    def add_comment(self, material_id: int, author_id: int, text: str) -> int:
        cleaned_text = text.strip()
        if not cleaned_text:
            raise ValidationError("Der Kommentartext darf nicht leer sein.")
        if not self.repository.user_exists(author_id):
            raise ValidationError(f"Benutzer-ID {author_id} wurde nicht gefunden.")
        self.repository.get_material(material_id)
        return self.repository.add_comment(material_id, author_id, cleaned_text)

    def _choose_storage_strategy(self, file_size: int) -> StorageStrategy:
        if file_size < self.config.blob_limit_bytes:
            return StorageStrategy.DB_BLOB
        return StorageStrategy.DATEISYSTEM

    def _calculate_checksum(self, path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(8192), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def _detect_file_type(self, path: Path) -> str:
        mime_type, _ = mimetypes.guess_type(path.name)
        if mime_type:
            return mime_type
        return path.suffix.lstrip(".") or "unbekannt"

    def _copy_to_managed_storage(self, source_path: Path) -> Path:
        unique_name = f"{uuid.uuid4().hex}_{source_path.name}"
        target_path = self.config.storage_root / unique_name
        shutil.copy2(source_path, target_path)
        return target_path

    def _deduplicate_target_path(self, target_path: Path) -> Path:
        counter = 1
        while True:
            candidate = target_path.with_name(
                f"{target_path.stem}_{counter}{target_path.suffix}"
            )
            if not candidate.exists():
                return candidate
            counter += 1

    def _open_file(self, file_path: Path) -> None:
        try:
            if sys.platform == "darwin":
                subprocess.run(["open", str(file_path)], check=False)
            elif sys.platform == "win32":
                os.startfile(str(file_path))  # type: ignore[attr-defined]
            else:
                subprocess.run(["xdg-open", str(file_path)], check=False)
        except Exception as exc:
            raise RepositoryError(f"Datei konnte nicht geöffnet werden: {exc}") from exc
