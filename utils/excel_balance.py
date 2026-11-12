"""Read comparative SP/CE worksheets without importing derived KPI sheets."""
import re
from datetime import datetime
from utils.civil_balance import CAPTIONS, parse_civil_balance


# Caption aliases, never company values. Keys are normalized after accounting prefixes.
ALIASES = {
    "totale_imm_immateriali": "totale_immobilizzazioni_immateriali",
    "totale_imm_materiali": "totale_immobilizzazioni_materiali",
    "rimanenze_prodotti_finiti_e_merci": "totale_rimanenze",
    "crediti_verso_clienti": "totale_crediti_verso_clienti",
    "disponibilita_liquide": "totale_disponibilita_liquide",
    "fondi_rischi_e_oneri": "totale_fondi_per_rischi_ed_oneri",
    "tfr": "trattamento_di_fine_rapporto_di_lavoro_subordinato",
    "debiti_verso_banche": "totale_debiti_verso_banche",
    "debiti_verso_fornitori": "totale_debiti_verso_fornitori",
    "ricavi_delle_vendite_e_prestazioni": "ricavi_delle_vendite_e_delle_prestazioni",
    "altri_ricavi_e_proventi": "totale_altri_ricavi_e_proventi",
    "totale_valore_produzione_a": "totale_valore_della_produzione_a",
    "totale_costi_produzione_b": "totale_costi_della_produzione_b",
    "materie_prime_e_merci": "per_materie_prime_sussidiarie_di_consumo_e_di_merci",
    "servizi": "per_servizi",
    "godimento_beni_di_terzi_affitti": "per_godimento_di_beni_di_terzi",
    "costi_per_il_personale": "totale_costi_per_il_personale",
    "amm_immobilizzazioni_immateriali": "ammortamento_delle_immobilizzazioni_immateriali",
    "amm_immobilizzazioni_materiali": "ammortamento_delle_immobilizzazioni_materiali",
    "ammortamenti_e_svalutazioni": "totale_ammortamenti_e_svalutazioni",
    "ebit_a_b_risultato_operativo": "differenza_tra_valore_e_costi_della_produzione_a_b",
    "interessi_e_oneri_finanziari": "totale_interessi_e_altri_oneri_finanziari",
    "risultato_prima_delle_imposte": "risultato_prima_delle_imposte_a_b_c_d",
    "imposte_sul_reddito": "totale_delle_imposte_sul_reddito_dell_esercizio_correnti_differite_e_anticipate",
}
SP_FIELDS = {
    "totale_attivo", "totale_passivo_bilancio", "patrimonio_netto", "totale_debiti",
    "debiti_banche", "debiti_altri_finanziatori", "debiti_fornitori", "crediti_clienti",
    "totale_crediti", "rimanenze", "disponibilita_liquide", "totale_attivo_circolante",
    "totale_immobilizzazioni", "immobilizzazioni_materiali", "immobilizzazioni_immateriali",
    "utili_non_distribuiti", "fondi_rischi_oneri", "tfr",
}


def _caption(value, normalize):
    text = str(value).strip()
    text = re.sub(r"^[A-Z]\.(?:[IVXLCDM]+|\d+)\s+", "", text)
    text = re.sub(r"^[A-Z]\s+(?:[—–-]\s*)?", "", text)
    key = normalize(text)
    return ALIASES.get(key, key)


def _header(rows):
    for index, row in enumerate(rows[:20]):
        dates = {}
        for column, value in enumerate(row[1:], 1):
            match = re.search(r"\b(\d{2}[/\-]\d{2}[/\-]\d{4})\b", str(value))
            if match:
                date = datetime.strptime(match.group(1).replace("/", "-"), "%d-%m-%Y").date()
                if date in dates:
                    raise ValueError("Excel: colonne con date duplicate; impossibile scegliere l’esercizio.")
                dates[date] = column
        if dates:
            return index, dates
    raise ValueError("Excel SP/CE: manca un’intestazione con date GG/MM/AAAA.")


def read_statement_sheets(sheets, normalize, parse_number, is_blank, filename):
    selected = {}
    for name, frame in sheets.items():
        key = normalize(name)
        kind = ("stato_patrimoniale" if key in ("sp", "stato_patrimoniale") else
                "conto_economico" if key in ("ce", "conto_economico") else None)
        if kind:
            if kind in selected:
                raise ValueError("Excel: più prospetti dello stesso tipo; selezione ambigua.")
            selected[kind] = (name, frame.values.tolist())
    if not selected:
        return None
    if len(selected) != 2:
        raise ValueError("Excel: servono entrambi i fogli Stato Patrimoniale e Conto Economico.")
    headers = {kind: _header(rows) for kind, (_, rows) in selected.items()}
    periods = set(headers["stato_patrimoniale"][1])
    if periods != set(headers["conto_economico"][1]):
        raise ValueError("Excel: gli esercizi di Stato Patrimoniale e Conto Economico non coincidono.")
    periods = sorted(periods, reverse=True)
    combined = [["prospetto", "livello", "voce"] + [d.strftime("%d/%m/%Y") for d in periods]]
    origins = {}
    signed_expenses = False
    reported_ebitda = None
    for kind, (sheet, rows) in selected.items():
        start, columns = headers[kind]
        for row_index, row in enumerate(rows[start + 1:], start + 2):
            caption = _caption(row[0], normalize)
            if kind == "conto_economico" and caption in ("ebitda", "ebitda_ebit_ammortamenti"):
                raw = row[columns[periods[0]]]
                if not is_blank(raw):
                    reported_ebitda = parse_number(raw)
            field = CAPTIONS.get(caption)
            if field is None or (kind == "stato_patrimoniale") != (field in SP_FIELDS):
                continue
            values = [row[columns[date]] for date in periods]
            if all(is_blank(value) for value in values):
                continue
            source_value = values[0]
            # Some statements use negative signs for expenses. Downstream ratios
            # require the positive amount of interest expense, not a revenue.
            if field == "interessi_passivi":
                signed_expenses = signed_expenses or any(not is_blank(v) and parse_number(v) < 0 for v in values)
                values = [abs(parse_number(v)) if not is_blank(v) else v for v in values]
            combined.append([kind, "totale", caption] + values)
            origins[len(combined)] = {"sheet": sheet, "row": row_index,
                                      "caption": str(row[0]), "column": columns[periods[0]] + 1,
                                      "raw_value": source_value}
    result = parse_civil_balance(combined, normalize, parse_number, is_blank, filename)
    for origin in result.get("_source_rows", {}).values():
        if origin["row"] in origins:
            origin.update(origins[origin["row"]])
    result["_source_sheets"] = [name for name, _ in selected.values()]
    result["_import_warnings"].append("Letti i fogli SP/CE; fogli di KPI e indicatori derivati non importati. Verifica gli importi sui prospetti originali.")
    if signed_expenses:
        result["_import_warnings"].append("Oneri finanziari esposti con segno negativo nel prospetto: importati come importo positivo del costo. Il valore originale resta nella provenienza del dato.")
    if reported_ebitda is not None and "ebitda" in result and abs(reported_ebitda - result["ebitda"]) > 1:
        result["_reported_ebitda"] = reported_ebitda
        result["_import_warnings"].append("L’EBITDA riportato nel foglio differisce da EBIT + ammortamenti materiali e immateriali. NEXUS mantiene questo calcolo separato: verificare eventuali svalutazioni o rettifiche incluse nel valore esposto.")
    return result
