"""
NEXUS Finance Pro — Credit Readiness Engine
Motore unificato: da bilancio → Credit Score → Credito ottenibile → Azioni prioritarie → Crisi detector
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
import math


# ─── Costanti bancarie italiane ──────────────────────────────────────────────

# Multipli EBITDA usati dalle banche italiane per PMI
BANK_EBITDA_MULTIPLES = {
    "AAA": 4.5,
    "AA":  4.0,
    "A":   3.5,
    "BBB": 3.0,
    "BB":  2.5,
    "B":   2.0,
    "CCC": 1.0,
    "D":   0.0,
}

# Benchmark settore PMI italiane (% su fatturato)
BENCHMARKS = {
    "costo_personale_pct":   28.0,   # Max accettabile
    "costo_materie_pct":     45.0,
    "costi_operativi_pct":   12.0,
    "oneri_finanziari_pct":   3.5,
    "ammortamenti_pct":       4.0,
}

# Soglie per Credit Score (0-100)
SCORE_THRESHOLDS = {
    (85, 100): ("AAA", "🟢", "Eccellente"),
    (70, 84):  ("AA",  "🟢", "Ottimo"),
    (60, 69):  ("A",   "🟡", "Buono"),
    (50, 59):  ("BBB", "🟡", "Discreto"),
    (40, 49):  ("BB",  "🟠", "Sufficiente"),
    (30, 39):  ("B",   "🔴", "Debole"),
    (15, 29):  ("CCC", "🔴", "A rischio"),
    (0,  14):  ("D",   "⛔", "Non finanziabile"),
}


# ─── Data classes ─────────────────────────────────────────────────────────────

@dataclass
class BalanceInput:
    """Dati minimi richiesti dal bilancio"""
    fatturato: float = 0.0
    ebitda: float = 0.0
    ebit: float = 0.0
    utile_netto: float = 0.0
    
    # Stato patrimoniale
    attivo_corrente: float = 0.0
    passivo_corrente: float = 0.0
    debiti_finanziari: float = 0.0
    patrimonio_netto: float = 0.0
    totale_attivo: float = 0.0
    
    # Costi dettagliati (opzionali ma aumentano precisione)
    costo_personale: float = 0.0
    costo_materie_prime: float = 0.0
    costi_operativi: float = 0.0
    oneri_finanziari: float = 0.0
    ammortamenti: float = 0.0
    
    # Cash flow
    cash_operativo: float = 0.0
    cash_corrente: float = 0.0
    
    # Dati storici (ultimo anno precedente)
    fatturato_prev: float = 0.0
    ebitda_prev: float = 0.0


@dataclass
class CostAction:
    """Una singola azione correttiva con impatto economico"""
    categoria: str
    descrizione: str
    costo_attuale_pct: float
    benchmark_pct: float
    taglio_consigliato_pct: float
    impatto_ebitda_eur: float
    impatto_credito_eur: float
    priorita: int  # 1 = massima
    difficolta: str  # "Bassa" / "Media" / "Alta"
    timeline_mesi: int


@dataclass
class CrisisSignal:
    """Segnale di rischio con timeline"""
    tipo: str
    descrizione: str
    mesi_alla_crisi: Optional[int]
    probabilita_pct: float
    severita: str  # "Bassa" / "Media" / "Alta" / "Critica"


@dataclass
class CreditReadinessResult:
    """Risultato completo del motore"""
    # Score
    credit_score: float
    rating: str
    rating_emoji: str
    rating_label: str
    
    # Credito
    credito_oggi_eur: float
    credito_potenziale_eur: float
    delta_credito_eur: float
    
    # EBITDA
    ebitda_attuale: float
    ebitda_potenziale: float
    ebitda_gap: float
    
    # Decomposizione score
    score_breakdown: Dict[str, float]
    
    # Azioni prioritarie (max 5)
    azioni: List[CostAction]
    
    # Segnali di crisi
    segnali: List[CrisisSignal]
    
    # Mesi alla crisi (None = nessuna crisi prevista)
    mesi_alla_crisi: Optional[int]
    rischio_default_pct: float
    
    # Stato sintetico
    stato: str  # "finanziabile" / "borderline" / "non_finanziabile"
    messaggio_principale: str


# ─── Motore principale ────────────────────────────────────────────────────────

class CreditReadinessEngine:
    
    def __init__(self, data: BalanceInput):
        self.d = data
        self._safe_fatturato = max(data.fatturato, 1.0)  # evita div/0
    
    def compute(self) -> CreditReadinessResult:
        """Calcola tutto in un unico passaggio"""
        
        # 1. Score breakdown (6 dimensioni)
        breakdown = self._compute_score_breakdown()
        score = round(sum(breakdown.values()), 1)
        score = max(0, min(100, score))
        
        # 2. Rating
        rating, emoji, label = self._score_to_rating(score)
        
        # 3. Credito oggi
        ebitda = self.d.ebitda
        multiplo = BANK_EBITDA_MULTIPLES.get(rating, 2.0)
        credito_oggi = max(0, ebitda * multiplo - self.d.debiti_finanziari)
        
        # 4. Azioni correttive
        azioni = self._compute_actions()
        
        # 5. EBITDA potenziale (dopo azioni)
        ebitda_boost = sum(a.impatto_ebitda_eur for a in azioni)
        ebitda_potenziale = ebitda + ebitda_boost
        
        # 6. Credito potenziale (score dopo miglioramento)
        score_potenziale = min(100, score + len(azioni) * 4)
        rating_pot, _, _ = self._score_to_rating(score_potenziale)
        multiplo_pot = BANK_EBITDA_MULTIPLES.get(rating_pot, 2.0)
        credito_potenziale = max(0, ebitda_potenziale * multiplo_pot - self.d.debiti_finanziari)
        
        # 7. Segnali di crisi
        segnali = self._detect_crisis_signals()
        mesi_crisi = self._months_to_crisis()
        rischio_default = self._default_probability(score)
        
        # 8. Stato sintetico
        if credito_oggi > 0 and score >= 50:
            stato = "finanziabile"
            msg = f"L'azienda è finanziabile per €{credito_oggi:,.0f}. Ottimizzando i costi puoi arrivare a €{credito_potenziale:,.0f}."
        elif credito_oggi > 0:
            stato = "borderline"
            msg = f"Accesso al credito limitato (€{credito_oggi:,.0f}). Servono interventi per sbloccare il potenziale di €{credito_potenziale:,.0f}."
        else:
            stato = "non_finanziabile"
            msg = f"Al momento non finanziabile. Con le azioni consigliate puoi raggiungere €{credito_potenziale:,.0f} in {len(azioni)*2}-{len(azioni)*3} mesi."
        
        return CreditReadinessResult(
            credit_score=score,
            rating=rating,
            rating_emoji=emoji,
            rating_label=label,
            credito_oggi_eur=credito_oggi,
            credito_potenziale_eur=credito_potenziale,
            delta_credito_eur=max(0, credito_potenziale - credito_oggi),
            ebitda_attuale=ebitda,
            ebitda_potenziale=ebitda_potenziale,
            ebitda_gap=ebitda_boost,
            score_breakdown=breakdown,
            azioni=sorted(azioni, key=lambda x: x.priorita),
            segnali=segnali,
            mesi_alla_crisi=mesi_crisi,
            rischio_default_pct=rischio_default,
            stato=stato,
            messaggio_principale=msg,
        )
    
    # ── Score breakdown ───────────────────────────────────────────────────────
    
    def _compute_score_breakdown(self) -> Dict[str, float]:
        d = self.d
        f = self._safe_fatturato
        
        scores = {}
        
        # 1. EBITDA Margin (max 25 punti) — peso maggiore perché è il driver del credito
        ebitda_pct = (d.ebitda / f) * 100
        if ebitda_pct >= 20:   s1 = 25
        elif ebitda_pct >= 15: s1 = 22
        elif ebitda_pct >= 10: s1 = 18
        elif ebitda_pct >= 7:  s1 = 13
        elif ebitda_pct >= 4:  s1 = 8
        elif ebitda_pct >= 0:  s1 = 3
        else:                   s1 = 0
        scores["EBITDA Margin"] = s1
        
        # 2. Debt/EBITDA (max 20 punti)
        if d.ebitda > 0:
            debt_ebitda = d.debiti_finanziari / d.ebitda
            if debt_ebitda <= 1:   s2 = 20
            elif debt_ebitda <= 2: s2 = 16
            elif debt_ebitda <= 3: s2 = 12
            elif debt_ebitda <= 4: s2 = 8
            elif debt_ebitda <= 6: s2 = 4
            else:                   s2 = 0
        else:
            s2 = 0
        scores["Debt / EBITDA"] = s2
        
        # 3. Liquidità corrente (max 20 punti)
        if d.passivo_corrente > 0:
            liquidity = d.attivo_corrente / d.passivo_corrente
            if liquidity >= 2.0:   s3 = 20
            elif liquidity >= 1.5: s3 = 17
            elif liquidity >= 1.2: s3 = 13
            elif liquidity >= 1.0: s3 = 8
            elif liquidity >= 0.8: s3 = 4
            else:                   s3 = 0
        else:
            s3 = 15 if d.attivo_corrente > 0 else 0
        scores["Liquidità Corrente"] = s3
        
        # 4. Cash Flow operativo (max 15 punti)
        if d.cash_operativo > 0:
            cf_pct = (d.cash_operativo / f) * 100
            if cf_pct >= 10:  s4 = 15
            elif cf_pct >= 6: s4 = 12
            elif cf_pct >= 3: s4 = 8
            else:             s4 = 4
        elif d.cash_operativo == 0:
            s4 = 2
        else:
            s4 = 0
        scores["Cash Flow Operativo"] = s4
        
        # 5. Patrimonio Netto / Attivo (solvibilità, max 12 punti)
        if d.totale_attivo > 0:
            equity_ratio = d.patrimonio_netto / d.totale_attivo
            if equity_ratio >= 0.5:   s5 = 12
            elif equity_ratio >= 0.35: s5 = 10
            elif equity_ratio >= 0.25: s5 = 7
            elif equity_ratio >= 0.15: s5 = 4
            elif equity_ratio >= 0.05: s5 = 2
            else:                       s5 = 0
        else:
            s5 = 0
        scores["Solidità Patrimoniale"] = s5
        
        # 6. Trend ricavi (max 8 punti)
        if d.fatturato_prev > 0:
            growth = (d.fatturato - d.fatturato_prev) / d.fatturato_prev * 100
            if growth >= 10:   s6 = 8
            elif growth >= 5:  s6 = 6
            elif growth >= 0:  s6 = 4
            elif growth >= -5: s6 = 2
            else:               s6 = 0
        else:
            s6 = 4  # neutro se dato non disponibile
        scores["Trend Ricavi"] = s6
        
        return scores
    
    # ── Rating ────────────────────────────────────────────────────────────────
    
    def _score_to_rating(self, score: float) -> Tuple[str, str, str]:
        for (lo, hi), (rating, emoji, label) in SCORE_THRESHOLDS.items():
            if lo <= score <= hi:
                return rating, emoji, label
        return "D", "⛔", "Non finanziabile"
    
    # ── Azioni correttive ─────────────────────────────────────────────────────
    
    def _compute_actions(self) -> List[CostAction]:
        d = self.d
        f = self._safe_fatturato
        actions = []
        multiplo = 2.5  # conservativo per calcolare impatto credito
        
        # A. Costo del personale
        if d.costo_personale > 0:
            pct = (d.costo_personale / f) * 100
            bench = BENCHMARKS["costo_personale_pct"]
            if pct > bench:
                gap_pct = pct - bench
                taglio_pct = min(gap_pct * 0.5, 8.0)  # max 8% taglio realistico
                impatto_ebitda = d.fatturato * (taglio_pct / 100)
                actions.append(CostAction(
                    categoria="👥 Costo del Personale",
                    descrizione=f"Il costo personale è al {pct:.1f}% del fatturato vs benchmark {bench:.0f}%. "
                                f"Ottimizzare con smart working, turnover naturale e revisione straordinari.",
                    costo_attuale_pct=pct,
                    benchmark_pct=bench,
                    taglio_consigliato_pct=taglio_pct,
                    impatto_ebitda_eur=impatto_ebitda,
                    impatto_credito_eur=impatto_ebitda * multiplo,
                    priorita=1,
                    difficolta="Alta",
                    timeline_mesi=6,
                ))
        
        # B. Costo materie prime / acquisti
        if d.costo_materie_prime > 0:
            pct = (d.costo_materie_prime / f) * 100
            bench = BENCHMARKS["costo_materie_pct"]
            if pct > bench:
                gap_pct = pct - bench
                taglio_pct = min(gap_pct * 0.4, 6.0)
                impatto_ebitda = d.fatturato * (taglio_pct / 100)
                actions.append(CostAction(
                    categoria="📦 Acquisti / Materie Prime",
                    descrizione=f"Il costo acquisti è al {pct:.1f}% vs benchmark {bench:.0f}%. "
                                f"Rinegoziare contratti fornitori, consolidare ordini, valutare fornitori alternativi.",
                    costo_attuale_pct=pct,
                    benchmark_pct=bench,
                    taglio_consigliato_pct=taglio_pct,
                    impatto_ebitda_eur=impatto_ebitda,
                    impatto_credito_eur=impatto_ebitda * multiplo,
                    priorita=2,
                    difficolta="Media",
                    timeline_mesi=3,
                ))
        
        # C. Costi operativi generali
        if d.costi_operativi > 0:
            pct = (d.costi_operativi / f) * 100
            bench = BENCHMARKS["costi_operativi_pct"]
            if pct > bench:
                gap_pct = pct - bench
                taglio_pct = min(gap_pct * 0.5, 5.0)
                impatto_ebitda = d.fatturato * (taglio_pct / 100)
                actions.append(CostAction(
                    categoria="⚙️ Costi Operativi",
                    descrizione=f"I costi operativi sono al {pct:.1f}% vs benchmark {bench:.0f}%. "
                                f"Revisione affitti, utilities, servizi esterni, digitalizzazione processi.",
                    costo_attuale_pct=pct,
                    benchmark_pct=bench,
                    taglio_consigliato_pct=taglio_pct,
                    impatto_ebitda_eur=impatto_ebitda,
                    impatto_credito_eur=impatto_ebitda * multiplo,
                    priorita=3,
                    difficolta="Bassa",
                    timeline_mesi=2,
                ))
        
        # D. Oneri finanziari
        if d.oneri_finanziari > 0:
            pct = (d.oneri_finanziari / f) * 100
            bench = BENCHMARKS["oneri_finanziari_pct"]
            if pct > bench:
                gap_pct = pct - bench
                taglio_pct = min(gap_pct * 0.3, 2.0)
                impatto_ebitda = d.fatturato * (taglio_pct / 100)
                actions.append(CostAction(
                    categoria="💳 Oneri Finanziari",
                    descrizione=f"Gli oneri finanziari sono al {pct:.1f}% vs benchmark {bench:.1f}%. "
                                f"Rinegoziare tassi, consolidare debiti breve termine, usare factoring.",
                    costo_attuale_pct=pct,
                    benchmark_pct=bench,
                    taglio_consigliato_pct=taglio_pct,
                    impatto_ebitda_eur=impatto_ebitda,
                    impatto_credito_eur=impatto_ebitda * multiplo,
                    priorita=4,
                    difficolta="Media",
                    timeline_mesi=4,
                ))
        
        # E. Miglioramento margine (se EBITDA margin basso ma nessun costo specifico)
        if not actions and d.ebitda > 0:
            ebitda_pct = (d.ebitda / f) * 100
            if ebitda_pct < 10:
                target_pct = 12.0
                impatto = d.fatturato * ((target_pct - ebitda_pct) / 100)
                actions.append(CostAction(
                    categoria="📈 Margine EBITDA",
                    descrizione=f"EBITDA margin al {ebitda_pct:.1f}%, sotto la soglia bancaria del 10%. "
                                f"Rivedere il pricing, aumentare la marginalità per prodotto/servizio.",
                    costo_attuale_pct=ebitda_pct,
                    benchmark_pct=10.0,
                    taglio_consigliato_pct=target_pct - ebitda_pct,
                    impatto_ebitda_eur=impatto,
                    impatto_credito_eur=impatto * multiplo,
                    priorita=1,
                    difficolta="Media",
                    timeline_mesi=4,
                ))
        
        return actions[:5]  # max 5 azioni
    
    # ── Crisis detector ───────────────────────────────────────────────────────
    
    def _detect_crisis_signals(self) -> List[CrisisSignal]:
        d = self.d
        signals = []
        
        # 1. Liquidità critica
        if d.passivo_corrente > 0:
            ratio = d.attivo_corrente / d.passivo_corrente
            if ratio < 0.8:
                signals.append(CrisisSignal(
                    tipo="🚨 Liquidità Critica",
                    descrizione=f"Rapporto corrente {ratio:.2f} — passivi a breve superiori all'attivo corrente. "
                                f"Rischio default su debiti correnti.",
                    mesi_alla_crisi=self._estimate_months_liquidity(),
                    probabilita_pct=min(90, (1 - ratio) * 120),
                    severita="Critica",
                ))
            elif ratio < 1.2:
                signals.append(CrisisSignal(
                    tipo="⚠️ Liquidità Sotto Soglia",
                    descrizione=f"Rapporto corrente {ratio:.2f} — margine di sicurezza insufficiente.",
                    mesi_alla_crisi=None,
                    probabilita_pct=35,
                    severita="Media",
                ))
        
        # 2. EBITDA negativo
        if d.ebitda < 0:
            signals.append(CrisisSignal(
                tipo="🔴 EBITDA Negativo",
                descrizione=f"L'azienda non genera cassa dalla gestione operativa. "
                            f"Ogni mese brucia risorse patrimoniali.",
                mesi_alla_crisi=self._months_ebitda_negative(),
                probabilita_pct=75,
                severita="Alta",
            ))
        
        # 3. Cash flow operativo negativo
        if d.cash_operativo < 0:
            signals.append(CrisisSignal(
                tipo="📉 Cash Flow Negativo",
                descrizione=f"Il cash flow operativo è negativo (€{d.cash_operativo:,.0f}). "
                            f"L'azienda consuma liquidità operativamente.",
                mesi_alla_crisi=self._estimate_months_cashburn(),
                probabilita_pct=60,
                severita="Alta",
            ))
        
        # 4. Patrimonio netto basso
        if d.totale_attivo > 0 and d.patrimonio_netto / d.totale_attivo < 0.1:
            signals.append(CrisisSignal(
                tipo="⚠️ Patrimonio Netto Insufficiente",
                descrizione=f"Il patrimonio netto copre solo il {(d.patrimonio_netto/d.totale_attivo*100):.1f}% dell'attivo. "
                            f"Le banche richiedono almeno il 15-20%.",
                mesi_alla_crisi=None,
                probabilita_pct=45,
                severita="Media",
            ))
        
        # 5. Debito eccessivo
        if d.ebitda > 0:
            debt_mult = d.debiti_finanziari / d.ebitda
            if debt_mult > 5:
                signals.append(CrisisSignal(
                    tipo="🔴 Debito Eccessivo",
                    descrizione=f"Debt/EBITDA pari a {debt_mult:.1f}x — soglia bancaria max 4x. "
                                f"Difficile ottenere nuovo credito senza ridurre l'indebitamento.",
                    mesi_alla_crisi=None,
                    probabilita_pct=55,
                    severita="Alta",
                ))
        
        return signals
    
    def _months_to_crisis(self) -> Optional[int]:
        """Mesi alla crisi più imminente"""
        all_months = [
            s.mesi_alla_crisi for s in self._detect_crisis_signals()
            if s.mesi_alla_crisi is not None
        ]
        return min(all_months) if all_months else None
    
    def _estimate_months_liquidity(self) -> int:
        d = self.d
        if d.cash_operativo < 0 and d.cash_corrente > 0:
            return max(1, int(d.cash_corrente / abs(d.cash_operativo) * 12))
        return 3
    
    def _months_ebitda_negative(self) -> int:
        d = self.d
        if d.patrimonio_netto > 0 and d.ebitda < 0:
            return max(1, int(d.patrimonio_netto / abs(d.ebitda) * 12))
        return 6
    
    def _estimate_months_cashburn(self) -> int:
        d = self.d
        if d.cash_corrente > 0 and d.cash_operativo < 0:
            monthly_burn = abs(d.cash_operativo) / 12
            return max(1, int(d.cash_corrente / monthly_burn))
        return 4
    
    def _default_probability(self, score: float) -> float:
        """Probabilità di default basata su score (curva sigmoidale inversa)"""
        # Score 100 → 0% default, Score 0 → 80% default
        prob = 80 * math.exp(-score / 25)
        return round(min(95, max(0, prob)), 1)


# ─── Funzione pubblica ────────────────────────────────────────────────────────

def analyze_credit_readiness(
    fatturato: float,
    ebitda: float,
    ebit: float = 0,
    utile_netto: float = 0,
    attivo_corrente: float = 0,
    passivo_corrente: float = 0,
    debiti_finanziari: float = 0,
    patrimonio_netto: float = 0,
    totale_attivo: float = 0,
    costo_personale: float = 0,
    costo_materie_prime: float = 0,
    costi_operativi: float = 0,
    oneri_finanziari: float = 0,
    ammortamenti: float = 0,
    cash_operativo: float = 0,
    cash_corrente: float = 0,
    fatturato_prev: float = 0,
    ebitda_prev: float = 0,
) -> CreditReadinessResult:
    """Entry point principale del motore"""
    data = BalanceInput(
        fatturato=fatturato,
        ebitda=ebitda,
        ebit=ebit,
        utile_netto=utile_netto,
        attivo_corrente=attivo_corrente,
        passivo_corrente=passivo_corrente,
        debiti_finanziari=debiti_finanziari,
        patrimonio_netto=patrimonio_netto,
        totale_attivo=totale_attivo,
        costo_personale=costo_personale,
        costo_materie_prime=costo_materie_prime,
        costi_operativi=costi_operativi,
        oneri_finanziari=oneri_finanziari,
        ammortamenti=ammortamenti,
        cash_operativo=cash_operativo,
        cash_corrente=cash_corrente,
        fatturato_prev=fatturato_prev,
        ebitda_prev=ebitda_prev,
    )
    engine = CreditReadinessEngine(data)
    return engine.compute()
