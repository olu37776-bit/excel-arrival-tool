"""Native OOXML pivots with saved caches and formula-backed drill-through sources.

One pivot column = one bucket. Current rows also have a subtotal bucket copy;
cross-column grand totals are disabled, so they cannot accidentally sum both copies.
Never use six conditional measures: their Show Details would include unrelated
months/segments from the entire region. Source sheets are not business facts.
"""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from openpyxl.pivot.cache import CacheDefinition, CacheField, CacheSource, SharedItems, WorksheetSource
from openpyxl.pivot.fields import Boolean, Index, Missing, Number, Text
from openpyxl.pivot.record import Record, RecordList
from openpyxl.pivot.table import (
    DataField, FieldItem, Location, PivotField, RowColField, RowColItem,
    TableDefinition, PivotTableStyle, PageField,
)
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter, quote_sheetname
from openpyxl.utils.datetime import to_excel
from openpyxl.worksheet.datavalidation import DataValidation

from revenue_tool.services.regional_summary import (
    EMPTY_REGION, EXCLUDED, SEGMENTS, build_regional_summary, report_months,
)

SUMMARY_SHEETS = {"rpd": "RPD地区收入汇总", "cpd": "CPD地区收入汇总"}
SOURCE_SHEETS = {"rpd": "_summary_source", "cpd": "_summary_source"}


def _q(value):
    return '"' + str(value).replace('"', '""') + '"'


def _cache_value(value):
    if value is None or value == "":
        return Missing()
    if isinstance(value, bool):
        return Boolean(v=value)
    if isinstance(value, (date, datetime)):
        return Number(v=to_excel(value))
    if isinstance(value, (int, float, Decimal)):
        return Number(v=float(value))
    return Text(v=str(value))


def _bucket_formula(refs, summary, subtotal, sheet_title):
    month, amount, segment = (refs[f"final_revenue_month_{summary.mode}"],
                              refs["final_revenue_forecast"], refs["final_revenue_segment"])
    labels = summary.labels
    selected = f'{quote_sheetname(sheet_title)}!$C$4'
    other = _q(labels[4])
    for position in range(2, -1, -1):
        other = f'IF({segment}={_q(SEGMENTS[position])},{_q(labels[position + 1])},{other})'
    valid = (f'AND({_valid_month(selected)},ISNUMBER({amount}),ISTEXT({month}),LEN({month})=7,'
             f'LEFT({month},5)=LEFT({selected},5),'
             f'IFERROR(TEXT(VALUE(RIGHT({month},2)),"00")=RIGHT({month},2),FALSE),'
             f'RIGHT({month},2)>="01",RIGHT({month},2)<="12")')
    current = _q(labels[5]) if subtotal else other
    earlier = _q(EXCLUDED) if subtotal else _q(labels[0])
    return (f'=IFERROR(IF({valid},IF({month}={selected},{current},'
            f'IF({month}<{selected},{earlier},{_q(EXCLUDED)})),'
            f'{_q(EXCLUDED)}),{_q(EXCLUDED)})')


def _valid_month(ref):
    return (f'IFERROR(AND(ISTEXT({ref}),LEN({ref})=7,MID({ref},5,1)="-",'
            f'TEXT(VALUE(LEFT({ref},4)),"0000")=LEFT({ref},4),VALUE(LEFT({ref},4))>=1,'
            f'TEXT(VALUE(RIGHT({ref},2)),"00")=RIGHT({ref},2),'
            f'VALUE(RIGHT({ref},2))>=1,VALUE(RIGHT({ref},2))<=12),FALSE)')


def write_regional_pivots(workbook, rows, config, month):
    months = report_months(month)
    for cache_id, selected in enumerate(months, 1):
        titles = {mode: f'{title}-{selected}' if len(months) > 1 else title
                  for mode, title in SUMMARY_SHEETS.items()}
        source_title = f'_summary_{selected.replace("-", "_")}' if len(months) > 1 else '_summary_source'
        _write_month_pivots(workbook, rows, config, selected, titles, source_title, cache_id)


def _write_month_pivots(workbook, rows, config, month, titles, source_title, cache_id):
    base = workbook[config.output["sheets"]["base"]]
    columns = config.base_columns
    ids = [c["id"] for c in columns]
    headers = ["原始地区部" if c["id"] == "region" else c["name"] for c in columns]
    headers += ["地区部", "汇总项目", "基表行号", "收入口径"]
    count = len(columns)
    if 4 * len(rows) + 7 > 1048576:
        raise ValueError("基表超过262142行，双口径明细源超出Excel工作表行数限制")
    report_sheets = {mode: workbook.create_sheet(title) for mode, title in titles.items()}
    source = workbook.create_sheet(source_title)
    source.append(headers)
    source.sheet_state = "hidden"
    source.freeze_panes = "A2"
    first = build_regional_summary(rows, month, "rpd")
    regions = first.regions
    buckets = [*first.labels, EXCLUDED]
    region_ids = {v: i for i, v in enumerate(regions)}
    bucket_ids = {v: i for i, v in enumerate(buckets)}
    fields = [CacheField(name=name, sharedItems=SharedItems()) for name in headers]
    fields[count].sharedItems = SharedItems(_fields=[Text(v=x) for x in regions], containsString=True)
    fields[count + 1].sharedItems = SharedItems(_fields=[Text(v=x) for x in buckets], containsString=True)
    fields[count + 3].sharedItems = SharedItems(_fields=[Text(v=x) for x in ("RPD", "CPD", "__SCHEMA__")], containsString=True)
    cache = CacheDefinition(
        cacheSource=CacheSource(type="worksheet", worksheetSource=WorksheetSource(
            ref=f"A1:{get_column_letter(len(headers))}{4 * len(rows) + 7}", sheet=source.title)),
        cacheFields=fields, recordCount=4 * len(rows) + 6, saveData=True,
        refreshOnLoad=False, enableRefresh=True, backgroundQuery=False,
        createdVersion=6, refreshedVersion=6, minRefreshableVersion=3,
    )
    cache.records = RecordList()
    # openpyxl constructs the records relationship before assigning records._id.
    # Seed it now so cache 2+ cannot accidentally point to cache 1's records.
    cache.records._id = cache_id
    records = cache.records.r
    for mode in ("rpd", "cpd"):
        summary = build_regional_summary(rows, month, mode)
        sheet = report_sheets[mode]
        mode_index = 0 if mode == "rpd" else 1
        for source_number, entry in enumerate(summary.entries, len(records) + 2):
            values = rows[entry.base_row - 2].values
            for index, field in enumerate(ids, 1):
                ref = f'{quote_sheetname(base.title)}!{get_column_letter(index)}{entry.base_row}'
                cell = source.cell(source_number, index, f'=IF(ISBLANK({ref}),"",{ref})')
                cell.number_format = base.cell(entry.base_row, index).number_format
            refs = {field: f"{get_column_letter(i)}{source_number}" for i, field in enumerate(ids, 1)}
            region = refs["region"]
            source.cell(source_number, count + 1,
                        f'=IF(LEN(TRIM({region}&""))=0,{_q(EMPTY_REGION)},{region}&"")')
            source.cell(source_number, count + 2, _bucket_formula(refs, summary, entry.subtotal_copy, sheet.title))
            source.cell(source_number, count + 3, entry.base_row)
            source.cell(source_number, count + 4, mode.upper())
            records.append(Record(_fields=[*(_cache_value(values.get(f)) for f in ids),
                Index(v=region_ids[entry.region]), Index(v=bucket_ids[entry.bucket]),
                Number(v=entry.base_row), Index(v=mode_index)]))
        source.auto_filter.ref = source.dimensions
        pivot_fields = [PivotField(defaultSubtotal=False) for _ in headers]
        pivot_fields[count] = PivotField(axis="axisRow", defaultSubtotal=False, showAll=True,
            name="地区部", items=[FieldItem(x=i) for i in range(len(regions))])
        pivot_fields[count + 1] = PivotField(axis="axisCol", defaultSubtotal=False,
            showAll=True, sortType="manual", items=[FieldItem(x=i, h=(i == 6)) for i in range(7)])
        pivot_fields[count + 3] = PivotField(axis="axisPage", defaultSubtotal=False,
            items=[FieldItem(x=0), FieldItem(x=1), FieldItem(x=2, h=True)])
        amount_index = ids.index("final_revenue_forecast")
        pivot_fields[amount_index].dataField = True
        pivot = TableDefinition(
            name=f"RegionalRevenue{mode.upper()}{month.replace('-', '')}", cacheId=cache_id, dataCaption="最终收入预测",
            grandTotalCaption="小计", rowHeaderCaption="地区部", colHeaderCaption="汇总项目",
            location=Location(ref=f"A8:G{10 + len(regions)}", firstHeaderRow=1, firstDataRow=2, firstDataCol=1, rowPageCount=1, colPageCount=1),
            pivotFields=pivot_fields, rowFields=[RowColField(x=count)], colFields=[RowColField(x=count + 1)],
            pageFields=[PageField(fld=count + 3, item=mode_index)],
            rowItems=[RowColItem(x=[Index(v=i)]) for i in range(len(regions))] + [RowColItem(t="grand", x=[Index(v=0)])],
            colItems=[RowColItem(x=[Index(v=i)]) for i in range(6)],
            dataFields=[DataField(name="最终收入预测汇总", fld=amount_index, subtotal="sum", numFmtId=4)],
            rowGrandTotals=True, colGrandTotals=False, enableDrill=True,
            subtotalHiddenItems=False, showHeaders=True, compact=False, compactData=False,
            outline=False, gridDropZones=False, showDrill=False, showEmptyRow=True,
            showEmptyCol=True, missingCaption="0.00", showMissing=True,
            createdVersion=6, updatedVersion=6, minRefreshableVersion=3,
            pivotTableStyleInfo=PivotTableStyle(name="PivotStyleMedium9", showRowHeaders=True,
                showColHeaders=True, showRowStripes=True, showColStripes=False, showLastColumn=True),
        )
        pivot.cache = cache
        sheet.add_pivot(pivot)
        sheet.merge_cells("A1:G1")
        sheet["A1"] = f"{mode.upper()}地区收入汇总"
        sheet["A1"].font = Font(size=16, bold=True, color="1F4E78")
        sheet.row_dimensions[1].height = 29
        sheet.merge_cells("A2:G2")
        sheet["A2"] = "黄色年月格可下拉选择。改月份或人工字段后，先Ctrl+Alt+F9重算，再“数据→全部刷新”。双击金额查看明细。"
        sheet["A2"].alignment = Alignment(wrap_text=True, vertical="center")
        sheet.row_dimensions[2].height = 32
        sheet.merge_cells("A3:G3")
        last_source = 4 * len(rows) + 7
        bucket_range = f'{quote_sheetname(source.title)}!$AP$2:$AP${last_source}'
        mode_range = f'{quote_sheetname(source.title)}!$AR$2:$AR${last_source}'
        omitted = (f'COUNTIFS({bucket_range},{_q(EXCLUDED)},{mode_range},{_q(mode.upper())})'
                   f'-{len(rows)}+COUNTIFS({bucket_range},"小计",{mode_range},{_q(mode.upper())})')
        sheet["A3"] = (f'=IF({_valid_month("C4")},"统计年份："&LEFT(C4,4)&"；未纳入："&({omitted})&'
                       '"条（月份不在范围、空白或金额无效）。辅助源请勿直接求和。",'
                       '"请修正黄色年月：填写YYYY-MM，然后重算并刷新。")')
        sheet["A3"].alignment = Alignment(wrap_text=True, vertical="center")
        sheet["A3"].font = Font(size=10, color="666666")
        sheet.row_dimensions[3].height = 30
        sheet["A6"] = "收入口径"
        sheet["B6"] = mode.upper()
        sheet.merge_cells("C4:G4")
        sheet["C4"] = month
        sheet["C4"].number_format = "@"
        sheet["C4"].fill = PatternFill("solid", fgColor="FFF2CC")
        sheet["C4"].font = Font(size=13, bold=True)
        sheet["C4"].alignment = Alignment(horizontal="center", vertical="center")
        sheet.row_dimensions[4].height = 28
        choices = ','.join(f'{month[:4]}-{number:02d}' for number in range(1, 13))
        validation = DataValidation(type="list", formula1=_q(choices), allow_blank=False,
            showDropDown=False, showErrorMessage=True, errorStyle="warning", errorTitle="确认统计年月",
            error="下拉列出生成时年份；跨年可填写完整YYYY-MM并确认。", showInputMessage=True,
            promptTitle="统计年月", prompt="下拉选择月份；修改后重算并刷新透视。")
        sheet.add_data_validation(validation)
        validation.add(sheet["C4"])
        sheet["A8"] = "最终收入预测"
        sheet["B8"] = "汇总项目"
        for index, label in enumerate(["地区部", *summary.labels], 1):
            sheet.cell(9, index, label)
            sheet.cell(5, index, label)
        sheet["B5"] = (f'=IF({_valid_month("C4")},IF(RIGHT(C4,2)="01","前期累计（无）",'
                       '"1—"&(VALUE(RIGHT(C4,2))-1)&"月累计"),"请修正统计年月")')
        for number, region in enumerate(regions, 10):
            sheet.cell(number, 1, region)
            for column, value in enumerate(summary.totals[region], 2):
                sheet.cell(number, column, float(value))
        last = 10 + len(regions)
        sheet.cell(last, 1, "小计")
        for column in range(6):
            sheet.cell(last, column + 2, float(sum((v[column] for v in summary.totals.values()), Decimal("0.00"))))
        for row in sheet.iter_rows(min_row=5, max_row=last, max_col=7):
            for cell in row:
                cell.alignment = Alignment(vertical="center", horizontal="left" if cell.column == 1 else "right")
                if cell.row in (5, 8, 9):
                    cell.fill = PatternFill("solid", fgColor="1F4E78")
                    cell.font = Font(bold=True, color="FFFFFF")
                else:
                    if cell.column > 1:
                        cell.number_format = "#,##0.00"
                    if cell.row == last or cell.column == 7:
                        cell.fill = PatternFill("solid", fgColor="D9EAF7")
                        cell.font = Font(bold=True)
                sheet.row_dimensions[cell.row].height = 22
        sheet.column_dimensions["A"].width = 26
        for column in "BCDEFG":
            sheet.column_dimensions[column].width = 19
        # Keep dynamic presentation headers outside the native pivot area;
        # Excel refresh must never overwrite the month input or cumulative formula.
        sheet.row_dimensions[6].hidden = True
        sheet.row_dimensions[7].hidden = True
        sheet.row_dimensions[8].hidden = True
        sheet.row_dimensions[9].hidden = True
        sheet.freeze_panes = "B10"
        sheet.sheet_view.showGridLines = False
        sheet.print_options.horizontalCentered = True
        sheet.print_area = f"A1:G{last}"
        sheet.sheet_properties.pageSetUpPr.fitToPage = True
        sheet.page_setup.orientation = "landscape"
        sheet.page_setup.paperSize = sheet.PAPERSIZE_A4
        sheet.page_setup.fitToWidth = 1
        sheet.page_setup.fitToHeight = 0
    # Filtered schema members keep all six columns in a fixed order even when
    # the selected period has no matching data. They can never enter totals or
    # native Show Details because their mode is neither RPD nor CPD.
    for index, bucket in enumerate(first.labels):
        number = len(records) + 2
        region = regions[0] if regions else None
        source.append([None] * count + [region, bucket, None, "__SCHEMA__"])
        records.append(Record(_fields=[Missing() for _ in ids] +
            [Index(v=0) if regions else Missing(), Index(v=index), Missing(), Index(v=2)]))
    source.auto_filter.ref = source.dimensions
