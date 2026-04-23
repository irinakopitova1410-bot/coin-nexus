import os
from celery import Celery
from analytics import NexusAI # Importiamo la logica AI

# Configurazione Redis (URL preso dalle variabili d'ambiente di Render)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery("tasks", broker=REDIS_URL, backend=REDIS_URL)
ai_engine = NexusAI()

@celery_app.task(name="analyze_finance_task")
def analyze_finance_task(records):
    """
    Task asincrono che esegue l'analisi AI pesante.
    """
    # 1. Esegue il calcolo tramite l'engine AI
    results = ai_engine.calculate_risk(records)
    
    # 2. Qui potresti aggiungere il salvataggio automatico su Supabase
    # o l'invio di una notifica via email/SendGrid
    
    return results
