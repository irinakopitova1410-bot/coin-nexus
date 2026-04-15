from fastapi import FastAPI
from pydantic import BaseModel
from engine.scoring import compute_score, risk_label

app = FastAPI()

class Input(BaseModel):
    cash: float
    receivables: float
    inventory: float
    payables: float
    current_assets: float


@app.post("/score")
def score(data: Input):

    f = data.dict()

    score, explanation = compute_score(f)

    return {
        "score": score,
        "risk": risk_label(score),
        "explanation": explanation
    }
