"""Markdown report generation."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from mnp_cdx.analytics.kpi import AnalyticsService


def generate_markdown_report(
    analytics: AnalyticsService,
    operator: str,
    period_type: str,
    output_path: Path,
) -> Path:
    snapshot = analytics.kpi_snapshot(operator, period_type)
    trend_df = analytics.trend(operator, period_type)
    top_donors = analytics.top_donors(operator, period_type, limit=5)
    top_recipients = analytics.top_recipients(operator, period_type, limit=5)

    lines: list[str] = []
    lines.append(f"# mnpCDX Report - {operator}")
    lines.append("")
    lines.append(f"Generated: {datetime.utcnow().isoformat()}Z")
    lines.append(f"Period type: {period_type}")
    lines.append("")

    lines.append("## Executive Summary")
    lines.append(f"- Total Port-In: {snapshot['total_port_in']:,.0f}")
    lines.append(f"- Total Port-Out: {snapshot['total_port_out']:,.0f}")
    lines.append(f"- Net Balance: {snapshot['net_balance']:,.0f}")
    lines.append(f"- Latest Net: {snapshot['latest_net']:,.0f} ({snapshot['latest_period']})")
    lines.append("")

    lines.append("## Top Donors")
    lines.append("| Donor | Volume |")
    lines.append("|---|---:|")
    for _, row in top_donors.iterrows():
        lines.append(f"| {row['donor_operator']} | {row['total_in']:,.0f} |")
    lines.append("")

    lines.append("## Top Recipients")
    lines.append("| Recipient | Volume |")
    lines.append("|---|---:|")
    for _, row in top_recipients.iterrows():
        lines.append(f"| {row['recipient_operator']} | {row['total_out']:,.0f} |")
    lines.append("")

    lines.append("## Trend (last 12 periods)")
    lines.append("| Date | Port-In | Port-Out | Net |")
    lines.append("|---|---:|---:|---:|")
    tail = trend_df.tail(12)
    for _, row in tail.iterrows():
        lines.append(
            f"| {row['period_date']} | {row['port_in']:,.0f} | {row['port_out']:,.0f} | {row['net_flow']:,.0f} |"
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path
