"""Minimal PivotTable fixture used only by compatibility/self-test paths.

Normal revenue output never calls this module. It exists so Windows EXE smoke
and input-compatibility tests can still prove that user-created PivotTables and
grouped caches are ignored safely after the system-generated regional pivots
were removed from production output.
"""
from __future__ import annotations

from openpyxl.pivot.cache import (
    CacheDefinition,
    CacheField,
    CacheSource,
    SharedItems,
    WorksheetSource,
)
from openpyxl.pivot.fields import Index, Number, Text
from openpyxl.pivot.record import Record, RecordList
from openpyxl.pivot.table import (
    DataField,
    FieldItem,
    Location,
    PageField,
    PivotField,
    RowColField,
    RowColItem,
    TableDefinition,
)


def add_pivot_fixture(
    workbook,
    target_sheet,
    *,
    location_ref: str = "AS3:AT5",
    name: str = "UserPivotSmoke",
):
    """Add one small native PivotTable with a report filter."""
    base_name = "_pivot_smoke_source"
    source_name = base_name
    suffix = 2
    while source_name in workbook.sheetnames:
        source_name = f"{base_name}_{suffix}"
        suffix += 1
    source = workbook.create_sheet(source_name)
    source.append(["合同号", "金额", "口径"])
    source.append(["SMOKE", 1, "USER"])
    source.sheet_state = "hidden"

    cache_fields = [
        CacheField(
            name="合同号",
            sharedItems=SharedItems(
                _fields=[Text(v="SMOKE")],
                containsString=True,
            ),
        ),
        CacheField(
            name="金额",
            sharedItems=SharedItems(
                _fields=[Number(v=1)],
                containsNumber=True,
            ),
        ),
        CacheField(
            name="口径",
            sharedItems=SharedItems(
                _fields=[Text(v="USER")],
                containsString=True,
            ),
        ),
    ]
    cache = CacheDefinition(
        cacheSource=CacheSource(
            type="worksheet",
            worksheetSource=WorksheetSource(
                ref="A1:C2",
                sheet=source.title,
            ),
        ),
        cacheFields=cache_fields,
        recordCount=1,
        saveData=True,
        refreshOnLoad=False,
        enableRefresh=True,
        backgroundQuery=False,
        createdVersion=6,
        refreshedVersion=6,
        minRefreshableVersion=3,
    )
    cache.records = RecordList()
    cache.records._id = 1
    cache.records.r.append(
        Record(_fields=[Index(v=0), Number(v=1), Index(v=0)])
    )

    pivot_fields = [
        PivotField(
            axis="axisRow",
            defaultSubtotal=False,
            showAll=True,
            items=[FieldItem(x=0)],
        ),
        PivotField(defaultSubtotal=False, showAll=True),
        PivotField(
            axis="axisPage",
            defaultSubtotal=False,
            showAll=True,
            items=[FieldItem(x=0)],
        ),
    ]
    pivot_fields[1].dataField = True
    pivot = TableDefinition(
        name=name,
        cacheId=1,
        dataCaption="金额",
        grandTotalCaption="小计",
        rowHeaderCaption="合同号",
        location=Location(
            ref=location_ref,
            firstHeaderRow=1,
            firstDataRow=1,
            firstDataCol=1,
            rowPageCount=1,
            colPageCount=1,
        ),
        pivotFields=pivot_fields,
        rowFields=[RowColField(x=0)],
        rowItems=[
            RowColItem(x=[Index(v=0)]),
            RowColItem(t="grand", x=[Index(v=0)]),
        ],
        pageFields=[PageField(fld=2, item=0)],
        dataFields=[
            DataField(name="金额汇总", fld=1, subtotal="sum", numFmtId=4)
        ],
        rowGrandTotals=True,
        colGrandTotals=True,
        enableDrill=True,
        showHeaders=True,
        compact=False,
        compactData=False,
        outline=False,
        showDrill=False,
        createdVersion=6,
        updatedVersion=6,
        minRefreshableVersion=3,
    )
    pivot.cache = cache
    target_sheet.add_pivot(pivot)
    return pivot
