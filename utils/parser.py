def extract_financials(df):
    """
    Estrae dati finanziari base da ERP generico con logica robusta
    """

    if "descrizione" not in df.columns or "saldo" not in df.columns:
        return default_financials()

    df["descrizione"] = df["descrizione"].astype(str).str.lower()

    def get(keywords, exclude=None):
        mask = df["descrizione"].str.contains("|".join(keywords))
        if exclude:
            mask &= ~df["descrizione"].str.contains("|".join(exclude))
        return df[mask]["saldo"].sum()

    # --- CASH ---
    cash = get(["cassa", "banca"])

    # --- CREDITI (solo operativi) ---
    receivables = get(
        ["crediti"],
        exclude=["tributari", "fiscali"]
    )

    # --- MAGAZZINO ---
    inventory = get(["magazzino", "rimanenze"])

    # --- DEBITI ---
    payables = get(
        ["debiti"],
        exclude=["tributari", "fiscali"]
    )

    # --- DEBITI BREVE (stima) ---
    short_debt = get(["debiti", "fornitori", "entro 12"])

    # --- CONTROLLO QUALITÀ (🔥 importante) ---
    detected_items = sum([
        cash != 0,
        receivables != 0,
        payables != 0
    ])

    confidence = "alta" if detected_items >= 3 else "media" if detected_items == 2 else "bassa"

    return {
        "cash": cash,
        "receivables": receivables,
        "inventory": inventory,
        "payables": payables,
        "short_debt": short_debt,

        # 🔥 valore percepito
        "data_quality": confidence
    }


def default_financials():
    return {
        "cash": 0,
        "receivables": 0,
        "inventory": 0,
        "payables": 0,
        "short_debt": 0,
        "data_quality": "bassa"
    }
