"""Reproduce the real openpyxl grouped-cache failure through XLSX loading."""
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from zipfile import ZipFile, ZIP_DEFLATED
from xml.etree import ElementTree as ET

from openpyxl import load_workbook
from revenue_tool.adapters.excel_reader import ExcelInputAdapter, _open_workbook
from revenue_tool.adapters.pivot_smoke_fixture import add_pivot_fixture
from revenue_tool.config import load_config
from revenue_tool.domain.models import IssueLog, WorkbookReadError
from tests.test_pipeline import CONFIG, _run, _write_sources, _base_rows
from tests.test_manual_revenue_forecast import _set_manual_inputs

NS = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'


def rewrite_package(path, transform):
    with ZipFile(path) as archive:
        parts = [(info, transform(info.filename, archive.read(info.filename))) for info in archive.infolist()]
    with ZipFile(path, 'w', ZIP_DEFLATED) as archive:
        for info, data in parts:
            archive.writestr(info, data)


def add_discrete_group(path):
    def transform(name, data):
        if name.startswith('xl/pivotCache/pivotCacheDefinition') and name.endswith('.xml'):
            root = ET.fromstring(data)
            field = root.find(f'{{{NS}}}cacheFields')[0]
            group = ET.SubElement(field, f'{{{NS}}}fieldGroup', {'base': '0'})
            discrete = ET.SubElement(group, f'{{{NS}}}discretePr', {'count': '1'})
            ET.SubElement(discrete, f'{{{NS}}}x', {'v': '0'})
            return ET.tostring(root)
        return data
    rewrite_package(path, transform)


class GroupedPivotInputTest(unittest.TestCase):
    def test_previous_grouped_cache_inherits_inputs_without_touching_original(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            sources = _write_sources(root, 'sources', variant='first')
            previous, output = root / 'previous.xlsx', root / 'next.xlsx'
            _run(sources, previous)
            _set_manual_inputs(previous, 'C001', 'SC-A', segment_flag=False, rpd='2026-9', cpd='2026-10', amount=0)
            workbook = load_workbook(previous)
            try:
                add_pivot_fixture(workbook, workbook['基表'])
                workbook.save(previous)
            finally:
                workbook.close()
            add_discrete_group(previous)
            # This exact package triggers the reported exception in the old reader.
            with self.assertRaisesRegex(TypeError, "Nested.from_tree.*node"):
                load_workbook(previous, data_only=True)
            before = sha256(previous.read_bytes()).digest()
            result = _run(sources, output, previous=previous)
            self.assertEqual(7, result.base_count)
            self.assertEqual(before, sha256(previous.read_bytes()).digest())
            wb = load_workbook(output, data_only=True)
            try:
                row = _base_rows(wb['基表'])[('C001', 'SC-A')]
                self.assertIs(False, row['最终收入分段类别'])
                self.assertEqual(0, row['调整金额'])
                self.assertEqual(0, row['最终收入预测'])
                self.assertEqual('2026-09', row['最终收入年月（按RPD）'])
                self.assertEqual('2026-10', row['最终收入年月（按CPD）'])
            finally:
                wb.close()

    def test_source_with_grouped_pivot_still_reads_business_cells(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            sources = _write_sources(root, 'sources', variant='first')
            source_path = sources[3]
            source = load_workbook(source_path)
            try:
                add_pivot_fixture(
                    source,
                    source.active,
                    location_ref='AS6:AT20',
                    name='SourceUserPivot',
                )
                source.save(source_path)
            finally:
                source.close()
            add_discrete_group(source_path)
            with self.assertRaisesRegex(TypeError, "Nested.from_tree.*node"):
                load_workbook(source_path, data_only=True)
            before = source_path.read_bytes()
            result = _run(sources, root / 'result.xlsx')
            self.assertEqual(7, result.base_count)
            self.assertEqual(before, source_path.read_bytes())

    def test_read_only_preserves_cell_types_formats_and_corrects_missing_dimensions(self):
        from datetime import datetime
        from openpyxl import Workbook
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / 'cells.xlsx'
            wb = Workbook()
            wb.active.append(['ID', 'Date', 'Boolean', 'Amount'])
            wb.active.append([12, datetime(2026, 9, 7), False, 0])
            wb.active['A2'].number_format = '00000'
            wb.active['B2'].number_format = 'yyyy-mm-dd'
            wb.save(path)
            wb.close()
            def omit_dimension(name, data):
                if name == 'xl/worksheets/sheet1.xml':
                    import re
                    return re.sub(rb'<dimension[^>]*/>', b'<dimension ref="A1:A1"/>', data)
                return data
            rewrite_package(path, omit_dimension)
            read = _open_workbook(path)
            try:
                self.assertEqual(2, read.active.max_row)
                self.assertEqual('00000', read.active['A2'].number_format)
                self.assertEqual(datetime(2026, 9, 7), read.active['B2'].value)
                self.assertIs(False, read.active['C2'].value)
                self.assertEqual(0, read.active['D2'].value)
            finally:
                read.close()

    def test_corrupt_package_still_reports_unreadable_instead_of_silent_empty_data(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / 'broken.xlsx'
            path.write_bytes(b'not a zip file')
            with self.assertRaisesRegex(WorkbookReadError, '工作簿无法读取'):
                _open_workbook(path)
