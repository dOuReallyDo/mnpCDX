"""Operator alias mapping utilities."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


def _normalize_name(name: str | None) -> str:
    if not name:
        return ""
    return str(name).upper().strip().replace("-", " ").replace("  ", " ")


@dataclass
class OperatorInfo:
    canonical_name: str
    group_name: str | None
    op_type: str | None


class OperatorMapper:
    def __init__(self, mapping_path: Path) -> None:
        self.mapping_path = Path(mapping_path)
        self.alias_map: dict[str, OperatorInfo] = {}
        self._load()

    def _load(self) -> None:
        with self.mapping_path.open("r", encoding="utf-8") as fh:
            payload = yaml.safe_load(fh) or {}

        for op in payload.get("operators", []):
            info = OperatorInfo(
                canonical_name=op["canonical_name"],
                group_name=op.get("group_name"),
                op_type=op.get("type"),
            )
            aliases = op.get("aliases", []) + [op["canonical_name"]]
            for alias in aliases:
                self.alias_map[_normalize_name(alias)] = info

    def resolve(self, raw_name: str) -> OperatorInfo:
        normalized = _normalize_name(raw_name)
        if normalized in self.alias_map:
            return self.alias_map[normalized]

        # fallback for combined names where left side is known
        if "+" in normalized:
            left = normalized.split("+", 1)[0].strip()
            if left in self.alias_map:
                return self.alias_map[left]

        # fallback unknown
        return OperatorInfo(
            canonical_name=normalized or "UNKNOWN",
            group_name="UNMAPPED",
            op_type="UNKNOWN",
        )
