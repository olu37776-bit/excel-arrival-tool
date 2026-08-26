# Excel 收入统计工具

## Windows 使用方式（推荐）

1. [直接下载 ExcelRevenueTool.exe](https://github.com/olu37776-bit/excel-arrival-tool/releases/download/v0.8.0/ExcelRevenueTool.exe)。
2. 双击 `ExcelRevenueTool.exe`。不需要安装 Python，也不需要运行 BAT 或打开终端。
3. 在窗口中选择三个必选源文件，并按需选择当月订货文件：
   - 遗留量 Excel
   - 当月订货 Excel（可选；没有时留空）
   - 要货明细 Excel
   - 国家运输周期 Excel
4. 选择结果保存位置，然后点击“开始生成”。

第一次运行时，“上一次成功结果”留空。以后需要跨期比较或继承人工填写字段时，选择上一次成功生成的结果文件。

如果 Windows SmartScreen 提示未识别应用，这是因为程序尚未购买代码签名证书；可点击“更多信息”后选择“仍要运行”。

## Python 方式（备用）

电脑已安装 Python 3.10 或更高版本时，可以解压[源码](https://github.com/olu37776-bit/excel-arrival-tool/archive/refs/heads/main.zip)，然后在工具目录执行：

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install .
.\.venv\Scripts\python.exe -m revenue_tool.gui --config .\config\default.json
```

图形窗口中的四个源文件可以位于任意文件夹，不需要放进工具目录。

## 常见问题

- 双击 EXE 后首次显示较慢：单文件程序需要先解压运行组件，请等待几秒。
- 提示“工作簿不存在”：重新选择文件，并确认文件没有被移动或重命名。
- 输出路径必须包含文件名和 `.xlsx` 后缀。
- 输出文件不能覆盖源文件或作为输入的上一次结果。
- Excel 文件正在打开时可能无法覆盖原结果，请先关闭该文件。
- 公司安全策略直接拦截 EXE：需要由公司 IT 放行，或改用上面的 Python 方式。
