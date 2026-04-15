import pandas as pd

def extract_financials(df):

    df.columns = [c.lower() for c in df.columns]
    df["descrizione"] = df["descrizione"].astype(str).str.lower()

    def get(key):
        return df[df["descrizione"].str.contains(key)]["saldo"].sum()

    cash = get("cassa") + get("banca")
    receivables = get("crediti")
    inventory = get("magazzino") + get("rimanenze")
    payables = get("debiti")

    total_assets = cash + receivables + inventory

    return {
        "cash": cash,
        "receivables": receivables,
        "inventory": inventory,
        "payables": payables,
        "current_assets": total_assets
    }
