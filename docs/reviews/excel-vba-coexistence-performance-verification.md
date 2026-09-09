# Issues #52 / #53 验证记录：Excel VBA 共存与系统透视取消

- 状态：`AUTOMATED_VALIDATION_PASSED / PENDING_LOCAL_EXCEL_VALIDATION`
- 日期：2026-09-09
- 仓库：`olu37776-bit/excel-arrival-tool`
- 合并提交：`5fe3b18604106fb760e9335a5d4793d2c49e09f4`
- PR：#54
- 关联 Issue：#52、#53

## 已实施的代码侧变更

1. 正常输出停止生成：
   - `RPD地区收入汇总`
   - `CPD地区收入汇总`
   - `_summary_source`
2. 正常输出不再创建系统 `PivotTable` / `PivotCache`。
3. 删除仅服务系统地区透视的生产链 `regional_pivot.py` / `regional_summary.py`。
4. 保留基表四个最终字段的实时公式和首次缓存值。
5. Excel计算属性改为普通自动计算：
   - `calcMode=auto`
   - `fullCalcOnLoad=False`
   - `forceFullCalc=False`
   - `calcOnSave=False`
6. 用户自建透视/分组 PivotCache 的上期读取兼容能力继续保留；测试和 EXE smoke 使用独立最小透视夹具，不把系统透视重新带回正常输出。

## 正常输出结构

只保留：

1. `基表`
2. `RPD跨月变化`
3. `CPD跨月变化`
4. `供应需要提拉诉求清单粗表`
5. `异常清单`
6. `_tool_meta`（隐藏）

自动回归已验证：

- 无 `_summary_source`；
- 无系统 `xl/pivotTables/*` / `xl/pivotCache/*` package parts；
- 基表每条业务记录只保留4个最终字段公式；
- 黄色人工字段仍可编辑；
- 用户自建透视/分组 PivotCache 的上期读取隔离不退化；
- 基表仍可供用户自行筛选、排序和创建透视表。

## 正式门禁

PR #54 最终验证运行：GitHub Actions `34335625275`，head `bbaa5322291b73c0f721168e8c7000833f9a5e6d`。

### Microsoft Open XML SDK

`ooxml-verification`：通过。

生成的 pipeline / edge-cases / empty 工作簿均通过 Microsoft Open XML SDK 校验；删除系统透视后未留下悬空 PivotTable/PivotCache 关系。

### Linux / 独立公式引擎

`formula-verification`：通过。

- `137` 项测试全部通过；
- LibreOffice 实际 XLSX 公式重算回归通过；
- `compileall` 通过；
- `git diff --check` 通过；
- wheel 构建通过。

### Windows / EXE

`build`：通过。

- Windows 全量测试：`137` 项通过，`1` 项因 Linux 专用公式引擎能力跳过；
- PyInstaller 成功生成 `ExcelRevenueTool-v0.11.3.exe`；
- 打包 EXE `--smoke-test` 通过；
- smoke 明确检查正常输出不含系统透视和 `_summary_source`、不启用强制全量重算；
- smoke 继续验证人工 `False` / 明确金额 `0` 的继承以及分组用户 PivotCache 上期读取能力；
- PR 构建 artifact ID：`10097649245`。

## 门禁结论

### Issue #53

系统地区收入透视及其隐藏辅助源已从正常输出完全移除，自动验证通过，可视为代码与构建层完成。

### Issue #52

已完成两项高优先级代码侧降负载：

1. 删除系统地区透视、PivotCache 和 `_summary_source` 大量辅助公式；
2. 取消 `forceFullCalc/fullCalcOnLoad/calcOnSave`，仅保留普通 `calcMode=auto` 以支持四个最终字段实时计算。

自动门禁证明结构、公式、上期兼容和 Windows EXE 构建未回退，但 CI 没有用户原始 VBA 脚本和 Microsoft Excel 桌面环境，因此**不能宣称用户现场 VBA 卡住已最终复现并验证消失**。

## Microsoft Excel 用户现场验收

Issue #52 保持：

`PENDING_LOCAL_EXCEL_VALIDATION`

验收步骤：

1. 使用包含上述修复的新 EXE 重新生成一个**新结果文件**；旧版本已经生成的工作簿不会被新 EXE 自动改写。
2. 完全退出所有 Excel 进程后重新启动 Excel，避免旧工作簿留下的计算状态干扰对照。
3. 在同一 Excel 会话中打开新生成结果和原 VBA 脚本目标文件。
4. 运行用户原来的 VBA 脚本。
5. 记录是否仍出现长时间无响应；若仍存在，再结合原 VBA 中的 `Calculate/CalculateFull/RefreshAll`、未限定 Workbook/Range 等调用做下一步定位。

只有该实机复测通过后，Issue #52 才应最终关闭。
