import os
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from supabase import create_client, Client

# --- CONFIGURAZIONE DIRETTA (Per evitare errori 500) ---
# Usiamo l'URL fisso perché questo non cambierà mai
URL_PROGETTO = "https://ipmttldwfsxuubugiyir.supabase.co"

# Leggiamo la chiave lunga eyJ... che hai messo su Render sotto il nome SUPABASE_KEY
CHIAVE_SERVICE = os.environ.get("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlwbXR0bGR3ZnN4dXVidWdpeWlyIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NjA5NDE3MSwiZXhwIjoyMDkxNjcwMTcxfQ.hFsH0_JtDOTgsPUm-RhvcZRztXqQmafaHgfMN6WxcKk")

# Inizializzazione sicura: se la chiave non viene letta, il server lo segnala nei log
if not CHIAVE_SERVICE:
    print("ERRORE: Variabile SUPABASE_KEY non trovata su Render!")
    supabase = None
else:
    try:
        supabase: Client = create_client(URL_PROGETTO, CHIAVE_SERVICE)
        print("Connessione a Supabase stabilita correttamente.")
    except Exception as e:
        print(f"Errore durante la creazione del client Supabase: {e}")
        supabase = None

app = FastAPI()

# Definizione della struttura dati attesa
class ScoringRequest(BaseModel):
    company_name: str
    revenue: float
    ebitda: float
    total_debt: float

@app.get("/")
def home():
    return {"status": "Nexus Engine Online"}

@app.post("/v1/scoring/analyze")
async def analyze(data: ScoringRequest, x_api_key: str = Header(None)):
    # Verifica che il server sia connesso al DB
    if supabase is None:
        raise HTTPException(status_code=500, detail="Il server non è connesso a Supabase. Controlla le Environment Variables.")

    # Verifica presenza API Key nell'header
    if not x_api_key:
        raise HTTPException(status_code=401, detail="X-API-KEY mancante nell'header")

    try:
        # 1. Trova il partner tramite API KEY
        res = supabase.table("tenants").select("*").eq("api_key", x_api_key).execute()
        
        if not res.data:
            raise HTTPException(status_code=403, detail="API Key non valida o non censita")
        
        tenant = res.data[0]

        # 2. Calcolo Logica Nexus (Z-Score)
        debt = data.total_debt if data.total_debt > 0 else 1
        z = (1.2 * (data.revenue * 0.1 / debt)) + (3.3 * (data.ebitda / debt))
        pd = 1 / (1 + (z**2.5))

        # 3. Salvataggio Log
        supabase.table("analysis_logs").insert({
            "tenant_id": tenant['id'],
            "company_name": data.company_name,
            "z_score": round(z, 2),
            "pd_rate": round(pd * 100, 2),
            "status_code": 200
        }).execute()

        # 4. Scalamento Crediti
        nuovo_saldo = tenant['credit_balance'] - 1
        supabase.table("tenants").update({"credit_balance": nuovo_saldo}).eq("id", tenant['id']).execute()

        return {
            "status": "success",
            "results": {
                "score": round(z, 2),
                "rating": "SOLIDO" if z > 2.6 else "VULNERABILE" if z > 1.1 else "DISTRESSED",
                "credits_left": nuovo_saldo
            }
        }
    except Exception as e:
        # Questo cattura l'errore e ti dice esattamente cosa non va nei log di Render
        raise HTTPException(status_code=500, detail=f"Errore interno: {str(e)}")
