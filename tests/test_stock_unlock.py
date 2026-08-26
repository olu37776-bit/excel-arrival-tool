from __future__ import annotations

import unittest

from revenue_tool.services.stock_unlock import aggregate_stock_unlock


class StockUnlockTest(unittest.TestCase):
    def test_documented_three_state_matrix(self) -> None:
        cases = (
            (["Y"], "未解锁"),
            (["Y", "Y"], "未解锁"),
            (["N"], "已解锁"),
            (["N", "N"], "已解锁"),
            (["Y", "N"], "部分解锁"),
            (["N", "N", "Y"], "部分解锁"),
            ([], None),
            ([None, "", "(空白)", "VALUE", "非法"], None),
        )
        for values, expected in cases:
            with self.subTest(values=values):
                self.assertEqual(expected, aggregate_stock_unlock(values))

    def test_invalid_values_do_not_pollute_valid_flag_set(self) -> None:
        self.assertEqual(
            "未解锁",
            aggregate_stock_unlock(["非法", "Y", "VALUE", None]),
        )


if __name__ == "__main__":
    unittest.main()
