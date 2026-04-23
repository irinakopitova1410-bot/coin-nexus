import streamlit as st
from engine.calculations import calculate_audit
from services.db import save_audit_report

def show_audit_report():
    st.markdown("""
    <div style="background:linear-gradient(135deg,#4C1D95,#7C3AED);padding:25px;border-radius:12px;margin-bottom:25px;">
        <h1 style="color:white;margin:0;font-size:1.8rem;">📊 Audit Report — ISA 320</h1>
        <p style="color:#DDD6FE;margin:5px 0 0 0;">Calcolo materialità, performance materiality e giudizio di revisione</p>
    </div>
    """, unsafe_allow_html=True)

    company_name = st.text_input("Nome Azienda", placeholder="Es: Tech Innovations S.r.l.")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📈 Dati di Bilancio")
        gross_profit = st.number_input("Utile Lordo (€)", value=250000.0, step=10000.0, format="%.0f")
        total_assets = st.number_input("Totale Attivo (€)", min_value=1.0, value=2000000.0, step=50000.0, format="%.0f")
        net_revenue = st.number_input("Ricavi Netti (€)", min_value=1.0, value=1500000.0, step=50000.0, format="%.0f")
        pre_tax_income = st.number_input("Reddito ante imposte (€)", value=200000.0, step=10000.0, format="%.0f")

    with col2:
        st.subheader("🔍 Parametri di Revisione")
        internal_control_score = st.slider("Qualità Controlli Interni", 1, 10, 7,
                                            help="1=Pessimo, 10=Eccellente")
        error_rate = st.number_input("Tasso di Errori Rilevati (%)", min_value=0.0, max_value=100.0,
                                      value=2.0, step=0.5, format="%.1f")
        risk_level = st.select_slider("Livello di Rischio Inerente",
                                       options=["low", "medium", "high"],
                                       value="medium",
                                       format_func=lambda x: {"low":"🟢 Basso","medium":"🟡 Medio","high":"🔴 Alto"}[x])
        st.markdown("---")
        st.markdown("""
        **Guida ISA 320:**
        - Materialità = 5% utile lordo
        - Performance Mat. = 75% materialità
        - Soglia irrilevanza = 3% materialità
        """)

    st.markdown("---")

    if st.button("📊 GENERA AUDIT REPORT", type="primary", use_container_width=True):
        result = calculate_audit(gross_profit, total_assets, net_revenue, pre_tax_income,
                                  internal_control_score, error_rate, risk_level)

        st.markdown(f"""
        <div style="background:#1E293B;border:2px solid {result.judgment_color};border-radius:12px;padding:20px;margin:15px 0;text-align:center;">
            <div style="font-size:1.4rem;font-weight:700;color:{result.judgment_color};">{result.judgment}</div>
            <div style="color:#94A3B8;margin-top:5px;">Score Qualità: {result.score}/100</div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"""
            <div style="background:#1E293B;border-radius:12px;padding:20px;text-align:center;">
                <div style="color:#94A3B8;font-size:0.8rem;">SOGLIA DI MATERIALITÀ</div>
                <div style="color:#3B82F6;font-size:1.6rem;font-weight:700;">€{result.materiality:,.2f}</div>
                <div style="color:#64748B;font-size:0.75rem;">5% × Utile Lordo</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div style="background:#1E293B;border-radius:12px;padding:20px;text-align:center;">
                <div style="color:#94A3B8;font-size:0.8rem;">PERFORMANCE MATERIALITY</div>
                <div style="color:#8B5CF6;font-size:1.6rem;font-weight:700;">€{result.performance_materiality:,.2f}</div>
                <div style="color:#64748B;font-size:0.75rem;">75%/80%/65% della Materialità</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div style="background:#1E293B;border-radius:12px;padding:20px;text-align:center;">
                <div style="color:#94A3B8;font-size:0.8rem;">SOGLIA DI IRRILEVANZA</div>
                <div style="color:#06B6D4;font-size:1.6rem;font-weight:700;">€{result.trivial_threshold:,.2f}</div>
                <div style="color:#64748B;font-size:0.75rem;">3% della Materialità</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("⚠️ Rischi Identificati")
            for risk in result.risks:
                st.markdown(f"- {risk}")

        with col2:
            st.subheader("💡 Raccomandazioni")
            for rec in result.recommendations:
                st.markdown(f"- {rec}")

        st.markdown("---")
        if st.button("💾 Salva Audit Report"):
            saved = save_audit_report({
                "company_name": company_name or "N/A",
                "materiality": result.materiality,
                "performance_materiality": result.performance_materiality,
                "trivial_threshold": result.trivial_threshold,
                "score": result.score,
                "judgment": result.judgment,
                "risk_level": risk_level,
                "internal_control_score": internal_control_score,
                "error_rate": error_rate,
            })
            if saved:
                st.success("✅ Audit report salvato con successo!")
