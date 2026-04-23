import streamlit as st
from supabase import create_client, Client
from typing import Optional, Dict, List
import datetime

@st.cache_resource
def get_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

def verify_api_key(api_key: str) -> Optional[Dict]:
    try:
        sb = get_supabase()
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

def get_recent_analyses(table: str, limit: int = 5) -> List[Dict]:
    try:
        sb = get_supabase()
        res = sb.table(table).select("*").order("created_at", desc=True).limit(limit).execute()
        return res.data or []
    except:
        return []

def save_risk_analysis(data: Dict) -> bool:
    try:
        sb = get_supabase()
        data["created_at"] = datetime.datetime.utcnow().isoformat()
        sb.table("analisi_rischio").insert(data).execute()
        return True
    except Exception as e:
        st.error(f"Errore salvataggio: {e}")
        return False

def save_credit_report(data: Dict) -> bool:
    try:
        sb = get_supabase()
        data["created_at"] = datetime.datetime.utcnow().isoformat()
        sb.table("credit_reports").insert(data).execute()
        return True
    except Exception as e:
        st.error(f"Errore salvataggio: {e}")
        return False

def save_audit_report(data: Dict) -> bool:
    try:
        sb = get_supabase()
        data["created_at"] = datetime.datetime.utcnow().isoformat()
        sb.table("audit_reports").insert(data).execute()
        return True
    except Exception as e:
        st.error(f"Errore salvataggio: {e}")
        return False

def get_all_history() -> Dict[str, List]:
    result = {}
    for tbl in ["analisi_rischio", "credit_reports", "audit_reports"]:
        result[tbl] = get_recent_analyses(tbl, 100)
    return result
