import os
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from supabase import create_client, Client
from fastapi.middleware.cors import CORSMiddleware

# --- 1. CONFIGURAZIONE E CONNESSIONE ---
URL_PROGETTO = "https://ipmttldwfsxuubugiyir.supabase.co"
CHIAVE_SERVICE = os.environ.get("SUPABASE_KEY")

try:
    if not CHIAVE_SERVICE:
        print("❌ ERRORE: Variabile SUPABASE_KEY non trovata nelle Environment Variables!")
        supabase = None
    else:
        supabase: Client = create_client(URL_PROGETTO, CHIAVE_SERVICE)
        print("✅ Connessione a Supabase stabilita con successo.")
except Exception as e:
    print(f"❌ Errore durante l'inizializzazione di Supabase: {e}")
    supabase = None

app = FastAPI(title="Nexus Engine API")

# --- 2. MIDDLEWARE CORS ---
# Permette a Streamlit (e altri domini) di chiamare questa API senza blocchi di sicurezza
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

# --- 4. ROTTE (ENDPOINT) ---

@app.get("/")
def home():
    """Verifica se il server è online e se il DB è connesso."""
    return {
        "status": "Nexus Engine Online",
        "database_connected": supabase is not None,
        "version": "1.0.1"
    }

@app.post("/v1/scoring/analyze")
async def analyze(data: ScoringRequest, x_api_key: str = Header(None)):
    # 1. Controllo connessione DB
    if not supabase:
        raise HTTPException(status_code=500, detail="Il server non è connesso a Supabase.")

    # 2. Verifica API Key (x_api_key viene dall'header inviato da Streamlit)
    if not x_api_key:
        raise HTTPException(status_code=401, detail="X-API-KEY mancante nell'header.")

    try:
        # Cerchiamo il partner nel database
        res = supabase.table("tenants").select("*").eq("api_key", x_api_key).execute()
        
        if not res.data:
            raise HTTPException(status_code=403, detail=f"API Key '{x_api_key}' non valida.")
        
        tenant = res.data[0]
        
        # Controllo se esiste la colonna credit_balance
        if 'credit_balance' not in tenant:
            raise HTTPException(status_code=500, detail="Colonna 'credit_balance' non trovata nella tabella tenants.")

        # 3. LOGICA DI ANALISI NEXUS
        debt_val = data.total_debt if data.total_debt > 0 else 1
        z_score = (1.2 * (data.revenue * 0.1 / debt_val)) + (3.3 * (data.ebitda / debt_val))
        
        # 4. OPERAZIONI SU DATABASE (Scalamento crediti e Log)
        nuovo_saldo = int(tenant['credit_balance']) - 1
        
        # Aggiorna il saldo
        supabase.table("tenants").update({"credit_balance": nuovo_saldo}).eq("id", tenant['id']).execute()
        
        # Registra l'analisi nei log
        supabase.table("analysis_logs").insert({
            "tenant_id": tenant['id'],
            "company_name": data.company_name,
            "z_score": round(z_score, 2),
            "status_code": 200
        }).execute()

        # 5. RISPOSTA FINALE
        return {
            "status": "success",
            "results": {
                "score": round(z_score, 2),
                "rating": "SOLIDO" if z_score > 2.6 else "VULNERABILE" if z_score > 1.1 else "DISTRESSED",
                "credits_left": nuovo_saldo
            }
        }

    except Exception as e:
        # Questo cattura errori di Supabase (es. colonne mancanti) e li riporta a Streamlit
        raise HTTPException(status_code=500, detail=f"Errore interno: {str(e)}")
