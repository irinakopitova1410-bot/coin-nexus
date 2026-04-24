import streamlit as st
import pandas as pd
from engine.calculations import calculate_credit_score
from utils.charts import radar_chart, bar_chart
from utils.file_parser import parse_credit_file, get_credit_template_bytes, get_credit_template_excel
from services.db import save_credit_report


def _show_credit_result(result, company_name="", access_token=""):
    """Mostra i risultati del credit scoring."""
    rating_colors = {
        "AAA": "#4ADE80", "AA": "#4ADE80", "A": "#86EFAC",
        "BBB": "#FCD34D", "BB": "#FCD34D", "B": "#FB923C",
        "CCC": "#F87171", "CC": "#F87171", "D": "#EF4444"
    }
    rc = rating_colors.get(result.rating, "#94A3B8")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div style="background:#1E293B;border-radius:12px;padding:25px;text-align:center;border:2px solid {result.decision_color};">
            <div style="color:#94A3B8;font-size:0.85rem;">SCORE</div>
            <div style="color:{result.decision_color};font-size:3.5rem;font-weight:800;">{result.score}</div>
            <div style="color:#64748B;font-size:0.75rem;">su 100</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style="background:#1E293B;border-radius:12px;padding:25px;text-align:center;border:2px solid {rc};">
            <div style="color:#94A3B8;font-size:0.85rem;">RATING Basel IV</div>
            <div style="color:{rc};font-size:3.5rem;font-weight:800;">{result.rating}</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div style="background:#1E293B;border-radius:12px;padding:25px;text-align:center;border:2px solid {result.decision_color};">
            <div style="color:#94A3B8;font-size:0.85rem;">DECISIONE</div>
            <div style="color:{result.decision_color};font-size:1.6rem;font-weight:700;">{result.decision}</div>
            <div style="color:#4ADE80;font-size:0.85rem;">Fido max: €{result.max_credit:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        cats = list(result.components.keys())
        vals = list(result.components.values())
        st.plotly_chart(radar_chart(cats, vals, "Profilo di Rischio"), use_container_width=True)
    with col2:
        st.plotly_chart(bar_chart(cats, vals, "Score per Componente"), use_container_width=True)

    st.subheader("📏 Indicatori Chiave")
    m1, m2, m3, m4 = st.columns(4)
    dscr_c = "#4ADE80" if result.dscr >= 1.5 else "#FCD34D" if result.dscr >= 1.0 else "#F87171"
    lev_c = "#4ADE80" if result.leverage <= 2 else "#FCD34D" if result.leverage <= 4 else "#F87171"
    eb_c = "#4ADE80" if result.ebitda_margin >= 15 else "#FCD34D" if result.ebitda_margin >= 8 else "#F87171"
    cr_c = "#4ADE80" if result.current_ratio >= 1.5 else "#FCD34D" if result.current_ratio >= 1.0 else "#F87171"

    for col, label, val, color, suffix, desc in [
        (m1, "DSCR", result.dscr, dscr_c, "x", "Soglia: ≥1.25"),
        (m2, "Leverage D/E", result.leverage, lev_c, "x", "Soglia: ≤3.0"),
        (m3, "EBITDA Margin", result.ebitda_margin, eb_c, "%", "Soglia: ≥10%"),
        (m4, "Current Ratio", result.current_ratio, cr_c, "x", "Soglia: ≥1.2"),
    ]:
        with col:
            st.markdown(f"""
            <div style="background:#1E293B;border-radius:8px;padding:15px;text-align:center;">
                <div style="color:#94A3B8;font-size:0.75rem;">{label}</div>
                <div style="color:{color};font-size:1.6rem;font-weight:700;">{val:.2f}{suffix}</div>
                <div style="color:#64748B;font-size:0.7rem;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.subheader("📋 Raccomandazioni")
    for rec in result.recommendations:
        st.markdown(f"- {rec}")


def show_credit_scoring():
    st.markdown("""
    <div style="background:linear-gradient(135deg,#1E3A8A,#1D4ED8);padding:25px;border-radius:12px;margin-bottom:25px;">
        <h1 style="color:white;margin:0;font-size:1.8rem;">💳 Credit Scoring — Basel IV</h1>
        <p style="color:#BFDBFE;margin:5px 0 0 0;">Analisi del merito creditizio con rating AAA–D e limite di fido stimato</p>
    </div>
    """, unsafe_allow_html=True)

    access_token = st.session_state.get("access_token", "")

    # ================================================================
    # ⚡ CARICA & ANALIZZA — UPLOAD UNICO + RISULTATI ISTANTANEI
    # ================================================================
    st.markdown("""
<div style="background:linear-gradient(135deg,#0D47A1,#1565C0);padding:20px 25px;border-radius:12px;margin-bottom:16px;">
    <h3 style="color:white;margin:0;">⚡ Carica & Analizza</h3>
    <p style="color:#BBDEFB;margin:6px 0 0 0;font-size:0.9rem;">
        Carica il tuo bilancio CSV o Excel → Credit Score istantaneo senza compilare nulla
    </p>
</div>
""", unsafe_allow_html=True)

    col_up, col_t1, col_t2 = st.columns([3, 1, 1])
    with col_up:
        uploaded = st.file_uploader(
            "Carica CSV o Excel",
            type=["csv", "xlsx", "xls"],
            key="credit_upload",
            label_visibility="collapsed",
            help="Usa il template per il formato corretto"
        )
    with col_t1:
        st.download_button("📥 Template CSV", data=get_credit_template_bytes(),
            file_name="template_credit_scoring.csv", mime="text/csv", use_container_width=True)
    with col_t2:
        try:
            st.download_button("📥 Template Excel", data=get_credit_template_excel(),
                file_name="template_credit_scoring.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True)
        except Exception:
            pass

    file_data = None
    if uploaded:
        parsed = parse_credit_file(uploaded)
        if parsed["success"]:
            file_data = parsed
            nome = parsed.get("nome_azienda", "Azienda")
            st.success(f"✅ **{nome}** — Dati importati! Credit Score qui sotto ↓")

            # Valori safe per divisione
            eq_val = parsed.get("total_equity", 0)
            rev_val = parsed.get("net_revenue", 0)
            cl_val = parsed.get("current_liabilities", 0)
            eq_safe = eq_val if abs(eq_val) >= 1 else 1
            rev_safe = rev_val if abs(rev_val) >= 1 else 1
            cl_safe = cl_val if abs(cl_val) >= 1 else 1

            result_auto = calculate_credit_score(
                parsed.get("ebit", 0),
                parsed.get("depreciation", 0),
                parsed.get("interest_expense", 0),
                parsed.get("debt_repayment", 0),
                parsed.get("total_debt", 0),
                parsed.get("ebitda", 0),
                rev_safe,
                parsed.get("current_assets", 0),
                cl_safe,
                eq_safe,
            )

            st.markdown("#### 📊 Risultato Analisi Automatica")
            _show_credit_result(result_auto, nome, access_token)
        else:
            st.error(f"❌ Errore nel file: {parsed['error']}")
            st.info("💡 Scarica il **Template CSV** per il formato corretto e riprova.")

    st.divider()

    # ================================================================
    # 📝 FORM MANUALE
    # ================================================================
    st.markdown("### 📝 Inserimento Manuale (opzionale)")
    st.caption("I campi si precompilano se hai caricato un file sopra")

    defaults = {
        "nome_azienda": "",
        "ebit": 120000.0,
        "depreciation": 30000.0,
        "interest_expense": 20000.0,
        "debt_repayment": 50000.0,
        "total_debt": 400000.0,
        "total_equity": 300000.0,
        "ebitda": 150000.0,
        "net_revenue": 900000.0,
        "current_assets": 350000.0,
        "current_liabilities": 200000.0,
    }
    if file_data:
        defaults.update(file_data)

    company_name = st.text_input("Nome Azienda / Debitore",
        value=str(defaults.get("nome_azienda", "")),
        placeholder="Es: Mario Bianchi S.p.A.")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**🔵 Reddito & Debito**")
        ebit = st.number_input("EBIT (€)", value=float(defaults["ebit"]), step=5000.0, format="%.0f")
        depreciation = st.number_input("Ammortamenti (€)", min_value=0.0, value=float(defaults["depreciation"]), step=1000.0, format="%.0f")
        interest_expense = st.number_input("Interessi passivi (€)", min_value=0.0, value=float(defaults["interest_expense"]), step=1000.0, format="%.0f")
        debt_repayment = st.number_input("Rimborso debito annuo (€)", min_value=0.0, value=float(defaults["debt_repayment"]), step=5000.0, format="%.0f")
    with col2:
        st.markdown("**🟡 Struttura Patrimoniale**")
        total_debt = st.number_input("Debiti Finanziari Totali (€)", min_value=0.0, value=float(defaults["total_debt"]), step=10000.0, format="%.0f")
        total_equity = st.number_input("Patrimonio Netto (€)", value=float(defaults["total_equity"]), step=10000.0, format="%.0f")
        ebitda = st.number_input("EBITDA (€)", value=float(defaults["ebitda"]), step=5000.0, format="%.0f")
        net_revenue = st.number_input("Ricavi Netti (€)", value=float(defaults["net_revenue"]), step=10000.0, format="%.0f")
    with col3:
        st.markdown("**🟢 Liquidità**")
        current_assets = st.number_input("Attivo Corrente (€)", min_value=0.0, value=float(defaults["current_assets"]), step=10000.0, format="%.0f")
        current_liabilities = st.number_input("Passivo Corrente (€)", min_value=0.0, value=float(defaults["current_liabilities"]), step=10000.0, format="%.0f")

    st.markdown("---")
    if st.button("💳 CALCOLA CREDIT SCORE", type="primary", use_container_width=True):
        eq_safe = total_equity if abs(total_equity) >= 1 else 1
        rev_safe = net_revenue if abs(net_revenue) >= 1 else 1
        cl_safe = current_liabilities if current_liabilities >= 1 else 1

        result = calculate_credit_score(
            ebit, depreciation, interest_expense, debt_repayment,
            total_debt, ebitda, rev_safe, current_assets, cl_safe, eq_safe
        )

        st.markdown("#### 📊 Risultato Analisi Manuale")
        _show_credit_result(result, company_name, access_token)

        st.markdown("---")
        if st.button("💾 Salva Credit Report", key="save_credit"):
            saved = save_credit_report({
                "company_name": company_name or "N/A",
                "score": result.score,
                "rating": result.rating,
                "decision": result.decision,
                "dscr": result.dscr,
                "leverage": result.leverage,
                "ebitda_margin": result.ebitda_margin,
                "current_ratio": result.current_ratio,
                "max_credit": result.max_credit,
            })
            if saved:
                st.success("✅ Credit report salvato!")
