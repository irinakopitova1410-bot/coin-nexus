import streamlit as st
from supabase import create_client
import os

def get_supabase():
    url = st.secrets.get("SUPABASE_URL", os.getenv("SUPABASE_URL", ""))
    key = st.secrets.get("SUPABASE_KEY", os.getenv("SUPABASE_KEY", ""))
    return create_client(url, key)

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

def is_admin():
    return st.session_state.get("role") == "admin"

def is_authenticated():
    return st.session_state.get("user") is not None

def require_auth():
    """Forza il login se non autenticato. Ritorna True se ok."""
    return is_authenticated()
