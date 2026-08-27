from __future__ import annotations

from dataclasses import replace
from datetime import date
import unittest

from revenue_tool.domain.models import DEMAND_CENTER
from revenue_tool.domain.revenue_models import FulfillmentProjection
from revenue_tool.services.candidate_identity import (
    build_candidate_id,
    build_projection_fingerprint,
)


class CandidateIdentityTest(unittest.TestCase):
    def test_candidate_id_v1_frozen_vector(self) -> None:
        self.assertEqual(
            "RAC-v1-adadc699ea166aac0e020e8640d57a9a6e843fd59e454b6143d6be9109d1bf77",
            build_candidate_id(" C001 ", "SC-A", DEMAND_CENTER),
        )
        self.assertEqual(
            build_candidate_id("Ｃ００１", "ｓｃ－ａ", DEMAND_CENTER),
            build_candidate_id("C001", "SC-A", DEMAND_CENTER),
        )

    def test_projection_fingerprint_v1_frozen_vector_and_exclusions(self) -> None:
        projection = _projection()
        fingerprint = build_projection_fingerprint(projection)
        self.assertEqual(
            "FP-v1-ff8e0014d505880bb6ca23663bad2e3ba53948c6c63657d0a9f578d79b09fd4f",
            fingerprint,
        )
        trace_only = replace(
            projection,
            source_row_summary="renamed.xlsx/Sheet2!999",
            demand_record_ids=("different-run-id",),
        )
        self.assertEqual(fingerprint, build_projection_fingerprint(trace_only))

        changed = replace(projection, latest_rpd=date(2026, 2, 2))
        self.assertNotEqual(fingerprint, build_projection_fingerprint(changed))
        self.assertEqual(
            build_candidate_id(
                projection.contract_no,
                projection.supply_center or "",
                projection.row_kind,
            ),
            build_candidate_id(
                changed.contract_no,
                changed.supply_center or "",
                changed.row_kind,
            ),
        )


def _projection() -> FulfillmentProjection:
    return FulfillmentProjection(
        contract_no="C001",
        supply_center="SC-A",
        row_kind=DEMAND_CENTER,
        multiple_supply_centers="Y",
        demand_record_count=2,
        demand_status_summary="有效 | 待确认 | 有效",
        source_row_summary="source.xlsx/Sheet1!3 | source.xlsx/Sheet1!8",
        demand_record_ids=("DR-1", "DR-2"),
        ata_values=(),
        asd_values=(date(2026, 1, 2),),
        rpd_values=(date(2026, 1, 5), date(2026, 1, 10)),
        cpd_values=(date(2026, 2, 1),),
        incoterm="cif",
        stock_unlocked="部分解锁",
        split_shipment="Y",
        transit_days=30,
        ata=None,
        asd=date(2026, 1, 2),
        rpd=date(2026, 1, 5),
        multiple_demand="Y",
        latest_asd=date(2026, 1, 2),
        latest_rpd=date(2026, 1, 10),
        shipment_incomplete="Y",
        cpd=date(2026, 2, 1),
        split_supply="Y",
        arrival_date_rpd=date(2026, 2, 9),
        arrival_date_cpd=date(2026, 3, 3),
        revenue_month_rpd="2026-02",
        revenue_month_cpd="2026-03",
        revenue_segment="需判断",
        issue_codes=("B", "A", "A"),
    )


if __name__ == "__main__":
    unittest.main()
