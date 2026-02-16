from pathlib import Path

from mnp_cdx.ingest.operator_mapping import OperatorMapper


def test_operator_alias_resolution() -> None:
    mapper = OperatorMapper(Path("config/operator_mapping.yml"))
    vod = mapper.resolve("VOD")
    assert vod.canonical_name == "VODAFONE"

    poste = mapper.resolve("poste")
    assert poste.canonical_name == "POSTE MOBILE"

    unknown = mapper.resolve("SOME NEW MVNO")
    assert unknown.group_name == "UNMAPPED"
