from __future__ import annotations

from revenue_tool.domain.models import DEMAND_CENTER, IssueLog
from revenue_tool.domain.revenue_models import (
    CANDIDATE_ID_VERSION,
    MANUAL_AMOUNT_BLANK,
    PROJECTION_FINGERPRINT_VERSION,
    FulfillmentProjection,
    ManualAllocationSnapshot,
    RevenueAllocationCandidate,
)
from revenue_tool.services.candidate_identity import (
    build_candidate_id,
    build_projection_fingerprint,
)
from revenue_tool.services.normalization import nonblank, normalize_lookup


class AllocationCandidateBuilder:
    def build(
        self,
        projections: list[FulfillmentProjection]
        | tuple[FulfillmentProjection, ...],
        issues: IssueLog,
    ) -> list[RevenueAllocationCandidate]:
        candidates: list[RevenueAllocationCandidate] = []
        identities: dict[str, tuple[str, str, str]] = {}
        for projection in projections:
            if projection.row_kind != DEMAND_CENTER:
                continue
            if not nonblank(projection.contract_no) or not nonblank(
                projection.supply_center
            ):
                issues.add(
                    "INVALID_ALLOCATION_CANDIDATE_KEY",
                    "履行投影缺少合同号或履行供应中心，不能生成分配候选",
                    business_key=projection.contract_no,
                    field="supply_center",
                    raw_value=projection.supply_center,
                )
                continue
            supply_center = str(projection.supply_center)
            candidate_id = build_candidate_id(
                projection.contract_no,
                supply_center,
                projection.row_kind,
            )
            business_key = (
                projection.contract_no,
                normalize_lookup(supply_center),
                projection.row_kind,
            )
            previous_key = identities.get(candidate_id)
            if previous_key is not None:
                issues.add(
                    "CANDIDATE_ID_COLLISION",
                    "同一运行生成重复分配候选ID，候选已排除",
                    severity="ERROR",
                    business_key=f"{projection.contract_no} | {supply_center}",
                    field="allocation_candidate_id",
                    raw_value=candidate_id,
                )
                continue
            identities[candidate_id] = business_key
            blank = ManualAllocationSnapshot(MANUAL_AMOUNT_BLANK)
            candidates.append(
                RevenueAllocationCandidate(
                    allocation_candidate_id=candidate_id,
                    candidate_id_version=CANDIDATE_ID_VERSION,
                    contract_no=projection.contract_no,
                    supply_center=supply_center,
                    row_kind=projection.row_kind,
                    projection_fingerprint=build_projection_fingerprint(
                        projection
                    ),
                    projection_fingerprint_version=(
                        PROJECTION_FINGERPRINT_VERSION
                    ),
                    fulfillment_projection=projection,
                    previous_manual_allocation=blank,
                    manual_allocation=blank,
                )
            )
        return sorted(
            candidates,
            key=lambda item: (
                normalize_lookup(item.contract_no),
                normalize_lookup(item.supply_center),
            ),
        )
