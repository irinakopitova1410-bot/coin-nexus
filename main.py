import os
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from typing import List, Optional
from supabase import create_client, Client

app = FastAPI(title="Nexus Finance Multi-Task Backend")

# --- CONFIGURAZIONE SUPABASE ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") # Assicurati che su Render si chiami così!

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ATTENZIONE: Variabili d'ambiente Supabase mancanti!")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

# --- MODELLI DATI ---
class FinancialRow(BaseModel):
    # Campi flessibili per accogliere i dati ERP/Excel
    id_operazione: Optional[str] = None
    descrizione: Optional[str] = None
    importo: Optional[float] = 0.0
    data: Optional[str] = None
    categoria: Optional[str] = None
    # Aggiungi qui altri campi se il tuo Excel ha colonne specifiche

class MultiTaskRequest(BaseModel):
    data: List[dict]

# --- UTILS: CALCOLO RISCHIO (Z-SCORE) ---
def calculate_altman_z_score(data: List[dict]):
    """
    Logica semplificata per il calcolo del rischio.
    In un caso reale, qui mappiamo le colonne del bilancio.
    """
    # Esempio di calcolo basato sulla media degli importi o logica specifica
    # Per ora restituiamo uno score simulato basato sull'analisi dei record
    count = len(data)
    if count > 0:
        return 2.85  # Valore di esempio: "Zona Grigia/Sicura"
    return 0.0

# --- ENDPOINTS ---

@app.get("/")
async def root():
    return {"status": "online", "system": "Nexus Multi-Task v1.0"}

# 1. TASK: ANALISI RISCHIO
@app.post("/analyze-finance")
async def analyze_finance(request: MultiTaskRequest, x_api_key: str = Header(None)):
    if x_api_key != "nx-live-docfinance-2026":
        raise HTTPException(status_code=4
