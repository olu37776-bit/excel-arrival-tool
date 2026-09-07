from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys

from revenue_tool.config import load_config


def default_config_path() -> Path:
    """Return the bundled config path for source and frozen builds."""
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS")) / "config" / "default.json"
    return Path(__file__).resolve().parents[2] / "config" / "default.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Excel tool graphical launcher")
    parser.add_argument(
        "--config",
        default=str(default_config_path()),
        help="Configuration JSON path (defaults to the bundled configuration)",
    )
    parser.add_argument("--smoke-test", action="store_true", help=argparse.SUPPRESS)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.smoke_test:
        import tkinter  # noqa: F401 - verifies the frozen GUI runtime
        from tempfile import TemporaryDirectory
        from openpyxl import load_workbook
        from revenue_tool.adapters.excel_writer import ExcelOutputAdapter
        from revenue_tool.adapters.regional_pivot import SUMMARY_SHEETS
        from revenue_tool.domain.models import BaseRow, IssueLog
        from revenue_tool.services.final_revenue import calculate_final_values

        config = load_config(args.config)
        values = dict(contract_no="SMOKE", region="测试地区", supply_center="深供",
                      revenue_month_rpd="2026-09", revenue_month_cpd="2026-09",
                      revenue_segment="订未发", revenue_forecast=1)
        values.update(calculate_final_values(values))
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "smoke.xlsx"
            ExcelOutputAdapter().write(path, [BaseRow(values)], [], [], [], IssueLog(), config)
            workbook = load_workbook(path)
            try:
                for name in SUMMARY_SHEETS.values():
                    sheet = workbook[name]
                    if len(sheet._pivots) != 1 or sheet["F10"].value != 1:
                        raise RuntimeError("Windows EXE透视工作簿自检失败")
            finally:
                workbook.close()
            workbook = load_workbook(path, data_only=True)
            try:
                base = workbook[config.output["sheets"]["base"]]
                indexes = {c["id"]: i for i, c in enumerate(config.base_columns, 1)}
                for field, expected in calculate_final_values(values).items():
                    if base.cell(2, indexes[field]).value != expected:
                        raise RuntimeError("Windows EXE最终字段计算值自检失败")
            finally:
                workbook.close()
        if sys.platform == 'win32' or os.environ.get('DISPLAY'):
            from revenue_tool.gui_app import RevenueApp
            root = tkinter.Tk()
            try:
                app = RevenueApp(root, args.config)
                root.update()
                if hasattr(app, 'months') or hasattr(app, 'year'):
                    raise RuntimeError('GUI不应包含月份选择')
            finally:
                root.destroy()
        return 0

    try:
        import tkinter as tk
        from tkinter import filedialog, messagebox, ttk
    except ImportError:
        print(
            "Tkinter is unavailable. Reinstall Python from python.org with "
            "the Tcl/Tk option enabled.",
            file=sys.stderr,
        )
        return 2

    from revenue_tool.gui_app import RevenueApp
    root = tk.Tk()
    RevenueApp(root, args.config)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
