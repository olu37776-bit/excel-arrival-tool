from revenue_tool.cli import build_parser


def test_monthly_order_cli_argument_is_optional() -> None:
    args = build_parser().parse_args(
        [
            "--legacy",
            "legacy.xlsx",
            "--demand-detail",
            "demand.xlsx",
            "--transit",
            "transit.xlsx",
            "--output",
            "result.xlsx",
        ]
    )

    assert args.monthly_order is None
