import os
from fastapi import FastAPI, BackgroundTasks, Header, HTTPException
from supabase import create_client, Client
from analytics import NexusAI  # Assicurati che il tuo file analytics.py sia presente

app = FastAPI()
ai_engine = NexusAI()

# Configurazione Supabase
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(url, key)

@app.post("/v1/analyze")
async def start_analysis(data: dict, background_tasks: BackgroundTasks, x_api_key: str = Header(None)):
    # Controllo Chiave di Sicurezza
    if x_api_key != "nx-live-docfinance-2026":
        raise HTTPException(status_code=403, detail="Chiave non autorizzata")

    # 1. Registra l'inizio dell'analisi su Supabase
    res = supabase.table("analisi_rischio").insert({
        "nome_azienda": data.get("azienda", "Sconosciuta"),
        "stato_rischio": "In elaborazione..."
    }).execute()
    
    analysis_id = res.data[0]['id']

    # 2. Avvia il calcolo AI in background (senza bloccare il sito)
    background_tasks.add_task(run_ai_logic, analysis_id, data['records'])

    return {
        "status": "success", 
        "id": analysis_id, 
        "message": "Analisi avviata correttamente"
    }

def run_ai_logic(analysis_id: str, records: list):
    try:
        # Esegue i calcoli pesanti (Z-Score, TensorFlow, ecc.)
        results = ai_engine.calculate_risk(records)
        
        # 3. Aggiorna Supabase con i risultati finali
        supabase.table("analisi_rischio").update({
            "z_score": results.get('z_score'),
            "stato_rischio": results.get('status'),
            "completato": True
        }).eq("id", analysis_id).execute()
        
    except Exception as e:
        # In caso di errore, lo logghiamo su Supabase
        supabase.table("analisi_rischio").update({
            "stato_rischio": f"Errore: {str(e)}",
            "completato": False
        }).eq("id", analysis_id).execute()
