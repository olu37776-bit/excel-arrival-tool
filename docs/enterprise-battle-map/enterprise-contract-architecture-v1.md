# 企业作战地图：共享契约架构与模块推广规范 V1

**状态：FINAL ARCHITECTURE AUTHORITY**  
**文档分支：`enterprise-battle-map-authority`**  
**本地实施分支：`feature/enterprise-battle-map`**  
**适用模块：MOX、TOB、ISP、电力、大企**  
**前置门禁：MOX Canonical Contract 必须先独立验证通过**

---

## 1. 目的

企业板块后续统一采用：

> **共享契约内核 + 每个模块独立 Field Contract + 每个模块独立 Metric Contract + 各层 Adapter/Projection 串联。**

目标是消除以下问题：

- 表格、新增、编辑分别维护字段，长期漂移；
- UI 字段名与 API、`database.js`、SQLite 列不一致；
- 统计值与点击筛选条件不一致；
- 旧 Schema、旧 config、旧字段继续参与运行；
- 一个模块的字段被错误复制到另一个模块；
- 本地 Agent 根据旧代码自行推断需求。

---

## 2. Authority 顺序

每个模块实施和审查均按以下顺序：

1. 对应模块的 Canonical Authority 文档；
2. 本地“企业作战地图基表”对应 Sheet；
3. 用户后续明确修正规则；
4. 当前代码、API、`database.js`、SQLite；
5. 历史文档、旧 Schema、旧配置。

规则：

- Excel 是字段原始需求来源；
- 模块 Authority 文档定义最终目标字段、显示规范、分组和行为；
- 当前代码和数据库只代表现状，不能反向创造目标字段；
- 旧文档与当前 Authority 冲突时直接作废；
- 未列入模块最终字段集合的旧业务字段，不因“当前存在”而保留。

---

## 3. 代码组织

不要使用 `src/features`，不要把领域契约继续堆在通用 `src/config`。

推荐结构：

```text
src/enterprise/
├─ contracts/
│  ├─ field-contract.js
│  ├─ field-projections.js
│  ├─ contract-validator.js
│  ├─ metric-contract.js
│  ├─ metric-engine.js
│  └─ option-sets.js
├─ mox/contracts/
│  ├─ mox-field-contract.js
│  └─ mox-metric-contract.js
├─ tob/contracts/
│  ├─ tob-field-contract.js
│  └─ tob-metric-contract.js
├─ isp/contracts/
│  ├─ isp-field-contract.js
│  └─ isp-metric-contract.js
├─ power/contracts/
│  ├─ power-field-contract.js
│  └─ power-metric-contract.js
└─ large-enterprise/contracts/
   ├─ large-enterprise-field-contract.js
   └─ large-enterprise-metric-contract.js
```

物理文件可按项目现状略作调整，但必须满足：

- 一个模块只能有一份活动 Field Authority；
- 一个模块只能有一份活动 Metric Authority；
- `src/config` 不得继续保留活动模块字段 Schema；
- 不保留旧文件 re-export、fallback、双轨运行；
- 共享层只提供类型、投影、校验和引擎，不包含具体模块字段。

---

## 4. Field Contract 逻辑格式

每个字段至少表达：

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

- Contract 是静态普通数据，不放入 Pinia 做深度响应式；
- 不在 Contract 中直接保存 Vue 组件实例；
- 特殊编辑器通过 `editorId` 从 registry 解析；
- UI、API、数据库可物理分层，但必须通过相同 canonical `key` 串联；
- Contract 描述最终态，不保留长期 legacy alias、fallback 或双写。

---

## 5. 三个 UI 面必须从同一 Contract 派生

```text
Module Field Contract
├─ Table Projection
├─ Create Projection
└─ Edit Projection
```

要求：

- 表格按 `table.visible + order` 派生；
- 新增按 `create.visible + group + order` 派生；
- 编辑按 `edit.visible + group + order` 派生；
- label、控件、枚举、权限均来自 Contract；
- 组件不得再次定义完整业务字段数组；
- 目标外业务字段数量必须为 0；
- 技术主键、操作列单独管理，不混入业务字段总数。

---

## 6. 客户关系统一规则

所有模块最终通过 `customer_id` 关联客户主数据。

共同规则：

- 保留当前地区部、代表处等已有联动；
- 新增时最终定位唯一客户并自动取得 `customer_id`；
- `customer_id` 不允许手工输入；
- 同名客户不得直接取第一条；
- 编辑时客户信息全部只读；
- 编辑业务字段不得改变 `customer_id`；
- API 必须验证 `customer_id` 对应真实客户；
- 模块业务表目标态只保存客户外键，不重复维护客户主数据字段；
- 各模块展示哪些客户属性，以各自 Authority 为准，不强制完全同构。

---

## 7. Metric Contract 与点击筛选

每个模块顶部统一为三个大模块：

1. 空间洞察；
2. 当年项目；
3. 空间拓展。

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

统一 9 项业务规则：

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

补充门禁：

- “当年项目”当前不额外增加年份过滤；
- `annual.total` 与 `expansion.total` 必须使用不同 key 和条件；
- 高风险是推进中的子集；
- 点击指标只改变表格结果，不得让顶部统计基于筛选结果错误重算；
- 9 个指标都必须可点击；
- 当前激活指标应有清晰状态。

---

## 8. 页面统一结构

各业务子页面沿用现有专项模块，并按以下顺序：

```text
模块专项
→ 三个并列统计大模块
→ Heatmap
→ 表格工具栏/新增
→ 数据表格/编辑
```

要求：

- 专项模块优先复用现有视觉结构；
- 三个统计模块样式参考现有“骨干”页面顶部统计区；
- 每个统计大模块内部展示多个指标，不得拆成 9 张顶级卡片；
- 标题和指标文字居中；
- Heatmap 业务规则未单独冻结前，不因字段重构顺便重写；
- 表格、新增、编辑以模块 Field Contract 为唯一业务字段来源。

---

## 9. 数据库与 Migration

项目数据库机制：

- `sql.js` 在 Node.js 中以 WASM 运行；
- `server.js` 调用 `database.js` 的 `init()`；
- `database.js` 负责连接、建表、JSON 初始化、Migration、CRUD、中英文字段映射和 Validation；
- 已执行版本由 `_migrations` 表记录；
- 版本化 SQL 使用 `V*.sql`。

模块重构要求：

1. 最终数据库 Schema 只保留目标业务列、`customer_id`、主键和必要技术列；
2. 旧字段与目标字段同义时，只在一次性 Migration 中迁移数据；
3. 完全无目标对应的旧业务字段直接删除；
4. Migration 后不保留运行时 fallback、双读、双写和旧字段映射；
5. 新建数据库 Schema 与旧库升级后的最终 Schema 必须一致；
6. Migration 必须注册到 `database.js` 实际执行链；
7. 只有事务全部成功后才能写入 `_migrations`；
8. 失败必须回滚；
9. 不直接修改真实数据库文件代替 Migration；
10. 删除多列时可使用表重建方式，但必须先搬迁目标数据并重建必要索引/约束。

---

## 10. Contract Validator

共享 Validator 至少检查：

- canonical key 唯一；
- order 连续、唯一、无缺号；
- group 合法；
- 每个业务字段有 Excel 或 requirement Authority；
- source=excel 的字段具备 Sheet、列、Row2、Row3；
- API/DB 持久化映射完整且唯一；
- select 字段具有 option set；
- 单位 label 使用中文全角括号；
- 重名业务字段不得共用 key/API/DB 列；
- 特殊字段具有对应 editor；
- 表格、新增、编辑不得存在 Contract 外业务字段；
- `src/config` 不得继续存在活动模块 Authority；
- 旧 Schema 不得继续参与运行；
- Metric key 唯一；
- Metric `where` 同时服务计算和点击筛选。

Validator 在开发/测试门禁运行，不在每次 Vue render 中重复执行。

---

## 11. 性能边界

多个模块的静态 Contract 不构成可感知性能问题。

必须遵守：

- Contract 使用普通 `const` / `Object.freeze()`；
- 不把全部 Contract 放入 Pinia 深度响应式；
- 表格/新增/编辑 Projection 在模块加载或组件初始化时派生一次；
- 路由进入哪个模块，只加载该模块明细数据；
- 企业首页未来只请求聚合结果，不一次加载五张完整明细；
- 真正需要优化的是大数据量，不是两三百个静态字段对象。

---

## 12. 推广顺序

严格按以下顺序：

```text
MOX Contract 完成
→ 自动测试
→ 独立审查
→ 用户人工验收
→ MOX VERIFIED
→ 提炼共享内核（仅提炼已验证机制）
→ TOB
→ ISP
→ 电力
→ 大企
```

禁止在 MOX 尚未 VERIFIED 时一次性重构五个模块。

推广时只复用：

- FieldContract 类型；
- Projection；
- Validator；
- Metric Engine；
- 数据库治理流程；
- 测试模式。

不得把 MOX 专属字段、枚举或分组硬套到其他模块。

---

## 13. 每模块实施闭环

每个模块必须同轮完成：

```text
读取 Authority 与 Excel
→ 精确 WRITE_SCOPE
→ Field Contract
→ Metric Contract
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

人工页面验收由用户执行，不写入本地 Agent 的自动任务。
