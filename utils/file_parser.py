import pandas as pd
import io

# ─── Template CSV Unico Completo ────────────────────────────────────────────────
BILANCIO_COMPLETO_TEMPLATE = """campo,valore,descrizione
nome_azienda,,Ragione sociale
settore,,Settore merceologico
anno_bilancio,,Anno esercizio
rischio,,Livello rischio (low/medium/high)
totale_attivo,,Totale Attivo (€)
patrimonio_netto,,Patrimonio Netto (€) — può essere negativo
totale_debiti,,Totale Debiti (€)
debiti_banche,,Debiti verso banche (€)
debiti_fornitori,,Debiti verso fornitori (€)
capitale_circolante_netto,,CCN = Attivo Circolante - Passivo Corrente (€)
disponibilita_liquide,,Liquidità disponibile (€)
totale_attivo_circolante,,Totale Attivo Circolante (€)
ricavi_netti,,Ricavi netti (€)
ebit,,EBIT - Reddito Operativo (€)
ebitda,,EBITDA (€)
ammortamenti,,Ammortamenti e svalutazioni (€)
utile_netto,,Utile (perdita) netto (€)
utili_non_distribuiti,,Perdite/utili portati a nuovo (€)
risultato_ante_imposte,,Risultato prima delle imposte (€)
costi_personale,,Costi per il personale (€)
costi_materie_prime,,Costi materie prime (€)
costi_servizi,,Costi per servizi (€)
costi_affitti,,Costi per affitti/leasing (€)
oneri_finanziari,,Oneri finanziari netti (€)
interessi_passivi,,Interessi passivi (€)
rimborso_debito,,Rimborso debito annuo (€)
controlli_interni,,Score qualità controlli interni (1-10)
tasso_errori,,Tasso errori stimato (%)
"""

# ─── Template CSV legacy (Credit Scoring) ───────────────────────────────────────
CREDIT_TEMPLATE = """campo,valore,descrizione
nome_azienda,,Nome dell'azienda
ebit,,EBIT - Reddito Operativo (€)
ammortamenti,,Ammortamenti e svalutazioni (€)
interessi_passivi,,Interessi passivi (€)
rimborso_debito,,Rimborso debito annuo (€)
debiti_finanziari_totali,,Debiti finanziari totali (€)
patrimonio_netto,,Patrimonio Netto (€)
ebitda,,EBITDA (€)
ricavi_netti,,Ricavi Netti (€)
attivo_corrente,,Attivo Corrente (€)
passivo_corrente,,Passivo Corrente (€)
"""

# ─── Template CSV legacy (Z-Score) ──────────────────────────────────────────────
ZSCORE_TEMPLATE = """campo,valore,descrizione
nome_azienda,,Nome dell'azienda
totale_attivo,,Totale Attivo (€)
utili_non_distribuiti,,Utili non distribuiti / Riserve (€)
ebit,,EBIT - Reddito Operativo (€)
capitale_circolante_netto,,Capitale Circolante Netto = Attivo Corr - Passivo Corr (€)
totale_passivita,,Totale Passività (€)
patrimonio_netto,,Patrimonio Netto Contabile (€)
ricavi_netti,,Ricavi Netti (€)
"""


def _parse_csv_universal(uploaded_file):
    """
    Parser universale: accetta CSV con 2 o 3 colonne, ignora righe che iniziano con #.
    Restituisce un dict {campo: valore}.
    """
    try:
        raw = uploaded_file.read()
        uploaded_file.seek(0)  # reset per eventuali riletture
        text = raw.decode("utf-8", errors="replace")

        # Filtra righe commento e righe vuote
        lines = [l for l in text.splitlines() if l.strip() and not l.strip().startswith("#")]
        clean_csv = "\n".join(lines)

        df = pd.read_csv(io.StringIO(clean_csv))

        if "campo" in df.columns and "valore" in df.columns:
            data = dict(zip(
                df["campo"].astype(str).str.strip().str.lower(),
                df["valore"]
            ))
        elif len(df.columns) >= 2:
            cols = list(df.columns)
            data = dict(zip(
                df[cols[0]].astype(str).str.strip().str.lower(),
                df[cols[1]]
            ))
        else:
            data = {col.strip().lower(): df[col].iloc[0] for col in df.columns}

        # Rimuovi chiavi vuote o NaN
        data = {k: v for k, v in data.items() if k and k != "nan"}
        return data
    except Exception as e:
        return {"_parse_error": str(e)}


def _num(data, *keys, default=0.0):
    """Prova più chiavi alias, restituisce il primo valore numerico trovato."""
    for key in keys:
        val = data.get(key)
        if val is not None and str(val).strip() not in ("", "nan", "None"):
            try:
                return float(str(val).replace(",", ".").replace("€", "").replace(" ", "").replace(".", "", str(val).count(".") - 1) if str(val).count(".") > 1 else str(val).replace(",", ".").replace("€", "").replace(" ", ""))
            except:
                continue
    return default


def _str(data, *keys, default=""):
    for key in keys:
        val = data.get(key)
        if val and str(val).strip() not in ("", "nan", "None"):
            return str(val).strip()
    return default


def parse_credit_file(uploaded_file):
    """Parsa file CSV/Excel per Credit Scoring. Supporta il CSV unico completo."""
    try:
        if uploaded_file.name.lower().endswith(".csv"):
            data = _parse_csv_universal(uploaded_file)
            if "_parse_error" in data:
                return {"success": False, "error": data["_parse_error"]}
        else:
            df = pd.read_excel(uploaded_file)
            if "campo" in df.columns and "valore" in df.columns:
                data = dict(zip(df["campo"].astype(str).str.strip().str.lower(), df["valore"]))
            else:
                data = {col.strip().lower(): df[col].iloc[0] for col in df.columns}

        nome = _str(data, "nome_azienda", "azienda", default="Azienda")

        ebit = _num(data, "ebit", default=0.0)
        ammortamenti = _num(data, "ammortamenti", "ammortamenti_immateriali", default=0.0)
        ebitda_raw = _num(data, "ebitda", default=None)
        ebitda = ebitda_raw if ebitda_raw is not None else ebit + ammortamenti

        return {
            "success": True,
            "nome_azienda": nome,
            "ebit": ebit,
            "depreciation": ammortamenti,
            "interest_expense": _num(data, "interessi_passivi", "oneri_finanziari", default=0.0),
            "debt_repayment": _num(data, "rimborso_debito", default=0.0),
            "total_debt": _num(data, "debiti_finanziari_totali", "totale_debiti", "debiti_banche", default=0.0),
            "total_equity": _num(data, "patrimonio_netto", default=1.0),
            "ebitda": ebitda,
            "net_revenue": _num(data, "ricavi_netti", "ricavi_vendite", "fatturato", default=1.0),
            "current_assets": _num(data, "attivo_corrente", "totale_attivo_circolante", default=0.0),
            "current_liabilities": _num(data, "passivo_corrente", "totale_debiti", default=1.0),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def parse_zscore_file(uploaded_file):
    """Parsa file CSV/Excel per Z-Score. Supporta il CSV unico completo."""
    try:
        if uploaded_file.name.lower().endswith(".csv"):
            data = _parse_csv_universal(uploaded_file)
            if "_parse_error" in data:
                return {"success": False, "error": data["_parse_error"]}
        else:
            df = pd.read_excel(uploaded_file)
            if "campo" in df.columns and "valore" in df.columns:
                data = dict(zip(df["campo"].astype(str).str.strip().str.lower(), df["valore"]))
            else:
                data = {col.strip().lower(): df[col].iloc[0] for col in df.columns}

        nome = _str(data, "nome_azienda", "azienda", default="Azienda")
        ebit = _num(data, "ebit", default=0.0)
        ammort = _num(data, "ammortamenti", default=0.0)

        # CCN: prova campo diretto, altrimenti calcola
        ccn = _num(data, "capitale_circolante_netto", default=None)
        if ccn is None:
            attivo_corr = _num(data, "totale_attivo_circolante", "attivo_corrente", default=0.0)
            passivo_corr = _num(data, "passivo_corrente", default=0.0)
            ccn = attivo_corr - passivo_corr

        # Totale passività: prova alias
        tot_passivita = _num(data, "totale_passivita", "totale_debiti", default=1.0)

        return {
            "success": True,
            "nome_azienda": nome,
            "total_assets": _num(data, "totale_attivo", default=1.0),
            "retained_earnings": _num(data, "utili_non_distribuiti", "perdite_precedenti", default=0.0),
            "ebit": ebit,
            "working_capital": ccn,
            "total_liabilities": tot_passivita,
            "equity_input": _num(data, "patrimonio_netto", default=0.0),
            "revenue": _num(data, "ricavi_netti", "ricavi_vendite", "fatturato", default=0.0),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def parse_ratios_file(uploaded_file):
    """Parsa file CSV/Excel per Financial Ratios. Supporta il CSV unico completo."""
    try:
        if uploaded_file.name.lower().endswith(".csv"):
            data = _parse_csv_universal(uploaded_file)
            if "_parse_error" in data:
                return {"success": False, "error": data["_parse_error"]}
        else:
            df = pd.read_excel(uploaded_file)
            if "campo" in df.columns and "valore" in df.columns:
                data = dict(zip(df["campo"].astype(str).str.strip().str.lower(), df["valore"]))
            else:
                data = {col.strip().lower(): df[col].iloc[0] for col in df.columns}

        nome = _str(data, "nome_azienda", "azienda", default="Azienda")
        ebit = _num(data, "ebit", default=0.0)
        ammort = _num(data, "ammortamenti", default=0.0)
        ebitda = _num(data, "ebitda", default=ebit + ammort)

        return {
            "success": True,
            "nome_azienda": nome,
            "total_assets": _num(data, "totale_attivo", default=1.0),
            "total_equity": _num(data, "patrimonio_netto", default=0.0),
            "total_liabilities": _num(data, "totale_debiti", "totale_passivita", default=0.0),
            "current_assets": _num(data, "totale_attivo_circolante", "attivo_corrente", default=0.0),
            "current_liabilities": _num(data, "passivo_corrente", default=0.0),
            "inventory": _num(data, "rimanenze", default=0.0),
            "cash": _num(data, "disponibilita_liquide", default=0.0),
            "net_revenue": _num(data, "ricavi_netti", "ricavi_vendite", "fatturato", default=1.0),
            "ebit": ebit,
            "ebitda": ebitda,
            "net_income": _num(data, "utile_netto", "perdita_esercizio", default=0.0),
            "interest_expense": _num(data, "interessi_passivi", "oneri_finanziari", default=0.0),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def parse_audit_file(uploaded_file):
    """Parsa file CSV/Excel per Audit Report ISA 320. Supporta il CSV unico completo."""
    try:
        if uploaded_file.name.lower().endswith(".csv"):
            data = _parse_csv_universal(uploaded_file)
            if "_parse_error" in data:
                return {"success": False, "error": data["_parse_error"]}
        else:
            df = pd.read_excel(uploaded_file)
            if "campo" in df.columns and "valore" in df.columns:
                data = dict(zip(df["campo"].astype(str).str.strip().str.lower(), df["valore"]))
            else:
                data = {col.strip().lower(): df[col].iloc[0] for col in df.columns}

        nome = _str(data, "nome_azienda", "azienda", default="Azienda")

        # Materialità base: utile lordo > totale attivo > ricavi (in ordine di priorità ISA 320)
        utile_lordo = _num(data, "utile_lordo", "ebit", "utile_netto", default=None)
        totale_attivo = _num(data, "totale_attivo", default=0.0)
        ricavi = _num(data, "ricavi_netti", "ricavi_vendite", "fatturato", default=0.0)

        # Reddito ante imposte per calcolo materialità alternativo
        reddito_ante = _num(data, "reddito_ante_imposte", "risultato_ante_imposte", default=None)

        # Rischio
        rischio_raw = _str(data, "rischio", default="medium").lower()
        rischio_map = {
            "alto": "high", "alta": "high", "elevato": "high",
            "medio": "medium", "media": "medium",
            "basso": "low", "bassa": "low"
        }
        rischio = rischio_map.get(rischio_raw, rischio_raw)
        if rischio not in ("low", "medium", "high"):
            rischio = "high" if totale_attivo > 0 and _num(data, "patrimonio_netto", default=0) < 0 else "medium"

        controlli = _num(data, "controlli_interni", default=5.0)
        tasso_errori = _num(data, "tasso_errori", default=2.0)

        return {
            "success": True,
            "nome_azienda": nome,
            "gross_profit": utile_lordo if utile_lordo is not None else ricavi * 0.05,
            "total_assets": totale_attivo,
            "net_revenue": ricavi,
            "pre_tax_income": reddito_ante if reddito_ante is not None else (utile_lordo or 0.0),
            "internal_controls_score": max(1.0, min(10.0, controlli)),
            "error_rate": max(0.0, tasso_errori),
            "risk_level": rischio,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def parse_credit_readiness_file(uploaded_file):
    """Parsa file CSV/Excel per Credit Readiness. Supporta il CSV unico completo."""
    try:
        if uploaded_file.name.lower().endswith(".csv"):
            data = _parse_csv_universal(uploaded_file)
            if "_parse_error" in data:
                return {"success": False, "error": data["_parse_error"]}
        else:
            df = pd.read_excel(uploaded_file)
            if "campo" in df.columns and "valore" in df.columns:
                data = dict(zip(df["campo"].astype(str).str.strip().str.lower(), df["valore"]))
            else:
                data = {col.strip().lower(): df[col].iloc[0] for col in df.columns}

        nome = _str(data, "nome_azienda", "azienda", default="Azienda")
        ebit = _num(data, "ebit", default=0.0)
        ammort = _num(data, "ammortamenti", default=0.0)
        ebitda = _num(data, "ebitda", default=ebit + ammort)

        return {
            "success": True,
            "nome_azienda": nome,
            "fatturato": _num(data, "fatturato", "ricavi_netti", "ricavi_vendite", default=0.0),
            "ebitda": ebitda,
            "patrimonio_netto": _num(data, "patrimonio_netto", default=0.0),
            "totale_debiti": _num(data, "totale_debiti", "debiti_banche", default=0.0),
            "debiti_banche": _num(data, "debiti_banche", default=0.0),
            "costi_personale": _num(data, "costi_personale", default=0.0),
            "costi_affitti": _num(data, "costi_affitti", default=0.0),
            "costi_materie_prime": _num(data, "costi_materie_prime", default=0.0),
            "costi_servizi": _num(data, "costi_servizi", default=0.0),
            "liquidita": _num(data, "disponibilita_liquide", default=0.0),
            "totale_attivo": _num(data, "totale_attivo", default=0.0),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_bilancio_template_bytes():
    return BILANCIO_COMPLETO_TEMPLATE.encode("utf-8")


def get_credit_template_bytes():
    return CREDIT_TEMPLATE.encode("utf-8")


def get_zscore_template_bytes():
    return ZSCORE_TEMPLATE.encode("utf-8")
