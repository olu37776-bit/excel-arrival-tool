# 企业作战地图：共享契约架构与模块推广规范 V2

**状态：FINAL ARCHITECTURE AUTHORITY**  
**文档分支：`enterprise-battle-map-authority`**  
**本地实施分支：`feature/enterprise-battle-map`**  
**适用范围：企业首页、MOX、TOB、ISP、电力、大企**  
**取代文档：`enterprise-contract-architecture-v1.md`**  
**推广前置门禁：MOX 页面、Contract、API、数据库、统计、筛选和用户人工页面验收全部通过**

---

## 1. 正式架构决策

企业板块统一采用：

> **共享契约内核 + 每个模块独立 Field Contract + 每个模块独立 Metric Contract + 每个页面独立 Heatmap Contract + 各层 Adapter/Projection 串联。**

目标不是把所有模块字段合并成一个超级 Schema，而是统一机制、保持模块业务边界：

```text
共享 FieldContract / Projection / Validator
├─ MOX Field Contract
├─ TOB Field Contract
├─ ISP Field Contract
├─ Power Field Contract
└─ Large Enterprise Field Contract

共享 Metric Engine
├─ MOX Metric Contract
├─ TOB Metric Contract
├─ ISP Metric Contract
├─ Power Metric Contract
└─ Large Enterprise Metric Contract

共享 Heatmap Engine / HeatmapChart
├─ Enterprise Home Heatmap Contract
├─ MOX Heatmap Contract
├─ TOB Heatmap Contract
├─ ISP Heatmap Contract
├─ Power Heatmap Contract
└─ Large Enterprise Heatmap Contract
```

该架构解决：

- 表格、新增、编辑分别维护字段造成漂移；
- UI、API、`database.js`、SQLite 列名和语义不一致；
- 统计数字与点击筛选条件不一致；
- Heatmap 显示口径、Tooltip 和点击行为散落在页面；
- 旧 Schema、旧 config、旧字段继续参与运行；
- MOX 专属字段被错误复制到其他模块；
- 本地 Agent 根据旧代码自行扩充需求。

---

## 2. Authority 顺序

任何模块实施与审查均按以下顺序：

1. 当前模块 Canonical Authority 文档；
2. 本地“企业作战地图基表”的对应 Sheet；
3. 用户后续明确修正规则；
4. 当前代码、API、`database.js`、SQLite；
5. 历史文档、旧 Schema、旧配置。

规则：

- Excel 是字段原始需求来源；
- Canonical Authority 定义最终目标字段、规范化显示、分组、行为和已确认业务规则；
- 当前代码和数据库只代表现状，不能反向创造目标字段；
- 未列入最终字段集合、且没有用户明确追加 Authority 的旧业务字段必须删除；
- 不保留长期 legacy alias、fallback、双读、双写或旧配置 re-export；
- 同义旧字段只允许在一次性 Migration 中迁移数据，迁移结束后旧字段退出生产运行链。

---

## 3. 代码组织

不要使用 `src/features`，也不要继续把企业领域 Contract 放入通用 `src/config`。

推荐结构：

```text
src/enterprise/
├─ contracts/
│  ├─ field-contract.js
│  ├─ field-projections.js
│  ├─ contract-validator.js
│  ├─ metric-contract.js
│  ├─ metric-engine.js
│  ├─ heatmap-contract.js
│  ├─ heatmap-engine.js
│  ├─ editor-registry.js
│  ├─ formatter-registry.js
│  └─ option-sets.js
├─ home/contracts/
│  ├─ enterprise-home-metric-contract.js
│  └─ enterprise-home-heatmap-contract.js
├─ mox/contracts/
│  ├─ mox-field-contract.js
│  ├─ mox-metric-contract.js
│  └─ mox-heatmap-contract.js
├─ tob/contracts/
│  ├─ tob-field-contract.js
│  ├─ tob-metric-contract.js
│  └─ tob-heatmap-contract.js
├─ isp/contracts/
│  ├─ isp-field-contract.js
│  ├─ isp-metric-contract.js
│  └─ isp-heatmap-contract.js
├─ power/contracts/
│  ├─ power-field-contract.js
│  ├─ power-metric-contract.js
│  └─ power-heatmap-contract.js
└─ large-enterprise/contracts/
   ├─ large-enterprise-field-contract.js
   ├─ large-enterprise-metric-contract.js
   └─ large-enterprise-heatmap-contract.js
```

物理文件可根据现有项目结构做小幅调整，但必须满足：

- 一个模块只能有一份活动 Field Authority；
- 一个模块只能有一份活动 Metric Authority；
- 一个页面只能有一份活动 Heatmap Authority；
- `src/config` 不得继续保留活动企业字段、指标或 Heatmap Schema；
- 旧文件不得通过 re-export、fallback 或双轨方式继续运行；
- 共享层只能提供类型、投影、校验、注册表和引擎，不包含任何模块专属字段。

---

## 4. Field Contract 逻辑格式

每个字段至少表达：

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

约束：

- Contract 是静态普通数据，不放入 Pinia 做深度响应式；
- Contract 不直接保存 Vue 组件实例；特殊编辑器通过 `editorId` 从 registry 解析；
- UI、API、数据库可物理分层，但必须通过相同 canonical `key` 串联；
- Contract 只描述最终态，不承载 Migration 过程或旧字段兼容逻辑；
- API/数据库映射如拆分为 Persistence Map，Validator 必须验证每个 canonical key 的映射完整性和唯一性。

---

## 5. 新增与编辑的 Section 是同级区块

Field Contract 使用 `section`，不是“前后依赖流程”。新增与编辑中的分类是同级并列区块，具体 UI 形态应复用项目现有成熟样式，例如同级 Tab、同级分栏或同级区块标题。

### 5.1 MOX

MOX 新增与编辑有四个同级 Section：

```text
客户信息 ｜ 无线格局 ｜ 微波格局 ｜ 作战情况
```

它们不是：

```text
客户信息 → 无线格局 → 微波格局 → 作战情况
```

`作战进展`属于“作战情况”，但固定在该 Section 的最后，并继续使用经验证的特殊进展编辑器。

### 5.2 TOB、ISP、电力、大企

后续四个模块统一使用三个同级 Section：

```text
客户信息 ｜ 业务格局 ｜ 作战情况
```

规则：

- 所有模块复用相同的新增/编辑弹窗外壳、Section 样式、按钮、间距和校验呈现；
- 不同模块仅由各自 Field Contract 提供 Section 内字段、顺序、控件、枚举和权限；
- 不把 TOB 的业务格局继续拆成“存量与份额”“建网与交付”等顶级 Section；这些可以作为字段内部语义说明，但 UI 顶级 Section 统一叫“业务格局”；
- 表格不显示 Section 标题，但按照模块 Contract 的全局 `order` 展开；
- 新增与编辑不得再维护独立完整字段数组。

---

## 6. Table/Create/Edit Projection

```text
Module Field Contract
├─ Table Projection
├─ Create Projection
└─ Edit Projection
```

要求：

- 表格按 `ui.table.visible + order` 派生；
- 新增按 `ui.create.visible + section + order` 派生；
- 编辑按 `ui.edit.visible + section + order` 派生；
- label、单位、控件、枚举、格式化和编辑权限全部来自 Contract；
- 组件可以保留布局逻辑和特殊控件插槽，但不得再次定义完整业务字段 Authority；
- 每个页面的目标外业务字段数量必须为 0；
- 主键、操作列和必要系统列单独管理，不计入业务字段总数。

---

## 7. 客户关系统一规则

所有模块最终通过 `customer_id` 关联客户主数据。

共同规则：

- 保留当前地区部、代表处等已有联动；
- 新增时最终定位唯一客户并自动取得 `customer_id`；
- `customer_id` 不允许手工输入；
- 同名客户不得直接取第一条；
- 编辑时当前模块所展示的客户信息全部只读；
- 编辑业务字段不得改变 `customer_id`；
- API 必须验证 `customer_id` 对应真实客户；
- 模块业务表目标态只保存客户外键，不重复维护客户主数据字段；
- 各模块展示哪些客户属性以各自 Authority 为准，不强制完全同构。

---

## 8. Metric Contract 与点击筛选

每个业务子页面顶部统一为三个大模块：

1. 空间洞察；
2. 当年项目；
3. 空间拓展。

每个大模块内部包含多个指标，不得把 9 个指标拆成 9 张顶级卡片。

Metric Contract 至少包含：

```js
{
  key,
  group,
  label,
  unit,
  where,
  aggregate
}
```

同一份 `where` 同时用于：

- 统计值计算；
- 点击指标后筛选下方表格。

统一 9 项规则：

| metricKey | 显示 | 条件 | 聚合 |
|---|---|---|---|
| `insight.incubated` | 已孵化 | 空间洞察=已孵化 | count |
| `insight.incubating` | 孵化中 | 空间洞察=孵化中 | count |
| `annual.total` | 总项目数 | 项目状态 IN（已签单，推进中） | count |
| `annual.signed` | 已签单 | 项目状态=已签单 | count |
| `annual.inProgress` | 推进中 | 项目状态=推进中 | count |
| `annual.highRisk` | 高风险 | 项目状态=推进中 AND 项目风险状态=高风险 | count |
| `expansion.availableSpace` | 可参与总空间 | 空间洞察=已孵化 AND 项目状态=跟踪 | sum 整体空间（M$） |
| `expansion.total` | 总项目 | 项目状态=跟踪 | count |
| `expansion.landed` | 已落地 | 空间洞察=已孵化 AND 项目状态=跟踪 | count |

门禁：

- “当年项目”当前不额外增加年份过滤；
- `annual.total` 与 `expansion.total` 必须使用不同 key 和条件；
- 高风险是推进中的子集；
- 9 个指标全部可点击；
- 点击只改变下方表格，不得让顶部统计基于过滤结果错误重算；
- 当前激活指标具有清晰状态；
- 统计卡片样式参考现有“骨干”页面，标题和指标文字居中。

---

## 9. Heatmap Contract

每个业务子页面和企业首页都必须有 Heatmap，但共享组件与页面规则必须解耦。

Heatmap Contract 至少表达：

```js
{
  key,
  module,
  title,
  source,
  dimensions: {
    x,
    y,
    geo
  },
  value: {
    field,
    aggregate,
    unit
  },
  tooltip: {
    fields,
    formatterId
  },
  interaction: {
    clickAction,
    filterWhere,
    navigationTarget
  },
  emptyState
}
```

要求：

- ECharts 初始化、resize、dispose、空状态和基础 Tooltip 由共享 `HeatmapChart` / Heatmap Engine 负责；
- 模块 Contract 只定义数据维度、聚合值、Tooltip 字段和交互规则；
- 不得在五个页面复制五套 ECharts 生命周期代码；
- 不把 ECharts 实例放入 Pinia；
- Heatmap Contract 是静态配置，不做深度响应式；
- 业务规则未冻结时只允许保留容器与明确空状态，不得生成随机数据或自行猜测维度；
- 子页面 Heatmap 如未来要求点击筛选表格，必须通过 Contract 的同一 `filterWhere` 产生表格条件；
- 企业首页没有明细表格，Heatmap 点击行为必须单独定义为导航、钻取或无动作，不得照搬子页面表格筛选。

---

## 10. 页面统一结构

### 10.1 业务子页面

MOX、TOB、ISP、电力、大企统一骨架：

```text
模块专项
→ 三个并列统计大模块
→ Heatmap
→ 表格工具栏 / 新增
→ 数据表格 / 编辑
```

要求：

- 专项模块优先复用现有视觉结构；
- 三个统计大模块使用“骨干”页面成熟样式；
- 标题和指标文字居中；
- Heatmap 使用共享组件和当前模块 Heatmap Contract；
- 表格、新增、编辑只消费当前模块 Field Contract；
- 页面骨架可共享，但不得把一个模块字段复制进另一个模块。

### 10.2 企业首页

点击一级“企业”直接进入企业首页，不存在独立“总览”子菜单。

企业首页结构：

```text
企业专项
→ MOX / TOB / ISP&大企 三个并列模块
→ 空间拓展
→ 企业首页 Heatmap
```

企业专项定义文案：

> 聚焦四大客户群，加速方案补齐，形成PtP+PtMP整体解决方案优势，贡献1.2亿$

要求：

- “企业专项”样式与现有 MOX专项 / TOB专项 / ISP专项一致，只替换标题和定义；
- MOX、TOB、ISP&大企三个模块横向并列，内部显示“目标”“实时”，文字居中；
- 空间拓展位于三个模块下方，显示“可参与总空间”“总项目”“已落地”；
- 企业首页 Heatmap 位于空间拓展下方；
- 企业专项、空间拓展和 Heatmap 都不是导航项；
- 目标、实时、企业首页空间拓展和 Heatmap 的真实数据口径未冻结前，不得自行实现假规则或假数据；
- 企业首页只请求聚合/Heatmap所需数据，不加载五个模块全部明细。

---

## 11. 导航规则

正确导航：

```text
企业
├─ MOX
├─ TOB
└─ ISP&大企
   ├─ ISP
   ├─ 电力
   └─ 大企
```

规则：

- 点击“企业”进入企业首页；
- 不存在独立“总览”菜单；
- 点击或进入“ISP&大企”父项时，目标为 ISP 页面，不得链接回企业首页；
- “企业专项”“空间拓展”“Heatmap”均不是导航项。

---

## 12. 数据库与 Migration

项目数据库机制：

- `sql.js` 在 Node.js 中以 WASM 运行；
- `server.js` 调用 `database.js` 的 `init()`；
- `database.js` 负责连接、建表、JSON 初始化、Migration、CRUD、中英文字段映射和 Validation；
- 已执行版本由 `_migrations` 表记录；
- 版本化 SQL 使用 `V*.sql`。

模块重构要求：

1. 最终数据库 Schema 只保留目标业务列、`customer_id`、主键和必要技术列；
2. 同义旧字段只在一次性 Migration 中迁移数据；
3. 无目标对应的旧业务字段直接删除；
4. Migration 后不保留 fallback、双读、双写和旧字段映射；
5. 新建数据库 Schema 与旧库升级后的最终 Schema 必须一致；
6. Migration 必须注册到 `database.js` 实际执行链；
7. 只有事务全部成功后才能写入 `_migrations`；
8. 失败必须回滚；
9. 不直接修改真实数据库文件代替 Migration；
10. 删除多列时允许使用表重建方式，但必须先搬迁目标数据并重建必要索引与约束。

---

## 13. Contract Validator

共享 Validator 至少检查：

- canonical key 唯一；
- order 连续、唯一、无缺号；
- section 合法；
- 每个字段有 Excel 或 requirement Authority；
- source=excel 的字段具备 Sheet、列、Row2、Row3；
- API/DB 持久化映射完整且唯一；
- select 字段具有 option set；
- 单位 label 使用中文全角括号；
- 重名字段不得共用 key/API/DB 列；
- 特殊字段具有 editorId；
- 表格、新增、编辑不得存在 Contract 外业务字段；
- `src/config` 不得继续存在活动模块 Authority；
- 旧 Schema 不得继续参与运行；
- Metric key 唯一；
- Metric `where` 同时服务计算和点击筛选；
- Heatmap Contract key 唯一；
- Heatmap 未冻结字段必须显式标记 OPEN，不允许随机默认值；
- 企业首页 Heatmap 不得错误绑定子页面表格筛选。

Validator 只在开发/测试门禁运行，不在每次 Vue render 中重复执行。

---

## 14. 性能边界

多个模块的静态 Contract 不构成可感知性能问题。

必须遵守：

- Contract 使用普通 `const` / `Object.freeze()`；
- 不把全部 Contract 放入 Pinia 深度响应式；
- Table/Create/Edit Projection 在模块加载或组件初始化时派生一次；
- 路由进入哪个模块，只加载该模块明细；
- 企业首页使用聚合 API 和专用 Heatmap 数据，不一次加载五张完整明细；
- Heatmap 只更新数据 option，不重复创建 ECharts 实例；
- 真正需要优化的是大数据量和重复请求，不是静态 Contract 对象。

---

## 15. 推广顺序

```text
MOX Contract和页面完成
→ 自动测试
→ 独立审查
→ 用户人工页面验收
→ MOX VERIFIED / REFERENCE_IMPLEMENTATION_V1
→ 仅提炼已验证共享内核
→ TOB
→ ISP
→ 电力
→ 大企
→ 企业首页真实聚合
→ 各页面Heatmap真实规则
→ 统一清理登记的死代码和技术债
```

禁止在 MOX 尚未 VERIFIED 时一次性改造五个模块。

后续模块全面参考 MOX 的：

- Contract 对象结构；
- Projection；
- Validator；
- 新增/编辑同级 Section 外壳；
- Metric Engine 与点击筛选；
- Heatmap Engine 与生命周期；
- API/数据库 Adapter；
- Migration、测试与独立审查闭环。

不得复制 MOX 的具体字段、枚举、四 Section 结构或数据库列。

---

## 16. 每模块实施闭环

每个模块必须在同一轮完成：

```text
读取 Authority 与 Excel
→ 精确 WRITE_SCOPE
→ Field Contract
→ Metric Contract
→ Heatmap Contract（规则已冻结时）
→ UI/API/DB/Migration 实施
→ 同步测试
→ 自动验证
→ 状态文档
→ 停止
→ 新 Agent 独立审查
→ 必要 remediation
→ VERIFIED
```

不允许先改代码、下一轮再补测试。

人工页面验收由用户执行，不写入本地 Agent 自动任务。