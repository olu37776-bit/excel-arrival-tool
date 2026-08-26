from pathlib import Path
import unittest

from revenue_tool.gui import build_parser, default_config_path, main


class GuiTest(unittest.TestCase):
    def test_gui_uses_default_config_path_when_not_overridden(self) -> None:
        config_path = Path(build_parser().parse_args([]).config)

        self.assertEqual(default_config_path(), config_path)
        self.assertEqual(("config", "default.json"), config_path.parts[-2:])

    def test_gui_accepts_explicit_config(self) -> None:
        self.assertEqual(
            "custom.json",
            build_parser().parse_args(["--config", "custom.json"]).config,
        )

    def test_gui_smoke_test_loads_default_config(self) -> None:
        self.assertEqual(
            0,
            main(
                [
                    "--smoke-test",
                    "--config",
                    str(Path("config/default.json")),
                ]
            ),
        )


if __name__ == "__main__":
    unittest.main()
