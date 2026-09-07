"""Independent native spreadsheet API: recalculate, refresh, and Show Details.

Executed with distribution python3-uno, not the application's Python runtime.
Only synthetic test workbooks are passed to this helper.
"""
import json
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
        snapshots = []
        for edits in json.loads(Path(plan_path).read_text()):
            for sheet_name, address, value in edits:
                cell = doc.Sheets.getByName(sheet_name).getCellRangeByName(address)
                if value is None:
                    cell.setFormula("")
                elif isinstance(value, (int, float)):
                    cell.setValue(value)
                else:
                    cell.setString(value)
            doc.calculateAll()
            snapshot = {}
            for name in ("RPD地区收入汇总", "CPD地区收入汇总"):
                sheet = doc.Sheets.getByName(name)
                tables = sheet.getDataPilotTables()
                if tables.getCount() != 1:
                    raise AssertionError(f"{name}: expected one native pivot, got {tables.getCount()}")
                table = tables.getByIndex(0)
                table.refresh()
                area = table.getOutputRange()
                # Discover positions after native refresh; also detect shifted or extra columns.
                grid = sheet.getCellRangeByPosition(area.StartColumn, area.StartRow, area.EndColumn, area.EndRow).getDataArray()
                header_offset = next(i for i, r in enumerate(grid) if "9月小计" in r)
                headers = list(grid[header_offset])
                cells = {}
                total_caption = None
                for row_offset in range(header_offset + 1, len(grid)):
                    values = grid[row_offset]
                    region = str(values[0])
                    if row_offset == len(grid) - 1:
                        # Calc drops OOXML grandTotalCaption on import and uses
                        # its localized total label. Record it; normalize only
                        # this last total row for numeric/drill-through checks.
                        total_caption = region
                        if region in ("Total Result", "小计"):
                            region = "小计"
                    cells[region] = {}
                    for col_offset in range(1, len(headers)):
                        address = CellAddress(area.Sheet, area.StartColumn + col_offset, area.StartRow + row_offset)
                        detail = table.getDrillDownData(address)
                        contracts = []
                        if detail:
                            contract_column = list(detail[0]).index("合同号")
                            contracts = [str(r[contract_column]) for r in detail[1:]]
                        cells[region][headers[col_offset]] = {"value": values[col_offset] or 0, "contracts": contracts}
                snapshot[name] = {"headers": headers, "cells": cells, "total_caption": total_caption}
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
