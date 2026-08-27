# 收入分配重构 Phase 1 验证报告

- 文档 ID：`REVENUE-ALLOCATION-PHASE1-VERIFICATION`
- 日期：`2026-08-27`
- 分支：`refactor/revenue-allocation-v1`
- Draft PR：`#25`
- 实施基线 commit：`0e43d5dd9789300300d158dbfad0d3c0129b8576`
- 权威实施入口：`docs/implementation/revenue-allocation-phase1-operation-plan.md`
- Gate 结论：`PASS`

## 1. 修改文件

生产代码：

- `src/revenue_tool/domain/revenue_models.py`
- `src/revenue_tool/services/contract_finance.py`
- `src/revenue_tool/services/demand_records.py`
- `src/revenue_tool/services/fulfillment_projection.py`
- `src/revenue_tool/services/legacy_projection_adapter.py`
- `src/revenue_tool/services/calculation.py`
- `src/revenue_tool/application/pipeline.py`

测试：

- `tests/test_contract_finance.py`
- `tests/test_demand_records.py`
- `tests/test_fulfillment_projection.py`
- `tests/test_fulfillment_projection_golden.py`
- `tests/test_carryover.py`

未修改输出配置、Excel Writer、GUI、CLI、README、项目版本号或 Release。

## 2. 新领域类型

### 2.1 `ContractFinancialFact`

粒度为合同号，保存：

- 合同级遗留量、当月新订货和收入预测；
- BG、地区部、最终国家、结转类型、客户群和项目名称；
- 合同是否存在要货记录。

构造时强制校验：

```text
revenue_forecast = legacy_amount + monthly_new_order
```

动态合同全集只生成一条合同事实，多供应中心不会复制合同事实。

### 2.2 `DemandRecord`

粒度为 Reader 已去重后的一条要货明细证据记录，保存本次运行追溯 ID、合同、中心、状态、控制标识、日期、BG、源文件、Sheet、行号和无效字段证据。

模型明确不包含：

- `legacy_amount`；
- `monthly_new_order`；
- `revenue_forecast`；
- 任何人工分配金额。

`demand_record_id`只定义为本次运行追溯标识，不作为跨期稳定发货事件 ID。

### 2.3 `FulfillmentProjection`

粒度为合同号 + 履行供应中心；无要货合同使用受控的`CONTRACT_ONLY_NO_DEMAND`占位状态。

除原有履行字段外，新增：

- 要货记录数；
- 需求状态摘要；
- 源行摘要；
- DemandRecord 引用；
- ATA/ASD/RPD/CPD有效日期集合；
- `row_kind`；
- 异常代码引用。

模型不拥有遗留量、当月新订货或收入预测权威金额。

## 3. 原 `RevenueEngine` 职责拆分

| 原职责 | Phase 1 属主 |
|---|---|
| 动态合同全集、合同金额、合同属性、最终国家、结转类型、是否存在要货 | `ContractFactBuilder` |
| 去重后要货证据、运行内追溯 ID、源行和无效字段 | `DemandRecordService` |
| 合同+中心分组、日期聚合、海运周期、货未发完、到货日期、收入年月、收入分段、备货三态 | `FulfillmentProjectionService` |
| Phase 1 模型映射为旧 `BaseRow` 自动字段可比视图 | `LegacyProjectionAdapter` |
| 旧工作簿、人工月份字段继承和当前生产兼容路径 | 原 `RevenueEngine` / `BaseRow` / `PreviousData` |

`RevenueEngine`当前已委托`ContractFactBuilder`构建合同事实；履行投影新路径复用`calculation.py`现有纯规则函数，没有复制第二套日期、运输周期、到货日期或收入分段算法。

## 4. 双轨方案

采用 Operation Plan 的方案 A：

```text
生产 run_pipeline
→ 继续使用 RevenueEngine 生成现有 v0.8 工作簿契约

Phase 1 内部组合器 build_phase1_models
→ ContractFinancialFact
→ DemandRecord
→ FulfillmentProjection
→ LegacyProjectionAdapter 可比视图
```

本阶段没有改变 Sheet、列顺序、GUI、人工字段或最终用户操作流程。唯一用户可见规则变化为已批准的 Issue #20 修复。

## 5. Golden 字段与场景

逐业务键比较以下 30 个自动字段/状态：

```text
合同号、遗留量、当月新订货、BG、地区部、国家、结转类型、客户群、项目名称、
贸易术语、履行供应中心、多个供应中心发货、是否解锁备货、分批发货、海运周期、
ATA、ASD、RPD、多次要货、最晚ASD、最晚RPD、货未发完、CPD、分批供应、
到货日期（按RPD）、到货日期（按CPD）、收入年月（按RPD）、收入年月（按CPD）、
收入分段类别、row_kind
```

Golden 场景：

- 常规单中心和多中心；
- 同中心多记录及多状态；
- 多次要货、分批供应和备货三态；
- FCA、FOB、EXW和普通贸易术语；
- 正常、缺失和非法运输周期；
- 无要货合同占位；
- 有要货合同但供应中心为空；
- 当月订货文件未提供；
- 空白和VALUE；
- 浮点金额规范化；
- 完全重复行；
- 七国最终国家回退。

结果：除 Issue #20 精确场景外，新旧路径所有字段完全一致。

## 6. Issue #20 实现与证据

正式实现：

```text
resolved_country
= 遗留量国家优先
→ 为空时回退要货明细国家

carryover_type
= normalize_country_identity(resolved_country)
→ 与七国 canonical 名单精确比较
```

不再单独使用`legacy_country`判断结转类型。

测试证据：

- 七国遗留量国家直接命中；
- 遗留量国家为空时，七国逐一从要货明细回退并输出`交付类`；
- 空白、全角空格、换行和格式控制字符 identity 回归；
- 非七国不误命中；
- v0.8兼容模式与Phase 1新路径只有一个精确差异：
  - 业务键：`C020 + SC-A`；
  - 字段：`carryover_type`；
  - 旧值：空；
  - 新值：`交付类`。

Golden 比较器没有任何字段通配忽略规则。

## 7. 测试与全量验证

新增 18 个测试，覆盖合同事实、要货证据、履行投影和双轨 Golden。

执行命令与结果：

```text
PYTHONPATH=src python -m unittest discover -s tests
Ran 96 tests in 2.581s
OK

PYTHONPATH=src python -m unittest -v tests.test_fulfillment_projection_golden
Ran 4 tests in 0.116s
OK

python -m compileall -q src tests
PASS

git diff --check
PASS

python -m pip wheel . --no-deps --wheel-dir /tmp/revenue-phase1-wheel.4oxBr0
Successfully built excel_arrival_tool-0.8.0-py3-none-any.whl
```

基线 78 项测试全部继续通过；全量测试总数为 96。

## 8. 当前仍保留的旧路径

以下兼容路径有意保留：

- `RevenueEngine`；
- `BaseRow`；
- `PreviousData`；
- 当前`run_pipeline`工作簿编排；
- 旧三个人工月份字段初始化和继承；
- 当前五个可见 Sheet 和隐藏 metadata；
- 当前比较、供应提拉和 Excel Writer。

`RevenueEngine(legacy_carryover_compat=True)`仅用于 Golden 精确还原 v0.8 的 Issue #20旧判断，不由生产`run_pipeline`启用。

## 9. 未进入 Phase 2 的内容

本阶段未实施：

- `RevenueAllocationCandidate`正式输出；
- 手工分配金额读取或写出；
- `PreviousRunState`金额继承；
- 部分分配；
- `RevenueAllocationDecision`；
- `MonthlyRevenuePosting`；
- RPD/CPD月度收入汇总；
- 新工作簿全部 Sheet；
- GUI重构；
- 旧三个人工月份字段迁移；
- 删除旧兼容路径。

## 10. 已知风险

- Phase 1新履行投影仍是内部双轨路径，尚未替换生产工作簿数据流；这是方案 A 的受控状态，Phase 2前不得删除旧路径。
- `demand_record_id`依赖本次源文件、Sheet和行号，只用于运行内追溯；不得被后续阶段误用为跨期发货事件 ID。
- 当前验证使用虚构源文件；真实四源业务文件仍需在后续本地验收中回归数据分布和性能。
- Windows桌面Excel交互未因本阶段改变；本阶段没有修改 Writer 或工作簿契约。

## 11. Phase 1 Gate

```text
明确领域类型：PASS
合同事实每合同唯一：PASS
DemandRecord不承载合同金额：PASS
FulfillmentProjection不拥有合同收入预测：PASS
合同事实与履行投影服务拆分：PASS
旧路径保留：PASS
Golden除Issue #20外一致：PASS
Issue #20精确修复：PASS
全量测试与构建：PASS
未提前进入Phase 2：PASS

Phase 1 Gate：PASS
```
