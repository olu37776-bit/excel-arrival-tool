# 企业作战地图：契约驱动架构 V3

**状态：CURRENT SHARED ARCHITECTURE AUTHORITY**  
**文档分支：`enterprise-battle-map-authority`**  
**本地实施分支：`feature/enterprise-battle-map`**  
**取代：`enterprise-contract-architecture-v1.md`、`enterprise-contract-architecture-v2.md` 中与本文件冲突的内容**

---

## 1. 目标

企业板块使用“共享契约机制 + 模块独立业务契约 + 分层 Adapter”的方式建设。

目标不是建立一份覆盖全部模块的超级 Schema，也不是让每个页面各自硬编码表格、新增、编辑、API 和数据库字段。

目标结构：

```text
模块 Field Contract
├─ Table Projection
├─ Create Projection
├─ Edit Projection
├─ API Mapping
├─ database.js Mapping
└─ SQLite Persistence

模块 Metric Contract
├─ Metric Calculation
└─ Click-to-Filter
```

长期原则：

1. 每个模块只有一份活动 Field Contract；
2. 每个模块只有一份活动 Metric Contract；
3. 表格、新增、编辑均从 Field Contract 派生；
4. 统计值与点击筛选使用 Metric Contract 中同一份条件；
5. canonical key 串联 UI、API、`database.js` 与 SQLite；
6. Excel 是字段原始需求来源，模块 Canonical Authority 是经用户确认后的目标定义；
7. Contract 描述最终态，不保留长期旧字段兼容；
8. 数据库结构变更走 `V*.sql + _migrations + database.js`；
9. 代码、测试、自动验证和状态同步必须同轮完成；
10. 实施完成后由新 Agent 独立审查，人工页面验收由用户执行。

---

## 2. 当前 Authority 顺序

本地 Agent 必须按以下顺序判断：

1. GitHub `enterprise-battle-map-authority` 分支中的当前模块 Canonical Authority；
2. 本地“企业作战地图基表”对应 Sheet，用于核实列、Row2、Row3、Data Validation 和输入说明；
3. 用户后续明确修正；
4. 当前代码、API、`database.js`、SQLite，仅用于判断现状差距；
5. 本地旧文档、旧 Schema、旧 config，仅作历史参考。

本地旧文档不得反向创造需求，也不得与远程 Authority 折中。

字段规则：

- Canonical Authority 中存在：必须保留或建设；
- Authority 中不存在：从目标 UI、活动 API 契约、`database.js` 活动映射和最终数据库 Schema 删除；
- Excel 中存在但未进入当前 Canonical Authority：不得由本地 Agent自行扩展，应记录冲突并停止该字段实施；
- 用户明确追加字段可不具备 Excel 列，例如 `customerId`；
- 必要技术主键不计入业务字段数量。

---

## 3. 代码目录

领域契约属于配置，不使用 `src/enterprise` 或 `src/features` 作为契约目录。

当前标准目录：

```text
src/config/enterprise/
├─ field-contract.js
├─ field-projections.js
├─ contract-validator.js
├─ metric-engine.js
├─ option-sets.js
├─ mox-field-contract.js
├─ mox-metric-contract.js
├─ tob-field-contract.js
├─ tob-metric-contract.js
├─ isp-field-contract.js
├─ isp-metric-contract.js
├─ power-field-contract.js
├─ power-metric-contract.js
├─ large-enterprise-field-contract.js
└─ large-enterprise-metric-contract.js
```

允许根据当前项目模块系统做轻微文件拆分，但必须全部位于 `src/config` 之下，并满足：

- `src/enterprise` 不再承载 Field/Metric Contract Authority；
- `src/config` 中不得同时存在旧 Schema 和新 Contract 两套活动定义；
- 旧 `mox-field-schema.js` 等文件迁移完成后删除；
- 不保留 re-export、fallback 或双轨兼容；
- 页面组件、API 和数据库代码保持在项目现有职责目录，不因 Contract 迁移被全部移动到 `src/config`。

---

## 4. Field Contract

每个字段的逻辑契约至少包含：

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

- Contract 为静态普通数据，不放入 Pinia 做深度响应式；
- Contract 中不直接保存 Vue 组件实例；
- 特殊控件通过 `editorId`、`formatterId` 和 registry 解析；
- API/DB 映射可物理拆出 Persistence Map，但必须用相同 canonical key 关联；
- Validator 必须发现缺失、重复和冲突映射；
- Contract 中不保留 `legacyAliases`、fallback、双读或双写。

---

## 5. 表单 Section

### 5.1 MOX

MOX 新增和编辑只有三个同级顶层 Section：

```text
客户信息 ｜ 业务格局 ｜ 作战情况
```

`业务格局`中按 Field Contract 顺序连续包含无线与微波业务字段。可以在 Contract 中保留 `wireless` / `microwave` 元数据用于区分重名 key，但不得再渲染成两个顶层 Section。

### 5.2 TOB、ISP、电力、大企

新增与编辑同样使用：

```text
客户信息 ｜ 业务格局 ｜ 作战情况
```

三个 Section 为同级区块，不是先后流程。具体字段由当前模块 Contract 决定。

### 5.3 投影规则

```text
Field Contract
├─ table projection：按 order 展开，不渲染 Section 标题
├─ create projection：按 section + order 渲染
└─ edit projection：按 section + order 渲染
```

组件不得另外维护完整字段数组或另外排序。

---

## 6. 客户关系

业务记录使用 `customer_id` 关联客户主数据。

通用规则：

- 复用现有地区部、代表处等联动；
- 最终选择必须定位唯一客户；
- `customer_id`自动取得，不可手填；
- 同名客户不得取第一条；
- API 必须验证客户存在；
- 编辑其他业务字段不得改变 `customer_id`。

具体客户属性是否允许编辑，由模块 Authority 明确。可编辑的客户主数据字段必须写回客户表，不得在业务表新增重复列。

---

## 7. Metric Contract

每个指标至少包含：

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

同一个 `where` 同时用于：

1. 统计值计算；
2. 点击指标后筛选下方表格。

禁止分别维护 `calculateCondition` 与 `filterCondition` 两套业务规则。

Metric Engine 应提供：

- `matchesWhere(record, where)`；
- `calculateMetric(records, metric)`；
- `filterByMetric(records, metric)`；
- active metric 状态管理；
- 清除或切换指标筛选。

点击指标只改变表格结果，不应让顶部统计基于自身筛选结果错误重算。

---

## 8. 数据库治理

当前数据库由 `sql.js` 在 Node.js 中以 WASM 方式运行，`server.js`启动调用 `database.js` 的初始化入口。

`database.js`负责：

- 连接；
- 建表；
- JSON 初始化；
- Migration；
- CRUD；
- 中英文字段映射；
- 数据验证。

数据库版本由 `_migrations`表记录，不使用 `PRAGMA user_version`。

任何 Schema 变更必须同步：

1. 新建数据库 Schema；
2. `V*.sql`旧库 Migration；
3. `database.js` Migration 注册和顺序；
4. `_migrations`成功登记；
5. CRUD；
6. 字段映射；
7. Validation；
8. API；
9. Contract runtime mapping；
10. Migration测试。

Migration 必须在事务中完成；只有整体成功才登记版本，失败必须回滚。

旧字段处理：

- 与目标字段同义且有数据：一次性迁移数据后删除旧字段；
- 无目标对应：直接舍弃；
- 最终运行时代码和数据库不保留旧字段 fallback、双读或双写。

---

## 9. 测试治理

测试必须以当前 GitHub Authority 和当前代码为准。

企业模块测试分类：

- `KEEP`：仍验证当前有效行为；
- `REBUILD`：测试目标有效，但结构、字段或路径已经变化；
- `DELETE`：仅验证已被取代的目录、字段、Schema、兼容层或旧需求。

必须删除或重建：

- 断言 `src/enterprise` 为 Contract 路径的旧测试；
- 断言旧 Schema 与新 Contract 并存的测试；
- 断言旧字段、旧 label、fallback、双写或 legacy alias 的测试；
- 仅测试已删除死代码的测试；
- 复制生产配置后测试复制品的伪测试。

测试不得只检查字符串存在；必须验证真实 projection、API/DB mapping、CRUD、Migration、Metric 与筛选行为。

---

## 10. 企业模块死代码清理

死代码清理当前仅限企业模块及其直接依赖：

- 企业 Field/Metric Contract；
- 企业 Projection、Validator、Metric Engine；
- 企业页面和表单旧配置；
- 企业 API 与 `database.js`旧映射；
- 企业测试；
- 旧 `src/enterprise` Contract 目录；
- `src/config` 中重复旧 Schema。

清理要求：

1. 先建立 import/reference 清单；
2. 仅删除无活动引用或已被当前 Contract 完全替代的代码；
3. 不扩大到其他业务域；
4. 删除后运行全量测试和 build；
5. 被删除能力如仍是当前需求，必须先由新实现覆盖；
6. Phase 1其他已登记、与企业模块无关的死代码继续延后。

---

## 11. 页面结构

业务子页面统一：

```text
模块专项
→ 三个并列统计大模块
→ 当前模块 Heatmap
→ 新增 / 表格 / 编辑
```

三个统计大模块为：

- 空间洞察；
- 当年项目；
- 空间拓展。

每个大模块内部显示自己的指标，不得一个指标一张顶级卡。

企业首页当前另有独立 Authority；首页 Heatmap 当前保持延后，不在子模块实施中处理。

---

## 12. 推广流程

MOX 必须先达到：

```text
VERIFIED
REFERENCE_IMPLEMENTATION_V1
```

然后其他模块复用：

- Contract 类型；
- `src/config/enterprise`目录结构；
- Projection；
- Validator；
- Metric Engine；
- 客户关系；
- Migration规范；
- 测试模板。

不得复制 MOX 具体字段。

推荐顺序：

```text
MOX完成
→ 自动验证
→ 独立审查
→ 用户人工验收
→ 发布MOX Reference Implementation
→ TOB
→ ISP
→ 电力
→ 大企
→ 企业首页最终聚合
→ 企业模块统一技术债清理
```
