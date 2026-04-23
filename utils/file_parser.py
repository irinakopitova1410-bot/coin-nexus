import pandas as pd
import io

# ─── Template CSV per Credit Scoring ───────────────────────────────────────────
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

# ─── Template CSV per Z-Score ───────────────────────────────────────────────────
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


def parse_credit_file(uploaded_file):
    """Parsa file CSV/Excel per Credit Scoring. Restituisce dict o errore."""
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # Supporta formato colonne (campo, valore) o riga unica
        if "campo" in df.columns and "valore" in df.columns:
            data = dict(zip(df["campo"].str.strip().str.lower(), df["valore"]))
        elif len(df) == 1:
            data = {col.strip().lower(): df[col].iloc[0] for col in df.columns}
        else:
            # Prende la prima riga numerica
            data = {col.strip().lower(): df[col].iloc[0] for col in df.columns}

        def get(key, default=0.0):
            val = data.get(key, default)
            try:
                return float(str(val).replace(",", ".").replace("€", "").replace(" ", "")) if val else default
            except:
                return default

        return {
            "success": True,
            "nome_azienda": str(data.get("nome_azienda", "")),
            "ebit": get("ebit"),
            "depreciation": get("ammortamenti"),
            "interest_expense": get("interessi_passivi"),
            "debt_repayment": get("rimborso_debito"),
            "total_debt": get("debiti_finanziari_totali"),
            "total_equity": get("patrimonio_netto", 1.0),
            "ebitda": get("ebitda"),
            "net_revenue": get("ricavi_netti", 1.0),
            "current_assets": get("attivo_corrente"),
            "current_liabilities": get("passivo_corrente", 1.0),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def parse_zscore_file(uploaded_file):
    """Parsa file CSV/Excel per Z-Score. Restituisce dict o errore."""
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        if "campo" in df.columns and "valore" in df.columns:
            data = dict(zip(df["campo"].str.strip().str.lower(), df["valore"]))
        elif len(df) == 1:
            data = {col.strip().lower(): df[col].iloc[0] for col in df.columns}
        else:
            data = {col.strip().lower(): df[col].iloc[0] for col in df.columns}

        def get(key, default=0.0):
            val = data.get(key, default)
            try:
                return float(str(val).replace(",", ".").replace("€", "").replace(" ", "")) if val else default
            except:
                return default

        return {
            "success": True,
            "nome_azienda": str(data.get("nome_azienda", "")),
            "total_assets": get("totale_attivo", 1.0),
            "retained_earnings": get("utili_non_distribuiti"),
            "ebit": get("ebit"),
            "working_capital": get("capitale_circolante_netto"),
            "total_liabilities": get("totale_passivita", 1.0),
            "equity_input": get("patrimonio_netto"),
            "revenue": get("ricavi_netti"),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_credit_template_bytes():
    return CREDIT_TEMPLATE.encode("utf-8")


def get_zscore_template_bytes():
    return ZSCORE_TEMPLATE.encode("utf-8")
