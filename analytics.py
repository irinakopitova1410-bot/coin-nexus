import numpy as np
from sklearn.ensemble import IsolationForest

class NexusAI:
    def __init__(self):
        # Inizializzazione modelli (es. caricamento pesi TensorFlow)
        pass

    def calculate_risk(self, data):
        """
        Calcola Z-Score e rileva anomalie.
        """
        # Simulazione calcolo Altman Z-Score
        # In produzione: mappare le colonne dell'Excel ai parametri A, B, C, D, E
        z_score = 2.85 
        
        # Semplice rilevamento anomalie con Scikit-Learn
        # Supponiamo di analizzare gli 'importi'
        importi = np.array([float(d.get('importo', 0)) for d in data]).reshape(-1, 1)
        if len(importi) > 1:
            model = IsolationForest(contamination=0.1)
            model.fit(importi)
            anomalie = int((model.predict(importi) == -1).sum())
        else:
            anomalie = 0

        return {
            "z_score": round(z_score, 2),
            "status": "Safe" if z_score > 2.6 else "At Risk",
            "anomalies_found": anomalie,
            "processed_records": len(data)
        }
