import os
from fastapi import FastAPI, BackgroundTasks, Header, HTTPException
from supabase import create_client, Client
from analytics import NexusAI

app = FastAPI()
ai_engine = NexusAI()

# Connessione Supabase tramite ENV
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"), 
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")
)

@app.get("/")
def home():
    return {"status": "Nexus AI Engine Online"}

@app.post("/v1/analyze")
async def start_analysis(data: dict, background_tasks: BackgroundTasks, x_api_key: str = Header(None)):
    if x_api_key != "nx-live-docfinance-2026":
        raise HTTPException(status_code=403, detail="Chiave API Errata")

    # 1. Creazione record "In Lavorazione"
    res = supabase.table("analisi_rischio").insert({
        "nome_azienda": data.get("azienda"),
        "stato_rischio": "Analisi in corso...",
        "completato": False
    }).execute()
    
    analysis_id = res.data[0]['id']
    
    # 2. Avvio calcolo pesante in background
    background_tasks.add_task(process_data, analysis_id, data['records'])

    return {"id": analysis_id, "message": "Analisi avviata correttamente"}

def process_data(analysis_id: str, records: list):
    results = ai_engine.calculate_risk(records)
    supabase.table("analisi_rischio").update({
        "z_score": results.get('z_score'),
        "ebitda": results.get('ebitda'),
        "stato_rischio": results.get('status'),
        "proiezioni": results.get('proiezioni'),
        "completato": True
    }).eq("id", analysis_id).execute()
