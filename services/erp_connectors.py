"""
NEXUS Finance Pro — ERP Connectors
Supporta: SAP, Zucchetti, TeamSystem, Sage, Microsoft Dynamics, Generic CSV/Excel
Auto-detect del formato, encoding italiano (Latin-1/CP1252), separatori multipli.
"""
import pandas as pd
import numpy as np
import io
import chardet
from typing import Dict, Optional, Tuple, List
from dataclasses import dataclass, field

# ─── Mapping colonne ERP → standard NEXUS ────────────────────────────────────

ERP_COLUMN_MAPS = {
    "SAP": {
        "WAERS": "currency", "BUDAT": "date", "BLDAT": "doc_date",
        "GJAHR": "year", "MONAT": "month",
        # Bilancio
        "AKTIV": "total_assets", "PASSIV": "total_liabilities",
        "UMSATZ": "revenue", "EBITDA": "ebitda", "EBIT": "ebit",
        "JU_GEWINN": "net_income", "EK_KAPITAL": "equity",
        "UMLAUFV": "current_assets", "KFV": "current_liabilities",
        "VORRAEETE": "inventory", "FORD_LUL": "accounts_receivable",
        "VERB_LUL": "accounts_payable", "ANLAGEN": "fixed_assets",
        "ZINSAUFW": "interest_expense", "STEUERAUFW": "tax_expense",
        "ABSCHREIB": "depreciation", "FK_GESAMT": "total_debt",
        "GEWINN_VJ": "retained_earnings", "MKTCAP": "market_cap",
        "UMLAUF_KAP": "working_capital",
    },
    "ZUCCHETTI": {
        "TotaleAttivo": "total_assets", "TotalePassivo": "total_liabilities",
        "Ricavi": "revenue", "EBITDA": "ebitda", "EBIT": "ebit",
        "UtileNetto": "net_income", "PatrimonioNetto": "equity",
        "AttivoCorriente": "current_assets", "PassivoCorriente": "current_liabilities",
        "Rimanenze": "inventory", "CreditiClienti": "accounts_receivable",
        "DebitiForni": "accounts_payable", "ImmobilizzazioniNette": "fixed_assets",
        "OneriFinanziari": "interest_expense", "Imposte": "tax_expense",
        "Ammortamenti": "depreciation", "DebitiFinanziari": "total_debt",
        "RiserveUtili": "retained_earnings", "CapitalizzazioneBorsa": "market_cap",
        "CapitaleCircolante": "working_capital", "Anno": "year",
    },
    "TEAMSYSTEM": {
        "Totale_Attivo": "total_assets", "Totale_Passivo": "total_liabilities",
        "Fatturato": "revenue", "EBITDA": "ebitda", "EBIT": "ebit",
        "Risultato_Netto": "net_income", "Patrimonio_Netto": "equity",
        "Attivo_Circolante": "current_assets", "Passivo_Corrente": "current_liabilities",
        "Magazzino": "inventory", "Crediti_Commerciali": "accounts_receivable",
        "Debiti_Commerciali": "accounts_payable", "Immobilizzazioni": "fixed_assets",
        "Oneri_Fin": "interest_expense", "Imposte_IRES_IRAP": "tax_expense",
        "Amm_Acc": "depreciation", "Debiti_Finanziari": "total_debt",
        "Utili_Portati": "retained_earnings", "Anno_Esercizio": "year",
    },
    "SAGE": {
        "TotalAssets": "total_assets", "TotalLiabilities": "total_liabilities",
        "Revenue": "revenue", "EBITDA": "ebitda", "EBIT": "ebit",
        "NetIncome": "net_income", "Equity": "equity",
        "CurrentAssets": "current_assets", "CurrentLiabilities": "current_liabilities",
        "Inventory": "inventory", "TradeReceivables": "accounts_receivable",
        "TradePayables": "accounts_payable", "FixedAssets": "fixed_assets",
        "FinancialCharges": "interest_expense", "TaxCharge": "tax_expense",
        "Depreciation": "depreciation", "FinancialDebt": "total_debt",
        "RetainedEarnings": "retained_earnings", "FiscalYear": "year",
    },
    "DYNAMICS": {
        "TotalAssets": "total_assets", "TotalLiabilities": "total_liabilities",
        "NetRevenue": "revenue", "EBITDA": "ebitda", "OperatingIncome": "ebit",
        "NetEarnings": "net_income", "StockholdersEquity": "equity",
        "CurrentAssets": "current_assets", "CurrentLiabilities": "current_liabilities",
        "Inventories": "inventory", "AccountsReceivable": "accounts_receivable",
        "AccountsPayable": "accounts_payable", "PropertyPlantEquipment": "fixed_assets",
        "InterestExpense": "interest_expense", "IncomeTaxExpense": "tax_expense",
        "DepreciationAmortization": "depreciation", "LongTermDebt": "total_debt",
        "RetainedEarnings": "retained_earnings", "FiscalYear": "year",
    },
}

# Campi standard NEXUS richiesti per i calcoli
REQUIRED_FIELDS = {
    "total_assets": "Totale Attivo",
    "total_liabilities": "Totale Passivo",
    "revenue": "Ricavi / Fatturato",
    "ebit": "EBIT",
    "equity": "Patrimonio Netto",
    "current_assets": "Attivo Corrente",
    "current_liabilities": "Passivo Corrente",
    "net_income": "Utile Netto",
}

OPTIONAL_FIELDS = {
    "ebitda": "EBITDA",
    "inventory": "Magazzino / Rimanenze",
    "accounts_receivable": "Crediti Commerciali",
    "accounts_payable": "Debiti Commerciali",
    "fixed_assets": "Immobilizzazioni Nette",
    "interest_expense": "Oneri Finanziari",
    "tax_expense": "Imposte",
    "depreciation": "Ammortamenti",
    "total_debt": "Debiti Finanziari Totali",
    "retained_earnings": "Riserve / Utili portati",
    "market_cap": "Capitalizzazione di Borsa",
    "working_capital": "Capitale Circolante Netto",
    "year": "Anno di esercizio",
}


@dataclass
class ERPParseResult:
    success: bool
    erp_type: str
    data: Dict[str, float] = field(default_factory=dict)
    missing_required: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    raw_df: Optional[pd.DataFrame] = None
    rows_imported: int = 0
    error: str = ""


def _detect_encoding(raw: bytes) -> str:
    result = chardet.detect(raw)
    enc = result.get("encoding", "utf-8") or "utf-8"
    # Forza latin-1 per file italiani common
    if enc.lower() in ("ascii", "windows-1252", "iso-8859-1"):
        return "latin-1"
    return enc


def _detect_delimiter(sample: str) -> str:
    counts = {d: sample.count(d) for d in [";", ",", "\t", "|"]}
    return max(counts, key=counts.get)


def _clean_number(val) -> Optional[float]:
    """Converte stringhe numeriche italiane (1.234.567,89) in float."""
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return None
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip().replace(" ", "").replace("\xa0", "")
    # Formato italiano: 1.234.567,89
    if "," in s and "." in s:
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    elif "," in s:
        s = s.replace(",", ".")
    s = s.replace("€", "").replace("$", "").strip()
    try:
        return float(s)
    except ValueError:
        return None


def _detect_erp_type(columns: List[str]) -> str:
    """Riconosce il tipo di ERP dai nomi delle colonne."""
    col_set = set(columns)
    best_match = ("GENERIC", 0)
    for erp_name, mapping in ERP_COLUMN_MAPS.items():
        matches = len(col_set.intersection(mapping.keys()))
        if matches > best_match[1]:
            best_match = (erp_name, matches)
    return best_match[0]


def _apply_mapping(df: pd.DataFrame, erp_type: str) -> Dict[str, float]:
    """Applica il mapping colonne ERP → standard NEXUS."""
    mapping = ERP_COLUMN_MAPS.get(erp_type, {})
    result = {}

    # Prima passa con il mapping esatto
    for erp_col, nexus_col in mapping.items():
        if erp_col in df.columns:
            # Prendi la riga con il valore più recente (ultimo anno)
            series = df[erp_col].apply(_clean_number).dropna()
            if not series.empty:
                result[nexus_col] = series.iloc[-1]

    # Fallback: cerca per nome simile (case-insensitive)
    if erp_type == "GENERIC":
        generic_map = {
            # Italiano
            "totale attivo": "total_assets", "totale_attivo": "total_assets",
            "attivo totale": "total_assets",
            "totale passivo": "total_liabilities", "totale_passivo": "total_liabilities",
            "passivo totale": "total_liabilities",
            "ricavi": "revenue", "fatturato": "revenue", "ricavi netti": "revenue",
            "vendite": "revenue",
            "ebit": "ebit", "reddito operativo": "ebit", "risultato operativo": "ebit",
            "ebitda": "ebitda", "mol": "ebitda", "margine operativo lordo": "ebitda",
            "utile netto": "net_income", "risultato netto": "net_income",
            "patrimonio netto": "equity", "capitale proprio": "equity",
            "attivo corrente": "current_assets", "attivo circolante": "current_assets",
            "passivo corrente": "current_liabilities", "passivo a breve": "current_liabilities",
            "magazzino": "inventory", "rimanenze": "inventory",
            "crediti clienti": "accounts_receivable", "crediti commerciali": "accounts_receivable",
            "debiti fornitori": "accounts_payable", "debiti commerciali": "accounts_payable",
            "immobilizzazioni": "fixed_assets", "immobilizzazioni nette": "fixed_assets",
            "oneri finanziari": "interest_expense", "interessi passivi": "interest_expense",
            "imposte": "tax_expense", "ires irap": "tax_expense",
            "ammortamenti": "depreciation",
            "debiti finanziari": "total_debt", "posizione finanziaria netta": "total_debt",
            "riserve": "retained_earnings", "utili portati": "retained_earnings",
            "capitalizzazione": "market_cap",
            "capitale circolante": "working_capital", "ccn": "working_capital",
            "anno": "year", "esercizio": "year",
            # Inglese
            "total assets": "total_assets", "total liabilities": "total_liabilities",
            "revenues": "revenue", "net revenue": "revenue", "sales": "revenue",
            "operating income": "ebit",
            "net income": "net_income", "net profit": "net_income",
            "equity": "equity", "shareholders equity": "equity",
            "current assets": "current_assets", "current liabilities": "current_liabilities",
            "inventory": "inventory", "inventories": "inventory",
            "accounts receivable": "accounts_receivable", "trade receivables": "accounts_receivable",
            "accounts payable": "accounts_payable", "trade payables": "accounts_payable",
            "fixed assets": "fixed_assets", "property plant equipment": "fixed_assets",
            "interest expense": "interest_expense",
            "income tax": "tax_expense", "taxes": "tax_expense",
            "depreciation": "depreciation", "depreciation amortization": "depreciation",
            "total debt": "total_debt", "financial debt": "total_debt",
            "retained earnings": "retained_earnings",
            "market cap": "market_cap", "market capitalization": "market_cap",
            "working capital": "working_capital",
            "year": "year", "fiscal year": "year",
        }
        for col in df.columns:
            key = col.strip().lower().replace("_", " ")
            if key in generic_map:
                nexus_col = generic_map[key]
                series = df[col].apply(_clean_number).dropna()
                if not series.empty and nexus_col not in result:
                    result[nexus_col] = series.iloc[-1]

    # Calcola campi derivati se mancanti
    if "working_capital" not in result and "current_assets" in result and "current_liabilities" in result:
        result["working_capital"] = result["current_assets"] - result["current_liabilities"]

    if "ebitda" not in result and "ebit" in result and "depreciation" in result:
        result["ebitda"] = result["ebit"] + result["depreciation"]

    return result


def parse_erp_file(file_bytes: bytes, filename: str) -> ERPParseResult:
    """
    Entry point principale. Accetta bytes del file e nome file.
    Restituisce ERPParseResult con tutti i dati estratti.
    """
    warnings = []
    ext = filename.lower().split(".")[-1]

    try:
        if ext in ("xlsx", "xls"):
            df = pd.read_excel(io.BytesIO(file_bytes), header=0)
        else:
            encoding = _detect_encoding(file_bytes)
            text = file_bytes.decode(encoding, errors="replace")
            delimiter = _detect_delimiter(text[:2000])
            df = pd.read_csv(io.StringIO(text), sep=delimiter, header=0, dtype=str)

        # Pulisci nomi colonne
        df.columns = [str(c).strip() for c in df.columns]
        df = df.dropna(how="all").dropna(axis=1, how="all")

        erp_type = _detect_erp_type(list(df.columns))
        data = _apply_mapping(df, erp_type)

        # Verifica campi obbligatori
        missing = [REQUIRED_FIELDS[f] for f in REQUIRED_FIELDS if f not in data]

        return ERPParseResult(
            success=True,
            erp_type=erp_type,
            data=data,
            missing_required=missing,
            warnings=warnings,
            raw_df=df,
            rows_imported=len(df),
        )

    except Exception as e:
        return ERPParseResult(
            success=False,
            erp_type="UNKNOWN",
            error=str(e),
        )


def get_template_df(erp_type: str = "GENERIC") -> pd.DataFrame:
    """Genera un DataFrame template per il tipo ERP selezionato."""
    if erp_type in ERP_COLUMN_MAPS:
        cols = list(ERP_COLUMN_MAPS[erp_type].keys())
    else:
        cols = list(REQUIRED_FIELDS.keys()) + list(OPTIONAL_FIELDS.keys())
        cols = [c.replace("_", " ").title() for c in cols]

    sample = {c: [0.0] for c in cols}
    return pd.DataFrame(sample)
