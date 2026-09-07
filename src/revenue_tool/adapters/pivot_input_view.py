"""Mask displayed native pivot cells during import without loading pivot caches."""
import posixpath
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree as ET

from openpyxl.cell.read_only import EMPTY_CELL
from openpyxl.utils.cell import range_boundaries
from revenue_tool.domain.models import WorkbookReadError


def _local(tag):
    return tag.rsplit('}', 1)[-1]


def _part_path(owner, target):
    parsed = urlsplit(target)
    if parsed.scheme or parsed.netloc or parsed.query or parsed.fragment:
        raise ValueError('透视关系不是内部文件')
    target = unquote(parsed.path)
    path = posixpath.normpath(target.lstrip('/') if target.startswith('/') else posixpath.join(posixpath.dirname(owner), target))
    if path.startswith('../') or path == '..' or '\\' in path:
        raise ValueError('透视关系路径无效')
    return path


def _bounds(ref):
    bounds = range_boundaries(ref)
    left, top, right, bottom = bounds
    if None in bounds or not (1 <= left <= right <= 16384 and 1 <= top <= bottom <= 1048576):
        raise ValueError('透视显示范围无效')
    return bounds


def _ranges(workbook, sheet):
    archive = getattr(workbook, '_archive', None)
    owner = getattr(sheet, '_worksheet_path', None)
    if archive is None or owner is None:
        return ()
    owner = owner.lstrip('/')
    rel_path = posixpath.join(posixpath.dirname(owner), '_rels', posixpath.basename(owner) + '.rels')
    ids = []
    # Stream the sheet instead of materializing every business cell as XML.
    with archive.open(owner) as stream:
        for event, node in ET.iterparse(stream, events=('end',)):
            if _local(node.tag) == 'pivotPart':
                ids.append(next((v for k, v in node.attrib.items() if _local(k) == 'id'), None))
            node.clear()
    if rel_path not in archive.namelist():
        if ids:
            raise ValueError('透视关系文件缺失')
        return ()
    relationships = {r.get('Id'): r for r in ET.fromstring(archive.read(rel_path))}
    # openpyxl's writer links pivots via worksheet relationships alone.
    # Both Excel's explicit pivotParts and this relationship-only form occur.
    if not ids:
        ids = [key for key, rel in relationships.items() if rel.get('Type', '').endswith('/pivotTable')]
    ranges = []
    for identifier in ids:
        rel = relationships.get(identifier)
        if rel is None or not rel.get('Type', '').endswith('/pivotTable') or rel.get('TargetMode') == 'External':
            raise ValueError('透视关系缺失或无效')
        part = _part_path(owner, rel.get('Target', ''))
        # Only layout metadata is needed. Never follow the cache relationship.
        with archive.open(part) as stream:
            location = None
            page_count = 0
            for event, node in ET.iterparse(stream, events=('end',)):
                name = _local(node.tag)
                if name == 'location':
                    location = dict(node.attrib)
                elif name == 'pageFields':
                    page_count = int(node.get('count', '0'))
                node.clear()
            if location is None:
                raise ValueError('透视显示范围缺失')
        bounds = _bounds(location.get('ref', ''))
        ranges.append(bounds)
        # Report filters are positioned above the result, separated by one row.
        if page_count:
            rows = int(location.get('rowPageCount', '0')) or page_count
            cols = int(location.get('colPageCount', '0')) or ((page_count + rows - 1) // rows)
            left, top, _, _ = bounds
            first = top - rows - 1
            last_column = left + cols * 3 - 2
            if first < 1 or last_column > 16384 or rows * cols < page_count:
                raise ValueError('透视筛选范围无效')
            for column in range(cols):
                ranges.append((left + column * 3, first, left + column * 3 + 1, top - 2))
    return tuple(ranges)


def business_sheet(workbook, sheet):
    """One cached, read-only projection per sheet; the input ZIP is untouched."""
    views = getattr(workbook, '_business_input_views', None)
    if views is None:
        views = workbook._business_input_views = {}
    if sheet.title not in views:
        try:
            ranges = _ranges(workbook, sheet)
        except Exception as exc:
            raise WorkbookReadError(f'工作表“{sheet.title}”的透视区域无法识别，已停止读取以避免误继承汇总数据：{exc}') from exc
        views[sheet.title] = _BusinessSheet(sheet, ranges) if ranges else sheet
    return views[sheet.title]


class _BusinessSheet:
    def __init__(self, sheet, ranges):
        self.sheet, self.ranges = sheet, ranges

    def __getattr__(self, name):
        return getattr(self.sheet, name)

    def iter_rows(self, min_row=None, max_row=None, min_col=None, max_col=None, values_only=False):
        start_row, start_col = min_row or 1, min_col or 1
        for number, cells in enumerate(self.sheet.iter_rows(min_row=min_row, max_row=max_row,
                                                           min_col=min_col, max_col=max_col), start_row):
            active = [(a, c) for a, b, c, d in self.ranges if b <= number <= d]
            if active:
                cells = tuple(EMPTY_CELL if any(a <= column <= c for a, c in active) else cell
                              for column, cell in enumerate(cells, start_col))
            yield tuple(c.value for c in cells) if values_only else cells

    def __getitem__(self, key):
        if isinstance(key, int):
            return next(self.iter_rows(min_row=key, max_row=key), ())
        left, top, right, bottom = _bounds(key)
        rows = tuple(self.iter_rows(min_row=top, max_row=bottom, min_col=left, max_col=right))
        return rows[0][0] if ':' not in key else rows
