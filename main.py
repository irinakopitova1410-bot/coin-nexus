import os
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from supabase import create_client, Client

# --- CONFIGURAZIONE ---
# L'URL è pubblico, va bene lasciarlo qui.
URL_PROGETTO = "https://ipmttldwfsxuubugiyir.supabase.co"

# CORREZIONE: Qui os.environ.get deve cercare il NOME della variabile su Render, 
# non il valore lungo eyJ...
CHIAVE_SERVICE = os.environ.get("SUPABASE_KEY")

if not CHIAVE_SERVICE:
    print("❌ ERRORE: Variabile SUPABASE_KEY non trovata su Render!")
    supabase = None
else:
    try:
        # Qui Python usa la chiave che ha pescato da Render
        supabase: Client = create_client(URL_PROGETTO, CHIAVE_SERVICE)
        print("✅ Connessione a Supabase stabilita correttamente.")
    except Exception as e:
        print(f"❌ Errore durante la creazione del client: {e}")
        supabase = None

app = FastAPI()

# ... tutto il resto del codice (ScoringRequest, analyze, ecc.) rimane uguale ...
