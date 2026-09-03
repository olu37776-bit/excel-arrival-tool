# 企业作战地图：TOB Canonical Authority V1

**状态：READY AFTER MOX VERIFIED**  
**文档分支：`enterprise-battle-map-authority`**  
**本地实施分支：`feature/enterprise-battle-map`**  
**适用范围：TOB 字段、表格、新增、编辑、API、`database.js`、SQLite、Migration、统计与点击筛选**  
**前置门禁：MOX Canonical Contract 独立验证通过并完成人工验收**

---

## 1. 实施原则

TOB 复用 MOX 已验证的契约机制，不复制 MOX 字段。

必须复用：

- 共享 `FieldContract` 类型；
- table/create/edit Projection；
- Contract Validator；
- Metric Contract 与 Metric Engine；
- 客户 `customer_id` 关系模式；
- `V*.sql + _migrations + database.js` 数据库治理；
- 代码、测试、自动验证、文档、独立审查闭环。

不得：

- 从旧 TOB 页面或数据库反向创造目标字段；
- 把 MOX 的客户类别、无线格局或微波字段套到 TOB；
- 同时保留旧 Schema 与新 Contract；
- 为了共用代码建立全企业超级 Schema；
- 在 TOB 实施时顺便修改 ISP、电力或大企。

Authority 顺序：

1. 本文件；
2. “企业作战地图基表”的 TOB Sheet；
3. 用户后续明确修正；
4. 当前代码、API、`database.js`、SQLite；
5. 旧文档和旧配置。

当前工作簿中 TOB Sheet 的预期名称为 `tob`；本地实施必须读取工作簿确认精确大小写并写入 Contract。

---

## 2. 代码目标

推荐：

```text
src/enterprise/tob/contracts/
├─ tob-field-contract.js
└─ tob-metric-contract.js
```

共享能力继续位于：

```text
src/enterprise/contracts/
```

要求：

- TOB 只能有一份活动 Field Contract；
- TOB 只能有一份活动 Metric Contract；
- 表格、新增、编辑必须从 TOB Field Contract 派生；
- 统计数值和点击筛选必须从 TOB Metric Contract 的同一 `where` 派生；
- `src/config` 中旧 TOB 字段配置迁移完成后删除，不保留活动 re-export 或 fallback。

---

## 3. TOB 最终 34 个业务字段

### 3.1 客户信息（1—5）

| order | canonical key | 用户可见字段 | 目标来源 |
|---:|---|---|---|
| 1 | `region` | 地区部 | 客户主数据关联 |
| 2 | `representativeOffice` | 代表处 | 客户主数据关联 |
| 3 | `country` | 国家 | 客户主数据关联 |
| 4 | `customerId` | 客户ID | 用户追加关系字段；业务表保存 `customer_id` |
| 5 | `customerName` | 客户名称 | 客户主数据关联 |

TOB 不包含：

- 客户类别；
- 行业。

新增：保留现有地区部、代表处等联动，最终定位唯一客户并自动取得 `customer_id`；不允许手填客户ID。

编辑：以上客户信息全部只读，编辑其他字段不得改变 `customer_id`。

### 3.2 存量与份额（6—15）

| order | canonical key | 用户可见字段 | 数据类型 |
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

第 10 项的用户口述为 `ToB微波XX份额-存量`，其中 `XX` 不是允许直接进入 UI 的最终文案。本地 Agent 必须直接读取 TOB Sheet 对应 Excel 列的 Row3 原文，并在实施前将：

- `label`；
- `authority.column`；
- `authority.row2Group`；
- `authority.row3Label`

全部写实。不得把占位符 `XX` 提交到生产页面。

份额字段统一按百分比语义处理；是否在 label 中显示 `%` 以 Excel 原文为准，显示格式由 formatter 统一处理，禁止把 `50%` 错存为 `50` 或 `0.5` 而不建立明确转换契约。

### 3.3 建网与交付（16—21）

| order | canonical key | 用户可见字段 | 推荐控件 |
|---:|---|---|---|
| 16 | `tobNetworkScenario` | ToB建网场景 | Excel Validation 决定 |
| 17 | `tenderType` | 招标类型 | Excel Validation 决定 |
| 18 | `solutionSelection` | 方案选择 | Excel Validation 决定 |
| 19 | `deliveryMode` | 交付方式 | Excel Validation 决定 |
| 20 | `customerVoice` | 客户声音（问题/需求） | textarea |
| 21 | `orderAmount2025Musd` | 25年订货（M$） | number |

固定下拉必须来自 TOB Sheet 的 Data Validation、明确输入说明或用户确认，不允许根据历史数据 distinct values 自动生成。

### 3.4 作战情况（22—34）

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

确认规则：

- `整体空间`：肥肉 / 瘦肉 / 骨头；
- `作战分类-是否重点项目`：是 / 否；
- `空间洞察`：已孵化 / 孵化中；
- `项目状态`：已签单 / 推进中 / 跟踪；
- TOB 确认存在 `项目风险状态`；
- `作战进展`固定为作战情况最后一项，并复用经 MOX 验证的特殊进展编辑机制；
- `一线接口人`保留并验证保存与回填；
- 不新增备注、服务接口人或其他无 Authority 字段。

`作战分类-是否重点项目` 是一个完整字段。页面现有重点项目筛选必须使用同一个 canonical `focusProject`，不得拆成两个业务字段。

---

## 4. 新增与编辑分组

新增/编辑使用以下区块：

1. 客户信息；
2. 存量与份额；
3. 建网与交付；
4. 作战情况。

要求：

- 分组与顺序来自 Contract；
- 表格不显示组标题，但按 1—34 顺序展开；
- `battleProgress`固定最后；
- 新增和编辑不得另建完整字段数组；
- 客户信息在编辑中全部只读；
- `customerVoice`使用多行文本；
- 数量、金额、份额必须使用对应数值控件和 formatter。

---

## 5. Field Contract 与 Excel Authority

每个 source=excel 字段必须直接读取 TOB Sheet 并填写：

```js
authority: {
  source: 'excel',
  sheet: '实际Sheet名',
  column: '实际列字母',
  row2Group: '实际Row2分类',
  row3Label: '实际Row3原文'
}
```

`customerId`：

```js
authority: {
  source: 'requirement',
  sheet: null,
  column: null,
  row2Group: '客户信息',
  row3Label: '客户ID'
}
```

Contract 中的规范化 `label` 与 Excel 原始 `row3Label`允许不同，但不得伪造 Excel 原文。

所有字段还必须明确：

- canonical key；
- data type / unit；
- table/create/edit 投影；
- create/edit 权限与控件；
- API read/create/update 字段；
- `database.js`映射；
- SQLite 列和类型；
- Validation；
- 特殊 behavior。

---

## 6. Metric Contract 与点击筛选

TOB 使用共享 9 项规则：

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

同一 `where` 同时用于统计和点击筛选。九个指标全部可点击；点击只改变下方表格，不错误重算顶部统计。

---

## 7. 页面与现有能力

TOB 页面沿用：

```text
TOB专项
→ 三个并列统计大模块
→ Heatmap
→ 新增/表格/编辑
```

要求：

- `TOB专项`保留现有成熟结构；
- 三个统计大模块参考骨干页面，文字居中；
- 不把九个指标拆成九张顶级卡；
- Heatmap 真实规则未另行冻结前，只做字段兼容和回归保护；
- 现有正确功能先映射到 Contract，不因契约化无理由重写。

---

## 8. 数据库最终态

TOB 业务表最终只保留：

- 34 项目标业务的持久化列（客户展示字段通过关系读取，不重复存储）；
- `customer_id`；
- 项目记录主键；
- 明确必要技术列。

旧字段处理：

- 同义旧字段：一次性 Migration 搬迁数据后删除；
- 无目标对应字段：删除；
- Migration 后不保留 fallback、双读、双写和旧映射；
- 任何结构修改走 `V*.sql + _migrations + database.js`；
- 新建库与升级库最终 Schema 一致；
- TOB 当前外键定义即使已存在，也必须检查运行时约束与 API 校验；不得只因 SQL 中写有 FOREIGN KEY 就宣布关系有效。

全局开启 SQLite foreign keys 属于单独治理范围；TOB 实施至少必须由 API 验证 `customer_id`存在，并确保业务写入不会产生新的无效引用。

---

## 9. Validator 门禁

至少验证：

- 34 个 canonical key 唯一；
- order 1—34 连续；
- 每个字段有 Excel 或 requirement Authority；
- 第 10 项 Excel 精确 label 已解析，不含占位 `XX`；
- 客户类别、行业未进入 TOB Contract；
- 份额字段类型与转换规则明确；
- API/DB映射完整唯一；
- 表格、新增、编辑没有 Contract 外业务字段；
- `focusProject`直接驱动重点项目筛选；
- `battleProgress`使用特殊编辑器；
- 9 个 Metric key 唯一，统计与筛选共用 `where`；
- 旧 `src/config` TOB Schema 无活动引用。

---

## 10. 测试与完成门槛

必须同步测试：

- 34 字段、分组和顺序；
- Excel Authority 元数据；
- 表格/新增/编辑消费同一 Contract；
- 目标外字段为 0；
- 份额、金额、数量类型与格式；
- customer_id 新增、保存、查询与编辑不变；
- 一线接口人和作战进展；
- 重点项目筛选；
- 9 个统计和 9 个点击筛选；
- Migration、新建库与升级库一致性；
- 全量 Vitest、build、lint/typecheck（如配置）。

人工页面验收由用户完成。

TOB 只有在代码、测试、验证、文档完成并经新 Agent 独立审查后，才能标记 VERIFIED。
