from __future__ import annotations

import argparse
import sys
from pathlib import Path

from revenue_tool.application.pipeline import run_pipeline
from revenue_tool.domain.errors import RevenueToolError
from revenue_tool.template import create_template


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="revenue-tool",
        description="Calculate arrival-based monthly revenue statistics from Excel.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    run = subparsers.add_parser("run", help="Generate revenue statistics")
    run.add_argument("--input", required=True, help="Input Excel workbook")
    run.add_argument("--output", required=True, help="Output Excel workbook")
    run.add_argument(
        "--previous",
        help="Previous output workbook used to identify revenue delayed by a month or more",
    )
    run.add_argument("--config", default="config", help="Configuration directory")

    template = subparsers.add_parser("template", help="Create an empty input template")
    template.add_argument("--output", required=True, help="Template output path")
    template.add_argument("--config", default="config", help="Configuration directory")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "template":
            path = create_template(args.output, args.config)
            print(f"Template created: {path}")
            return 0
        result = run_pipeline(
            input_path=args.input,
            output_path=args.output,
            config_dir=args.config,
            previous_path=args.previous,
        )
        print(f"Output created: {result.output_path}")
        print(f"Revenue detail rows: {result.revenue_detail_count}")
        print(f"Revenue summary rows: {result.revenue_summary_count}")
        print(f"Delayed by >= configured threshold: {result.delayed_count}")
        return 0
    except (RevenueToolError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

