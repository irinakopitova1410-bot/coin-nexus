import os
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from supabase import create_client, Client

# Queste devono essere impostate su Render nelle Environment Variables
url = os.environ.get("https://ipmttldwfsxuubugiyir.supabase.co")
key = os.environ.get("sb_publishable_HasWDK8G-d09qqpGEA-syw_sCPBhpos")
supabase: Client = create_client(url, key)

app = FastAPI()

class ScoringRequest(BaseModel):
    company_name: str
    revenue: float
    ebitda: float
    total_debt: float

@app.post("/v1/scoring/analyze")
async def analyze(data: ScoringRequest, x_api_key: str = Header(None)):
    # 1. CERCA IL CLIENTE NELLA TABELLA CHE VEDO NELLA TUA FOTO
    res = supabase.table("tenants").select("*").eq("api_key", x_api_key).execute()
    
    if not res.data:
        raise HTTPException(status_code=403, detail="API Key non valida")
    
    tenant = res.data[0]

    # 2. CALCOLO LOGICA NEXUS
    z = (1.2 * (data.revenue * 0.1 / data.total_debt)) + (3.3 * (data.ebitda / data.total_debt))
    
    # 3. SALVA IL LOG (così la tabella analysis_logs si riempie!)
    supabase.table("analysis_logs").insert({
        "tenant_id": tenant['id'],
        "company_name": data.company_name,
        "z_score": round(z, 2)
    }).execute()

    return {
        "status": "success",
        "score": round(z, 2),
        "message": f"Analisi completata per {tenant['name']}"
    }
