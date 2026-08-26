import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from revenue_tool.config import load_config


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "default.json"


class ConfigTest(unittest.TestCase):
    def test_missing_stable_field_id_is_rejected(self) -> None:
        data = json.loads(CONFIG.read_text(encoding="utf-8"))
        del data["fields"]["demand_detail"]["stock_control_flag"]

        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "invalid.json"
            path.write_text(
                json.dumps(data, ensure_ascii=False), encoding="utf-8"
            )

            with self.assertRaisesRegex(ValueError, "稳定内部字段 ID"):
                load_config(path)

    def test_duplicate_output_sheet_name_is_rejected(self) -> None:
        data = json.loads(CONFIG.read_text(encoding="utf-8"))
        data["output"]["sheets"]["issues"] = data["output"]["sheets"][
            "base"
        ]

        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "invalid.json"
            path.write_text(
                json.dumps(data, ensure_ascii=False), encoding="utf-8"
            )

            with self.assertRaisesRegex(ValueError, "输出 Sheet"):
                load_config(path)

    def test_empty_stock_flag_delimiter_is_rejected(self) -> None:
        data = json.loads(CONFIG.read_text(encoding="utf-8"))
        data["rules"]["stock_flag_delimiter"] = ""

        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "invalid.json"
            path.write_text(
                json.dumps(data, ensure_ascii=False), encoding="utf-8"
            )

            with self.assertRaisesRegex(ValueError, "必须为非空字符串"):
                load_config(path)


if __name__ == "__main__":
    unittest.main()
