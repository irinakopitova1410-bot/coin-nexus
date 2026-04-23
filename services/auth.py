"""
NEXUS Finance Pro — Auth Service
Login con Supabase Auth, gestione ruoli admin/client.
"""
import streamlit as st
from supabase import create_client, Client
import os

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")


def get_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def get_authed_client(access_token: str) -> Client:
    """Crea client Supabase con JWT dell'utente loggato (per RLS)."""
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    client.postgrest.auth(access_token)
    return client


def get_user_profile(user_id: str, access_token: str) -> dict:
    """Legge il profilo da user_profiles usando il JWT dell'utente."""
    try:
        client = get_authed_client(access_token)
        result = client.table("user_profiles").select("*").eq("id", user_id).single().execute()
        if result.data:
            return result.data
    except Exception:
        pass
    # Fallback: usa service key (solo se RLS ancora non configurato)
    try:
        client = get_supabase()
        result = client.table("user_profiles").select("*").eq("id", user_id).execute()
        if result.data:
            return result.data[0]
    except Exception:
        pass
    return None


def login_page():
    """Pagina di login professionale."""
    st.markdown("""
    <style>
    .main { background: linear-gradient(135deg, #0D47A1 0%, #1565C0 50%, #0097A7 100%); }
    .block-container { max-width: 420px; margin: auto; padding-top: 80px; }
    .login-card {
        background: white;
        border-radius: 16px;
        padding: 40px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    }
    .login-title {
        text-align: center;
        font-size: 28px;
        font-weight: 800;
        color: #0D47A1;
        margin-bottom: 8px;
    }
    .login-subtitle {
        text-align: center;
        color: #666;
        margin-bottom: 30px;
        font-size: 14px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="login-title">NEXUS Finance Pro</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-subtitle">Analisi Finanziaria Professionale</div>', unsafe_allow_html=True)
    st.markdown("---")

    email = st.text_input("Email", placeholder="nome@azienda.it", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Accedi", type="primary", use_container_width=True):
        if not email or not password:
            st.error("Inserisci email e password.")
            return
        try:
            supabase = get_supabase()
            response = supabase.auth.sign_in_with_password({"email": email, "password": password})

            if response.user:
                user = response.user
                session = response.session
                access_token = session.access_token if session else None

                # Leggi profilo con JWT dell'utente (rispetta RLS)
                profile = get_user_profile(user.id, access_token) if access_token else None

                st.session_state["user"] = {
                    "id": user.id,
                    "email": user.email,
                    "role": profile.get("role", "client") if profile else "client",
                    "full_name": profile.get("full_name", "") if profile else "",
                    "company_name": profile.get("company_name", "") if profile else "",
                    "tenant_id": profile.get("tenant_id") if profile else None,
                    "access_token": access_token,
                }
                st.success("Accesso effettuato!")
                st.rerun()
            else:
                st.error("Email o password non corretti.")
        except Exception as e:
            err = str(e).lower()
            if "invalid" in err or "wrong" in err or "credentials" in err:
                st.error("Email o password non corretti.")
            else:
                st.error(f"Errore di connessione: {e}")


def get_current_user() -> dict:
    """Ritorna l'utente dalla session state, o None se non loggato."""
    return st.session_state.get("user", None)


def logout():
    """Logout: pulisce la session state."""
    for key in ["user", "erp_data", "erp_company"]:
        st.session_state.pop(key, None)
    try:
        get_supabase().auth.sign_out()
    except Exception:
        pass
    st.rerun()
