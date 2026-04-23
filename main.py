from fastapi import FastAPI, BackgroundTasks, Header, HTTPException
import os
from analytics import NexusAI 

app = FastAPI()
ai_engine = NexusAI()

@app.get("/")
def home():
    return {"status": "Nexus AI Engine Online"}

@app.post("/v1/analyze") # <--- Questa riga è CRITICA
async def start_analysis(data: dict, background_tasks: BackgroundTasks, x_api_key: str = Header(None)):
    # ... resto del codice ...
    
    # 1. Verifica di Sicurezza
    if x_api_key != "nx-live-docfinance-2026":
        raise HTTPException(status_code=403, detail="Chiave API non valida")

    # 2. Registrazione Iniziale su Supabase
    try:
        res = supabase.table("analisi_rischio").insert({
            "nome_azienda": data.get("azienda"),
            "stato_rischio": "Elaborazione AI...",
            "completato": False
        }).execute()
        
        analysis_id = res.data[0]['id']
        
        # 3. Avvio calcolo pesante in background per non bloccare la risposta
        background_tasks.add_task(run_background_logic, analysis_id, data['records'])

        return {"status": "success", "id": analysis_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def run_background_logic(analysis_id: str, records: list):
    """Funzione che esegue i calcoli senza far aspettare l'utente"""
    results = ai_engine.calculate_risk(records)
    
    supabase.table("analisi_rischio").update({
        "z_score": results.get('z_score'),
        "ebitda": results.get('ebitda'),
        "ebitda_margin": results.get('ebitda_margin'),
        "stato_rischio": results.get('status'),
        "proiezioni": results.get('proiezioni'),
        "completato": True
    }).eq("id", analysis_id).execute()
