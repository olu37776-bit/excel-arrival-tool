# 收入分配与月度汇总重构方案 V2

- 文档 ID：`REVENUE-ALLOCATION-REFACTOR-V2`
- 状态：`DRAFT_PENDING_2_BUSINESS_DECISIONS`
- 日期：`2026-08-27`
- 仓库：`olu37776-bit/excel-arrival-tool`
- 重构分支：`refactor/revenue-allocation-v1`
- Draft PR：`#25`
- 当前生产基线：`main / v0.8.0`
- 取代文档：`docs/refactor/revenue-allocation-refactor-v1.md`
- 已撤销临时方案：Issue `#21`
- 仍需回归/落实：Issue `#10`、Issue `#20`

> V2 是当前重构唯一权威设计入口。V1 保留为讨论历史，不得作为代码实施依据。当前仅允许继续完善设计、Schema、测试计划和虚构样例；第 16 节两个开放决策关闭前，不开始生产代码重构。

---

## 1. 重构目标

用户最终目标是：

```text
把合同收入预测金额分配给实际要货/发货事件
→ 同一份分配金额分别按RPD、CPD两种收入年月口径归月
→ 按月份汇总
→ 允许用户只完成部分分配
→ 未分配或无法归月的金额始终可见
```

本次重构不是修改已经确认的字段和履行计算公式，而是修正旧输出模型无法继续处理金额、人工分配和月度汇总的问题。

旧最终输出的核心粒度是：

```text
合同号 + 履行供应中心
```

但以下金额属于合同级：

```text
遗留量
当月新订货
收入预测 = 遗留量 + 当月新订货
```

旧基表将合同金额复制到每个供应中心行，因此不能作为可直接求和的收入事实表。

重构后必须满足：

```text
合同金额只存在一次
人工金额只分配一次
RPD和CPD只是两种统计口径
部分分配允许先进入月度结果
任一口径中金额不能重复、不能消失
```

---

## 2. 已确认业务决策

### BD-001 手工输入金额

用户填写：

```text
手工分配金额
```

系统计算：

```text
分配比例 = 最终分配金额 / 合同收入预测
```

用户不填写比例。

### BD-002 允许部分分配

当本次数据只涵盖合同周期的一部分时，用户可以只分配当前已确认部分。

例如：

```text
合同收入预测 = 100
已确认事件分配 = 40
尚未分配 = 60
```

系统必须：

- 将可归月的 40 纳入月度结果；
- 将 60 保留为待分配金额；
- 不自动把 60 平均分配或塞入任意月份；
- 保持合同金额守恒。

### BD-003 分配对象是一次发货/要货事件

收入金额不是分给供应中心，也不是先按RPD/CPD月份组合合并后再分配。

用户的业务操作对象是：

```text
一次真实要货/发货事件
```

当前源数据中，要货明细去除完全重复行后的真实记录，是事件事实的候选来源。

因此 V2 不再采用 V1 的以下建议：

```text
合同号 + 收入年月（按RPD） + 收入年月（按CPD）
→ 合并为一个金额分配单元
```

相同月份的多个事件仍可以分别分配金额。最终月度汇总再按收入年月合并。

### BD-004 旧三个人工月份字段废弃

以下旧字段不进入新输出契约：

- 是否手工调整收入月份；
- 手工调整收入月份；
- 调整备注。

旧字段原本承担的人工处理诉求，改由新字段承接：

- 手工分配金额；
- 分配备注。

V1 不迁移旧三个人工字段，也不让人工月份覆盖自动计算的RPD/CPD收入年月。

### BD-005 RPD和CPD是两种统计口径

金额只分配一次。

同一笔事件分配金额分别根据：

- `收入年月（按RPD）`；
- `收入年月（按CPD）`；

生成两种月度统计结果。

禁止：

- 为RPD单独维护一套手工金额；
- 为CPD再维护另一套手工金额；
- 将RPD汇总和CPD汇总相加作为总收入。

### BD-006 最终按月份呈现

最终用户结果必须围绕月份呈现，而不是围绕旧合同+供应中心基表呈现。

月度输出至少需要表达：

- 当月预测；
- 订未发；
- 发未收；
- 未录入订货。

这四项的精确度量含义见第 16.2 节，尚需最后确认。

---

## 3. 不改变的输入与字段契约

### 3.1 输入文件

```text
遗留量 Excel          必选
当月订货 Excel        可选
要货明细 Excel        必选
国家运输周期 Excel    必选
上一次结果 Excel      可选
```

四类业务源仍为独立文件。

继续复用：

- 自动Sheet名支持；
- 按字段契约定位业务Sheet；
- exact → contains唯一匹配；
- 字段歧义和Sheet歧义诊断；
- 当月订货整个文件可选。

### 3.2 源字段

遗留量、当月订货、要货明细、国家运输周期现有稳定内部字段ID保持不变。

要货明细继续读取：

- 原合同号；
- 地区部；
- 国家中文名称；
- 签约客户群；
- 交付项目中文名称；
- 需求状态；
- 供应中心简称；
- 贸易术语；
- 备货总控标识；
- 发货总控标识；
- 天_ATA；
- ASD日期；
- RPD日期；
- CPD日期；
- BG_CN。

当前字段契约中没有已确认的稳定事件ID字段。该问题见第 16.1 节。

### 3.3 空值与金额精度

继续执行：

```text
空单元格 / 空白字符 / (空白) / VALUE标记
金额 → 0
日期 → None
文本与标识 → 空
```

金额继续统一使用：

```text
Decimal(str(raw_value))
→ ROUND_HALF_UP量化到0.01
```

合同事实、事件分配、守恒校验和月度汇总必须共享同一规范化金额。

---

## 4. 不改变的业务计算规则

现有字段、公式和优先级继续保留。

### 4.1 合同级字段

继续使用：

- 遗留量；
- 当月新订货；
- BG；
- 地区部；
- 国家；
- 结转类型；
- 客户群；
- 项目名称。

其中：

```text
收入预测 = 遗留量 + 当月新订货
```

收入预测只在合同粒度计算一次。

Issue #20 在本重构中落实：

```text
先解析最终国家：遗留量国家 → 要货明细国家
最终国家属于七国 → 结转类型 = 交付类
```

### 4.2 履行字段与规则

以下字段继续保留：

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
- 收入分段类别。

### 4.3 日期聚合

当前合同+履行供应中心汇总规则继续保留，用于履行汇总、跨期变化和既有业务分析：

```text
ATA = MAX(天_ATA)
ASD = MAX(ASD日期)
RPD = MIN(RPD日期)
最晚ASD = MAX(ASD日期)
最晚RPD = MAX(RPD日期)
CPD = MAX(CPD日期)
```

### 4.4 货未发完

```text
最晚RPD为空 → 空
最晚RPD有效、最晚ASD为空 → Y
最晚RPD > 最晚ASD → Y
最晚RPD <= 最晚ASD → N
```

### 4.5 到货日期

```text
到货日期（按RPD）：
货未发完 != Y：ATA优先，否则ASD+海运周期
货未发完 = Y：最晚RPD+海运周期

到货日期（按CPD）：
货未发完 != Y：ATA优先，否则ASD+海运周期
货未发完 = Y：CPD+海运周期
```

### 4.6 收入年月

```text
收入年月（按RPD） = 到货日期（按RPD）的年月
收入年月（按CPD） = 到货日期（按CPD）的年月
```

### 4.7 收入分段

继续保留现有：

- 需判断；
- 发未收；
- 订未发；
- 未录入订货；
- 不要货。

无要货合同继续使用显式状态，不因金额非0改判为其他分类。

### 4.8 其他规则

继续保留：

- 完全重复行先去重；
- 是否解锁备货三态；
- 海运周期固定5天和查表异常分型；
- RPD/CPD跨期变化；
- 有要货↔不要货状态变化；
- 供应需要提拉诉求；
- Excel AutoFilter和“数据→清除”验收。

---

## 5. 当前代码事实

### 5.1 可复用

当前代码已经具备：

- `ExcelInputAdapter`：源文件读取、完全重复去重、空值和类型解析；
- `sheet_locator.py`：按字段契约识别业务Sheet；
- `field_matching.py`：统一字段匹配；
- `normalization.py`：文本、国家identity、金额精度；
- `calculation.py`：合同事实、履行汇总、运输周期、日期、分段；
- `stock_unlock.py`：备货三态；
- `comparison.py`：普通月份变化和有要货/不要货状态变化；
- `excel_writer.py`：AutoFilter、冻结首行、格式和隐藏元数据；
- `gui.py`：四源文件和上一次结果选择。

### 5.2 必须重构

当前问题集中在：

- `BaseRow.values`混合多个业务粒度；
- `RevenueEngine`同时承担合同、履行、日期、分段和输出行构建；
- `PreviousData`只支持旧合同+中心基表；
- Writer和配置固定五个Sheet和32列；
- GUI只表达一次生成旧基表，不表达人工分配闭环；
- 合同金额在多个中心行重复展示。

### 5.3 旧合同+中心基表的定位

旧基表不再作为最终用户收入处理入口。

其计算结果转为内部：

```text
FulfillmentSummary
```

用于：

- 保留原履行计算规则；
- RPD/CPD跨期变化；
- 有要货/不要货状态；
- 供应提拉；
- 规则回归和审计。

用户不再依赖该表汇总合同金额。

---

## 6. 目标领域模型

### 6.1 ContractFinancialFact

粒度：

```text
合同号
```

字段至少包括：

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

约束：每合同恰好一条。

### 6.2 DemandEventRecord

粒度：

```text
去除完全重复后的要货明细真实记录
```

它表示一次要货/发货事件的源事实候选，保留：

- 事件身份；
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
- 源文件、Sheet和行号；
- 原始字段证据。

`source row number`只用于证据，不得单独作为跨运行稳定事件ID。

### 6.3 FulfillmentSummary

粒度：

```text
合同号 + 履行供应中心
```

由DemandEventRecord按现有规则聚合。

它保留旧32字段中履行相关计算，但不再承载合同级金额权威事实。

### 6.4 ShipmentAllocationLine

粒度：

```text
一次真实发货/要货事件
```

用户对该行填写一次金额。

字段至少包括：

- shipment_event_id；
- contract_no；
- supply_center；
- demand_status；
- ATA / ASD / RPD / CPD；
- 到货日期（按RPD）；
- 到货日期（按CPD）；
- 收入年月（按RPD）；
- 收入年月（按CPD）；
- revenue_segment；
- contract_revenue_forecast_reference；
- auto_allocated_amount；
- manual_allocated_amount；
- final_allocated_amount；
- allocation_note；
- allocation_status。

金额分配粒度不再是供应中心，也不再是月份组合。

### 6.5 MonthlyRevenuePosting

同一ShipmentAllocationLine的最终分配金额生成两条统计Posting：

```text
RPD口径Posting
CPD口径Posting
```

两条Posting引用同一个最终分配金额，不复制成两笔业务收入。

字段至少包括：

- perspective：RPD / CPD；
- shipment_event_id；
- contract_no；
- revenue_month；
- revenue_segment；
- posted_amount；
- pending_amount；
- posting_status；
- contract dimensions。

### 6.6 MonthlyRevenueSummary

分别按RPD、CPD两种统计口径，从MonthlyRevenuePosting汇总。

最终展示字段见第 9 节和第 16.2 节。

### 6.7 PreviousRunState

替代旧`PreviousData`，至少承载：

- 上期FulfillmentSummary，用于跨期变化；
- 上期ShipmentAllocationLine人工金额；
- shipment_event_id版本；
- metadata schema；
- run_id和规则版本。

---

## 7. 人工分配规则

### 7.1 单事件合同

合同只有一个可分配事件时，可以自动：

```text
auto_allocated_amount = revenue_forecast
```

用户仍可在后续业务决定允许时覆盖；V1默认自动全额并锁定自动金额，不把它写入手工输入列。

### 7.2 多事件合同

合同有多个事件时：

- 系统不平均；
- 系统不按事件数分配；
- 系统不按供应中心数分配；
- 用户填写各事件的`手工分配金额`；
- 允许只填写部分事件。

### 7.3 最终分配金额

```text
存在有效手工分配金额 → 使用手工金额
否则存在自动分配金额 → 使用自动金额
否则 → 未分配
```

空单元格表示未决定；数值0表示明确分配0。两者不能混淆。

### 7.4 部分分配

```text
合同收入预测 = 100
事件A = 40
事件B = 空
```

则：

```text
已分配金额 = 40
待分配金额 = 60
分配状态 = 部分分配
```

已分配且收入年月有效的40进入月度统计；剩余60进入待处理收入。

### 7.5 分配校验

```text
Σfinal_allocated_amount < revenue_forecast
→ 部分分配

Σfinal_allocated_amount = revenue_forecast
→ 分配完成

Σfinal_allocated_amount > revenue_forecast
→ 分配超额，记录异常，超额部分不得静默进入正式汇总
```

负数合同和冲销场景继续使用Decimal金额，具体校验方向应在实现测试中覆盖。

---

## 8. RPD/CPD归月规则

### 8.1 金额只分一次

同一事件：

```text
final_allocated_amount = 40
收入年月（按RPD） = 2026-10
收入年月（按CPD） = 2026-11
```

则：

```text
RPD统计口径：2026-10记录40
CPD统计口径：2026-11记录40
```

两种口径分别汇总，不相加。

### 8.2 月份为空

某口径收入年月为空时：

- 已分配金额不能消失；
- 该口径生成待归月Posting；
- 待处理原因说明月份无法取得；
- 另一口径月份有效时，另一口径仍可正常归月。

### 8.3 不要货

无要货合同没有ShipmentAllocationLine：

- 合同收入预测仍保留；
- 全部金额进入待处理收入；
- 原因=`不要货，无收入月份依据`；
- 不生成虚构事件或月份。

---

## 9. 最终输出工作簿

### 9.1 核心可见Sheet

#### 9.1.1 合同收入预测

粒度：一合同一行。

建议字段：

1. 合同号
2. 遗留量
3. 当月新订货
4. 收入预测
5. BG
6. 地区部
7. 国家
8. 结转类型
9. 客户群
10. 项目名称
11. 要货状态
12. 发货事件数
13. 已分配金额
14. 待分配金额
15. 分配状态
16. RPD已归月金额
17. RPD待归月金额
18. CPD已归月金额
19. CPD待归月金额

这是唯一可以直接汇总合同收入预测的合同事实表。

#### 9.1.2 收入分配

粒度：一ShipmentAllocationLine一行。

建议字段：

1. 发货事件ID
2. 合同号
3. 履行供应中心
4. 需求状态
5. 贸易术语
6. ATA
7. ASD
8. RPD
9. CPD
10. 到货日期（按RPD）
11. 到货日期（按CPD）
12. 收入年月（按RPD）
13. 收入年月（按CPD）
14. 收入分段类别
15. 合同收入预测（参考，不可直接汇总）
16. 自动分配金额
17. 手工分配金额
18. 最终分配金额
19. 合同已分配金额
20. 合同待分配金额
21. 分配状态
22. 分配备注

黄色可编辑列：

- 手工分配金额；
- 分配备注。

旧三个人工月份字段不再输出。

#### 9.1.3 待处理收入

至少包括：

- 未分配合同金额；
- 分配超额；
- RPD月份为空的已分配金额；
- CPD月份为空的已分配金额；
- 不要货合同金额；
- 事件身份变化导致无法继承的人工金额；
- 日期或运输周期异常导致无法归月的金额。

#### 9.1.4 RPD月度收入汇总

按`收入年月（按RPD）`汇总。

最终字段草案：

- 收入年月；
- BG；
- 地区部；
- 国家；
- 结转类型；
- 客户群；
- 当月预测；
- 订未发；
- 发未收；
- 未录入订货。

#### 9.1.5 CPD月度收入汇总

字段与RPD月度收入汇总一致，按`收入年月（按CPD）`汇总。

采用两张表而不是一张超宽表，原因：

- 两种统计口径更容易独立筛选和导出；
- 字段名称完全一致；
- 避免用户将两套口径误加；
- 用户已确认两种展示形式均可。

### 9.2 辅助可见Sheet

继续保留：

- RPD跨月变化；
- CPD跨月变化；
- 供应需要提拉诉求清单粗表；
- 异常清单。

三张变化/差异表在国家后增加结转类型。

### 9.3 隐藏Sheet

建议：

- `_demand_event`：去重后的事件证据；
- `_fulfillment_summary`：原合同+中心履行计算结果；
- `_monthly_posting`：两种口径的归月明细和守恒证据；
- `_tool_meta`：schema、字段ID、事件ID版本、run_id和规则版本。

---

## 10. 用户操作闭环

### 10.1 第一次运行

```text
选择源文件
→ 生成合同收入预测
→ 识别发货事件
→ 计算履行字段和两个收入年月
→ 单事件合同自动分配
→ 多事件合同等待用户填写金额
→ 已确认部分进入月度汇总
→ 其余金额进入待处理收入
```

### 10.2 用户填写

用户只修改`收入分配`中的：

- 手工分配金额；
- 分配备注。

保存结果文件。

### 10.3 再次运行

用户选择保存后的结果作为上一次结果。

系统：

1. 读取PreviousRunState；
2. 按shipment_event_id继承手工金额和备注；
3. 重新读取本期源数据；
4. 重新计算合同收入预测、事件和收入年月；
5. 校验事件新增、消失或变化；
6. 重新生成部分分配、月度汇总和待处理收入；
7. 输出新文件。

输出文件不能覆盖输入的上一次结果。

---

## 11. 金额守恒

### 11.1 合同金额唯一

```text
每合同恰好一个ContractFinancialFact
```

### 11.2 分配守恒

```text
已分配金额 + 待分配金额 = 收入预测
```

### 11.3 RPD口径守恒

```text
RPD已归月金额 + RPD待归月金额 = 收入预测
```

### 11.4 CPD口径守恒

```text
CPD已归月金额 + CPD待归月金额 = 收入预测
```

### 11.5 全局守恒

```text
合同收入预测总额
= RPD月度已归月总额 + RPD待归月总额
= CPD月度已归月总额 + CPD待归月总额
```

任何差额必须可追溯，不能静默修平。

---

## 12. 架构重构

### 12.1 Domain

新增：

- ContractFinancialFact；
- DemandEventRecord；
- FulfillmentSummary；
- ShipmentAllocationLine；
- AllocationDecision；
- ContractAllocationSummary；
- MonthlyRevenuePosting；
- MonthlyRevenueSummaryRow；
- PendingRevenueRow；
- PreviousRunState。

旧BaseRow只保留为v0.8历史兼容类型，不能继续作为新主数据流。

### 12.2 Services

建议拆分：

- ContractFactBuilder；
- DemandEventBuilder；
- FulfillmentSummaryService；
- ShipmentProjectionService；
- AllocationService；
- MonthlyRevenuePostingService；
- MonthlyRevenueSummaryService；
- FulfillmentComparisonService；
- SupplyPullService。

### 12.3 Application

使用：

```text
RunRequest
RunResult
```

Application只编排，不写业务规则。

### 12.4 Adapters

拆分：

- ExcelSourceReader；
- PreviousResultReader；
- ExcelResultWriter。

### 12.5 Configuration

输出配置升级为按dataset声明，不再硬编码五Sheet和32列。

至少包括：

- contract_forecast；
- allocation；
- pending_revenue；
- monthly_summary_rpd；
- monthly_summary_cpd；
- rpd_changes；
- cpd_changes；
- supply_pull；
- issues；
- hidden_demand_event；
- hidden_fulfillment_summary；
- hidden_monthly_posting。

---

## 13. 分阶段实施

### Phase 0：关闭两个开放业务问题

关闭第16节问题，更新状态为：

```text
APPROVED_FOR_IMPLEMENTATION
```

### Phase 1：领域拆分与Golden回归

- 抽取ContractFinancialFact；
- 抽取DemandEventRecord；
- 抽取FulfillmentSummary；
- 保持旧输出并执行Golden对比；
- 落实Issue #20。

Gate：除Issue #20外，原履行字段结果不变。

### Phase 2：事件投影和稳定事件身份

- 生成shipment_event_id；
- 为事件生成两种收入年月；
- 建立事件变化诊断；
- 读取/保存事件级人工金额。

### Phase 3：分配和部分分配

- 单事件自动分配；
- 多事件手工金额；
- 空与0区分；
- 部分分配；
- 超额诊断；
- 合同守恒。

### Phase 4：月度Posting和汇总

- RPD/CPD两种Posting；
- 月份为空的待归月；
- RPD月度汇总；
- CPD月度汇总；
- 待处理收入；
- 全局守恒。

### Phase 5：新工作簿和历史往返

- 新可见/隐藏Sheet；
- 黄色编辑列；
- metadata schema升级；
- 保存→填写→导入→重算往返测试。

### Phase 6：辅助分析迁移

- 跨期变化切换到FulfillmentSummary；
- 变化表增加结转类型；
- 供应提拉迁移；
- 保留不要货状态变化。

### Phase 7：GUI、打包和实机验收

- 更新GUI摘要；
- 明确“上一次结果/已分配结果”；
- EXE构建；
- Windows Excel筛选、金额编辑和再导入实机验证。

---

## 14. 测试与验证

### 14.1 既有规则回归

必须覆盖：

- 当月订货可选；
- Sheet定位；
- 字段匹配；
- 空白/VALUE；
- Decimal金额；
- 完全重复行；
- 七国和Issue #20；
- 运输周期；
- 备货三态；
- 日期、货未发完、到货日期和收入年月；
- 收入分段；
- 不要货；
- 跨期变化；
- Excel筛选。

### 14.2 事件与分配

至少覆盖：

- 单事件自动分配；
- 多事件无分配；
- 多事件部分分配；
- 多事件完整分配；
- 同中心多事件；
- 多中心多事件；
- 相同月份多个事件仍保持独立金额行；
- 空与0；
- 超额；
- 事件新增/消失/字段变化；
- 手工金额继承；
- 无要货合同。

### 14.3 月度统计

至少覆盖：

- 同一金额分别进入RPD/CPD不同月份；
- 两种口径使用同一分配金额；
- 一种月份有效、另一种为空；
- 部分分配；
- 待归月；
- 按收入分段分类汇总；
- 合同级和全局守恒；
- 禁止RPD+CPD相加。

### 14.4 工作簿往返

```text
生成
→ 填写部分金额
→ 保存
→ 作为上一次结果导入
→ 继承金额与备注
→ 重算汇总
```

必须测试列移动、插入非关键列、显示名变化、metadata恢复和事件变化。

---

## 15. 不允许的实现

- 在旧BaseRow上继续堆金额分配字段；
- 继续把合同金额复制到供应中心/事件行作为权威金额；
- 按供应中心数、事件数或月份数自动平均；
- 相同月份事件强制合并后让用户失去一次发货粒度；
- 为RPD/CPD维护两套手工金额；
- 用Excel公式替代领域守恒校验；
- 以源行号作为唯一跨运行事件ID；
- 月份为空时丢弃已分配金额；
- 部分分配时把剩余金额静默塞给最后一行；
- 在设计Gate前修改生产代码。

---

## 16. 剩余两个业务问题

### 16.1 发货事件如何稳定识别，以及事件级收入年月如何计算

用户已经确认金额按“一次发货/要货事件”填写。

当前仍需确认两个紧密相关的实现事实：

#### A. 事件身份

当前源字段中尚未确认存在稳定的：

- 要货单号；
- 发货批次号；
- 需求明细ID；
- 行项目号；
- 其他跨月不变的唯一事件字段。

需要确认真实要货明细是否存在此类字段但尚未纳入当前映射。

若存在，应将其作为`shipment_event_id`的主键来源。

若不存在，只能使用业务字段组合生成事件指纹；当日期或状态变化时，可能无法自动继承上期手工金额，需要进入待处理收入。

#### B. 事件级收入年月

当前代码的到货日期和收入年月是在：

```text
合同号 + 履行供应中心
```

聚合后计算的。

若金额按单次事件分配，则必须明确事件行使用哪一对收入年月：

方案1（推荐）：

```text
每条事件使用自身ATA/ASD/RPD/CPD
沿用现有优先级和海运周期规则
计算事件级到货日期和两个收入年月
```

合同+中心汇总仍保留原MAX/MIN规则，用于既有履行分析和跨期比较。

方案2：

```text
同一合同+中心下所有事件共用现有汇总后的两个收入年月
```

方案2虽然完全不改变当前汇总结果，但无法区分同一中心多次发货落在不同月份，不利于按一次发货分配。

需要业务确认方案1是否符合真实含义。

### 16.2 月度汇总四个字段的度量含义

用户确认最终按月份呈现：

- 当月预测；
- 订未发；
- 发未收；
- 未录入订货。

需要确认：

#### 推荐定义

```text
当月预测
= 该收入年月全部已归月分配金额合计

订未发
= 其中收入分段类别=订未发的分配金额合计

发未收
= 其中收入分段类别=发未收的分配金额合计

未录入订货
= 收入分段类别=未录入订货的合同/事件数量
```

原因：按当前规则，未录入订货要求遗留量=0且当月新订货=0，因此收入预测金额也是0；把它作为金额合计永远为0，业务价值有限。

还需确认：

- `未录入订货`要显示合同数还是事件数；
- `需判断`是否在月度汇总增加独立金额列，还是只进入待处理收入；
- `不要货`是否只进入待处理收入，不出现在月份行。

---

## 17. 设计Gate

开始生产代码前必须满足：

- 第16.1和16.2节确认；
- 文档状态改为`APPROVED_FOR_IMPLEMENTATION`；
- shipment_event_id来源冻结；
- 事件级收入年月规则冻结；
- 两张月度汇总字段和度量冻结；
- 新输出Sheet契约冻结；
- Phase 1 WRITE_SCOPE和Golden验证计划通过审查；
- 所有代码继续在`refactor/revenue-allocation-v1`分支实施。

---

## 18. 当前结论

已经确认：

```text
手工填写金额
部分分配可先入汇总
分配对象是一次发货/要货事件
旧三个人工月份字段废弃
RPD/CPD是同一金额的两种统计口径
最终按月份呈现
```

尚待确认：

```text
事件稳定ID和事件级收入年月
月度汇总四个字段的精确度量
```

当前实施状态：

```text
NOT_READY_PENDING_2_BUSINESS_DECISIONS
```
