from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel

app = FastAPI()

# Definiamo cosa deve inviarci Doc-Finance (lo schema dati)
class CompanyData(BaseModel):
    revenue: float
    ebitda: float
    total_debt: float

# Simuliamo una chiave di accesso per Doc-Finance
VALID_API_KEY = "nx-live-docfinance-2026"

@app.get("/")
def home():
    return {"message": "Nexus Credit API is Online"}

@app.post("/v1/scoring/analyze")
async def analyze(data: CompanyData, x_api_key: str = Header(None)):
    # Controllo sicurezza: se la chiave è sbagliata, blocca tutto
    if x_api_key != VALID_API_KEY:
        raise HTTPException(status_code=403, detail="Chiave API non valida")

    # IL MOTORE DI CALCOLO (Il tuo valore intellettuale)
    z = (1.2 * (data.revenue * 0.1 / data.total_debt)) + (3.3 * (data.ebitda / data.total_debt))
    pd = 1 / (1 + (z**2.5)) # Probabilità di Default
    
    return {
        "status": "success",
        "results": {
            "z_score": round(z, 2),
            "probability_of_default": f"{round(pd * 100, 2)}%",
            "rating": "A" if z > 2.6 else "B" if z > 1.1 else "D",
            "suggested_rate": f"{round((0.05 + pd) * 100, 2)}%"
        }
    }
