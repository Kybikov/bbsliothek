from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class AppConfig:
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str
    storage_root: Path
    download_root: Path
    blob_limit_bytes: int

    @classmethod
    def from_env(cls) -> "AppConfig":
        project_root = Path(__file__).resolve().parent.parent
        storage_root = Path(
            os.getenv("BBSLIOTHEK_STORAGE_ROOT", project_root / "storage" / "materials")
        )
        download_root = Path(
            os.getenv("BBSLIOTHEK_DOWNLOAD_ROOT", project_root / "downloads")
        )
        return cls(
            db_host=os.getenv("BBSLIOTHEK_DB_HOST", "127.0.0.1"),
            db_port=int(os.getenv("BBSLIOTHEK_DB_PORT", "3306")),
            db_name=os.getenv("BBSLIOTHEK_DB_NAME", "bbsliothek"),
            db_user=os.getenv("BBSLIOTHEK_DB_USER", "root"),
            db_password=os.getenv("BBSLIOTHEK_DB_PASSWORD", ""),
            storage_root=storage_root,
            download_root=download_root,
            blob_limit_bytes=int(os.getenv("BBSLIOTHEK_BLOB_LIMIT_BYTES", "1000000")),
        )

    @property
    def project_root(self) -> Path:
        return Path(__file__).resolve().parent.parent

    @property
    def sql_root(self) -> Path:
        return self.project_root / "sql"

    def ensure_directories(self) -> None:
        self.storage_root.mkdir(parents=True, exist_ok=True)
        self.download_root.mkdir(parents=True, exist_ok=True)
