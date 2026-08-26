from __future__ import annotations

import argparse
from pathlib import Path
import sys

from revenue_tool.application.pipeline import run_pipeline
from revenue_tool.config import load_config
from revenue_tool.domain.models import WorkbookReadError


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

        load_config(args.config)
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

    root = tk.Tk()
    root.title("Excel 收入统计工具")
    root.minsize(780, 410)
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    frame = ttk.Frame(root, padding=18)
    frame.grid(row=0, column=0, sticky="nsew")
    frame.columnconfigure(1, weight=1)

    ttk.Label(
        frame,
        text="请选择四个源文件和结果保存位置",
        font=("Microsoft YaHei UI", 13, "bold"),
    ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 12))

    variables = {
        "legacy": tk.StringVar(),
        "monthly_order": tk.StringVar(),
        "demand_detail": tk.StringVar(),
        "transit": tk.StringVar(),
        "output": tk.StringVar(),
        "previous": tk.StringVar(),
    }
    source_types = [("Excel files", "*.xlsx *.xlsm"), ("All files", "*.*")]

    def select_input(field: str) -> None:
        selected = filedialog.askopenfilename(filetypes=source_types)
        if selected:
            variables[field].set(selected)

    def select_output() -> None:
        selected = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel workbook", "*.xlsx")],
            initialfile="result.xlsx",
        )
        if selected:
            variables["output"].set(selected)

    fields = [
        ("遗留量 Excel", "legacy", False),
        ("当月订货 Excel（可选）", "monthly_order", False),
        ("要货明细 Excel", "demand_detail", False),
        ("国家运输周期 Excel", "transit", False),
        ("结果保存位置", "output", True),
        ("上一次成功结果（可选）", "previous", False),
    ]
    for row, (label, field, is_output) in enumerate(fields, start=1):
        ttk.Label(frame, text=label).grid(
            row=row, column=0, sticky="w", padx=(0, 10), pady=5
        )
        ttk.Entry(frame, textvariable=variables[field]).grid(
            row=row, column=1, sticky="ew", pady=5
        )
        command = select_output if is_output else lambda name=field: select_input(name)
        ttk.Button(frame, text="选择…", command=command).grid(
            row=row, column=2, padx=(10, 0), pady=5
        )

    ttk.Label(
        frame,
        text="第一次运行不用选择上一次结果；后续需要继承和跨期比较时再选择。",
        foreground="#555555",
    ).grid(row=7, column=0, columnspan=3, sticky="w", pady=(8, 4))

    status = tk.StringVar(value="等待选择文件")
    ttk.Label(frame, textvariable=status).grid(
        row=8, column=0, columnspan=3, sticky="w", pady=(8, 8)
    )

    def execute() -> None:
        required = {
            "遗留量 Excel": variables["legacy"].get().strip(),
            "要货明细 Excel": variables["demand_detail"].get().strip(),
            "国家运输周期 Excel": variables["transit"].get().strip(),
            "结果保存位置": variables["output"].get().strip(),
        }
        missing = [label for label, value in required.items() if not value]
        if missing:
            messagebox.showerror("缺少文件", "请先选择：" + "、".join(missing))
            return

        run_button.state(["disabled"])
        status.set("正在读取和生成，请稍候……")
        root.update_idletasks()
        try:
            previous = variables["previous"].get().strip() or None
            result = run_pipeline(
                legacy_path=variables["legacy"].get().strip(),
                monthly_order_path=(
                    variables["monthly_order"].get().strip() or None
                ),
                demand_detail_path=variables["demand_detail"].get().strip(),
                transit_path=variables["transit"].get().strip(),
                output_path=variables["output"].get().strip(),
                config_path=Path(args.config),
                previous_path=previous,
            )
        except (WorkbookReadError, ValueError, OSError) as exc:
            status.set("生成失败")
            messagebox.showerror("执行失败", str(exc))
        except Exception as exc:  # keep the window open for unexpected failures
            status.set("生成失败")
            messagebox.showerror("未预期错误", f"{type(exc).__name__}: {exc}")
        else:
            status.set(f"生成完成：{result.output_path}")
            messagebox.showinfo(
                "生成完成",
                "\n".join(
                    [
                        f"结果文件：{result.output_path}",
                        f"基表行数：{result.base_count}",
                        f"RPD 跨月变化：{result.rpd_change_count}",
                        f"CPD 跨月变化：{result.cpd_change_count}",
                        f"供应需要提拉诉求：{result.supply_pull_count}",
                        f"异常记录：{result.issue_count}",
                    ]
                ),
            )
        finally:
            run_button.state(["!disabled"])

    button_frame = ttk.Frame(frame)
    button_frame.grid(row=9, column=0, columnspan=3, sticky="e", pady=(8, 0))
    ttk.Button(button_frame, text="退出", command=root.destroy).pack(
        side="right", padx=(8, 0)
    )
    run_button = ttk.Button(button_frame, text="开始生成", command=execute)
    run_button.pack(side="right")

    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
