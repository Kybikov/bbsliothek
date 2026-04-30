from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class StorageStrategy(str, Enum):
    DB_BLOB = "DB_BLOB"
    DATEISYSTEM = "DATEISYSTEM"


@dataclass(slots=True)
class RoleRecord:
    rollen_id: int
    name: str
    beschreibung: str


@dataclass(slots=True)
class UserRecord:
    benutzer_id: int
    anzeigename: str
    email: str
    rollenname: str


@dataclass(slots=True)
class TopicRecord:
    themengebiet_id: int
    name: str
    beschreibung: str


@dataclass(slots=True)
class MaterialSummary:
    material_id: int
    titel: str
    dateiname: str
    dateityp: str
    themengebiet: str
    autor: str
    version: int
    dateigroesse_bytes: int
    speicherstrategie: str
    erstellt_am: datetime
    geaendert_am: datetime


@dataclass(slots=True)
class MaterialRecord:
    material_id: int
    titel: str
    themengebiet_id: int
    erstellt_von: int
    aktuelle_version_id: int | None


@dataclass(slots=True)
class MaterialDownloadRecord:
    material_id: int
    titel: str
    dateiname: str
    dateityp: str
    speicherstrategie: str
    blob_inhalt: bytes | None
    dateipfad: str | None


@dataclass(slots=True)
class CommentRecord:
    kommentar_id: int
    autor: str
    kommentartext: str
    erstellt_am: datetime
    geaendert_am: datetime


@dataclass(slots=True)
class UploadPayload:
    material_id: int | None
    titel: str | None
    themengebiet_id: int | None
    autor_id: int
    dateiname: str
    dateityp: str
    dateigroesse_bytes: int
    checksumme_sha256: str
    speicherstrategie: StorageStrategy
    blob_inhalt: bytes | None
    dateipfad: str | None


@dataclass(slots=True)
class UploadResult:
    material_id: int
    version_id: int
    versionsnummer: int
    speicherstrategie: str
    dateiname: str
