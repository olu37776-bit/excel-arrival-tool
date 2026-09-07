"""Normalize generated parts to Microsoft's SpreadsheetML constraints.

openpyxl's pivot serializer emits an undeclared r:id on pivotTableDefinition;
the cache is linked via cacheId and the relationship part instead. Its font
serializer also uses an order rejected by the Microsoft Open XML validator.
Only those exact generated structures are changed, without reserializing the
entire package or dropping unrelated attributes/relationships.
"""
import re
from xml.etree import ElementTree as ET


_FONT = re.compile(rb'<font\b[^>]*>.*?</font>', re.DOTALL)
_FONT_ORDER = {name: i for i, name in enumerate((
    'b', 'i', 'strike', 'condense', 'extend', 'outline', 'shadow', 'u',
    'vertAlign', 'sz', 'color', 'name', 'family', 'charset', 'scheme',
))}


def normalize_excel_part(name: str, data: bytes) -> bytes:
    if name.startswith('xl/pivotTables/pivotTable') and name.endswith('.xml'):
        return re.sub(rb'<pivotTableDefinition\b[^>]*>',
                      lambda m: re.sub(rb'\s+r:id="[^"]*"', b'', m.group(0)), data, count=1)
    if name == 'xl/styles.xml':
        def sort_font(match):
            font = ET.fromstring(match.group(0))
            font[:] = sorted(font, key=lambda child: _FONT_ORDER.get(child.tag, 999))
            return ET.tostring(font, encoding='utf-8')
        return _FONT.sub(sort_font, data)
    return data
