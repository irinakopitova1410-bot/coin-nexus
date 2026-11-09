import streamlit as st
from supabase import create_client
import os


SUPABASE_URL_DEFAULT = "https://ipmttldwfsxuubugiyir.supabase.co"
SUPABASE_KEY_DEFAULT = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlwbXR0bGR3ZnN4dXVidWdpeWlyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzYwOTQxNzEsImV4cCI6MjA5MTY3MDE3MX0.HRFDqEKVCygVSKByVupgK3XGIkkpxxCyO7PH4LucPZg"

def get_supabase():
    url = st.secrets.get("SUPABASE_URL", os.getenv("SUPABASE_URL", SUPABASE_URL_DEFAULT))
    key = st.secrets.get("SUPABASE_KEY", os.getenv("SUPABASE_KEY", SUPABASE_KEY_DEFAULT))
    return create_client(url, key)


def get_supabase_url() -> str:
    return st.secrets.get("SUPABASE_URL", os.getenv("SUPABASE_URL", SUPABASE_URL_DEFAULT))


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


def get_user_profile(user_id: str):
    """Recupera profilo e ruolo utente da Supabase."""
    try:
        supabase = get_supabase()
        result = supabase.table("user_profiles").select("*").eq("id", user_id).single().execute()
        return result.data
    except:
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
    """Login Aurora — light, tipografico, con reset password."""
    _login_css = """
    <style>
    [data-testid="stSidebar"] { display: none; }
    [data-testid="stApp"] {
        background:
            radial-gradient(1100px 500px at 82% -10%, rgba(30,55,108,0.14), transparent 60%),
            radial-gradient(900px 460px at -10% 30%, rgba(233,241,235,0.85), transparent 55%),
            radial-gradient(700px 400px at 60% 115%, rgba(201,162,39,0.08), transparent 60%),
            #F6F8F6 !important;
    }
    [data-testid="stHeader"] { background: transparent !important; }
    footer { visibility: hidden; }
    .lg-kicker {
        font-family:'IBM Plex Mono', monospace; font-size:0.68rem; font-weight:600;
        letter-spacing:0.24em; text-transform:uppercase; color:#B98A2F; margin-bottom:10px;
    }
    .lg-title {
        font-family:'Playfair Display', serif; font-weight:700; line-height:1.06;
        font-size:clamp(1.9rem, 4vw, 2.9rem); color:#0B1230; letter-spacing:-0.03em; margin:0;
    }
    .lg-grad {
        background:linear-gradient(120deg,#1E376C 0%,#0034A4 48%,#B98A2F 100%);
        -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent;
    }
    .lg-sub { color:#5A6478; font-size:1.02rem; margin-top:12px; }
    .lg-chip {
        display:inline-flex; align-items:center; gap:7px; border:1px solid #E6EAF2;
        background:#fff; border-radius:999px; padding:6px 14px; font-size:0.8rem;
        font-weight:600; color:#0B1230; margin-right:8px;
    }
    .lg-footer {
        font-family:'IBM Plex Mono', monospace; font-size:0.6rem; letter-spacing:0.18em;
        text-transform:uppercase; color:rgba(11,18,48,0.4); text-align:center; margin-top:2rem;
    }
    [data-testid="stVerticalBlockBorderWrapper"] {
        background:#fff !important;
        border:1px solid #E6EAF2 !important;
        border-radius:22px !important;
        box-shadow:0 24px 70px rgba(11,18,48,0.10) !important;
    }
    </style>
    """
    st.markdown("\n".join(l for l in _login_css.splitlines() if l.strip()), unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([1.1, 1.15, 1.1])

    with col_l:
        st.markdown("""
        <div style='padding-top:14vh;'>
            <div style='display:flex; align-items:center; gap:10px; margin-bottom:34px;'>
                <div style='width:40px; height:40px; border-radius:12px;
                            background:linear-gradient(135deg,#1E376C 0%,#4A6FA5 100%);
                            display:flex; align-items:center; justify-content:center;
                            color:white; font-weight:800; font-size:19px;
                            font-family:Playfair Display, serif;'>N</div>
                <div style="font-family:'Playfair Display',serif; font-weight:700; font-size:1.35rem; color:#0B1230;">NEXUS</div>
            </div>
            <div class='lg-kicker'>Financial Intelligence Platform</div>
            <h1 class='lg-title'>La prossima generazione<br>di <span class='lg-grad'>analisi finanziaria.</span></h1>
            <p class='lg-sub'>Z-Score · Credit Readiness · Early Warning CCII · Cash Flow · Copilot AI.<br>
            Il tuo bilancio, trasformato in decisioni.</p>
            <div style='margin-top:26px;'>
                <span class='lg-chip'>⚡ Credit Readiness</span>
                <span class='lg-chip'>◆ Copilot AI</span><br><br>
                <span class='lg-chip'>🚨 Early Warning CCII</span>
                <span class='lg-chip'>🔮 What-If</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_c:
        st.markdown("<div style='height:6vh;'></div>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("<div class='lg-kicker' style='color:#5A6478;'>Area riservata</div>",
                        unsafe_allow_html=True)
            st.markdown("### Accedi alla piattaforma")
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
                        profile = get_user_profile(user_obj.id)

                        user_data = {
                            "id": user_obj.id,
                            "email": user_obj.email,
                            "role": profile.get("role", "client") if profile else "client",
                            "full_name": profile.get("full_name", "") if profile else "",
                            "company_name": profile.get("company_name", "") if profile else "",
                            "access_token": session_obj.access_token if session_obj else "",
                        }

                        st.session_state["user"] = user_data
                        st.session_state["role"] = user_data["role"]
                        st.session_state["user_email"] = user_data["email"]
                        st.session_state["user_name"] = user_data["full_name"]
                        st.rerun()
                    else:
                        err = result.get("error", "Credenziali non valide")
                        st.error(f"❌ {err}")

            with st.expander("Password dimenticata?"):
                reset_email = st.text_input("Email di recupero",
                                            placeholder="la-tua-email@azienda.it",
                                            key="reset_email")
                if st.button("Invia link di reset", use_container_width=True):
                    if not reset_email:
                        st.warning("Inserisci la tua email.")
                    else:
                        try:
                            sb = get_supabase()
                            sb.auth.reset_password_email(reset_email.strip())
                            st.success("📧 Email inviata: controlla la casella per reimpostare la password.")
                        except Exception:
                            # Risposta neutra: non rivela se l'email esiste o meno
                            st.success("📧 Email inviata: controlla la casella per reimpostare la password.")

    st.markdown("""
    <div class='lg-footer'>NEXUS v6.0 · Aurora Edition · © 2026 Irina Kopitova · Tutti i diritti riservati</div>
    """, unsafe_allow_html=True)
