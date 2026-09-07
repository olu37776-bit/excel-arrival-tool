# Excel 收入统计工具

## Windows 使用方式（推荐）

1. [直接下载 ExcelRevenueTool-v0.9.0.exe](https://github.com/olu37776-bit/excel-arrival-tool/releases/download/v0.9.0/ExcelRevenueTool-v0.9.0.exe)。
2. 双击 `ExcelRevenueTool-v0.9.0.exe`。不需要安装 Python，也不需要运行 BAT 或打开终端。
3. 在窗口中选择三个必选源文件，并按需选择当月订货文件：
   - 遗留量 Excel
   - 当月订货 Excel（可选；没有时留空）
   - 要货明细 Excel
   - 国家运输周期 Excel
4. 确认“汇总统计月份”（默认当前月份），选择结果保存位置，然后点击“开始生成”。

第一次运行时，“上一次成功结果”留空。以后需要跨期比较或继承人工填写字段时，选择上一次成功生成的结果文件。

如果 Windows SmartScreen 提示未识别应用，这是因为程序尚未购买代码签名证书；可点击“更多信息”后选择“仍要运行”。

## 地区收入汇总

结果自动包含“RPD地区收入汇总”和“CPD地区收入汇总”。两张表均按最终收入年月、最终收入分段和最终收入预测统计。

- 在订未发至小计五列上方的黄色年月区域填写完整年月，例如 `2026-09`；两张表可分别修改。
- 前期累计自动对应所选年份的1月至上月。例如选9月显示1—8月累计，选6月显示1—5月累计，选1月则为0。
- 改年月或基表黄色人工字段后，先按 `Ctrl+Alt+F9` 重算，再点“数据 → 全部刷新”。
- 双击金额单元格查看匹配明细；包括累计、四类分段、最后一列和最后一行小计。点击标题不展开明细。
- 最后一列和右下角只统计当月，不包含前期累计。隐藏辅助源仅服务透视，请使用基表或汇总页进行分析。

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
