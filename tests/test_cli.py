import unittest

from revenue_tool.cli import build_parser


class CliTest(unittest.TestCase):
    def test_monthly_order_cli_argument_is_optional(self) -> None:
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

        self.assertIsNone(args.monthly_order)


if __name__ == "__main__":
    unittest.main()
