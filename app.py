"""
NEXUS Finance Pro — Main Application
Piattaforma professionale di analisi finanziaria aziendale.
Superiore a DocFinance: Z-Score, 35+ ratios, cash flow, ERP integration, PDF export.
"""
import streamlit as st
from services.auth import login_page, get_current_user, logout

# ── Configurazione pagina ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="NEXUS Finance Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "NEXUS Finance Pro — Analisi finanziaria professionale",
    }
)

# ── CSS Custom ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0D47A1 0%, #1565C0 50%, #0D47A1 100%);
}
[data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stRadio label, [data-testid="stSidebar"] p {
    color: white !important;
}
[data-testid="stSidebar"] .stRadio > label {
    color: rgba(255,255,255,0.8) !important;
    font-size: 0.85em;
}
/* Header */
.nexus-header {
    background: linear-gradient(90deg, #0D47A1, #00897B);
    padding: 1rem 1.5rem;
    border-radius: 8px;
    margin-bottom: 1rem;
    color: white;
}
/* Metric cards */
[data-testid="metric-container"] {
    background: #F8FAFF;
    border: 1px solid #E3E8F0;
    border-radius: 8px;
    padding: 0.5rem;
}
/* Buttons */
.stButton > button[kind="primary"] {
    background: #0D47A1;
    border: none;
    font-weight: 600;
}
.stButton > button[kind="primary"]:hover {
    background: #1565C0;
}
/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #F0F4FF;
    border-radius: 8px;
}
/* Expander */
.streamlit-expanderHeader {
    background: #F0F4FF;
    font-weight: 600;
}
/* Hide footer */
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ── Auth ──────────────────────────────────────────────────────────────────────
user = get_current_user()

if not user:
    login_page()
    st.stop()

# ── Sidebar navigazione ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 1rem 0 0.5rem;'>
        <div style='font-size:2.5rem;'>📊</div>
        <div style='font-size:1.3rem; font-weight:700; color:white;'>NEXUS Finance Pro</div>
        <div style='font-size:0.8rem; color:rgba(255,255,255,0.7);'>Analisi Finanziaria Professionale</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Info utente
    role = user.get("role", "client")
    role_badge = "👑 Admin" if role == "admin" else "👤 Cliente"
    st.markdown(f"""
    <div style='background:rgba(255,255,255,0.15); border-radius:8px; padding:0.6rem; margin-bottom:0.5rem;'>
        <div style='color:white; font-size:0.85rem;'>{role_badge}</div>
        <div style='color:rgba(255,255,255,0.85); font-size:0.75rem;'>{user.get("email","")}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**⚡ STRUMENTO PRINCIPALE**")
    st.markdown("""
    <div style='background:rgba(255,255,255,0.12); border-radius:8px; padding:0.4rem 0.6rem; margin-bottom:0.5rem; border:1px solid rgba(255,255,255,0.2);'>
        <div style='color:#fbbf24; font-size:0.75rem; font-weight:700;'>🔥 NUOVO</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("**📂 ANALISI**")
    pages = {
        "⚡ Credit Readiness": "credit_readiness",
        "🏠 Dashboard": "dashboard",
        "🔌 Import da ERP": "erp_import",
        "📊 Ratio Analysis": "ratio_analysis",
        "💰 Cash Flow": "cashflow",
        "🎯 Z-Score Altman": "risk_analysis",
        "🏅 Credit Scoring": "credit_scoring",
        "📄 Audit Report": "audit_report",
        "📁 Storico Analisi": "history",
    }

    if role == "admin":
        pages["⚙️ Pannello Admin"] = "admin"

    page = st.radio(
        "Naviga",
        list(pages.keys()),
        label_visibility="collapsed",
        key="nav_page",
    )
    page_id = pages[page]

    st.divider()

    # ERP data indicator
    if st.session_state.get("erp_data"):
        company = st.session_state.get("erp_company", "Azienda")
        st.markdown(f"""
        <div style='background:rgba(0,200,83,0.25); border-radius:6px; padding:0.5rem; margin-bottom:0.5rem;'>
            <div style='color:white; font-size:0.8rem;'>✅ Dati ERP caricati</div>
            <div style='color:rgba(255,255,255,0.8); font-size:0.75rem;'>{company}</div>
        </div>
        """, unsafe_allow_html=True)

    if st.button("🚪 Logout", use_container_width=True):
        logout()
        st.rerun()

    st.markdown("""
    <div style='text-align:center; color:rgba(255,255,255,0.4); font-size:0.65rem; margin-top:1rem;'>
    NEXUS Finance Pro v3.0<br>© 2025 Irina Kopitova
    </div>
    """, unsafe_allow_html=True)

# ── Routing pagine ────────────────────────────────────────────────────────────
if page_id == "credit_readiness":
    from pages_modules.credit_readiness import render_credit_readiness
    render_credit_readiness()

elif page_id == "dashboard":
    from pages_modules.dashboard import render_dashboard
    render_dashboard(user)

elif page_id == "erp_import":
    from pages_modules.erp_import import render_erp_import
    render_erp_import()

elif page_id == "ratio_analysis":
    from pages_modules.financial_ratios import render_financial_ratios
    render_financial_ratios()

elif page_id == "cashflow":
    from pages_modules.cashflow_analysis import render_cashflow_analysis
    render_cashflow_analysis()

elif page_id == "risk_analysis":
    from pages_modules.risk_analysis import render_risk_analysis
    render_risk_analysis()

elif page_id == "credit_scoring":
    from pages_modules.credit_scoring import render_credit_scoring
    render_credit_scoring()

elif page_id == "audit_report":
    from pages_modules.audit_report import render_audit_report
    render_audit_report()

elif page_id == "history":
    from pages_modules.history import render_history
    render_history()

elif page_id == "admin" and role == "admin":
    from pages_modules.admin_panel import render_admin_panel
    render_admin_panel()
