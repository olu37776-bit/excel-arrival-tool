"""Independent native spreadsheet API: recalculate, refresh, and Show Details.

Executed with distribution python3-uno, not the application's Python runtime.
Only synthetic test workbooks are passed to this helper.
"""
import json
import re
from pathlib import Path
import subprocess
import sys
import time
import uuid

import uno
from com.sun.star.beans import PropertyValue
from com.sun.star.table import CellAddress


def prop(name, value):
    p = PropertyValue()
    p.Name, p.Value = name, value
    return p


def main():
    office, source, plan_path, output = sys.argv[1:]
    source = Path(source).resolve()
    pipe = "summary_" + uuid.uuid4().hex
    process = subprocess.Popen([office, "--headless", "--norestore", "--nodefault", "--nofirststartwizard",
        f"-env:UserInstallation={(source.parent / 'uno-profile').as_uri()}",
        f"--accept=pipe,name={pipe};urp;StarOffice.ServiceManager"], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    doc = desktop = None
    try:
        local = uno.getComponentContext()
        resolver = local.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver", local)
        deadline = time.monotonic() + 30
        while True:
            try:
                context = resolver.resolve(f"uno:pipe,name={pipe};urp;StarOffice.ComponentContext")
                break
            except Exception:
                if time.monotonic() >= deadline or process.poll() is not None:
                    raise
                time.sleep(0.1)
        desktop = context.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", context)
        doc = desktop.loadComponentFromURL(source.as_uri(), "_blank", 0,
            (prop("Hidden", True), prop("ReadOnly", False), prop("UpdateDocMode", 3)))
        if doc is None:
            raise RuntimeError("Office could not open the generated XLSX")
        doc.enableAutomaticCalculation(True)
        snapshots = []
        for edits in json.loads(Path(plan_path).read_text()):
            for sheet_name, address, value in edits:
                cell = doc.Sheets.getByName(sheet_name).getCellRangeByName(address)
                if value is None:
                    cell.setFormula("")
                elif isinstance(value, bool):
                    cell.setFormula("=TRUE()" if value else "=FALSE()")
                elif isinstance(value, (int, float)):
                    cell.setValue(value)
                else:
                    cell.setString(value)
            # Capture formula results immediately after editing, before refreshing
            # pivots. No F9/calculateAll is allowed in this automatic-edit test.
            base = doc.Sheets.getByName("基表")
            cursor = base.createCursor()
            cursor.gotoEndOfUsedArea(False)
            snapshot = {"base": base.getCellRangeByPosition(0, 0, 39, cursor.RangeAddress.EndRow).getDataArray(), "summaries": {}}
            for name in doc.Sheets.getElementNames():
                if not name.startswith(("RPD地区收入汇总", "CPD地区收入汇总")):
                    continue
                sheet = doc.Sheets.getByName(name)
                tables = sheet.getDataPilotTables()
                if tables.getCount() != 1:
                    raise AssertionError(f"{name}: expected one native pivot, got {tables.getCount()}")
                table = tables.getByIndex(0)
                table.refresh()
                area = table.getOutputRange()
                # Discover positions after native refresh; also detect shifted or extra columns.
                grid = sheet.getCellRangeByPosition(area.StartColumn, area.StartRow, area.EndColumn, area.EndRow).getDataArray()
                header_offset = next(i for i, r in enumerate(grid) if "订未发" in r and "小计" in r)
                headers = list(grid[header_offset])
                month_headers = grid[header_offset - 1]
                columns, months = {}, []
                month = None
                for col_offset in range(1, len(headers)):
                    value = str(month_headers[col_offset])
                    if re.fullmatch(r"[0-9]{4}-[0-9]{2}", value):
                        month = value
                        if month not in months:
                            months.append(month)
                    if headers[col_offset] in ("订未发", "发未收", "交未验", "其他", "小计"):
                        if month is None:
                            raise AssertionError(f"Missing month heading: {grid!r}")
                        columns[col_offset] = (month, headers[col_offset])
                cells = {}
                for row_offset in range(header_offset + 1, len(grid)):
                    values = grid[row_offset]
                    region = str(values[0])
                    if row_offset == len(grid) - 1 and region in ("Total Result", "小计"):
                        region = "小计"
                    cells[region] = {}
                    for col_offset, (month, label) in columns.items():
                        address = CellAddress(area.Sheet, area.StartColumn + col_offset, area.StartRow + row_offset)
                        detail = table.getDrillDownData(address)
                        contracts = []
                        if detail:
                            contract_column = list(detail[0]).index("合同号")
                            contracts = [str(r[contract_column]) for r in detail[1:]]
                        cells[region].setdefault(month, {})[label] = {"value": values[col_offset] or 0, "contracts": contracts}
                snapshot["summaries"][name] = {"months": months, "cells": cells}
            snapshots.append(snapshot)
        Path(output).write_text(json.dumps(snapshots, ensure_ascii=False), encoding="utf-8")
    finally:
        if doc:
            doc.close(True)
        if desktop:
            desktop.terminate()
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


if __name__ == "__main__":
    main()
