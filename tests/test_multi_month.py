from decimal import Decimal
import json
import os
from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory
import unittest
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from openpyxl import load_workbook
from revenue_tool.adapters.excel_writer import ExcelOutputAdapter
from revenue_tool.config import load_config
from revenue_tool.domain.models import IssueLog
from revenue_tool.services.regional_summary import report_months, build_regional_summary
from tests.test_pipeline import CONFIG
from tests.test_regional_summary import example_rows


class MultiMonthTest(unittest.TestCase):
    def test_selection_validation_and_deduplication(self):
        self.assertEqual(('2026-08', '2026-09'), report_months(['2026-09', '2026-08', '2026-09']))
        for value in ([], False, [None], ['2026-9'], ['0000-01']):
            with self.assertRaises(ValueError):
                report_months(value)

    def test_independent_pivots_dropdowns_and_unprotected_base(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / 'multi.xlsx'
            ExcelOutputAdapter().write(path, example_rows(), [], [], [], IssueLog(), load_config(CONFIG), ['2026-08', '2026-09'])
            wb = load_workbook(path)
            try:
                self.assertFalse(wb['基表'].protection.sheet)
                self.assertEqual(40, wb['基表'].max_column)
                caches = set()
                names = set()
                for month in ('2026-08', '2026-09'):
                    for mode in ('RPD', 'CPD'):
                        sheet = wb[f'{mode}地区收入汇总-{month}']
                        self.assertEqual(month, sheet['C4'].value)
                        validation = sheet.data_validations.dataValidation[0]
                        self.assertEqual('list', validation.type)
                        self.assertFalse(validation.showDropDown)
                        self.assertEqual(12, len(validation.formula1.strip('"').split(',')))
                        pivot = sheet._pivots[0]
                        caches.add(pivot.cacheId)
                        names.add(pivot.name)
                        source_title = pivot.cache.cacheSource.worksheetSource.sheet
                        self.assertEqual(f'_summary_{month.replace("-", "_")}', source_title)
                        source = wb[source_title]
                        number = 2 if mode == 'RPD' else 2 + 2 * len(example_rows())
                        self.assertIn(sheet.title, source.cell(number, 42).value)
                        expected = (100 if mode == 'RPD' else 20) if month == '2026-08' else (29 if mode == 'RPD' else 159)
                        self.assertEqual(expected, sheet['G13'].value)
                self.assertEqual(2, len(caches))
                self.assertEqual(4, len(names))
            finally:
                wb.close()
            with ZipFile(path) as archive:
                ns = {'x': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
                base = ET.fromstring(archive.read('xl/worksheets/sheet1.xml'))
                self.assertIsNone(base.find('x:sheetProtection', ns))
                for name in archive.namelist():
                    if name.startswith('xl/pivotTables/pivotTable') and name.endswith('.xml'):
                        root = ET.fromstring(archive.read(name))
                        self.assertNotIn('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id', root.attrib)
                        self.assertFalse(root.findall('.//x:pivotField/x:items/x:item[@t="grand"]', ns))

    def test_refresh_one_month_does_not_change_other_month_details(self):
        office = shutil.which('libreoffice') or shutil.which('soffice')
        uno_python = Path('/usr/bin/python3')
        if not office or not uno_python.exists() or subprocess.run([str(uno_python), '-c', 'import uno'], capture_output=True).returncode:
            if os.environ.get('REQUIRE_FORMULA_ENGINE') == '1':
                self.fail('Native pivot engine required')
            self.skipTest('Native pivot verification runs in Linux job')
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / 'multi.xlsx'
            rows = example_rows()
            ExcelOutputAdapter().write(path, rows, [], [], [], IssueLog(), load_config(CONFIG), ['2026-08', '2026-09'])
            plan = [[], [['RPD地区收入汇总-2026-08', 'C4', '2026-10']]]
            (root / 'plan.json').write_text(json.dumps(plan), encoding='utf-8')
            result = subprocess.run([str(uno_python), str(Path(__file__).parent / 'support/verify_native_pivot.py'),
                office, str(path), str(root / 'plan.json'), str(root / 'result.json')], capture_output=True, text=True, timeout=150)
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            snapshots = json.loads((root / 'result.json').read_text())
            for snapshot in snapshots:
                self.assertEqual(4, len(snapshot))
                for title, actual in snapshot.items():
                    summary = build_regional_summary(rows, actual['month'], title[:3].lower())
                    for region in [*summary.regions, '小计']:
                        for label in summary.labels:
                            entries = [e for e in summary.entries if e.bucket == label and (region == '小计' or e.region == region)]
                            cell = actual['cells'][region][label]
                            self.assertEqual(sorted(rows[e.base_row - 2].values['contract_no'] for e in entries), sorted(cell['contracts']))
                            self.assertEqual(float(sum((e.amount for e in entries), Decimal(0))), cell['value'])
            for title in ('CPD地区收入汇总-2026-08', 'RPD地区收入汇总-2026-09', 'CPD地区收入汇总-2026-09'):
                self.assertEqual(snapshots[0][title], snapshots[1][title])
