from __future__ import annotations

from copy import deepcopy
from decimal import Decimal
import json
import os
from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory
import unittest
from zipfile import ZipFile

from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

from revenue_tool.adapters.excel_writer import ExcelOutputAdapter
from revenue_tool.adapters.regional_pivot import SOURCE_SHEETS, SUMMARY_SHEETS
from revenue_tool.config import load_config
from revenue_tool.domain.models import BaseRow, IssueLog
from revenue_tool.services.final_revenue import calculate_final_values
from revenue_tool.services.regional_summary import (
    build_regional_summary, EMPTY_REGION, EXCLUDED, LABELS, discover_months,
)
from tests.test_pipeline import CONFIG


def example_rows():
    # Every current segment and excluded-period condition; literal independent oracle.
    data = [
        ("A1", "A", "2026-08", "2026-09", "订未发", 100),
        ("A2", "A", "2026-09", "2026-08", "订未发", 20),
        ("A3", "A", "2026-09", "2026-09", "发未收", -5),
        ("A4", "A", "2026-09", "2026-09", "交未验", 0),
        ("A5", "A", "2026-09", "2026-09", "特殊处理", 7),
        ("OLD", "A", "2025-09", "2025-09", "订未发", 900),
        ("FUT", "A", "2026-10", "2026-10", "订未发", 800),
        ("NONE", "A", None, None, "订未发", 700),
        ("B1", "B", "2026-01", "2026-09", "发未收", 50),
        ("B2", "B", "2026-09", "2026-09", False, 3),
        ("EMPTY", None, "2026-09", "2026-09", "订未发", 4),
    ]
    result = []
    for contract, region, rpd, cpd, segment, amount in data:
        values = dict(contract_no=contract, supply_center="深供", region=region,
            revenue_month_rpd=rpd, revenue_month_cpd=cpd,
            revenue_segment=segment, revenue_forecast=Decimal(amount))
        values.update(calculate_final_values(values))
        result.append(BaseRow(values))
    return result


