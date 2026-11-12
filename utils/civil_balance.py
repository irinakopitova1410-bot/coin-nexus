"""Adapter for Italian civil balance-sheet/income-statement comparative exports.

Only explicit totals or identified statement lines are mapped. Sections,
detail rows and totals are never added together. No cash flows are inferred.
"""
import re
from datetime import datetime
from pathlib import Path


def _label(value, normalize):
    text = str(value).strip()
    text = re.sub(r"^(?:[A-Z]\)|\d+(?:-[a-z]+)?\)|[IVXLCDM]+\s*[-–]|[a-z]\))\s*", "", text)
    return normalize(text)


# Standard civil-accounting captions, not company-specific values.
CAPTIONS = {
    "totale_attivo": "totale_attivo",
    "totale_passivo": "totale_passivo_bilancio",
    "totale_patrimonio_netto": "patrimonio_netto",
    "totale_debiti": "totale_debiti",
    "totale_debiti_verso_banche": "debiti_banche",
    "totale_debiti_verso_altri_finanziatori": "debiti_altri_finanziatori",
    "totale_debiti_verso_fornitori": "debiti_fornitori",
    "totale_crediti_verso_clienti": "crediti_clienti",
    "totale_crediti": "totale_crediti",
    "totale_rimanenze": "rimanenze",
    "totale_disponibilita_liquide": "disponibilita_liquide",
    "totale_attivo_circolante_c": "totale_attivo_circolante",
    "totale_attivo_circolante": "totale_attivo_circolante",
    "totale_immobilizzazioni_b": "totale_immobilizzazioni",
    "totale_immobilizzazioni": "totale_immobilizzazioni",
    "totale_immobilizzazioni_materiali": "immobilizzazioni_materiali",
    "totale_immobilizzazioni_immateriali": "immobilizzazioni_immateriali",
    "utili_perdite_portati_a_nuovo": "utili_non_distribuiti",
    "utile_perdita_dell_esercizio": "utile_netto",
    "ricavi_delle_vendite_e_delle_prestazioni": "ricavi_netti",
    "totale_altri_ricavi_e_proventi": "altri_ricavi",
    "totale_valore_della_produzione_a": "totale_valore_produzione",
    "totale_costi_della_produzione_b": "totale_costi_produzione",
    "differenza_tra_valore_e_costi_della_produzione_a_b": "ebit",
    "per_materie_prime_sussidiarie_di_consumo_e_di_merci": "costi_materie_prime",
    "per_servizi": "costi_servizi",
    "per_godimento_di_beni_di_terzi": "costi_affitti",
    "totale_costi_per_il_personale": "costi_personale",
    "ammortamento_delle_immobilizzazioni_immateriali": "ammortamenti_immateriali",
    "ammortamento_delle_immobilizzazioni_materiali": "ammortamenti_materiali",
    "totale_ammortamenti_e_svalutazioni": "ammortamenti_e_svalutazioni",
    "totale_interessi_e_altri_oneri_finanziari": "interessi_passivi",
    "totale_altri_proventi_finanziari": "proventi_finanziari",
    "risultato_prima_delle_imposte_a_b_c_d": "risultato_ante_imposte",
    "totale_delle_imposte_sul_reddito_dell_esercizio_correnti_differite_e_anticipate": "imposte",
    "totale_fondi_per_rischi_ed_oneri": "fondi_rischi_oneri",
    "trattamento_di_fine_rapporto_di_lavoro_subordinato": "tfr",
}


def is_civil_balance_header(header):
    return all(key in header for key in ("prospetto", "livello", "voce"))


def parse_civil_balance(rows, normalize, parse_number, is_blank, filename=""):
    header = [normalize(v) for v in rows[0]]
    periods = []
    for index, caption in enumerate(rows[0]):
        match = re.search(r"\b(\d{2}[-/]\d{2}[-/]\d{4})\b", str(caption))
        if match:
            date = datetime.strptime(match.group(1).replace("/", "-"), "%d-%m-%Y").date()
            periods.append((date, index))
    if not periods:
        raise ValueError("Prospetto civilistico riconosciuto, ma nessuna colonna esercizio con data GG-MM-AAAA.")
    if len({date for date, _ in periods}) != len(periods):
        raise ValueError("Date esercizio duplicate: specifica una sola colonna per periodo.")
    periods.sort(reverse=True)
    pi, li, vi = (header.index(key) for key in ("prospetto", "livello", "voce"))
    warnings = []
    provenance = {}

    def extract(column):
        output, origins = {}, {}
        balance_side, debt_context = "", False
        short_debt = []

        def store(key, number, index, caption):
            if key in output and output[key] != number:
                raise ValueError(f"Voce {key} presente più volte con importi diversi (riga {index}).")
            output[key] = number
            origins.setdefault(key, {"row": index, "caption": str(caption), "column": str(rows[0][column])})

        for index, row in enumerate(rows[1:], 2):
            if len(row) != len(header):
                raise ValueError(f"Riga {index}: il numero di colonne non coincide con l'intestazione.")
            statement = normalize(row[pi])
            level = normalize(row[li])
            caption = _label(row[vi], normalize)
            if statement == "stato_patrimoniale":
                if caption in ("attivo", "passivo"):
                    balance_side = caption
                    debt_context = False
                if level == "voce":
                    debt_context = caption.startswith("debiti_") or caption == "altri_debiti"
                if caption.startswith("ratei_e_risconti"):
                    debt_context = False
            else:
                debt_context = False
            raw = row[column]
            if is_blank(raw):
                continue
            key = CAPTIONS.get(caption)
            if caption == "ratei_e_risconti" and balance_side:
                key = "ratei_risconti_attivi" if balance_side == "attivo" else "ratei_risconti_passivi"
            if key is not None:
                store(key, parse_number(raw), index, row[vi])
            if (statement == "stato_patrimoniale" and debt_context
                    and level == "sotto_voce" and caption == "esigibili_entro_l_esercizio_successivo"):
                short_debt.append(parse_number(raw))
        if short_debt:
            output["debiti_esigibili_entro_esercizio_successivo"] = sum(short_debt)
        if "totale_attivo" in output and "patrimonio_netto" in output:
            output["totale_passivita"] = output["totale_attivo"] - output["patrimonio_netto"]
        depreciation = ("ammortamenti_immateriali", "ammortamenti_materiali")
        if all(key in output for key in depreciation):
            output["ammortamenti"] = sum(output[key] for key in depreciation)
            if "ebit" in output:
                output["ebitda"] = output["ebit"] + output["ammortamenti"]
        if all(key in output for key in ("debiti_banche", "debiti_altri_finanziatori")):
            output["debiti_finanziari_totali"] = output["debiti_banche"] + output["debiti_altri_finanziatori"]
        return output, origins

    current, provenance = extract(periods[0][1])
    if not all(key in current for key in ("totale_attivo", "patrimonio_netto", "ricavi_netti", "ebit")):
        raise ValueError("Prospetto riconosciuto ma mancano voci essenziali mappabili (attivo, patrimonio netto, ricavi o EBIT). Nessuna analisi generata.")
    stem = Path(filename).stem
    company = re.split(r"_bilancio\b|_bilancio_", stem, maxsplit=1, flags=re.I)[0].replace("_", " ").strip()
    if company and company != stem.replace("_", " "):
        current["nome_azienda"] = company
        warnings.append("Ragione sociale ricavata dal nome del file: verifica che sia corretta.")
    current["anno_bilancio"] = periods[0][0].year
    warnings.append(f"Importato l'esercizio chiuso al {periods[0][0].strftime('%d/%m/%Y')}; gli esercizi non sono sommati.")
    if len(periods) > 1:
        previous, _ = extract(periods[1][1])
        for key, value in previous.items():
            current[key + "_precedente"] = value
        if "ricavi_netti" in previous:
            current["fatturato_prev"] = previous["ricavi_netti"]
        current["_comparison_period"] = periods[1][0].isoformat()
    warnings.extend([
        "TOTALE PASSIVO include il patrimonio netto: le passività verso terzi sono ricavate da Attivo meno Patrimonio netto, non dal totale passivo di bilancio.",
        "Il file non contiene il totale completo delle passività correnti, il rendiconto finanziario, il cash flow operativo, il piano di rimborso o il servizio del debito prospettico. Non è sufficiente da solo per validare DSCR, liquidità e Credit Readiness.",
        "I debiti esigibili entro l'esercizio successivo, quando presenti, sono un dettaglio delle scadenze dei debiti: non sono automaticamente tutte le passività correnti.",
    ])
    if "ebitda" in current:
        warnings.append("EBITDA derivato = EBIT + ammortamenti materiali e immateriali; non vengono riaggiunte automaticamente tutte le svalutazioni. Non è un EBITDA adjusted certificato.")
    total_passive = current.get("totale_passivo_bilancio")
    if total_passive is not None and abs(total_passive - current["totale_attivo"]) > 2:
        warnings.append("ATTENZIONE: totale attivo e totale passivo di bilancio non coincidono; verifica il prospetto originale.")
    current.update({
        "_source_format": "civil_balance",
        "_source_period": periods[0][0].isoformat(),
        "_import_warnings": warnings,
        "_missing_fields": ["passivo_corrente", "cash_flow_operativo", "rimborso_debito", "servizio_debito_prospettico"],
        "_source_rows": provenance,
    })
    return current
