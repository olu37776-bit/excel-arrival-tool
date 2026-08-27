# 收入分配重构 Phase 1 Operation Plan

- 文档 ID：`REVENUE-ALLOCATION-PHASE1-OPERATION-PLAN`
- 状态：`READY_FOR_IMPLEMENTATION`
- 日期：`2026-08-27`
- 实施分支：`refactor/revenue-allocation-v1`
- Draft PR：`#25`
- 权威设计：`docs/refactor/revenue-allocation-refactor-v3.md`
- 实施批准：`docs/decisions/DR-008-revenue-allocation-v3-implementation-approval.md`
- 本阶段：`Phase 1 — 领域拆分与双轨履行计算`

## 1. 阶段目标

Phase 1只完成以下事情：

1. 建立不同数据粒度的明确领域类型；
2. 将当前`RevenueEngine`中的合同事实与履行归纳职责拆开；
3. 保留当前生产结果路径，并建立新旧双轨Golden比较；
4. 修复Issue #20：结转类型按最终解析国家判断；
5. 证明除Issue #20外，现有字段和业务计算结果没有变化。

本阶段不建设人工金额、月度Posting、新工作簿或GUI新界面。

## 2. 权威输入与优先级

实施前必须读取：

1. `docs/refactor/revenue-allocation-refactor-v3.md`
2. `docs/decisions/DR-008-revenue-allocation-v3-implementation-approval.md`
3. `docs/reviews/revenue-allocation-refactor-readiness-v3-2026-08-27.md`
4. `docs/requirements-baseline.md`
5. `docs/source-schema.md`
6. `docs/output-schema.md`
7. `docs/comparison-output.md`
8. `docs/decisions/DR-001-manual-adjustment-fields.md`
9. `docs/decisions/DR-002-amount-arrival-segment-normalization.md`
10. `docs/decisions/DR-003-monthly-order-source-optional.md`
11. `docs/decisions/DR-004-country-filter-and-transit-diagnostics.md`
12. `docs/decisions/DR-005-retain-contract-without-demand-detail.md`
13. `docs/decisions/DR-006-no-demand-cross-period-visibility.md`
14. `docs/decisions/DR-007-stock-unlock-three-state-output.md`
15. Issue #20

优先级：

```text
DR-008 / V3
> DR-007..DR-001
> requirements/source/output/comparison
> 当前代码、配置和测试
```

V1、V2重构文档不得作为实施依据。

## 3. 当前代码事实

当前主要耦合位于：

```text
src/revenue_tool/services/calculation.py
```

`RevenueEngine.calculate()`同时负责：

- 合同全集；
- 遗留量、当月新订货和合同属性；
- 要货记录按合同和供应中心分组；
- 海运周期；
- 日期聚合；
- 货未发完；
- 两套到货日期；
- 两套收入年月；
- 收入分段；
- 人工字段继承；
- BaseRow构建。

当前`BaseRow`混合合同级金额和履行级字段，不适合作为新模型核心。

## 4. Phase 1目标领域类型

建议新增独立模块：

```text
src/revenue_tool/domain/revenue_models.py
```

至少定义：

### 4.1 ContractFinancialFact

粒度：合同号。

至少包含：

- contract_no；
- legacy_amount；
- monthly_new_order；
- revenue_forecast；
- bg；
- region；
- country；
- carryover_type；
- customer_group；
- project_name；
- demand_state。

约束：

```text
revenue_forecast = legacy_amount + monthly_new_order
```

每个合同只能生成一条。

### 4.2 DemandRecord

粒度：去重后的一条要货明细证据记录。

至少包含：

- demand_record_id（仅本次运行追溯，不作为跨期人工金额主键）；
- contract_no；
- supply_center；
- demand_status；
- incoterm；
- stock_control_flag；
- shipment_control_flag；
- ata；
- asd；
- rpd；
- cpd；
- bg；
- source_workbook；
- source_sheet；
- source_row_number；
- invalid_fields。

DemandRecord不得包含：

- legacy_amount；
- monthly_new_order；
- revenue_forecast；
- 手工分配金额。

### 4.3 FulfillmentProjection

粒度：合同号 + 履行供应中心；无要货合同允许受控占位状态。

至少包含当前既有履行结果：

- contract_no；
- supply_center；
- row_kind；
- multiple_supply_centers；
- demand_record_count；
- demand_status_summary；
- source_row_summary；
- incoterm；
- stock_unlocked；
- split_shipment；
- transit_days；
- ata；
- asd；
- rpd；
- multiple_demand；
- latest_asd；
- latest_rpd；
- shipment_incomplete；
- cpd；
- split_supply；
- arrival_date_rpd；
- arrival_date_cpd；
- revenue_month_rpd；
- revenue_month_cpd；
- revenue_segment；
- issue_codes或等价引用。

FulfillmentProjection不得拥有合同收入预测权威金额。

## 5. Phase 1服务拆分

建议新增：

```text
src/revenue_tool/services/contract_finance.py
src/revenue_tool/services/demand_records.py
src/revenue_tool/services/fulfillment_projection.py
```

### 5.1 ContractFactBuilder

职责：

- 生成动态合同全集；
- 遗留量、当月新订货和合同属性；
- revenue_forecast；
- 最终国家；
- 结转类型；
- 合同是否存在要货。

必须落实Issue #20：

```text
resolved_country = 遗留量国家 → 要货明细国家
carryover_type基于resolved_country判断
```

不能继续只使用legacy_country判断。

### 5.2 DemandRecordService

职责：

- 从Reader输出的去重`ParsedRow`建立DemandRecord；
- 保留源文件、Sheet、行号证据；
- 生成本次运行可追溯的demand_record_id；
- 不进行合同金额计算；
- 不将每条记录解释为独立发货。

本阶段不要求稳定跨期事件ID。

### 5.3 FulfillmentProjectionService

职责：

- 按合同号+履行供应中心归纳DemandRecord；
- 完整复用当前海运周期、日期、货未发完、到货日期、收入年月、收入分段和备货三态规则；
- 生成无要货合同占位Projection；
- 生成需求状态、源行和日期集合摘要；
- 不处理合同金额分配；
- 不读取或继承人工金额。

建议将当前`calculation.py`中的纯规则函数抽出或复用，禁止复制两套业务算法长期并存。

## 6. 双轨策略

Phase 1必须保留当前旧路径用于Golden验证。

允许选择以下任一安全实现：

### 方案A（推荐）

```text
生产run_pipeline仍使用旧RevenueEngine输出v0.8工作簿
新ContractFactBuilder/FulfillmentProjectionService由Phase 1测试和内部组合器调用
```

Phase 1结束时不改变用户可见工作簿。

### 方案B

```text
生产内部先运行新模型
通过LegacyBaseRowAdapter转换为旧BaseRow写出
旧RevenueEngine只在Golden测试运行
```

只有在完整Golden证明通过后才允许采用方案B。

无论选择哪种方案，都必须：

- 旧路径可独立运行；
- 新路径可独立运行；
- 同一虚构输入可逐字段比较；
- 不在本阶段删除旧RevenueEngine、BaseRow或PreviousData。

## 7. Golden比较契约

建立新旧组合结果比较器，仅用于测试/验证。

将：

```text
ContractFinancialFact + FulfillmentProjection
```

映射为旧BaseRow可比视图。

逐业务键比较：

- 合同号；
- 遗留量；
- 当月新订货；
- BG；
- 地区部；
- 国家；
- 结转类型；
- 客户群；
- 项目名称；
- 贸易术语；
- 履行供应中心；
- 多个供应中心发货；
- 是否解锁备货；
- 分批发货；
- 海运周期；
- ATA；
- ASD；
- RPD；
- 多次要货；
- 最晚ASD；
- 最晚RPD；
- 货未发完；
- CPD；
- 分批供应；
- 到货日期（按RPD）；
- 到货日期（按CPD）；
- 收入年月（按RPD）；
- 收入年月（按CPD）；
- 收入分段类别；
- row_kind。

旧三个人工字段不属于新领域模型。本阶段旧输出仍按现有路径保持；Golden只验证自动业务字段。

允许的唯一预期差异：

```text
Issue #20导致的结转类型修正
```

该差异必须有明确测试，不能被通配忽略。

## 8. WRITE_SCOPE

Phase 1允许修改或新增：

```text
src/revenue_tool/domain/models.py
src/revenue_tool/domain/revenue_models.py
src/revenue_tool/services/calculation.py
src/revenue_tool/services/contract_finance.py
src/revenue_tool/services/demand_records.py
src/revenue_tool/services/fulfillment_projection.py
src/revenue_tool/services/normalization.py（仅必要的小型复用重构）
src/revenue_tool/application/pipeline.py（仅双轨组合所需，不改变输出契约）
tests/*
tests/fixtures/*
docs/reviews/revenue-allocation-phase1-verification.md
Draft PR #25说明
```

如需新增一个明确的Golden/legacy adapter文件，可以新增，例如：

```text
src/revenue_tool/services/legacy_projection_adapter.py
```

不得修改：

```text
config/default.json的输出Sheet/字段契约
src/revenue_tool/adapters/excel_writer.py
src/revenue_tool/gui.py
src/revenue_tool/cli.py
README中的最终用户流程
发布版本号
GitHub Release
```

除修Issue #20所必需外，不改变当前用户可见结果。

## 9. 强制测试

至少新增：

```text
tests/test_contract_finance.py
tests/test_demand_records.py
tests/test_fulfillment_projection.py
tests/test_fulfillment_projection_golden.py
```

必须覆盖：

### 9.1 ContractFinancialFact

- 每合同唯一；
- revenue_forecast正确；
- 当月订货文件未提供；
- 当月订货合同无匹配；
- Decimal正、负、零金额；
- 多供应中心不复制合同事实；
- 无要货合同仍有合同事实；
- 最终国家回退；
- Issue #20七国归类。

### 9.2 DemandRecord

- 去重后记录数量；
- 源证据完整；
- 本次运行ID稳定于同一输入；
- 不包含合同金额；
- 同中心多状态记录仍保留为多条证据；
- 不把DemandRecord命名或断言为独立ShipmentEvent。

### 9.3 FulfillmentProjection

- 单中心；
- 多中心；
- 同中心多记录；
- 无要货占位；
- 有合同但中心为空的异常边界；
- 日期聚合；
- 货未发完；
- 海运周期；
- 两套到货日期；
- 两套收入年月；
- 收入分段；
- 备货三态；
- 状态/源行摘要。

### 9.4 Golden

至少覆盖：

- 常规单中心；
- 多中心；
- 同中心多状态记录；
- 多次要货；
- 分批供应；
- FCA/FOB/EXW；
- 普通运输周期；
- 运输周期异常；
- 无要货合同；
- 要货合同中心为空；
- 空白/VALUE；
- 浮点金额；
- 七国最终国家回退。

## 10. 全量验证

必须运行项目现有全部测试，不只运行新增测试。

至少执行：

```text
python -m unittest discover -s tests
python -m compileall -q src tests
git diff --check
python -m pip wheel . --no-deps --wheel-dir <temp>/wheel
```

如项目环境使用不同命令，以仓库实际入口为准，但报告中必须给出完整命令和结果。

## 11. Phase 1验证报告

必须新增：

```text
docs/reviews/revenue-allocation-phase1-verification.md
```

至少包括：

- 基线commit；
- 修改文件；
- 新领域类型；
- 旧RevenueEngine拆分映射；
- 双轨方案选择；
- Golden字段和场景；
- Issue #20证据；
- 新增测试与全量测试结果；
- 仍保留的旧路径；
- 未进入Phase 2的范围；
- 已知风险；
- Phase 1 Gate结论。

## 12. 完成标准

只有同时满足以下条件，才能声明Phase 1完成：

- ContractFinancialFact、DemandRecord、FulfillmentProjection已实现；
- 合同事实和履行投影职责已从旧大函数中形成清晰边界；
- 新旧路径都可运行；
- Golden除Issue #20外完全一致；
- Issue #20修复并有测试；
- DemandRecord不承载合同金额；
- FulfillmentProjection不成为合同金额权威表；
- 现有全部测试通过；
- Phase 1验证报告已提交；
- Draft PR #25更新；
- 未提前实现Phase 2及以后范围。

完成后只可申请进入Phase 2，不得直接宣称整个重构完成。
