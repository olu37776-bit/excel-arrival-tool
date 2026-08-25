# Excel 收入统计工具（第一版 POC）

这是一个收入统计 Excel 工具的可运行 POC。当前代码用于验证解耦结构、Excel 读写、规则编排和跨月对比；它的职责是**收入统计与变化识别**，不是装运规划或排程。

> 当前版本尚未用真实/脱敏源表完成字段契约验收，不能作为正式业务版直接使用。`Plan Month + Transit Days = Revenue Month`、默认 sheet/列名及部分归并键都是暂定输入契约，需以真实源表和最终业务规则替换。

## POC 已实现

- 读取 `PRD`、`Shipment`、`Transit Days` 三个 sheet。
- 按当前暂定配置去重；合同或发货点不同的记录始终分开。
- 同一 PO 范围内，`PRD` 取最早值，`Original PO Quantity` 取最大值。
- 按 `Trade Type` 查运输天数；特殊贸易类型的额外天数或覆盖天数独立配置。
- 计算 `Arrival Date` 和 `Revenue Month`，并按收入月份汇总数量和可选收入金额。
- 可读取上一次结果，只在 `Comparison` 中列出收入月份向后延迟至少 1 个月的记录。
- 输出 `Revenue Summary`、`Revenue Detail`、`Comparison`、`Run Info` 四个 sheet。

`Revenue Amount` 是可选字段。输入没有金额时，第一版仍可按数量统计收入月份；后续确认正式金额字段后，只改字段映射或金额规则，不改 Excel 读写主流程。

## 正式业务版仍需完成

- 用真实或脱敏源表冻结：源文件数量、sheet 名、表头行、字段、类型、别名、稳定关联键。
- 按最终口径重写归并：同合同和同发货点是前提，PRD 取最小，其余已确认字段取最大；被聚合字段不能同时放进归并键。
- 写入真实的特殊贸易类型和海运周期规则；当前配置只有机制和占位示例。
- 确认收入月份基于 PRD、计划出货、预计到货还是其他日期；当前计算公式只是 POC 假设。
- 冻结跨次对比的稳定 Shipment 身份键，处理重复键、新增、消失和规则版本变化。
- 使用真实样例补端到端验收，并根据公司电脑环境决定是否打包离线 EXE。

## 解耦结构

```text
config/                  字段映射与可调整业务参数
src/revenue_tool/domain  纯业务数据结构和错误
src/revenue_tool/rules   归并、PRD、贸易类型运输周期规则
src/revenue_tool/services 收入计算、月度汇总、历史对比
src/revenue_tool/adapters Excel 输入与输出
src/revenue_tool/application 用例编排
```

字段名或 sheet 名变化时修改 `config/field_mappings.json`。特殊贸易类型变化时修改 `config/business_rules.json` 的 `trade_type_adjustments`。核心计算不依赖 Excel 列名。

## Windows 使用

需要安装 Python 3.10 或更高版本。

1. 下载并解压仓库源码。
2. 双击 `setup_windows.bat`，只需执行一次。
3. 双击 `run_tool.bat`，依次输入本次源 Excel、输出文件和可选的上次结果路径。

也可以使用命令行：

```powershell
py -3 -m venv .venv
.venv\Scripts\python -m pip install .
.venv\Scripts\python -m revenue_tool template --output input-template.xlsx --config config
.venv\Scripts\python -m revenue_tool run --input input.xlsx --output result.xlsx --config config
.venv\Scripts\python -m revenue_tool run --input input.xlsx --output result.xlsx --previous last-result.xlsx --config config
```

## 输入契约

默认字段如下，实际列名可在配置中修改：

| Sheet | 必填字段 | 可选字段 |
|---|---|---|
| PRD | PO Number、PRD、Original PO Quantity | Contract Number、Shipping Point |
| Shipment | PO Number、Plan Month、Plan Quantity、Contract Number、Shipping Point、Trade Type | Shipment ID、Revenue Amount |
| Transit Days | Trade Type、Transit Days | 无 |

为了可靠对比多次运行，建议提供稳定的 `Shipment ID`。没有时工具会使用 PO、合同、发货点、贸易类型和计划数量生成稳定业务键。

## 验证

```powershell
$env:PYTHONPATH="src"
python -m unittest discover -s tests -v
```

测试覆盖：相同记录去重、不同合同/发货点不合并、PRD 取最早、数量取最大、特殊贸易周期、按月收入归集，以及延迟一个月标记。
