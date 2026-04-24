"""
NEXUS Finance Pro -- Financial Ratios Dashboard
35+ indicatori con upload istantaneo + form manuale.
"""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import io
from engine.financial_ratios import (
    calculate_all_ratios, INDUSTRY_BENCHMARKS, REQUIRED_FIELDS, OPTIONAL_FIELDS
)
from utils.pdf_export import generate_full_report
from utils.file_parser import (
    get_ratios_template_bytes, get_ratios_template_excel, parse_ratios_file
)


def _gauge(value: float, title: str) -> go.Figure:
    color = "#00C853" if value >= 75 else ("#FFD600" if value >= 40 else "#D50000")
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={"text": title, "font": {"size": 14}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1},
            "bar": {"color": color},
            "steps": [
                {"range": [0, 40], "color": "#FFEBEE"},
                {"range": [40, 70], "color": "#FFF9C4"},
                {"range": [70, 100], "color": "#E8F5E9"},
            ],
        },
        number={"suffix": "/100", "font": {"size": 20}},
    ))
    fig.update_layout(height=200, margin=dict(l=10, r=10, t=40, b=10))
    return fig


def _status_badge(status: str) -> str:
    return {"ok": "✅ OK", "warning": "⚠️ WARN", "danger": "🔴 CRIT"}.get(status, "--")


def _show_ratio_result(result, company_name, industry):
    """Mostra i risultati completi dei ratio."""
    # Header Score
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Health Score", f"{result.overall_score:.0f}/100", result.health_label)
    ok_count = sum(sum(1 for r in c.ratios if r.status == "ok") for c in result.categories)
    warn_count = sum(sum(1 for r in c.ratios if r.status == "warning") for c in result.categories)
    danger_count = sum(sum(1 for r in c.ratios if r.status == "danger") for c in result.categories)
    total_count = ok_count + warn_count + danger_count
    col2.metric("✅ OK", ok_count)
    col3.metric("⚠️ Attenzione", warn_count)
    col4.metric("🔴 Critico", danger_count)

    # Gauge per categoria
    st.subheader("Score per Categoria")
    gauge_cols = st.columns(3)
    for i, cat in enumerate(result.categories[:6]):
        with gauge_cols[i % 3]:
            st.plotly_chart(_gauge(cat.score, f"{cat.icon} {cat.name}"),
                            use_container_width=True, key=f"gauge_auto_{i}")

    # Radar Chart
    st.subheader("Profilo Finanziario")
    cats = [c.name for c in result.categories]
    scores = [c.score for c in result.categories]
    fig_radar = go.Figure(go.Scatterpolar(
        r=scores + [scores[0]], theta=cats + [cats[0]],
        fill="toself", fillcolor="rgba(13,71,161,0.2)",
        line=dict(color="rgb(13,71,161)", width=2), name=company_name or "Azienda",
    ))
    fig_radar.add_trace(go.Scatterpolar(
        r=[75]*len(cats) + [75], theta=cats + [cats[0]],
        fill="toself", fillcolor="rgba(0,150,136,0.1)",
        line=dict(color="rgb(0,150,136)", width=1, dash="dash"),
        name=f"Benchmark {industry}",
    ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True, height=400
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    # Dettaglio per categoria
    st.subheader("Dettaglio Indicatori")
    for cat in result.categories:
        with st.expander(f"{cat.icon} {cat.name}  —  Score: {cat.score:.0f}/100", expanded=False):
            rows = []
            for r in cat.ratios:
                delta = None
                if r.benchmark and r.value:
                    diff_pct = (r.value - r.benchmark) / abs(r.benchmark) * 100 if r.benchmark != 0 else 0
                    delta = f"{diff_pct:+.1f}% vs benchmark"
                rows.append({
                    "Stato": _status_badge(r.status),
                    "Indicatore": r.name,
                    "Valore": r.formatted,
                    "Benchmark": r.benchmark_formatted,
                    "Vs Benchmark": delta or "--",
                    "Descrizione": r.description,
                })
            if rows:
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # Alert e Strengths
    col1, col2 = st.columns(2)
    with col1:
        if result.key_alerts:
            st.subheader("⚠️ Alert Principali")
            for alert in result.key_alerts:
                st.warning(alert)
    with col2:
        if result.strengths:
            st.subheader("💪 Punti di Forza")
            for s in result.strengths:
                st.success(s)

    # Bar chart vs benchmark
    st.subheader("Confronto vs Benchmark di Settore")
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


def render_financial_ratios():
    st.title("Ratio Analysis — 35+ Indicatori Finanziari")

    erp_data = st.session_state.get("erp_data", {})

    # ================================================================
    # ⚡ CARICA & ANALIZZA — UPLOAD UNICO + RISULTATI ISTANTANEI
    # ================================================================
    st.markdown("""
    <div style="background:linear-gradient(135deg,#004D40,#00695C);padding:20px 25px;border-radius:12px;margin-bottom:16px;">
        <h3 style="color:white;margin:0;">⚡ Carica & Analizza</h3>
        <p style="color:#B2DFDB;margin:6px 0 0 0;font-size:0.9rem;">
            Carica il tuo bilancio CSV o Excel → 35+ ratio istantanei senza compilare nulla
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_up, col_t1, col_t2 = st.columns([3, 1, 1])
    with col_up:
        uploaded = st.file_uploader(
            "Carica CSV o Excel",
            type=["csv", "xlsx", "xls"],
            key="ratios_upload",
            label_visibility="collapsed",
            help="Usa il template per il formato corretto"
        )
    with col_t1:
        st.download_button("📥 Template CSV", data=get_ratios_template_bytes(),
            file_name="template_ratios.csv", mime="text/csv", use_container_width=True)
    with col_t2:
        try:
            st.download_button("📥 Template Excel", data=get_ratios_template_excel(),
                file_name="template_ratios.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True)
        except Exception:
            pass

    file_data = None
    if uploaded:
        parsed = parse_ratios_file(uploaded)
        if parsed["success"]:
            file_data = parsed
            nome = parsed.get("nome_azienda", "Azienda")
            st.success(f"✅ **{nome}** — Dati importati! Analisi qui sotto ↓")

            data_in = {
                "total_assets": parsed.get("total_assets", 1) or 1,
                "total_liabilities": parsed.get("total_liabilities", 0),
                "equity": parsed.get("equity", 0),
                "current_assets": parsed.get("current_assets", 0),
                "current_liabilities": parsed.get("current_liabilities", 1) or 1,
                "revenue": parsed.get("revenue", 1) or 1,
                "ebit": parsed.get("ebit", 0),
                "ebitda": parsed.get("ebitda", 0),
                "net_income": parsed.get("net_income", 0),
                "depreciation": parsed.get("depreciation", 0),
                "interest_expense": parsed.get("interest_expense", 0),
                "inventory": parsed.get("inventory", 0),
                "accounts_receivable": parsed.get("accounts_receivable", 0),
                "accounts_payable": parsed.get("accounts_payable", 0),
                "retained_earnings": parsed.get("retained_earnings", 0),
                "cash": parsed.get("cash", 0),
                "long_term_debt": parsed.get("long_term_debt", 0),
            }

            ratios_result = calculate_all_ratios(data_in, industry="Manifatturiero")
            st.markdown("#### 📊 Risultato Analisi Automatica")
            _show_ratio_result(ratios_result, nome, "Manifatturiero")

            # Export diretto
            st.divider()
            rows_export = []
            for cat in ratios_result.categories:
                for r in cat.ratios:
                    rows_export.append({
                        "Categoria": cat.name, "Indicatore": r.name,
                        "Valore": r.formatted, "Benchmark": r.benchmark_formatted,
                        "Status": _status_badge(r.status),
                    })
            df_exp = pd.DataFrame(rows_export)
            buf = io.BytesIO()
            df_exp.to_excel(buf, index=False)
            st.download_button("📥 Esporta Excel risultati", data=buf.getvalue(),
                file_name=f"ratios_{nome}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True)
        else:
            st.error(f"❌ Errore nel file: {parsed['error']}")
            st.info("💡 Scarica il **Template CSV** per il formato corretto e riprova.")

    st.divider()

    # ================================================================
    # 📝 FORM MANUALE
    # ================================================================
    st.markdown("### 📝 Inserimento Manuale (opzionale)")
    st.caption("I campi si precompilano se hai caricato un file sopra")

    merged = {**erp_data, **(file_data or {})}
    company_name = merged.get("nome_azienda", st.session_state.get("erp_company", ""))

    with st.sidebar:
        st.subheader("Parametri Analisi")
        industry = st.selectbox("Settore di riferimento",
                                list(INDUSTRY_BENCHMARKS.keys()), index=0)

    with st.expander(
        "Inserisci / modifica dati di bilancio" if not merged else "Modifica dati (precompilati da file)",
        expanded=not bool(merged)
    ):
        company_name = st.text_input("Nome Azienda", value=company_name, key="ra_company")
        all_labels = {**REQUIRED_FIELDS, **OPTIONAL_FIELDS}
        data = {}
        cols = st.columns(3)
        for i, (key, label) in enumerate(all_labels.items()):
            default = float(merged.get(key, 0))
            with cols[i % 3]:
                data[key] = st.number_input(label, value=default, format="%.2f", key=f"ra_{key}")

    if st.button("📊 CALCOLA TUTTI I RATIO", type="primary", use_container_width=True):
        # Safe values per calcolo
        safe_data = data.copy()
        if safe_data.get("total_assets", 0) == 0:
            safe_data["total_assets"] = 1
        if safe_data.get("current_liabilities", 0) == 0:
            safe_data["current_liabilities"] = 1
        if safe_data.get("revenue", 0) == 0:
            safe_data["revenue"] = 1

        result = calculate_all_ratios(safe_data, industry)
        st.markdown("#### 📊 Risultato Analisi Manuale")
        _show_ratio_result(result, company_name, industry)

        # Export PDF
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📄 Genera Report PDF", type="primary", use_container_width=True, key="pdf_ratio"):
                with st.spinner("Generazione PDF..."):
                    try:
                        pdf_bytes = generate_full_report(
                            company_name=company_name or "Azienda",
                            ratio_result=result, raw_data=data,
                        )
                        st.download_button("📥 Scarica Report PDF", data=pdf_bytes,
                            file_name=f"ratios_{company_name or 'report'}.pdf",
                            mime="application/pdf", use_container_width=True)
                    except Exception as e:
                        st.error(f"Errore PDF: {e}")
        with col2:
            rows_export = []
            for cat in result.categories:
                for r in cat.ratios:
                    rows_export.append({
                        "Categoria": cat.name, "Indicatore": r.name,
                        "Valore": r.formatted, "Benchmark": r.benchmark_formatted,
                        "Status": _status_badge(r.status), "Descrizione": r.description,
                    })
            df_exp = pd.DataFrame(rows_export)
            buf = io.BytesIO()
            df_exp.to_excel(buf, index=False)
            st.download_button("📥 Esporta Excel risultati", data=buf.getvalue(),
                file_name=f"ratios_{company_name or 'export'}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True)
