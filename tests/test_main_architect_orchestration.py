from pathlib import Path

from mnp_cdx.orchestration.main_architect import summarize_program


def test_summarize_program_includes_backlog_and_team() -> None:
    backlog_path = Path("docs/agent_backlog.yaml")
    team_path = Path("docs/agent_team_manifest.yaml")

    summary = summarize_program(backlog_path, team_path)

    assert "Program: mnpCDX Next MVP delivery" in summary
    assert "Main Architect: Main Architect" in summary
    assert "v1.0.0-mvp" in summary
    assert "AI Governance Agent" in summary
