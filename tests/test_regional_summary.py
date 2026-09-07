from __future__ import annotations

from copy import deepcopy
from decimal import Decimal
import json
import os
from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory
import unittest
from zipfile import ZipFile

from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

from revenue_tool.adapters.excel_writer import ExcelOutputAdapter
from revenue_tool.adapters.regional_pivot import SOURCE_SHEETS, SUMMARY_SHEETS
from revenue_tool.config import load_config
from revenue_tool.domain.models import BaseRow, IssueLog
from revenue_tool.services.final_revenue import calculate_final_values
from revenue_tool.services.regional_summary import (
    build_regional_summary, EMPTY_REGION, EXCLUDED, report_month,
)
from tests.test_pipeline import CONFIG


def example_rows():
    # Every current segment and excluded-period condition; literal independent oracle.
    data = [
        ("A1", "A", "2026-08", "2026-09", "订未发", 100),
        ("A2", "A", "2026-09", "2026-08", "订未发", 20),
        ("A3", "A", "2026-09", "2026-09", "发未收", -5),
        ("A4", "A", "2026-09", "2026-09", "交未验", 0),
        ("A5", "A", "2026-09", "2026-09", "特殊处理", 7),
        ("OLD", "A", "2025-09", "2025-09", "订未发", 900),
        ("FUT", "A", "2026-10", "2026-10", "订未发", 800),
        ("NONE", "A", None, None, "订未发", 700),
        ("B1", "B", "2026-01", "2026-09", "发未收", 50),
        ("B2", "B", "2026-09", "2026-09", False, 3),
        ("EMPTY", None, "2026-09", "2026-09", "订未发", 4),
    ]
    result = []
    for contract, region, rpd, cpd, segment, amount in data:
        values = dict(contract_no=contract, supply_center="深供", region=region,
            revenue_month_rpd=rpd, revenue_month_cpd=cpd,
            revenue_segment=segment, revenue_forecast=Decimal(amount))
        values.update(calculate_final_values(values))
        result.append(BaseRow(values))
    return result


class RegionalSummaryTest(unittest.TestCase):
    def test_literal_totals_and_every_cell_detail_membership(self):
        rows = example_rows()
        rpd = build_regional_summary(rows, "2026-09", "rpd")
        cpd = build_regional_summary(rows, "2026-09", "cpd")
        self.assertEqual([100, 20, -5, 0, 7, 22], rpd.totals["A"])
        self.assertEqual([20, 100, -5, 0, 7, 102], cpd.totals["A"])
        self.assertEqual([50, 0, 0, 0, 3, 3], rpd.totals["B"])
        self.assertEqual([0, 0, 50, 0, 3, 53], cpd.totals["B"])
        self.assertEqual([0, 4, 0, 0, 0, 4], rpd.totals[EMPTY_REGION])
        self.assertEqual(3, rpd.excluded_count)
        for summary in (rpd, cpd):
            for region in [*summary.regions, None]:
                for i, label in enumerate(summary.labels):
                    detail = [e for e in summary.entries if e.bucket == label and (region is None or e.region == region)]
                    self.assertEqual(len(detail), len({e.base_row for e in detail}))
                    expected = summary.totals[region][i] if region else sum(v[i] for v in summary.totals.values())
                    self.assertEqual(expected, sum((e.amount for e in detail), Decimal(0)))
            subtotal = {rows[e.base_row - 2].values["contract_no"] for e in summary.entries if e.bucket == summary.labels[-1]}
            self.assertEqual({"A2", "A3", "A4", "A5", "B2", "EMPTY"} if summary.mode == "rpd" else
                             {"A1", "A3", "A4", "A5", "B1", "B2", "EMPTY"}, subtotal)

    def test_january_december_empty_invalid_and_manual_priority(self):
        rows = example_rows()
        for mode in ("rpd", "cpd"):
            january = build_regional_summary(rows, "2026-01", mode)
            self.assertEqual(0, sum(v[0] for v in january.totals.values()))
            december = build_regional_summary(rows, "2026-12", mode)
            self.assertEqual(979, sum(v[0] for v in december.totals.values()))
            self.assertEqual(0, sum(v[-1] for v in december.totals.values()))
        self.assertEqual({}, build_regional_summary([], "2026-09", "rpd").totals)
        for value in ("2026-9", "0000-01", "2026-13", "", False):
            with self.assertRaises(ValueError):
                report_month(value)
        rows[0].values.update(manual_revenue_forecast_rpd="9月", manual_revenue_month=0,
                              manual_revenue_segment=False, manual_adjust_flag="N")
        rows[0].values.update(calculate_final_values(rows[0].values))
        actual = build_regional_summary(rows, "2026-09", "rpd")
        self.assertEqual([0, 20, -5, 0, 7, 22], actual.totals["A"])
        rows[0].values["final_revenue_forecast"] = "待修正：请填写有效金额"
        self.assertEqual(4, build_regional_summary(rows, "2026-09", "rpd").excluded_count)

    def test_native_pivot_cache_and_saved_numeric_view(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "summary.xlsx"
            rows = example_rows()
            config = load_config(CONFIG)
            ExcelOutputAdapter().write(path, rows, [], [], [], IssueLog(), config, "2026-09")
            for _ in range(2):
                wb = load_workbook(path)
                try:
                    for mode in ("rpd", "cpd"):
                        sheet = wb[SUMMARY_SHEETS[mode]]
                        self.assertEqual("小计", sheet["A11"].value)
                        self.assertEqual(29 if mode == "rpd" else 159, sheet["G11"].value)
                        self.assertEqual("9月小计", sheet["G7"].value)
                        self.assertEqual("#,##0.00", sheet["G11"].number_format)
                        self.assertFalse(sheet.protection.sheet)
                        self.assertEqual(1, len(sheet._pivots))
                        p = sheet._pivots[0]
                        self.assertTrue(p.enableDrill)
                        self.assertTrue(p.rowGrandTotals)
                        self.assertFalse(p.colGrandTotals)
                        self.assertEqual("小计", p.grandTotalCaption)
                        self.assertEqual("sum", p.dataFields[0].subtotal)
                        self.assertTrue(p.cache.saveData)
                        self.assertFalse(p.cache.refreshOnLoad)
                        self.assertEqual(4 * len(rows), len(p.cache.records.r))
                        self.assertEqual(SOURCE_SHEETS[mode], p.cache.cacheSource.worksheetSource.sheet)
                        source = wb[SOURCE_SHEETS[mode]]
                        self.assertEqual("hidden", source.sheet_state)
                        self.assertEqual(44, source.max_column)
                        self.assertEqual("f", source["AP2"].data_type)
                        self.assertEqual("f", source["AJ2"].data_type)
                        region_values = [s.v for s in p.cache.cacheFields[40].sharedItems._fields]
                        buckets = [s.v for s in p.cache.cacheFields[41].sharedItems._fields]
                        for col, bucket in enumerate(buckets[:6], 2):
                            for region_index, region in enumerate(region_values):
                                matching = [r._fields for r in p.cache.records.r
                                    if r._fields[40].v == region_index and buckets[r._fields[41].v] == bucket
                                    and r._fields[43].v == (0 if mode == "rpd" else 1)]
                                self.assertEqual(len(matching), len({r[42].v for r in matching}))
                                amount_index = [c["id"] for c in config.base_columns].index("final_revenue_forecast")
                                self.assertEqual(sheet.cell(8 + region_index, col).value,
                                                 sum(r[amount_index].v for r in matching))
                    wb.save(path)
                finally:
                    wb.close()
            with ZipFile(path) as z:
                self.assertEqual(2, len([n for n in z.namelist() if n.startswith("xl/pivotTables/pivotTable") and n.endswith(".xml")]))

    def test_empty_workbook_has_two_valid_pivots_and_zero_subtotals(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "empty.xlsx"
            ExcelOutputAdapter().write(path, [], [], [], [], IssueLog(), load_config(CONFIG), "2026-01")
            wb = load_workbook(path)
            try:
                for title in SUMMARY_SHEETS.values():
                    sheet = wb[title]
                    self.assertEqual("小计", sheet["A8"].value)
                    self.assertEqual([0] * 6, [c.value for c in sheet[8]][1:])
                    self.assertEqual(0, len(sheet._pivots[0].cache.records.r))
            finally:
                wb.close()

    def test_real_engine_refresh_and_native_drill_through(self):
        office = shutil.which("libreoffice") or shutil.which("soffice")
        uno_python = Path("/usr/bin/python3")
        available = bool(office and uno_python.exists() and subprocess.run(
            [str(uno_python), "-c", "import uno"], capture_output=True).returncode == 0)
        if not available:
            if os.environ.get("REQUIRE_FORMULA_ENGINE") == "1":
                self.fail("LibreOffice and python3-uno are required for native pivot verification")
            self.skipTest("Native pivot engine runs in the mandatory Linux job")
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            rows = example_rows()
            config = load_config(CONFIG)
            source = root / "summary.xlsx"
            ExcelOutputAdapter().write(source, rows, [], [], [], IssueLog(), config, "2026-09")
            ids = [c["id"] for c in config.base_columns]
            def edit(field, value):
                return ["基表", f"{get_column_letter(ids.index(field) + 1)}2", value]
            plan = [[], [edit("manual_revenue_forecast_rpd", "9月"),
                         edit("manual_revenue_forecast_cpd", "8月"),
                         edit("manual_revenue_segment", "特殊处理"), edit("manual_revenue_month", -10)],
                    [edit(field, None) for field in ("manual_revenue_forecast_rpd", "manual_revenue_forecast_cpd", "manual_revenue_segment", "manual_revenue_month")]]
            (root / "plan.json").write_text(json.dumps(plan), encoding="utf-8")
            command = [str(uno_python), str(Path(__file__).parent / "support" / "verify_native_pivot.py"),
                       office, str(source), str(root / "plan.json"), str(root / "result.json")]
            result = subprocess.run(command, text=True, capture_output=True, timeout=150)
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            snapshots = json.loads((root / "result.json").read_text())
            for stage, snapshot in enumerate(snapshots):
                current_rows = deepcopy(rows)
                if stage == 1:
                    current_rows[0].values.update(manual_revenue_forecast_rpd="9月",
                        manual_revenue_forecast_cpd="8月", manual_revenue_segment="特殊处理", manual_revenue_month=-10)
                    current_rows[0].values.update(calculate_final_values(current_rows[0].values))
                for mode, title in SUMMARY_SHEETS.items():
                    summary = build_regional_summary(current_rows, "2026-09", mode)
                    actual = snapshot[title]
                    self.assertEqual(["地区部", *summary.labels], actual["headers"], (stage, mode, actual))
                    for region in [*summary.regions, "小计"]:
                        for label in summary.labels:
                            cell = actual["cells"][region][label]
                            matching = [e for e in summary.entries if e.bucket == label and (region == "小计" or e.region == region)]
                            expected_ids = sorted(current_rows[e.base_row - 2].values["contract_no"] for e in matching)
                            self.assertEqual(expected_ids, sorted(cell["contracts"]), (stage, mode, region, label, cell))
                            self.assertEqual(float(sum((e.amount for e in matching), Decimal(0))), cell["value"],
                                             (stage, mode, region, label, cell))
