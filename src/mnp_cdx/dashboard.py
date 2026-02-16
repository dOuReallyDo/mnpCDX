"""Streamlit dashboard entrypoint."""

from __future__ import annotations

import plotly.express as px
import streamlit as st

from mnp_cdx.analytics.ai_service import AISummaryInput, AISummaryService
from mnp_cdx.analytics.kpi import AnalyticsService
from mnp_cdx.config import Settings
from mnp_cdx.db.repository import DBRepository


def run_dashboard() -> None:
    st.set_page_config(page_title="mnpCDX Dashboard", page_icon="📡", layout="wide")
    st.title("mnpCDX Dashboard")

    settings = Settings.load()
    repo = DBRepository(settings.db_path)
    repo.init_schema()
    analytics = AnalyticsService(repo)

    operators = analytics.operators()
    if not operators:
        st.info("Nessun dato disponibile. Esegui prima ingest da CLI/API.")
        return

    operator = st.sidebar.selectbox("Operatore", operators, index=operators.index("WINDTRE") if "WINDTRE" in operators else 0)
    period = st.sidebar.radio("Granularity", ["MONTHLY", "DAILY"], horizontal=True)

    snapshot = analytics.kpi_snapshot(operator, period)
    c1, c2, c3 = st.columns(3)
    c1.metric("Port-In", f"{snapshot['total_port_in']:,.0f}")
    c2.metric("Port-Out", f"{snapshot['total_port_out']:,.0f}")
    c3.metric("Net", f"{snapshot['net_balance']:,.0f}")

    trend = analytics.trend(operator, period)
    if not trend.empty:
        fig = px.line(trend, x="period_date", y="net_flow", title=f"Net Flow - {operator}")
        fig.add_hline(y=0, line_dash="dash", line_color="gray")
        st.plotly_chart(fig, use_container_width=True)

    d1, d2 = st.columns(2)
    with d1:
        st.subheader("Top Donors")
        st.dataframe(analytics.top_donors(operator, period, limit=10), use_container_width=True)
    with d2:
        st.subheader("Top Recipients")
        st.dataframe(analytics.top_recipients(operator, period, limit=10), use_container_width=True)

    st.subheader("Data Quality")
    st.json(analytics.quality_report())

    st.subheader("AI Summary (fallback-safe)")
    if st.button("Generate Summary"):
        ai = AISummaryService(provider="none")
        payload = AISummaryInput(
            operator=operator,
            period_type=period,
            snapshot=snapshot,
            top_donors=analytics.top_donors(operator, period, limit=5).to_dict(orient="records"),
            top_recipients=analytics.top_recipients(operator, period, limit=5).to_dict(orient="records"),
        )
        st.markdown(ai.summarize(payload))


if __name__ == "__main__":  # pragma: no cover
    run_dashboard()
