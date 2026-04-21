import os
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from supabase import create_client, Client

# --- CONFIGURAZIONE ---
URL_PROGETTO = "https://ipmttldwfsxuubugiyir.supabase.co"
# Qui peschiamo il NOME della variabile impostata su Render
CHIAVE_SERVICE = os.environ.get("SUPABASE_KEY")

if not CHIAVE_SERVICE:
    print("❌ ERRORE: Variabile SUPABASE_KEY non trovata su Render!")
    supabase = None
else:
    try:
        supabase: Client = create_client(URL_PROGETTO, CHIAVE_SERVICE)
        print("✅ Connessione a Supabase OK")
    except Exception as e:
        print(f"❌ Errore: {e}")
        supabase = None

app = FastAPI()
# ... resto del codice ...
