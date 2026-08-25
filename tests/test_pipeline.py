from datetime import date
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from openpyxl import Workbook, load_workbook

from revenue_tool.application.pipeline import run_pipeline


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "default.json"


class PipelineTest(unittest.TestCase):
    def test_first_run_matches_documented_grain_and_rules(self) -> None:
        with TemporaryDirectory() as temporary:
            directory = Path(temporary)
            source = directory / "source.xlsx"
            output = directory / "result.xlsx"
            _write_source(source, variant="first", include_monthly=True)

            result = run_pipeline(source, output, CONFIG)

            self.assertEqual(6, result.base_count)
            workbook = load_workbook(output, data_only=True)
            try:
                self.assertEqual(
                    [
                        "基表",
                        "RPD跨月变化",
                        "CPD跨月变化",
                        "异常清单",
                        "_tool_meta",
                    ],
                    workbook.sheetnames,
                )
                self.assertEqual(
                    "hidden", workbook["_tool_meta"].sheet_state
                )
                base = workbook["基表"]
                headers = [cell.value for cell in base[1]]
                self.assertEqual(EXPECTED_BASE_HEADERS, headers)
                self.assertEqual("A2", base.freeze_panes)
                self.assertTrue(base.tables)

                rows = _base_rows(base)
                sc_a = rows[("C001", "SC-A")]
                self.assertEqual(100, sc_a["遗留量"])
                self.assertEqual(50, sc_a["当月新订货"])
                self.assertEqual("BG-L", sc_a["BG"])
                self.assertEqual("交付类", sc_a["结转类型"])
                self.assertEqual("Y", sc_a["多个供应中心发货"])
                self.assertEqual("Y|N", sc_a["是否解锁备货"])
                self.assertEqual("Y", sc_a["分批发货"])
                self.assertEqual(30, sc_a["海运周期"])
                self.assertEqual(date(2026, 1, 5), _as_date(sc_a["RPD"]))
                self.assertEqual(date(2026, 2, 1), _as_date(sc_a["CPD"]))
                self.assertEqual("Y", sc_a["多次要货"])
                self.assertEqual("Y", sc_a["分批供应"])
                self.assertEqual(
                    date(2026, 2, 4),
                    _as_date(sc_a["到货日期（按RPD）"]),
                )
                self.assertEqual(
                    date(2026, 3, 3),
                    _as_date(sc_a["到货日期（按CPD）"]),
                )
                self.assertEqual("2026-02", sc_a["收入年月（按RPD）"])
                self.assertEqual("2026-03", sc_a["收入年月（按CPD）"])
                self.assertEqual("需判断", sc_a["收入分段类别"])

                sc_b = rows[("C001", "SC-B")]
                self.assertEqual(5, sc_b["海运周期"])
                self.assertEqual(
                    date(2026, 3, 10),
                    _as_date(sc_b["到货日期（按RPD）"]),
                )
                self.assertEqual(
                    date(2026, 3, 10),
                    _as_date(sc_b["到货日期（按CPD）"]),
                )
                self.assertEqual("发未收", sc_b["收入分段类别"])

                c004 = rows[("C004", "SC-D")]
                self.assertEqual(70, c004["当月新订货"])
                self.assertEqual("BG-M", c004["BG"])
                self.assertEqual("订未发", c004["收入分段类别"])
                self.assertIsNone(c004["收入年月（按CPD）"])

                c007_x = rows[("C007", "SC-X")]
                c007_y = rows[("C007", "SC-Y")]
                self.assertEqual("地区7A", c007_x["地区部"])
                self.assertEqual("地区7A", c007_y["地区部"])
                self.assertEqual("中国", c007_x["国家"])
                self.assertEqual("中国", c007_y["国家"])

                self.assertEqual(1, workbook["RPD跨月变化"].max_row)
                self.assertEqual(1, workbook["CPD跨月变化"].max_row)

                issue_codes = {
                    row[0].value
                    for row in workbook["异常清单"].iter_rows(min_row=2)
                }
                self.assertIn("DUPLICATE_ROW_IGNORED", issue_codes)
                self.assertIn("CONFLICTING_CONTRACT_VALUE", issue_codes)
                self.assertIn("CONFLICTING_TRANSIT_DAYS", issue_codes)
                self.assertIn(
                    "CONFLICTING_COUNTRY_FOR_CONTRACT", issue_codes
                )
                self.assertIn("CONTRACT_WITHOUT_SUPPLY_CENTER", issue_codes)
                self.assertIn("ARRIVAL_CPD_UNAVAILABLE", issue_codes)
                self.assertIn("CONTROL_FLAG_MISMATCH", issue_codes)

                issue_rows = list(
                    workbook["异常清单"].iter_rows(
                        min_row=2, values_only=True
                    )
                )
                transit_conflict = next(
                    row
                    for row in issue_rows
                    if row[0] == "CONFLICTING_TRANSIT_DAYS"
                )
                self.assertIn("国家运输周期!3=30", transit_conflict[7])
                self.assertIn("国家运输周期!5=40", transit_conflict[7])
            finally:
                workbook.close()

    def test_previous_manual_fields_and_two_change_sheets(self) -> None:
        with TemporaryDirectory() as temporary:
            directory = Path(temporary)
            first_source = directory / "first-source.xlsx"
            second_source = directory / "second-source.xlsx"
            first_result = directory / "first-result.xlsx"
            second_result = directory / "second-result.xlsx"
            _write_source(first_source, variant="first", include_monthly=True)
            _write_source(second_source, variant="second", include_monthly=True)
            run_pipeline(first_source, first_result, CONFIG)
            _set_manual_values(first_result, "C001", "SC-A")

            result = run_pipeline(
                second_source,
                second_result,
                CONFIG,
                previous_path=first_result,
            )

            self.assertGreaterEqual(result.rpd_change_count, 3)
            self.assertGreaterEqual(result.cpd_change_count, 3)
            workbook = load_workbook(second_result, data_only=True)
            try:
                base_rows = _base_rows(workbook["基表"])
                inherited = base_rows[("C001", "SC-A")]
                self.assertEqual("Y", inherited["是否手工调整收入月份"])
                self.assertEqual("2026-04", inherited["手工调整收入月份"])
                self.assertEqual("业务确认", inherited["调整备注"])
                self.assertIsNone(
                    base_rows[("C005", "SC-E")]["是否手工调整收入月份"]
                )

                rpd = _change_rows(workbook["RPD跨月变化"])
                self.assertEqual("延后", rpd[("C001", "SC-A")]["变化方向"])
                self.assertEqual(1, rpd[("C001", "SC-A")]["变化月数"])
                self.assertEqual("取消", rpd[("C003", "SC-C")]["变化方向"])
                self.assertEqual("新增", rpd[("C005", "SC-E")]["变化方向"])

                cpd = _change_rows(workbook["CPD跨月变化"])
                self.assertEqual("提前", cpd[("C001", "SC-A")]["变化方向"])
                self.assertEqual(1, cpd[("C001", "SC-A")]["变化月数"])
                self.assertEqual("取消", cpd[("C003", "SC-C")]["变化方向"])
                self.assertEqual("新增", cpd[("C005", "SC-E")]["变化方向"])
            finally:
                workbook.close()

    def test_optional_monthly_sheet_is_not_an_error_or_zero(self) -> None:
        with TemporaryDirectory() as temporary:
            directory = Path(temporary)
            source = directory / "source.xlsx"
            output = directory / "result.xlsx"
            _write_source(source, variant="first", include_monthly=False)

            run_pipeline(source, output, CONFIG)

            workbook = load_workbook(output, data_only=True)
            try:
                rows = _base_rows(workbook["基表"])
                self.assertIsNone(rows[("C001", "SC-A")]["当月新订货"])
                issue_rows = list(
                    workbook["异常清单"].iter_rows(
                        min_row=2, values_only=True
                    )
                )
                monthly_missing = [
                    row
                    for row in issue_rows
                    if row[0] == "MISSING_SHEET"
                    and row[6] == "monthly_order"
                ]
                self.assertEqual([], monthly_missing)
            finally:
                workbook.close()

    def test_previous_metadata_survives_output_display_name_changes(self) -> None:
        with TemporaryDirectory() as temporary:
            directory = Path(temporary)
            first_source = directory / "first-source.xlsx"
            second_source = directory / "second-source.xlsx"
            first_result = directory / "first-result.xlsx"
            second_result = directory / "second-result.xlsx"
            changed_config = directory / "changed-config.json"
            _write_source(first_source, variant="first", include_monthly=True)
            _write_source(second_source, variant="second", include_monthly=True)
            run_pipeline(first_source, first_result, CONFIG)
            _set_manual_values(first_result, "C001", "SC-A")

            config_data = json.loads(CONFIG.read_text(encoding="utf-8"))
            config_data["output"]["sheets"]["base"] = "主数据"
            for column in config_data["output"]["base_columns"]:
                column["name"] = f"新-{column['id']}"
            changed_config.write_text(
                json.dumps(config_data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            run_pipeline(
                second_source,
                second_result,
                changed_config,
                previous_path=first_result,
            )

            workbook = load_workbook(second_result, data_only=True)
            try:
                sheet = workbook["主数据"]
                headers = {cell.value: cell.column for cell in sheet[1]}
                matching = [
                    row
                    for row in range(2, sheet.max_row + 1)
                    if sheet.cell(row, headers["新-contract_no"]).value
                    == "C001"
                    and sheet.cell(
                        row, headers["新-supply_center"]
                    ).value
                    == "SC-A"
                ]
                self.assertEqual(1, len(matching))
                row = matching[0]
                self.assertEqual(
                    "Y",
                    sheet.cell(
                        row, headers["新-manual_adjust_flag"]
                    ).value,
                )
                self.assertEqual(
                    "2026-04",
                    sheet.cell(
                        row, headers["新-manual_revenue_month"]
                    ).value,
                )
                self.assertEqual(
                    "业务确认",
                    sheet.cell(
                        row, headers["新-adjustment_note"]
                    ).value,
                )
            finally:
                workbook.close()

    def test_unusable_previous_does_not_create_false_new_changes(self) -> None:
        with TemporaryDirectory() as temporary:
            directory = Path(temporary)
            source = directory / "source.xlsx"
            previous = directory / "wrong-previous.xlsx"
            output = directory / "result.xlsx"
            _write_source(source, variant="first", include_monthly=True)
            wrong = Workbook()
            wrong.active.title = "错误页"
            wrong.active.append(["错误文件"])
            wrong.save(previous)
            wrong.close()

            run_pipeline(
                source, output, CONFIG, previous_path=previous
            )

            workbook = load_workbook(output, data_only=True)
            try:
                self.assertEqual(1, workbook["RPD跨月变化"].max_row)
                self.assertEqual(1, workbook["CPD跨月变化"].max_row)
                codes = {
                    row[0].value
                    for row in workbook["异常清单"].iter_rows(min_row=2)
                }
                self.assertIn(
                    "PREVIOUS_BASE_SHEET_UNAVAILABLE", codes
                )
            finally:
                workbook.close()

    def test_supply_center_representation_drift_keeps_stable_key(self) -> None:
        with TemporaryDirectory() as temporary:
            directory = Path(temporary)
            first_source = directory / "first-source.xlsx"
            second_source = directory / "second-source.xlsx"
            first_result = directory / "first-result.xlsx"
            second_result = directory / "second-result.xlsx"
            _write_source(first_source, variant="first", include_monthly=True)
            _write_source(second_source, variant="first", include_monthly=True)
            _replace_supply_center(
                second_source,
                contract="C001",
                old_center="SC-A",
                new_center="　ｓｃ－ａ　",
            )
            run_pipeline(first_source, first_result, CONFIG)
            _set_manual_values(first_result, "C001", "SC-A")

            run_pipeline(
                second_source,
                second_result,
                CONFIG,
                previous_path=first_result,
            )

            workbook = load_workbook(second_result, data_only=True)
            try:
                rows = _base_rows(workbook["基表"])
                inherited = rows[("C001", "sc-a")]
                self.assertEqual("Y", inherited["是否手工调整收入月份"])
                self.assertEqual("2026-04", inherited["手工调整收入月份"])
                self.assertEqual("业务确认", inherited["调整备注"])
                self.assertEqual(1, workbook["RPD跨月变化"].max_row)
                self.assertEqual(1, workbook["CPD跨月变化"].max_row)
            finally:
                workbook.close()

    def test_output_cannot_overwrite_input_or_previous(self) -> None:
        with TemporaryDirectory() as temporary:
            directory = Path(temporary)
            source = directory / "source.xlsx"
            previous = directory / "previous.xlsx"
            output = directory / "result.xlsx"
            _write_source(source, variant="first", include_monthly=True)
            _write_source(previous, variant="first", include_monthly=True)

            with self.assertRaisesRegex(ValueError, "本次输入"):
                run_pipeline(source, source, CONFIG)
            with self.assertRaisesRegex(ValueError, "上一次成功运行结果"):
                run_pipeline(
                    source,
                    previous,
                    CONFIG,
                    previous_path=previous,
                )

            self.assertFalse(output.exists())


EXPECTED_BASE_HEADERS = [
    "合同号",
    "遗留量",
    "当月新订货",
    "BG",
    "地区部",
    "国家",
    "结转类型",
    "客户群",
    "项目名称",
    "贸易术语",
    "履行供应中心",
    "多个供应中心发货",
    "是否解锁备货",
    "分批发货",
    "海运周期",
    "ATA",
    "ASD",
    "RPD",
    "多次要货",
    "CPD",
    "分批供应",
    "到货日期（按RPD）",
    "到货日期（按CPD）",
    "收入年月（按RPD）",
    "收入年月（按CPD）",
    "收入分段类别",
    "是否手工调整收入月份",
    "手工调整收入月份",
    "调整备注",
]


def _write_source(
    path: Path, *, variant: str, include_monthly: bool
) -> None:
    workbook = Workbook()
    legacy = workbook.active
    legacy.title = "遗留量"
    _add_header(
        legacy,
        [
            "华为合同号",
            "地区部中文名称",
            "国家中文名称",
            "客户群中文名称",
            "交付项目中文名称",
            "行销产品维BG中文名称",
            "设备订未收-新",
        ],
    )
    legacy_rows = [
        ["C001", "地区L", "阿拉伯联合酋长国", "客户L", "项目L", "BG-L", 100],
        ["C001", "地区L", "阿拉伯联合酋长国", "客户L", "项目L", "BG-L", 100],
        ["C001", "地区L", "巴西", "客户L", "项目L", "BG-L", 999],
        ["C002", "地区2", "中国", "客户2", "项目2", "BG-2", 200],
        ["C003", "地区3", "日本", "客户3", "项目3", "BG-3", 300],
    ]
    for row in legacy_rows:
        legacy.append(row)

    if include_monthly:
        monthly = workbook.create_sheet("当月订货")
        _add_header(
            monthly,
            [
                "华为合同号",
                "地区部中文名称",
                "国家中文名称",
                "交付项目中文名称",
                "行销产品维BG中文名称",
                "设备订货（不含VAT）",
            ],
        )
        monthly.append(["C001", "地区M", "中国", "项目M", "BG-M1", 50])
        monthly.append(["C004", "地区M4", "巴西", "项目M4", "BG-M", 70])

    demand = workbook.create_sheet("要货明细")
    _add_header(
        demand,
        [
            "原合同号",
            "地区部",
            "国家中文名称",
            "签约客户群",
            "交付项目中文名称",
            "需求状态",
            "供应中心简称",
            "贸易术语",
            "备货总控标识",
            "发货总控标识",
            "天_ATA",
            "ASD日期",
            "RPD日期",
            "CPD日期",
            "BG_CN",
        ],
    )
    if variant == "first":
        sc_a_1 = [
            "C001", "地区D", "阿拉伯联合酋长国", "客户D", "项目D",
            "有效", "SC-A", "CIF", "Y", "Y", None, None,
            date(2026, 1, 10), date(2026, 1, 20), "BG-D",
        ]
        sc_a_2 = [
            "C001", "地区D", "阿拉伯联合酋长国", "客户D", "项目D",
            "有效", "SC-A", "CIF", "N", "N", None, None,
            date(2026, 1, 5), date(2026, 2, 1), "BG-D",
        ]
        demand.append(sc_a_1)
        demand.append(sc_a_1)
        demand.append(sc_a_2)
        demand.append([
            "C001", "地区D", "阿拉伯联合酋长国", "客户D", "项目D",
            "有效", "SC-B", "fob", "Y", "Y", date(2026, 3, 10),
            None, date(2026, 2, 1), date(2026, 2, 10), "BG-D",
        ])
        demand.append([
            "C003", "地区3D", "日本", "客户3D", "项目3D", "有效",
            "SC-C", "CIF", "Y", "Y", None, date(2026, 4, 15),
            date(2026, 3, 1), date(2026, 3, 5), "BG-3D",
        ])
    else:
        demand.append([
            "C001", "地区D", "阿拉伯联合酋长国", "客户D", "项目D",
            "有效", "SC-A", "CIF", "Y", "Y", None, None,
            date(2026, 2, 10), date(2026, 1, 1), "BG-D",
        ])
        demand.append([
            "C001", "地区D", "阿拉伯联合酋长国", "客户D", "项目D",
            "有效", "SC-A", "CIF", "N", "N", None, None,
            date(2026, 2, 5), date(2026, 1, 15), "BG-D",
        ])
        demand.append([
            "C001", "地区D", "阿拉伯联合酋长国", "客户D", "项目D",
            "有效", "SC-B", "FOB", "Y", "Y", date(2026, 3, 10),
            None, date(2026, 2, 1), date(2026, 2, 10), "BG-D",
        ])
        demand.append([
            "C005", "地区5", "新加坡", "客户5", "项目5", "有效",
            "SC-E", "EXW", "Y", "Y", None, None,
            date(2026, 6, 1), date(2026, 6, 5), "BG-5",
        ])
    demand.append([
        "C004", "地区4", "巴西", "客户4", "项目4", "有效",
        "SC-D", "EXW", "Y", "Y", None, None,
        date(2026, 5, 1), None, "BG-4",
    ])
    demand.append([
        "C007", "地区7A", "中国", "客户7A", "项目7A", "有效",
        "SC-X", "EXW", "Y", "Y", None, None,
        date(2026, 7, 1), date(2026, 7, 2), "BG-7A",
    ])
    demand.append([
        "C007", "地区7B", "巴西", "客户7B", "项目7B", "有效",
        "SC-Y", "EXW", "Y", "N", None, None,
        date(2026, 7, 1), date(2026, 7, 2), "BG-7B",
    ])

    transit = workbook.create_sheet("国家运输周期")
    _add_header(transit, ["国家", "供应中心", "运输周期"])
    transit.append(["阿拉伯联合酋长国", "SC-A", 30])
    transit.append(["阿拉伯联合酋长国", "SC-A", 30])
    transit.append(["阿拉伯联合酋长国", "SC-A", 40])
    transit.append(["日本", "SC-C", 20])
    workbook.save(path)
    workbook.close()


def _add_header(sheet, headers: list[str]) -> None:
    sheet.append(["业务数据"])
    sheet.append(headers)


def _base_rows(sheet) -> dict[tuple[str, str], dict[str, object]]:
    headers = [cell.value for cell in sheet[1]]
    rows = {}
    for values in sheet.iter_rows(min_row=2, values_only=True):
        data = dict(zip(headers, values))
        rows[(data["合同号"], data["履行供应中心"])] = data
    return rows


def _change_rows(sheet) -> dict[tuple[str, str], dict[str, object]]:
    headers = [cell.value for cell in sheet[1]]
    result = {}
    for values in sheet.iter_rows(min_row=2, values_only=True):
        data = dict(zip(headers, values))
        result[(data["合同号"], data["履行供应中心"])] = data
    return result


def _set_manual_values(path: Path, contract: str, center: str) -> None:
    workbook = load_workbook(path)
    try:
        sheet = workbook["基表"]
        headers = {cell.value: cell.column for cell in sheet[1]}
        for row_number in range(2, sheet.max_row + 1):
            if (
                sheet.cell(row_number, headers["合同号"]).value == contract
                and sheet.cell(row_number, headers["履行供应中心"]).value
                == center
            ):
                sheet.cell(
                    row_number,
                    headers["是否手工调整收入月份"],
                    "Y",
                )
                sheet.cell(
                    row_number,
                    headers["手工调整收入月份"],
                    "2026-04",
                )
                sheet.cell(
                    row_number,
                    headers["调整备注"],
                    "业务确认",
                )
                break
        workbook.save(path)
    finally:
        workbook.close()


def _replace_supply_center(
    path: Path,
    *,
    contract: str,
    old_center: str,
    new_center: str,
) -> None:
    workbook = load_workbook(path)
    try:
        sheet = workbook["要货明细"]
        headers = {cell.value: cell.column for cell in sheet[2]}
        for row_number in range(3, sheet.max_row + 1):
            if (
                sheet.cell(row_number, headers["原合同号"]).value == contract
                and sheet.cell(
                    row_number, headers["供应中心简称"]
                ).value
                == old_center
            ):
                sheet.cell(
                    row_number, headers["供应中心简称"], new_center
                )
        workbook.save(path)
    finally:
        workbook.close()


def _as_date(value):
    return value.date() if hasattr(value, "date") else value


if __name__ == "__main__":
    unittest.main()
