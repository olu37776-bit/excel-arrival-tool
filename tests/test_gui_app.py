from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Event
from types import SimpleNamespace
import time
import tkinter as tk
import unittest
from unittest.mock import patch

from revenue_tool.gui_app import RevenueApp
from tests.test_pipeline import CONFIG


class DesktopFormTest(unittest.TestCase):
    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError:
            self.skipTest('GUI tests run with Xvfb on Linux and native Tk on Windows')
        self.addCleanup(self.root.destroy)

    def pump_until(self, condition):
        deadline = time.monotonic() + 5
        while not condition():
            self.root.update()
            if time.monotonic() > deadline:
                self.fail('GUI event delivery timed out')
            time.sleep(.01)

    def test_default_multiple_months_and_visible_actions(self):
        app = RevenueApp(self.root, CONFIG)
        self.root.update()
        self.assertEqual((date.today().strftime('%Y-%m'),), app.selected_months())
        app.year.set('2026')
        app.set_months((8, 9))
        self.assertEqual(('2026-08', '2026-09'), app.selected_months())
        self.assertIn('4 张', app.selection_text.get())
        app.set_months(())
        with self.assertRaises(ValueError):
            app.selected_months()
        app.select_current()
        self.assertEqual((date.today().strftime('%Y-%m'),), app.selected_months())
        bottom = app.run_button.winfo_rooty() + app.run_button.winfo_height()
        self.assertLessEqual(bottom, self.root.winfo_rooty() + self.root.winfo_height(),
                             f'Generate button below window: {bottom}, required={self.root.winfo_reqheight()}')

    def test_background_generation_keeps_ui_responsive_and_restores_controls(self):
        started, finish = Event(), Event()
        received = []
        def runner(**kwargs):
            received.append(kwargs)
            started.set()
            if not finish.wait(5):
                raise RuntimeError('Test worker timed out')
            return SimpleNamespace(output_path=Path(kwargs['output_path']), base_count=7, issue_count=1)
        app = RevenueApp(self.root, CONFIG, runner=runner)
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            for key in ('legacy', 'demand_detail', 'transit'):
                file = root / f'{key}.xlsx'
                file.touch()
                app.variables[key].set(str(file))
            app.variables['output'].set(str(root / 'result.xlsx'))
            app.year.set('2026')
            app.set_months((8, 9))
            app.execute()
            self.addCleanup(finish.set)
            self.pump_until(started.is_set)
            self.assertTrue(app.busy)
            tick = []
            self.root.after(0, lambda: tick.append(True))
            self.pump_until(lambda: bool(tick))
            self.assertTrue(app.run_button.instate(['disabled']))
            app.execute()
            self.assertEqual(1, len(received))
            finish.set()
            self.pump_until(lambda: not app.busy)
            self.assertEqual(('2026-08', '2026-09'), received[0]['report_month'])
            self.assertTrue(app.open_button.instate(['!disabled']))
            self.assertTrue(app.run_button.instate(['!disabled']))
