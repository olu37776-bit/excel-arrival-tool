from pathlib import Path

from revenue_tool.gui import build_parser, default_config_path


def test_gui_uses_default_config_path_when_not_overridden() -> None:
    config_path = Path(build_parser().parse_args([]).config)

    assert config_path == default_config_path()
    assert config_path.parts[-2:] == ("config", "default.json")


def test_gui_accepts_explicit_config() -> None:
    assert build_parser().parse_args(["--config", "custom.json"]).config == "custom.json"
