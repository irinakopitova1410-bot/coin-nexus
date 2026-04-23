import streamlit as st

st.set_page_config(
    page_title="NEXUS Finance Pro",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CSS GLOBALE ────────────────────────────────────────────────
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background: #0a0e1a; }
    [data-testid="stSidebar"] { background: #0d1220; border-right: 1px solid #1e2d4a; }
    .main .block-container { padding: 2rem; max-width: 1400px; }
    h1, h2, h3 { color: #e2e8f0 !important; }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; border: none; border-radius: 8px;
        font-weight: 600; transition: all 0.3s;
    }
    .stButton > button:hover { transform: translateY(-2px); box-shadow: 0 4px 15px rgba(102,126,234,0.4); }
    .metric-card {
        background: linear-gradient(135deg, #1a2340 0%, #0d1220 100%);
        border: 1px solid #1e2d4a; border-radius: 12px;
        padding: 20px; text-align: center; margin: 8px 0;
    }
    /* Login form */
    .login-container {
        max-width: 420px; margin: 80px auto;
        background: linear-gradient(135deg, #1a2340 0%, #0d1220 100%);
        border: 1px solid #1e2d4a; border-radius: 16px; padding: 40px;
    }
    div[data-testid="stTextInput"] input {
        background: #0a0e1a !important; color: #e2e8f0 !important;
        border: 1px solid #1e2d4a !important; border-radius: 8px !important;
    }
</style>
""", unsafe_allow_html=True)

# ─── FUNZIONI AUTH ────────────────────────────────────────────
from services.auth import login, logout, get_user_profile, is_admin, is_authenticated

def show_login_page():
    """Pagina di login elegante."""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align:center; padding: 40px 0 20px;">
            <div style="font-size:4rem">💎</div>
            <h1 style="color:#667eea; font-size:2.2rem; margin:0;">NEXUS Finance Pro</h1>
            <p style="color:#64748b; font-size:1rem; margin-top:8px;">
                Piattaforma Avanzata di Analisi Finanziaria
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        with st.form("login_form"):
            st.markdown("### 🔐 Accedi")
            email = st.text_input("📧 Email", placeholder="la-tua-email@azienda.com")
            password = st.text_input("🔑 Password", type="password", placeholder="••••••••")
            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("➡️ Entra", use_container_width=True)

            if submitted:
                if not email or not password:
                    st.error("Inserisci email e password")
                else:
                    with st.spinner("Accesso in corso..."):
                        result = login(email, password)
                    if result["success"]:
                        user = result["user"]
                        profile = get_user_profile(user.id)
                        st.session_state["user"] = user.id
                        st.session_state["user_email"] = user.email
                        st.session_state["role"] = profile["role"] if profile else "client"
                        st.session_state["user_name"] = profile.get("full_name", email) if profile else email
                        st.session_state["company"] = profile.get("company_name", "") if profile else ""
                        st.success("✅ Accesso effettuato!")
                        st.rerun()
                    else:
                        err = result["error"]
                        if "Invalid login" in err or "invalid_credentials" in err:
                            st.error("❌ Email o password non corretti")
                        else:
                            st.error(f"❌ Errore: {err}")

        st.markdown("""
        <p style="text-align:center; color:#475569; font-size:0.8rem; margin-top:24px;">
            © 2026 NEXUS Finance Pro · Tutti i diritti riservati
        </p>
        """, unsafe_allow_html=True)

# ─── SIDEBAR ─────────────────────────────────────────────────
def show_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center; padding:16px 0;">
            <div style="font-size:2.5rem">💎</div>
            <div style="color:#667eea; font-weight:700; font-size:1.3rem;">NEXUS Finance Pro</div>
        </div>
        """, unsafe_allow_html=True)

        # Info utente
        role = st.session_state.get("role", "client")
        name = st.session_state.get("user_name", "Utente")
        company = st.session_state.get("company", "")
        badge = "👑 Amministratore" if role == "admin" else "🏢 Cliente"

        st.markdown(f"""
        <div style="background:#1a2340; border-radius:10px; padding:12px; margin-bottom:16px; border:1px solid #1e2d4a;">
            <div style="color:#94a3b8; font-size:0.75rem">{badge}</div>
            <div style="color:#e2e8f0; font-weight:600;">{name}</div>
            <div style="color:#64748b; font-size:0.8rem">{company}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### Navigazione")

        pages = [
            ("🏠", "Dashboard", "dashboard"),
            ("⚠️", "Analisi Rischio", "risk"),
            ("💳", "Credit Scoring", "credit"),
            ("📋", "Audit Report", "audit"),
            ("📜", "Storico", "history"),
        ]
        if role == "admin":
            pages.append(("👑", "Pannello Admin", "admin"))

        if "page" not in st.session_state:
            st.session_state["page"] = "dashboard"

        for icon, label, key in pages:
            active = "background:#1e2d4a; border-left:3px solid #667eea;" if st.session_state["page"] == key else ""
            if st.button(f"{icon}  {label}", key=f"nav_{key}", use_container_width=True):
                st.session_state["page"] = key
                st.rerun()

        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            logout()
            st.rerun()

# ─── MAIN ─────────────────────────────────────────────────────
def main():
    if not is_authenticated():
        show_login_page()
        return

    show_sidebar()

    page = st.session_state.get("page", "dashboard")

    if page == "dashboard":
        from pages_modules.dashboard import show_dashboard
        show_dashboard()
    elif page == "risk":
        from pages_modules.risk_analysis import show_risk_analysis
        show_risk_analysis()
    elif page == "credit":
        from pages_modules.credit_scoring import show_credit_scoring
        show_credit_scoring()
    elif page == "audit":
        from pages_modules.audit_report import show_audit_report
        show_audit_report()
    elif page == "history":
        from pages_modules.history import show_history
        show_history()
    elif page == "admin" and is_admin():
        from pages_modules.admin_panel import show_admin_panel
        show_admin_panel()
    else:
        st.error("Pagina non trovata")

if __name__ == "__main__":
    main()
