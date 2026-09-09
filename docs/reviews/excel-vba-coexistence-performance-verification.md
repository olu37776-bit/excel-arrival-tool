# Issues #52 / #53 验证记录：Excel VBA 共存与系统透视取消

- 状态：`IN_PROGRESS`
- 日期：2026-09-09
- 仓库：`olu37776-bit/excel-arrival-tool`
- 分支：`fix/issues-52-53-vba-pivot-removal`
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

## 正常输出目标结构

仅保留：

1. `基表`
2. `RPD跨月变化`
3. `CPD跨月变化`
4. `供应需要提拉诉求清单粗表`
5. `异常清单`
6. `_tool_meta`（隐藏）

正常输出必须满足：

- 无 `_summary_source`；
- 无系统 PivotTable/PivotCache package parts；
- 基表每条业务记录仅保留4个最终字段公式；
- 黄色人工字段仍可编辑；
- 用户仍可自行在 Excel 基于基表创建透视表。

## 当前验证状态

首轮 PR 门禁发现删除系统透视模块后仍存在旧 `pipeline`、GUI smoke 与兼容测试引用，已作为真实回归修正，没有绕过门禁。随后已把用户透视输入回归改为独立测试夹具。

最新正式 Linux / OpenXML / Windows / EXE 门禁结果待本次提交触发后回填。

## Microsoft Excel 用户现场边界

Issue #52 的原始用户 VBA 脚本和现场 Microsoft Excel 环境不在 CI 中，因此即使自动门禁全部通过，仍必须标记：

`PENDING_LOCAL_EXCEL_VALIDATION`

用户需要使用修复版本重新生成**新结果文件**，完全退出并重新启动 Excel 后，在同一 Excel 会话中打开新结果和宏目标文件，运行原 VBA 脚本进行最终对照。旧版本已经生成的工作簿不会被新 EXE 自动改写。
