import streamlit as st
from supabase import create_client
import os


def get_supabase():
    url = st.secrets.get("SUPABASE_URL", os.getenv("SUPABASE_URL", ""))
    key = st.secrets.get("SUPABASE_KEY", os.getenv("SUPABASE_KEY", ""))
    return create_client(url, key)


def get_supabase_url() -> str:
    return st.secrets.get("SUPABASE_URL", os.getenv("SUPABASE_URL", ""))


def login(email: str, password: str):
    """Login utente — restituisce session o errore."""
    try:
        supabase = get_supabase()
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        return {"success": True, "session": response.session, "user": response.user}
    except Exception as e:
        return {"success": False, "error": str(e)}


def logout():
    """Logout e pulizia sessione."""
    try:
        supabase = get_supabase()
        supabase.auth.sign_out()
    except:
        pass
    for key in ["user", "session", "role", "user_email", "user_name"]:
        st.session_state.pop(key, None)


def get_user_profile(user_id: str, access_token: str = None):
    """Recupera profilo e ruolo utente da Supabase.
    
    Usa access_token per autenticare la query PostgREST — necessario
    quando la RLS richiede auth.uid() = id.
    """
    try:
        supabase = get_supabase()
        if access_token:
            # Imposta il JWT dell'utente loggato per rispettare la RLS
            supabase.postgrest.auth(access_token)
        result = supabase.table("user_profiles").select("*").eq("id", user_id).single().execute()
        return result.data
    except Exception:
        return None


def get_current_user():
    """Ritorna l'utente corrente dalla session_state, oppure None."""
    return st.session_state.get("user", None)


def is_admin():
    return st.session_state.get("role") == "admin"


def is_authenticated():
    return st.session_state.get("user") is not None


def require_auth():
    """Forza il login se non autenticato. Ritorna True se ok."""
    return is_authenticated()


def login_page():
    """Mostra la pagina di login professionale."""
    st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0D47A1 0%, #00897B 100%);
    }
    [data-testid="stSidebar"] { display: none; }
    footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        st.markdown("""
        <div style='text-align:center; padding: 2rem 0 1.5rem;'>
            <div style='font-size:3.5rem;'>📊</div>
            <div style='font-size:2rem; font-weight:800; color:white; letter-spacing:-0.5px;'>NEXUS Finance Pro</div>
            <div style='font-size:1rem; color:rgba(255,255,255,0.75); margin-top:0.3rem;'>Analisi finanziaria professionale</div>
        </div>
        """, unsafe_allow_html=True)

        with st.container():
            st.markdown("""
            <div style='background:white; border-radius:16px; padding:2rem; box-shadow:0 20px 60px rgba(0,0,0,0.3);'>
            """, unsafe_allow_html=True)

            st.markdown("### 🔐 Accedi alla piattaforma")
            email = st.text_input("Email", placeholder="la-tua-email@azienda.it", key="login_email")
            password = st.text_input("Password", type="password", placeholder="••••••••", key="login_password")

            if st.button("Accedi →", type="primary", use_container_width=True):
                if not email or not password:
                    st.error("Inserisci email e password.")
                else:
                    with st.spinner("Accesso in corso..."):
                        result = login(email, password)

                    if result["success"]:
                        user_obj = result["user"]
                        session_obj = result["session"]
                        
                        # ⚠️ IMPORTANTE: passa il token JWT al profilo
                        # così la RLS (auth.uid() = id) viene rispettata
                        access_token = session_obj.access_token if session_obj else None
                        profile = get_user_profile(user_obj.id, access_token)

                        user_data = {
                            "id": user_obj.id,
                            "email": user_obj.email,
                            "role": profile.get("role", "client") if profile else "client",
                            "full_name": profile.get("full_name", "") if profile else "",
                            "company_name": profile.get("company_name", "") if profile else "",
                            "access_token": access_token or "",
                        }

                        st.session_state["user"] = user_data
                        st.session_state["role"] = user_data["role"]
                        st.session_state["user_email"] = user_data["email"]
                        st.session_state["user_name"] = user_data["full_name"]
                        st.rerun()
                    else:
                        err = result.get("error", "Credenziali non valide")
                        st.error(f"❌ {err}")

            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
        <div style='text-align:center; color:rgba(255,255,255,0.5); font-size:0.75rem; margin-top:1.5rem;'>
        NEXUS Finance Pro v3.0 · © 2025 Irina Kopitova · Tutti i diritti riservati
        </div>
        """, unsafe_allow_html=True)
