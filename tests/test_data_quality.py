from datetime import date
from pathlib import Path
import unittest

from revenue_tool.domain.models import IssueLog, ParsedRow, SourceData
from revenue_tool.services.data_quality import DataQualityAnalyzer


class DataQualityTest(unittest.TestCase):
    def test_parseable_text_date_and_blank_text_are_not_issues(self) -> None:
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

        DataQualityAnalyzer().analyze(source, issues)

        self.assertEqual([], issues.items)


if __name__ == "__main__":
    unittest.main()
