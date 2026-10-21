"""Exercise real automatic recalculation and row height after UI-equivalent edits."""
from pathlib import Path
import subprocess
import sys
import time
import uuid

import uno
from com.sun.star.beans import PropertyValue


office, source = sys.argv[1], Path(sys.argv[2])
pipe = 'revenue_space_' + uuid.uuid4().hex
profile = (source.parent / 'office-profile').as_uri()
process = subprocess.Popen([office, '-env:UserInstallation=' + profile,
                            '--headless', '--norestore', '--nodefault', '--nofirststartwizard',
                            '--accept=pipe,name=' + pipe + ';urp;StarOffice.ServiceManager'],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
document = desktop = None
try:
    local = uno.getComponentContext()
    resolver = local.ServiceManager.createInstanceWithContext('com.sun.star.bridge.UnoUrlResolver', local)
    deadline = time.monotonic() + 25
    while True:
        try:
            context = resolver.resolve('uno:pipe,name=' + pipe + ';urp;StarOffice.ComponentContext')
            break
        except Exception:
            if time.monotonic() >= deadline:
                raise
            time.sleep(0.1)
    desktop = context.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', context)
    hidden = PropertyValue(); hidden.Name = 'Hidden'; hidden.Value = True
    document = desktop.loadComponentFromURL(source.as_uri(), '_blank', 0, (hidden,))
    assert document.isAutomaticCalculationEnabled()
    sheet = document.Sheets.getByName('基表')
    gap = sheet.getCellRangeByName('AN2')
    final = sheet.getCellRangeByName('AM2')
    manual = sheet.getCellRangeByName('AL2')
    row = sheet.Rows.getByIndex(1)
    height = row.Height
    assert not row.OptimalHeight, 'Generated data row must have a fixed height'
    assert gap.Value == 0 and final.Value == 150
    for value, expected_final, expected_gap in ((0, 0, 150), (175, 175, -25), (-20, -20, 170),
                                                (80.125, 80.13, 69.87)):
        manual.setValue(value)
        assert abs(final.Value - expected_final) < 0.000001, (value, final.Value)
        assert abs(gap.Value - expected_gap) < 0.000001, (value, gap.Value)
    manual.setString('abc')
    assert gap.String == '待修正：请检查收入空间或最终收入预测'
    manual.setString('')
    assert gap.Value == 0 and final.Value == 150
    sheet.getCellRangeByName('AO2').setString(('长备注输入测试' * 40 + '\n') * 8)
    assert row.Height == height and not row.OptimalHeight, (height, row.Height)
    document.store()
    document.close(True)
    document = desktop.loadComponentFromURL(source.as_uri(), '_blank', 0, (hidden,))
    sheet = document.Sheets.getByName('基表')
    assert abs(sheet.Rows.getByIndex(1).Height - height) <= 2
    assert not sheet.Rows.getByIndex(1).OptimalHeight
    assert sheet.getCellRangeByName('AN2').Value == 0
    print('Automatic amount edit/clear, gap recalculation and fixed multiline-note height passed')
finally:
    if document is not None:
        document.close(True)
    if desktop is not None:
        desktop.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.terminate()
        process.wait(timeout=5)
