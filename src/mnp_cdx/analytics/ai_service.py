"""Optional AI summary helper.

This module is intentionally resilient: if provider SDK is unavailable,
it returns deterministic fallback text.
"""

from __future__ import annotations

from dataclasses import dataclass
import json


@dataclass
class AISummaryInput:
    operator: str
    period_type: str
    snapshot: dict
    top_donors: list[dict]
    top_recipients: list[dict]


class AISummaryService:
    def __init__(self, provider: str = "none", api_key: str | None = None, model: str | None = None) -> None:
        self.provider = provider.lower()
        self.api_key = api_key
        self.model = model

    def summarize(self, payload: AISummaryInput) -> str:
        if not self.api_key or self.provider == "none":
            return self._fallback(payload)

        # MVP: fallback-first to avoid blocking operations.
        # External provider invocation can be added behind this interface.
        return self._fallback(payload)

    def _fallback(self, payload: AISummaryInput) -> str:
        s = payload.snapshot
        direction = "positivo" if s.get("net_balance", 0) > 0 else "negativo"
        lines = [
            f"- Trend complessivo: {direction}",
            f"- Operatore focus: {payload.operator} ({payload.period_type})",
            f"- Net balance totale: {s.get('net_balance', 0):,.0f}",
            "- Nota: summary generato in modalita fallback deterministica (no external LLM).",
        ]
        return "\n".join(lines)
