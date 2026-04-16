def extract_financials(df):
    """
    Estrae dati finanziari con controllo qualità per credit engine
    """

    if "descrizione" not in df.columns or "saldo" not in df.columns:
        return default_financials()

    df["descrizione"] = df["descrizione"].astype(str).str.lower()

    def get(keywords, exclude=None):
        mask = df["descrizione"].str.contains("|".join(keywords))
        if exclude:
            mask &= ~df["descrizione"].str.contains("|".join(exclude))
        return df[mask]["saldo"].sum()

    cash = get(["cassa", "banca"])
    receivables = get(["crediti"], exclude=["tributari", "fiscali"])
    inventory = get(["magazzino", "rimanenze"])
    payables = get(["debiti"], exclude=["tributari", "fiscali"])
    short_debt = get(["debiti", "fornitori", "entro 12"])

    # --- DATA QUALITY CHECK ---
    issues = []

    if receivables < 0:
        issues.append("Crediti negativi rilevati")
    if payables < 0:
        issues.append("Debiti negativi rilevati")
    if cash < 0:
        issues.append("Cassa negativa rilevata")

    confidence = (
        "alta" if len(issues) == 0
        else "media" if len(issues) <= 2
        else "bassa"
    )

    return {
        "cash": cash,
        "receivables": receivables,
        "inventory": inventory,
        "payables": payables,
        "short_debt": short_debt,

        # 🔥 importante per il prodotto
        "data_quality": confidence,
        "data_issues": issues
    }


def default_financials():
    return {
        "cash": 0,
        "receivables": 0,
        "inventory": 0,
        "payables": 0,
        "short_debt": 0,
        "data_quality": "bassa",
        "data_issues": ["Dati mancanti o non leggibili"]
    }
