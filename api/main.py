# api/main.py
from fastapi import FastAPI
from engine.scoring import calculate_metrics
from services.decision import get_credit_approval

app = FastAPI(title="Coin-Nexus API Gateway")

@app.post("/v1/analyze")
async def analyze_and_decide(data: dict):
    # 1. Calcola indici (Engine)
    metrics = calculate_metrics(data)
    
    # 2. Prendi decisione (Services)
    decision = get_credit_approval(metrics)
    
    return {
        "status": "processed",
        "company": data.get("name"),
        "metrics": metrics,
        "bank_decision": decision
    }
