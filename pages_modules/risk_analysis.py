"""
NEXUS Finance Pro -- Altman Z-Score Analysis
Upload & Analizza istantaneo + Form manuale.
"""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import io
from engine.calculations import altman_z_original, altman_z_prime, altman_z_doubleprime
from engine.financial_ratios import calculate_all_ratios
from services.db import save_risk_analysis
from utils.file_parser import (
    get_zscore_template_bytes, get_zscore_template_excel, parse_zscore_file
)
from services.erp_connectors import parse_erp_file


def _render_gauge(z_score: float, safe: float, grey: float) -> go.Figure:
    top = max(safe * 1.5, abs(z_score) * 1.5, 5.0)
    color = "#00C853" if z_score >= safe else ("#FFD600" if z_score >= grey else "#D50000")
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=z_score,
        title={"text": "Z-Score", "font": {"size": 16}},
        gauge={
            "axis": {"range": [-5, top], "tickwidth": 1},
            "bar": {"color": color, "thickness": 0.25},
            "steps": [
                {"range": [-5, grey], "color": "#FFEBEE"},
                {"range": [grey, safe], "color": "#FFF9C4"},
                {"range": [safe, top], "color": "#E8F5E9"},
            ],
            "threshold": {"line": {"color": "darkblue", "width": 3}, "value": safe},
        },
        number={"font": {"size": 36, "color": color}},
    ))
    fig.update_layout(height=280, margin=dict(l=20, r=20, t=60, b=20))
    return fig


def _show_zscore_result(result, data_for_ratios, company_name, industry, access_token=""):
    """Mostra i risultati Z-Score completi."""
    z = result.z_score
    zone = result.zone
    zone_colors = {"distress": "#B71C1C", "grey": "#F57F17", "safe": "#1B5E20"}
    zone_labels = {
        "distress": "🔴 ZONA DI DISTRESS",
        "grey": "⚠️ ZONA GRIGIA",
        "safe": "✅ ZONA SICURA",
    }
    zone_color = zone_colors.get(zone, "#333")
    zone_label = zone_labels.get(zone, zone)

    col1, col2 = st.columns([1, 1])
    with col1:
        st.plotly_chart(
            _render_gauge(z, result.thresholds["safe"], result.thresholds["grey_low"]),
            use_container_width=True
        )
    with col2:
        st.markdown(f"""
        <div style="background:{zone_color};padding:15px;border-radius:10px;text-align:center;margin-bottom:10px;">
            <div style="color:white;font-size:1.1rem;font-weight:bold;">{zone_label}</div>
        </div>
        """, unsafe_allow_html=True)
        st.metric("Z-Score", f"{z:.3f}")
        st.metric("Probabilità Fallimento", f"{result.bankruptcy_probability:.1f}%")
        st.metric("Rating Equivalente", result.rating)

    if zone == "distress":
        st.error(f"⚠️ {result.recommendation}")
    elif zone == "grey":
        st.warning(f"⚡ {result.recommendation}")
    else:
        st.success(f"✅ {result.recommendation}")

    # Variabili del modello
    st.subheader("Variabili del Modello")
    df_vars = pd.DataFrame(list(result.variables.items()), columns=["Variabile", "Valore"])
    col1, col2 = st.columns([2, 1])
    with col1:
        st.dataframe(df_vars, use_container_width=True, hide_index=True)
    with col2:
        fig_bar = go.Figure(go.Bar(
            x=list(result.variables.values()),
            y=list(result.variables.keys()),
            orientation="h",
            marker_color=["#00C853" if v > 0 else "#D50000" for v in result.variables.values()],
        ))
        fig_bar.update_layout(height=250, margin=dict(l=10, r=10, t=10, b=10), showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)

    # Proiezioni
    st.subheader("Proiezioni Z-Score (4 anni)")
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

    # Health Score
    ratio_result = calculate_all_ratios(data_for_ratios, industry)
    st.subheader(f"Health Score: {ratio_result.overall_score:.0f}/100 — {ratio_result.health_label}")
    cols = st.columns(len(ratio_result.categories))
    for i, cat in enumerate(ratio_result.categories):
        cols[i].metric(f"{cat.icon} {cat.name.split()[0]}", f"{cat.score:.0f}/100")

    # Salva su Supabase
    saved = save_risk_analysis({
        "company_name": company_name,
        "model": result.model,
        "z_score": result.z_score,
        "zone": result.zone,
        "bankruptcy_probability": result.bankruptcy_probability,
        "rating": result.rating,
        "total_assets": data_for_ratios.get("total_assets", 0),
        "revenue": data_for_ratios.get("revenue", 0),
        "ebit": data_for_ratios.get("ebit", 0),
    }, access_token=access_token)
    if saved:
        st.toast("Analisi salvata nello storico", icon="💾")

    # Export
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📄 Genera Report PDF", type="primary", use_container_width=True, key="pdf_btn"):
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
                    st.download_button("📥 Scarica PDF", data=pdf_bytes,
                                       file_name=f"zscore_{company_name or 'report'}.pdf",
                                       mime="application/pdf", use_container_width=True)
                except Exception as e:
                    st.error(f"Errore PDF: {e}")
    with col2:
        csv_rows = [("Z-Score", result.z_score), ("Zona", result.zone_label),
                    ("Prob. Fallimento", f"{result.bankruptcy_probability}%"),
                    ("Rating", result.rating)] + list(result.variables.items())
        df_csv = pd.DataFrame(csv_rows, columns=["Indicatore", "Valore"])
        buf = io.StringIO()
        df_csv.to_csv(buf, index=False)
        st.download_button("📥 Esporta CSV risultati", data=buf.getvalue().encode(),
                           file_name="zscore_export.csv", mime="text/csv",
                           use_container_width=True)


def render_risk_analysis():
    st.title("Altman Z-Score — Probabilità di Fallimento")
    st.markdown("Tre modelli ufficiali di Altman per aziende quotate, private e di servizi.")

    access_token = st.session_state.get("access_token", "")
    erp_data = st.session_state.get("erp_data", {})

    # ================================================================
    # ⚡ CARICA & ANALIZZA — UN SOLO UPLOAD, RISULTATI ISTANTANEI
    # ================================================================
    st.markdown("""
    <div style="background:linear-gradient(135deg,#0D47A1,#1565C0);padding:20px 25px;border-radius:12px;margin-bottom:16px;">
        <h3 style="color:white;margin:0;">⚡ Carica & Analizza</h3>
        <p style="color:#BBDEFB;margin:6px 0 0 0;font-size:0.9rem;">
            Carica il tuo bilancio CSV o Excel → analisi Z-Score istantanea senza compilare nulla
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_up, col_t1, col_t2 = st.columns([3, 1, 1])
    with col_up:
        uploaded = st.file_uploader(
            "Carica CSV o Excel",
            type=["csv", "xlsx", "xls"],
            key="zscore_upload",
            label_visibility="collapsed",
            help="Usa il template per il formato corretto. Formati: CSV, Excel (.xlsx, .xls)"
        )
    with col_t1:
        st.download_button("📥 Template CSV", data=get_zscore_template_bytes(),
            file_name="template_zscore.csv", mime="text/csv", use_container_width=True)
    with col_t2:
        try:
            st.download_button("📥 Template Excel", data=get_zscore_template_excel(),
                file_name="template_zscore.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True)
        except Exception:
            pass

    file_data = None
    if uploaded:
        parsed = parse_zscore_file(uploaded)
        if parsed["success"]:
            file_data = parsed
            nome = parsed.get("nome_azienda", "Azienda")
            st.success(f"✅ **{nome}** — Dati importati! Analisi automatica qui sotto ↓")

            # Calcola Z-Score automaticamente
            ta = parsed.get("total_assets", 1) or 1
            wc = parsed.get("working_capital", 0)
            re_val = parsed.get("retained_earnings", 0)
            eb = parsed.get("ebit", 0)
            tl = parsed.get("total_liabilities", 1) or 1
            eq = parsed.get("equity_input", 0)
            rv = parsed.get("revenue", 0)
            dep = parsed.get("depreciation", 0)

            result_auto = altman_z_prime(wc, ta, re_val, eb, eq, tl, rv)

            st.markdown("#### 📊 Risultato Analisi Automatica")
            _show_zscore_result(
                result_auto,
                data_for_ratios=dict(
                    total_assets=ta, total_liabilities=tl, revenue=rv,
                    ebit=eb, ebitda=eb + dep, net_income=re_val, equity=eq,
                    current_assets=parsed.get("current_assets", 0),
                    current_liabilities=parsed.get("current_liabilities", 0),
                    inventory=0, accounts_receivable=0, accounts_payable=0,
                    interest_expense=0, retained_earnings=re_val, depreciation=dep,
                ),
                company_name=nome,
                industry="Manifatturiero",
                access_token=access_token,
            )
        else:
            st.error(f"❌ Errore nel file: {parsed['error']}")
            st.info("💡 Scarica il **Template CSV** o **Template Excel** per il formato corretto.")

    st.divider()

    # ================================================================
    # 📝 FORM MANUALE
    # ================================================================
    st.markdown("### 📝 Inserimento Manuale")
    st.caption("Compila i campi sotto (i valori si precompilano se hai caricato un file)")

    merged = {**erp_data, **(file_data or {})}

    col_model, col_info = st.columns([2, 1])
    with col_model:
        model = st.selectbox("Seleziona il modello Z-Score:", [
            "Z'-Score (1983) — Aziende Private [CONSIGLIATO]",
            "Z-Score (1968) — Aziende Quotate Manifatturiere",
            "Z''-Score (1995) — Servizi / Non Manifatturiere",
        ])
    with col_info:
        st.info("Z' → SRL/SPA non quotate\nZ → SPA quotate\nZ'' → Servizi/Retail")

    with st.form("zscore_form_manual"):
        company_name = st.text_input("Nome Azienda",
            value=merged.get("nome_azienda", st.session_state.get("erp_company", "")))
        industry = st.selectbox("Settore", ["Manifatturiero", "Commercio", "Servizi", "Costruzioni", "Tecnologia"])

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**Stato Patrimoniale**")
            total_assets = st.number_input("Totale Attivo (€)", value=float(merged.get("total_assets", 0)), format="%.2f")
            total_liabilities = st.number_input("Totale Passivo (€)", value=float(merged.get("total_liabilities", 0)), format="%.2f")
            equity = st.number_input("Patrimonio Netto (€)", value=float(merged.get("equity_input", merged.get("equity", 0))), format="%.2f")
            current_assets = st.number_input("Attivo Corrente (€)", value=float(merged.get("current_assets", 0)), format="%.2f")
            current_liabilities = st.number_input("Passivo Corrente (€)", value=float(merged.get("current_liabilities", 0)), format="%.2f")
        with col2:
            st.markdown("**Conto Economico**")
            revenue = st.number_input("Ricavi (€)", value=float(merged.get("revenue", 0)), format="%.2f")
            ebit = st.number_input("EBIT (€)", value=float(merged.get("ebit", 0)), format="%.2f")
            net_income = st.number_input("Utile Netto (€)", value=float(merged.get("net_income", 0)), format="%.2f")
            depreciation = st.number_input("Ammortamenti (€)", value=float(merged.get("depreciation", 0)), format="%.2f")
            interest_expense = st.number_input("Oneri Finanziari (€)", value=float(merged.get("interest_expense", 0)), format="%.2f")
        with col3:
            st.markdown("**Altri Dati**")
            retained_earnings = st.number_input("Riserve / Utili portati (€)", value=float(merged.get("retained_earnings", 0)), format="%.2f")
            market_cap = st.number_input("Cap. Borsa (€) [solo 1968]", value=float(merged.get("market_cap", merged.get("equity", 0))), format="%.2f")
            inventory = st.number_input("Magazzino (€)", value=float(merged.get("inventory", 0)), format="%.2f")
            accounts_receivable = st.number_input("Crediti Commerciali (€)", value=float(merged.get("accounts_receivable", 0)), format="%.2f")
            accounts_payable = st.number_input("Debiti Commerciali (€)", value=float(merged.get("accounts_payable", 0)), format="%.2f")

        submitted = st.form_submit_button("🔍 CALCOLA Z-SCORE", type="primary", use_container_width=True)

    if submitted:
        if total_assets == 0:
            st.error("Inserisci almeno il Totale Attivo")
            return

        working_capital = current_assets - current_liabilities
        ta_safe = total_assets if total_assets != 0 else 1
        tl_safe = total_liabilities if total_liabilities != 0 else 1

        if "1968" in model:
            result = altman_z_original(working_capital, ta_safe, retained_earnings,
                                        ebit, market_cap, tl_safe, revenue)
        elif "1995" in model:
            result = altman_z_doubleprime(working_capital, ta_safe, retained_earnings,
                                           ebit, equity, tl_safe)
        else:
            result = altman_z_prime(working_capital, ta_safe, retained_earnings,
                                     ebit, equity, tl_safe, revenue)

        st.divider()
        st.markdown("#### 📊 Risultato Analisi Manuale")
        data_for_ratios = dict(
            total_assets=total_assets, total_liabilities=total_liabilities,
            revenue=revenue, ebit=ebit, ebitda=ebit + depreciation,
            net_income=net_income, equity=equity,
            current_assets=current_assets, current_liabilities=current_liabilities,
            inventory=inventory, accounts_receivable=accounts_receivable,
            accounts_payable=accounts_payable, interest_expense=interest_expense,
            retained_earnings=retained_earnings, depreciation=depreciation,
        )
        _show_zscore_result(result, data_for_ratios, company_name, industry, access_token)
