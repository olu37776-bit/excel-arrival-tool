# 企业作战地图：MOX Canonical Authority V4

**状态：CURRENT MOX AUTHORITY**  
**文档分支：`enterprise-battle-map-authority`**  
**本地实施分支：`feature/enterprise-battle-map`**  
**取代：`mox-canonical-authority-v3.md` 及所有与本文件冲突的本地 MOX 字段、Schema、Contract、WRITE_SCOPE 和 Review 结论**

---

## 1. 当前目标

MOX 必须成为企业板块第一个完整、可复用的参考实现。

当前目标不是继续兼容旧字段，而是让以下各层最终只认识同一套 canonical 字段：

```text
MOX Field Contract
├─ 表格
├─ 新增
├─ 编辑
├─ API
├─ database.js
└─ SQLite

MOX Metric Contract
├─ 统计值
└─ 点击筛选表格
```

当前 41 个字段是封闭集合。除明确必要的记录主键和系统技术列外，本文件未列出的 MOX 业务字段一律删除。

---

## 2. Authority 顺序

1. 本文件；
2. 本地“企业作战地图基表”的 MOX Sheet，用于核实列、Row2、Row3、Data Validation；
3. 用户后续明确修正；
4. 当前代码、API、`database.js`、SQLite，仅用于判断差距；
5. 旧本地文档、旧 Schema 和旧配置，仅作历史参考。

Excel 是原始需求来源，但本文件是经用户确认后的当前目标定义。本地 Agent 不得从旧代码或 Excel 中自行扩充第 42 个字段。

---

## 3. 代码目录与唯一 Authority

契约配置必须位于 `src/config` 之下。

当前标准：

```text
src/config/enterprise/
├─ field-contract.js
├─ field-projections.js
├─ contract-validator.js
├─ metric-engine.js
├─ option-sets.js
├─ mox-field-contract.js
└─ mox-metric-contract.js
```

要求：

- 不使用 `src/enterprise` 作为 Contract Authority 目录；
- `src/enterprise` 下已经创建的 MOX Contract/Schema 配置必须迁移到 `src/config/enterprise`；
- 组件和页面无需因契约目录迁移而全部移动；
- 旧 `mox-field-schema.js` 不得继续定义第二份字段集合、顺序、枚举或权限；
- `src/config` 中如果已有旧 `mox-field-contract.js`、`mox-field-schema.js`、`mox-metric-contract.js`，必须收敛为当前目录中的唯一 Field Contract 和 Metric Contract；
- 所有 import 迁移完成后删除旧文件，不保留 re-export、fallback 或双轨兼容。

---

## 4. Field Contract 对象

每个字段至少包含：

```js
{
  key,
  label,
  section,
  order,

  authority: {
    source,       // excel | requirement
    sheet,
    column,
    row2Group,
    row3Label
  },

  data: {
    type,         // text | number | percent | enum | relation | progress
    unit
  },

  ui: {
    table: {
      visible,
      formatterId
    },
    create: {
      visible,
      editable,
      controlId
    },
    edit: {
      visible,
      editable,
      controlId
    }
  },

  runtime: {
    source,       // business-table | customer-relation
    apiReadField,
    apiCreateField,
    apiUpdateField,
    dbColumn,
    dbType
  },

  validation: {
    required,
    optionSetId,
    min,
    max
  },

  behavior: {
    editorId,
    formatterId
  }
}
```

Contract 描述最终态，不包含 `legacyAliases`、旧字段 fallback 或双写配置。旧数据迁移只存在于一次性 Migration。

---

## 5. 新增与编辑的三个同级 Section

MOX 新增和编辑只使用：

```text
客户信息 ｜ 业务格局 ｜ 作战情况
```

要求：

- 三个 Section 为同级区块；
- 不再显示旧“客户信息 / 业务信息”二分结构；
- 不再把“无线格局”和“微波格局”渲染为两个顶层 Section；
- `业务格局`内部先展示无线字段，再展示微波字段；
- Contract 可保留 `wireless` / `microwave`内部元数据用于区分重名字段，但 UI 顶层仍只有三个 Section；
- 表格不显示 Section 标题，按 1—41 顺序展开；
- 作战进展属于“作战情况”，固定放最后。

---

## 6. MOX 最终 41 个业务字段

### 6.1 客户信息（1—6）

| order | canonical key | 用户可见字段 | UI/数据规则 |
|---:|---|---|---|
| 1 | `region` | 地区部 | 复用现有客户联动 |
| 2 | `representativeOffice` | 代表处 | 复用现有客户联动 |
| 3 | `country` | 国家 | 客户主数据 |
| 4 | `customerId` | 客户ID | 自动匹配，不可手填 |
| 5 | `customerName` | 客户名称 | 客户主数据 |
| 6 | `customerCategory` | 客户类别 | 可选枚举，见下文 |

MOX 不包含“行业”。

#### 客户类别

`客户类别`必须在新增和编辑中可选择，固定选项：

- 空值；
- 核心NA；
- 战略NA。

不得继续因为“客户信息默认只读”而禁用该字段。本规则是 MOX 的明确例外。

客户类别属于客户主数据。保存时必须更新客户表中的权威字段，不得在 MOX 业务表新增重复客户类别列。若当前客户 API 没有安全更新能力，应补齐明确的客户主数据更新路径，而不是把值静默存进 MOX 表。

其他客户字段在编辑时保持只读，编辑业务字段不得改变 `customer_id`。

### 6.2 业务格局：无线部分（7—18）

| order | canonical key | 用户可见字段 |
|---:|---|---|
| 7 | `stage` | 阶段 |
| 8 | `wirelessSpaceMusd` | 无线空间（MUSD） |
| 9 | `narrowbandLandscape` | 窄带格局 |
| 10 | `broadbandLandscape` | 宽带格局 |
| 11 | `broadbandSiteCount` | 宽带站点数 |
| 12 | `broadbandSpectrum` | 宽带频谱 |
| 13 | `wirelessSpectrumStatus` | 频谱状态 |
| 14 | `wirelessOpportunity2026` | 26年机会点 |
| 15 | `wirelessSpace2026BaseStations` | 26年空间（基站数量） |
| 16 | `wirelessOpportunitySpace2027To2028` | 27-28年机会空间（基站数据量） |
| 17 | `baseStationUnitPriceUsd` | 基站单价（xxx美金/站） |
| 18 | `priority` | 优先级 |

确认枚举：

- 阶段：孵化 / 突破 / 纵深；
- 优先级：A / B / C / D；
- 无线 26年机会点：Y（有企业无线项目）/ N（无企业无线项目）。

已确认 Excel：MOX `F`列正式字段为“阶段”。

### 6.3 业务格局：微波部分（19—28）

| order | canonical key | 用户可见字段 |
|---:|---|---|
| 19 | `fiberizationRate` | 光纤化率 |
| 20 | `microwaveInstalledLinkCount` | 微波存量总链路数 |
| 21 | `microwaveOurLandscape` | 存量我司格局 |
| 22 | `microwaveCompetitorShare` | 现网友商份额 |
| 23 | `microwaveSpectrumStatus` | 频谱状态 |
| 24 | `competitorSpaceHops` | 友商空间（跳数） |
| 25 | `microwaveOpportunity2026` | 26年机会点 |
| 26 | `baseStationBackhaulSpace2026Hops` | 26年基站回传空间（微波跳数） |
| 27 | `videoBackhaulSpace2026Hops` | 26年视频回传空间（微波跳数） |
| 28 | `microwaveGap2026` | 26年GAP |

确认枚举：微波 26年机会点为 Y（有微波项目）/ N（无微波项目）。

重名字段必须完全独立：

- `wirelessSpectrumStatus` ≠ `microwaveSpectrumStatus`；
- `wirelessOpportunity2026` ≠ `microwaveOpportunity2026`。

它们必须使用不同 canonical key、API 字段、`database.js` 映射和 SQLite 列。

### 6.4 作战情况（29—41）

| order | canonical key | 用户可见字段 |
|---:|---|---|
| 29 | `overallSpaceTier` | 整体空间 |
| 30 | `focusProject` | 作战分类-是否重点项目 |
| 31 | `spaceInsight` | 空间洞察 |
| 32 | `projectStatus` | 项目状态 |
| 33 | `projectRiskStatus` | 项目风险状态 |
| 34 | `overallSpaceHops` | 整体空间（跳） |
| 35 | `overallSpaceMusd` | 整体空间（M$） |
| 36 | `space2026Hops` | 26年空间（跳） |
| 37 | `orderSpace2026Musd` | 26年订货空间（$M） |
| 38 | `orderedHops` | 已下单数量（跳） |
| 39 | `orderedAmountMusd` | 已下单金额（$M） |
| 40 | `frontlineContact` | 一线接口人 |
| 41 | `battleProgress` | 作战进展 |

确认规则：

- 整体空间：肥肉 / 瘦肉 / 骨头；
- 作战分类-是否重点项目：是 / 否；
- 空间洞察：已孵化 / 孵化中；
- 项目状态：已签单 / 推进中 / 跟踪；
- 项目风险状态：用于标识高风险；
- `作战分类-是否重点项目`是一个完整字段，不得拆分；
- 当前页面已有重点项目筛选必须直接使用 canonical `focusProject`；
- 作战进展固定为最后一项。

---

## 7. 单位规范

所有带单位的用户可见字段使用中文全角括号：

```text
字段名（单位）
```

包括：

- 无线空间（MUSD）；
- 26年空间（基站数量）；
- 27-28年机会空间（基站数据量）；
- 基站单价（xxx美金/站）；
- 友商空间（跳数）；
- 26年基站回传空间（微波跳数）；
- 26年视频回传空间（微波跳数）；
- 整体空间（跳）；
- 整体空间（M$）；
- 26年空间（跳）；
- 26年订货空间（$M）；
- 已下单数量（跳）；
- 已下单金额（$M）。

---

## 8. 明确删除的字段

以下字段不是 MOX 目标字段：

- `dpm`；
- `remark`；
- `service_interface`；
- `entered_amount`；
- `space_26`；
- `produce_owner`；
- `industry`；
- `latest_progress`；
- `phase_wireless`；
- 任何不属于本文件 41 项且不是明确必要技术列的旧业务字段。

删除范围：

1. 表格；
2. 新增；
3. 编辑；
4. API 活动请求/响应；
5. `database.js` CRUD、映射和 Validation；
6. 最终 SQLite Schema；
7. 活动 Contract/Schema/config；
8. 过期测试。

不保留长期 alias、fallback、双读、双写或旧配置 re-export。

一次性迁移：

- `entered_amount`历史数据迁移到 `orderedAmountMusd`后删除旧列；
- `latest_progress`历史数据迁移到 `battleProgress`后删除旧列；
- 其他无目标对应字段直接舍弃。

---

## 9. 作战进展特殊实现

作战进展必须使用当前 TOB 页面中仍然正确工作的进展新增/编辑实现作为直接参考。

要求：

- 复用 TOB 当前有效进展组件、handler 或交互模式；
- MOX 用户可见名称为“作战进展”；
- 继承原进展追加、编辑、保存和回填能力；
- 不得退化为普通 input 或 textarea；
- 不得继续使用 `latest_progress`作为活动 canonical 字段；
- 不得复制一套新的不一致进展组件。

---

## 10. 点击新增“获取客户数据失败”

这是当前阻塞问题，必须修复真实根因。

追踪链路：

```text
MOX新增弹窗
→ 客户数据请求
→ API route
→ database.js客户查询
→ 客户表
```

必须检查：

- URL、method、请求参数；
- API route 是否注册；
- 响应结构是否与前端一致；
- `customer_id`改造是否破坏查询；
- `database.js` SQL 与客户表列是否一致；
- 错误是否被统一 catch 掩盖。

禁止仅隐藏错误提示。修复后必须有 API 成功、API 失败、新增初始化、地区部/代表处联动和 customer_id 匹配测试。

---

## 11. V34 与数据库最终态

当前已知：

- 目标数据库列曾缺失；
- V34 SQL 曾写错；
- V34 曾未注册到 `database.js` Migration执行链；
- `database.js`仍有旧字段活动映射。

必须保证：

```text
V34.sql
→ database.js注册和有序执行
→ 事务内完成
→ 成功后写入_migrations
```

要求：

- 修复 SQL 语法；
- 明确注册 V34；
- 失败回滚且不登记版本；
- 重复启动不重复执行；
- 新建库与旧库升级后最终 MOX Schema 一致；
- 最终 Schema 只包含 41 个目标字段对应的持久化列、`customer_id`、记录主键和明确必要技术列；
- `dpm`、`remark`、`service_interface`、`entered_amount`、`space_26`、`produce_owner`、`latest_progress`、`phase_wireless`等不得继续存在。

---

## 12. 表格、新增与编辑

必须由同一 Field Contract 派生：

```text
MOX_FIELD_CONTRACT
├─ table projection
├─ create projection
└─ edit projection
```

目标：

- `EXTRA_TABLE_FIELDS=0`；
- `EXTRA_CREATE_FIELDS=0`；
- `EXTRA_EDIT_FIELDS=0`。

要求：

- 表格按 order 1—41；
- 新增与编辑按三个 Section 渲染；
- 客户类别在新增和编辑中均为可选下拉；
- 除客户类别外，其他客户信息在编辑中只读；
- 一线接口人保留；
- 服务接口人、备注、行业、旧进展字段均不存在；
- 作战进展使用 TOB 的有效特殊实现。

---

## 13. Metric Contract 与点击筛选

顶部只有三个并列大模块：

- 空间洞察；
- 当年项目；
- 空间拓展。

九个指标：

| metricKey | 显示 | where | aggregate |
|---|---|---|---|
| `insight.incubated` | 已孵化 | `spaceInsight=已孵化` | count |
| `insight.incubating` | 孵化中 | `spaceInsight=孵化中` | count |
| `annual.total` | 总项目数 | `projectStatus IN（已签单，推进中）` | count |
| `annual.signed` | 已签单 | `projectStatus=已签单` | count |
| `annual.inProgress` | 推进中 | `projectStatus=推进中` | count |
| `annual.highRisk` | 高风险 | `projectStatus=推进中 AND projectRiskStatus=高风险` | count |
| `expansion.availableSpace` | 可参与总空间 | `spaceInsight=已孵化 AND projectStatus=跟踪` | sum `overallSpaceMusd` |
| `expansion.total` | 总项目 | `projectStatus=跟踪` | count |
| `expansion.landed` | 已落地 | `spaceInsight=已孵化 AND projectStatus=跟踪` | count |

同一个 `where`必须同时用于统计数值与点击筛选。九个指标全部可点击，点击后真实筛选下方表格。顶部统计不得基于自身筛选结果错误重算。

---

## 14. 导航回归

企业导航：

```text
企业
├─ MOX
├─ TOB
└─ ISP&大企
   ├─ ISP
   ├─ 电力
   └─ 大企
```

点击或进入“ISP&大企”父项时，目标应为 ISP 页面，不得跳回企业首页。

---

## 15. 测试与死代码

### 15.1 过期测试

企业模块内的测试必须分类：

- KEEP：仍验证当前 Authority；
- REBUILD：测试目标仍有效，但路径、字段或结构变化；
- DELETE：只验证旧路径、旧 Schema、旧字段、fallback、兼容层或已删除死代码。

必须删除或重建的典型测试：

- 断言 Contract 位于 `src/enterprise`；
- 断言旧 `mox-field-schema.js`仍为 Authority；
- 断言旧字段或旧 label 存在；
- 断言新旧字段双写、fallback或legacy alias；
- 只测试已经删除代码的测试；
- 复制生产配置后测试复制品的伪测试。

### 15.2 死代码

本轮允许清理企业模块及其直接依赖中的死代码：

- 旧 `src/enterprise` Contract配置；
- 旧 `src/config` MOX重复Schema；
- 已无引用的旧字段映射、Projection、helper、API分支和测试；
- 旧进展、旧客户数据获取、旧字段兼容路径。

不得扩大到其他业务域。删除前必须检查 import/reference，删除后必须运行全量测试和 build。

---

## 16. Contract Validator

至少验证：

1. 41个 key 唯一；
2. order 1—41连续；
3. Section 只有客户信息、业务格局、作战情况；
4. source=excel字段具备真实Excel Authority；
5. 客户ID可为 requirement来源；
6. 两组重名字段使用不同 key/API/DB列；
7. API/DB映射完整唯一；
8. select字段有 option set；
9. 单位 label 使用中文括号；
10. 客户类别枚举为 `空值/核心NA/战略NA`，新增和编辑均可选；
11. 作战进展挂接有效特殊 editor；
12. 旧字段不在 Contract；
13. 表格、新增、编辑无 Contract 外字段；
14. `src/enterprise`不再存在活动 Contract Authority；
15. 旧 Schema无活动引用；
16. V34已注册并产出最终Schema。

---

## 17. 完成门槛

MOX 只有同时满足以下条件才可进入独立审查：

- Contract 已迁移到 `src/config/enterprise`；
- 只有一份活动 Field Contract 和 Metric Contract；
- 41字段、顺序、三个 Section正确；
- 表格、新增、编辑共用同一 Contract；
- 客户数据加载错误修复；
- 客户类别可按确认枚举选择；
- 作战进展复用 TOB 有效特殊实现；
- 旧字段、旧配置、企业模块死代码和过期测试完成收敛；
- V34、`database.js`、`_migrations`、新库与升级库一致；
- 九个统计和点击筛选正确；
- 相关测试、全量测试、build及已有lint/typecheck通过。
