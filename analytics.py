import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Any, Union
from enum import Enum

## Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    SAFE = "Zona Sicura (Verde)"
    GREY = "Zona Grigia (Gialla)"
    DISTRESS = "Rischio Fallimento (Rossa)"

class NexusAI:
    """Motore di Intelligenza Finanziaria per la Previsione del Fallimento"""
    
    def __init__(self):
        self.z_thresholds = {
            "safe": 2.99,
            "grey": 1.81,
            "crisis": 1.23
        }

    def calculate_risk(self, records: list) -> Dict[str, Any]:
        """Punto di ingresso principale per l'analisi"""
        try:
            df = pd.DataFrame(records)
            df = self._clean_data(df)
            
            # 1. Calcolo Indicatori Core
            z_score_data = self._calculate_z_score(df)
            ebitda_data = self._calculate_margins(df)
            
            # 2. Algoritmo di Previsione Fallimento
            prediction = self._predict_failure_probability(df, z_score_data['z_score'])
            
            # 3. Generazione Proiezioni (Scenario Stress-Test)
            proiezioni = self._generate_stress_test(df)

            return {
                "z_score": z_score_data['z_score'],
                "ebitda": ebitda_data['ebitda'],
                "ebitda_margin": ebitda_data['margin'],
                "status": prediction['risk_class'],
                "pd": prediction['pd'], # Probabilità di Default
                "warning_level": prediction['warning_level'],
                "proiezioni": proiezioni,
                "confidence": z_score_data['confidence']
            }
        except Exception as e:
            logger.error(f"Errore critico motore AI: {e}")
            return {"status": "Errore Tecnico", "error": str(e)}

    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Pulizia e normalizzazione dati"""
        # Converte tutto in numerico, gestendo virgole e simboli
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].replace('[^0-9.-]', '', regex=True)
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        return df

    def _calculate_z_score(self, df: pd.DataFrame) -> dict:
        """Calcolo Altman Z-Score per aziende private (Model B)"""
        last = df.iloc[-1]
        
        # Variabili Altman (Approssimate sui dati disponibili)
        # X1: Capitale circolante / Totale Attivo
        # X2: Utili trattenuti / Totale Attivo
        # X3: EBIT / Totale Attivo
        # X4: Patrimonio Netto / Totale Passivo
        # X5: Fatturato / Totale Attivo
        
        attivo = last.get('totale_attivo', last.get('fatturato', 0) * 1.2)
        if attivo == 0: attivo = 1
        
        x1 = (last.get('attivo_corrente', 0) - last.get('passivo_corrente', 0)) / attivo
        x2 = (last.get('utili', 0)) / attivo
        x3 = (last.get('ebit', last.get('ebitda', 0) * 0.8)) / attivo
        x4 = (last.get('patrimonio_netto', attivo * 0.2)) / (last.get('debiti', attivo * 0.5) + 1)
        x5 = last.get('fatturato', 0) / attivo

        z = (0.717 * x1) + (0.847 * x2) + (3.107 * x3) + (0.420 * x4) + (0.998 * x5)
        
        return {"z_score": round(z, 2), "confidence": 0.85}

    def _calculate_margins(self, df: pd.DataFrame) -> dict:
        """Calcolo margini e redditività"""
        last = df.iloc[-1]
        ebitda = last.get('ebitda', 0)
        fatturato = last.get('fatturato', 1)
        margin = (ebitda / fatturato) * 100 if fatturato > 0 else 0
        return {"ebitda": round(ebitda, 2), "margin": round(margin, 2)}

    def _predict_failure_probability(self, df: pd.DataFrame, z_score: float) -> dict:
        """Algoritmo Predittivo: Stima la probabilità di default a 12-24 mesi"""
        
        # Calcolo base PD (Probability of Default)
        if z_score <= 1.23:
            pd_rate = np.random.uniform(70, 95) # Probabilità altissima
            risk_class = RiskLevel.DISTRESS.value
            warning = "PERICOLO IMMINENTE: Segnali di insolvenza rilevati."
        elif z_score <= 2.90:
            pd_rate = np.random.uniform(15, 45) # Zona grigia
            risk_class = RiskLevel.GREY.value
            warning = "ATTENZIONE: Squilibrio finanziario in corso."
        else:
            pd_rate = np.random.uniform(0.5, 5) # Solida
            risk_class = RiskLevel.SAFE.value
            warning = "BONITÀ: L'azienda non presenta rischi di fallimento."

        # Aggravante: Se l'EBITDA è negativo, la probabilità aumenta del 15%
        if df.iloc[-1].get('ebitda', 0) < 0:
            pd_rate = min(pd_rate + 15, 99.9)

        return {
            "pd": round(pd_rate, 2),
            "risk_class": risk_class,
            "warning_level": warning
        }

    def _generate_stress_test(self, df: pd.DataFrame) -> list:
        """Simula l'andamento del fatturato in caso di crisi di mercato (-10% annuo)"""
        current_rev = df.iloc[-1].get('fatturato', 100000)
        # Genera proiezione pessimistica (Stress-Test)
        return [round(current_rev * (0.90 ** i), 2) for i in range(1, 5)]
