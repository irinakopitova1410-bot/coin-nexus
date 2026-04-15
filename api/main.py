from fastapi import FastAPI
from pydantic import BaseModel
from engine.scoring import compute_metrics
from services.decision import credit_decision

app = FastAPI(title="Coin-Nexus Risk Engine")

class CompanyData(BaseModel):
    cash: float
    receivables: float
    inventory: float
    payables: float
    ebitda: float
    debt: float


@app.post("/analyze")
def analyze(data: CompanyData):

    metrics = compute_metrics(data)
    decision = credit_decision(metrics)

    return {
        "metrics": metrics,
        "decision": decision["status"],
        "risk_score": decision["score"],
        "reason": decision["reason"]
    }
