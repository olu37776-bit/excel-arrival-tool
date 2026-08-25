# Excel 工具使用说明

## 一、下载

推荐直接下载最新版压缩包：

https://github.com/olu37776-bit/excel-arrival-tool/archive/refs/heads/main.zip

下载完成后，先把 ZIP 完整解压到一个固定文件夹，不要直接在压缩包内运行。

也可以使用 Git：

```powershell
git clone https://github.com/olu37776-bit/excel-arrival-tool.git
```

## 二、首次安装

电脑需要先安装 Python 3.10 或更高版本。安装 Python 时请勾选 `Add Python to PATH`。

进入解压后的工具文件夹，双击：

```text
setup_windows.bat
```

看到“安装完成”后即可关闭窗口。首次安装需要联网下载依赖。

以后更新了工具版本，需要重新执行一次 `setup_windows.bat`。

## 三、运行

双击：

```text
run_tool.bat
```

按提示依次粘贴以下完整路径：

1. 遗留量 Excel 文件
2. 当月订货 Excel 文件
3. 要货明细 Excel 文件
4. 国家运输周期 Excel 文件
5. 输出 Excel 文件，例如 `D:\收入统计\result.xlsx`
6. 上一次成功结果文件

四个源文件可以放在任意文件夹，不需要复制到工具目录，但必须选择四个不同的 Excel 文件。

第一次运行时，第 6 项直接按回车留空。后续运行需要跨期比较或继承人工填写字段时，第 6 项选择上一次成功生成的结果文件。

可以在 Windows 文件资源管理器中对文件使用“复制为路径”，然后直接粘贴；脚本会自动处理路径两侧的双引号。

运行成功后，窗口会显示结果文件路径和各 Sheet 的记录数量。

## 四、常见问题

- 提示“请先运行 setup_windows.bat”：说明尚未安装，或工具文件夹移动后需要重新安装。
- 提示“工作簿不存在”：检查粘贴的是完整文件路径，并确认文件没有被移动或重命名。
- 输出路径必须包含文件名和 `.xlsx` 后缀，不能只填写文件夹。
- 输出文件不能覆盖四个源文件，也不能覆盖作为上期输入的结果文件。
- Excel 文件正在打开时可能无法覆盖原结果；请先关闭该文件再运行。

## 五、命令行方式

通常直接使用 `run_tool.bat` 即可。需要命令行运行时：

```powershell
.\.venv\Scripts\python.exe -m revenue_tool `
  --legacy "D:\数据\遗留量.xlsx" `
  --monthly-order "D:\数据\当月订货.xlsx" `
  --demand-detail "D:\数据\要货明细.xlsx" `
  --transit "D:\数据\国家运输周期.xlsx" `
  --output "D:\结果\result.xlsx" `
  --config ".\config\default.json"
```

需要读取上一次结果时，再增加：

```powershell
--previous "D:\结果\last-result.xlsx"
```
