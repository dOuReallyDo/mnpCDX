"""Pydantic schemas for API responses."""

from __future__ import annotations

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str


class IngestResponse(BaseModel):
    file_id: int | None
    filename: str
    checksum: str
    inserted_records: int
    monthly_records: int
    daily_records: int
    skipped_duplicate: bool
    warnings: list[str]
