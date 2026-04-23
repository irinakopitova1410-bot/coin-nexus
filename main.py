import os
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from typing import List
from supabase import create_client, Client

app = FastAPI()

# Configurazione Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") # Deve chiamarsi così su Render!
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class AnalysisRequest(BaseModel):
    data: List[dict]

@app.get("/")
async def root():
    return {"status": "online", "message": "Nexus Backend is running"}

# --- ENDPOINT ANALISI ---
@app.post("/analyze-finance")
async def analyze_finance(request: AnalysisRequest, x_api_key: str = Header(None)):
    if x_api_key != "nx-live-docfinance-2026":
        raise HTTPException(status_code=403, detail="API Key non valida")
    
    # Logica di esempio Z-Score
    return {"status": "success", "rating": "Solido", "score": 2.85}

# --- ENDPOINT SALVATAGGIO ---
@app.post("/save-to-supabase")
async def save_to_supabase(request: AnalysisRequest, x_api_key: str = Header(None)):
    if x_api_key != "nx-live-docfinance-2026":
        raise HTTPException(status_code=403, detail="API Key non valida")
    
    try:
        # Recupera ID del tenant
        res = supabase.table("tenants").select("id").eq("api_key", x_api_key).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="Tenant non trovato")
        
        tenant_id = res.data[0]["id"]
        for row in request.data:
            row["tenant_id"] = tenant_id
            
        supabase.table("financial_data").insert(request.data).execute()
        return {"status": "success", "message": "Dati salvati"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
