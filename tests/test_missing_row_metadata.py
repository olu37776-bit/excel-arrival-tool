from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from openpyxl import load_workbook
from revenue_tool.adapters.excel_reader import ExcelInputAdapter
from revenue_tool.config import load_config
from revenue_tool.domain.models import IssueLog
from tests.test_pipeline import CONFIG, _write_sources, _run, _base_rows


class MissingRowMetadataTest(unittest.TestCase):
    def test_two_period_manual_values_survive_missing_metadata(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            sources = _write_sources(root, 'src', variant='first')
            def amounts(monthly):
                for path, amount in zip(sources[:2], (0, monthly)):
                    wb = load_workbook(path)
                    for row in wb.active.iter_rows(min_row=3):
                        if row[0].value == 'C001':
                            row[-1].value = amount
                    wb.save(path)
                    wb.close()
            amounts(0)
            old, new = root / 'old.xlsx', root / 'new.xlsx'
            _run(sources, old)
            wb = load_workbook(old)
            sheet = wb['基表']
            cols = {c.value: c.column for c in sheet[1]}
            for row in sheet.iter_rows(min_row=2):
                if row[0].value == 'C001':
                    row[cols['调整金额'] - 1].value = .25
                    row[cols['调整备注'] - 1].value = '上期预估'
            meta = wb['_tool_meta']
            for row in list(meta.iter_rows()):
                if row[0].value == 'C001':
                    row[0].value = 'stale-key'
            wb.save(old)
            wb.close()
            before = old.read_bytes()
            amounts(.77)
            _run(sources, new, previous=old)
            wb = load_workbook(new, data_only=True)
            for center in ('SC-A', 'SC-B'):
                row = _base_rows(wb['基表'])[('C001', center)]
                self.assertEqual(.77, row['当月新订货'])
                self.assertEqual(.25, row['调整金额'])
                self.assertEqual(.25, row['最终收入预测'])
                self.assertEqual('上期预估', row['调整备注'])
            wb.close()
            self.assertEqual(before, old.read_bytes())

    def test_formatted_contract_key_and_missing_metadata(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            old = root / 'old.xlsx'
            _run(_write_sources(root, 'src', variant='first'), old)
            wb = load_workbook(old)
            base = wb['基表']
            base['A2'] = 123
            base['A2'].number_format = '00000'
            base['AL2'] = .25
            base['AO2'] = '保留备注'
            wb.save(old)
            wb.close()
            issues = IssueLog()
            previous = ExcelInputAdapter().read_previous(old, load_config(CONFIG), issues)
            row = previous.rows[('00123', 'sc-a')]
            self.assertEqual('保留备注', row.values['adjustment_note'])
            self.assertIn('PREVIOUS_ROW_KIND_RECOVERED', {i.code for i in issues.items})
