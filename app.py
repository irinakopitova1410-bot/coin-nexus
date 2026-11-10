"""
NEXUS Finance Pro — Entry Point
La prossima generazione di financial intelligence per PMI italiane.
v6.0 — Aurora Edition: Copilot AI · Design System · Big Four Suite
"""
import streamlit as st
import os

# ── Configurazione pagina ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="NEXUS Finance Pro",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Secrets: supporta sia Streamlit Cloud che variabili d'ambiente ─────────────
def get_secret(key: str, fallback: str = "") -> str:
    try:
        return st.secrets[key]
    except Exception:
        return os.environ.get(key, fallback)

if not os.environ.get("SUPABASE_URL"):
    url = get_secret("SUPABASE_URL")
    key = get_secret("SUPABASE_KEY")
    if url:
        os.environ["SUPABASE_URL"] = url
    if key:
        os.environ["SUPABASE_KEY"] = key

# ── Design System Aurora ───────────────────────────────────────────────────────
from utils.ui_kit import inject_global_css
inject_global_css()

# ── Autenticazione ─────────────────────────────────────────────────────────────
from services.auth import login_page, get_current_user, logout, pretty_display_name

# Bypass solo per sviluppo locale (mai attivo su Streamlit Cloud)
if not os.environ.get("NEXUS_DEV_BYPASS"):
    user = get_current_user()
else:
    user = {
        "id": "dev", "email": "demo@nexus.local",
        "role": "admin", "full_name": "Demo Aurora",
        "company_name": "NEXUS Demo", "access_token": "",
    }

if not user:
    login_page()
    st.stop()

# ── Sidebar navigazione ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:10px 4px 2px 4px;'>
        <div style='display:flex; align-items:center; gap:10px;'>
            <div style='width:34px; height:34px; border-radius:10px;
                        background:linear-gradient(135deg,#1E376C 0%,#4A6FA5 100%);
                        display:flex; align-items:center; justify-content:center;
                        color:white; font-weight:800; font-size:16px;
                        font-family:Playfair Display, serif;'>N</div>
            <div>
                <div class='nx-side-brand'>NEXUS</div>
                <div class='nx-side-tag'>Financial Intelligence</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    role_label = "Admin" if user.get("role") == "admin" else "Cliente"
    company = user.get("company_name") or user.get("email", "")
    name = pretty_display_name(user.get("full_name", ""), user.get("email", ""))
    st.markdown(f"""
    <div class='nx-side-user'>
        <div style='font-size:12.5px; font-weight:700;'>{name}</div>
        <div style='font-size:10.5px; opacity:0.65; word-break:break-all; margin-top:2px;'>{company}</div>
        <div style='margin-top:6px;'><span style='font-family:IBM Plex Mono, monospace; font-size:9px;
            letter-spacing:0.14em; text-transform:uppercase; background:rgba(201,162,39,0.28);
            border:1px solid rgba(245,226,141,0.5); border-radius:999px; padding:2px 9px;'>{role_label}</span></div>
    </div>
    """, unsafe_allow_html=True)

    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "credit_readiness"

    def nav_button(page_id, label):
        is_active = st.session_state.get("current_page") == page_id
        prefix = "› " if is_active else ""
        weight = "font-weight:700;" if is_active else ""
        if st.button(f"{prefix}{label}", key=f"nav_{page_id}"):
            st.session_state["current_page"] = page_id
            st.rerun()

    # ── STRUMENTO PRINCIPALE ──
    st.markdown("<div class='nx-side-label'>⚡ Strumento principale</div>", unsafe_allow_html=True)
    nav_button("credit_readiness", "Credit Readiness")

    # ── COPILOT AI ──
    st.markdown("<div class='nx-side-label'>◆ Copilot AI</div>", unsafe_allow_html=True)
    nav_button("copilot", "NEXUS Copilot")

    # ── ANALISI FINANZIARIA ──
    st.markdown("<div class='nx-side-label'>📊 Analisi finanziaria</div>", unsafe_allow_html=True)
    nav_button("dashboard",      "Dashboard")
    nav_button("risk_analysis",  "Z-Score Altman")
    nav_button("credit_scoring", "Credit Scoring")
    nav_button("ratio_analysis", "Ratio Analysis")
    nav_button("cashflow",       "Cash Flow")
    nav_button("audit_report",   "Audit Report ISA 320")

    # ── BIG FOUR SUITE ──
    st.markdown("<div class='nx-side-label'>🏆 Big Four Suite</div>", unsafe_allow_html=True)
    nav_button("early_warning",    "Early Warning CCII")
    nav_button("esg_scoring",      "ESG Scoring")
    nav_button("ai_analyst",       "AI Financial Analyst")
    nav_button("open_banking",     "Open Banking PSD2")
    nav_button("whatif_simulator", "What-If Simulator")
    nav_button("variance_analysis","Variance Analysis")

    # ── INTEGRAZIONI ──
    st.markdown("<div class='nx-side-label'>🔌 Integrazioni</div>", unsafe_allow_html=True)
    nav_button("erp_import", "Import da ERP")

    # ── STORICO ──
    st.markdown("<div class='nx-side-label'>📁 Archivio</div>", unsafe_allow_html=True)
    nav_button("history", "Storico Analisi")

    if user.get("role") == "admin":
        st.markdown("<div class='nx-side-label'>⚙️ Admin</div>", unsafe_allow_html=True)
        nav_button("admin_panel", "Admin Panel")

    st.markdown("---")
    if st.button("Esci", key="logout_btn"):
        logout()

    st.markdown("""
    <div class='nx-side-footer'>
        NEXUS v6.2 · Aurora<br>© 2026 Irina Kopitova
    </div>
    """, unsafe_allow_html=True)

# ── Routing pagine ─────────────────────────────────────────────────────────────
page_id = st.session_state.get("current_page", "credit_readiness")

try:
    # ── STRUMENTO PRINCIPALE ──
    if page_id == "credit_readiness":
        from pages_modules.credit_readiness import render_credit_readiness
        render_credit_readiness()

    # ── COPILOT ──
    elif page_id == "copilot":
        from pages_modules.copilot import render_copilot
        render_copilot(user)

    # ── ANALISI FINANZIARIA ──
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
        from pages_modules.credit_scoring import show_credit_scoring
        show_credit_scoring()

    elif page_id == "audit_report":
        from pages_modules.audit_report import show_audit_report
        show_audit_report()

    elif page_id == "history":
        from pages_modules.history import show_history
        show_history()

    # ── BIG FOUR SUITE ──
    elif page_id == "early_warning":
        from pages_modules.early_warning import show_early_warning
        show_early_warning()

    elif page_id == "esg_scoring":
        from pages_modules.esg_scoring import show_esg_scoring
        show_esg_scoring()

    elif page_id == "ai_analyst":
        from pages_modules.ai_analyst import show_ai_analyst
        show_ai_analyst()

    elif page_id == "open_banking":
        from pages_modules.open_banking import show_open_banking
        show_open_banking()

    elif page_id == "whatif_simulator":
        from pages_modules.whatif_simulator import show_whatif_simulator
        show_whatif_simulator()

    elif page_id == "variance_analysis":
        from pages_modules.variance_analysis import show_variance_analysis
        show_variance_analysis()

    # ── ADMIN ──
    elif page_id == "admin_panel":
        if user.get("role") == "admin":
            from pages_modules.admin_panel import show_admin_panel
            show_admin_panel()
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
