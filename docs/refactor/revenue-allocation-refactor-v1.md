# 收入分配与月度汇总重构方案 V1

- 文档 ID：`REVENUE-ALLOCATION-REFACTOR-V1`
- 状态：`DRAFT_PENDING_BUSINESS_DECISIONS`
- 日期：`2026-08-27`
- 仓库：`olu37776-bit/excel-arrival-tool`
- 重构分支：`refactor/revenue-allocation-v1`
- 当前生产基线：`main` / `v0.8.0`
- 被取代的临时方案：Issue #21
- 仍需独立处理或在本重构中回归：Issue #10、Issue #20

> 本文档先冻结重构边界、数据粒度、输出闭环和实施路径。当前只新增设计文档，不修改生产代码、配置、测试和现有发布版本。业务开放决策关闭后，才进入代码建设。

---

## 1. 重构结论

当前工具已经具备可复用的源文件识别、字段映射、数据规范化、海运周期、日期聚合、到货日期、收入年月、异常诊断和跨期比较能力。

当前真正的问题不是原字段或原计算公式错误，而是最终输出数据模型不适合继续处理收入金额：

```text
旧最终粒度 = 合同号 + 履行供应中心
```

而：

```text
遗留量 / 当月新订货 / 收入预测
真实粒度 = 合同号
```

一个合同有多个履行供应中心时，合同级金额会被复制到多个行。用户直接对旧基表求和，会把一笔合同金额重复计算。

重构后的核心关系必须变成：

```text
ContractFinancialFact
合同级金额唯一事实
        │
        │ 1:N
        ▼
DemandEventRecord
去重后的要货明细事件记录
        │
        │ 按既有规则聚合
        ▼
FulfillmentProjection
合同号 + 履行供应中心的履行计算结果
        │
        │ 按两个收入年月组合形成
        ▼
AllocationUnit
一次金额分配的最小无损单元
        │
        │ 自动或人工分配一次金额
        ▼
MonthlyRevenuePosting
同一份分配金额分别按RPD/CPD两种口径归月
        │
        ▼
MonthlyRevenueSummary
最终月度收入汇总
```

核心原则：

```text
合同金额只定义一次
金额只分配一次
RPD和CPD只是两种统计口径
每种口径分别满足金额守恒
```

---

## 2. 本次重构不改变什么

以下内容不是本轮重新设计对象，必须保留并做回归验证。

### 2.1 输入结构不变

```text
遗留量 Excel          必选
当月订货 Excel        可选
要货明细 Excel        必选
国家运输周期 Excel    必选
上一次结果 Excel      可选
```

四类业务源仍为独立Excel文件。

Sheet名称仍不能作为业务表识别的必要条件；继续按字段契约扫描工作簿内所有Sheet。

### 2.2 源字段不变

当前已确认的遗留量、当月订货、要货明细、国家运输周期字段继续使用稳定内部字段ID。

要货明细继续包含：

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

当前未确认存在稳定的“要货事件ID / 要货单号 / 明细ID”。这不阻塞V1，因为手工金额不直接绑定单个物理事件行。

### 2.3 空值和金额规范化不变

继续执行：

```text
空单元格 / 空白字符 / (空白) / VALUE标记
金额字段 → 0
日期字段 → None
普通文本/标识 → 空
```

金额继续使用：

```text
Decimal(str(raw_value))
→ ROUND_HALF_UP量化到0.01
```

基表、分配、守恒校验和月度汇总必须共享同一个规范化金额值。

### 2.4 履行计算规则不变

去除完全重复明细后，继续按：

```text
合同号 + 履行供应中心
```

生成履行计算结果。

现有日期聚合继续保持：

```text
ATA = MAX(天_ATA)
ASD = MAX(ASD日期)
RPD = MIN(RPD日期)
最晚ASD = MAX(ASD日期)
最晚RPD = MAX(RPD日期)
CPD = MAX(CPD日期)
```

货未发完继续保持：

```text
最晚RPD为空 → 空
最晚RPD有效、最晚ASD为空 → Y
最晚RPD > 最晚ASD → Y
最晚RPD <= 最晚ASD → N
```

到货日期继续保持：

```text
按RPD：
货未发完 != Y：ATA优先，否则ASD+海运周期
货未发完 = Y：最晚RPD+海运周期

按CPD：
货未发完 != Y：ATA优先，否则ASD+海运周期
货未发完 = Y：CPD+海运周期
```

收入年月继续保持：

```text
收入年月（按RPD） = 到货日期（按RPD）的年月
收入年月（按CPD） = 到货日期（按CPD）的年月
```

RPD和CPD是同一合同收入的两种统计口径，不是两套金额。

### 2.5 其他既有规则不变

继续保留：

- 当月订货整个文件可选；
- 完全重复行去重；
- 七国结转类型；
- 国家和供应中心运输周期诊断；
- 是否解锁备货三态；
- 多个供应中心发货；
- 分批发货；
- 多次要货；
- 分批供应；
- 收入分段类别；
- 无要货合同显式状态；
- RPD/CPD跨期变化；
- 供应需要提拉诉求；
- 异常清单；
- Windows Excel筛选与“数据→清除”可用性。

Issue #20的最新业务口径应在重构中落实：结转类型按最终解析后的国家判断，而不是只按遗留量国家判断。

---

## 3. 当前代码事实与问题定位

### 3.1 当前输入层可复用

`ExcelInputAdapter`已经负责：

- 可选当月订货来源；
- 按字段契约定位业务Sheet；
- 表头和字段匹配；
- 数据类型解析；
- 完全重复物理行识别；
- 源文件/Sheet/行号证据；
- 上期结果读取。

该层可以保留，后续只需要扩展“新结果工作簿”的人工分配读取能力。

### 3.2 当前领域模型过度围绕BaseRow

当前核心模型只有：

- `ParsedRow`；
- `BaseRow`；
- `PreviousData`；
- `ComparisonRow`。

`BaseRow`同时承载：

- 合同级金额；
- 合同属性；
- 履行供应中心；
- 日期聚合；
- 收入年月；
- 收入分段；
- 三个人工字段。

这使不同粒度的数据被压进同一个字典，金额重复没有类型边界保护。

### 3.3 当前RevenueEngine混合多个职责

`RevenueEngine.calculate()`当前同时完成：

1. 合同全集；
2. 合同级第一条规则；
3. 合同属性回退；
4. 要货明细按供应中心分组；
5. 日期聚合；
6. 运输周期；
7. 到货日期；
8. 收入年月；
9. 收入分段；
10. 人工字段继承；
11. BaseRow构建。

重构不能继续向该函数追加收入预测、分配和汇总逻辑。

### 3.4 当前输出层固定为旧五张表

`ExcelOutputAdapter.write()`只接收：

- `base_rows`；
- `rpd_changes`；
- `cpd_changes`；
- `supply_pull_rows`；
- `issues`。

配置校验还硬编码：

- 基表32列；
- 五个可见Sheet；
- 变化表固定列；
- 供应提拉表固定列。

新输出无法通过“在旧base_columns后面加几列”实现，必须升级为多数据集输出契约。

### 3.5 当前历史结果导入绑定旧基表

`read_previous()`通过旧基表列名读取：

- 合同号；
- 履行供应中心；
- 两个收入年月；
- 三个人工字段；
- 隐藏`row_kind`。

新模型需要导入：

- 上期履行投影快照；
- 上期人工月份字段；
- 上期收入分配金额；
- 上期分配备注；
- 稳定分配单元ID；
- schema版本和数据集定义。

因此`PreviousData`应替换为更完整的`PreviousRunState`。

### 3.6 当前GUI可保留输入框架

当前GUI的文件选择流程可以继续使用，但：

- “上一次成功结果”需要表达“上一次结果/已分配结果”；
- 完成摘要不再显示“基表行数”，而是合同数、分配单元数、待处理合同数和月度汇总数；
- 后续运行必须能读取用户在`收入分配`Sheet中填写的内容。

---

## 4. 目标领域模型

### 4.1 ContractFinancialFact

粒度：

```text
合同号
```

建议字段：

```text
contract_no
legacy_amount
monthly_new_order
revenue_forecast
bg
region
country
carryover_type
customer_group
project_name
demand_state
```

金额定义：

```text
revenue_forecast = legacy_amount + monthly_new_order
```

要求：

- 每个合同只能存在一条；
- 金额只在合同粒度计算一次；
- 多个履行供应中心不能复制产生新的财务事实；
- 该数据集是合同金额汇总的唯一权威来源。

### 4.2 DemandEventRecord

粒度：

```text
要货明细去重后的一个真实源记录
```

来源：`ParsedRow(role=demand_detail)`。

建议字段：

```text
event_record_id
contract_no
supply_center
region
country
customer_group
project_name
demand_status
incoterm
stock_control_flag
shipment_control_flag
ata
asd
rpd
cpd
bg
source_workbook
source_sheet
source_row_number
source_signature
```

V1身份策略：

- `event_record_id`只用于当次运行内部追溯；
- 使用源文件、Sheet、行号和标准化签名构造；
- 不用它作为人工金额跨期继承键；
- 如果以后在真实源表中发现稳定事件ID，再作为可选canonical字段接入。

### 4.3 FulfillmentProjection

粒度：

```text
合同号 + 履行供应中心
```

该对象承接旧BaseRow中所有履行计算字段，但不作为金额汇总事实。

建议字段继续包含旧32列中除人工金额分配外的业务字段：

```text
contract_no
contract financial reference
bg / region / country / carryover_type / customer_group / project_name
incoterm
supply_center
multiple_supply_centers
stock_unlocked
split_shipment
transit_days
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
row_kind
source_event_record_ids
```

注意：

- 这是既有计算规则的内部结果；
- 可以用于跨期变化和供应提拉；
- 不允许对其中重复引用的合同金额直接求和；
- 不再作为用户最终收入处理入口。

### 4.4 AllocationUnit

粒度：

```text
合同号
+ 收入年月（按RPD）
+ 收入年月（按CPD）
+ unit_kind
```

V1采用该粒度的原因：

- 同一合同下，如果多个履行投影具有相同的两个收入年月组合，无论金额在这些投影之间怎样拆，最终RPD和CPD月度汇总都相同；
- 将其合并不会损失两种统计口径的月度金额信息；
- 可以显著减少用户需要手工分配的行数；
- 不需要把金额硬分给供应中心或物理事件。

建议字段：

```text
allocation_unit_id
unit_kind
contract_no
revenue_month_rpd
revenue_month_cpd
projection_count
event_count
supply_centers
projection_keys
contract_revenue_forecast_reference
auto_allocated_amount
manual_allocated_amount
final_allocated_amount
allocation_ratio
allocation_status
allocation_note
```

`allocation_unit_id`必须确定性生成，例如：

```text
contract identity
+ normalized RPD revenue month or NULL
+ normalized CPD revenue month or NULL
+ unit_kind
```

不把供应中心列表放入ID。供应中心变化但两个统计口径月份组合不变时，月度归纳语义没有变化，历史人工金额可以继续复用。

### 4.5 AllocationDecision

用于表达人工输入和系统计算，不能只存在于Excel单元格。

建议字段：

```text
allocation_unit_id
manual_allocated_amount
allocation_note
source_run_id
source_workbook
```

V1推荐用户填写“手工分配金额”，系统计算比例作为参考：

```text
allocation_ratio = final_allocated_amount / revenue_forecast
```

不建议只让用户填写比例，因为：

- 金额守恒更直观；
- 负数合同/调整金额更容易表达；
- 避免比例四舍五入导致合同金额差额；
- 系统仍可显示派生比例。

### 4.6 MonthlyRevenuePosting

粒度：

```text
统计口径 + 合同号 + 收入年月 + 分配来源
```

统计口径：

```text
RPD
CPD
```

金额只来自同一套`final_allocated_amount`，不能为RPD和CPD分别维护两套金额。

建议字段：

```text
basis
contract_no
allocation_unit_id
revenue_month
posted_amount
pending_amount
posting_status
posting_source
bg
region
country
carryover_type
customer_group
project_name
```

### 4.7 MonthlyRevenueSummary

粒度建议：

```text
收入年月
+ BG
+ 地区部
+ 国家
+ 结转类型
+ 客户群
```

输出两个并列指标：

```text
收入预测（按RPD）
收入预测（按CPD）
```

另保留：

```text
RPD待归月金额
CPD待归月金额
合同数
```

RPD与CPD是两列替代统计口径，不能横向相加。

### 4.8 PendingRevenue

用于解释所有尚不能进入明确月份的金额。

建议字段：

```text
contract_no
allocation_unit_id
revenue_forecast
allocated_amount
unallocated_amount
rpd_pending_amount
cpd_pending_amount
pending_reason
candidate_revenue_months_rpd
candidate_revenue_months_cpd
allocation_status
```

必须区分：

1. 金额尚未分配到AllocationUnit；
2. 金额已经分配，但RPD收入年月为空；
3. 金额已经分配，但CPD收入年月为空；
4. 无要货合同没有归月依据；
5. 日期或运输周期异常导致收入年月为空。

---

## 5. 要货事件与既有履行计算的关系

要货明细的一条去重后记录是一个`DemandEventRecord`。

但V1不直接在每个事件上重新定义到货规则。

现有规则继续先生成：

```text
FulfillmentProjection
粒度 = 合同号 + 履行供应中心
```

原因：

- ATA、ASD、RPD、最晚RPD、CPD等现有规则本来就是同合同+供应中心内的聚合；
- 用户明确要求原字段和原计算规则不变；
- 直接改为每事件一套到货日期会改变当前业务结果；
- 本轮目标是重构金额处理和输出闭环，不是重写履行计算。

因此正式链路为：

```text
DemandEventRecord
        ↓ 按合同+中心聚合，规则不变
FulfillmentProjection
        ↓ 按两个收入年月组合合并
AllocationUnit
```

旧“合同+履行供应中心基表”不再作为核心用户表，但它对应的计算结果仍以内部数据集存在。

---

## 6. 收入分配规则

### 6.1 合同收入预测

```text
收入预测 = 遗留量 + 当月新订货
```

使用两位小数Decimal业务值。

当月订货文件未提供或合同无匹配：

```text
当月新订货 = 0
```

### 6.2 零金额合同

```text
revenue_forecast = 0.00
```

处理：

- 不要求用户分配；
- 分配状态=`无需分配`；
- 所有AllocationUnit最终分配金额为0或不生成金额行；
- 不产生金额不平异常。

### 6.3 单一AllocationUnit

一个合同只有一个AllocationUnit时：

```text
auto_allocated_amount = revenue_forecast
final_allocated_amount = revenue_forecast
allocation_status = 自动完成
```

即使一个或两个收入年月为空，金额分配本身仍然完成；月份为空的问题进入待归月诊断。

### 6.4 多个AllocationUnit

一个合同有多个AllocationUnit且收入预测非0时：

- 不自动平均；
- 不按供应中心数平均；
- 不按要货明细行数平均；
- 不把全部金额放到第一个单元；
- 不把合同金额复制到所有单元。

用户在`收入分配`中填写`手工分配金额`。

### 6.5 最终分配金额

```text
若手工分配金额有值：
final_allocated_amount = manual_allocated_amount

否则若自动分配金额有值：
final_allocated_amount = auto_allocated_amount

否则：
final_allocated_amount = 未分配
```

必须区分Excel空单元格和数值0。

### 6.6 合同分配守恒

每个合同计算：

```text
allocated_total = Σ final_allocated_amount
allocation_delta = revenue_forecast - allocated_total
```

状态建议：

```text
无需分配
自动完成
手工完成
部分分配
分配不平
待分配
```

判断：

```text
forecast=0 → 无需分配
单一单元自动全额 → 自动完成
多单元且所有金额明确、合计=forecast → 手工完成
已填写部分金额且合计!=forecast → 部分分配/分配不平
无任何金额 → 待分配
```

金额允许为负数，守恒判断只比较两位小数Decimal，不使用浮点容差。

### 6.7 分配拓扑变化

从上一次结果继承人工金额时，只按`allocation_unit_id`精确继承。

如果本期月份组合变化：

- 新单元不继承旧金额；
- 消失单元不进入本期；
- 保留单元继续继承；
- 本期重新校验合同合计；
- 合计不平时进入待处理。

禁止只按合同号把旧金额随意迁移到新月份组合。

---

## 7. 两种统计口径的自动归月

金额只分配一次，但RPD和CPD可以独立判断某个合同在该口径下是否无需人工分配即可确定月份。

### 7.1 口径完全自动归月

对某个合同、某个统计口径，如果：

```text
所有AllocationUnit在该口径下均有有效收入年月
且所有收入年月完全相同
```

则该口径可以直接：

```text
该收入年月 = 合同收入预测全额
posting_source = AUTO_SINGLE_MONTH
```

即使另一个统计口径有多个不同月份、仍需人工分配，本口径也可以先得到完整汇总。

### 7.2 口径需要分配

如果该口径存在多个不同有效收入年月，必须依赖AllocationUnit金额。

已分配单元按其收入年月归月；未分配差额进入该口径待归月金额。

### 7.3 口径月份部分缺失

如果某些AllocationUnit有月份，另一些为空：

- 不能把合同全额自动放到唯一可见月份；
- 已明确分配到有月份单元的金额可以归月；
- 分配到空月份单元的金额进入该口径待归月；
- 尚未分配的合同差额同样进入待归月。

### 7.4 无要货合同

`CONTRACT_ONLY_NO_DEMAND`合同：

- 合同收入预测仍保留；
- 不虚构收入月份；
- 两种口径均进入待归月；
- 原收入分段类别继续为`不要货`；
- 不产生运输周期或日期缺失异常。

### 7.5 口径守恒

每个合同分别满足：

```text
RPD已归月金额 + RPD待归月金额 = 合同收入预测
CPD已归月金额 + CPD待归月金额 = 合同收入预测
```

全量同样满足：

```text
Σ合同收入预测
= ΣRPD已归月 + ΣRPD待归月
= ΣCPD已归月 + ΣCPD待归月
```

RPD总额与CPD总额不能相加；它们是同一合同收入预测的两种时间统计结果。

---

## 8. 最终输出工作簿

### 8.1 核心用户Sheet

#### 8.1.1 `合同收入预测`

粒度：一合同一行。

建议字段顺序：

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
12. 履行供应中心数
13. 分配单元数
14. 已分配金额
15. 待分配金额
16. 分配状态
17. RPD归月状态
18. CPD归月状态
19. RPD待归月金额
20. CPD待归月金额

用途：

- 合同金额权威表；
- 可直接汇总收入预测；
- 快速识别待处理合同；
- 不重复合同金额。

#### 8.1.2 `收入分配`

粒度：一AllocationUnit一行。

建议字段顺序：

1. 分配单元ID
2. 合同号
3. BG
4. 地区部
5. 国家
6. 结转类型
7. 客户群
8. 项目名称
9. 收入年月（按RPD）
10. 收入年月（按CPD）
11. 涉及履行供应中心
12. 履行投影数
13. 要货事件数
14. 合同收入预测（参考）
15. 自动分配金额
16. 手工分配金额
17. 最终分配金额
18. 分配比例
19. 合同已分配合计
20. 合同待分配金额
21. 分配状态
22. 分配备注
23. 是否手工调整收入月份
24. 手工调整收入月份
25. 调整备注

可编辑字段建议使用黄色底色：

- 手工分配金额；
- 分配备注；
- 原三个人工月份字段。

`合同收入预测（参考）`会在同合同多行重复，仅用于用户分配时参考，列标题和说明必须明确“不可直接汇总”。真正金额汇总只能使用`合同收入预测`Sheet或`最终分配金额`。

#### 8.1.3 `收入归月明细`

系统生成、不可手工修改。

建议使用长表：

1. 统计口径
2. 合同号
3. 分配单元ID
4. 收入年月
5. 已归月金额
6. 待归月金额
7. 归月状态
8. 归月来源
9. BG
10. 地区部
11. 国家
12. 结转类型
13. 客户群
14. 项目名称
15. 待处理原因

用途：

- 解释月度汇总来源；
- 进行守恒审计；
- 作为后续透视或外部导出的规范明细数据集。

#### 8.1.4 `月度收入汇总`

建议宽表，同一行并列两种统计口径：

1. 归月状态
2. 收入年月
3. BG
4. 地区部
5. 国家
6. 结转类型
7. 客户群
8. 项目名称（可选汇总维度）
9. 收入预测（按RPD）
10. 收入预测（按CPD）
11. 合同数

`归月状态`：

```text
已归月
待归月
```

待归月行的收入年月留空，不使用伪造月份。

该表是用户最终按月查看和透视的主要结果。

#### 8.1.5 `待处理收入`

粒度：合同或AllocationUnit问题。

建议字段：

1. 合同号
2. 分配单元ID
3. 收入预测
4. 已分配金额
5. 待分配金额
6. RPD待归月金额
7. CPD待归月金额
8. RPD候选月份
9. CPD候选月份
10. 处理状态
11. 待处理原因
12. 建议操作

用户先在该表定位问题，再回到`收入分配`填写金额。

### 8.2 辅助分析Sheet

继续保留：

- `RPD跨月变化`
- `CPD跨月变化`
- `供应需要提拉诉求清单粗表`
- `异常清单`

三张变化/差异表在`国家`后增加`结转类型`。

变化和供应提拉仍基于`FulfillmentProjection`，不使用合同金额重复行做金额汇总。

### 8.3 隐藏系统Sheet

#### `_fulfillment_projection`

保存当前履行计算结果及`row_kind`，用于：

- 跨期变化；
- 上期状态恢复；
- 供应提拉；
- 规则回归审计。

#### `_demand_event`

保存去重后的要货事件记录和源证据，用于追溯。

#### `_tool_meta`

建议升级schema版本，至少保存：

- schema_version；
- run_id；
- rules_version；
- dataset名称与显示Sheet；
- 字段ID与显示名称；
- allocation_unit_id定义版本；
- 金额精度；
- row_kind；
- 输出生成时间；
- 源文件指纹（不保存真实内容）。

---

## 9. 人工处理闭环

### 9.1 第一次运行

```text
选择本期源文件
→ 生成合同收入预测
→ 生成履行投影
→ 生成分配单元
→ 单一单元自动分配
→ 多单元进入待分配
→ 输出月度汇总和待处理收入
```

### 9.2 用户编辑

用户只在`收入分配`Sheet填写：

- 手工分配金额；
- 分配备注；
- 必要时填写原三个人工月份字段。

用户保存结果工作簿。

### 9.3 再次运行

GUI选择保存后的结果作为：

```text
上一次结果 / 已分配结果
```

工具：

1. 读取AllocationDecision；
2. 按allocation_unit_id继承；
3. 重新计算本期合同收入预测和履行月份；
4. 校验分配单元拓扑变化；
5. 重新执行金额守恒；
6. 重新生成归月明细、月度汇总和待处理收入；
7. 输出新文件。

输出文件不能覆盖作为输入的上一次结果。

### 9.4 部分分配

推荐V1行为：

- 已明确分配并有有效月份的部分进入月度汇总；
- 未分配差额进入待归月；
- 不自动猜测剩余金额；
- `待处理收入`明确显示差额。

这样用户可以逐步完成分配，同时始终满足金额守恒。

该行为仍需业务最终确认，见第18节。

---

## 10. 原三个人工月份字段的迁移

现有字段保留显示名称：

- 是否手工调整收入月份；
- 手工调整收入月份；
- 调整备注。

当前旧粒度：

```text
合同号 + 履行供应中心
```

推荐新粒度：

```text
allocation_unit_id
```

迁移规则建议：

1. 当前AllocationUnit只包含一个旧履行投影时，直接继承；
2. 包含多个履行投影且三个人工字段完全一致时，继承一次；
3. 多个履行投影的人工值不一致时：
   - 不自动选择；
   - 记录`LEGACY_MANUAL_ADJUSTMENT_CONFLICT`；
   - 新单元人工字段留空；
4. 新增单元为空；
5. 人工月份字段继续不覆盖自动RPD/CPD收入年月，也不参与RPD/CPD跨期比较。

该粒度迁移仍需业务确认，见第18节。

---

## 11. 架构分层

### 11.1 Domain

新增明确类型：

```text
ContractFinancialFact
DemandEventRecord
FulfillmentProjection
AllocationUnit
AllocationDecision
ContractAllocationSummary
MonthlyRevenuePosting
MonthlyRevenueSummaryRow
PendingRevenueRow
PreviousRunState
```

禁止继续以一个`dict[str, Any]`类型承担所有业务粒度。

V1可以继续用dataclass和字典字段混合，但必须通过不同类隔离粒度。

### 11.2 Services

建议拆分：

```text
ContractFactBuilder
- 合同全集
- 金额和合同属性
- 最终国家与结转类型

FulfillmentProjectionService
- 从现有RevenueEngine抽取
- 复用全部既有履行计算规则

AllocationUnitBuilder
- 按RPD/CPD收入年月组合形成单元
- 生成稳定allocation_unit_id

AllocationService
- 自动/人工金额
- 历史继承
- 合同守恒和状态

MonthlyRevenueService
- 两种口径归月
- 待归月
- 月度明细与汇总

FulfillmentComparisonService
- RPD/CPD跨期变化
- 有要货/不要货状态变化

SupplyPullService
- 同期两口径差异
```

### 11.3 Application

用一个结构化请求代替不断扩展函数参数：

```text
RunRequest
- source_files
- previous_result
- output_path
- config_path
```

应用结果：

```text
RunResult
- contract_facts
- fulfillment_projections
- allocation_units
- allocation_summaries
- monthly_postings
- monthly_summary
- pending_revenue
- comparisons
- issues
- output_path
```

Application只编排，不实现业务计算。

### 11.4 Adapters

```text
ExcelSourceReader
PreviousResultReader
ExcelResultWriter
```

`PreviousResultReader`与源文件Reader可以共用openpyxl基础设施，但逻辑应独立，避免继续把旧基表读取逻辑塞进`ExcelInputAdapter`。

### 11.5 Configuration

当前配置硬编码旧五张表和32列，需要升级为：

```text
output.datasets.contract_forecast
output.datasets.allocation
output.datasets.monthly_detail
output.datasets.monthly_summary
output.datasets.pending
output.datasets.rpd_changes
output.datasets.cpd_changes
output.datasets.supply_pull
output.datasets.issues
```

每个数据集独立配置：

- Sheet名称；
- 字段顺序；
- 字段显示名；
- 日期/金额类型；
- 可编辑字段；
- 是否隐藏；
- 筛选/冻结设置。

配置只定义映射和展示，不定义复杂业务流程。

---

## 12. 现有代码复用与替换清单

### 12.1 直接复用或小改

- `adapters/sheet_locator.py`
- `services/field_matching.py`
- `services/normalization.py`
- 源文件读取和解析大部分逻辑
- 完全重复行去重
- 金额Decimal策略
- 国家identity规范化
- `services/stock_unlock.py`
- 运输周期查找和异常分型
- 到货日期计算函数
- 收入分段基础规则
- Issue模型和异常清单
- GUI文件选择基础框架

### 12.2 拆分后复用

- `services/calculation.py`
  - 合同事实部分迁入`ContractFactBuilder`
  - 履行部分迁入`FulfillmentProjectionService`
- `services/comparison.py`
  - 继续处理FulfillmentProjection变化
  - 不再依赖用户可见基表
- `adapters/excel_reader.py`
  - 源文件读取保留
  - 旧结果读取拆到独立Reader

### 12.3 需要重写

- `domain/models.py`
- `application/pipeline.py`
- `adapters/excel_writer.py`
- `config/default.json`输出结构
- `config.py`输出契约校验
- 旧`BaseRow`主数据流
- 旧`PreviousData`主数据流
- GUI完成摘要和上期结果语义
- 大部分依赖旧五Sheet结构的集成测试

### 12.4 不允许的实现方式

- 在旧BaseRow后直接增加收入预测和手工分配字段；
- 继续让合同金额在中心行重复并要求用户“注意不要汇总”；
- 用供应中心数量自动平均金额；
- 用要货事件数自动平均金额；
- 分别为RPD和CPD维护两套手工金额；
- Writer重新计算业务规则；
- 用Excel公式替代领域守恒校验；
- 只在GUI或输出标题层做重构。

---

## 13. 输出兼容与历史迁移

### 13.1 当前v0.8结果

旧结果没有收入分配单元和手工分配金额。

首次进入新版本时：

- 旧结果仍可用于履行跨期比较；
- 旧`row_kind`继续恢复；
- 旧三个人工月份字段按第10节尝试迁移；
- 不生成伪造的历史分配金额；
- 所有多单元合同进入待分配。

### 13.2 新schema

建议新结果schema升级为`4`或更高。

新版本必须记录：

- 各数据集版本；
- allocation_unit_id版本；
- 分配输入字段；
- 行状态；
- 金额精度；
- 规则版本。

### 13.3 向后兼容边界

- 新版本可以读取v0.8结果；
- v0.8程序不要求能读取新结果；
- 不在新输出中保留一张伪装成旧基表的兼容表；
- 需要兼容导出时，未来单独提供“履行计算导出”，不污染核心数据模型。

---

## 14. 实施分支与阶段

正式重构全部在：

```text
refactor/revenue-allocation-v1
```

进行。

在设计Gate通过前，该分支只允许更新设计、Schema草案、测试计划和虚构样例，不实施生产代码。

### Phase 0：业务决策关闭

关闭第18节开放问题，更新本文档状态：

```text
APPROVED_FOR_IMPLEMENTATION
```

### Phase 1：新领域模型和双轨计算骨架

- 新增领域类型；
- 将现有RevenueEngine拆为合同事实和履行投影；
- 暂时继续生成旧结果用于回归；
- 新旧履行结果执行Golden对比。

Gate：

```text
除Issue #20确认变更外，旧32字段履行计算结果一致
```

### Phase 2：AllocationUnit与历史分配导入

- 生成稳定分配单元；
- 自动单元分配；
- 手工金额读取；
- 合同分配守恒；
- 旧人工月份字段迁移。

### Phase 3：归月明细与月度汇总

- RPD/CPD两种口径；
- 单月份口径自动归月；
- 多月份分配归月；
- 部分分配和待归月；
- 合同级和全局守恒。

### Phase 4：新工作簿输出

- 九个可见/辅助Sheet；
- 三个隐藏系统Sheet；
- 可编辑列样式；
- AutoFilter和冻结首行；
- metadata schema升级。

### Phase 5：跨期、供应提拉和Issue #20

- 跨期比较切换到隐藏FulfillmentProjection；
- 三张变化/差异表增加结转类型；
- 结转类型按最终国家；
- 保留不要货状态变化。

### Phase 6：GUI和打包

- 更新文字、摘要和上期结果语义；
- 保持简单单页GUI；
- 更新EXE构建；
- Windows桌面Excel实机验收。

### Phase 7：真实数据验收和切换

- 使用脱敏或本地真实数据；
- 对比合同总额；
- 完成一轮手工分配→保存→重新导入→汇总；
- 验证月度金额守恒；
- 决定是否发布新主版本。

---

## 15. 测试与验证计划

### 15.1 既有规则回归

必须继续覆盖：

- 当月订货文件可选；
- Sheet2/Sheet3识别；
- 字段exact→contains唯一匹配；
- 完全重复行；
- 空白/VALUE；
- 金额精度；
- 七国结转；
- 海运周期异常；
- 是否解锁备货三态；
- 日期聚合；
- 货未发完；
- 两套到货日期；
- 收入分段；
- 不要货占位；
- 跨期状态变化；
- Excel筛选。

### 15.2 合同事实测试

- 每合同只有一条财务事实；
- 多供应中心不增加合同金额；
- 收入预测准确；
- 当月订货缺失时金额正确；
- 正负金额和零金额；
- Issue #20最终国家结转类型。

### 15.3 AllocationUnit测试

- 多中心相同月份组合合并为一个单元；
- 同中心/多中心不同月份组合形成多个单元；
- 空月份参与ID；
- ID在行顺序变化后稳定；
- 供应中心列表变化但月份组合相同时ID稳定；
- 无要货单元；
- 完全重复事件不增加单元。

### 15.4 分配测试

- 单单元自动全额；
- 多单元无人工金额；
- 多单元完整人工金额；
- 部分分配；
- 合计不平；
- 明确0与空单元格；
- 负数合同；
- 历史精确继承；
- 单元新增/删除/月份变化；
- 旧结果无分配字段。

### 15.5 归月测试

- 两种口径使用同一分配金额；
- 单月份口径自动全额；
- 多月份按分配金额；
- 一种口径月份有效、另一种为空；
- 部分分配；
- 无要货；
- 运输周期异常；
- 每合同两种口径守恒；
- 全局守恒；
- 不允许RPD+CPD相加作为总收入。

### 15.6 工作簿往返测试

完整场景：

```text
生成结果
→ 用户在收入分配填写金额
→ 保存
→ 作为上一次结果重新读取
→ 生成新结果
→ 人工金额、备注和状态保持
→ 月度汇总正确
```

需要测试：

- 列顺序变化；
- 显示名变化但metadata可恢复；
- 用户插入非关键列；
- 空白和0；
- 分配单元变化；
- 人工字段冲突；
- 输出文件不能覆盖输入结果。

### 15.7 Excel实机验证

Windows桌面Excel必须验证：

- 黄色可编辑列；
- 金额输入和保存；
- 筛选及“数据→清除”；
- 冻结首行；
- 多Sheet导航；
- 重新打开；
- 中文和日期/金额格式；
- 再次导入。

自动OOXML检查不能替代实机验证。

---

## 16. 强制质量门禁

### 16.1 合同金额唯一

```text
COUNT(ContractFinancialFact by contract_no) = 1
```

任何用户可汇总表不得把合同收入预测按履行行复制成权威金额。

### 16.2 分配守恒

完成状态的合同：

```text
Σfinal_allocated_amount = revenue_forecast
```

未完成合同必须显示差额，不能静默通过。

### 16.3 RPD守恒

```text
RPD已归月 + RPD待归月 = revenue_forecast
```

### 16.4 CPD守恒

```text
CPD已归月 + CPD待归月 = revenue_forecast
```

### 16.5 输出汇总守恒

```text
合同收入预测Sheet合计
= 月度收入汇总RPD已归月+待归月
= 月度收入汇总CPD已归月+待归月
```

### 16.6 计算规则一致

隐藏FulfillmentProjection与旧v0.8履行计算Golden结果一致，允许差异只有：

- Issue #20最终国家结转类型修正；
- 明确批准的新业务决策。

### 16.7 人工输入可追溯

每个手工分配金额必须能追溯：

- allocation_unit_id；
- 来源结果文件；
- 上次运行ID；
- 分配备注；
- 本次是否继承或新填。

---

## 17. 建议WRITE_SCOPE

允许修改或新增：

```text
config/default.json
src/revenue_tool/config.py
src/revenue_tool/gui.py
src/revenue_tool/cli.py
src/revenue_tool/application/*
src/revenue_tool/domain/*
src/revenue_tool/adapters/excel_reader.py
src/revenue_tool/adapters/excel_writer.py
src/revenue_tool/adapters/previous_result_reader.py
src/revenue_tool/services/calculation.py
src/revenue_tool/services/comparison.py
src/revenue_tool/services/contract_finance.py
src/revenue_tool/services/fulfillment_projection.py
src/revenue_tool/services/allocation.py
src/revenue_tool/services/monthly_revenue.py
src/revenue_tool/services/stock_unlock.py
相关测试和虚构fixture
README.md
新Schema和验证报告
```

不得：

- 提交真实业务Excel；
- 在设计Gate前修改生产代码；
- 引入Web服务或数据库；
- 引入pandas作为业务核心依赖；
- 删除现有计算回归测试后降低覆盖；
- 以旧基表兼容为理由保留错误金额粒度。

---

## 18. 需要业务确认的开放决策

以下问题必须关闭后，本文档才能改为`APPROVED_FOR_IMPLEMENTATION`。

### OD-001 手工输入金额还是比例

推荐：

```text
用户填写手工分配金额
系统计算分配比例
```

备选：用户填写比例，系统算金额。

需要确认最终输入方式。

### OD-002 部分分配是否进入月度汇总

推荐：

```text
已确认部分进入已归月金额
剩余差额进入待归月金额
```

备选：合同未完全分配时，整笔合同收入预测都不进入已归月汇总。

需要确认。

### OD-003 AllocationUnit合并粒度

推荐：

```text
合同号
+ 收入年月（按RPD）
+ 收入年月（按CPD）
```

相同组合的多个中心/履行投影合并为一行，避免无意义的中心级金额拆分。

需要确认用户是否希望仍按供应中心分别填写金额。若没有中心级金额业务需求，推荐按月份组合合并。

### OD-004 原三个人工月份字段放置位置

推荐迁移到`收入分配`，粒度改为allocation_unit_id，并按一致性规则继承。

备选：新增独立`履行调整`Sheet，继续按合同+履行供应中心维护。

需要确认这些字段未来主要用于：

- 备注/人工判断；
- 形成第三种最终统计月份；
- 还是仅保留历史兼容。

### OD-005 月度汇总展示形式

推荐：一张`月度收入汇总`，同一行并列：

```text
收入预测（按RPD）
收入预测（按CPD）
```

备选：分别输出两张汇总Sheet。

需要确认用户习惯。

---

## 19. 设计Gate

进入代码实施前必须满足：

- Issue #21保持关闭且不再作为实现依据；
- OD-001至OD-005全部确认；
- 文档状态更新为`APPROVED_FOR_IMPLEMENTATION`；
- 输出Sheet和字段顺序冻结；
- allocation_unit_id定义冻结；
- 旧人工字段迁移规则冻结；
- 测试计划通过独立审查；
- 从重构分支创建/更新Draft PR；
- 明确Phase 1 WRITE_SCOPE和验证门禁。

---

## 20. 当前建议

在没有中心级金额、数量或比例来源的前提下，V1不应把收入预测分给供应中心。

最佳闭环是：

```text
合同金额唯一
→ 现有履行规则计算两个收入年月
→ 相同RPD/CPD月份组合形成分配单元
→ 单单元自动、多个单元用户填金额
→ 同一金额分别按RPD/CPD归月
→ 已归月与待归月共同守恒
→ 输出最终月度收入汇总
```

这个模型既保留现有字段和计算规则，又从根本上解决：

- 多供应中心金额重复；
- 用户无法继续处理；
- 手工分配无法继承；
- 月度汇总不可信；
- 未分配金额消失；
- RPD/CPD被误当成两套金额。
