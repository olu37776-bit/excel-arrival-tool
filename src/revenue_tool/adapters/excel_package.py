"""Normalize generated parts to Microsoft's SpreadsheetML constraints.

openpyxl's font serializer can emit an element order rejected by the Microsoft
Open XML validator. Normalize only that generated structure without
reserializing unrelated workbook parts.
"""
import re
from xml.etree import ElementTree as ET


_FONT = re.compile(rb'<font\b[^>]*>.*?</font>', re.DOTALL)
_FONT_ORDER = {name: i for i, name in enumerate((
    'b', 'i', 'strike', 'condense', 'extend', 'outline', 'shadow', 'u',
    'vertAlign', 'sz', 'color', 'name', 'family', 'charset', 'scheme',
))}


def normalize_excel_part(name: str, data: bytes) -> bytes:
    if name == 'xl/styles.xml':
        def sort_font(match):
            font = ET.fromstring(match.group(0))
            font[:] = sorted(font, key=lambda child: _FONT_ORDER.get(child.tag, 999))
            return ET.tostring(font, encoding='utf-8')
        return _FONT.sub(sort_font, data)
    return data
