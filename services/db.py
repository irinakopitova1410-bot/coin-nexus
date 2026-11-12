import streamlit as st
from supabase import create_client, Client
from typing import Optional, Dict, List
import datetime
import jwt as pyjwt
import os

_SUPABASE_URL = "https://ipmttldwfsxuubugiyir.supabase.co"
_SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlwbXR0bGR3ZnN4dXVidWdpeWlyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzYwOTQxNzEsImV4cCI6MjA5MTY3MDE3MX0.HRFDqEKVCygVSKByVupgK3XGIkkpxxCyO7PH4LucPZg"

def get_supabase_config():
    """Allow environment-only deployments even when secrets.toml is absent."""
    def setting(name, default):
        try:
            value = st.secrets.get(name)
        except (FileNotFoundError, KeyError):
            value = None
        return value or os.getenv(name) or default
    return setting("SUPABASE_URL", _SUPABASE_URL), setting("SUPABASE_KEY", _SUPABASE_KEY)


def get_supabase() -> Client:
    url, key = get_supabase_config()
    return create_client(url, key)

def get_auth_supabase(access_token: str = None) -> Client:
    """Client Supabase con JWT utente — necessario per RLS."""
    url, key = get_supabase_config()
    client = create_client(url, key)
    if access_token:
        client.postgrest.auth(access_token)
    return client

def _extract_user_id(access_token: str) -> Optional[str]:
    """Estrae user_id dal JWT senza verificare firma."""
    try:
        if not access_token:
            return None
        payload = pyjwt.decode(access_token, options={"verify_signature": False})
        return payload.get("sub")
    except Exception:
        return None

def verify_api_key(api_key: str) -> Optional[Dict]:
    try:
        sb = get_supabase()
        # Via RPC (la tabella tenants è protetta da RLS)
        try:
            res = sb.rpc("verify_api_key", {"p_api_key": api_key}).execute()
            if res.data:
                return res.data[0] if isinstance(res.data, list) else res.data
            return None
        except Exception:
            pass
        # Fallback legacy: SELECT diretta (funziona solo senza RLS)
        res = sb.table("tenants").select("*").eq("api_key", api_key).execute()
        if res.data:
            return res.data[0]
        return None
    except Exception as e:
        st.error(f"Errore connessione DB: {e}")
        return None

def get_dashboard_stats(tenant_id: str) -> Dict:
    sb = get_supabase()
    stats = {"risk": 0, "credit": 0, "audit": 0}
    try:
        r = sb.table("analisi_rischio").select("id", count="exact").execute()
        stats["risk"] = r.count or 0
    except: pass
    try:
        r = sb.table("credit_reports").select("id", count="exact").execute()
        stats["credit"] = r.count or 0
    except: pass
    try:
        r = sb.table("audit_reports").select("id", count="exact").execute()
        stats["audit"] = r.count or 0
    except: pass
    return stats

def get_recent_analyses(table: str, limit: int = 5, access_token: str = None) -> List[Dict]:
    if not access_token or table not in {"analisi_rischio", "credit_reports", "audit_reports"}:
        return []
    try:
        sb = get_auth_supabase(access_token) if access_token else get_supabase()
        res = sb.table(table).select("*").order("created_at", desc=True).limit(limit).execute()
        return res.data or []
    except:
        return []

def save_risk_analysis(data: Dict, access_token: str = None) -> bool:
    """Salva analisi rischio. Mappa i campi sul formato corretto della tabella."""
    if not access_token:
        return False
    try:
        sb = get_auth_supabase(access_token) if access_token else get_supabase()
        user_id = _extract_user_id(access_token)
        if not user_id:
            return False

        # Mappa campi: la tabella usa 'nome_azienda' (NOT NULL) non 'company_name'
        row = {
            "nome_azienda": data.get("company_name") or data.get("nome_azienda") or "Azienda",
            "z_score": data.get("z_score"),
            "zone": data.get("zone"),
            "stato_rischio": data.get("zone"),
            "bankruptcy_probability": data.get("bankruptcy_probability"),
            "rating": data.get("rating"),
            "model": data.get("model"),
            "total_assets": data.get("total_assets"),
            "revenue": data.get("revenue"),
            "ebit": data.get("ebit"),
            "ebitda": data.get("ebitda"),
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
        if user_id:
            row["user_id"] = user_id

        sb.table("analisi_rischio").insert(row).execute()
        return True
    except Exception as e:
        st.warning(f"Salvataggio storico non disponibile: {e}")
        return False

def save_credit_report(data: Dict, access_token: str = None) -> bool:
    """Salva credit report — resiliente: prova il payload completo, poi senza
    colonne opzionali, poi il minimo garantito. Usa raw_data (jsonb) per i metadati."""
    if not access_token:
        return False
    try:
        sb = get_auth_supabase(access_token) if access_token else get_supabase()
        user_id = _extract_user_id(access_token)
        if not user_id:
            return False

        raw = dict(data.get("raw_data") or {})
        payload = {k: v for k, v in data.items() if k != "raw_data"}
        payload["created_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        if user_id:
            payload["user_id"] = user_id
            raw.setdefault("saved_for_user", user_id)
        if raw:
            payload["raw_data"] = raw

        try:
            sb.table("credit_reports").insert(payload).execute()
            return True
        except Exception:
            # Never retry by stripping ownership or financial evidence.
            # The current database contains both user_id and raw_data.
            st.warning("Report non salvato. Verifica schema, permessi e sessione; nessun dato di proprietà è stato rimosso.")
            return False
    except Exception as e:
        st.warning(f"Salvataggio credit report non disponibile: {e}")
        return False

def save_audit_report(data: Dict, access_token: str = None) -> bool:
    if not access_token:
        return False
    try:
        data = dict(data)
        sb = get_auth_supabase(access_token) if access_token else get_supabase()
        data["created_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        user_id = _extract_user_id(access_token)
        if not user_id:
            return False
        if user_id:
            data["user_id"] = user_id
        sb.table("audit_reports").insert(data).execute()
        return True
    except Exception as e:
        st.warning(f"Salvataggio audit report non disponibile: {e}")
        return False

def get_all_history(access_token: str = None) -> Dict[str, List]:
    result = {}
    for tbl in ["analisi_rischio", "credit_reports", "audit_reports"]:
        result[tbl] = get_recent_analyses(tbl, 100, access_token)
    return result
