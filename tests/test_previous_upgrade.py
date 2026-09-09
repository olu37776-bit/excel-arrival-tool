from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from openpyxl import load_workbook

from revenue_tool.adapters.excel_writer import ExcelOutputAdapter
from revenue_tool.adapters.formula_cache import _patch
from revenue_tool.config import load_config
from revenue_tool.domain.models import BaseRow, IssueLog
from revenue_tool.services.final_revenue import FINAL_FIELD_SOURCES, calculate_final_values
from tests.test_final_revenue import formula_cases
from tests.test_manual_revenue_forecast import (
    POST_32_FIELD_IDS, _remove_fields_from_result, _set_manual_inputs,
)
from tests.test_pipeline import CONFIG, _base_rows, _run, _write_sources


class PreviousUpgradeTest(unittest.TestCase):
    def test_empty_self_closing_cell_does_not_consume_next_formula(self):
        # ElementTree emits <c ... />, whereas lxml emits <c ...></c>.
        for empty in (b'<c r="A1" />', b'<c r="A1"></c>'):
            xml = b'<row>' + empty + b'<c r="B1"><f>1+1</f><v /></c></row>'
            result = _patch(xml, {'B1': 2})
            self.assertIn(empty, result)
            self.assertIn(b'<c r="B1" t="n"><f>1+1</f><v>2</v></c>', result)

    def test_old_layouts_generate_values_without_opening_excel(self):
        for removed in (POST_32_FIELD_IDS, tuple(FINAL_FIELD_SOURCES)):
            with self.subTest(removed=removed), TemporaryDirectory() as tmp:
                root = Path(tmp)
                sources = _write_sources(root, 'old', variant='first')
                old, new = root / 'old.xlsx', root / 'new.xlsx'
                _run(sources, old)
                _set_manual_inputs(old, 'C001', 'SC-A', segment_flag=False,
                                   rpd='2026-9', cpd='2026-10', amount=0)
                _remove_fields_from_result(old, removed)
                _run(sources, new, previous=old)
                wb = load_workbook(new, data_only=True)
                try:
                    row = _base_rows(wb['基表'])[('C001', 'SC-A')]
                    if removed == POST_32_FIELD_IDS:
                        self.assertEqual(row['收入分段类别'], row['最终收入分段类别'])
                        self.assertEqual(row['收入年月（按RPD）'], row['最终收入年月（按RPD）'])
                        self.assertEqual(row['收入年月（按CPD）'], row['最终收入年月（按CPD）'])
                        self.assertEqual(row['遗留量'] + row['当月新订货'], row['收入预测'])
                    else:
                        self.assertIs(False, row['最终收入分段类别'])
                        self.assertEqual('2026-09', row['最终收入年月（按RPD）'])
                        self.assertEqual('2026-10', row['最终收入年月（按CPD）'])
                    self.assertEqual(0, row['最终收入预测'])
                    self.assertEqual(0, row['调整金额'])
                    self.assertFalse(any(sheet._pivots for sheet in wb.worksheets))
                    self.assertNotIn('_summary_source', wb.sheetnames)
                finally:
                    wb.close()

    def test_formula_caches_match_calculated_values_and_preserve_formulas(self):
        with TemporaryDirectory() as tmp:
            config = load_config(CONFIG)
            cases = formula_cases() + [dict(revenue_segment='A < B & C > D')]
            rows = [BaseRow(dict(v, contract_no=f'T{i}', region='地区'))
                    for i, v in enumerate(cases)]
            path = Path(tmp) / 'values.xlsx'
            ExcelOutputAdapter().write(path, rows, [], [], [], IssueLog(), config)
            cached = load_workbook(path, data_only=True)
            live = load_workbook(path)
            indexes = {c['id']: i for i, c in enumerate(config.base_columns, 1)}
            try:
                for number, values in enumerate(cases, 2):
                    for field, expected in calculate_final_values(values).items():
                        actual = cached['基表'].cell(number, indexes[field]).value
                        if isinstance(expected, Decimal):
                            expected = float(expected)
                        self.assertEqual(expected, actual, (number, field))
                        if isinstance(expected, bool):
                            self.assertIs(expected, actual)
                        self.assertEqual('f', live['基表'].cell(number, indexes[field]).data_type)
                self.assertEqual('auto', live.calculation.calcMode)
                self.assertFalse(live.calculation.fullCalcOnLoad)
                self.assertFalse(live.calculation.forceFullCalc)
                self.assertFalse(live.calculation.calcOnSave)
            finally:
                cached.close()
                live.close()
