# 收入分配重构 Phase 2 Operation Plan

- 文档 ID：`REVENUE-ALLOCATION-PHASE2-OPERATION-PLAN`
- 状态：`READY_FOR_IMPLEMENTATION`
- 日期：`2026-08-27`
- 实施分支：`refactor/revenue-allocation-v1`
- Draft PR：`#25`
- Phase 1 实施提交：`8be324e4c3f67acf8f88599c376ba6b1eb554203`
- 本计划基线提交：`0eb5c569c5274ba0fd799f9da377ff0d5c34b2ff`
- 权威设计：`docs/refactor/revenue-allocation-refactor-v3.md`
- 实施批准：`docs/decisions/DR-008-revenue-allocation-v3-implementation-approval.md`
- 前置 Gate：`docs/reviews/revenue-allocation-phase1-verification.md`，结论 `PASS`
- 本阶段：`Phase 2 — 分配候选和历史状态`

## 1. 阶段目标

Phase 2 只完成以下领域和内部双轨能力：

1. 定义 `RevenueAllocationCandidate`；
2. 冻结 `candidate ID v1`；
3. 冻结与 candidate ID 分离的 `projection fingerprint v1`；
4. 定义 `PreviousRunState`；
5. 定义历史手工分配金额与分配备注的结构化表示；
6. 定义候选新增、消失、履行投影变化和合同收入预测变化的诊断；
7. 建立候选与历史状态的内部双轨组合器和兼容测试；
8. 保持当前生产工作簿、GUI和旧历史路径不变。

Phase 2 不进行分配计算、月度 Posting、月度汇总或新工作簿建设。

## 2. 权威输入与优先级

实施前必须完整读取：

1. `docs/refactor/revenue-allocation-refactor-v3.md`；
2. `docs/decisions/DR-008-revenue-allocation-v3-implementation-approval.md`；
3. `docs/implementation/revenue-allocation-phase1-operation-plan.md`；
4. `docs/reviews/revenue-allocation-phase1-verification.md`；
5. `docs/reviews/revenue-allocation-refactor-readiness-v3-2026-08-27.md`；
6. 当前 Phase 1 领域模型、服务、Golden adapter 和 pipeline。

优先级：

```text
DR-008 / revenue-allocation-refactor-v3
> Phase 1 Operation Plan 与 Phase 1 Gate 事实
> 当前分支 Phase 1 代码和测试
```

V1、V2 重构文档仅保留讨论历史，不得作为实施依据。

## 3. Phase 1 基线与 Phase 2 接口

### 3.1 已完成的 Phase 1 输入

Phase 2 直接消费：

```text
ContractFinancialFact
DemandRecord
FulfillmentProjection
```

粒度保持：

```text
ContractFinancialFact：合同号
DemandRecord：本次运行内的一条去重要货证据
FulfillmentProjection：合同号 + 履行供应中心
```

Phase 2 不改变 Phase 1 已冻结的日期、运输周期、收入年月、收入分段、备货三态和不要货规则。

### 3.2 当前生产路径

当前生产编排仍为：

```text
run_pipeline
→ ExcelInputAdapter
→ RevenueEngine
→ BaseRow / PreviousData
→ comparison / supply pull
→ ExcelOutputAdapter
→ v0.8 工作簿契约
```

Phase 1 新轨入口为：

```text
build_phase1_models
→ ContractFactBuilder
→ DemandRecordService
→ FulfillmentProjectionService
```

Phase 2 不得把生产 `run_pipeline` 切换到新轨。

## 4. 本阶段双轨决策

Phase 2 采用：

```text
内部双轨，不写入新的隐藏系统数据
```

具体规则：

- 新候选、指纹、历史恢复和诊断由新的内部组合器与测试运行；
- 当前五个可见 Sheet 不变；
- 当前 `_tool_meta` 继续保持 schema `3`；
- 不新增 `_fulfillment_projection` 或其他隐藏 Sheet；
- 不在当前基表写入 candidate ID、人工分配金额或分配备注；
- 不修改当前旧三个人工月份字段；
- 不修改 Excel Writer、GUI、CLI或配置输出契约。

选择该方案的原因是 Phase 5 才建设新工作簿、metadata schema 和完整 Excel 往返。Phase 2 若提前写隐藏数据，会产生只能写不能完整读取、编辑、校验和升级的半套持久化契约。

该内部双轨是批准的阶段设计，不是 Phase 2 风险或未完成项。

## 5. RevenueAllocationCandidate

### 5.1 粒度与资格

V1 默认：

```text
一条 row_kind = DEMAND_CENTER 的 FulfillmentProjection
→ 一条 RevenueAllocationCandidate
```

约束：

- `contract_no`必须非空；
- `supply_center`必须非空；
- `row_kind`必须为`DEMAND_CENTER`；
- 同一运行内 `allocation_candidate_id` 必须唯一；
- `CONTRACT_ONLY_NO_DEMAND` 不生成候选；
- 有要货记录但供应中心为空的异常记录不生成正常候选。

无要货合同仍保留 `ContractFinancialFact` 和 `FulfillmentProjection` 占位，但 Phase 2 不为其制造虚构候选。

### 5.2 领域字段

`RevenueAllocationCandidate` 至少包含：

```text
allocation_candidate_id: str
candidate_id_version: str
contract_no: str
supply_center: str
row_kind: str
projection_fingerprint: str
projection_fingerprint_version: str
fulfillment_projection: FulfillmentProjection
projection_changed: bool
contract_forecast_changed: bool
review_required: bool
diagnostic_codes: tuple[str, ...]
```

其中：

- `fulfillment_projection` 是分配判断上下文；
- `projection_changed`、`contract_forecast_changed`、`review_required`由历史匹配结果产生；
- candidate 不拥有合同收入预测权威金额；
- 后续显示合同收入预测时只能作为来自 `ContractFinancialFact` 的参考值；
- Phase 2 不在 candidate 上实现最终分配金额、部分分配或 Posting。

## 6. candidate ID v1

### 6.1 版本

```text
candidate_id_version = "1"
```

ID 显示格式：

```text
RAC-v1-<64位小写SHA-256十六进制>
```

### 6.2 规范化规则

`normalized_contract_no`：

```text
normalize_text(contract_no)
= Unicode NFKC
→ 连续空白折叠为一个半角空格
→ 去除首尾空白
→ 保留大小写
```

合同号保留大小写是为了与当前合同事实和 `business_key_identity` 的合同身份一致，避免把当前被识别为两个合同的值错误合并。

`normalized_supply_center`：

```text
normalize_lookup(supply_center)
= normalize_text
→ Unicode casefold
```

`normalized_row_kind`：

```text
normalize_text(row_kind).upper()
```

只接受正式枚举值 `DEMAND_CENTER`。

### 6.3 精确生成算法

按以下顺序构造 JSON 数组：

```text
[
  candidate_id_version,
  normalized_contract_no,
  normalized_supply_center,
  normalized_row_kind
]
```

序列化规则：

```text
json.dumps(
  payload,
  ensure_ascii=False,
  separators=(",", ":")
)
```

随后：

```text
digest = sha256(canonical_json.encode("utf-8")).hexdigest()
allocation_candidate_id = "RAC-v1-" + digest
```

固定测试向量：

```text
输入：contract_no=" C001 "
     supply_center="SC-A"
     row_kind="DEMAND_CENTER"
     candidate_id_version="1"

canonical JSON：
["1","C001","sc-a","DEMAND_CENTER"]

candidate ID：
RAC-v1-adadc699ea166aac0e020e8640d57a9a6e843fd59e454b6143d6be9109d1bf77
```

全角合同号`Ｃ００１`与`C001`生成相同 ID；`SC-A`与`sc-a`生成相同 ID。

### 6.4 明确排除字段

以下字段不得进入 candidate ID：

- ATA、ASD、RPD、CPD；
- 最晚ASD、最晚RPD；
- 到货日期；
- 收入年月；
- 收入分段；
- 海运周期和货未发完；
- 合同收入预测、遗留量和当月新订货；
- 要货记录数和状态摘要；
- 源文件、Sheet、源行号；
- `demand_record_id`；
- 异常代码。

这些字段变化不得制造新候选。

### 6.5 ID 冲突与版本变化

- 同一运行出现相同 ID 对应不同规范化业务键时，记录 `CANDIDATE_ID_COLLISION` 并使 Phase 2 Gate 失败；
- `candidate_id_version`不同不得自动精确继承；
- 不允许用日期、金额或源行号作为冲突后的追加盐值；
- 未来升级 candidate ID 必须新增正式版本和迁移决策，不得静默改变 v1 算法。

## 7. projection fingerprint v1

### 7.1 与 candidate ID 的区别

```text
candidate ID
= 候选身份

projection fingerprint
= 该身份下本期履行内容快照
```

日期、月份、收入分段或履行证据变化：

```text
candidate ID 不变
projection fingerprint 改变
projection_changed = Y
review_required = Y
```

### 7.2 版本和格式

```text
projection_fingerprint_version = "1"
projection_fingerprint = "FP-v1-" + sha256(canonical_json).hexdigest()
```

使用 UTF-8、小写 64 位 SHA-256 和 canonical JSON：

```text
json.dumps(
  payload,
  ensure_ascii=False,
  sort_keys=True,
  separators=(",", ":")
)
```

### 7.3 固定字段集合

fingerprint payload 固定包含：

```text
projection_fingerprint_version
normalized_contract_no
normalized_supply_center
row_kind
multiple_supply_centers
demand_record_count
demand_status_set
incoterm
stock_unlocked
split_shipment
transit_days
ata_values
asd_values
rpd_values
cpd_values
ata
asd
rpd
multiple_demand
latest_asd
latest_rpd
shipment_incomplete
cpd
split_supply
arrival_date_rpd
arrival_date_cpd
revenue_month_rpd
revenue_month_cpd
revenue_segment
issue_codes
```

规范化：

- 日期使用 ISO `YYYY-MM-DD`，空值为 JSON `null`；
- 日期集合去重、升序并序列化为数组；
- `demand_status_set`按`normalize_lookup`规范化、去重、升序；
- `incoterm`按`normalize_text(...).upper()`；
- Y/N、枚举和收入分段按正式领域值输出；
- `issue_codes`去重、升序；
- `transit_days`为整数或`null`；
- 空文本统一为`null`，不得同时存在空字符串和`null`两种表示。

### 7.4 明确排除字段

fingerprint 不包含：

- `demand_record_id`；
- `source_row_summary`；
- 源文件名、Sheet名和源行号；
- 生成时间和 run ID；
- 合同金额；
- 人工分配金额和备注。

原因：运行内追溯位置或文件重排不能单独触发履行变化；合同金额变化使用独立诊断；人工决定不能参与履行指纹。

## 8. 历史人工分配的结构化表示

### 8.1 ManualAllocationSnapshot

定义：

```text
ManualAmountState = UNAVAILABLE | BLANK | VALUE

ManualAllocationSnapshot
- amount_state: ManualAmountState
- amount: Decimal | None
- note: str | None
- source_run_id: str | None
```

不变量：

```text
UNAVAILABLE → 来源格式不支持手工分配金额，amount必须为None
BLANK       → 来源支持该字段但用户未填写，amount必须为None
VALUE       → 用户明确填写数值，amount必须为Decimal
```

数值 `0` 表示：

```text
amount_state = VALUE
amount = Decimal("0.00")
```

它不得被转换为 `BLANK`。

金额沿用 `Decimal`、`ROUND_HALF_UP` 和 `0.01` 精度；备注经过`normalize_text`，空备注为`None`。备注可以在金额空白时存在，不因此伪造金额。

### 8.2 序列化契约

未来持久化时必须使用：

```text
amount_state: "UNAVAILABLE" | "BLANK" | "VALUE"
amount: null | 两位小数字符串
note: null | string
```

示例：

```text
空白：{"amount_state":"BLANK","amount":null,"note":null}
明确0：{"amount_state":"VALUE","amount":"0.00","note":"本期明确不分配"}
```

Phase 2 只冻结并测试该契约，不写入生产工作簿。

## 9. PreviousRunState

### 9.1 结构

建议定义以下不可变类型：

```text
PreviousRunMetadata
- metadata_schema: str
- candidate_id_version: str | None
- projection_fingerprint_version: str | None
- run_id: str | None
- source_format: NATIVE | V08_COMPAT | TEST_FIXTURE

PreviousContractState
- contract_no: str
- revenue_forecast: Decimal

PreviousCandidateState
- allocation_candidate_id: str
- candidate_id_version: str
- contract_no: str
- supply_center: str
- row_kind: str
- projection: FulfillmentProjectionSnapshot
- projection_fingerprint: str
- revenue_month_rpd: str | None
- revenue_month_cpd: str | None
- revenue_segment: str
- manual_allocation: ManualAllocationSnapshot

PreviousRunState
- metadata: PreviousRunMetadata
- fulfillment_projections: tuple[FulfillmentProjectionSnapshot, ...]
- candidates_by_id: Mapping[str, PreviousCandidateState]
- contracts_by_no: Mapping[str, PreviousContractState]
- usable_for_projection_comparison: bool
- usable_for_allocation_inheritance: bool
- diagnostic_codes: tuple[str, ...]
```

`fulfillment_projections`必须独立于候选集合，因为`CONTRACT_ONLY_NO_DEMAND`不生成候选，但仍需要跨期履行状态比较。

### 9.2 索引和唯一性

- `contracts_by_no`按`normalized_contract_no`唯一；
- `candidates_by_id`按完整 candidate ID 唯一；
- 履行投影按规范化`contract_no + supply_center + row_kind`唯一；
- 重复历史候选不得保留第一条后静默继续，必须记录 `PREVIOUS_DUPLICATE_CANDIDATE_ID` 并禁用相关候选的金额继承；
- metadata schema 或 candidate ID version 不支持时，不得猜测人工金额。

### 9.3 v0.8 兼容恢复

当前 v0.8 / metadata schema 2、3：

- 可恢复旧 `BaseRow` 履行字段和 `row_kind`；
- schema 2 可继续按“空中心 + 收入分段=不要货”推断占位状态；
- schema 3 使用显式 `row_kind`；
- 对 `DEMAND_CENTER` 行可按 candidate ID v1 算法生成仅用于比较的派生 ID；
- `source_format = V08_COMPAT`；
- `manual_allocation.amount_state = UNAVAILABLE`；
- `usable_for_projection_comparison = true`；
- `usable_for_allocation_inheritance = false`；
- 旧三个人工月份字段和`调整备注`不得映射为手工分配金额或分配备注；
- 首次进入未来新工作簿时不生成伪造的历史金额。

## 10. 历史匹配与变化诊断

### 10.1 精确命中

精确命中条件：

```text
candidate_id_version相同
且 allocation_candidate_id完全相同
```

处理：

- 原样继承 `ManualAllocationSnapshot`；
- 保留数值0；
- 继承分配备注；
- 保存`inherited_from_run_id`；
- 再分别比较 projection fingerprint 和合同收入预测。

不得按相似中心、日期、月份或源行进行模糊金额迁移。

### 10.2 规则矩阵

| 上期/本期情况 | 金额与备注 | 诊断 | `review_required` |
|---|---|---|---|
| ID精确命中，指纹和合同预测均相同 | 原样继承 | 无变化诊断 | `N` |
| ID精确命中，指纹变化 | 原样继承 | `PROJECTION_CHANGED` | `Y` |
| ID精确命中，合同预测变化 | 原样继承 | `CONTRACT_REVENUE_FORECAST_CHANGED` | `Y` |
| ID精确命中，两者都变化 | 原样继承 | 同时记录两项 | `Y` |
| 本期新增候选 | 不继承 | `CANDIDATE_ADDED` | `Y` |
| 上期候选消失且金额为`BLANK/UNAVAILABLE` | 无金额迁移 | `CANDIDATE_REMOVED` | 不适用当前行 |
| 上期候选消失且金额为`VALUE`，包括0 | 保留为待处理历史记录 | `ORPHANED_PREVIOUS_ALLOCATION` | `Y` |
| candidate ID版本不一致 | 禁止精确继承 | `CANDIDATE_ID_VERSION_MISMATCH`；按新增/消失处理 | `Y` |
| v0.8兼容结果 | 只用于履行比较 | `PREVIOUS_ALLOCATION_UNAVAILABLE` | 不伪造金额 |

### 10.3 履行投影变化

指纹变化时：

```text
candidate ID保持不变
projection_changed = Y
review_required = Y
```

历史金额和备注保留，不自动清空、不自动改写。Phase 2 不判断金额是否仍应有效；用户复核和 Phase 3 分配状态负责后续处理。

### 10.4 合同收入预测变化

同合同本期与上期：

```text
current.revenue_forecast != previous.revenue_forecast
→ CONTRACT_REVENUE_FORECAST_CHANGED
```

处理：

- 该合同所有当前候选设置`contract_forecast_changed=Y`；
- 精确命中的历史金额和备注继续保留；
- 所有当前候选设置`review_required=Y`；
- 不自动按比例调整、不截断、不补差；
- 不在 Phase 2 计算部分分配、超额或守恒状态。

### 10.5 候选拓扑变化

供应中心新增或消失按 candidate ID 集合差处理：

- 新中心形成 `CANDIDATE_ADDED`；
- 旧中心形成 `CANDIDATE_REMOVED`；
- 不把旧中心金额自动迁移到新中心；
- 合同由有要货变为不要货时，所有上期真实中心候选均视为消失；
- 合同由不要货恢复要货时，本期真实中心均视为新增；
- `CONTRACT_ONLY_NO_DEMAND`本身不生成候选。

### 10.6 ORPHANED_PREVIOUS_ALLOCATION

上期候选消失且：

```text
manual_allocation.amount_state = VALUE
```

必须生成结构化待处理记录：

```text
diagnostic_code = ORPHANED_PREVIOUS_ALLOCATION
previous_run_id
allocation_candidate_id
candidate_id_version
contract_no
supply_center
row_kind
previous_manual_amount
previous_allocation_note
previous_revenue_month_rpd
previous_revenue_month_cpd
previous_revenue_segment
previous_projection_fingerprint
```

明确数值0仍是历史人工决定，因此也生成该记录。该记录不进入本期正式分配或月度汇总。

上期只有备注、金额为`BLANK`时，`CANDIDATE_REMOVED`诊断仍保留备注快照，但不得标记为有金额的 `ORPHANED_PREVIOUS_ALLOCATION`。

## 11. 服务边界

建议新增：

```text
AllocationCandidateBuilder
- 选择可生成候选的FulfillmentProjection
- 调用CandidateIdFactory
- 调用ProjectionFingerprintService
- 保证候选ID唯一

CandidateIdFactory
- candidate ID v1规范化、序列化和哈希
- 固定测试向量

ProjectionFingerprintService
- projection fingerprint v1
- 明确包含和排除字段

PreviousRunStateBuilder
- 从结构化历史快照建立PreviousRunState
- 从v0.8 PreviousData建立只读兼容状态
- 不读取旧人工月份字段为分配决定

CandidateHistoryService
- ID精确匹配
- 继承金额和备注
- 新增/消失/投影变化/合同预测变化诊断
- ORPHANED_PREVIOUS_ALLOCATION
```

Application 可新增：

```text
build_phase2_models(...)
```

它只能作为内部组合器返回候选、历史匹配和诊断，不得改变生产`run_pipeline`返回值和写出流程。

## 12. 内部运行顺序

```text
build_phase1_models
→ ContractFinancialFact
→ DemandRecord
→ FulfillmentProjection
→ AllocationCandidateBuilder
→ 本期RevenueAllocationCandidate

可选PreviousData / 测试历史fixture
→ PreviousRunStateBuilder
→ PreviousRunState

本期候选 + PreviousRunState + 本期ContractFinancialFact
→ CandidateHistoryService
→ 继承快照 + 变化诊断 + orphaned历史分配
```

不调用 Excel Writer，不生成新的用户可见结果。

## 13. Phase 2 WRITE_SCOPE

允许修改或新增：

```text
src/revenue_tool/domain/revenue_models.py
src/revenue_tool/services/allocation_candidates.py
src/revenue_tool/services/candidate_identity.py
src/revenue_tool/services/projection_fingerprint.py
src/revenue_tool/services/previous_run_state.py
src/revenue_tool/services/candidate_history.py
src/revenue_tool/services/normalization.py（仅复用现有规范化所需的小型调整）
src/revenue_tool/application/pipeline.py（仅新增内部Phase 2组合器）
一个明确的v0.8 PreviousData兼容adapter文件
tests/test_allocation_candidates.py
tests/test_candidate_identity.py
tests/test_projection_fingerprint.py
tests/test_previous_run_state.py
tests/test_candidate_history.py
tests/test_revenue_allocation_phase2_golden.py
相关虚构fixture
docs/reviews/revenue-allocation-phase2-verification.md
Draft PR #25说明
```

如实现时可以在不降低边界清晰度的前提下合并小型服务文件，必须在验证报告中记录实际属主。

本阶段禁止修改：

```text
config/default.json
src/revenue_tool/adapters/excel_writer.py
src/revenue_tool/gui.py
src/revenue_tool/cli.py
README.md最终用户流程
项目版本号
GitHub Release
P1 EXE工作流
当前可见Sheet、列、样式和_tool_meta schema 3
```

除内部组合器外，不改变生产 `run_pipeline`。

## 14. 强制测试计划

### 14.1 candidate ID v1

- 固定测试向量精确匹配；
- NFKC与空白规范化；
- 供应中心大小写不影响ID；
- 合同号大小写按当前身份规则保留；
- 日期、月份、分段、金额和源行变化不改变ID；
- 合同号、供应中心、row_kind或版本变化改变ID；
- 无要货占位不生成候选；
- 空供应中心异常投影不生成候选；
- ID重复或冲突使测试失败。

### 14.2 projection fingerprint v1

- 固定字段顺序和 canonical JSON；
- 每个正式履行字段变化会改变指纹；
- 日期集合、状态集合和异常代码顺序变化不改变指纹；
- 源文件、Sheet、行号、`demand_record_id`变化不改变指纹；
- 合同金额和人工金额变化不改变指纹；
- 指纹变化不改变 candidate ID。

### 14.3 PreviousRunState

- metadata schema、candidate ID版本和run ID恢复；
- 合同事实、投影和候选唯一索引；
- `UNAVAILABLE`、`BLANK`、`VALUE`三态；
- 空白与明确0往返不混淆；
- 正数、负数、0和两位小数金额；
- v0.8 schema 2、3兼容；
- v0.8不伪造手工分配金额或备注；
- 重复candidate ID禁止继承。

### 14.4 历史继承和诊断

- 精确命中且无变化；
- 履行投影变化时保留金额与备注并要求复核；
- 合同收入预测变化时保留金额与备注并要求复核；
- 两种变化同时发生；
- 新增候选；
- 消失候选无金额；
- 消失候选有正数、负数和明确0金额；
- `ORPHANED_PREVIOUS_ALLOCATION`字段完整；
- ID版本不匹配不自动迁移；
- 有要货↔不要货候选集合变化；
- 多中心新增/消失逐候选诊断；
- note-only消失不伪造成历史金额。

### 14.5 Phase 1与生产兼容回归

- 当前96项测试全部继续通过；
- Phase 1 Golden 30字段仍一致；
- Issue #20精确差异不扩大；
- 当前生产`run_pipeline`仍只写五个可见Sheet和schema 3 `_tool_meta`；
- 基表32列、列顺序、人工月份字段和GUI流程不变；
- Phase 2内部对象不被 Excel Writer消费。

## 15. Golden与兼容门禁

### 15.1 Phase 1 Golden门禁

继续执行现有：

```text
ContractFinancialFact + FulfillmentProjection
→ LegacyProjectionAdapter
→ 与RevenueEngine自动字段逐项比较
```

唯一允许差异仍只有 Issue #20 的精确结转类型修正。

### 15.2 Phase 2身份Golden

提交固定 candidate ID 和 projection fingerprint 测试向量。算法、字段集合、规范化、JSON序列化或前缀发生变化时，测试必须失败并要求新的正式版本决策。

### 15.3 工作簿兼容门禁

同一虚构输入分别运行 Phase 2 前生产路径和加入 Phase 2 后生产路径，规范化比较：

- Sheet 名和顺序；
- 可见/隐藏状态；
- 字段 ID、显示名和列顺序；
- 单元格值与类型；
- 日期、金额格式；
- editable列；
- AutoFilter；
- `_tool_meta` schema与row_kind。

要求完全一致，不设置 Phase 2 预期差异。

## 16. 全量验证命令

至少执行：

```text
PYTHONPATH=src python -m unittest discover -s tests
PYTHONPATH=src python -m unittest -v tests.test_candidate_identity
PYTHONPATH=src python -m unittest -v tests.test_projection_fingerprint
PYTHONPATH=src python -m unittest -v tests.test_candidate_history
python -m compileall -q src tests
git diff --check
python -m pip wheel . --no-deps --wheel-dir <临时目录>/wheel
```

并检查：

```text
git diff --name-only <Phase 2基线>..HEAD
```

不得包含 WRITE_SCOPE 外生产文件。

## 17. Phase 2验证报告

实施完成后新增：

```text
docs/reviews/revenue-allocation-phase2-verification.md
```

至少记录：

- 实施基线和最终commit；
- 修改文件；
- candidate ID v1测试向量；
- projection fingerprint v1字段和排除项；
- PreviousRunState实际结构；
- 空白与0证据；
- 历史继承和变化诊断矩阵；
- v0.8兼容行为；
- orphaned历史金额证据；
- Phase 1 Golden与96项基线回归；
- 新增测试和全量测试结果；
- 生产工作簿零变化证据；
- 未进入Phase 3及以后范围；
- Phase 2 Gate结论。

## 18. 明确不在 Phase 2 实施

Phase 2 不实施：

- 单候选自动分配；
- 部分分配；
- 分配超额计算；
- 负数分配业务校验；
- 合同金额守恒；
- `RevenueAllocationDecision`正式计算；
- `ContractAllocationSummary`；
- `MonthlyRevenuePosting`；
- RPD/CPD月度收入汇总；
- 待处理收入正式输出；
- 新工作簿Sheet；
- 隐藏系统数据写入；
- 手工分配金额的Excel读取或写出；
- GUI重构；
- 旧三个人工月份字段迁移；
- 删除`RevenueEngine`、`BaseRow`、`PreviousData`；
- 合并Draft PR、发布版本或生成正式Release。

## 19. Phase 2完成标准

只有同时满足以下条件，才能声明 Phase 2 完成：

- `RevenueAllocationCandidate`明确实现；
- candidate ID v1与固定测试向量一致；
- projection fingerprint v1与candidate ID职责分离；
- `PreviousRunState`承载要求的投影、候选、历史金额、备注、合同预测、月份、分段和metadata；
- 空白、明确0和旧格式不可用三态不混淆；
- 精确继承、变化复核、新增、消失和orphan规则完整；
- v0.8兼容不伪造金额；
- Phase 1 Golden与全量现有测试通过；
- 当前生产工作簿完全不变；
- Phase 2验证报告已提交；
- Draft PR #25保持Draft；
- 未提前进入 Phase 3及以后范围。

