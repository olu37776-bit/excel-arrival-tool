import unittest

from revenue_tool.services.field_matching import resolve_name


class FieldMatchingTest(unittest.TestCase):
    def test_nfkc_whitespace_and_case_are_exact(self) -> None:
        result = resolve_name(
            "BG_CN",
            [],
            [" BG＿CN\t"],
        )
        self.assertEqual("exact", result.mode)
        self.assertEqual(0, result.index)

    def test_unique_contains_is_used_only_after_exact_miss(self) -> None:
        result = resolve_name(
            "原合同号",
            [],
            ["原合同号（文本）", "项目名称"],
        )
        self.assertEqual("contains", result.mode)
        self.assertEqual(0, result.index)

    def test_multiple_contains_candidates_are_ambiguous(self) -> None:
        result = resolve_name(
            "国家",
            [],
            ["国家中文名称", "目标国家"],
        )
        self.assertEqual("ambiguous", result.mode)
        self.assertIsNone(result.index)
        self.assertEqual((0, 1), result.candidates)


if __name__ == "__main__":
    unittest.main()

