import io
import unittest
from pathlib import Path

from utils.financial_import import read_financial_data, parse_number
from utils.file_parser import (parse_credit_file, parse_zscore_file,
                              parse_ratios_file, parse_audit_file,
                              parse_credit_readiness_file, parse_financial_file)


def upload(text, name="test.csv", encoding="utf-8"):
    file = io.BytesIO(text.encode(encoding))
    file.name = name
    return file


class FinancialImportTests(unittest.TestCase):
    def test_localized_amounts(self):
        for text, expected in [("1.234,56", 1234.56), ("1,234.56", 1234.56),
                               ("(1.234,56 €)", -1234.56), ("1.234.567", 1234567),
                               ("1 234,56", 1234.56), ("2.41", 2.41),
                               ("0.123", .123), ("0", 0), ("1,234,567", 1234567),
                               ("1e6", 1000000), (1234.567, 1234.567)]:
            with self.subTest(text=text):
                self.assertAlmostEqual(parse_number(text), expected)

    def test_invalid_and_nonfinite_amounts(self):
        for text in ("bad", "nan", "inf", "1e999", "12.34.56", "1.234", "1,2,3", "(-123)"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                parse_number(text)

    def test_csv_variants_and_stream_position(self):
        for text in ("campo;valore;descrizione\nnome_azienda;Test;Azienda\nebit;1234,56;EBIT\n",
                     '\ufeffCAMPO,VALORE\nnome_azienda,Test\nebit,"1234,56"\n',
                     "# commento\ncampo\tvalore\nnome_azienda\tTest\nebit\t1234,56\n",
                     "sep=;\ncampo;valore\nnome_azienda;Test\nebit;1234,56\n"):
            file = upload(text)
            file.seek(4)
            data = read_financial_data(file)
            self.assertEqual(file.tell(), 4)
            self.assertAlmostEqual(parse_number(data["ebit"]), 1234.56)

    def test_headerless_and_horizontal(self):
        for text in ("ebit;100\nebitda;120\n", "ebit;100;risultato\nebitda;120;margine\n",
                     "ebit;ebitda\n100;120\n", "nome_azienda;ebit;ebitda\nTest;100;120\n"):
            data = read_financial_data(upload(text))
            self.assertEqual(parse_number(data["ebit"]), 100)
            self.assertEqual(parse_number(data["ebitda"]), 120)

    def test_empty_duplicate_malformed(self):
        for text in ("", "campo,valore\n", "campo,valore\nebit,1\nebit,2\n",
                     "campo,valore\nebit,1,2\n", 'campo,valore\nebit,"1\n'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                read_financial_data(upload(text))

    def test_excel_vertical_horizontal(self):
        import pandas as pd
        for rows in ([['campo', 'valore'], ['ebit', 1234.567]],
                     [['nome_azienda', 'ebit', 'ebitda'], ['Test', 1234.567, 1500]]):
            file = io.BytesIO()
            pd.DataFrame(rows).to_excel(file, header=False, index=False)
            file.name = "test.xlsx"
            data = read_financial_data(file)
            self.assertAlmostEqual(parse_number(data['ebit']), 1234.567)

    def test_all_entrypoints_surface_bad_numeric_data(self):
        parsers = (parse_credit_file, parse_zscore_file, parse_ratios_file,
                   parse_audit_file, parse_credit_readiness_file, parse_financial_file)
        for parser in parsers:
            with self.subTest(parser=parser.__name__):
                result = parser(upload("campo;valore\nnome_azienda;Test\nebit;NON_NUMERICO\n"))
                self.assertFalse(result['success'])
                self.assertIn('ebit', result['error'])

    def test_existing_fixture_compatibility(self):
        root = Path(__file__).resolve().parents[1]
        data = (root/'demo_data/COIN_SPA_Bilancio_Completo_2025.csv').read_bytes()
        for parser in (parse_credit_file, parse_zscore_file, parse_ratios_file,
                       parse_audit_file, parse_credit_readiness_file, parse_financial_file):
            file = io.BytesIO(data)
            file.name = 'fixture.csv'
            self.assertTrue(parser(file)['success'], parser.__name__)

    def test_unfilled_templates_do_not_produce_analysis(self):
        from utils.file_parser import get_bilancio_template_bytes
        for parser in (parse_credit_file, parse_zscore_file, parse_ratios_file,
                       parse_audit_file, parse_credit_readiness_file, parse_financial_file):
            file = io.BytesIO(get_bilancio_template_bytes())
            file.name = 'template.csv'
            result = parser(file)
            self.assertFalse(result['success'])
            self.assertIn('importi', result['error'])


if __name__ == '__main__':
    unittest.main()
