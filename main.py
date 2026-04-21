import os
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client, Client

# --- CONFIGURAZIONE VARIABILI ---
# Qui NON devi scrivere i valori reali. 
# Il codice pescherà i valori che hai inserito nelle etichette di Render.
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

# Inizializzazione del database con controllo errori
try:
    if not url or not key:
        print("⚠️ ATTENZIONE: SUPABASE_URL o SUPABASE_KEY non trovate su Render!")
        supabase = None
    else:
        supabase: Client = create_client(url, key)
        print("✅ Connessione a Supabase stabilita con successo!")
except Exception as e:
    print(f"❌ Errore durante l'inizializzazione di Supabase: {e}")
    supabase = None

app = FastAPI()

# Permette a Streamlit di comunicare con Render senza blocchi di sicurezza
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Struttura dati attesa (deve combaciare con quella inviata da Streamlit)
class ScoringRequest(BaseModel):
    company_name: str
    revenue: float
    ebitda: float
    total_debt: float

@app.get("/")
def home():
    return {
        "status": "Nexus Engine Online", 
        "database_connected": supabase is not None,
        "msg": "Usa la rotta /v1/scoring/analyze per l'analisi"
    }

@app.post("/v1/scoring/analyze")
async def analyze(data: ScoringRequest, x_api_key: str = Header(None)):
    if supabase is None:
        raise HTTPException(status_code=500, detail="Il server non è connesso a Supabase. Controlla le variabili su Render.")

    if not x_api_key:
        raise HTTPException(status_code=401, detail="X-API-KEY mancante nell'header")

    try:
        # 1. Verifica Partner tramite API KEY
        res = supabase.table("tenants").select("*").eq("api_key", x_api_key).execute()
        if not res.data:
            raise HTTPException(status_code=403, detail="API Key non valida")
        
        tenant = res.data[0]

        # 2. Calcolo Z-Score
        debt = data.total_debt if data.total_debt > 0 else 1
        z = (1.2 * (data.revenue * 0.1 / debt)) + (3.3 * (data.ebitda / debt))

        # 3. Aggiornamento Database (Log e Crediti)
        # Scalo un credito
        nuovo_saldo = tenant['credit_balance'] - 1
        supabase.table("tenants").update({"credit_balance": nuovo_saldo}).eq("id", tenant['id']).execute()

        # Inserisco il log dell'analisi
        supabase.table("analysis_logs").insert({
            "tenant_id": tenant['id'],
            "company_name": data.company_name,
            "z_score": round(z, 2),
            "status_code": 200
        }).execute()

        return {
            "status": "success",
            "results": {
                "score": round(z, 2),
                "rating": "SOLIDO" if z > 2.6 else "VULNERABILE" if z > 1.1 else "DISTRESSED",
                "credits_left": nuovo_saldo
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
