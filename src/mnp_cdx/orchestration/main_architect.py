"""Main Architect orchestration helpers.

Utilities to load and validate team/backlog manifests used by the
multi-agent delivery process.
"""

from __future__ import annotations

from pathlib import Path

import yaml


class OrchestrationManifestError(ValueError):
    """Raised when backlog/team manifests are invalid."""


def _load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        payload = yaml.safe_load(fh) or {}
    if not isinstance(payload, dict):
        raise OrchestrationManifestError(f"Invalid YAML root in {path}")
    return payload


def load_backlog(path: Path) -> dict:
    payload = _load_yaml(path)
    if "milestones" not in payload:
        raise OrchestrationManifestError("Backlog missing 'milestones'")
    return payload


def load_team_manifest(path: Path) -> dict:
    payload = _load_yaml(path)
    if "agents" not in payload:
        raise OrchestrationManifestError("Team manifest missing 'agents'")
    return payload


def summarize_backlog(path: Path) -> str:
    payload = load_backlog(path)
    lines: list[str] = []
    lines.append(f"Program: {payload.get('program', 'unknown')}")
    lines.append(f"Coordinator: {payload.get('coordinator', 'unknown')}")

    for milestone in payload.get("milestones", []):
        lines.append(f"- {milestone['version']}: {milestone['objective']}")
        for task in milestone.get("tasks", []):
            lines.append(f"  * {task['owner']}: {task['item']}")

    return "\n".join(lines)


def summarize_team_manifest(path: Path) -> str:
    payload = load_team_manifest(path)
    lines: list[str] = []
    lines.append(f"Program: {payload.get('program', 'unknown')}")
    lines.append(f"Main Architect: {payload.get('main_architect', 'unknown')}")
    lines.append(f"Status: {payload.get('status', 'unknown')}")

    for agent in payload.get("agents", []):
        lines.append(f"- {agent['name']}: {agent['domain']}")

    return "\n".join(lines)


def summarize_program(backlog_path: Path, team_manifest_path: Path) -> str:
    backlog_text = summarize_backlog(backlog_path)
    team_text = summarize_team_manifest(team_manifest_path)
    return f"{backlog_text}\n\n{team_text}"


if __name__ == "__main__":  # pragma: no cover
    backlog_path = Path("docs/agent_backlog.yaml")
    team_path = Path("docs/agent_team_manifest.yaml")
    print(summarize_program(backlog_path, team_path))
