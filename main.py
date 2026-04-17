import os
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from supabase import create_client, Client
import datetime

# --- CONFIGURAZIONE SICURA ---
# Queste variabili vengono lette dalle "Environment Variables" di Render
SUPABASE_URL = os.environ.get("https://ipmttldwfsxuubugiyir.supabase.co")
SUPABASE_KEY = os.environ.get("nx-live-docfinance-2026")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERRORE: Variabili SUPABASE_URL o SUPABASE_KEY non trovate su Render!")
else:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()

class ScoringRequest(BaseModel):
    company_name: str
    revenue: float
    total_assets: float
    net_income: float

@app.get("/")
def home():
    return {"status": "Nexus API is online", "version": "1.1"}

@app.post("/analyze")
async def analyze_company(request: ScoringRequest, x_api_key: str = Header(None)):
    # 1. Verifica API KEY (quella che abbiamo messo su Supabase)
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API Key mancante")
    
    # 2. Controllo Crediti su Supabase
    tenant_res = supabase.table("tenants").select("*").eq("api_key", x_api_key).execute()
    
    if not tenant_res.data:
        raise HTTPException(status_code=403, detail="API Key non valida")
    
    tenant = tenant_res.data[0]
    if tenant['credit_balance'] <= 0:
        raise HTTPException(status_code=402, detail="Crediti esauriti per questo partner")

    # 3. Logica di Calcolo (Esempio Z-Score semplificato)
    # Z = 1.2*(Working Capital/Total Assets) + ... (qui puoi mettere la tua formula reale)
    z_score = round((request.net_income / request.total_assets) * 1.5 + (request.revenue / request.total_assets) * 0.5, 2)
    pd_rate = "Basso" if z_score > 2.5 else "Medio" if z_score > 1.5 else "Alto"

    # 4. Operazioni Database: Scala Credito e Salva Log
    # Scala 1 credito al tenant
    new_balance = tenant['credit_balance'] - 1
    supabase.table("tenants").update({"credit_balance": new_balance}).eq("id", tenant['id']).execute()

    # Salva il log dell'analisi
    log_data = {
        "tenant_id": tenant['id'],
        "company_name": request.company_name,
        "z_score": z_score,
        "pd_rate": pd_rate,
        "created_at": datetime.datetime.utcnow().isoformat()
    }
    supabase.table("analysis_logs").insert(log_data).execute()

    # 5. Risposta
    return {
        "company": request.company_name,
        "z_score": z_score,
        "risk_level": pd_rate,
        "remaining_credits": new_balance
    }
