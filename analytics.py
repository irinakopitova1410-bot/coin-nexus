import os
from fastapi import FastAPI, BackgroundTasks, Header, HTTPException
from supabase import create_client, Client
from analytics import NexusAI

app = FastAPI()
ai_engine = NexusAI()

supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_ROLE_KEY"))

@app.post("/v1/analyze")
async def start_analysis(data: dict, background_tasks: BackgroundTasks, x_api_key: str = Header(None)):
    if x_api_key != "nx-live-docfinance-2026":
        raise HTTPException(status_code=403, detail="Unauthorized")

    # Registrazione iniziale su Supabase
    res = supabase.table("analisi_rischio").insert({
        "nome_azienda": data.get("azienda"),
        "stato_rischio": "Elaborazione dati finanziari..."
    }).execute()
    
    analysis_id = res.data[0]['id']
    background_tasks.add_task(run_ai_logic, analysis_id, data['records'])

    return {"status": "success", "id": analysis_id}

def run_ai_logic(analysis_id: str, records: list):
    results = ai_engine.calculate_risk(records)
    supabase.table("analisi_rischio").update({
        "z_score": results.get('z_score'),
        "ebitda": results.get('ebitda'),
        "stato_rischio": results.get('status'),
        "proiezioni": results.get('proiezioni'),
        "completato": True
    }).eq("id", analysis_id).execute()
