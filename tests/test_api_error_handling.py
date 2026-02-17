import re

import pytest
from fastapi import HTTPException

from mnp_cdx.api.app import _raise_internal_error


def test_raise_internal_error_for_template_analyze_has_reference_code() -> None:
    with pytest.raises(HTTPException) as captured:
        _raise_internal_error("Analisi template", RuntimeError("boom"))

    assert captured.value.status_code == 500
    detail = str(captured.value.detail)
    assert detail.startswith("Analisi template fallita per errore interno (ref: ")
    assert re.search(r"ref: [a-f0-9]{8}\)", detail)


def test_raise_internal_error_for_template_ingest_has_reference_code() -> None:
    with pytest.raises(HTTPException) as captured:
        _raise_internal_error("Ingestion template", RuntimeError("boom"))

    assert captured.value.status_code == 500
    detail = str(captured.value.detail)
    assert detail.startswith("Ingestion template fallita per errore interno (ref: ")
    assert re.search(r"ref: [a-f0-9]{8}\)", detail)
