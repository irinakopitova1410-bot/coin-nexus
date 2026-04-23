"""
NEXUS Finance Pro — Financial Ratios Dashboard
35+ indicatori finanziari con benchmark, score, alert e export PDF.
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import io
from engine.financial_ratios import (
    calculate_all_ratios, INDUSTRY_BENCHMARKS, REQUIRED_FIELDS, OPTIONAL_FIELDS
)
from utils.pdf_export import generate_full_report


def _gauge(value: float, title: str, max_val: float = 100) -> go.Figure:
    color = "#00C853" if value >= 75 else ("#FFD600" if value >= 40 else "#D50000")
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={"text": title, "font": {"size": 14}},
        gauge={
            "axis": {"range": [0, max_val], "tickwidth": 1},
            "bar": {"color": color},
            "steps": [
                {"range": [0, 40], "color": "#FFEBEE"},
                {"range": [40, 70], "color": "#FFF9C4"},
                {"range": [70, 100], "color": "#E8F5E9"},
            ],
            "threshold": {"line": {"color": "black", "width": 3}, "value": value},
        },
        number={"suffix": "/100", "font": {"size": 20}},
    ))
    fig.update_layout(height=200, margin=dict(l=10, r=10, t=40, b=10))
    return fig


def _status_badge(status: str) -> str:
    return {"ok": "🟢", "warning": "🟡", "danger": "🔴"}.get(status, "⚪")


def render_financial_ratios():
    st.title("📊 Ratio Analysis — 35+ Indicatori Finanziari")

    # ── Dati da ERP import o inserimento manuale ──────────────────────────────
    erp_data = st.session_state.get("erp_data", {})
    company_name = st.session_state.get("erp_company", "")

    with st.sidebar:
        st.subheader("⚙️ Parametri Analisi")
        industry = st.selectbox("Settore di riferimento",
                                list(INDUSTRY_BENCHMARKS.keys()), index=0)
        if erp_data:
            st.success("✅ Dati da ERP import caricati")
            if st.button("🔄 Inserimento manuale"):
                st.session_state.pop("erp_data", None)
                st.rerun()

    with st.expander(
        "📋 Inserisci dati di bilancio" if not erp_data else "📋 Modifica dati di bilancio",
        expanded=not bool(erp_data)
    ):
        company_name = st.text_input("Nome Azienda", value=company_name or "", key="ra_company")

        all_labels = {**REQUIRED_FIELDS, **OPTIONAL_FIELDS}
        data = {}
        cols = st.columns(3)
        for i, (key, label) in enumerate(all_labels.items()):
            default = float(erp_data.get(key, 0))
            with cols[i % 3]:
                data[key] = st.number_input(label, value=default, format="%.2f",
                                            key=f"ra_{key}")

    # ── Calcolo ───────────────────────────────────────────────────────────────
    result = calculate_all_ratios(data, industry)

    # ── Header Score ──────────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🏆 Health Score", f"{result.overall_score:.0f}/100", result.health_label)

    ok_count = sum(sum(1 for r in c.ratios if r.status == "ok") for c in result.categories)
    warn_count = sum(sum(1 for r in c.ratios if r.status == "warning") for c in result.categories)
    danger_count = sum(sum(1 for r in c.ratios if r.status == "danger") for c in result.categories)
    total_count = ok_count + warn_count + danger_count

    col2.metric("🟢 OK", ok_count, f"{ok_count/total_count*100:.0f}%" if total_count else "")
    col3.metric("🟡 Attenzione", warn_count, f"{warn_count/total_count*100:.0f}%" if total_count else "")
    col4.metric("🔴 Critico", danger_count, f"{danger_count/total_count*100:.0f}%" if total_count else "")

    # ── Gauge per categoria ────────────────────────────────────────────────────
    st.subheader("📈 Score per Categoria")
    gauge_cols = st.columns(3)
    for i, cat in enumerate(result.categories[:6]):
        with gauge_cols[i % 3]:
            st.plotly_chart(_gauge(cat.score, f"{cat.icon} {cat.name}"),
                            use_container_width=True, key=f"gauge_{i}")

    # ── Radar Chart ────────────────────────────────────────────────────────────
    st.subheader("🕸️ Profilo Finanziario")
    cats = [c.name for c in result.categories]
    scores = [c.score for c in result.categories]
    fig_radar = go.Figure(go.Scatterpolar(
        r=scores + [scores[0]],
        theta=cats + [cats[0]],
        fill="toself",
        fillcolor="rgba(13, 71, 161, 0.2)",
        line=dict(color="rgb(13, 71, 161)", width=2),
        name=company_name or "Azienda",
    ))
    # Benchmark
    bm_scores = [75] * len(cats)
    fig_radar.add_trace(go.Scatterpolar(
        r=bm_scores + [bm_scores[0]],
        theta=cats + [cats[0]],
        fill="toself",
        fillcolor="rgba(0, 150, 136, 0.1)",
        line=dict(color="rgb(0, 150, 136)", width=1, dash="dash"),
        name=f"Benchmark {industry}",
    ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True, height=400
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    # ── Dettaglio per categoria ─────────────────────────────────────────────
    st.subheader("📋 Dettaglio Indicatori")

    for cat in result.categories:
        score_color = "#00C853" if cat.score >= 70 else ("#FFD600" if cat.score >= 40 else "#D50000")
        with st.expander(f"{cat.icon} {cat.name}  —  Score: {cat.score:.0f}/100", expanded=False):
            rows = []
            for r in cat.ratios:
                delta = None
                if r.benchmark and r.value:
                    diff_pct = (r.value - r.benchmark) / abs(r.benchmark) * 100 if r.benchmark != 0 else 0
                    delta = f"{diff_pct:+.1f}% vs benchmark"
                rows.append({
                    "": _status_badge(r.status),
                    "Indicatore": r.name,
                    "Valore": r.formatted,
                    "Benchmark": r.benchmark_formatted,
                    "Vs Benchmark": delta or "—",
                    "Descrizione": r.description,
                })
            if rows:
                df_cat = pd.DataFrame(rows)
                st.dataframe(df_cat, use_container_width=True, hide_index=True)

    # ── Alert e Strengths ─────────────────────────────────────────────────────
    col1, col2 = st.columns(2)
    with col1:
        if result.key_alerts:
            st.subheader("⚠️ Alert Principali")
            for alert in result.key_alerts:
                st.warning(alert)
    with col2:
        if result.strengths:
            st.subheader("✅ Punti di Forza")
            for s in result.strengths:
                st.success(s)

    # ── Bar chart confronto vs benchmark ──────────────────────────────────────
    st.subheader("📊 Confronto vs Benchmark di Settore")
    all_ratios_flat = [r for cat in result.categories for r in cat.ratios
                       if r.benchmark is not None and r.value != 0]
    if all_ratios_flat:
        df_bm = pd.DataFrame({
            "Indicatore": [r.name for r in all_ratios_flat],
            "Azienda": [r.value * (100 if r.unit == "%" else 1) for r in all_ratios_flat],
            "Benchmark": [r.benchmark * (100 if r.unit == "%" else 1) for r in all_ratios_flat],
        }).head(12)
        fig_bar = go.Figure()
        fig_bar.add_bar(name="Azienda", x=df_bm["Indicatore"], y=df_bm["Azienda"],
                        marker_color="#0D47A1")
        fig_bar.add_bar(name=f"Benchmark ({industry})", x=df_bm["Indicatore"],
                        y=df_bm["Benchmark"], marker_color="#009688", opacity=0.7)
        fig_bar.update_layout(barmode="group", height=380, xaxis_tickangle=-30)
        st.plotly_chart(fig_bar, use_container_width=True)

    # ── Export PDF ───────────────────────────────────────────────────────────
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📄 Genera Report PDF Completo", type="primary", use_container_width=True):
            with st.spinner("Generazione PDF in corso..."):
                try:
                    pdf_bytes = generate_full_report(
                        company_name=company_name or "Azienda",
                        ratio_result=result,
                        raw_data=data,
                    )
                    st.download_button(
                        "⬇️ Scarica Report PDF",
                        data=pdf_bytes,
                        file_name=f"nexus_ratio_{company_name or 'report'}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )
                    st.success("✅ PDF generato!")
                except Exception as e:
                    st.error(f"Errore PDF: {e}")

    with col2:
        # Export Excel
        rows_export = []
        for cat in result.categories:
            for r in cat.ratios:
                rows_export.append({
                    "Categoria": cat.name,
                    "Indicatore": r.name,
                    "Valore": r.formatted,
                    "Benchmark": r.benchmark_formatted,
                    "Status": _status_badge(r.status),
                    "Descrizione": r.description,
                    "Formula": r.formula,
                })
        df_exp = pd.DataFrame(rows_export)
        buf = io.BytesIO()
        df_exp.to_excel(buf, index=False)
        st.download_button(
            "📊 Esporta Excel",
            data=buf.getvalue(),
            file_name=f"nexus_ratios_{company_name or 'export'}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
