"""Save initial formula results without removing live Excel formulas.

openpyxl intentionally emits empty formula caches. Patch only the generated
cells, leaving every other XLSX part (including native pivots) byte-identical.
Excel still recalculates on opening and after manual edits.
"""
from decimal import Decimal
from pathlib import Path
import re
from tempfile import TemporaryDirectory
from xml.sax.saxutils import escape
from zipfile import ZipFile

from openpyxl import Workbook


_CELL = re.compile(rb'<c\b(?P<attrs>[^>]*)>(?P<body>.*?)</c>', re.DOTALL)
_ADDRESS = re.compile(rb'\br="([A-Z]+[0-9]+)"')
_TYPE = re.compile(rb'\s+t="[^"]*"')
_VALUE = re.compile(rb'<v(?:\s[^>]*)?>.*?</v>|<v\s*/>', re.DOTALL)


def _patch(xml: bytes, values: dict[str, object]) -> bytes:
    pending = dict(values)

    def replace(match: re.Match) -> bytes:
        attrs, body = match.group('attrs', 'body')
        address = _ADDRESS.search(attrs)
        key = address.group(1).decode() if address else None
        if key not in pending:
            return match.group(0)
        if b'<f' not in body:
            raise ValueError(f'Expected formula in cached cell {key}')
        value = pending.pop(key)
        if isinstance(value, bool):
            kind, text = 'b', str(int(value))
        elif isinstance(value, (int, float, Decimal)):
            kind, text = 'n', str(value)
        else:
            kind, text = 'str', '' if value is None else str(value)
        attrs = _TYPE.sub(b'', attrs) + f' t="{kind}"'.encode()
        body = _VALUE.sub(b'', body)
        return b'<c' + attrs + b'>' + body + b'<v>' + escape(text).encode('utf-8') + b'</v></c>'

    result = _CELL.sub(replace, xml)
    if pending:
        raise ValueError('Some formula cache cells were not written')
    return result


def save_with_formula_cache(
    workbook: Workbook, path: Path, values_by_sheet: dict[str, dict[str, object]],
) -> None:
    # Sheet order and sheetN.xml numbering are assigned by openpyxl on save.
    parts = {f'xl/worksheets/sheet{i}.xml': values_by_sheet[sheet.title]
             for i, sheet in enumerate(workbook.worksheets, 1)
             if sheet.title in values_by_sheet}
    with TemporaryDirectory(prefix='.revenue-save-', dir=path.parent) as tmp:
        raw, finished = Path(tmp) / 'raw.xlsx', Path(tmp) / 'finished.xlsx'
        workbook.save(raw)
        with ZipFile(raw) as source, ZipFile(finished, 'w') as target:
            for info in source.infolist():
                data = source.read(info.filename)
                if info.filename in parts:
                    data = _patch(data, parts[info.filename])
                target.writestr(info, data)
        finished.replace(path)
