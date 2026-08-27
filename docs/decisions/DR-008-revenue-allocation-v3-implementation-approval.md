# DR-008 收入分配重构 V3 实施批准

- 状态：`CONFIRMED`
- 日期：`2026-08-27`
- 适用分支：`refactor/revenue-allocation-v1`
- 关联 Draft PR：`#25`
- 权威设计：`docs/refactor/revenue-allocation-refactor-v3.md`
- 关联审查：`docs/reviews/revenue-allocation-refactor-readiness-v3-2026-08-27.md`

## 1. 决策

业务方确认采用 V3 当前边界并开始分阶段实施。

即日起：

```text
docs/refactor/revenue-allocation-refactor-v3.md
```

视为：

```text
APPROVED_FOR_IMPLEMENTATION
```

V3 文件头中尚未同步修改的旧状态文字，不再阻塞实施；本决策是实施 Gate 的正式批准记录。

V1、V2仅保留讨论历史，不得作为生产代码实施依据。

## 2. 已批准的核心模型

```text
ContractFinancialFact
合同级金额唯一事实
        ↓
DemandRecord
要货/履行过程证据记录
        ↓
FulfillmentProjection
合同号 + 履行供应中心的既有规则归纳结果
        ↓
RevenueAllocationCandidate
用户填写金额时的判断上下文
        ↓
RevenueAllocationDecision
人工或自动金额决定
        ↓
MonthlyRevenuePosting
同一金额分别按RPD、CPD两种口径归月
        ↓
RPD月度收入汇总 / CPD月度收入汇总
```

## 3. 分配粒度批准

V1默认：

```text
一条 FulfillmentProjection
→ 一条 RevenueAllocationCandidate
```

即默认候选粒度为：

```text
合同号 + 履行供应中心
```

该粒度只是用户分配判断上下文，不是合同金额事实粒度。

以下边界同时确认：

- DemandRecord只作为业务证据，不直接分配合同金额；
- 不能把去重后每条要货明细物理行认定为一次独立发货；
- 同中心多条要货/状态记录继续按既有规则归纳为FulfillmentProjection；
- 用户可在收入分配表查看记录数、状态、日期集合、源行摘要、归月结果和异常摘要；
- 后续确需在同一中心内部进一步拆分金额时，必须先新增稳定批次/事件标识或新的正式人工拆分规则，不在V1猜测。

## 4. 金额与人工输入批准

合同级金额：

```text
收入预测 = 遗留量 + 当月新订货
```

每合同只存在一次。

用户填写：

```text
手工分配金额
分配备注
```

系统计算：

- 自动分配金额；
- 最终分配金额；
- 已分配金额；
- 待分配金额；
- 分配状态；
- 分配比例；
- 两种统计口径的已归月/待归月金额。

空白表示尚未决定；数值0表示明确分配0，二者必须区分。

允许部分分配：已确认且可归月的部分先进入月度结果，剩余金额进入待处理收入。

旧三个人工月份字段废弃：

- 是否手工调整收入月份；
- 手工调整收入月份；
- 调整备注。

不得迁移为新的金额分配决定。

## 5. 原字段和计算规则保持不变

本重构不修改当前正式定义的：

- 源文件和源字段；
- 空值/VALUE规范化；
- Decimal两位小数金额；
- 完全重复行去重；
- 合同属性来源；
- 履行供应中心分组；
- ATA/ASD/RPD/最晚ASD/最晚RPD/CPD聚合；
- 货未发完；
- 海运周期；
- 到货日期（按RPD）；
- 到货日期（按CPD）；
- 收入年月（按RPD）；
- 收入年月（按CPD）；
- 收入分段基础规则；
- 是否解锁备货三态；
- 不要货状态；
- RPD/CPD跨期变化；
- 供应需要提拉诉求；
- 异常诊断。

Issue #20是批准的规则修正：结转类型按最终解析国家判断。

## 6. 最终月度输出批准

分别输出：

```text
RPD月度收入汇总
CPD月度收入汇总
```

共同字段：

1. 收入年月；
2. BG；
3. 地区部；
4. 国家；
5. 结转类型；
6. 客户群；
7. 当月预测；
8. 订未发；
9. 发未收；
10. 未录入订货（合同数）。

定义：

```text
当月预测 = 订未发金额 + 发未收金额
```

`未录入订货`按去重合同数统计，不按金额统计。

`需判断`、`不要货`以及无法取得收入年月的已分配金额进入待处理收入，不进入正式当月预测。

RPD、CPD是同一批分配金额的两种统计口径，不能相加作为总收入。

## 7. 金额守恒批准

每合同：

```text
已分配金额 + 待分配金额 = 收入预测
```

RPD口径：

```text
RPD已归月 + RPD待归月 + 合同未分配 = 收入预测
```

CPD口径：

```text
CPD已归月 + CPD待归月 + 合同未分配 = 收入预测
```

任何不守恒都必须成为验证失败或明确待处理记录，不能静默纠正。

## 8. 分阶段实施

批准按V3第17节分阶段推进。

当前只开放：

```text
Phase 1：领域拆分与双轨履行计算
```

Phase 1完成并独立验证通过后，才能进入Phase 2。

后续阶段不得在Phase 1中提前混入，以避免无法确认旧计算规则是否保持一致。

## 9. Phase 1 Gate

Phase 1必须至少达到：

- 新增ContractFinancialFact、DemandRecord、FulfillmentProjection明确类型；
- 从RevenueEngine拆出合同事实和履行投影服务；
- 旧计算路径暂时保留用于双轨Golden比较；
- 除Issue #20批准修正外，既有履行字段逐项一致；
- ContractFinancialFact每合同唯一；
- DemandRecord不承载合同金额；
- FulfillmentProjection不作为合同收入预测权威表；
- 全量现有测试通过；
- 新Golden与架构测试通过；
- 形成Phase 1验证报告；
- 不提前删除旧输出、GUI或历史读取路径。

## 10. 当前未开放范围

Phase 1不得实施：

- 人工金额读写；
- RevenueAllocationCandidate正式输出；
- PreviousRunState金额继承；
- 部分分配；
- MonthlyRevenuePosting；
- RPD/CPD月度汇总；
- 新工作簿全部Sheet；
- GUI新结果摘要；
- 删除旧BaseRow/PreviousData兼容路径。

这些内容留待后续Phase按Gate推进。
