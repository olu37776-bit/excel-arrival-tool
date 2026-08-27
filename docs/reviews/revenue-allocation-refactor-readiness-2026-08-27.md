# 收入分配重构实施前就绪性审查

- 审查 ID：`REVENUE-ALLOCATION-REFACTOR-READINESS-2026-08-27`
- 日期：`2026-08-27`
- 审查分支：`refactor/revenue-allocation-v1`
- 设计文档：`docs/refactor/revenue-allocation-refactor-v1.md`
- 状态：`NOT_READY_PENDING_BUSINESS_DECISIONS`

## 1. 结论

当前已经完成：

- 撤销Issue #21中的旧基表临时修补方案；
- 从最新main建立独立重构分支；
- 对当前输入、领域计算、历史导入、比较、输出、GUI和测试结构做代码级审查；
- 建立合同金额、要货事件、履行投影、分配单元和月度汇总的目标模型；
- 明确原字段和原履行计算规则继续保留；
- 明确RPD/CPD是同一金额的两种统计口径；
- 明确每种统计口径的金额守恒门禁；
- 给出分阶段实施、WRITE_SCOPE、迁移和验证计划。

当前尚不能开始生产代码实施，原因是设计文档第18节的五项业务决策尚未确认。

## 2. 当前代码可复用能力

| 能力 | 结论 | 现有位置 |
|---|---|---|
| 四类源文件读取 | 可复用 | `adapters/excel_reader.py` |
| 可选当月订货 | 可复用 | `SourceFiles`、Reader、GUI、Pipeline |
| Sheet按字段契约定位 | 可复用 | `adapters/sheet_locator.py` |
| 字段匹配 | 可复用 | `services/field_matching.py` |
| 空值/VALUE规范化 | 可复用 | `services/normalization.py` |
| Decimal两位小数金额 | 可复用 | `services/normalization.py` |
| 完全重复行去重 | 可复用 | `adapters/excel_reader.py` |
| 七国国家identity | 可复用并修Issue #20 | `normalize_country_identity`、`calculation.py` |
| 运输周期与异常分型 | 可复用 | `services/calculation.py` |
| 备货三态 | 可复用 | `services/stock_unlock.py` |
| 既有日期/到货规则 | 必须抽取并回归 | `services/calculation.py` |
| 不要货领域状态 | 可复用 | `domain/models.py`、`comparison.py` |
| RPD/CPD跨期变化 | 可复用但切换数据源 | `services/comparison.py` |
| Excel AutoFilter | 可复用并实机回归 | `adapters/excel_writer.py` |

## 3. 当前代码必须重构的边界

### 3.1 BaseRow不是新模型的可持续核心

`BaseRow.values`把合同金额、履行计算、状态和人工字段放在同一字典中，缺少粒度隔离。

结论：

- 不在BaseRow上追加收入预测和分配字段；
- 新增明确领域类型；
- BaseRow仅允许在过渡期作为旧结果兼容类型。

### 3.2 RevenueEngine职责过多

当前一个服务同时负责合同事实、履行聚合、日期、分段、人工继承和输出行构建。

结论：拆成合同事实、履行投影、分配和月度归纳服务。

### 3.3 PreviousData只支持旧基表

当前历史导入以合同号+中心为键，只能读取旧人工字段和自动月份。

结论：替换为`PreviousRunState`，同时承载履行快照和人工分配决定。

### 3.4 Writer和Config硬编码旧输出

当前只支持五个Sheet和固定32列。

结论：输出配置升级为多数据集契约，Writer按数据集元数据写出。

## 4. 设计合理性检查

### 4.1 金额粒度

```text
合同号
```

结论：正确。可从根本上消除多中心重复金额。

### 4.2 履行计算粒度

```text
合同号 + 履行供应中心
```

结论：作为既有规则的内部计算粒度继续保留，不再作为最终金额事实。

### 4.3 分配单元粒度

推荐：

```text
合同号 + 收入年月（按RPD） + 收入年月（按CPD）
```

结论：对最终两个统计口径而言是最小无损粒度；相同月份组合内按中心继续拆金额不会改变最终月度汇总。

仍需业务确认用户是否有中心级金额管理需求。

### 4.4 一次分配、两种口径

结论：正确。

同一个`final_allocated_amount`分别根据两个收入年月字段归入RPD和CPD统计，不维护两套分配金额。

### 4.5 待归月机制

结论：必要。

不能因为月份或分配不确定就让合同金额消失，也不能强行塞入伪造月份。

## 5. 与旧规则的一致性

设计不改变：

- 源字段；
- 日期聚合；
- 货未发完；
- 海运周期；
- 到货日期；
- 收入年月；
- 收入分段基础规则；
- 不要货状态；
- 备货三态；
- 跨期变化；
- 供应提拉；
- 异常诊断。

唯一已知需要业务修正的现有逻辑是Issue #20：结转类型改为按最终解析国家判断。

## 6. 主要风险

### R1 人工字段粒度迁移

旧三个人工月份字段按合同+中心维护，新分配单元可能合并多个中心。

未确认时不能实现自动迁移。

### R2 用户输入方式

金额和比例两种输入方式会直接影响Excel字段、校验和继承逻辑。

### R3 部分分配展示

是否把部分已确认金额先纳入月度汇总会影响财务使用口径。

### R4 输出Sheet数量和用户认知

设计包含核心表、辅助表和隐藏表。实施前需要冻结哪些表默认可见。

### R5 旧结果兼容

v0.8结果无分配信息。首次重构运行必须明确哪些字段可迁移、哪些必须重新填写。

## 7. 实施Gate

只有以下条件同时满足才允许开始Phase 1：

- OD-001至OD-005确认；
- 设计文档状态为`APPROVED_FOR_IMPLEMENTATION`；
- 输出字段与Sheet冻结；
- allocation_unit_id定义冻结；
- 旧人工字段迁移规则冻结；
- Draft PR继续使用独立重构分支；
- Phase 1只做领域拆分和双轨Golden验证，不直接删除旧路径。

## 8. 审查回执

```text
当前代码事实审查：完成
旧临时Issue撤销：完成
独立重构分支：完成
目标模型：已建立
计算规则保持边界：已确认
输出闭环：已设计
自动/人工分配规则：待业务确认
实施状态：NOT READY
```
