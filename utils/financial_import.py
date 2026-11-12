"""Strict, shared CSV/Excel reader. No network calls or database writes."""
import csv
import io
import math
import re
import unicodedata
from numbers import Real


def normalize_key(value):
    value = unicodedata.normalize("NFKD", str(value).lstrip("\ufeff"))
    value = "".join(c for c in value if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")


def is_blank(value):
    return value is None or str(value).strip().lower() in ("", "nan", "none", "null", "<na>")


def parse_number(value):
    """Parse native numbers, Italian/English money, grouped thousands and negatives.

    A single dot followed by three digits is ambiguous: reject instead of
    silently multiplying or dividing a financial amount by 1000.
    """
    if isinstance(value, Real):
        number = float(value)
    else:
        text = str(value).strip().replace("\u2212", "-")
        negative = text.startswith("(") and text.endswith(")")
        if negative:
            text = text[1:-1]
        text = re.sub(r"(?i)EUR", "", text).replace("€", "")
        text = re.sub(r"[\s\u00a0\u202f'’]", "", text)
        if "," in text and "." in text:
            decimal, grouping = (",", ".") if text.rfind(",") > text.rfind(".") else (".", ",")
            integer, fraction = text.rsplit(decimal, 1)
            if not re.fullmatch(r"[+-]?\d{1,3}(?:" + re.escape(grouping) + r"\d{3})+", integer):
                raise ValueError("Raggruppamento delle migliaia non valido")
            if not fraction.isdigit():
                raise ValueError("Parte decimale non valida")
            text = integer.replace(grouping, "") + "." + fraction
        elif "," in text:
            if text.count(",") > 1:
                if not re.fullmatch(r"[+-]?\d{1,3}(?:,\d{3})+", text):
                    raise ValueError("Separatore numerico non valido")
                text = text.replace(",", "")
            else:
                text = text.replace(",", ".")
        elif text.count(".") > 1:
            if not re.fullmatch(r"[+-]?\d{1,3}(?:\.\d{3})+", text):
                raise ValueError("Separatore numerico non valido")
            text = text.replace(".", "")
        elif re.fullmatch(r"[+-]?[1-9]\d{0,2}\.\d{3}", text):
            raise ValueError("Numero ambiguo: usa 1234 oppure 1234,00 invece di 1.234")
        if not re.fullmatch(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", text):
            raise ValueError("Valore non numerico")
        number = float(text)
        if negative:
            if number < 0:
                raise ValueError("Doppio segno negativo")
            number = -number
    if not math.isfinite(number):
        raise ValueError("Il valore deve essere finito")
    return number


def data_from_rows(rows):
    rows = [list(row) for row in rows if row and any(not is_blank(v) for v in row)]
    if not rows:
        raise ValueError("Il file è vuoto. Compila il modello prima di caricarlo.")
    header = [normalize_key(v) for v in rows[0]]
    pairs = []
    if "campo" in header and "valore" in header:
        ki, vi = header.index("campo"), header.index("valore")
        for index, row in enumerate(rows[1:], 2):
            if len(row) <= max(ki, vi):
                raise ValueError(f"Riga {index}: manca la colonna valore.")
            if len(row) > len(header):
                raise ValueError(f"Riga {index}: troppe colonne. Racchiudi i valori con virgole tra virgolette oppure usa il separatore punto e virgola.")
            pairs.append((row[ki], row[vi]))
    elif (len(rows) == 2 and len(rows[0]) == len(rows[1]) and len(rows[0]) > 2
          and all(re.fullmatch(r"[a-z][a-z0-9_]*", field) for field in header)):
        pairs = list(zip(rows[0], rows[1]))
    elif all(2 <= len(row) <= 3 for row in rows):
        # Also accept legacy two-column files with a generic heading, and
        # headerless key/value exports without dropping their first field.
        if header[0] in ("field", "voce", "parametro", "campo"):
            rows = rows[1:]
        elif len(rows) == 2 and header[0] in ("nome_azienda", "azienda", "ebit", "ebitda", "fatturato", "ricavi_netti", "totale_attivo"):
            # A two-column wide export has two field names in its header.
            if normalize_key(rows[0][1]) in ("fatturato", "ebit", "ebitda", "ricavi_netti", "totale_attivo"):
                pairs = list(zip(rows[0], rows[1]))
                rows = []
        pairs.extend((row[0], row[1]) for row in rows)
    else:
        raise ValueError("Formato non supportato: usa campo,valore,descrizione oppure un'unica riga di dati con intestazioni.")
    result = {}
    for field, value in pairs:
        key = normalize_key(field)
        if not key:
            continue
        if key in result:
            raise ValueError(f"Campo duplicato: {key}. Mantieni una sola riga per voce.")
        result[key] = value
    if not result:
        raise ValueError("Nessun dato presente dopo l'intestazione.")
    return result


def read_financial_data(uploaded_file):
    """Read without consuming the upload; preserve numeric strings until parsing."""
    position = uploaded_file.tell()
    try:
        uploaded_file.seek(0)
        raw = uploaded_file.read()
    finally:
        uploaded_file.seek(position)
    if len(raw) > 10 * 1024 * 1024:
        raise ValueError("File troppo grande: limite 10 MB.")
    if str(getattr(uploaded_file, "name", "")).lower().endswith((".xlsx", ".xls")):
        import pandas as pd
        frame = pd.read_excel(io.BytesIO(raw), header=None, dtype=object, keep_default_na=False)
        return data_from_rows(frame.values.tolist())
    if isinstance(raw, str):
        text = raw
    else:
        for encoding in ("utf-8-sig", "cp1252"):
            try:
                text = raw.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        else:
            raise ValueError("Codifica non supportata. Salva il file come CSV UTF-8.")
    # Comment lines are ignored only outside quoted multiline CSV cells.
    lines, quoted = [], False
    for line in text.splitlines(keepends=True):
        if not quoted and (not line.strip() or line.lstrip().startswith("#")):
            continue
        lines.append(line)
        if line.count('"') % 2:
            quoted = not quoted
    text = "".join(lines)
    if not text.strip():
        raise ValueError("Il file è vuoto.")
    # Excel adds this optional delimiter declaration to some CSV exports.
    first, _, rest = text.partition("\n")
    if re.fullmatch(r"sep=[;,\t|]\s*", first, re.I):
        delimiter, text = first[4], rest
    else:
        first = text.splitlines()[0]
        candidates = [(len(next(csv.reader([first], delimiter=d))), d) for d in (",", ";", "\t", "|")]
        width, delimiter = max(candidates, key=lambda item: item[0])
        if width < 2:
            raise ValueError("Separatore CSV non riconosciuto: usa virgola, punto e virgola o tabulazione.")
    try:
        return data_from_rows(list(csv.reader(io.StringIO(text), delimiter=delimiter, strict=True)))
    except csv.Error as exc:
        raise ValueError("CSV non valido: controlla virgolette e separatori.") from exc
