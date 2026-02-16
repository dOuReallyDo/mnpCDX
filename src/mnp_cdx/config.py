"""Runtime configuration utilities."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


@dataclass(frozen=True)
class Settings:
    base_dir: Path
    data_dir: Path
    db_path: Path
    mapping_path: Path

    @classmethod
    def load(cls) -> "Settings":
        base_dir = Path(os.getenv("MNP_CDX_BASE_DIR", Path.cwd())).resolve()
        data_dir = Path(os.getenv("MNP_CDX_DATA_DIR", base_dir / "data")).resolve()
        db_path = Path(os.getenv("MNP_CDX_DB_PATH", data_dir / "db" / "mnp_cdx.duckdb")).resolve()
        mapping_path = Path(
            os.getenv("MNP_CDX_MAPPING_PATH", base_dir / "config" / "operator_mapping.yml")
        ).resolve()
        return cls(base_dir=base_dir, data_dir=data_dir, db_path=db_path, mapping_path=mapping_path)
