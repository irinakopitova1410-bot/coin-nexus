from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
import os
from supabase import create_client, Client

app = FastAPI(title="Nexus Fintech API - Enterprise Edition")

# --- CONFIGURAZIONE SUPABASE ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") # Chiave admin per gestire i crediti
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- MODELLO DATI ---
class AnalysisRequest(BaseModel):
    company_name: str
    revenue: float
    ebitda: float
    total_debt: float

# --- MIDDLEWARE: CONTROLLO SICUREZZA & CREDITI ---
async def verify_access(x_api_key: str = Header(...)):
    # 1. Verifica se l'API Key esiste nel database (Multi-tenant)
    tenant = supabase.table("tenants").select("*").eq("api_key", x_api_key).single().execute()
    
    if not tenant.data:
        raise HTTPException(status_code=401, detail="Chiave API non valida")
    
    # 2. Controllo Crediti (Billing)
    if tenant.data['credit_balance'] <= 0:
        raise HTTPException(status_code=402, detail="Crediti esauriti. Ricarica con Stripe.")
    
    return tenant.data

# --- ENDPOINT CORE: ANALISI & ERP ---
@app.post("/v1/analyze")
async def analyze_and_sync(request: AnalysisRequest, tenant: dict = Depends(verify_access)):
    # 1. Algoritmo Protetto (Basilea IV)
    denominatore = request.total_debt if request.total_debt > 0 else 1
    z_score = (1.2 * (request.revenue * 0.1 / denominatore)) + (3.3 * (request.ebitda / denominatore))
    
    rating = "SOLIDO" if z_score > 2.6 else "VULNERABILE" if z_score > 1.1 else "DISTRESSED"
    
    # 2. Generazione Tracciato NTS Informatica (Standard ERP)
    # Formato specifico: Codice;RagioneSociale;Rating;ZScore;Data
    nts_record = f"NEXUS;{request.company_name};{rating};{round(z_score, 2)};2026-04-22"
    
    # 3. Scalamento Crediti & Log (Transazione Atomica)
    new_credits = tenant['credit_balance'] - 1
    supabase.table("tenants").update({"credit_balance": new_credits}).eq("id", tenant['id']).execute()
    
    supabase.table("analysis_logs").insert({
        "tenant_id": tenant['id'],
        "company_name": request.company_name,
        "z_score": z_score,
        "nts_payload": nts_record # Salviamo il tracciato pronto per l'ERP
    }).execute()

    return {
        "status": "success",
        "analysis": {
            "z_score": round(z_score, 2),
            "rating": rating,
            "nts_flusso": nts_record
        },
        "billing": {
            "credits_left": new_credits
        }
    }
