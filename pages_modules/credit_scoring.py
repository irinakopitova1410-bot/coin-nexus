import streamlit as st
from engine.calculations import calculate_credit_score
from utils.charts import radar_chart, bar_chart
from services.db import save_credit_report

def show_credit_scoring():
    st.markdown("""
    <div style="background:linear-gradient(135deg,#1E3A8A,#1D4ED8);padding:25px;border-radius:12px;margin-bottom:25px;">
        <h1 style="color:white;margin:0;font-size:1.8rem;">💳 Credit Scoring — Basel IV</h1>
        <p style="color:#BFDBFE;margin:5px 0 0 0;">Analisi del merito creditizio con rating AAA–D e limite di fido stimato</p>
    </div>
    """, unsafe_allow_html=True)

    company_name = st.text_input("Nome Azienda / Debitore", placeholder="Es: Mario Bianchi S.p.A.")

    st.subheader("📊 Dati Finanziari")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**🔵 Reddito & Debito**")
        ebit = st.number_input("EBIT (€)", value=120000.0, step=5000.0, format="%.0f")
        depreciation = st.number_input("Ammortamenti (€)", min_value=0.0, value=30000.0, step=1000.0, format="%.0f")
        interest_expense = st.number_input("Interessi passivi (€)", min_value=0.0, value=20000.0, step=1000.0, format="%.0f")
        debt_repayment = st.number_input("Rimborso debito annuo (€)", min_value=0.0, value=50000.0, step=5000.0, format="%.0f")

    with col2:
        st.markdown("**🟡 Struttura Patrimoniale**")
        total_debt = st.number_input("Debiti Finanziari Totali (€)", min_value=0.0, value=400000.0, step=10000.0, format="%.0f")
        total_equity = st.number_input("Patrimonio Netto (€)", min_value=1.0, value=300000.0, step=10000.0, format="%.0f")
        ebitda = st.number_input("EBITDA (€)", value=150000.0, step=5000.0, format="%.0f")
        net_revenue = st.number_input("Ricavi Netti (€)", min_value=1.0, value=900000.0, step=10000.0, format="%.0f")

    with col3:
        st.markdown("**🟢 Liquidità**")
        current_assets = st.number_input("Attivo Corrente (€)", min_value=0.0, value=350000.0, step=10000.0, format="%.0f")
        current_liabilities = st.number_input("Passivo Corrente (€)", min_value=1.0, value=200000.0, step=10000.0, format="%.0f")

    st.markdown("---")

    if st.button("💳 CALCOLA CREDIT SCORE", type="primary", use_container_width=True):
        result = calculate_credit_score(
            ebit, depreciation, interest_expense, debt_repayment,
            total_debt, ebitda, net_revenue, current_assets, current_liabilities, total_equity
        )

        col1, col2, col3 = st.columns(3)

        rating_colors = {"AAA": "#4ADE80","AA": "#4ADE80","A": "#86EFAC","BBB": "#FCD34D",
                         "BB": "#FCD34D","B": "#FB923C","CCC": "#F87171","CC": "#F87171","D": "#F87171"}
        rc = rating_colors.get(result.rating, "#94A3B8")

        with col1:
            st.markdown(f"""
            <div style="background:#1E293B;border-radius:12px;padding:25px;text-align:center;border:2px solid {result.decision_color};">
                <div style="color:#94A3B8;font-size:0.85rem;">SCORE COMPLESSIVO</div>
                <div style="color:{result.decision_color};font-size:3.5rem;font-weight:800;">{result.score}</div>
                <div style="color:#64748B;font-size:0.75rem;">su 100</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div style="background:#1E293B;border-radius:12px;padding:25px;text-align:center;border:2px solid {rc};">
                <div style="color:#94A3B8;font-size:0.85rem;">RATING CREDITIZIO</div>
                <div style="color:{rc};font-size:3.5rem;font-weight:800;">{result.rating}</div>
                <div style="color:#64748B;font-size:0.75rem;">Basel IV</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div style="background:#1E293B;border-radius:12px;padding:25px;text-align:center;border:2px solid {result.decision_color};">
                <div style="color:#94A3B8;font-size:0.85rem;">DECISIONE</div>
                <div style="color:{result.decision_color};font-size:1.6rem;font-weight:700;">{result.decision}</div>
                <div style="color:#64748B;font-size:0.75rem;">Fido max: €{result.max_credit:,.0f}</div>
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
                    <div style="color:{color};font-size:1.6rem;font-weight:700;">{val}{suffix}</div>
                    <div style="color:#64748B;font-size:0.7rem;">{desc}</div>
                </div>
                """, unsafe_allow_html=True)

        st.subheader("📋 Raccomandazioni")
        for rec in result.recommendations:
            st.markdown(f"- {rec}")

        st.markdown("---")
        if st.button("💾 Salva Credit Report"):
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
                st.success("✅ Credit report salvato con successo!")
