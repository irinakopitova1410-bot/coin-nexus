import os
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from supabase import create_client, Client
from typing import List, Optional

app = FastAPI()

# Configurazione Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") # Assicurati che su Render si chiami così!
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Modello dati per la richiesta di salvataggio
class SaveDataRequest(BaseModel):
    tenant_id: str
    data: List[dict]

@app.get("/")
async def root():
    return {"message": "Backend Nexus attivo!"}

# --- QUESTO È IL PUNTO CRITICO ---
# Se Streamlit cerca /save-to-supabase, il nome qui deve essere identico
@app.post("/save-to-supabase")
async def save_to_supabase(request: SaveDataRequest, x_api_key: str = Header(None)):
    # 1. Verifica API Key (Sicurezza)
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API Key mancante")
    
    # 2. Verifica se il tenant esiste
    tenant = supabase.table("tenants").select("*").eq("api_key", x_api_key).execute()
    if not tenant.data:
        raise HTTPException(status_code=403, detail="Accesso negato: API Key non valida")

    # 3. Salvataggio dati
    try:
        # Aggiungiamo il tenant_id a ogni riga di dati
        for item in request.data:
            item["tenant_id"] = tenant.data[0]["id"]
            
        response = supabase.table("financial_data").insert(request.data).execute()
        return {"status": "success", "message": "Dati salvati correttamente su Supabase"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint per l'analisi (quello che dà il rating)
@app.post("/analyze-finance")
async def analyze_finance(request: dict, x_api_key: str = Header(None)):
    # Qui va la logica dello Z-Score che abbiamo visto prima
    return {"status": "success", "rating": "Solido"}
