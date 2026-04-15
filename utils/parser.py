import pandas as pd

def load_data(file):
    """
    Carica CSV o Excel in modo sicuro (Streamlit-ready)
    """

    try:
        if file.name.endswith(".csv"):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)

        # pulizia base colonne
        df.columns = [c.strip().lower() for c in df.columns]

        return df

    except Exception as e:
        return pd.DataFrame()


def extract_financials(df):
    """
    Estrae dati finanziari base da ERP generico
    """

    # sicurezza: evita crash se colonne mancanti
    if "descrizione" not in df.columns or "saldo" not in df.columns:
        return {
            "cash": 0,
            "receivables": 0,
            "inventory": 0,
            "payables": 0
        }

    df["descrizione"] = df["descrizione"].astype(str).str.lower()

    def get(keyword):
        return df[df["descrizione"].str.contains(keyword)]["saldo"].sum()

    cash = get("cassa") + get("banca")
    receivables = get("crediti")
    inventory = get("magazzino")
    payables = get("debiti")

    return {
        "cash": cash,
        "receivables": receivables,
        "inventory": inventory,
        "payables": payables
    }
