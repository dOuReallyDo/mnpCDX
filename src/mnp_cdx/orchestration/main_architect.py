"""Main Architect orchestration helper.

This module documents and validates the multi-agent delivery plan.
"""

from __future__ import annotations

from pathlib import Path
import yaml


def load_backlog(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


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


if __name__ == "__main__":  # pragma: no cover
    backlog_path = Path("docs/agent_backlog.yaml")
    print(summarize_backlog(backlog_path))
