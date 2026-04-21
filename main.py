import os
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from supabase import create_client, Client
from fastapi.middleware.cors import CORSMiddleware

# --- 1. INIZIALIZZAZIONE ---
URL_PROGETTO = "https://ipmttldwfsxuubugiyir.supabase.co"
CHIAVE_SERVICE = os.environ.get("SUPABASE_KEY")

try:
    if not CHIAVE_SERVICE:
        print("❌ ERRORE: Variabile SUPABASE_KEY non trovata!")
        supabase = None
    else:
        supabase: Client = create_client(URL_PROGETTO, CHIAVE_SERVICE)
        print("✅ Connessione a Supabase OK")
except Exception as e:
    print(f"❌ Errore connessione: {e}")
    supabase = None

app = FastAPI()
@app.get("/")
def read_root():
    return {"status": "Nexus Engine Online", "message": "Benvenuto nel motore di calcolo"}
# --- 2. CORS (Per permettere a Streamlit di parlare con Render) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 3. SCHEMA DATI ---
class ScoringRequest(BaseModel):
    company_name: str
    revenue: float
    ebitda: float
    total_debt: float

# --- 4. ROTTE (Senza queste avrai errore 404) ---

@app.get("/")
def home():
    return {"status": "Nexus Engine Online", "db_connected": supabase is not None}

@app.post("/v1/scoring/analyze")
async def analyze(data: ScoringRequest, x_api_key: str = Header(None)):
    if not supabase:
        raise HTTPException(status_code=500, detail="Database non connesso")

    # Verifica API KEY del Partner (Doc-Finance)
    res = supabase.table("tenants").select("*").eq("api_key", x_api_key).execute()
    if not res.data:
        raise HTTPException(status_code=403, detail="API Key non valida")
    
    tenant = res.data[0]

    # Logica di calcolo
    debt = data.total_debt if data.total_debt > 0 else 1
    z = (1.2 * (data.revenue * 0.1 / debt)) + (3.3 * (data.ebitda / debt))
    
    try:
        # Aggiornamento saldo crediti
        nuovo_saldo = tenant['credit_balance'] - 1
        supabase.table("tenants").update({"credit_balance": nuovo_saldo}).eq("id", tenant['id']).execute()
        
        # Scrittura Log
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
