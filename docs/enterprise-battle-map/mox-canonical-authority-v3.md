# 企业作战地图：MOX Canonical Authority V3

**状态：FINAL TARGET AUTHORITY**  
**文档分支：`enterprise-battle-map-authority`**  
**本地实施分支：`feature/enterprise-battle-map`**  
**适用范围：MOX 字段、UI、API、`database.js`、SQLite、Migration、统计与筛选**  
**取代范围：此前所有与本文件冲突的 MOX 字段清单、Schema、Contract、WRITE_SCOPE 和 Review 结论**

---

## 1. Authority 与执行原则

本文件列出的 MOX 字段、分组、顺序、单位、统计规则和交互规则是当前最终 Authority。

规则：

1. 本文件列出的字段必须保留或建设。
2. 本文件未列出的 MOX 业务字段一律删除。
3. 当前代码、旧 Schema、旧 Contract、旧数据库存在某字段，不能作为保留理由。
4. Excel 是字段原始需求来源，用于核实 Sheet、列、Row2 分类、Row3 表头、Data Validation 与输入说明。
5. 用户明确追加/修正规则高于旧代码与旧文档，例如 `客户ID`、单位显示规范、作战进展、重点项目映射、统计规则与点击筛选规则。
6. 不保留长期 legacy alias、fallback、双读、双写或旧配置 re-export。
7. 旧字段如与目标字段语义相同，只允许在一次性 Migration 中搬迁数据；迁移完成后旧字段退出运行时代码和最终数据库 Schema。
8. 所有实施必须同步完成生产代码、测试、自动验证和文档状态更新，然后停止并接受独立审查。
9. 本地旧 MOX 字段文档、旧 Schema 与旧 Contract 不再作为 Authority；本地 Agent 每轮必须优先读取本文件并读取 Excel 核实来源。

### 1.1 目标架构

```text
MOX Field Contract
├─ Table Projection
├─ Create Form Projection
├─ Edit Form Projection
├─ API Mapping
├─ database.js Mapping
└─ SQLite Persistence

MOX Metric Contract
├─ Metric Calculation
└─ Click-to-Filter
```

MOX 只能有一份活动 Field Authority 和一份活动 Metric Authority。

---

## 2. 代码组织

不要使用 `src/features`，也不要把领域契约继续放在通用 `src/config`。

推荐：

```text
src/enterprise/contracts/
├─ field-contract.js
├─ field-projections.js
├─ contract-validator.js
├─ metric-engine.js
└─ option-sets.js

src/enterprise/mox/contracts/
├─ mox-field-contract.js
└─ mox-metric-contract.js
```

要求：

- `src/config` 中不再存在活动 MOX 字段或 Metric Authority；
- 旧 `mox-field-schema.js` 不得继续定义第二份字段集合、顺序、枚举或权限；
- 所有调用方迁移完成后删除旧活动配置；
- 不保留 fallback、re-export 或新旧双轨运行。

---

## 3. Field Contract 对象格式

每个字段至少应表达：

```js
{
  key,
  label,
  group,
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

约束：

- Contract 是静态普通数据，不放进 Pinia 做深度响应式；
- Contract 中不直接保存 Vue 组件实例；特殊组件通过 `editorId` / `formatterId` 从 registry 解析；
- 表格、新增、编辑不得分别维护完整业务字段数组；
- API/数据库映射可以物理拆到 Persistence Map，但必须使用同一 canonical `key` 串联，并由 Validator 校验完整性；
- Contract 描述最终态，不保留 legacy compatibility 层。

---

## 4. MOX 最终 41 个业务字段

### 4.1 客户信息（1—6）

| order | canonical key | 用户可见字段 | 规则 |
|---:|---|---|---|
| 1 | `region` | 地区部 | 客户主数据关联 |
| 2 | `representativeOffice` | 代表处 | 客户主数据关联 |
| 3 | `country` | 国家 | 客户主数据关联 |
| 4 | `customerId` | 客户ID | 用户追加关系字段；MOX 保存 `customer_id` |
| 5 | `customerName` | 客户名称 | 客户主数据关联 |
| 6 | `customerCategory` | 客户类别 | 客户主数据关联 |

MOX **没有行业字段**。

新增：复用当前地区部、代表处等联动，最终定位唯一客户并自动取得 `customer_id`；客户ID不可手工输入。

编辑：以上客户信息全部不可修改，编辑其他字段不得改变 `customer_id`。

目标态：MOX 业务表只保存 `customer_id`；其他客户展示信息通过客户表关联读取。

### 4.2 无线格局（7—18）

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

确认规则：

- `阶段`：孵化 / 突破 / 纵深；Excel MOX `F` 列正式字段为“阶段”。
- `优先级`：A / B / C / D。
- 无线 `26年机会点`：Y（有企业无线项目）/ N（无企业无线项目）。

### 4.3 微波格局（19—28）

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

确认规则：

- 微波 `26年机会点`：Y（有微波项目）/ N（无微波项目）。
- `wirelessSpectrumStatus` ≠ `microwaveSpectrumStatus`。
- `wirelessOpportunity2026` ≠ `microwaveOpportunity2026`。
- 两组重名字段必须使用不同 canonical key、API 字段、`database.js` 映射和 SQLite 列。

### 4.4 作战情况（29—41）

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

- `整体空间`：肥肉 / 瘦肉 / 骨头。
- `作战分类-是否重点项目`：是 / 否。
- `空间洞察`：已孵化 / 孵化中。
- `项目状态`：已签单 / 推进中 / 跟踪。
- `项目风险状态`：用于标识高风险。
- `作战分类-是否重点项目` 是一个完整业务字段，不得拆成“作战分类”和“重点项目”两个字段。
- 页面现有“重点项目”筛选必须直接使用 canonical `focusProject`，不得创建第二个重点项目字段。
- `作战进展`属于“作战情况”，固定放最后；用户可见名称由旧“最新进展”统一为“作战进展”，但必须继承原有特殊新增、编辑、保存和回填交互，不能退化为普通文本框。

---

## 5. 单位显示规范

所有用户可见的带单位字段统一使用中文全角括号：

```text
字段名（单位）
```

正式示例：

- 无线空间（MUSD）
- 26年空间（基站数量）
- 27-28年机会空间（基站数据量）
- 基站单价（xxx美金/站）
- 友商空间（跳数）
- 26年基站回传空间（微波跳数）
- 26年视频回传空间（微波跳数）
- 整体空间（跳）
- 整体空间（M$）
- 26年空间（跳）
- 26年订货空间（$M）
- 已下单数量（跳）
- 已下单金额（$M）

显示名称规范不得仅因括号变化强迫正确 API/数据库列改名；canonical 技术映射必须稳定且唯一。

---

## 6. 明确删除的字段

以下字段不属于 MOX 最终目标：

- `dpm`
- `remark`
- `service_interface`
- `entered_amount`
- `space_26`
- `produce_owner`
- `industry`
- `latest_progress`
- `phase_wireless`
- 任何不属于本文件 41 项、且不是明确必要技术列的 MOX 旧业务字段

删除范围：

1. MOX 表格；
2. MOX 新增弹窗；
3. MOX 编辑弹窗；
4. API 活动请求/响应契约；
5. `database.js` MOX CRUD、映射和 Validation；
6. MOX 最终 SQLite Schema；
7. 活动 Field Schema / Contract / 配置；
8. 测试中的旧目标断言。

禁止保留 fallback、双读、双写、旧字段 re-export 或活动 legacy compatibility。

一次性迁移：

- `entered_amount` 若历史数据确认对应 `orderedAmountMusd`，仅在 Migration 中一次性迁移后删除 `entered_amount`；
- `latest_progress` 若历史数据对应 `battleProgress`，仅在 Migration 中一次性迁移后删除 `latest_progress`；
- 其他无目标对应字段直接舍弃；
- Migration 完成后运行时代码不得继续认识旧字段。

必要技术列白名单默认只包括：MOX 记录主键、`customer_id`、以及经本次设计明确批准的系统列。

---

## 7. 数据库最终态与 V34 修复

### 7.1 当前已知阻塞

- MOX 最终数据库列存在缺失；
- V34 SQL 曾存在语法错误；
- V34 未正确注册到 `database.js` 的 Migration 执行链；
- `database.js` 中仍存在旧字段活动映射。

### 7.2 V34 必须完成

```text
V34.sql
→ database.js migration registry / ordered execution list
→ 成功执行
→ _migrations 记录 V34
```

要求：

1. 修复 V34 SQL 语法；
2. 将 V34 注册到 `database.js` 实际 Migration 清单/加载器；
3. Migration 在事务中执行；
4. 只有全部成功后才写入 `_migrations`；
5. 失败必须回滚，不能留下半迁移状态；
6. 新建数据库初始化 Schema 与旧数据库执行 V34 后的 Schema 必须一致；
7. 不得直接修改真实数据库文件代替 Migration；
8. 如删除多列需要重建 MOX 表：创建最终结构新表 → 只复制目标字段/允许迁移数据 → 替换旧表 → 重建必要索引/约束；
9. V34 后最终 MOX 表不得包含本文件明确删除的旧业务列；
10. 重复启动不得重复执行 V34，由 `_migrations` 保证幂等。

---

## 8. 表格、新增与编辑唯一来源

必须由同一 `MOX_FIELD_CONTRACT` 派生：

```text
MOX_FIELD_CONTRACT
├─ table projection
├─ create projection
└─ edit projection
```

要求：

- 表格按 Contract `order` 展示；
- 新增/编辑按 `group + order` 展示；
- 新增/编辑分组固定为：客户信息、无线格局、微波格局、作战情况；
- 表格不显示分组标题，但顺序按 1—41 展开；
- 作战进展在作战情况最后；
- 不允许第二份完整业务字段数组；
- 目标外业务字段数量必须为 0。

---

## 9. 客户数据链路

已确认目标：

- 复用现有地区部、代表处等选择与联动；
- 点击新增不得再出现“获取客户数据失败”；
- 最终选择必须对应唯一客户；
- 自动保存 `customer_id`；
- `customer_id`不可手填；
- 同名客户不得直接取第一条；
- 编辑时客户信息全部只读；
- 编辑其他字段不得改变 `customer_id`；
- API 必须验证 `customer_id` 对应真实客户记录。

---

## 10. Metric Contract 与点击筛选

MOX 顶部只有三个并列大模块：空间洞察、当年项目、空间拓展。

每个指标必须定义：`metricKey`、`group`、`label`、`unit`、`where`、`aggregate`。

**同一份 `where` 同时用于统计计算和点击后的表格筛选。**

### 10.1 空间洞察

| metricKey | 显示 | where | aggregate |
|---|---|---|---|
| `insight.incubated` | 已孵化 | 空间洞察 = 已孵化 | count |
| `insight.incubating` | 孵化中 | 空间洞察 = 孵化中 | count |

### 10.2 当年项目

当前不增加年份过滤。

| metricKey | 显示 | where | aggregate |
|---|---|---|---|
| `annual.total` | 总项目数 | 项目状态 IN（已签单，推进中） | count |
| `annual.signed` | 已签单 | 项目状态 = 已签单 | count |
| `annual.inProgress` | 推进中 | 项目状态 = 推进中 | count |
| `annual.highRisk` | 高风险 | 项目状态 = 推进中 AND 项目风险状态 = 高风险 | count |

### 10.3 空间拓展

| metricKey | 显示 | where | aggregate |
|---|---|---|---|
| `expansion.availableSpace` | 可参与总空间 | 空间洞察 = 已孵化 AND 项目状态 = 跟踪 | sum `overallSpaceMusd` |
| `expansion.total` | 总项目 | 项目状态 = 跟踪 | count |
| `expansion.landed` | 已落地 | 空间洞察 = 已孵化 AND 项目状态 = 跟踪 | count |

门禁：

- 九个指标全部可点击；
- 点击后下方 MOX 表格使用同一 `where` 筛选；
- `annual.total` 与 `expansion.total` 必须使用不同 key 和不同条件；
- 点击指标只改变表格，不允许顶部统计基于筛选结果错误重算；
- 现有“重点项目”筛选必须直接使用 canonical `focusProject`。

---

## 11. ISP&大企导航修复

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

- 点击一级“企业”进入企业首页；
- 点击或进入“ISP&大企”父项时，目标必须是 **ISP 页面**，不得链接回企业首页；
- 不得重新增加独立“总览”菜单。

---

## 12. Contract Validator 门禁

Validator 至少检查：

1. 41 个 canonical key 唯一；
2. `order` 1—41 连续、无重复、无缺号；
3. 分组仅允许客户信息、无线格局、微波格局、作战情况；
4. 每个字段具备有效 Authority；
5. source=excel 字段具备真实 Sheet、列、Row2、Row3；
6. `customerId`允许 requirement 来源；
7. 两个频谱状态的 key/API/DB 列不同；
8. 两个 26 年机会点的 key/API/DB 列不同；
9. API/DB 持久化映射完整且唯一；
10. 所有 select 字段具有 option set；
11. 所有带单位 label 使用中文全角括号；
12. `battleProgress`配置特殊 editor；
13. 明确删除字段不得进入最终 Contract；
14. 表格、新增、编辑不得存在 Contract 外业务字段；
15. `src/config`不得继续存在活动 MOX Authority；
16. 旧 `mox-field-schema.js`不得继续参与运行；
17. V34 已注册并可成功完成迁移；
18. V34 后最终 SQLite Schema 不含废弃字段。

Validator 在开发/测试门禁运行，不在每次 Vue render 中执行。

---

## 13. 自动测试与验证

实施必须同步覆盖：

- 41 字段和精确顺序；
- 四个分组；
- 单位规范；
- 表格/新增/编辑真实消费同一 Contract；
- 目标外业务字段为 0；
- 客户数据请求成功；
- `customer_id`保存、查询、编辑不变；
- 重名字段不串；
- `focusProject`与现有重点项目筛选一致；
- `battleProgress`特殊交互；
- V34 SQL语法；
- V34 在 `database.js` 注册；
- `_migrations`登记与重复启动幂等；
- 新库和升级库最终 Schema 一致；
- 废弃列删除；
- 九个 Metric 计算；
- 九个点击筛选；
- ISP&大企进入 ISP；
- 全量 Vitest；
- build；
- lint/typecheck（如配置）。

人工页面验收由用户完成，不写入本地 Agent 自动任务。

---

## 14. 旧文档处理

本文件成为当前 MOX 唯一设计 Authority。

本地既有 MOX 字段、Schema、Contract 文档：

- 不再作为实施或审查 Authority；
- 不需要逐份修补；
- 与本文件冲突时直接判为 superseded；
- 历史 Review 可保留为证据，但不得控制当前实现；
- `enterprise-status.md`只需记录本文件路径、当前实施状态和 Review Gate。

后续本地 Agent 每次开始 MOX 实施或审查，必须首先读取本文件，并直接读取本地 Excel 核实字段来源。