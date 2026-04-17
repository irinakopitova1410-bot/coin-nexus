import os
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from supabase import create_client, Client

# CORRETTO: Cerca il nome della variabile, non il valore!
url = os.environ.get("https://ipmttldwfsxuubugiyir.supabase.co")
key = os.environ.get("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlwbXR0bGR3ZnN4dXVidWdpeWlyIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NjA5NDE3MSwiZXhwIjoyMDkxNjcwMTcxfQ.hFsH0_JtDOTgsPUm-RhvcZRztXqQmafaHgfMN6WxcKk")

# Protezione contro il crash
if not url or not key:
    supabase = None
    print("ATTENZIONE: Variabili SUPABASE_URL o SUPABASE_KEY mancanti!")
else:
    supabase: Client = create_client(url, key)

app = FastAPI()
class ScoringRequest(BaseModel):
    company_name: str
    revenue: float
    ebitda: float
    total_debt: float

@app.post("/v1/scoring/analyze")
async def analyze(data: ScoringRequest, x_api_key: str = Header(None)):
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API Key mancante nell'header")

    # 1. Trova il cliente (tenant)
    res = supabase.table("tenants").select("*").eq("api_key", x_api_key).execute()
    if not res.data:
        raise HTTPException(status_code=403, detail="API Key non valida")
    
    tenant = res.data[0]

    # Controllo crediti residui
    if tenant['credit_balance'] <= 0:
        raise HTTPException(status_code=402, detail="Crediti esauriti")

    # 2. Calcolo Logica Nexus (Z-Score)
    # Evitiamo divisioni per zero se total_debt è 0
    debt = data.total_debt if data.total_debt > 0 else 1
    z = (1.2 * (data.revenue * 0.1 / debt)) + (3.3 * (data.ebitda / debt))
    pd = 1 / (1 + (z**2.5))

    # 3. Scrittura Log su Supabase
    supabase.table("analysis_logs").insert({
        "tenant_id": tenant['id'],
        "company_name": data.company_name,
        "z_score": round(z, 2),
        "pd_rate": round(pd * 100, 2),
        "status_code": 200
    }).execute()

    # 4. Scalamento Credito
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
