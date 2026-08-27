# 收入分配重构 V3 实施前就绪性审查

- 审查 ID：`REVENUE-ALLOCATION-REFACTOR-READINESS-V3-2026-08-27`
- 日期：`2026-08-27`
- 审查分支：`refactor/revenue-allocation-v1`
- 权威设计：`docs/refactor/revenue-allocation-refactor-v3.md`
- 状态：`READY_FOR_IMPLEMENTATION_APPROVAL`

## 1. 结论

V3 已纠正 V2 中“去重后一条要货明细直接等于一次独立发货并直接分配金额”的不可靠假设。

当前正式模型为：

```text
ContractFinancialFact
→ DemandRecord（证据）
→ FulfillmentProjection（归纳）
→ RevenueAllocationCandidate（人工判断上下文）
→ RevenueAllocationDecision（金额决定）
→ MonthlyRevenuePosting
→ RPD/CPD月度收入汇总
```

V3 已具备以下实施条件：

- 业务目标明确；
- 旧基表失效原因明确；
- 要货明细业务角色明确；
- 原字段和原计算规则保持边界明确；
- 合同金额、履行证据、分配决定和月度Posting粒度已分离；
- 用户手工分配表字段和证据范围已定义；
- 部分分配、待处理和金额守恒规则已定义；
- 两种收入年月口径和最终月度指标已定义；
- 现有代码复用、替换、阶段和验证门禁已定义。

当前尚未修改生产代码。用户确认V3第19节的关键实施边界后，可将设计状态改为`APPROVED_FOR_IMPLEMENTATION`并进入Phase 1。

## 2. 当前代码事实

### 2.1 输入层

当前代码已具备：

- 四类独立源文件；
- 当月订货可选；
- 按字段契约定位业务Sheet；
- exact→contains字段匹配；
- 空白/VALUE规范化；
- Decimal两位小数；
- 完全重复物理行去重；
- 源文件异常诊断。

结论：输入层大部分可复用。

### 2.2 领域模型

当前`BaseRow.values`混合：

- 合同级金额；
- 合同属性；
- 履行供应中心；
- 日期聚合；
- 收入年月；
- 收入分段；
- 人工字段。

结论：不能在BaseRow继续增加收入预测和人工金额字段；必须建立不同粒度的领域类型。

### 2.3 RevenueEngine

当前RevenueEngine同时承担：

- 合同全集；
- 合同金额和属性；
- 要货明细分组；
- 运输周期；
- 日期聚合；
- 到货日期；
- 收入年月；
- 收入分段；
- 人工继承；
- BaseRow构建。

结论：拆分为合同事实、履行投影、分配和月度归纳服务。

### 2.4 PreviousData

当前PreviousData按：

```text
合同号 + 履行供应中心
```

恢复旧基表和row_kind。

结论：替换为PreviousRunState，同时支持：

- 旧履行快照；
- 新candidate ID；
- 人工金额和备注；
- 候选变化；
- metadata schema。

### 2.5 比较服务

当前比较服务已经能够：

- 比较RPD/CPD收入年月；
- 识别有要货↔不要货状态；
- 生成供应提拉清单。

结论：逻辑可复用，但输入从用户可见BaseRow切换为隐藏FulfillmentProjection。

### 2.6 Writer与配置

当前Writer和配置固定：

- 五个可见Sheet；
- 基表32列；
- 一套BaseRow数据；
- 一个隐藏元数据Sheet。

结论：需要重写为多数据集输出契约。

### 2.7 GUI

当前GUI能够选择源文件、上期结果和输出路径，但完成摘要仍围绕：

- 基表行数；
- RPD/CPD变化；
- 供应提拉；
- 异常。

结论：保留单页文件选择结构，更新历史结果语义和结果摘要。

## 3. V3关键设计合理性

### 3.1 DemandRecord只作为证据

结论：合理。

原因：源表没有稳定发货/要货事件ID，同一中心可能存在多条状态记录。逐行分配会产生无法可靠继承、重复拆分和伪事件风险。

### 3.2 FulfillmentProjection继续按合同+中心

结论：合理。

原因：现有正式日期、到货日期和收入年月规则就在该粒度上定义，用户已确认计算规则和字段不变。

### 3.3 分配候选默认等于FulfillmentProjection

结论：是当前V1最小可靠人工判断粒度。

它不会恢复旧基表的金额问题，因为：

- 合同收入预测仍只存在于ContractFinancialFact；
- 候选行只显示重复的参考金额；
- 候选行真正可汇总的金额只有最终分配金额；
- 最终月度汇总只消费MonthlyRevenuePosting。

### 3.4 同中心多条记录的用户可判断性

结论：V3已通过宽表摘要和`要货记录明细`解决。

用户在分配行可看到：

- 要货记录数；
- 状态摘要；
- 源行摘要；
- 日期和派生标识；
- 两套到货日期和收入年月；
- 收入分段；
- 异常摘要。

### 3.5 部分分配

结论：符合用户确认。

已分配且可归月部分先进入月度结果，剩余金额保留在待处理收入。

### 3.6 RPD/CPD两种统计口径

结论：正确。

同一最终分配金额生成两种Posting，分别按两套收入年月归月，不维护两套手工金额。

### 3.7 月度汇总指标

V3定义：

```text
当月预测 = 订未发金额 + 发未收金额
未录入订货 = 去重合同数
```

`需判断`、`不要货`金额进入待处理收入。

该口径与用户当前确认一致，可进入实现。

## 4. 已知风险与控制

### R1 参考合同金额在收入分配表重复显示

控制：

- 列名明确`合同收入预测（参考，不可直接汇总）`；
- 真正可汇总合同金额只在合同收入预测Sheet；
- 月度汇总只读取最终分配金额；
- 自动测试扫描禁止使用参考金额生成Posting。

### R2 candidate ID稳定性

控制：

```text
candidate ID = 合同号 + 履行供应中心 + row_kind + 版本
```

日期和月份变化不改变ID，但设置projection_changed和review_required。

### R3 同中心内部未来确需拆分

V1明确不支持系统自动拆分。

未来只有在具备稳定业务事件ID或正式人工拆分规则后扩展，不能在V1猜测。

### R4 上期候选消失

控制：生成ORPHANED_PREVIOUS_ALLOCATION待处理记录，人工金额不得消失。

### R5 分配超额

控制：整合同不进入正式月度汇总，直到修正；不自动截断。

### R6 宽表可用性

控制：

- 冻结关键列；
- 黄色编辑列；
- 合理列宽；
- AutoFilter；
- `要货记录明细`承载完整证据；
- Windows Excel实机验收。

## 5. 实施Gate

进入Phase 1前必须完成：

- 用户确认V3第19节边界；
- V3状态改为`APPROVED_FOR_IMPLEMENTATION`；
- Draft PR继续使用独立重构分支；
- 新输出字段配置冻结；
- candidate ID版本冻结；
- Golden虚构样例提交；
- Phase 1 WRITE_SCOPE冻结；
- 不在Phase 1直接删除旧路径。

## 6. 审查回执

```text
旧临时Issue #21撤销：完成
要货明细业务角色修正：完成
实际代码审查：完成
V3目标模型：完成
用户分配上下文：完成
部分分配闭环：完成
RPD/CPD月度汇总：完成
金额守恒门禁：完成
生产代码修改：未开始
当前状态：READY_FOR_IMPLEMENTATION_APPROVAL
```
