from datetime import date
from pathlib import Path
import unittest

from revenue_tool.config import load_config
from revenue_tool.domain.models import IssueLog, ParsedRow, SourceData
from revenue_tool.services.data_quality import DataQualityAnalyzer


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "default.json"


class DataQualityTest(unittest.TestCase):
    def test_parseable_text_date_is_reported_as_storage_type_risk(self) -> None:
        demand = ParsedRow(
            role="demand_detail",
            workbook="demand.xlsx",
            sheet="要货明细",
            row_number=3,
            values={
                "contract_no": "C1",
                "country": "中国",
                "customer_group": "客户群",
                "supply_center": "SC1",
                "incoterm": "EXW",
                "stock_control_flag": "Y",
                "shipment_control_flag": "Y",
                "ata": None,
                "asd": None,
                "rpd": date(2026, 8, 1),
                "cpd": None,
            },
            raw_values={"rpd": "2026-08-01"},
        )
        source = SourceData(
            {
                "legacy": Path("legacy.xlsx"),
                "monthly_order": Path("monthly.xlsx"),
                "demand_detail": Path("demand.xlsx"),
                "transit": Path("transit.xlsx"),
            },
            {
                "legacy": [],
                "monthly_order": [],
                "demand_detail": [demand],
                "transit": [],
            },
            {},
        )
        issues = IssueLog()

        DataQualityAnalyzer().analyze(source, load_config(CONFIG), issues)

        self.assertEqual(1, len(issues.items))
        self.assertEqual("DATE_STORAGE_TYPE_UNEXPECTED", issues.items[0].code)
        self.assertEqual(3, issues.items[0].row_number)


if __name__ == "__main__":
    unittest.main()
