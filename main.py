import os
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from supabase import create_client, Client

# Inizializzazione Supabase dalle variabili d'ambiente di Render
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

app = FastAPI()

class CompanyData(BaseModel):
    company_name: str
    revenue: float
    ebitda: float
    total_debt: float

@app.post("/v1/scoring/analyze")
async def analyze(data: CompanyData, x_api_key: str = Header(None)):
    # 1. VERIFICA IL CLIENTE SUL DATABASE
    res = supabase.table("tenants").select("*").eq("api_key", x_api_key).execute()
    
    if not res.data:
        raise HTTPException(status_code=403, detail="API Key non valida")
    
    tenant = res.data[0]
    
    # 2. CONTROLLO CREDITI
    if tenant['credit_balance'] <= 0:
        raise HTTPException(status_code=402, detail="Crediti esauriti")

    # 3. MOTORE DI CALCOLO NEXUS
    z = (1.2 * (data.revenue * 0.1 / data.total_debt)) + (3.3 * (data.ebitda / data.total_debt))
    pd = 1 / (1 + (z**2.5))
    
    # 4. SCALA 1 CREDITO E SALVA LOG (OPERAZIONE ATOMICA)
    new_balance = tenant['credit_balance'] - 1
    supabase.table("tenants").update({"credit_balance": new_balance}).eq("id", tenant['id']).execute()
    
    supabase.table("analysis_logs").insert({
        "tenant_id": tenant['id'],
        "company_name": data.company_name,
        "z_score": round(z, 2),
        "pd_rate": round(pd * 100, 2)
    }).execute()

    return {
        "status": "success",
        "company": data.company_name,
        "results": {
            "z_score": round(z, 2),
            "rating": "SOLIDO" if z > 2.6 else "VULNERABILE",
            "remaining_credits": new_balance
        }
    }
