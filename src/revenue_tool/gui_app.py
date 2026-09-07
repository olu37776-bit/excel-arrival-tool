"""Responsive desktop form. Worker threads never access Tk objects."""
from datetime import date, datetime
from pathlib import Path
from queue import Empty, Queue
import os
import subprocess
import sys
from threading import Thread
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from revenue_tool import __version__
from revenue_tool.application.pipeline import run_pipeline
from revenue_tool.services.regional_summary import report_months


class RevenueApp:
    def __init__(self, root, config_path, runner=run_pipeline):
        self.root, self.config_path, self.runner = root, Path(config_path), runner
        self.events = Queue()
        self.busy = False
        self.last_output = None
        self.controls = []
        today = date.today()
        root.title(f"Excel 收入统计工具 · v{__version__}")
        root.geometry('940x740')
        root.minsize(860, 680)
        root.configure(background='#F3F5F8')
        root.columnconfigure(0, weight=1)
        root.rowconfigure(1, weight=1)
        root.option_add('*Font', ('Microsoft YaHei UI', 10))
        style = ttk.Style(root)
        if 'clam' in style.theme_names():
            style.theme_use('clam')
        style.configure('Card.TFrame', background='white')
        style.configure('Card.TLabel', background='white', foreground='#24344B')
        style.configure('Hint.TLabel', background='white', foreground='#68768A', font=('Microsoft YaHei UI', 9))
        style.configure('Title.TLabel', background='white', foreground='#163F72', font=('Microsoft YaHei UI', 11, 'bold'))
        style.configure('TButton', padding=(10, 5))
        style.configure('Primary.TButton', padding=(20, 9), foreground='white', background='#245CA6', font=('Microsoft YaHei UI', 11, 'bold'))
        style.map('Primary.TButton', background=[('active', '#194B8B'), ('disabled', '#A8B4C4')])
        style.configure('Month.TCheckbutton', background='white', padding=(8, 3))

        header = tk.Frame(root, background='#173D68', padx=24, pady=14)
        header.grid(row=0, column=0, sticky='ew')
        tk.Label(header, text='Excel 收入统计', background='#173D68', foreground='white',
                 font=('Microsoft YaHei UI', 18, 'bold')).pack(anchor='w')
        tk.Label(header, text='选择数据 → 勾选月份 → 生成结果', background='#173D68',
                 foreground='#D5E3F5', font=('Microsoft YaHei UI', 10)).pack(anchor='w', pady=(4, 0))
        viewport = tk.Frame(root, background='#F3F5F8')
        viewport.grid(row=1, column=0, sticky='nsew')
        viewport.columnconfigure(0, weight=1)
        viewport.rowconfigure(0, weight=1)
        canvas = tk.Canvas(viewport, background='#F3F5F8', highlightthickness=0)
        canvas.grid(row=0, column=0, sticky='nsew')
        scroll = ttk.Scrollbar(viewport, orient='vertical', command=canvas.yview)
        scroll.grid(row=0, column=1, sticky='ns')
        canvas.configure(yscrollcommand=scroll.set)
        body = tk.Frame(canvas, background='#F3F5F8', padx=20, pady=12)
        window = canvas.create_window(0, 0, window=body, anchor='nw')
        canvas.bind('<Configure>', lambda event: canvas.itemconfigure(window, width=event.width))
        body.bind('<Configure>', lambda event: canvas.configure(scrollregion=canvas.bbox('all')))
        body.columnconfigure(0, weight=1)
        self.variables = {key: tk.StringVar() for key in
                          ('legacy', 'demand_detail', 'transit', 'monthly_order', 'previous', 'output')}
        self.year = tk.StringVar(value=str(today.year))
        self.months = {m: tk.BooleanVar(value=m == today.month) for m in range(1, 13)}

        files = self.card(body, 0, '1  选择数据文件')
        files.columnconfigure(1, weight=1)
        for number, (key, label) in enumerate((
            ('legacy', '遗留量 · 必选'), ('demand_detail', '要货明细 · 必选'),
            ('transit', '国家运输周期 · 必选'), ('monthly_order', '当月订货 · 可选'),
            ('previous', '上一次结果 · 可选'),
        ), 1):
            ttk.Label(files, text=label, style='Card.TLabel').grid(row=number, column=0, sticky='w', padx=(0, 14), pady=4)
            entry = ttk.Entry(files, textvariable=self.variables[key])
            entry.grid(row=number, column=1, sticky='ew', pady=4)
            button = ttk.Button(files, text='浏览…', command=lambda field=key: self.select_input(field))
            button.grid(row=number, column=2, padx=(10, 0), pady=4)
            self.controls.extend((entry, button))
        ttk.Label(files, text='首次生成可不选上一次结果；旧版结果可用于继承人工调整和跨月比较。',
                  style='Hint.TLabel').grid(row=6, column=0, columnspan=3, sticky='w', pady=(5, 0))

        period = self.card(body, 1, '2  选择汇总月份（可多选）')
        period.columnconfigure(0, weight=1)
        toolbar = ttk.Frame(period, style='Card.TFrame')
        toolbar.grid(row=1, column=0, sticky='ew', pady=(8, 3))
        ttk.Label(toolbar, text='年份', style='Card.TLabel').pack(side='left', padx=(0, 10))
        year_box = ttk.Combobox(toolbar, textvariable=self.year, width=8,
                               values=[str(y) for y in range(today.year - 10, today.year + 6)])
        year_box.pack(side='left')
        self.controls.append(year_box)
        for label, command in [('本月', self.select_current), ('全年', lambda: self.set_months(range(1, 13))),
                               ('清空', lambda: self.set_months(()))]:
            button = ttk.Button(toolbar, text=label, command=command)
            button.pack(side='right', padx=(8, 0))
            self.controls.append(button)
        checks = ttk.Frame(period, style='Card.TFrame')
        checks.grid(row=2, column=0, sticky='ew')
        for m, value in self.months.items():
            checks.columnconfigure((m - 1) % 6, weight=1)
            box = ttk.Checkbutton(checks, text=f'{m:02d}月', variable=value, style='Month.TCheckbutton')
            box.grid(row=(m - 1) // 6, column=(m - 1) % 6, sticky='w')
            self.controls.append(box)
        self.selection_text = tk.StringVar()
        for value in self.months.values():
            value.trace_add('write', self.update_selection)
        self.year.trace_add('write', self.update_selection)
        ttk.Label(period, textvariable=self.selection_text, style='Hint.TLabel').grid(row=3, column=0, sticky='w', pady=(4, 0))
        self.update_selection()

        output = self.card(body, 2, '3  保存结果')
        output.columnconfigure(0, weight=1)
        entry = ttk.Entry(output, textvariable=self.variables['output'])
        entry.grid(row=1, column=0, sticky='ew', pady=(8, 0))
        button = ttk.Button(output, text='另存为…', command=self.select_output)
        button.grid(row=1, column=1, padx=(10, 0), pady=(8, 0))
        self.controls.extend((entry, button))
        footer = tk.Frame(root, background='#F3F5F8', padx=20, pady=10)
        footer.grid(row=2, column=0, sticky='ew')
        footer.columnconfigure(0, weight=1)
        self.status = tk.StringVar(value='准备就绪：请选择源文件。')
        ttk.Label(footer, textvariable=self.status, background='#F3F5F8', wraplength=820).grid(row=0, column=0, sticky='w', pady=(0, 5))
        self.progress = ttk.Progressbar(footer, mode='indeterminate')
        self.progress.grid(row=1, column=0, sticky='ew', pady=(0, 8))
        actions = tk.Frame(footer, background='#F3F5F8')
        actions.grid(row=2, column=0, sticky='ew')
        self.open_button = ttk.Button(actions, text='打开结果', command=self.open_result, state='disabled')
        self.open_button.pack(side='left')
        self.folder_button = ttk.Button(actions, text='打开所在文件夹', command=lambda: self.open_result(folder=True), state='disabled')
        self.folder_button.pack(side='left', padx=(8, 0))
        self.run_button = ttk.Button(actions, text='开始生成', command=self.execute, style='Primary.TButton')
        self.run_button.pack(side='right')
        self.controls.append(self.run_button)
        self.closed = False
        self.poll_id = root.after(100, self.poll)
        root.bind('<Destroy>', self.on_destroy, add='+')

    def on_destroy(self, event):
        if event.widget is self.root:
            self.closed = True
            self.root.after_cancel(self.poll_id)

    def card(self, parent, row, title):
        frame = ttk.Frame(parent, padding=(14, 10), style='Card.TFrame')
        frame.grid(row=row, column=0, sticky='ew', pady=(0, 9))
        ttk.Label(frame, text=title, style='Title.TLabel').grid(row=0, column=0, columnspan=3, sticky='w')
        return frame

    def set_months(self, selected):
        for month, value in self.months.items():
            value.set(month in selected)

    def select_current(self):
        today = date.today()
        self.year.set(str(today.year))
        self.set_months((today.month,))

    def selected_months(self):
        year = self.year.get().strip()
        if len(year) != 4 or not year.isascii() or not year.isdigit() or int(year) == 0:
            raise ValueError('请选择或输入四位年份，例如2026。')
        return report_months([f'{year}-{m:02d}' for m, value in self.months.items() if value.get()])

    def update_selection(self, *_):
        try:
            months = self.selected_months()
            self.selection_text.set(f'已选 {len(months)} 个月 · 生成 {len(months) * 2} 张汇总表；每月分别计算前期累计和当月。')
        except ValueError as exc:
            self.selection_text.set(str(exc))

    def select_input(self, field):
        path = filedialog.askopenfilename(parent=self.root, title='选择 Excel 文件',
                    filetypes=[('Excel 工作簿', '*.xlsx *.xlsm')])
        if path:
            self.variables[field].set(path)
            if not self.variables['output'].get():
                name = datetime.now().strftime('收入统计_%Y%m%d_%H%M%S.xlsx')
                self.variables['output'].set(str(Path(path).parent / name))

    def select_output(self):
        selected = filedialog.asksaveasfilename(parent=self.root, defaultextension='.xlsx',
                    filetypes=[('Excel 工作簿', '*.xlsx')], initialfile='收入统计.xlsx')
        if selected:
            self.variables['output'].set(selected)

    def execute(self):
        if self.busy:
            return
        try:
            months = self.selected_months()
            values = {key: value.get().strip() for key, value in self.variables.items()}
            for key, label in [('legacy', '遗留量'), ('demand_detail', '要货明细'), ('transit', '国家运输周期')]:
                if not values[key]:
                    raise ValueError(f'请选择{label}文件。')
            for key in ('legacy', 'demand_detail', 'transit', 'monthly_order', 'previous'):
                if values[key] and not Path(values[key]).is_file():
                    raise ValueError(f'文件不存在：{values[key]}')
            if not values['output'] or Path(values['output']).suffix.lower() != '.xlsx':
                raise ValueError('请选择以 .xlsx 结尾的结果保存位置。')
        except ValueError as exc:
            messagebox.showerror('请检查选择', str(exc), parent=self.root)
            return
        self.busy = True
        for control in self.controls:
            control.state(['disabled'])
        self.open_button.state(['disabled'])
        self.folder_button.state(['disabled'])
        self.status.set(f'正在生成 {len(months)} 个月的结果，请稍候……')
        self.progress.start(12)

        def work():
            try:
                result = self.runner(legacy_path=values['legacy'], monthly_order_path=values['monthly_order'] or None,
                    demand_detail_path=values['demand_detail'], transit_path=values['transit'],
                    output_path=values['output'], config_path=self.config_path,
                    previous_path=values['previous'] or None, report_month=months)
                self.events.put(('success', result, len(months)))
            except Exception as exc:
                self.events.put(('error', exc, 0))
        Thread(target=work, daemon=True, name='revenue-generation').start()

    def poll(self):
        if self.closed:
            return
        try:
            kind, result, count = self.events.get_nowait()
        except Empty:
            pass
        else:
            self.busy = False
            self.progress.stop()
            for control in self.controls:
                control.state(['!disabled'])
            if kind == 'success':
                self.last_output = result.output_path
                self.status.set(f'生成完成 · 基表 {result.base_count} 行 · {count * 2} 张汇总表 · 异常记录 {result.issue_count} 条')
                self.open_button.state(['!disabled'])
                self.folder_button.state(['!disabled'])
            else:
                self.status.set('生成失败，请检查提示后重试。')
                messagebox.showerror('生成失败', str(result), parent=self.root)
        self.poll_id = self.root.after(100, self.poll)

    def open_result(self, folder=False):
        if self.last_output is None:
            return
        path = Path(self.last_output)
        if folder:
            path = path.parent
        try:
            if sys.platform == 'win32':
                os.startfile(str(path))
            else:
                subprocess.Popen(['open' if sys.platform == 'darwin' else 'xdg-open', str(path)])
        except OSError as exc:
            messagebox.showerror('无法打开', str(exc), parent=self.root)
