"""Legacy API entry point; financial scoring requires a validated full model."""
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel, ConfigDict, Field

app = FastAPI()


class ScoringRequest(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False)
    company_name: str = Field(min_length=1, max_length=250)
    revenue: float = Field(ge=0)
    ebitda: float
    total_debt: float = Field(ge=0)


@app.post("/v1/scoring/analyze")
async def analyze(data: ScoringRequest, x_api_key: str = Header(None)):
    # The previous three-field approximation was not an Altman Z-Score or
    # validated PD. Never persist or charge for its results.
    raise HTTPException(status_code=503, detail=(
        "Endpoint legacy sospeso: modello non validato. "
        "Usare il flusso di analisi completo; nessun credito è stato addebitato."
    ))
