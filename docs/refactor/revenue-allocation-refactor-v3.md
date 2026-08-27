# 收入分配与月度汇总重构方案 V3

- 文档 ID：`REVENUE-ALLOCATION-REFACTOR-V3`
- 状态：`READY_FOR_IMPLEMENTATION_APPROVAL`
- 日期：`2026-08-27`
- 仓库：`olu37776-bit/excel-arrival-tool`
- 重构分支：`refactor/revenue-allocation-v1`
- Draft PR：`#25`
- 当前生产基线：`main / v0.8.0`
- 取代文档：
  - `docs/refactor/revenue-allocation-refactor-v1.md`
  - `docs/refactor/revenue-allocation-refactor-v2.md`
- 已撤销临时方案：Issue `#21`
- 仍需在重构中落实或回归：Issue `#10`、Issue `#20`

> V3 是当前收入分配重构的唯一权威设计入口。V1、V2 只保留为讨论历史，不得作为代码实施依据。V3 不改变已经确认的源字段、日期聚合、海运周期、到货日期、收入年月和收入分段基础规则；它只重构金额事实、人工分配、月度归纳和最终输出闭环。

---

## 1. 最终业务目标

用户最终需要完成的业务闭环是：

```text
读取本期合同和要货数据
→ 计算既有履行结果与两个收入年月
→ 得到每个合同唯一的收入预测金额
→ 用户根据履行证据分配部分或全部金额
→ 同一份分配金额分别按RPD、CPD两种统计口径归月
→ 输出按月份汇总的收入预测
→ 未分配、无法归月或需判断的金额始终可见
```

核心原则：

```text
合同金额只存在一次
履行记录只提供业务证据
履行归纳结果只提供分配上下文
人工金额只分配一次
RPD和CPD只是两种统计口径
部分分配允许先进入月度结果
金额不能因多供应中心或多条要货记录而重复
金额不能因月份为空或状态不清而消失
```

---

## 2. 对要货明细的正式业务理解

### 2.1 一条要货明细不是天然的一次独立发货

当前真实要货明细包含：

- 原合同号；
- 需求状态；
- 履行供应中心；
- 贸易术语；
- 备货总控标识；
- 发货总控标识；
- ATA；
- ASD；
- RPD；
- CPD；
- 其他合同和项目属性。

这些字段描述的是一次要货/履行过程在当前数据中的记录和状态。真实表中不存在已确认的：

- 要货单号；
- 发货批次号；
- 需求明细ID；
- 行项目号；
- 其他可跨期稳定标识一次独立发货的业务主键。

因此，V3 明确废止 V2 中以下假设：

```text
去重后每一条要货明细物理行
= 一次独立ShipmentEvent
= 一条可直接分配金额的业务对象
```

### 2.2 要货明细的正确角色

去除完全重复行后，每一条保留记录定义为：

```text
DemandRecord
= 要货/履行过程证据记录
```

DemandRecord 用于：

- 识别合同是否存在要货；
- 展开履行供应中心；
- 判断多个供应中心；
- 判断分批发货；
- 判断多次要货；
- 判断分批供应；
- 计算备货解锁状态；
- 聚合ATA、ASD、RPD、CPD；
- 形成货未发完、到货日期和收入年月；
- 为用户手工分配提供证据。

DemandRecord 不直接拥有合同收入金额，也不直接等于人工金额分配行。

### 2.3 同一履行过程可能有多条状态记录

同一合同、同一履行供应中心下可能存在多条 DemandRecord：

- 记录数不同；
- 需求状态不同；
- 日期不同；
- 控制标识不同；
- 同一业务过程可能随状态更新出现多条记录。

在没有稳定业务事件ID的前提下，系统不能自动判断这些记录应拆成几次独立发货并分别分配多少钱。

---

## 3. 本次重构不改变的业务规则

### 3.1 输入结构不变

```text
遗留量 Excel          必选
当月订货 Excel        可选
要货明细 Excel        必选
国家运输周期 Excel    必选
上一次结果 Excel      可选
```

四类业务源仍为彼此独立的 Excel 文件。

Sheet 名仍然只作提示，业务 Sheet 继续按字段契约扫描和识别。

### 3.2 字段映射不变

稳定内部字段 ID 和当前源字段继续沿用。输出字段名称变化只影响输出配置，不反向改变领域规则。

### 3.3 空值与金额精度不变

以下原始值继续安静规范化：

- 空单元格；
- 空字符串；
- 半角/全角空白；
- 制表符、换行；
- `(空白)`；
- `#VALUE!`、`VALUE`、`#VALUE`等价标记。

类型结果：

```text
金额 → 0
日期 → None
文本/标识 → 空
运输周期 → 空
```

金额继续统一使用：

```text
Decimal(str(raw_value))
→ ROUND_HALF_UP量化到0.01
```

合同事实、人工分配、待分配、归月和汇总必须共享同一个 Decimal 金额口径。

### 3.4 DemandRecord 完全重复去重不变

完全重复记录：

- 只保留第一条参与业务计算；
- 继续记录`DUPLICATE_ROW_IGNORED`；
- 不增加分批发货、多次要货、分批供应或供应中心数。

### 3.5 履行归纳粒度不变

既有履行计算仍按：

```text
合同号 + 履行供应中心
```

聚合 DemandRecord，生成：

```text
FulfillmentProjection
```

这层保留现有规则，但不再作为最终金额事实表。

### 3.6 日期聚合不变

同一合同+履行供应中心：

```text
ATA = MAX(天_ATA)
ASD = MAX(ASD日期)
RPD = MIN(RPD日期)
最晚ASD = MAX(ASD日期)
最晚RPD = MAX(RPD日期)
CPD = MAX(CPD日期)
```

### 3.7 货未发完不变

```text
最晚RPD为空 → 空
最晚RPD有效且最晚ASD为空 → Y
两者有效且最晚RPD > 最晚ASD → Y
两者有效且最晚RPD <= 最晚ASD → N
```

### 3.8 到货日期不变

按RPD：

```text
货未发完 != Y：
  ATA有效 → ATA
  否则ASD和海运周期有效 → ASD + 海运周期
  否则 → 空

货未发完 = Y：
  最晚RPD和海运周期有效 → 最晚RPD + 海运周期
  否则 → 空
```

按CPD：

```text
货未发完 != Y：
  ATA有效 → ATA
  否则ASD和海运周期有效 → ASD + 海运周期
  否则 → 空

货未发完 = Y：
  CPD和海运周期有效 → CPD + 海运周期
  否则 → 空
```

### 3.9 收入年月不变

```text
收入年月（按RPD）
= 到货日期（按RPD）的年月

收入年月（按CPD）
= 到货日期（按CPD）的年月
```

RPD、CPD不是两笔金额，也不是两次分配；它们是同一份收入金额的两种统计时间口径。

### 3.10 其他规则继续保留

- 当月订货整个文件可选；
- 七国结转类型；
- 国家+履行供应中心运输周期；
- FCA/FOB/EXW固定5天；
- 是否解锁备货三态；
- 多个供应中心发货；
- 分批发货；
- 多次要货；
- 分批供应；
- 收入分段基础规则；
- 无要货合同显式状态；
- RPD/CPD跨期变化；
- 供应需要提拉诉求；
- 异常清单；
- Excel AutoFilter和`数据 → 清除`可用性。

Issue #20 在本重构中落实：结转类型必须按最终解析后的国家判断。

---

## 4. 旧模型的问题与新模型的边界

### 4.1 旧基表的问题

旧用户可见基表粒度：

```text
合同号 + 履行供应中心
```

但以下金额是合同级：

```text
遗留量
当月新订货
收入预测
```

同一合同存在多个履行供应中心时，合同级金额在多行重复。旧基表适合查看履行摘要，不适合作为可直接求和、继续分配和按月汇总的金额事实表。

### 4.2 V3 不恢复旧基表作为最终入口

V3 仍会生成合同+履行供应中心的 FulfillmentProjection，但它的角色变为：

```text
内部履行归纳结果
+ 用户分配时的判断上下文
+ 跨期与供应提拉的计算来源
```

它不拥有合同收入预测，不是最终金额事实，也不是最终月度汇总。

### 4.3 新的正式数据链

```text
ContractFinancialFact
合同金额唯一事实
        │
        │ 1:N
        ▼
DemandRecord
要货/履行过程证据
        │
        │ 按原规则归纳
        ▼
FulfillmentProjection
合同+履行供应中心的履行摘要
        │
        │ 形成系统分配候选
        ▼
RevenueAllocationCandidate
用户分配工作台中的候选行
        │
        │ 人工或自动确认金额
        ▼
RevenueAllocationDecision
金额分配决定
        │
        │ 同一金额按两个口径归月
        ▼
MonthlyRevenuePosting
        │
        ▼
RPD月度收入汇总 / CPD月度收入汇总
```

---

## 5. 目标领域模型

### 5.1 ContractFinancialFact

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
- demand_state；
- allocation_candidate_count；
- allocated_amount；
- unallocated_amount；
- allocation_status；
- rpd_posted_amount；
- rpd_pending_amount；
- cpd_posted_amount；
- cpd_pending_amount。

金额定义：

```text
revenue_forecast
= legacy_amount + monthly_new_order
```

每个合同只能有一条 ContractFinancialFact。

### 5.2 DemandRecord

粒度：

```text
去重后的一条要货明细证据记录
```

字段至少包括：

- demand_record_id；
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
- raw evidence summary。

`demand_record_id`用于本次运行内追溯，不作为跨期人工金额主键。不得只用源行号作为跨期身份。

### 5.3 FulfillmentProjection

粒度：

```text
合同号 + 履行供应中心
```

字段包括现有履行结果：

- contract_no；
- supply_center；
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
- row_kind；
- issue references。

### 5.4 RevenueAllocationCandidate

RevenueAllocationCandidate 是系统提供给用户进行金额判断的上下文单元。

V3 的默认候选粒度为：

```text
一条FulfillmentProjection
= 合同号 + 履行供应中心
```

原因：

1. 当前两套收入年月在该粒度上按既有规则正式计算；
2. DemandRecord没有稳定事件ID，不能安全地逐行继承人工金额；
3. 同一中心下多条状态记录已经被现有业务规则归纳成一个可解释的履行结果；
4. 用户可以通过记录数、状态摘要、日期集合和源行证据判断是否给该候选分配金额；
5. 合同金额不再复制成该行的权威金额，只有用户实际分配金额才是候选行上的可汇总金额。

候选稳定ID建议：

```text
allocation_candidate_id
= versioned_hash(
    normalized_contract_no,
    normalized_supply_center,
    row_kind
  )
```

收入年月、日期和状态变化不直接改变 candidate ID，但会形成`projection_changed`标识，提示用户复核继承金额。

### 5.5 RevenueAllocationDecision

粒度：

```text
allocation_candidate_id
```

字段至少包括：

- allocation_candidate_id；
- contract_no；
- previous_manual_amount；
- auto_allocated_amount；
- manual_allocated_amount；
- final_allocated_amount；
- allocation_source；
- allocation_status；
- allocation_note；
- inherited_from_run_id；
- projection_changed；
- review_required。

最终金额：

```text
存在有效手工分配金额
→ final_allocated_amount = 手工分配金额

否则存在有效自动分配金额
→ final_allocated_amount = 自动分配金额

否则
→ 未分配
```

空单元格表示尚未决定；数值0表示明确分配0，必须区分。

### 5.6 ContractAllocationSummary

粒度：合同号。

```text
allocated_amount
= Σ final_allocated_amount

unallocated_amount
= revenue_forecast - allocated_amount
```

状态至少包括：

- 无需分配；
- 未分配；
- 部分分配；
- 分配完成；
- 分配超额；
- 需复核。

### 5.7 MonthlyRevenuePosting

每个 RevenueAllocationDecision 对每种统计口径分别产生一个 Posting：

```text
RPD口径Posting
CPD口径Posting
```

两条 Posting 引用同一个 `final_allocated_amount`，不是两笔业务收入。

字段至少包括：

- perspective：RPD / CPD；
- allocation_candidate_id；
- contract_no；
- revenue_month；
- revenue_segment；
- posted_amount；
- pending_amount；
- posting_status；
- pending_reason；
- contract dimensions。

### 5.8 MonthlyRevenueSummary

分别从 RPD、CPD Posting 汇总，形成两张最终月度收入表。

---

## 6. 分配候选如何向用户提供判断依据

### 6.1 原始记录不是人工输入行

用户不直接面对每条 DemandRecord 输入金额。

DemandRecord用于证据追溯；RevenueAllocationCandidate用于人工判断。

### 6.2 同中心多条要货记录如何呈现

同一合同+履行供应中心存在多条 DemandRecord 时，候选行必须展示摘要，而不是隐藏复杂性。

至少包括：

- 要货记录数；
- 需求状态集合；
- 源行号摘要；
- 不同ATA日期；
- 不同ASD日期；
- 不同RPD日期；
- 不同CPD日期；
- 是否解锁备货；
- 分批发货；
- 多次要货；
- 分批供应；
- 货未发完；
- 异常引用。

完整记录放在`要货记录明细`Sheet，候选行通过`allocation_candidate_id`关联。

### 6.3 V1不自动拆分同一候选内部金额

当前没有稳定事件ID，也没有事件级正式收入年月规则，因此 V1 不允许系统：

- 按要货记录数平均；
- 按状态数量平均；
- 按RPD/CPD日期数平均；
- 把一条候选自动拆成多条假定发货；
- 为每条DemandRecord创建可继承人工金额。

如果未来业务需要同一合同+中心内部进一步拆分金额，必须先新增：

- 稳定业务批次/事件标识；或
- 明确的人工拆分单元与月份归属规则。

该能力不属于本次 V1 重构。

---

## 7. 自动分配和人工分配规则

### 7.1 单候选合同

若合同：

- revenue_forecast非0；
- 只有一个可用 RevenueAllocationCandidate；
- 收入分段不是`需判断`或`不要货`；

则可以自动：

```text
auto_allocated_amount = revenue_forecast
```

如果某一统计口径收入年月为空，仍可完成金额分配；该口径的金额进入待归月，另一口径可正常归月。

### 7.2 多候选合同

合同存在多个 RevenueAllocationCandidate 时：

- 不自动平均；
- 不按供应中心数分配；
- 不按记录数分配；
- 不按月份数分配；
- 用户填写各候选的`手工分配金额`；
- 允许只分配部分候选或部分金额。

### 7.3 需判断候选

`收入分段类别=需判断`时：

- 不自动分配；
- 即使用户填写了金额，该金额在业务状态未解决前进入待处理收入；
- 不进入正式月度当月预测；
- 用户可通过分配备注说明处理情况。

### 7.4 不要货合同

无要货合同没有 RevenueAllocationCandidate：

- ContractFinancialFact继续保留；
- revenue_forecast全部进入待处理收入；
- 原因=`不要货，无履行和收入年月依据`；
- 不生成虚构供应中心、候选行或月份。

### 7.5 未录入订货

`收入分段类别=未录入订货`时：

```text
legacy_amount = 0
monthly_new_order = 0
revenue_forecast = 0
```

因此不产生可分配金额，但仍需在月度汇总中统计合同数量。

### 7.6 部分分配

例如：

```text
合同收入预测 = 100
候选A手工分配 = 40
候选B = 空
```

则：

```text
已分配金额 = 40
待分配金额 = 60
分配状态 = 部分分配
```

已分配且可归月的40进入月度汇总；60进入待处理收入。

### 7.7 分配超额

```text
Σfinal_allocated_amount > revenue_forecast
→ 分配超额
```

处理：

- 记录`ALLOCATION_EXCEEDS_FORECAST`；
- 超额合同的分配金额不得进入正式月度汇总；
- 全额进入待处理收入，直到用户修正；
- 不自动截断或调整最后一行。

### 7.8 负数和冲销金额

系统继续支持 Decimal 负数合同金额。

分配应满足：

- 分配合计与合同收入预测同号或为0；
- 完成状态时精确相等；
- 混合正负分配导致不可解释时记录异常并待处理。

---

## 8. 历史人工金额继承

### 8.1 上一次结果的角色

GUI中的旧字段：

```text
上一次成功结果
```

重构后语义调整为：

```text
上一次结果 / 已分配结果
```

用于：

- 恢复 FulfillmentProjection 进行跨期比较；
- 继承 RevenueAllocationDecision；
- 识别候选新增、消失和变化；
- 恢复分配备注。

### 8.2 候选ID精确命中

相同 allocation_candidate_id 时：

- 继承上期手工金额；
- 继承分配备注；
- 如果履行月份、收入分段、金额或证据摘要变化，设置`projection_changed=Y`；
- 仍保留继承金额，但标记`review_required=Y`。

### 8.3 合同候选拓扑变化

以下变化需要复核：

- 新增履行供应中心；
- 原履行供应中心消失；
- 同合同候选数量变化；
- 候选从正常状态变为需判断；
- 候选收入年月发生变化；
- 合同收入预测变化导致分配不再守恒。

### 8.4 消失候选的历史金额

上期存在人工金额、本期候选消失时：

- 不静默丢弃金额；
- 生成`ORPHANED_PREVIOUS_ALLOCATION`待处理记录；
- 展示上期合同、中心、金额、月份和备注；
- 不进入本期正式月度汇总。

### 8.5 旧v0.8结果

v0.8结果没有新人工分配金额：

- 仍可用于履行跨期比较；
- 原三个人工月份字段废弃，不迁移到金额分配；
- 不生成伪造历史分配金额；
- 首次新版本运行按当前候选重新自动/人工分配。

---

## 9. 月度归纳规则

### 9.1 金额只分配一次

例如：

```text
final_allocated_amount = 40
收入年月（按RPD） = 2026-10
收入年月（按CPD） = 2026-11
```

则：

```text
RPD口径：2026-10归月40
CPD口径：2026-11归月40
```

RPD、CPD结果不能相加作为总收入。

### 9.2 可进入正式月度预测的收入分段

V1正式归月金额只包括：

```text
订未发
发未收
```

`需判断`和`不要货`不进入正式月度预测，进入待处理收入。

`未录入订货`金额为0，只统计合同数。

### 9.3 月份为空

某统计口径收入年月为空时：

- 已分配金额不能消失；
- 该口径生成 pending Posting；
- 待处理原因说明月份无法取得；
- 另一口径月份有效时可正常归月。

### 9.4 月度汇总维度

RPD和CPD两张表均按以下维度汇总：

- 收入年月；
- BG；
- 地区部；
- 国家；
- 结转类型；
- 客户群。

项目名称保留在明细层，不作为V1默认月度汇总维度，避免汇总过细；后续可通过归月明细透视。

### 9.5 月度汇总指标

最终字段：

1. 收入年月；
2. BG；
3. 地区部；
4. 国家；
5. 结转类型；
6. 客户群；
7. 当月预测；
8. 订未发；
9. 发未收；
10. 未录入订货。

定义：

```text
当月预测
= 当前统计口径、当前月份、当前维度下
  已正式归月的最终分配金额合计

订未发
= 其中收入分段类别=订未发的金额合计

发未收
= 其中收入分段类别=发未收的金额合计

未录入订货
= 当前统计口径、当前月份、当前维度下
  收入分段类别=未录入订货的去重合同数
```

由于V1正式金额分类只有订未发和发未收，因此每个汇总行应满足：

```text
当月预测 = 订未发 + 发未收
```

未录入订货的单位是`合同数`，不是金额。输出列显示名建议明确为：

```text
未录入订货（合同数）
```

同一合同在同一统计口径、同一月份、同一维度下只计一次；若同一合同在不同月份存在不同履行投影，可分别在相应月份计数。

---

## 10. 最终输出工作簿

### 10.1 核心可见Sheet

#### 10.1.1 `合同收入预测`

粒度：一合同一行。

字段建议：

1. 合同号；
2. 遗留量；
3. 当月新订货；
4. 收入预测；
5. BG；
6. 地区部；
7. 国家；
8. 结转类型；
9. 客户群；
10. 项目名称；
11. 要货状态；
12. 履行供应中心数；
13. 分配候选数；
14. 已分配金额；
15. 待分配金额；
16. 分配状态；
17. RPD已归月金额；
18. RPD待归月金额；
19. CPD已归月金额；
20. CPD待归月金额。

这是合同收入预测唯一可直接求和的权威表。

#### 10.1.2 `收入分配`

粒度：一 RevenueAllocationCandidate 一行。

该表是用户唯一主要手工操作区。

建议字段分组如下。

**A. 身份与合同金额**

1. 分配候选ID；
2. 合同号；
3. 合同收入预测（参考，不可直接汇总）；
4. 上期手工分配金额；
5. 自动分配金额；
6. 手工分配金额；
7. 最终分配金额；
8. 合同已分配金额；
9. 合同待分配金额；
10. 分配状态；
11. 分配来源；
12. 需复核；
13. 分配备注。

**B. 合同属性**

14. BG；
15. 地区部；
16. 国家；
17. 结转类型；
18. 客户群；
19. 项目名称。

**C. 履行与要货证据摘要**

20. 履行供应中心；
21. 要货记录数；
22. 需求状态摘要；
23. 源行摘要；
24. 多个供应中心发货；
25. 是否解锁备货；
26. 分批发货；
27. 多次要货；
28. 分批供应；
29. 货未发完；
30. 贸易术语；
31. 海运周期。

**D. 日期和归月依据**

32. ATA；
33. ASD；
34. RPD；
35. 最晚ASD；
36. 最晚RPD；
37. CPD；
38. 到货日期（按RPD）；
39. 到货日期（按CPD）；
40. 收入年月（按RPD）；
41. 收入年月（按CPD）；
42. 收入分段类别。

**E. 变化和异常提示**

43. 履行投影已变化；
44. 异常代码摘要；
45. 待处理原因。

黄色可编辑列：

- 手工分配金额；
- 分配备注。

`合同收入预测（参考）`会在同合同多候选行重复，只用于判断，不得作为金额汇总源。列头、批注和说明必须明确：

```text
参考值，不可直接求和
```

#### 10.1.3 `RPD月度收入汇总`

字段：

- 收入年月；
- BG；
- 地区部；
- 国家；
- 结转类型；
- 客户群；
- 当月预测；
- 订未发；
- 发未收；
- 未录入订货（合同数）。

#### 10.1.4 `CPD月度收入汇总`

字段与RPD汇总一致，统计月份使用`收入年月（按CPD）`。

#### 10.1.5 `待处理收入`

至少展示：

- 合同号；
- 分配候选ID；
- 履行供应中心；
- 合同收入预测；
- 已分配金额；
- 待分配金额；
- RPD待归月金额；
- CPD待归月金额；
- 收入分段类别；
- 处理状态；
- 待处理原因；
- 建议操作；
- 上期金额/备注参考。

处理原因至少包括：

- 未分配；
- 部分分配；
- 分配超额；
- 需判断；
- 不要货；
- RPD月份为空；
- CPD月份为空；
- 上期候选消失；
- 履行投影变化需复核；
- 源数据异常影响归月。

#### 10.1.6 `收入归月明细`

系统生成、不可人工改金额。

字段至少包括：

- 统计口径；
- 收入年月；
- 合同号；
- 分配候选ID；
- 履行供应中心；
- 最终分配金额；
- 已归月金额；
- 待归月金额；
- 收入分段类别；
- 归月状态；
- 待处理原因；
- BG；
- 地区部；
- 国家；
- 结转类型；
- 客户群；
- 项目名称。

该表是月度汇总的可审计事实明细，也是后续Excel透视的规范数据源。

### 10.2 辅助可见Sheet

继续保留：

- `要货记录明细`；
- `RPD跨月变化`；
- `CPD跨月变化`；
- `供应需要提拉诉求清单粗表`；
- `异常清单`。

三张变化/差异表在`国家`后增加`结转类型`。

`要货记录明细`保存去重后的 DemandRecord，并通过分配候选ID关联到`收入分配`。

### 10.3 隐藏系统Sheet

#### `_fulfillment_projection`

保存正式 FulfillmentProjection、row_kind、candidate ID及比较证据。

#### `_tool_meta`

schema建议升级为`4`或更高，至少保存：

- schema_version；
- run_id；
- rules_version；
- candidate_id_version；
- 输出数据集及显示Sheet；
- 字段ID与显示名称；
- 金额精度；
- row_kind；
- 源文件指纹；
- 生成时间。

DemandRecord可以写入可见`要货记录明细`，无需额外复制到隐藏Sheet。

---

## 11. 用户操作闭环

### 11.1 第一次运行

```text
选择本期源文件
→ 读取和规范化
→ 构建合同金额事实
→ 生成履行归纳结果
→ 生成分配候选
→ 单候选可自动分配
→ 多候选进入人工分配
→ 输出月度汇总、归月明细和待处理收入
```

### 11.2 用户编辑

用户打开结果工作簿，主要查看：

- 合同收入预测；
- 收入分配；
- 要货记录明细；
- 待处理收入。

用户只在`收入分配`填写：

- 手工分配金额；
- 分配备注。

### 11.3 再次运行

用户将已保存的结果选择为：

```text
上一次结果 / 已分配结果
```

工具：

1. 读取上期人工金额和备注；
2. 恢复上期履行投影进行跨期比较；
3. 重新计算本期合同金额和履行结果；
4. 按candidate ID继承人工决定；
5. 标记候选、月份或合同金额变化；
6. 重新校验合同分配守恒；
7. 重新生成RPD/CPD月度汇总；
8. 保留所有未分配和无法归月金额；
9. 输出新文件。

输出文件不得覆盖作为输入的上一次结果。

---

## 12. 架构设计

### 12.1 Domain

新增明确领域类型：

```text
ContractFinancialFact
DemandRecord
FulfillmentProjection
RevenueAllocationCandidate
RevenueAllocationDecision
ContractAllocationSummary
MonthlyRevenuePosting
MonthlyRevenueSummaryRow
PendingRevenueRow
PreviousRunState
RunRequest
RunResult
```

禁止继续使用一个`BaseRow.values`字典承载所有粒度。

旧BaseRow仅允许作为v0.8结果兼容读取类型和Golden对比过渡类型。

### 12.2 Services

建议拆分：

```text
ContractFactBuilder
- 合同全集
- 合同金额
- 合同属性
- 最终国家和结转类型

DemandRecordService
- 去重后记录
- 证据ID和摘要

FulfillmentProjectionService
- 复用现有RevenueEngine履行计算
- 生成合同+中心归纳结果

AllocationCandidateBuilder
- 一FulfillmentProjection一候选
- candidate ID
- 证据摘要

AllocationService
- 自动/手工分配
- 历史继承
- 部分分配
- 超额和合同守恒

MonthlyRevenueService
- 两种Posting
- 待归月
- 月度明细
- RPD/CPD汇总
- 未录入订货合同数

FulfillmentComparisonService
- RPD/CPD跨期变化
- 有要货/不要货状态变化

SupplyPullService
- 同期两口径差异
```

### 12.3 Application

使用结构化请求：

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
- demand_records
- fulfillment_projections
- allocation_candidates
- allocation_decisions
- allocation_summaries
- monthly_postings
- rpd_monthly_summary
- cpd_monthly_summary
- pending_revenue
- comparisons
- issues
- output_path
```

Application只负责流程编排，不实现业务规则。

### 12.4 Adapters

```text
ExcelSourceReader
PreviousResultReader
ExcelResultWriter
```

PreviousResultReader独立读取新输出和旧v0.8结果，不继续把历史导入职责堆入源文件Reader。

### 12.5 Configuration

当前固定五Sheet、32列配置改为数据集契约：

```text
output.datasets.contract_forecast
output.datasets.allocation
output.datasets.rpd_monthly_summary
output.datasets.cpd_monthly_summary
output.datasets.pending_revenue
output.datasets.monthly_posting_detail
output.datasets.demand_record_detail
output.datasets.rpd_changes
output.datasets.cpd_changes
output.datasets.supply_pull
output.datasets.issues
output.datasets.fulfillment_projection
```

每个数据集配置：

- Sheet名称；
- 字段ID、显示名称和顺序；
- 金额/日期/文本类型；
- 可编辑字段；
- 是否隐藏；
- 是否筛选；
- 冻结位置；
- 列宽上限；
- 数据验证规则。

配置定义展示，不定义复杂业务流程。

---

## 13. 当前代码复用与替换

### 13.1 可直接复用或小改

- `adapters/sheet_locator.py`；
- `services/field_matching.py`；
- `services/normalization.py`；
- 源文件读取和字段解析；
- 完全重复行去重；
- Decimal金额规范；
- 国家identity；
- `services/stock_unlock.py`；
- 海运周期查找与异常分型；
- 现有日期、货未发完和到货计算函数；
- Issue模型；
- GUI文件选择基础结构；
- AutoFilter写出基础能力。

### 13.2 拆分后复用

- `services/calculation.py`
  - 合同事实迁入ContractFactBuilder；
  - 履行归纳迁入FulfillmentProjectionService；
- `services/comparison.py`
  - 改为消费FulfillmentProjection；
- `adapters/excel_reader.py`
  - 源读取保留；
  - 历史结果读取拆分。

### 13.3 需要结构性重写

- `domain/models.py`；
- `application/pipeline.py`；
- `adapters/excel_writer.py`；
- `config/default.json`输出结构；
- `config.py`输出校验；
- 旧BaseRow主数据流；
- 旧PreviousData主数据流；
- GUI结果摘要和历史结果语义；
- 依赖旧五Sheet结构的集成测试。

---

## 14. 不允许的实现

- 把每条DemandRecord直接当成一次独立发货；
- 以源行号作为跨期人工金额主键；
- 在旧BaseRow上继续追加分配字段；
- 继续把合同收入预测复制到供应中心行作为权威金额；
- 要求用户自己记住参考金额不能求和而不给系统守恒保护；
- 按供应中心数、记录数、日期数或月份数平均分配；
- 将相同状态记录错误拆成多笔收入；
- 为RPD、CPD维护两套手工金额；
- 月份为空时丢弃金额；
- 部分分配时自动把剩余金额塞给最后一行；
- 分配超额时自动截断；
- Writer重新计算业务规则；
- 用Excel公式代替领域金额守恒；
- 只修改GUI或Sheet标题而不重构领域模型。

---

## 15. 金额与质量门禁

### 15.1 合同金额唯一

```text
COUNT(ContractFinancialFact by contract_no) = 1
```

### 15.2 合同分配守恒

```text
allocated_amount + unallocated_amount
= revenue_forecast
```

### 15.3 RPD口径守恒

```text
RPD已归月金额 + RPD待归月金额
= allocated_amount
```

再与未分配金额结合：

```text
RPD已归月 + RPD待归月 + 合同未分配
= revenue_forecast
```

### 15.4 CPD口径守恒

```text
CPD已归月 + CPD待归月 + 合同未分配
= revenue_forecast
```

### 15.5 月度指标一致

每个RPD/CPD汇总行：

```text
当月预测 = 订未发 + 发未收
```

### 15.6 Golden回归

除已批准的 Issue #20 修正外，FulfillmentProjection必须与v0.8旧基表对应履行字段一致：

- 供应中心分组；
- 日期聚合；
- 海运周期；
- 货未发完；
- 两套到货日期；
- 两套收入年月；
- 收入分段；
- 备货三态；
- 不要货状态。

---

## 16. 测试与验证计划

### 16.1 既有规则回归

- 当月订货可选；
- Sheet2/Sheet3定位；
- exact→contains字段匹配；
- 完全重复行；
- 空白/VALUE；
- Decimal金额；
- 七国及Issue #20；
- 海运周期异常；
- 备货三态；
- 日期聚合；
- 货未发完；
- 到货日期；
- 收入年月；
- 收入分段；
- 不要货；
- 跨期变化；
- Excel筛选。

### 16.2 DemandRecord与证据

- 完全重复记录不进入证据数；
- 同中心多状态记录保留证据；
- 需求状态摘要稳定；
- 日期集合摘要正确；
- 源行追溯正确；
- DemandRecord不直接拥有合同金额。

### 16.3 分配候选

- 同合同多中心形成多个候选；
- 同中心多记录只形成一个候选；
- candidate ID不依赖源行顺序；
- 日期变化不改变candidate ID但标记projection_changed；
- 无要货合同无候选；
- 要货存在但中心为空不生成正常候选并保留异常。

### 16.4 分配

- 单候选自动分配；
- 多候选无人工金额；
- 部分分配；
- 完整分配；
- 0与空区分；
- 超额；
- 负数合同；
- 上期精确继承；
- 候选新增/消失；
- 合同金额变化；
- projection_changed复核；
- 需判断不进入正式汇总；
- 不要货全部待处理。

### 16.5 月度统计

- 同一金额进入RPD/CPD不同月份；
- 两种口径引用同一分配金额；
- 一种月份有效、另一种为空；
- 部分分配；
- 订未发金额；
- 发未收金额；
- 未录入订货去重合同数；
- 当月预测=订未发+发未收；
- RPD/CPD合同级和全局守恒；
- 禁止两口径相加。

### 16.6 工作簿往返

```text
生成
→ 用户填写部分金额和备注
→ 保存
→ 作为上一次结果导入
→ 继承金额
→ 重新计算
→ 月度汇总正确
→ 未分配差额仍可见
```

测试：

- 列移动；
- 插入非关键列；
- 显示名变化但metadata可恢复；
- 空白与0；
- 候选变化；
- 上期候选消失；
- 输出文件不能覆盖输入结果。

### 16.7 Windows Excel实机验证

- 黄色可编辑列；
- 金额输入；
- 0和空白；
- 筛选及`数据→清除`；
- 冻结首行；
- 多Sheet导航；
- 保存、关闭、重新打开；
- 作为上一次结果再次导入；
- 中文、日期、金额格式；
- 宽表的横向浏览体验。

自动OOXML验证不能替代桌面Excel实机验证。

---

## 17. 分阶段实施

全部实施继续在：

```text
refactor/revenue-allocation-v1
```

进行。

### Phase 0：设计批准与Schema冻结

- 用户确认V3关键边界；
- 状态改为`APPROVED_FOR_IMPLEMENTATION`；
- 冻结输出Sheet和字段；
- 冻结candidate ID版本；
- 建立虚构Golden样例。

### Phase 1：领域拆分与双轨履行计算

- 新增ContractFinancialFact、DemandRecord、FulfillmentProjection；
- 从RevenueEngine拆分服务；
- 暂时保留旧结果用于Golden；
- 修Issue #20。

Gate：除Issue #20外，既有履行结果一致。

### Phase 2：分配候选和历史状态

- RevenueAllocationCandidate；
- candidate ID；
- PreviousRunState；
- 上期金额和备注继承；
- 候选变化诊断。

### Phase 3：分配服务

- 单候选自动分配；
- 多候选手工分配；
- 部分分配；
- 超额；
- 负数；
- 合同守恒；
- 待处理收入。

### Phase 4：Posting和月度汇总

- RPD/CPD Posting；
- 月份为空待归月；
- RPD月度收入汇总；
- CPD月度收入汇总；
- 未录入订货合同数；
- 全局守恒。

### Phase 5：新工作簿

- 新核心和辅助Sheet；
- 收入分配宽表；
- 黄色可编辑列；
- 要货记录明细；
- metadata schema升级；
- 往返测试。

### Phase 6：跨期、供应提拉和异常迁移

- 比较服务改用FulfillmentProjection；
- 三张表增加结转类型；
- 不要货状态变化回归；
- Issue #10实机回归。

### Phase 7：GUI、打包和本地验收

- GUI摘要改为合同、候选、待处理和月度金额；
- 更新历史结果说明；
- EXE构建；
- Windows Excel实机验证；
- 本地真实数据完整往返。

---

## 18. 建议WRITE_SCOPE

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
src/revenue_tool/services/demand_records.py
src/revenue_tool/services/fulfillment_projection.py
src/revenue_tool/services/allocation.py
src/revenue_tool/services/monthly_revenue.py
相关测试和虚构fixture
README.md
新Schema、实施计划和验证报告
```

不得提交真实业务Excel或真实业务数据。

---

## 19. 实施批准前的唯一关键确认

V3 已将最新业务理解闭合为以下实施边界：

```text
DemandRecord
= 要货/履行过程证据，不直接分配金额

FulfillmentProjection
= 按既有规则形成的合同+履行供应中心归纳结果

RevenueAllocationCandidate
= 默认一条FulfillmentProjection一行
= 用户分配金额的判断上下文

合同金额
= 只存在于ContractFinancialFact

月度汇总
= 只汇总最终分配金额，不汇总参考合同金额
```

该边界解决了：

- 不能证明每条源记录是一次独立发货；
- 合同金额在多中心重复；
- 用户缺乏分配判断信息；
- 人工金额无法稳定跨期继承；
- RPD/CPD被误解成两套金额；
- 月度汇总缺乏金额守恒。

用户确认该边界后，文档状态更新为：

```text
APPROVED_FOR_IMPLEMENTATION
```

并进入Phase 1。
