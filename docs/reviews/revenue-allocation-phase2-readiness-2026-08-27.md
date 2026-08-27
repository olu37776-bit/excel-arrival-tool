# 收入分配重构 Phase 2 实施前就绪性审查

- 审查 ID：`REVENUE-ALLOCATION-PHASE2-READINESS-2026-08-27`
- 日期：`2026-08-27`
- 审查分支：`refactor/revenue-allocation-v1`
- Draft PR：`#25`
- Phase 1 实施提交：`8be324e4c3f67acf8f88599c376ba6b1eb554203`
- 审查基线分支头：`0eb5c569c5274ba0fd799f9da377ff0d5c34b2ff`
- Phase 2 Operation Plan：`docs/implementation/revenue-allocation-phase2-operation-plan.md`
- 审查结论：`PASS`
- 状态：`READY_FOR_PHASE2_IMPLEMENTATION`

## 1. 审查范围

本次独立复核：

1. Phase 1 Gate、实施提交与当前分支头；
2. Phase 1 EXE工作流是否改变领域Gate；
3. 96项测试证据来源；
4. 当前仍保留的旧生产路径；
5. `RevenueAllocationCandidate`边界；
6. candidate ID v1精确算法；
7. projection fingerprint v1；
8. `PreviousRunState`和历史人工分配表示；
9. 历史继承、变化诊断和v0.8兼容；
10. Phase 2 WRITE_SCOPE、Golden门禁和完成标准。

本次未修改生产代码。

## 2. 权威输入复核

已完整审查：

- `docs/refactor/revenue-allocation-refactor-v3.md`；
- `docs/decisions/DR-008-revenue-allocation-v3-implementation-approval.md`；
- `docs/implementation/revenue-allocation-phase1-operation-plan.md`；
- `docs/reviews/revenue-allocation-phase1-verification.md`；
- `docs/reviews/revenue-allocation-refactor-readiness-v3-2026-08-27.md`；
- Phase 1 `ContractFinancialFact`、`DemandRecord`、`FulfillmentProjection`；
- `ContractFactBuilder`、`DemandRecordService`、`FulfillmentProjectionService`；
- `LegacyProjectionAdapter`和`build_phase1_models()`；
- 当前`RevenueEngine`、`PreviousData`、历史结果metadata和生产pipeline兼容事实。

结论：Phase 2 Operation Plan与DR-008/V3一致，没有采用V1、V2旧假设。

## 3. Phase 1独立复核

### 3.1 提交和分支头

Phase 1领域实施提交：

```text
8be324e4c3f67acf8f88599c376ba6b1eb554203
refactor: implement revenue allocation phase 1
```

审查时远端分支头：

```text
0eb5c569c5274ba0fd799f9da377ff0d5c34b2ff
build: add Phase 1 Windows artifact workflow
```

`8be324e..0eb5c56`差异只有：

```text
A .github/workflows/build-phase1-windows-exe.yml
```

该工作流负责从P1分支构建、启动自检和发布分支专属预发布EXE，不修改领域模型、服务、生产pipeline、输出字段或测试。

结论：后续EXE工作流提交不改变Phase 1领域Gate。

### 3.2 Phase 1模型和职责

代码已实现：

```text
ContractFinancialFact
DemandRecord
FulfillmentProjection
RevenuePhase1Models
```

职责边界：

| 领域职责 | 当前属主 | 复核结论 |
|---|---|---|
| 合同全集、金额、属性、最终国家、结转类型 | `ContractFactBuilder` | 清晰 |
| 去重要货证据和运行内追溯 | `DemandRecordService` | 清晰 |
| 合同+中心履行归纳 | `FulfillmentProjectionService` | 清晰 |
| 新轨到旧自动字段可比视图 | `LegacyProjectionAdapter` | 清晰 |
| 旧生产工作簿和人工月份字段 | `RevenueEngine` / `BaseRow` / `PreviousData` | 有意保留 |

`ContractFinancialFact`强制：

```text
revenue_forecast = legacy_amount + monthly_new_order
```

`DemandRecord`不含合同金额或人工金额；`FulfillmentProjection`不拥有合同收入预测权威金额。

### 3.3 双轨事实

当前采用Phase 1方案A：

```text
生产run_pipeline → RevenueEngine → v0.8工作簿
内部build_phase1_models → 新领域模型
```

因此P1 EXE的用户可见Sheet与v0.8一致是已批准行为。新领域模型当前通过内部组合器和Golden测试验证，不通过新Sheet向用户展示。

该状态是阶段设计，不是风险。

### 3.4 96项测试证据

Phase 1验证报告记录：

```text
基线测试：78
Phase 1新增测试：18
全量：96
```

新增测试来源：

- `tests/test_contract_finance.py`；
- `tests/test_demand_records.py`；
- `tests/test_fulfillment_projection.py`；
- `tests/test_fulfillment_projection_golden.py`；
- `tests/test_carryover.py`中的Issue #20回归补强。

本次在当前分支头独立执行：

```text
PYTHONPATH=src python -m unittest discover -s tests
Ran 96 tests in 2.384s
OK
```

结论：96项证据可从仓库测试发现入口复现，不是只引用历史报告。

### 3.5 Phase 2开始前保留的旧路径

仍有意保留：

- `RevenueEngine`；
- `BaseRow`；
- `PreviousData`；
- `ExcelInputAdapter.read_previous()`；
- 旧三个人工月份字段初始化和继承；
- 当前`run_pipeline`；
- 当前比较与供应提拉服务；
- 当前五个可见Sheet；
- schema 3 `_tool_meta`；
- 当前Excel Writer、GUI和CLI。

结论：Phase 2不得删除或替换这些路径。

## 4. Phase 2目标模型复核

Phase 2模型边界闭合为：

```text
FulfillmentProjection
→ RevenueAllocationCandidate

PreviousRunState
→ CandidateHistoryService
→ 继承快照 / 变化诊断 / orphaned历史分配
```

正式类型至少包括：

- `RevenueAllocationCandidate`；
- `ManualAllocationSnapshot`；
- `PreviousRunMetadata`；
- `PreviousContractState`；
- `PreviousCandidateState`；
- `PreviousRunState`；
- 候选历史匹配结果或等价结构。

无要货占位投影不生成候选，但继续保存在历史投影集合中供跨期状态比较。

结论：模型未把DemandRecord误当分配行，也未把合同金额下沉为候选权威金额。

## 5. candidate ID v1复核

已冻结：

```text
candidate_id_version = "1"

payload = [
  "1",
  normalize_text(contract_no),
  normalize_lookup(supply_center),
  normalize_text(row_kind).upper()
]

allocation_candidate_id
= "RAC-v1-" + SHA256(canonical JSON UTF-8)
```

固定测试向量：

```text
["1","C001","sc-a","DEMAND_CENTER"]
→ RAC-v1-adadc699ea166aac0e020e8640d57a9a6e843fd59e454b6143d6be9109d1bf77
```

日期、到货日期、月份、分段、合同金额和源行均被明确排除。

复核结论：

- 与当前合同/中心business key规范一致；
- 日期变化不会制造新候选；
- 版本进入payload和显示前缀；
- 冲突不得通过追加源行或日期解决；
- 算法足够精确，可直接编码和Golden验证。

## 6. projection fingerprint复核

指纹与candidate ID已明确分离：

```text
candidate ID = 身份
projection fingerprint = 履行内容版本
```

指纹包含：

- 记录数和状态集合；
- 多中心、分批、备货三态和货未发完；
- 贸易术语、运输周期；
- ATA/ASD/RPD/CPD日期集合及聚合值；
- 两套到货日期和收入年月；
- 收入分段；
- 异常代码。

指纹排除：

- 运行内DemandRecord ID；
- 源文件、Sheet和行号；
- 合同金额；
- 人工金额和备注；
- run ID和生成时间。

复核结论：业务内容变化可触发复核，文件重排不会制造假变化。

## 7. PreviousRunState复核

结构已覆盖用户要求：

| 要求 | 结构位置 | 结论 |
|---|---|---|
| 上期FulfillmentProjection | `fulfillment_projections` / previous projection snapshot | 已覆盖 |
| 上期candidate ID | `PreviousCandidateState.allocation_candidate_id` | 已覆盖 |
| 上期手工分配金额 | `ManualAllocationSnapshot` | 已覆盖 |
| 上期分配备注 | `ManualAllocationSnapshot.note` | 已覆盖 |
| 上期合同收入预测 | `PreviousContractState.revenue_forecast` | 已覆盖 |
| 上期收入年月 | `PreviousCandidateState.revenue_month_rpd/cpd` | 已覆盖 |
| 上期收入分段 | `PreviousCandidateState.revenue_segment` | 已覆盖 |
| metadata schema | `PreviousRunMetadata.metadata_schema` | 已覆盖 |
| candidate ID version | `PreviousRunMetadata`与candidate state | 已覆盖 |
| run ID | `PreviousRunMetadata.run_id` | 已覆盖 |

金额状态使用：

```text
UNAVAILABLE / BLANK / VALUE
```

因此：

- 旧v0.8不支持新金额字段；
- 新格式空白；
- 明确数值0；

三者不会混淆。

## 8. 历史继承和诊断复核

已冻结：

- 只有candidate ID和版本精确命中才能继承；
- 指纹变化保留金额与备注，同时要求复核；
- 合同收入预测变化保留金额与备注，同时要求复核；
- 新候选不继承；
- 消失候选不自动迁移到其他中心；
- 消失候选存在`VALUE`金额时生成`ORPHANED_PREVIOUS_ALLOCATION`；
- 明确0属于`VALUE`，不会被当作空白；
- v0.8只恢复履行比较，不伪造人工分配；
- candidate ID版本变化不进行模糊迁移。

结论：人工金额不会因日期变化被清空，也不会因候选消失而静默丢失。

## 9. 双轨和持久化复核

Phase 2选择：

```text
内部双轨
不写新隐藏系统数据
不修改用户可见工作簿
```

Phase 5才同时建设：

- 新可见Sheet；
- candidate ID和人工金额写出；
- 新metadata schema；
- PreviousResultReader；
- 保存、关闭、重开、再次导入的完整往返。

结论：Phase 2不会产生半套持久化格式；该选择满足“不在没有完整往返设计时随意修改工作簿”。

## 10. WRITE_SCOPE复核

Phase 2 WRITE_SCOPE只开放：

- 新领域类型；
- candidate身份与fingerprint服务；
- 历史状态和变化诊断服务；
- v0.8只读兼容adapter；
- 内部Phase 2组合器；
- 测试、虚构fixture和Phase 2验证报告。

明确禁止：

- `config/default.json`；
- Excel Writer；
- GUI、CLI；
- README最终用户流程；
- 版本和Release；
- 用户可见Sheet；
- `_tool_meta` schema；
- Phase 3分配服务；
- Phase 4 Posting和月度汇总；
- Phase 5新工作簿；
- 删除旧兼容路径。

结论：范围足以实现Phase 2，且不会越界。

## 11. 测试与Gate复核

Operation Plan已要求：

- candidate ID固定向量；
- projection fingerprint包含/排除字段；
- 空白、0和旧格式不可用三态；
- 精确继承；
- projection变化；
- 合同预测变化；
- 新增、消失和orphan；
- v0.8 schema 2/3兼容；
- Phase 1 30字段Golden；
- 96项现有测试回归；
- 当前工作簿结构和值完全兼容；
- compileall、diff check和wheel构建。

结论：测试计划能够证明身份稳定、历史金额不丢失和生产契约零变化。

## 12. 尚未进入的范围

本次计划没有开放：

- 自动或手工分配计算；
- 部分分配；
- 超额和守恒；
- `RevenueAllocationDecision`正式计算；
- Posting；
- RPD/CPD月度收入汇总；
- 待处理收入正式输出；
- 新Sheet和隐藏数据写入；
- GUI重构；
- 旧人工月份字段迁移；
- 删除旧生产路径。

## 13. Readiness Gate

```text
Phase 1 Gate复核：PASS
当前分支头确认：PASS
EXE工作流不改变领域Gate：PASS
96项测试独立复现：PASS
旧生产路径保留：PASS
RevenueAllocationCandidate边界：PASS
candidate ID v1精确冻结：PASS
projection fingerprint职责分离：PASS
PreviousRunState结构闭合：PASS
空白与明确0区分：PASS
历史继承与变化诊断：PASS
ORPHANED_PREVIOUS_ALLOCATION：PASS
v0.8兼容行为：PASS
内部双轨与持久化边界：PASS
WRITE_SCOPE：PASS
测试、Golden和完成标准：PASS
未修改生产代码：PASS

Phase 2 Readiness：PASS
```

Phase 2可以在现有`refactor/revenue-allocation-v1`和Draft PR #25上进入实施；不得新建第二个重构分支，不得提前进入Phase 3。
