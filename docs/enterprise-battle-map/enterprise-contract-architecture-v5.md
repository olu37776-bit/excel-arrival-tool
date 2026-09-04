# 企业作战地图：契约驱动架构 V5

**状态：CURRENT SHARED ARCHITECTURE AUTHORITY**  
**取代：`enterprise-contract-architecture-v4.md` 中与本文件冲突的内容**  
**代码长期分支：`feature/enterprise-battle-map`**

---

## 1. 本版依据

本版不是重新设计框架，而是根据已完成的 Runtime Survey、MOX Create/Edit Contract Audit 和客户数据修复结果，把现有“契约驱动、模块独立、适配器串联”架构收敛为真正端到端可验证的运行链。

已确认事实：

1. MOX Field Contract 字段主体正确，实际 Create/Edit renderer 会消费 Contract；
2. MOX 实际运行路径是 `getCreateFields()` / `getEditFields()`，但旧测试曾验证 `getCreateProjection()` / `getEditProjection()`；
3. MOX 应为 4 个顶层 group：客户信息、无线格局、微波格局、作战情况；其他模块为 3 个 group：客户信息、业务格局、作战情况；
4. Heatmap 当前仍有使用中文 label 作为字段身份的实现；
5. `updateMoxNetwork()` 仍接受 `office`、`customer`、`major_project`、`progress` 等旧 key；
6. Progress 当前存在“进展历史表 + `battleProgress` 文本”双写；
7. 客户查询 SQL 曾只查询 `region/office/country/customer`，漏掉 `customer_id`，导致关系主键链路中断；该问题已定位并修复，后续作为永久回归门禁；
8. 测试曾出现验证非真实运行 Projection、单向字段检查、漏测 option-set 空值等盲区。

因此当前核心问题不是缺少更多抽象层，而是 **canonical 业务身份没有在所有实际消费者中被强制守恒**。

---

## 2. 端到端唯一原则

企业模块继续使用既有主链：

```text
Canonical Authority / Excel
        ↓
Module Field Contract
        ↓
Runtime Projection
        ↓
Table / Create / Edit
        ↓
API canonical payload / response
        ↓
Persistence mapping / database.js
        ↓
SQLite / Relation / History table
```

旁路消费者：

```text
Field Contract canonical key
├─ Metric Contract
├─ Heatmap field references
├─ Customer relation
└─ Progress projection/editor
```

硬规则：

> 用户可见 label 只是展示文本；DB column 只是持久化名称；真正跨层稳定身份只能是 canonical key。

任何运行时层不得自行创造第二套业务 key、旧 alias、中文 label identity 或平行事实源。

---

## 3. Field Contract 与 Runtime Projection

### 3.1 group 是唯一表单分组语义

Field Contract 统一使用 `group`。

MOX：

```text
客户信息
无线格局
微波格局
作战情况
```

TOB / ISP / 电力 / 大企：

```text
客户信息
业务格局
作战情况
```

Renderer 只能按 Contract `group` 组织字段，不得重新解释业务归属。

### 3.2 Runtime Projection 只有一套算法

真实页面使用的 Projection 才是 Runtime Authority。

当前实际 Create/Edit 路径已确认围绕：

```text
getCreateFields()
getEditFields()
```

收敛规则：

- 保留一套过滤、排序、分组算法；
- `getCreateProjection()` / `getEditProjection()` 如无消费者则删除；
- 如仍有调用方，则只能成为对唯一实现的薄包装；
- 不允许 Production 走 A 算法、测试验证 B 算法；
- 无消费者 helper（例如已确认未使用的 `getMoxFromSections()`）在确认无引用后删除。

### 3.3 双向 Conformance

必须验证：

```text
Contract expected keys == Runtime actual keys
```

分别覆盖 Table / Create / Edit，并验证：

- 无缺失；
- 无额外；
- 无重复；
- order 一致；
- group 一致；
- option-set 完整。

禁止仅验证 `actual ⊆ contract` 的单向检查。

---

## 4. API：只接受 canonical key

目标态 API、service 和 `database.js` 活动运行时不得继续接受旧字段 key。

例如 MOX 已确认的旧 key：

```text
office
customer
major_project
progress
```

不得继续由 `updateMoxNetwork()` 或等价活动函数接收、翻译或 fallback。

规则：

1. 新请求只使用 canonical key；
2. API adapter 只在 canonical key 与 DB column 之间映射；
3. 历史旧字段只允许存在于一次性 Migration；
4. 生产运行时不得 `legacyAlias → canonical`；
5. 测试必须证明 legacy key 不再被活动更新路径接受；
6. 删除旧 key 支持前必须先确认当前 UI/API 调用方均已使用 canonical key。

---

## 5. Customer relation：关系主键必须贯穿

客户主数据由独立 `customers` 表负责，业务记录通过 `customer_id` 关联。

已确认过的失败模式：SQL 能返回地区部、代表处、国家、客户名称，但漏掉 `customer_id`，导致业务关系链断开。

因此永久门禁为：

```text
customers.customer_id
→ database.js customer SELECT
→ API response
→ frontend normalization
→ customer candidate
→ unique customer selection
→ create payload.customer_id
→ server existence validation
→ business table.customer_id
```

每一层都必须保留真实 `customer_id`。

禁止：

- 通过客户名称作为关系身份；
- 同名客户默认取第一条；
- 查询成功但缺 `customer_id` 仍视为成功；
- 模块业务表重复保存客户展示字段作为第二主数据源。

---

## 6. Heatmap：字段身份必须 canonical

Heatmap 已经是企业页面正式消费者，但其业务字段引用必须遵守同一 canonical identity。

规则：

1. Heatmap 数据转换、维度、measure、tooltip 字段引用必须使用 canonical key；
2. 中文 label 只用于 UI 展示，不得作为 lookup key；
3. DB column 不得直接泄漏到 Heatmap UI 配置；
4. Heatmap 引用的每个 canonical key 必须存在于当前模块 Field Contract；
5. 当前 Heatmap 业务规则未冻结的部分不得趁本轮自行改写；
6. 本轮允许在不改变现有业务结果的前提下，把 label-based lookup 替换为 canonical-key lookup；
7. 后续模块 Heatmap 如建立独立 Heatmap Contract，其中所有字段引用必须是 canonical key。

Conformance Gate 至少检查：

```text
HEATMAP_REFERENCED_KEYS ⊆ MODULE_FIELD_CONTRACT_KEYS
LABEL_AS_FIELD_IDENTITY = 0
```

---

## 7. Progress：只能有一个持久化事实源

当前调查确认 Progress 存在：

```text
进展历史表
+
battleProgress 文本字段
```

双写会产生一致性问题，目标态不可接受。

结合现有“独立新增进展弹窗、追加、编辑、历史”行为，最终原则是：

> **进展历史表是 Progress 唯一持久化 Authority。**

`battleProgress` 保留为 canonical 业务身份，但它的角色调整为：

- 表格/详情中的“当前/最新作战进展”投影；
- Create/Edit 中特殊 Progress editor 的业务入口；
- 从进展历史关系读取，不在 MOX 业务表维护第二份可写文本事实。

目标链：

```text
Progress History
→ latest/current projection
→ canonical battleProgress
→ Table/Edit display
```

写入链：

```text
独立新增/编辑进展 UI
→ Progress API
→ Progress History table
```

禁止：

- 同一操作同时写 history 和 business-table text；
- history 与 `battleProgress` column 互相兜底；
- 用普通 textarea 取代现有特殊进展能力。

### 7.1 数据收敛

删除业务表 Progress 文本事实前，必须先比较：

```text
business text
vs
history latest projection
```

处理：

- 完全一致：停止双写后可删除/废弃 business text 持久化列；
- business text 有独有内容：必须先安全迁移到 history；
- 无法可靠保留历史语义/时间信息：阻塞并报告，不得静默丢数据或伪造业务时间。

Schema 变更继续使用 `V*.sql + _migrations + transaction`。

---

## 8. Persistence 与数据库仍是正式 Contract 链

数据库不是页面之后的“实现细节”，而是 canonical chain 的正式消费者。

必须保持：

```text
canonical key
→ API mapping
→ database.js mapping
→ SQLite column / relation
```

Validator / tests 必须验证：

- mapping 唯一；
- 新建库与升级库一致；
- CRUD round-trip；
- 关系字段完整；
- legacy runtime mapping 为 0；
- Progress 只有一个 persistence authority；
- Customer `customer_id` 贯穿。

---

## 9. Metric Contract 保持现有设计

Metric Contract 继续独立于 Field Contract，通过 canonical key 引用字段。

同一 `where` 同时用于：

```text
metric calculation
+
click-to-filter
```

当前没有证据需要重构 Metric 架构，只需要在统一审查中验证真实实现没有使用 label/legacy key/另一套条件。

---

## 10. UI group 视觉机制

所有 Create/Edit 顶层 group 使用共享样式机制：

- 明显标题层级；
- 稳定上间距；
- 标题与字段区有明确分隔；
- 相邻 group 不得视觉粘连；
- Create/Edit 一致；
- MOX 四组和其他模块三组只由 Contract 决定，不由 CSS/renderer 硬编码模块业务字段。

---

## 11. End-to-End Conformance Gate

本阶段必须补齐以下门禁。

### 11.1 UI Runtime

- Table/Create/Edit expected == actual；
- group exact match；
- renderer 测试真实 runtime function；
- option-set 完整。

### 11.2 API

- canonical key only；
- legacy request key 不被接受；
- response canonical；
- unknown/legacy key 有可诊断失败。

### 11.3 Customer

- SQL 必须包含 `customer_id`；
- API/normalization/save 全链保留；
- unique match。

### 11.4 Heatmap

- canonical key references；
- label identity 为 0。

### 11.5 Progress

- 单一 history persistence；
- 双写为 0；
- latest projection 正确；
- 添加/编辑进展后读取一致。

### 11.6 Database

- Migration 注册、事务、回滚、幂等；
- 新建/升级 Schema 一致；
- CRUD round-trip；
- legacy runtime mapping 为 0。

---

## 12. 推进策略

当前不要一次性重构五个模块。

顺序：

```text
MOX End-to-End Canonical Convergence
→ 自动验证
→ 独立审查
→ 用户人工验收
→ MOX REFERENCE_IMPLEMENTATION_V1
→ 将已验证门禁应用到 TOB/ISP/电力/大企
→ 企业模块统一审查
→ 企业首页最终建设
```

MOX 通过前，不再以未收敛的 MOX 实现作为其他模块新增机制的最终参考。
