# 企业作战地图：TOB Canonical Authority V1

**状态：READY FOR IMPLEMENTATION**  
**文档分支：`enterprise-battle-map-authority`**  
**本地实施分支：`feature/enterprise-battle-map`**  
**适用范围：TOB 页面、Field Contract、Metric Contract、表格、新增、编辑、API、`database.js`、SQLite、Migration 与自动测试**  
**前置条件：MOX V3 契约化实现已经完成，可作为代码结构参考；本文件定义 TOB 业务内容，MOX 代码不能反向覆盖本文件。**

---

## 1. 唯一 Authority 与实施原则

TOB 的业务字段需求来自：

1. 本文件；
2. 本地“企业作战地图基表”的 TOB Sheet，用于核实精确 Sheet 名、Excel 列、Row2 分类、Row3 字段名、Data Validation 和字段说明；
3. 用户后续明确修正；
4. 当前代码、API、`database.js` 和 SQLite 仅代表现状；
5. 本地旧文档、旧 Schema 和旧字段配置不再定义需求。

原则：

- 全面参考 MOX 已完成的契约机制、Projection、Validator、Metric Engine、客户关系和数据库治理方式；
- 不复制 MOX 的具体字段、分组或枚举；
- TOB 只保留一份活动 Field Contract 和一份活动 Metric Contract；
- 表格、新增、编辑必须由同一 TOB Field Contract 派生；
- 统计值与点击筛选必须使用同一 TOB Metric Contract 条件；
- 当前代码中不属于本文件最终字段的 TOB 旧业务字段全部删除；
- 不保留长期 legacy alias、fallback、双读、双写或旧配置 re-export；
- 旧数据如需保留，只能通过一次性 Migration 搬入最终字段；
- 代码、测试、自动验证和状态文档必须同轮完成。

---

## 2. 代码结构

复用现有共享层：

```text
src/enterprise/contracts/
├─ field-contract.js
├─ field-projections.js
├─ contract-validator.js
├─ metric-engine.js
└─ option-sets.js
```

TOB 模块目标：

```text
src/enterprise/tob/contracts/
├─ tob-field-contract.js
└─ tob-metric-contract.js
```

要求：

- 不在 `src/config` 中建立或保留第二份 TOB 字段 Authority；
- 若已有旧 TOB Schema，所有调用方迁移后删除；
- 不新建一套 TOB 专用表格/表单引擎；
- 复用 MOX 已验证的 table/create/edit Projection、特殊编辑器注册、Metric Engine 和 Validator；
- 模块差异只放在 TOB Field Contract、TOB Metric Contract 和必要 Persistence Mapping 中。

---

## 3. TOB Field Contract 对象要求

每个字段必须至少表达：

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
    table: { visible, formatterId },
    create: { visible, editable, controlId },
    edit: { visible, editable, controlId }
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

Contract 是静态普通数据，不进入 Pinia 深响应式；特殊控件通过注册 ID 解析，不直接保存 Vue 组件实例。

---

## 4. TOB 最终 34 个业务字段

TOB 新增和编辑只使用三个一级区块：

1. 客户信息；
2. 业务格局；
3. 作战情况。

表格不显示分组标题，但按以下 1—34 顺序展开。

### 4.1 客户信息（1—5）

| order | canonical key | 用户可见字段 | 规则 |
|---:|---|---|---|
| 1 | `region` | 地区部 | 客户主数据关联 |
| 2 | `representativeOffice` | 代表处 | 客户主数据关联 |
| 3 | `country` | 国家 | 客户主数据关联 |
| 4 | `customerId` | 客户ID | 用户明确追加；TOB 保存 `customer_id` |
| 5 | `customerName` | 客户名称 | 客户主数据关联 |

TOB 不包含：

- 客户类别；
- 行业。

新增时复用现有地区部、代表处等联动，最终定位唯一客户并自动取得 `customer_id`；不允许手填客户ID。

编辑时以上客户信息全部只读，编辑业务字段不得改变 `customer_id`。

### 4.2 业务格局（6—21）

| order | canonical key | 用户可见字段 | 类型/要求 |
|---:|---|---|---|
| 6 | `backboneMicrowaveLinkCount` | 大网微波链路数量 | number |
| 7 | `tobInstalledMicrowaveLinkCount` | ToB微波链路数量-存量 | number |
| 8 | `tobInstalledOurShare` | ToB微波我司份额-存量 | percent |
| 9 | `tobInstalledNokiaShare` | ToB微波NOKIA份额-存量 | percent |
| 10 | `tobInstalledAdditionalVendorShare` | 以 Excel Row3 精确原文为准 | percent |
| 11 | `tobInstalledEricssonShare` | ToB微波Ericsson份额-存量 | percent |
| 12 | `tobInstalledNceShare` | ToB微波NCE份额-存量 | percent |
| 13 | `tobInstalledSiaeShare` | ToB微波SIAE份额-存量 | percent |
| 14 | `tobInstalledCeragonShare` | ToB微波Ceragon份额-存量 | percent |
| 15 | `tobNewMicrowaveShareReference` | ToB微波份额（New，供参考） | percent |
| 16 | `tobNetworkScenario` | ToB建网场景 | Excel Validation 决定控件 |
| 17 | `tenderType` | 招标类型 | Excel Validation 决定控件 |
| 18 | `solutionSelection` | 方案选择 | Excel Validation 决定控件 |
| 19 | `deliveryMode` | 交付方式 | Excel Validation 决定控件 |
| 20 | `customerVoice` | 客户声音（问题/需求） | textarea |
| 21 | `orderAmount2025Musd` | 25年订货（M$） | number |

第 10 项用户曾以 `ToB微波XX份额-存量` 描述，`XX` 只是占位。实施前必须直接读取 TOB Sheet 的实际 Row3 原文并写入：

- `label`；
- `authority.column`；
- `authority.row2Group`；
- `authority.row3Label`。

禁止将 `XX` 提交到生产页面或数据库契约。

百分比字段必须有明确存储语义。Contract 必须说明数据库保存的是 `0—1` 还是 `0—100`，UI formatter/parser 必须成对，禁止显示与存储口径漂移。

### 4.3 作战情况（22—34）

| order | canonical key | 用户可见字段 |
|---:|---|---|
| 22 | `overallSpaceTier` | 整体空间 |
| 23 | `focusProject` | 作战分类-是否重点项目 |
| 24 | `spaceInsight` | 空间洞察 |
| 25 | `projectStatus` | 项目状态 |
| 26 | `projectRiskStatus` | 项目风险状态 |
| 27 | `overallSpaceHops` | 整体空间（跳） |
| 28 | `overallSpaceMusd` | 整体空间（M$） |
| 29 | `space2026Hops` | 26年空间（跳） |
| 30 | `orderSpace2026Musd` | 26年订货空间（$M） |
| 31 | `orderedHops` | 已下单数量（跳） |
| 32 | `orderedAmountMusd` | 已下单金额（$M） |
| 33 | `frontlineContact` | 一线接口人 |
| 34 | `battleProgress` | 作战进展 |

固定规则：

- `整体空间`：肥肉 / 瘦肉 / 骨头；
- `作战分类-是否重点项目`：是 / 否；
- `空间洞察`：已孵化 / 孵化中；
- `项目状态`：已签单 / 推进中 / 跟踪；
- TOB 确认存在 `项目风险状态`；
- `作战进展`固定为最后一项，复用 MOX 已验证的特殊新增、编辑、保存和回填交互；
- `一线接口人`保留，禁止再增加“服务接口人”；
- 不增加备注。

`作战分类-是否重点项目`是一个完整字段，现有页面“重点项目”筛选必须直接使用 canonical `focusProject`，不得拆成两个字段。

---

## 5. Excel Authority

Excel 是字段原始需求来源。本地实施必须逐项读取 TOB Sheet，并给每个 source=excel 字段填写：

```js
authority: {
  source: 'excel',
  sheet: '实际精确Sheet名',
  column: '实际列字母',
  row2Group: '实际Row2分类',
  row3Label: '实际Row3原文'
}
```

`customerId`使用：

```js
authority: {
  source: 'requirement',
  sheet: null,
  column: null,
  row2Group: '客户信息',
  row3Label: '客户ID'
}
```

本文件列出的 34 项是封闭目标集合。Excel 用于核实来源，不允许本地 Agent 从旧列、旧说明或旧数据中新增第 35 个业务字段。

所有带单位的用户可见字段使用中文全角括号。Excel 原始表头可保留在 `authority.row3Label`，规范化页面名称写在 `label`。

---

## 6. 表格、新增与编辑

必须由同一 `TOB_FIELD_CONTRACT` 派生：

```text
TOB_FIELD_CONTRACT
├─ Table Projection
├─ Create Projection
└─ Edit Projection
```

要求：

- 表格严格按 1—34 排序；
- 新增和编辑使用“客户信息 / 业务格局 / 作战情况”三个分组；
- 字段集合、label、顺序、类型、枚举和权限均来自 Contract；
- 表格、新增、编辑不得保留完整独立字段数组；
- 目标外业务字段数必须为 0；
- 操作列和必要技术主键不计入 34 项；
- `battleProgress`使用共享特殊进展编辑器；
- 客户字段在编辑中全部只读。

---

## 7. API、database.js 与 SQLite

每个字段必须建立唯一链路：

```text
canonical key
→ API read/create/update
→ database.js mapping / CRUD / Validation
→ SQLite column
```

目标态：

- TOB 业务表保存 `customer_id`；
- 地区部、代表处、国家、客户名称从客户关系读取，不作为 TOB 重复业务 Authority；
- 目标持久化字段与 Contract 一一对应；
- 不属于最终 34 项的旧 TOB 业务字段从 API、`database.js` 和最终 SQLite Schema 删除；
- 同义旧字段只允许通过一次性 Migration 搬迁数据，迁移后不保留 fallback、双读或双写；
- 数据库结构变更必须使用下一个未使用的 `V*.sql`，注册到 `database.js`，并由 `_migrations`记录；
- 新建数据库与旧库升级后的最终 TOB Schema 必须一致；
- 不得直接修改真实数据库代替 Migration。

TOB 当前即使已有外键声明，也必须由 API 验证 `customer_id` 对应真实客户。全局开启 SQLite foreign key enforcement 属于独立治理范围，未经单独 Authority 不得在本轮顺手开启。

---

## 8. Metric Contract 与点击筛选

TOB 复用共享 9 个指标语义，但必须维护独立 `TOB_METRIC_CONTRACT`：

| metricKey | 显示 | where | aggregate |
|---|---|---|---|
| `insight.incubated` | 已孵化 | `spaceInsight = 已孵化` | count |
| `insight.incubating` | 孵化中 | `spaceInsight = 孵化中` | count |
| `annual.total` | 总项目数 | `projectStatus IN（已签单，推进中）` | count |
| `annual.signed` | 已签单 | `projectStatus = 已签单` | count |
| `annual.inProgress` | 推进中 | `projectStatus = 推进中` | count |
| `annual.highRisk` | 高风险 | `projectStatus = 推进中 AND projectRiskStatus = 高风险` | count |
| `expansion.availableSpace` | 可参与总空间 | `spaceInsight = 已孵化 AND projectStatus = 跟踪` | sum `overallSpaceMusd` |
| `expansion.total` | 总项目 | `projectStatus = 跟踪` | count |
| `expansion.landed` | 已落地 | `spaceInsight = 已孵化 AND projectStatus = 跟踪` | count |

规则：

- 同一 `where` 同时用于统计数值和点击后的表格筛选；
- 九个指标全部可点击；
- 点击只改变下方 TOB 表格，不使用筛选结果重新计算顶部统计；
- `annual.total` 与 `expansion.total`必须使用不同 key 和不同条件；
- 顶部只显示“空间洞察 / 当年项目 / 空间拓展”三个大模块，不能拆成九张顶级卡；
- 文字与成熟页面样式保持一致并居中。

---

## 9. 页面骨架与 Heatmap

TOB 页面顺序保持：

```text
TOB专项
→ 三个并列统计模块
→ Heatmap
→ 新增入口和数据表格
```

本阶段：

- 复用当前 TOB 专项结构；
- 复用 MOX 已验证的统计模块结构；
- Heatmap 暂不重构真实业务规则，只保证字段收敛后不回归；
- 不因契约化无理由重写整个 TOB 页面。

---

## 10. Contract Validator

至少验证：

1. 34 个 canonical key 唯一；
2. order 为 1—34，连续、无重复、无缺号；
3. group 只允许客户信息、业务格局、作战情况；
4. 每个字段具备 Excel 或 requirement Authority；
5. 第 10 项厂商字段已经解析真实 Row3 名称，不含 `XX`；
6. TOB Contract 不包含客户类别或行业；
7. 所有 select 字段具备 option set；
8. 百分比 parser/formatter 与数据库口径一致；
9. API、`database.js`、SQLite 映射完整且唯一；
10. 表格、新增、编辑不存在 Contract 外业务字段；
11. `focusProject`直接驱动现有重点项目筛选；
12. `battleProgress`挂接共享特殊编辑器；
13. 所有带单位 label 使用中文全角括号；
14. `src/config`中不存在活动 TOB 字段 Authority；
15. 旧 TOB Schema 不再被运行时引用。

Validator 只在开发/测试门禁运行，不在每次 Vue render 中重复执行。

---

## 11. 自动测试与验证

实施必须同步覆盖：

- 34 字段、三个分组和精确顺序；
- Excel Authority 完整性；
- 第 10 项真实厂商字段；
- 表格、新增、编辑真实消费同一 Contract；
- 目标外字段为 0；
- 客户数据与 `customer_id`；
- 编辑客户信息只读；
- 百分比字段读写一致；
- `focusProject`和现有重点项目筛选；
- `battleProgress`特殊交互；
- API/DB保存和回填；
- 新建库与迁移库最终 Schema 一致；
- 9 个统计值；
- 9 个点击筛选；
- Heatmap无本阶段回归；
- TOB专项和三卡布局无回归；
- 全量 Vitest、build、lint/typecheck（如已配置）。

不要求本地 Agent 做人工页面检查，用户自行验收页面效果。

---

## 12. WRITE_SCOPE 与禁止范围

本轮允许处理：

- TOB Field Contract；
- TOB Metric Contract；
- TOB 表格、新增、编辑；
- TOB 客户关联；
- TOB API、`database.js`、SQLite 与必要 Migration；
- TOB统计、点击筛选；
- TOB相关测试和状态更新。

本轮禁止：

- 修改 MOX 已验证字段和业务规则；
- 修改 ISP、电力、大企字段；
- 建设企业首页真实汇总；
- 重构 Heatmap 业务规则；
- 清理与 TOB 无关的死代码；
- 构建全企业超级 Schema；
- 保留旧 TOB 双轨兼容。

---

## 13. 完成门槛

只有以下全部满足才能声明 TOB 实施完成：

1. 34 项封闭字段集合准确；
2. 三个分组和顺序准确；
3. 第 10 项 Excel 厂商字段已写实；
4. 表格、新增、编辑使用同一 Contract；
5. 目标外业务字段为 0；
6. `customer_id`链路正确；
7. API、`database.js`和SQLite一一对应；
8. 必要 Migration 正确注册并通过测试；
9. `focusProject`筛选正确；
10. `battleProgress`特殊交互正确；
11. 9 个指标计算正确；
12. 9 个指标点击筛选正确；
13. TOB自动测试和全量测试通过；
14. build通过；
15. 无越界修改。

完成后停止，下一步只能是 TOB 独立审查。
