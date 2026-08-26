# 下一轮集中修复实施验证报告

- 文档 ID：`IMPLEMENTATION-VERIFICATION-NEXT-FIXES`
- 日期：`2026-08-26`
- 实施基线：`main@be253be` + Issue #13/#17
- 目标版本：`v0.8.0`
- 自动验证状态：`PASSED`
- Windows 桌面版 Excel 实机状态：`PENDING_LOCAL_EXCEL_VALIDATION`

## 1. 实施结果

| 范围 | 结果 | 主要证据 |
|---|---|---|
| 合同级要货状态 | 已实现 | 比较器先聚合 `HAS_DEMAND` / `NO_DEMAND`，再执行普通月份比较 |
| 变为不要货 | 已实现 | RPD/CPD 均按上期每个真实中心输出，空月份仍输出 |
| 恢复要货 | 已实现 | RPD/CPD 均按本期每个真实中心输出，空月份仍输出 |
| 状态事件防重复 | 已实现 | 状态转换合同不再生成普通新增/取消；两期均不要货不输出 |
| 历史状态恢复 | 已实现 | 新结果 `_tool_meta` schema v3 显式保存 `row_kind`；schema v2/无元数据结果兼容推断 |
| 供应提拉排除占位行 | 已回归 | `CONTRACT_ONLY_NO_DEMAND` 继续在比较服务入口排除 |
| 是否解锁备货三态 | 已实现 | 独立聚合策略只输出未解锁/部分解锁/已解锁/空 |
| 旧拼接配置 | 已删除 | `stock_flag_delimiter`、配置校验和拼接代码均已移除 |
| 非法备货标识 | 已回归 | 继续报告 `INVALID_ENUM_VALUE`，非法值不参与三态集合 |
| 同行总控不一致 | 已回归 | `CONTROL_FLAG_MISMATCH` 继续逐源行报告 |

## 2. 规则到代码映射

| 规则 | 实现位置 |
|---|---|
| `DEMAND_CENTER` / `CONTRACT_ONLY_NO_DEMAND` 领域状态 | `src/revenue_tool/domain/models.py` |
| `HAS_DEMAND` / `NO_DEMAND` 合同级状态及冲突诊断 | `src/revenue_tool/services/comparison.py` |
| `变为不要货` / `恢复要货`、属性回退及月份空值保留 | `src/revenue_tool/services/comparison.py` |
| 新结果显式状态持久化 | `src/revenue_tool/adapters/excel_writer.py` |
| schema v3 状态恢复及 schema v2 兼容推断 | `src/revenue_tool/adapters/excel_reader.py` |
| 备货三态闭合聚合与集中中文文案 | `src/revenue_tool/services/stock_unlock.py` |
| 三态进入领域计算结果 | `src/revenue_tool/services/calculation.py` |
| 删除旧分隔符规则 | `config/default.json`、`src/revenue_tool/config.py` |

## 3. Issue #13 验收证据

- 上期多中心、本期不要货：按每个上期真实中心分别输出。
- 上期真实中心月份为空、本期不要货：RPD/CPD 工作簿集成测试均输出`变为不要货`，两期月份允许为空。
- 上期不要货、本期多中心且包含空月份：每个本期真实中心输出`恢复要货`。
- 两期均不要货：两张跨期清单均无输出。
- 同期同合同同时存在两种行状态：记录一次`CONTRACT_DEMAND_STATE_CONFLICT`，RPD/CPD 不静默选择。
- 新结果从隐藏元数据恢复行状态，不受用户可见收入分段单元格改动影响。
- 旧 schema v2 结果继续通过“空履行供应中心 + 不要货”恢复占位状态。
- 状态转换优先于普通新增/取消，测试结果无重复业务键。

## 4. Issue #17 验收证据

自动测试覆盖：单个/多个 Y、单个/多个 N、Y/N 不同顺序、无有效值、业务空白、VALUE、非法值与有效值混合。

结果矩阵：

| 有效标识集合 | 输出 |
|---|---|
| 空 | 空 |
| `{Y}` | 未解锁 |
| `{N}` | 已解锁 |
| `{Y,N}` | 部分解锁 |

完整重复源行在输入适配层先报告并去除；最终工作簿检查确认不再出现`Y|N`形式。同行备货/发货不一致异常保持不变。

## 5. 全量自动验证

执行命令：

```text
PYTHONPATH=src python -m unittest discover -s tests
PYTHONPATH=src python -m compileall -q src tests
git diff --check
python -m pip wheel . --no-deps --wheel-dir <temp>/wheel
python -m pip install --no-deps --target <temp>/installed <temp>/wheel/excel_arrival_tool-0.8.0-py3-none-any.whl
PYTHONPATH=<temp>/installed python -m revenue_tool.gui --smoke-test --config config/default.json
```

结果：

- 全量测试：`78`项通过。
- Python 编译检查：通过。
- Git 补丁空白检查：通过。
- wheel 构建、隔离安装、版本/32列配置导入及 GUI smoke：通过。
- 测试工作簿：5个可见业务 Sheet + 1个隐藏元数据 Sheet；基表32列。
- 独立工作簿解析：RPD/CPD各3条变化，其中`C003 | SC-C`为`变为不要货`。
- 独立公式错误扫描：0条。
- 5个可见业务 Sheet 均完成自动渲染检查；自动渲染环境缺少中文字体，但数值、结构、格式元数据和原始中文单元格均可解析。

全部验证使用虚构数据，未提交真实业务 Excel 或真实业务数据。

## 6. 已有 Issue 回归

| Issue | 自动回归结果 | 证据 |
|---|---|---|
| #6 | `PASSED` | 四类角色按字段契约定位 Sheet2；自动名称、歧义、无匹配诊断均通过 |
| #9 | `PASSED` | 七国结转、遗留量国家优先、空白/格式字符规范化及非七国反例通过 |
| #10 | `AUTOMATED_PASSED` | 5个可见 Sheet 使用可重开工作表 AutoFilter、无 Structured Table；桌面 Excel 操作仍待实机 |
| #11 | `PASSED` | 国家缺失、组合未找到、值不可用、非法值、固定5天术语及无需运输周期时静默均通过 |

## 7. Windows 桌面版 Excel 实机验证

状态：`PENDING_LOCAL_EXCEL_VALIDATION`

当前环境不能启动 Windows 桌面版 Excel。自动解析、OOXML 重开、AutoFilter 结构检查和渲染检查不等同于以下实机操作：

1. 分别在5个业务 Sheet 执行单列和多列筛选；
2. 点击`数据 → 清除`，确认所有隐藏行恢复且筛选下拉保留；
3. 保存、关闭、重新打开后重复操作；
4. 确认冻结首行、条纹、列宽、中文字体、日期/金额格式和人工字段编辑体验。

在本地完成上述步骤前，不声明 Windows 桌面 Excel 实机通过。

## 8. 剩余风险

- Windows 桌面 Excel 的筛选清除与显示体验仍为`PENDING_LOCAL_EXCEL_VALIDATION`。
- Windows EXE 需要在 PR 合入后由仓库 Windows 构建流程生成并执行启动 smoke test。
- 自动验收只使用虚构数据，真实四源文件仍需由业务用户做本地数据验收。
