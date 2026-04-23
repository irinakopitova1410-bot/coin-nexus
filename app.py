import streamlit as st

st.set_page_config(
    page_title="NEXUS Finance Pro",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #0F172A; }
[data-testid="stSidebar"] { background: linear-gradient(180deg,#0F172A 0%,#1E293B 100%) !important; border-right: 1px solid #334155; }
[data-testid="stHeader"] { background: transparent; }
.stButton > button { border-radius: 8px; font-weight: 600; transition: all 0.2s; }
.stButton > button[kind="primary"] { background: linear-gradient(135deg,#1E40AF,#7C3AED) !important; border: none; color: white !important; }
.stTextInput > div > div > input { background: #1E293B; border: 1px solid #334155; color: #F1F5F9; border-radius: 8px; }
.stNumberInput > div > div > input { background: #1E293B; border: 1px solid #334155; color: #F1F5F9; }
.stSelectbox > div > div { background: #1E293B; border-color: #334155; color: #F1F5F9; }
.stTabs [data-baseweb="tab"] { background: #1E293B; color: #94A3B8; border-radius: 8px 8px 0 0; }
.stTabs [aria-selected="true"] { background: #3B82F6; color: white; }
div[data-testid="metric-container"] { background: #1E293B; border: 1px solid #334155; border-radius: 12px; padding: 15px; }
div[data-testid="metric-container"] label { color: #94A3B8 !important; }
div[data-testid="metric-container"] div[data-testid="metric-value"] { color: #3B82F6 !important; }
.stDataFrame { background: #1E293B; }
h1,h2,h3,h4 { color: #F1F5F9 !important; }
p, label, .stMarkdown { color: #CBD5E1; }
.stSlider > div { color: #F1F5F9; }
hr { border-color: #334155; }
</style>
""", unsafe_allow_html=True)


def login_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align:center;padding:50px 0 30px 0;">
            <div style="font-size:4rem;">💎</div>
            <h1 style="color:#3B82F6;font-size:2.5rem;margin:0;">NEXUS Finance Pro</h1>
            <p style="color:#64748B;font-size:1.1rem;margin-top:8px;">Piattaforma Enterprise di Analisi Finanziaria</p>
            <div style="display:flex;justify-content:center;gap:8px;margin:15px 0;flex-wrap:wrap;">
                <span style="background:#1E3A8A;color:#93C5FD;padding:4px 12px;border-radius:20px;font-size:0.8rem;">⚠️ Z-Score Altman</span>
                <span style="background:#164E63;color:#7DD3FC;padding:4px 12px;border-radius:20px;font-size:0.8rem;">💳 Credit Scoring Basel IV</span>
                <span style="background:#2E1065;color:#C4B5FD;padding:4px 12px;border-radius:20px;font-size:0.8rem;">📊 Audit ISA 320</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login"):
            api_key = st.text_input("🔑 API Key", type="password", placeholder="Inserisci la tua API Key aziendale")
            login_btn = st.form_submit_button("🚀 Accedi alla Piattaforma", use_container_width=True, type="primary")
            if login_btn:
                if api_key:
                    from services.db import verify_api_key
                    tenant = verify_api_key(api_key)
                    if tenant:
                        st.session_state.authenticated = True
                        st.session_state.tenant = tenant
                        st.rerun()
                    else:
                        st.error("❌ API Key non valida.")
                else:
                    st.warning("Inserisci la tua API Key.")

        st.markdown("""
        <div style="text-align:center;margin-top:30px;color:#334155;font-size:0.8rem;">
            <p>🔒 SSL • GDPR Compliant • Powered by Supabase</p>
            <p>© 2025 NEXUS Finance Pro</p>
        </div>
        """, unsafe_allow_html=True)


def sidebar_nav():
    tenant = st.session_state.get("tenant", {})
    with st.sidebar:
        st.markdown(f"""
        <div style="padding:15px 0;border-bottom:1px solid #334155;margin-bottom:15px;">
            <div style="text-align:center;">
                <div style="font-size:2rem;">💎</div>
                <div style="color:#3B82F6;font-weight:700;font-size:1.1rem;">NEXUS Finance Pro</div>
                <div style="color:#64748B;font-size:0.75rem;">Enterprise Edition v2.0</div>
            </div>
            <div style="background:#0F172A;border-radius:8px;padding:10px;margin-top:15px;">
                <div style="color:#CBD5E1;font-size:0.85rem;">👤 {tenant.get('name','Utente')}</div>
                <div style="color:#64748B;font-size:0.75rem;margin-top:4px;">
                    💳 Crediti: <span style="color:#4ADE80;">{tenant.get('credit_balance',0)}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        page = st.radio(
            "nav",
            ["🏠 Dashboard", "⚠️ Analisi Rischio", "💳 Credit Scoring", "📊 Audit Report", "📋 Storico"],
            label_visibility="hidden"
        )

        st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()

        st.markdown("""
        <div style="position:fixed;bottom:20px;left:0;width:280px;text-align:center;color:#334155;font-size:0.7rem;">
            NEXUS Finance Pro v2.0<br>Supabase + Streamlit
        </div>
        """, unsafe_allow_html=True)
    return page


def main():
    if not st.session_state.get("authenticated", False):
        login_page()
        return

    page = sidebar_nav()

    if page == "🏠 Dashboard":
        from pages_modules.dashboard import show_dashboard
        show_dashboard()
    elif page == "⚠️ Analisi Rischio":
        from pages_modules.risk_analysis import show_risk_analysis
        show_risk_analysis()
    elif page == "💳 Credit Scoring":
        from pages_modules.credit_scoring import show_credit_scoring
        show_credit_scoring()
    elif page == "📊 Audit Report":
        from pages_modules.audit_report import show_audit_report
        show_audit_report()
    elif page == "📋 Storico":
        from pages_modules.history import show_history
        show_history()


if __name__ == "__main__":
    main()
