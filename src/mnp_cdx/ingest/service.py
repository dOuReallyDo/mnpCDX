"""Ingestion application service."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from mnp_cdx.db.repository import DBRepository
from mnp_cdx.ingest.operator_mapping import OperatorMapper
from mnp_cdx.ingest.parser import MNPParser


@dataclass
class IngestResult:
    file_id: int | None
    filename: str
    checksum: str
    inserted_records: int
    monthly_records: int
    daily_records: int
    skipped_duplicate: bool
    warnings: list[str]


class IngestionService:
    def __init__(
        self,
        repo: DBRepository,
        parser: MNPParser,
        mapper: OperatorMapper,
        parser_version: str = "cdx-0.3.0",
    ) -> None:
        self.repo = repo
        self.parser = parser
        self.mapper = mapper
        self.parser_version = parser_version

    def ingest_file(self, file_path: str | Path, force: bool = False) -> IngestResult:
        file_path = Path(file_path)
        file_id = file_path.name

        parsed_rows, summary = self.parser.parse(file_path, file_id=file_id)

        if self.repo.file_exists(summary.checksum):
            if not force:
                return IngestResult(
                    file_id=None,
                    filename=summary.filename,
                    checksum=summary.checksum,
                    inserted_records=0,
                    monthly_records=summary.monthly_records,
                    daily_records=summary.daily_records,
                    skipped_duplicate=True,
                    warnings=summary.warnings,
                )
            self.repo.delete_file_and_flows_by_checksum(summary.checksum)

        ingest_file_id = self.repo.insert_ingest_file(
            filename=summary.filename,
            checksum=summary.checksum,
            parser_version=self.parser_version,
        )

        fact_rows: list[dict] = []
        for row in parsed_rows:
            donor = self.mapper.resolve(row["donor_raw"])
            recipient = self.mapper.resolve(row["recipient_raw"])

            donor_id = self.repo.get_or_create_operator(
                donor.canonical_name, donor.group_name, donor.op_type
            )
            recipient_id = self.repo.get_or_create_operator(
                recipient.canonical_name, recipient.group_name, recipient.op_type
            )

            if donor_id == recipient_id:
                continue

            fact_rows.append(
                {
                    "file_id": ingest_file_id,
                    "period_type": row["period_type"],
                    "period_date": row["period_date"],
                    "donor_operator_id": donor_id,
                    "recipient_operator_id": recipient_id,
                    "value": float(row["value"]),
                    "sheet_name": row["sheet_name"],
                    "quality_flag": row["quality_flag"],
                    "donor_raw": row["donor_raw"],
                    "recipient_raw": row["recipient_raw"],
                }
            )

        df = pd.DataFrame(fact_rows)
        inserted = self.repo.insert_flow_dataframe(df)
        self.repo.update_ingest_status(ingest_file_id, "OK", inserted)

        return IngestResult(
            file_id=ingest_file_id,
            filename=summary.filename,
            checksum=summary.checksum,
            inserted_records=inserted,
            monthly_records=summary.monthly_records,
            daily_records=summary.daily_records,
            skipped_duplicate=False,
            warnings=summary.warnings,
        )
