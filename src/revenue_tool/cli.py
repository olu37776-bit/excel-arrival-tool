from __future__ import annotations

import argparse
from pathlib import Path
import sys

from revenue_tool.application.pipeline import run_pipeline
from revenue_tool.domain.models import WorkbookReadError


def build_parser() -> argparse.ArgumentParser:
    project_root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(
        description="按需求基线生成到货日期、收入月份和跨月变化工作簿"
    )
    parser.add_argument("--legacy", required=True, help="遗留量 Excel 路径")
    parser.add_argument(
        "--monthly-order", required=True, help="当月订货 Excel 路径"
    )
    parser.add_argument(
        "--demand-detail", required=True, help="要货明细 Excel 路径"
    )
    parser.add_argument(
        "--transit", required=True, help="国家运输周期 Excel 路径"
    )
    parser.add_argument("--output", required=True, help="结果 Excel 路径")
    parser.add_argument(
        "--previous",
        help="可选：上一次成功运行结果，用于人工字段继承和跨月比较",
    )
    parser.add_argument(
        "--config",
        default=str(project_root / "config" / "default.json"),
        help="字段映射与规则配置 JSON",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = run_pipeline(
            legacy_path=args.legacy,
            monthly_order_path=args.monthly_order,
            demand_detail_path=args.demand_detail,
            transit_path=args.transit,
            output_path=args.output,
            config_path=args.config,
            previous_path=args.previous,
        )
    except (WorkbookReadError, ValueError, OSError) as exc:
        print(f"执行失败: {exc}", file=sys.stderr)
        return 2
    print(f"结果文件: {result.output_path}")
    print(f"基表行数: {result.base_count}")
    print(f"RPD跨月变化: {result.rpd_change_count}")
    print(f"CPD跨月变化: {result.cpd_change_count}")
    print(f"供应需要提拉诉求: {result.supply_pull_count}")
    print(f"异常记录: {result.issue_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
