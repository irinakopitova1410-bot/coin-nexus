"""Synthetic civil-statement regression fixtures; no customer financial data."""
import io
import unittest

from utils.financial_import import read_financial_data
from utils.file_parser import (parse_credit_file, parse_zscore_file,
                              parse_ratios_file, parse_audit_file,
                              parse_credit_readiness_file, parse_financial_file)


FIXTURE = """Prospetto;Livello;Voce;31-01-2025 (EUR);31-01-2024 (EUR);Var. %
Stato Patrimoniale;Sezione;ATTIVO;;;
Stato Patrimoniale;Subtotale;Totale attivo circolante (C);450;400;0,125
Stato Patrimoniale;Totale;TOTALE ATTIVO;1000;1100;-0,091
Stato Patrimoniale;Sezione;PASSIVO;;;
Stato Patrimoniale;Voce;VIII - Utili (perdite) portati a nuovo;-20;10;-3
Stato Patrimoniale;Subtotale;Totale patrimonio netto;-100;100;-2
Stato Patrimoniale;Sezione;D) Debiti;;;
Stato Patrimoniale;Voce;4) debiti verso banche;;;
Stato Patrimoniale;Sotto-voce;esigibili entro l'esercizio successivo;300;200;0,5
Stato Patrimoniale;Subtotale;Totale debiti verso banche;300;200;0,5
Stato Patrimoniale;Voce;5) debiti verso altri finanziatori;;;
Stato Patrimoniale;Sotto-voce;esigibili entro l'esercizio successivo;0;50;-1
Stato Patrimoniale;Subtotale;Totale debiti verso altri finanziatori;0;50;-1
Stato Patrimoniale;Voce;7) debiti verso fornitori;;;
Stato Patrimoniale;Sotto-voce;esigibili entro l'esercizio successivo;550;450;0,2
Stato Patrimoniale;Sotto-voce;esigibili oltre l'esercizio successivo;50;100;-0,5
Stato Patrimoniale;Subtotale;Totale debiti verso fornitori;600;550;0,09
Stato Patrimoniale;Subtotale;Totale debiti;900;800;0,125
Stato Patrimoniale;Totale;TOTALE PASSIVO;1000;1100;-0,091
Conto Economico;Voce;1) ricavi delle vendite e delle prestazioni;800;900;-0,1
Conto Economico;Sotto-voce;a) ammortamento delle immobilizzazioni immateriali;5;10;-0,5
Conto Economico;Sotto-voce;b) ammortamento delle immobilizzazioni materiali;15;20;-0,25
Conto Economico;Sotto-voce;d) svalutazioni dei crediti compresi nell'attivo circolante e delle disponibilita' liquide;4;9;-0,5
Conto Economico;Subtotale;Totale ammortamenti e svalutazioni;24;39;-0,3
Conto Economico;Risultato;Differenza tra valore e costi della produzione (A - B);-40;-60;0,3
Conto Economico;Subtotale;Totale interessi e altri oneri finanziari;10;12;-0,16
Conto Economico;Risultato;Risultato prima delle imposte (A - B + - C + - D);-50;-72;0,3
Conto Economico;Totale;21) UTILE (PERDITA) DELL'ESERCIZIO;-55;-80;0,3
"""


def upload(text=FIXTURE):
    f = io.BytesIO(text.encode('utf-8'))
    f.name = 'EXAMPLE_SRL_Bilancio_SP_CE.csv'
    return f


class CivilBalanceTests(unittest.TestCase):
    def test_periods_totals_and_no_double_count(self):
        data = read_financial_data(upload())
        self.assertEqual(data['_source_period'], '2025-01-31')
        self.assertEqual(data['_comparison_period'], '2024-01-31')
        self.assertEqual(data['ricavi_netti'], 800)
        self.assertEqual(data['fatturato_prev'], 900)
        self.assertEqual(data['totale_debiti'], 900)
        self.assertEqual(data['debiti_finanziari_totali'], 300)
        self.assertEqual(data['debiti_esigibili_entro_esercizio_successivo'], 850)
        self.assertEqual(data['nome_azienda'], 'EXAMPLE SRL')

    def test_liabilities_exclude_negative_equity(self):
        data = read_financial_data(upload())
        self.assertEqual(data['totale_passivo_bilancio'], 1000)
        self.assertEqual(data['totale_passivita'], 1100)
        self.assertNotIn('passivo_corrente', data)
        self.assertNotIn('capitale_circolante_netto', data)

    def test_ebitda_uses_depreciation_not_all_writedowns(self):
        data = read_financial_data(upload())
        self.assertEqual(data['ammortamenti'], 20)
        self.assertEqual(data['ammortamenti_e_svalutazioni'], 24)
        self.assertEqual(data['ebitda'], -20)
        self.assertEqual(data['ebitda_precedente'], -30)

    def test_unknown_cashflows_are_not_zero(self):
        data = read_financial_data(upload())
        for field in ('cash_flow_operativo', 'capex', 'rimborso_debito'):
            self.assertNotIn(field, data)
        self.assertTrue(data['_import_warnings'])

    def test_missing_data_returns_preview_not_fabricated_score(self):
        for parser in (parse_credit_file, parse_zscore_file, parse_ratios_file,
                       parse_credit_readiness_file, parse_financial_file):
            with self.subTest(parser=parser.__name__):
                result = parser(upload())
                self.assertFalse(result['success'])
                self.assertTrue(result['requires_completion'])
                self.assertEqual(result['extracted_data']['ricavi_netti'], 800)
                self.assertTrue(result['missing_fields'])
        audit = parse_audit_file(upload())
        self.assertTrue(audit['success'])
        self.assertEqual(audit['pre_tax_income'], -50)
        self.assertTrue(audit['_import_warnings'])

    def test_columns_reordered_select_latest_date(self):
        import csv
        rows = list(csv.reader(io.StringIO(FIXTURE), delimiter=';'))
        for row in rows:
            row[3], row[4] = row[4], row[3]
        f = io.StringIO()
        csv.writer(f, delimiter=';').writerows(rows)
        self.assertEqual(read_financial_data(upload(f.getvalue()))['ricavi_netti'], 800)

    def test_missing_date_or_essential_captions_rejected(self):
        for text in (FIXTURE.replace('31-01-2025 (EUR)', 'current').replace('31-01-2024 (EUR)', 'previous'),
                     FIXTURE.replace('TOTALE ATTIVO', 'TOTAL UNKNOWN')):
            with self.assertRaises(ValueError):
                read_financial_data(upload(text))


if __name__ == '__main__':
    unittest.main()
