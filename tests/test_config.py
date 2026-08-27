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
        data["output"]["datasets"]["issues"]["sheet"] = data["output"][
            "datasets"
        ]["allocation"]["sheet"]

        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "invalid.json"
            path.write_text(
                json.dumps(data, ensure_ascii=False), encoding="utf-8"
            )

            with self.assertRaisesRegex(ValueError, "Sheet 显示名必须唯一"):
                load_config(path)

    def test_sheet_required_fields_must_reference_role_fields(self) -> None:
        data = json.loads(CONFIG.read_text(encoding="utf-8"))
        data["sheets"]["monthly_order"]["required_fields"] = [
            "contract_no",
            "unknown_field",
        ]

        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "invalid.json"
            path.write_text(
                json.dumps(data, ensure_ascii=False), encoding="utf-8"
            )

            with self.assertRaisesRegex(ValueError, "required_fields"):
                load_config(path)

    def test_only_monthly_order_source_may_be_optional(self) -> None:
        data = json.loads(CONFIG.read_text(encoding="utf-8"))
        data["sheets"]["legacy"]["optional"] = True

        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "invalid.json"
            path.write_text(
                json.dumps(data, ensure_ascii=False), encoding="utf-8"
            )

            with self.assertRaisesRegex(ValueError, "仅 monthly_order 可选"):
                load_config(path)


if __name__ == "__main__":
    unittest.main()
