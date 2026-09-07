"""Editable native pivots: month groups run horizontally across five buckets."""
from datetime import date, datetime
from decimal import Decimal

from openpyxl.pivot.cache import CacheDefinition, CacheField, CacheSource, SharedItems, WorksheetSource
from openpyxl.pivot.fields import Boolean, Index, Missing, Number, Text
from openpyxl.pivot.record import Record, RecordList
from openpyxl.pivot.table import DataField, FieldItem, Location, PivotField, RowColField, RowColItem, TableDefinition, PivotTableStyle, PageField
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter, quote_sheetname
from openpyxl.utils.datetime import to_excel

from revenue_tool.services.final_revenue import calculate_final_values
from revenue_tool.services.regional_summary import EMPTY_REGION, EXCLUDED, SEGMENTS, LABELS, build_regional_summary, discover_months

SUMMARY_SHEETS = {'rpd': 'RPD地区收入汇总', 'cpd': 'CPD地区收入汇总'}
SOURCE_SHEETS = {'rpd': '_summary_source', 'cpd': '_summary_source'}


def _q(value):
    return '"' + str(value).replace('"', '""') + '"'


def _cache_value(value):
    if value is None or value == '':
        return Missing()
    if isinstance(value, bool):
        return Boolean(v=value)
    if isinstance(value, (date, datetime)):
        return Number(v=to_excel(value))
    if isinstance(value, (int, float, Decimal)):
        return Number(v=float(value))
    return Text(v=str(value))


def _valid_month(ref):
    return (f'IFERROR(AND(ISTEXT({ref}),LEN({ref})=7,MID({ref},5,1)="-",'
            f'TEXT(VALUE(LEFT({ref},4)),"0000")=LEFT({ref},4),VALUE(LEFT({ref},4))>=1,'
            f'TEXT(VALUE(RIGHT({ref},2)),"00")=RIGHT({ref},2),'
            f'VALUE(RIGHT({ref},2))>=1,VALUE(RIGHT({ref},2))<=12),FALSE)')


def write_regional_pivots(workbook, rows, config):
    months = discover_months(rows)
    sheets = {mode: workbook.create_sheet(title) for mode, title in SUMMARY_SHEETS.items()}
    if not months:
        for mode, sheet in sheets.items():
            sheet['A1'] = f'{mode.upper()}地区收入汇总'
            sheet['A2'] = '暂无有效收入年月。基表可以编辑、筛选和自行创建透视表。'
            sheet.column_dimensions['A'].width = 80
        return
    last_column = 1 + 5 * len(months)
    source_length = 4 * len(rows) + 5 * len(months) + 1
    if last_column > 16384 or source_length > 1048576:
        raise ValueError('实际月份或明细行数超过Excel工作表上限，请缩小源数据范围')
    base = workbook[config.output['sheets']['base']]
    ids = [c['id'] for c in config.base_columns]
    headers = ['原始地区部' if c['id'] == 'region' else c['name'] for c in config.base_columns]
    headers += ['地区部', '收入年月', '汇总项目', '基表行号', '收入口径']
    count = len(ids)
    region_col, month_col, bucket_col, row_col, mode_col = range(count, count + 5)
    summaries = {mode: build_regional_summary(rows, mode, months) for mode in sheets}
    regions = summaries['rpd'].regions
    region_ids = {value: i for i, value in enumerate(regions)}
    month_members = [*months, EXCLUDED]
    bucket_members = [*LABELS, EXCLUDED]
    month_ids = {value: i for i, value in enumerate(month_members)}
    bucket_ids = {value: i for i, value in enumerate(bucket_members)}
    source = workbook.create_sheet('_summary_source')
    source.sheet_state = 'hidden'
    source.append(headers)
    fields = [CacheField(name=name, sharedItems=SharedItems()) for name in headers]
    for field, values in ((region_col, regions), (month_col, month_members),
                          (bucket_col, bucket_members), (mode_col, ['RPD', 'CPD', '__SCHEMA__'])):
        fields[field].sharedItems = SharedItems(_fields=[Text(v=v) for v in values], containsString=True)
    cache = CacheDefinition(cacheSource=CacheSource(type='worksheet', worksheetSource=WorksheetSource(
        ref=f'A1:{get_column_letter(len(headers))}{source_length}', sheet=source.title)),
        cacheFields=fields, recordCount=source_length - 1, saveData=True, refreshOnLoad=False,
        enableRefresh=True, backgroundQuery=False, createdVersion=6, refreshedVersion=6, minRefreshableVersion=3)
    cache.records = RecordList()
    cache.records._id = 1
    for mode_index, (mode, summary) in enumerate(summaries.items()):
        for entry in summary.entries:
            number = len(cache.records.r) + 2
            values = dict(rows[entry.base_row - 2].values)
            values.update(calculate_final_values(values))
            refs = {}
            for index, field in enumerate(ids, 1):
                ref = f'{quote_sheetname(base.title)}!{get_column_letter(index)}{entry.base_row}'
                source.cell(number, index, f'=IF(ISBLANK({ref}),"",{ref})').number_format = base.cell(entry.base_row, index).number_format
                refs[field] = f'{get_column_letter(index)}{number}'
            region = refs['region']
            month = refs[f'final_revenue_month_{mode}']
            amount = refs['final_revenue_forecast']
            segment = refs['final_revenue_segment']
            bucket = _q('其他')
            for label in reversed(SEGMENTS[:3]):
                bucket = f'IF({segment}={_q(label)},{_q(label)},{bucket})'
            if entry.subtotal_copy:
                bucket = _q('小计')
            source.cell(number, region_col + 1, f'=IF(LEN(TRIM({region}&""))=0,{_q(EMPTY_REGION)},{region}&"")')
            source.cell(number, month_col + 1, f'=IF({_valid_month(month)},{month},{_q(EXCLUDED)})')
            source.cell(number, bucket_col + 1,
                        f'=IFERROR(IF(AND({_valid_month(month)},ISNUMBER({amount})),{bucket},{_q(EXCLUDED)}),{_q(EXCLUDED)})')
            source.cell(number, row_col + 1, entry.base_row)
            source.cell(number, mode_col + 1, mode.upper())
            cache.records.r.append(Record(_fields=[*(_cache_value(values.get(field)) for field in ids),
                Index(v=region_ids[entry.region]), Index(v=month_ids[entry.month]), Index(v=bucket_ids[entry.bucket]),
                Number(v=entry.base_row), Index(v=mode_index)]))
        sheet = sheets[mode]
        pivot_fields = [PivotField(defaultSubtotal=False) for _ in headers]
        pivot_fields[region_col] = PivotField(axis='axisRow', defaultSubtotal=False, showAll=True,
                                             items=[FieldItem(x=i) for i in range(len(regions))])
        pivot_fields[month_col] = PivotField(axis='axisCol', defaultSubtotal=False, showAll=True,
            sortType='ascending', items=[FieldItem(x=i, h=value == EXCLUDED) for i, value in enumerate(month_members)])
        pivot_fields[bucket_col] = PivotField(axis='axisCol', defaultSubtotal=False, showAll=True,
            sortType='manual', items=[FieldItem(x=i, h=value == EXCLUDED) for i, value in enumerate(bucket_members)])
        pivot_fields[mode_col] = PivotField(axis='axisPage', defaultSubtotal=False,
                                           items=[FieldItem(x=0), FieldItem(x=1), FieldItem(x=2, h=True)])
        amount_index = ids.index('final_revenue_forecast')
        pivot_fields[amount_index].dataField = True
        last_row = 9 + len(regions)
        last_letter = get_column_letter(last_column)
        pivot = TableDefinition(name=f'RegionalRevenue{mode.upper()}', cacheId=1, dataCaption='最终收入预测',
            grandTotalCaption='小计', rowHeaderCaption='地区部', colHeaderCaption='收入年月',
            location=Location(ref=f'A6:{last_letter}{last_row}', firstHeaderRow=1, firstDataRow=3,
                              firstDataCol=1, rowPageCount=1, colPageCount=1),
            pivotFields=pivot_fields, rowFields=[RowColField(x=region_col)],
            colFields=[RowColField(x=month_col), RowColField(x=bucket_col)],
            pageFields=[PageField(fld=mode_col, item=mode_index)],
            rowItems=[RowColItem(x=[Index(v=i)]) for i in range(len(regions))] + [RowColItem(t='grand', x=[Index(v=0)])],
            colItems=[RowColItem(x=[Index(v=i), Index(v=j)]) for i in range(len(months)) for j in range(5)],
            dataFields=[DataField(name='最终收入预测汇总', fld=amount_index, subtotal='sum', numFmtId=4)],
            rowGrandTotals=True, colGrandTotals=False, enableDrill=True, subtotalHiddenItems=False,
            showHeaders=True, compact=False, compactData=False, outline=False, gridDropZones=False,
            showDrill=False, showEmptyRow=True, showEmptyCol=True, missingCaption='0.00', showMissing=True,
            createdVersion=6, updatedVersion=6, minRefreshableVersion=3,
            pivotTableStyleInfo=PivotTableStyle(name='PivotStyleMedium9', showRowHeaders=True,
                showColHeaders=True, showRowStripes=True, showColStripes=False, showLastColumn=True))
        pivot.cache = cache
        sheet.add_pivot(pivot)
        sheet['A1'] = f'{mode.upper()}地区收入汇总'
        sheet['A1'].font = Font(size=16, bold=True, color='1F4E78')
        sheet.merge_cells('A1:F1')
        sheet['A2'] = '可使用透视表下拉筛选，双击金额查看明细。请在基表黄色字段调整；最终字段自动更新后，点“数据→全部刷新”更新汇总。'
        sheet.merge_cells('A2:K2' if last_column >= 11 else 'A2:F2')
        sheet['A2'].alignment = Alignment(wrap_text=True, vertical='center')
        sheet.row_dimensions[2].height = 36
        sheet['A3'] = '按实际最终收入年月排列；无前期累计。基表可编辑、排序、筛选及自行透视。'
        sheet.merge_cells('A3:K3' if last_column >= 11 else 'A3:F3')
        sheet['A4'], sheet['B4'] = '收入口径', mode.upper()
        sheet['A6'], sheet['B6'], sheet['A8'] = '最终收入预测', '收入年月', '地区部'
        for month_index, month in enumerate(months):
            start = 2 + month_index * 5
            sheet.cell(7, start, month)
            for offset, label in enumerate(LABELS):
                column = start + offset
                sheet.cell(8, column, label)
                for number, region in enumerate(regions, 9):
                    sheet.cell(number, 1, region)
                    sheet.cell(number, column, float(summary.totals[region][month][offset]))
                sheet.cell(last_row, column, float(sum((summary.totals[region][month][offset] for region in regions), Decimal(0))))
        sheet.cell(last_row, 1, '小计')
        for row in sheet.iter_rows(min_row=6, max_row=last_row, max_col=last_column):
            for cell in row:
                cell.alignment = Alignment(vertical='center', horizontal='left' if cell.column == 1 else 'right')
                if cell.row <= 8:
                    cell.fill = PatternFill('solid', fgColor='1F4E78')
                    cell.font = Font(bold=True, color='FFFFFF')
                else:
                    if cell.column > 1:
                        cell.number_format = '#,##0.00'
                    if cell.row == last_row or (cell.column > 1 and (cell.column - 1) % 5 == 0):
                        cell.fill = PatternFill('solid', fgColor='D9EAF7')
                        cell.font = Font(bold=True)
        sheet.column_dimensions['A'].width = 26
        for column in range(2, last_column + 1):
            sheet.column_dimensions[get_column_letter(column)].width = 17
        sheet.freeze_panes = 'B9'
        sheet.sheet_view.showGridLines = False
        sheet.print_title_rows = '6:8'
        sheet.print_area = f'A1:{last_letter}{last_row}'
        sheet.page_setup.orientation = 'landscape'
    for month_index, month in enumerate(months):
        for bucket_index, bucket in enumerate(LABELS):
            source.append([None] * count + [regions[0], month, bucket, None, '__SCHEMA__'])
            cache.records.r.append(Record(_fields=[Missing() for _ in ids] + [Index(v=0),
                Index(v=month_index), Index(v=bucket_index), Missing(), Index(v=2)]))
    source.auto_filter.ref = source.dimensions
