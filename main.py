import os
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client, Client

# --- 1. CONFIGURAZIONE VARIABILI (LEGGE DA RENDER) ---
# Qui NON incollare l'URL o la Chiave. Il codice le cercherà nelle etichette di Render.
url = os.environ.get("https://ipmttldwfsxuubugiyir.supabase.co")
key = os.environ.get("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlwbXR0bGR3ZnN4dXVidWdpeWlyIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NjA5NDE3MSwiZXhwIjoyMDkxNjcwMTcxfQ.hFsH0_JtDOTgsPUm-RhvcZRztXqQmafaHgfMN6WxcKk")

# Inizializzazione sicura
if not url or not key:
    print("ERRORE: Variabili d'ambiente SUPABASE_URL o SUPABASE_KEY non trovate!")
    supabase = None
else:
    supabase: Client = create_client(url, key)

app = FastAPI()

# --- 2. ABILITAZIONE COMUNICAZIONE (CORS) ---
# Fondamentale per permettere a Streamlit di chiamare l'API di Render
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 3. MODELLO DATI ---
class ScoringRequest(BaseModel):
    company_name: str
    revenue: float
    ebitda: float
    total_debt: float

@app.get("/")
def home():
    return {"status": "Nexus Engine Online", "supabase_connected": supabase is not None}

# --- 4. MOTORE DI ANALISI ---
@app.post("/v1/scoring/analyze")
async def analyze(data: ScoringRequest, x_api_key: str = Header(None)):
    if supabase is None:
        raise HTTPException(status_code=500, detail="Il server non è connesso a Supabase.")
    
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API Key mancante")

    try:
        # 1. Verifica Partner
        res = supabase.table("tenants").select("*").eq("api_key", x_api_key).execute()
        if not res.data:
            raise HTTPException(status_code=403, detail="API Key non valida")
        
        tenant = res.data[0]

        # 2. Calcolo Logica (Z-Score)
        debt = data.total_debt if data.total_debt > 0 else 1
        z = (1.2 * (data.revenue * 0.1 / debt)) + (3.3 * (data.ebitda / debt))
        pd = 1 / (1 + (z**2.5))

        # 3. Log dell'analisi
        supabase.table("analysis_logs").insert({
            "tenant_id": tenant['id'],
            "company_name": data.company_name,
            "z_score": round(z, 2),
            "pd_rate": round(pd * 100, 2),
            "status_code": 200
        }).execute()

        # 4. Scalamento Crediti
        new_balance = tenant['credit_balance'] - 1
        supabase.table("tenants").update({"credit_balance": new_balance}).eq("id", tenant['id']).execute()

        return {
            "status": "success",
            "results": {
                "score": round(z, 2),
                "rating": "SOLIDO" if z > 2.6 else "VULNERABILE" if z > 1.1 else "DISTRESSED",
                "credits_left": new_balance
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
