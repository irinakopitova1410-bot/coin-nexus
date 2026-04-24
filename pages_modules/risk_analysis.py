"""
NEXUS Finance Pro — Altman Z-Score Analysis
3 modelli (1968/1983/1995), probabilità fallimento, proiezioni, PDF export.
"""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import io
from engine.calculations import altman_z_original, altman_z_prime, altman_z_doubleprime
from engine.financial_ratios import calculate_all_ratios
from services.db import save_risk_analysis
from utils.file_parser import get_zscore_template_bytes
from services.erp_connectors import parse_erp_file


def _render_gauge(z_score: float, safe: float, grey: float) -> go.Figure:
    color = "#00C853" if z_score >= safe else ("#FFD600" if z_score >= grey else "#D50000")
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=z_score,
        title={"text": "Z-Score", "font": {"size": 16}},
        gauge={
            "axis": {"range": [0, max(safe * 1.5, z_score * 1.2)], "tickwidth": 1},
            "bar": {"color": color, "thickness": 0.25},
            "steps": [
                {"range": [0, grey], "color": "#FFEBEE"},
                {"range": [grey, safe], "color": "#FFF9C4"},
                {"range": [safe, max(safe * 1.5, z_score * 1.2)], "color": "#E8F5E9"},
            ],
            "threshold": {"line": {"color": "darkblue", "width": 3}, "value": safe},
        },
        number={"font": {"size": 36, "color": color}},
    ))
    fig.update_layout(height=280, margin=dict(l=20, r=20, t=60, b=20))
    return fig


def render_risk_analysis():
    st.title("🎯 Altman Z-Score — Probabilità di Fallimento")
    st.markdown("Tre modelli ufficiali di Altman per aziende quotate, private e di servizi.")

    erp_data = st.session_state.get("erp_data", {})

    # ── Selezione modello ───────────────────────────────────────────────────────
    col_model, col_info = st.columns([2, 1])
    with col_model:
        model = st.selectbox("Seleziona il modello Z-Score:", [
            "Z'-Score (1983) — Aziende Private [CONSIGLIATO]",
            "Z-Score (1968) — Aziende Quotate Manifatturiere",
            "Z''-Score (1995) — Servizi / Non Manifatturiere",
        ])
    with col_info:
        st.info("""
        📌 **Guida modelli:**
        - **Z'** → SRL, SPA non quotate
        - **Z** → SPA quotate in borsa
        - **Z''** → Servizi, retail, tech
        """)

    # ── Upload file ─────────────────────────────────────────────────────────────
    with st.expander("📤 Import da file CSV/Excel o ERP", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            tpl = get_zscore_template_bytes()
            st.download_button("⬇️ Template CSV", data=tpl,
                               file_name="template_zscore.csv", mime="text/csv")
        with c2:
            up = st.file_uploader("Carica CSV/Excel", type=["csv", "xlsx", "xls"],
                                   key="zscore_upload")
            if up:
                result = parse_erp_file(up.read(), up.name)
                if result.success and result.data:
                    st.session_state["erp_data"] = result.data
                    erp_data = result.data
                    st.success(f"✅ Caricati {len(result.data)} campi da {result.erp_type}")
                    st.rerun()

    # ── Dati di input ──────────────────────────────────────────────────────────
    with st.form("zscore_form"):
        st.subheader("📋 Dati di Bilancio")
        if erp_data:
            st.success("✅ Dati precaricati da ERP Import — verifica e modifica se necessario")

        company_name = st.text_input("Nome Azienda",
                                      value=st.session_state.get("erp_company", ""))
        industry = st.selectbox("Settore (per benchmark)", 
                                ["Manifatturiero", "Commercio", "Servizi", "Costruzioni", "Tecnologia"])

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**📊 Stato Patrimoniale**")
            total_assets = st.number_input("Totale Attivo (EUR)", value=float(erp_data.get("total_assets", 0)), format="%.2f", key="zs_ta")
            total_liabilities = st.number_input("Totale Passivo (EUR)", value=float(erp_data.get("total_liabilities", 0)), format="%.2f", key="zs_tl")
            equity = st.number_input("Patrimonio Netto (EUR)", value=float(erp_data.get("equity", 0)), format="%.2f", key="zs_eq")
            current_assets = st.number_input("Attivo Corrente (EUR)", value=float(erp_data.get("current_assets", 0)), format="%.2f", key="zs_ca")
            current_liabilities = st.number_input("Passivo Corrente (EUR)", value=float(erp_data.get("current_liabilities", 0)), format="%.2f", key="zs_cl")

        with col2:
            st.markdown("**📈 Conto Economico**")
            revenue = st.number_input("Ricavi (EUR)", value=float(erp_data.get("revenue", 0)), format="%.2f", key="zs_rev")
            ebit = st.number_input("EBIT (EUR)", value=float(erp_data.get("ebit", 0)), format="%.2f", key="zs_ebit")
            net_income = st.number_input("Utile Netto (EUR)", value=float(erp_data.get("net_income", 0)), format="%.2f", key="zs_ni")
            depreciation = st.number_input("Ammortamenti (EUR)", value=float(erp_data.get("depreciation", 0)), format="%.2f", key="zs_dep")
            interest_expense = st.number_input("Oneri Finanziari (EUR)", value=float(erp_data.get("interest_expense", 0)), format="%.2f", key="zs_int")

        with col3:
            st.markdown("**🏦 Altri Dati**")
            retained_earnings = st.number_input("Riserve / Utili portati (EUR)", value=float(erp_data.get("retained_earnings", 0)), format="%.2f", key="zs_re")
            market_cap = st.number_input("Capitalizzazione di Borsa (EUR)\n[solo per modello 1968]", value=float(erp_data.get("market_cap", equity)), format="%.2f", key="zs_mc")
            inventory = st.number_input("Magazzino (EUR)", value=float(erp_data.get("inventory", 0)), format="%.2f", key="zs_inv")
            accounts_receivable = st.number_input("Crediti Commerciali (EUR)", value=float(erp_data.get("accounts_receivable", 0)), format="%.2f", key="zs_ar")
            accounts_payable = st.number_input("Debiti Commerciali (EUR)", value=float(erp_data.get("accounts_payable", 0)), format="%.2f", key="zs_ap")

        submitted = st.form_submit_button("🚀 CALCOLA Z-SCORE", type="primary", use_container_width=True)

    if not submitted:
        return

    if total_assets == 0:
        st.error("❌ Inserisci almeno il Totale Attivo")
        return

    # ── Calcolo ───────────────────────────────────────────────────────────────
    working_capital = current_assets - current_liabilities

    if "1968" in model:
        result = altman_z_original(working_capital, total_assets, retained_earnings,
                                    ebit, market_cap, total_liabilities, revenue)
    elif "1995" in model:
        result = altman_z_doubleprime(working_capital, total_assets, retained_earnings,
                                       ebit, equity, total_liabilities)
    else:
        result = altman_z_prime(working_capital, total_assets, retained_earnings,
                                 ebit, equity, total_liabilities, revenue)

    # ── Risultati ─────────────────────────────────────────────────────────────
    st.divider()

    col1, col2 = st.columns([1, 1])

    with col1:
        st.plotly_chart(
            _render_gauge(result.z_score, result.thresholds["safe"], result.thresholds["grey_low"]),
            use_container_width=True
        )

    with col2:
        st.metric("📍 Zona", result.zone_label)
        st.metric("📊 Z-Score", result.z_score)
        prob = result.bankruptcy_probability
        prob_delta = "BASSO" if prob < 20 else ("MEDIO" if prob < 50 else "ELEVATO")
        st.metric("💀 Probabilità Fallimento", f"{prob:.1f}%", prob_delta)
        st.metric("🏷️ Rating Equivalente", result.rating)

    # Alert zona
    if result.zone == "distress":
        st.error(f"🔴 **ZONA DI PERICOLO** — {result.recommendation}")
    elif result.zone == "grey":
        st.warning(f"🟡 **ZONA GRIGIA** — {result.recommendation}")
    else:
        st.success(f"🟢 **ZONA SICURA** — {result.recommendation}")

    # ── Variabili ──────────────────────────────────────────────────────────────
    st.subheader("📐 Variabili del Modello")
    df_vars = pd.DataFrame(list(result.variables.items()), columns=["Variabile", "Valore"])
    col1, col2 = st.columns([2, 1])
    with col1:
        st.dataframe(df_vars, use_container_width=True, hide_index=True)
    with col2:
        fig_bar = go.Figure(go.Bar(
            x=list(result.variables.values()),
            y=list(result.variables.keys()),
            orientation="h",
            marker_color=["#00C853" if v > 0 else "#D50000"
                          for v in result.variables.values()],
        ))
        fig_bar.update_layout(height=250, margin=dict(l=10, r=10, t=10, b=10),
                               showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)

    # ── Proiezioni ────────────────────────────────────────────────────────────
    st.subheader("📈 Proiezioni Z-Score (4 anni)")
    df_proj = pd.DataFrame(result.projections)
    st.dataframe(df_proj, use_container_width=True, hide_index=True)

    fig_proj = go.Figure()
    fig_proj.add_trace(go.Scatter(x=df_proj["Anno"], y=df_proj["Scenario Base"],
                                   name="Scenario Base", mode="lines+markers",
                                   line=dict(color="#0D47A1", width=2)))
    fig_proj.add_trace(go.Scatter(x=df_proj["Anno"], y=df_proj["Scenario Stress"],
                                   name="Scenario Stress", mode="lines+markers",
                                   line=dict(color="#D50000", width=2, dash="dash")))
    fig_proj.add_hline(y=result.thresholds["safe"], line_color="green",
                        line_dash="dot", annotation_text="Soglia Sicura")
    fig_proj.add_hline(y=result.thresholds["grey_low"], line_color="orange",
                        line_dash="dot", annotation_text="Soglia Grigia")
    fig_proj.update_layout(height=320, title="Evoluzione Z-Score - Scenari")
    st.plotly_chart(fig_proj, use_container_width=True)

    # ── Ratio Analysis integrata ──────────────────────────────────────────────
    data_for_ratios = dict(
        total_assets=total_assets, total_liabilities=total_liabilities, revenue=revenue,
        ebit=ebit, ebitda=ebit + depreciation, net_income=net_income, equity=equity,
        current_assets=current_assets, current_liabilities=current_liabilities,
        inventory=inventory, accounts_receivable=accounts_receivable,
        accounts_payable=accounts_payable, interest_expense=interest_expense,
        retained_earnings=retained_earnings,
    )
    ratio_result = calculate_all_ratios(data_for_ratios, industry)

    st.subheader(f"📊 Health Score Finanziario: {ratio_result.overall_score:.0f}/100 - {ratio_result.health_label}")
    cols = st.columns(len(ratio_result.categories))
    for i, cat in enumerate(ratio_result.categories):
        cols[i].metric(f"{cat.icon} {cat.name.split()[0]}", f"{cat.score:.0f}/100")

    # ── Salva su Supabase (con JWT per RLS) ───────────────────────────────────
    access_token = st.session_state.get("access_token", "")
    saved = save_risk_analysis({
        "company_name": company_name,
        "model": result.model,
        "z_score": result.z_score,
        "zone": result.zone,
        "bankruptcy_probability": result.bankruptcy_probability,
        "rating": result.rating,
        "total_assets": total_assets,
        "revenue": revenue,
        "ebit": ebit,
    }, access_token=access_token)
    if saved:
        st.toast("Analisi salvata nello storico Supabase", icon="💾")

    # ── Export PDF ────────────────────────────────────────────────────────────
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📄 Genera Report PDF Completo", type="primary", use_container_width=True):
            with st.spinner("Generazione PDF..."):
                try:
                    from utils.pdf_export import generate_full_report
                    from engine.cashflow import calculate_cashflow
                    cf = calculate_cashflow(data_for_ratios)
                    pdf_bytes = generate_full_report(
                        company_name=company_name or "Azienda",
                        altman_result=result,
                        ratio_result=ratio_result,
                        cashflow_result=cf,
                        raw_data=data_for_ratios,
                    )
                    st.download_button("⬇️ Scarica PDF", data=pdf_bytes,
                                       file_name=f"nexus_zscore_{company_name or 'report'}.pdf",
                                       mime="application/pdf", use_container_width=True)
                    st.success("✅ Report PDF completo generato!")
                except Exception as e:
                    st.error(f"Errore PDF: {e}")
    with col2:
        csv_rows = [("Z-Score", result.z_score), ("Zona", result.zone_label),
                    ("Prob. Fallimento", f"{result.bankruptcy_probability}%"),
                    ("Rating", result.rating)] + list(result.variables.items())
        df_csv = pd.DataFrame(csv_rows, columns=["Indicatore", "Valore"])
        buf = io.StringIO()
        df_csv.to_csv(buf, index=False)
        st.download_button("📊 Esporta CSV", data=buf.getvalue().encode(),
                           file_name="zscore_export.csv", mime="text/csv",
                           use_container_width=True)
