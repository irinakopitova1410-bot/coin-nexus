"""
NEXUS Finance Pro — Entry Point
Analisi finanziaria professionale per PMI italiane.
"""
import streamlit as st
import os

# ── Configurazione pagina ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="NEXUS Finance Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Secrets: supporta sia Streamlit Cloud che variabili d'ambiente ─────────────
def get_secret(key: str, fallback: str = "") -> str:
    try:
        return st.secrets[key]
    except Exception:
        return os.environ.get(key, fallback)

# Rendi i secrets disponibili come env vars per i moduli services/
if not os.environ.get("SUPABASE_URL"):
    url = get_secret("SUPABASE_URL")
    key = get_secret("SUPABASE_KEY")
    if url:
        os.environ["SUPABASE_URL"] = url
    if key:
        os.environ["SUPABASE_KEY"] = key

# ── CSS globale ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0D47A1 0%, #1565C0 60%, #0097A7 100%);
    color: white;
}
[data-testid="stSidebar"] * { color: white !important; }
[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.15);
    border: 1px solid rgba(255,255,255,0.3);
    color: white !important;
    border-radius: 8px;
    width: 100%;
    text-align: left;
    margin-bottom: 2px;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.25);
}
/* Metric cards */
[data-testid="metric-container"] {
    background: #f8faff;
    border-radius: 12px;
    padding: 16px;
    border: 1px solid #e3eafc;
    box-shadow: 0 2px 8px rgba(13,71,161,0.06);
}
/* Headers */
h1, h2, h3 { color: #0D47A1; }
/* Hide Streamlit default menu */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Autenticazione ─────────────────────────────────────────────────────────────
from services.auth import login_page, get_current_user, logout

user = get_current_user()

if not user:
    login_page()
    st.stop()

# ── Sidebar navigazione ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding:16px 0 8px 0;'>
        <div style='font-size:32px;'>📊</div>
        <div style='font-size:18px; font-weight:800; letter-spacing:1px;'>NEXUS Finance</div>
        <div style='font-size:11px; opacity:0.8;'>Pro Analytics Platform</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Info utente
    role_label = "👑 Admin" if user.get("role") == "admin" else "👤 Cliente"
    company = user.get("company_name") or user.get("email", "")
    st.markdown(f"""
    <div style='background:rgba(255,255,255,0.12); border-radius:8px; padding:10px 12px; margin-bottom:12px;'>
        <div style='font-size:13px; font-weight:700;'>{role_label}</div>
        <div style='font-size:11px; opacity:0.85; word-break:break-all;'>{company}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Navigazione principale ─────────────────────────────────────────────────
    st.markdown("<div style='font-size:11px; opacity:0.7; font-weight:600; letter-spacing:1px; margin-bottom:6px;'>⚡ STRUMENTO PRINCIPALE</div>", unsafe_allow_html=True)

    PAGES = {
        "credit_readiness": ("⚡", "Credit Readiness"),
        "dashboard":        ("🏠", "Dashboard"),
        "erp_import":       ("🔌", "Import da ERP"),
        "ratio_analysis":   ("📊", "Ratio Analysis"),
        "cashflow":         ("💰", "Cash Flow"),
        "risk_analysis":    ("🎯", "Z-Score Altman"),
        "credit_scoring":   ("🏅", "Credit Scoring"),
        "audit_report":     ("📄", "Audit Report"),
        "history":          ("📁", "Storico Analisi"),
    }

    if user.get("role") == "admin":
        PAGES["admin_panel"] = ("⚙️", "Admin Panel")

    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "credit_readiness"

    def nav_button(page_id, icon, label):
        is_active = st.session_state.get("current_page") == page_id
        btn_style = "background:rgba(255,255,255,0.3) !important;" if is_active else ""
        # Usa un marker visivo
        prefix = "▶ " if is_active else "   "
        if st.button(f"{prefix}{icon} {label}", key=f"nav_{page_id}"):
            st.session_state["current_page"] = page_id
            st.rerun()

    for pid, (icon, label) in PAGES.items():
        nav_button(pid, icon, label)

    st.markdown("---")
    if st.button("🚪 Esci", key="logout_btn"):
        logout()

    st.markdown("""
    <div style='text-align:center; font-size:10px; opacity:0.6; margin-top:16px;'>
        NEXUS Finance Pro v4.0<br>© 2025 Irina Kopitova
    </div>
    """, unsafe_allow_html=True)

# ── Routing pagine ─────────────────────────────────────────────────────────────
page_id = st.session_state.get("current_page", "credit_readiness")

try:
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
        render_history(user)

    elif page_id == "admin_panel":
        if user.get("role") == "admin":
            from pages_modules.admin_panel import render_admin_panel
            render_admin_panel()
        else:
            st.error("Accesso non autorizzato.")

    else:
        st.info("Seleziona una sezione dalla barra laterale.")

except ImportError as e:
    st.error(f"❌ Errore modulo: {e}")
    st.info("Controlla che tutti i file siano correttamente caricati su GitHub.")
    with st.expander("Dettagli errore"):
        import traceback
        st.code(traceback.format_exc())

except Exception as e:
    st.error(f"❌ Errore: {e}")
    with st.expander("Dettagli errore"):
        import traceback
        st.code(traceback.format_exc())
