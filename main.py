import os
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from typing import List
from supabase import create_client, Client

app = FastAPI()

# Inizializzazione Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") 
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class DataRequest(BaseModel):
    data: List[dict]

@app.get("/")
async def health_check():
    return {"status": "online", "message": "Nexus Backend Pronto"}

# --- QUESTI NOMI DEVONO ESSERE IDENTICI IN STREAMLIT ---
@app.post("/analyze-finance")
async def analyze(request: DataRequest, x_api_key: str = Header(None)):
    if x_api_key != "nx-live-docfinance-2026":
        raise HTTPException(status_code=403, detail="Key Errata")
    return {"status": "success", "rating": "Solido", "score": 2.85}

@app.post("/save-to-supabase")
async def save(request: DataRequest, x_api_key: str = Header(None)):
    if x_api_key != "nx-live-docfinance-2026":
        raise HTTPException(status_code=403, detail="Key Errata")
    try:
        # Recupero ID Tenant
        res = supabase.table("tenants").select("id").eq("api_key", x_api_key).execute()
        tenant_id = res.data[0]["id"]
        for row in request.data:
            row["tenant_id"] = tenant_id
        supabase.table("financial_data").insert(request.data).execute()
        return {"status": "success", "message": "Dati salvati"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
