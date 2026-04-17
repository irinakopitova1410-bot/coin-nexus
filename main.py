import os
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from supabase import create_client, Client
import datetime

# Prendi questi da Render -> Settings -> Environment Variables
url = os.environ.get("https://ipmttldwfsxuubugiyir.supabase.co")
key = os.environ.get("nx-live-docfinance-2026")
supabase: Client = create_client(url, key)

app = FastAPI()

class ScoringRequest(BaseModel):
    company_name: str
    revenue: float
    ebitda: float
    total_debt: float

@app.post("/v1/scoring/analyze")
async def analyze(data: ScoringRequest, x_api_key: str = Header(None)):
    # 1. Trova il cliente
    res = supabase.table("tenants").select("*").eq("api_key", x_api_key).execute()
    if not res.data:
        raise HTTPException(status_code=403, detail="API Key non valida")
    
    tenant = res.data[0]

    # 2. Calcola lo Z-Score (Logica Nexus)
    # Esempio semplificato:
    z = (1.2 * (data.revenue * 0.1 / data.total_debt)) + (3.3 * (data.ebitda / data.total_debt))
    pd = 1 / (1 + (z**2.5))

    # 3. SCRIVI NELLA TABELLA CHE STAI GUARDANDO (analysis_logs)
    supabase.table("analysis_logs").insert({
        "tenant_id": tenant['id'],
        "company_name": data.company_name,
        "z_score": round(z, 2),
        "pd_rate": round(pd * 100, 2),
        "status_code": 200
    }).execute()

    # 4. SCALA IL CREDITO
    new_balance = tenant['credit_balance'] - 1
    supabase.table("tenants").update({"credit_balance": new_balance}).eq("id", tenant['id']).execute()

    return {
        "status": "success",
        "results": {
            "score": round(z, 2),
            "rating": "SOLIDO" if z > 2.6 else "VULNERABILE",
            "credits_left": new_balance
        }
    }
