import pandas as pd
# Importa qui sklearn o tensorflow-cpu se li usi

class NexusAI:
    def calculate_risk(self, records):
        # Converte i dati in DataFrame
        df = pd.DataFrame(records)
        
        # Esegui i tuoi calcoli (Z-Score, modelli ML ecc.)
        # Esempio semplificato:
        z_score = df['alcun_valore'].mean() # La tua formula reale qui
        status = "Safe" if z_score > 1.8 else "At Risk"
        
        return {
            "z_score": round(z_score, 2),
            "status": status
        }
