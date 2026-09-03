# 企业作战地图：电力 Canonical Authority V1

**状态：READY AFTER MOX VERIFIED**  
**文档分支：`enterprise-battle-map-authority`**  
**本地实施分支：`feature/enterprise-battle-map`**  
**适用范围：电力字段、表格、新增、编辑、API、`database.js`、SQLite、Migration、统计与点击筛选**  
**前置门禁：MOX Canonical Contract 独立验证通过并完成人工验收**

---

## 1. 实施原则

电力模块复用 MOX 已验证的契约机制，但维护独立 Field Contract 和 Metric Contract，不复制 MOX 专属字段。

必须复用：

- 共享 `FieldContract` 类型；
- table/create/edit Projection；
- Contract Validator；
- Metric Contract 与 Metric Engine；
- `customer_id` 关系模式；
- `V*.sql + _migrations + database.js` 数据库治理；
- 同轮代码、测试、自动验证和文档更新；
- 新 Agent 独立审查。

Authority 顺序：

1. 本文件；
2. “企业作战地图基表”的 `电力` Sheet；
3. 用户后续明确修正；
4. 当前代码、API、`database.js`、SQLite；
5. 历史文档、旧 Schema 和旧配置。

当前代码或数据库中存在某字段不能作为保留理由；本文件和 Excel 均无依据的旧业务字段应从最终态删除。

---

## 2. 代码目标

推荐：

```text
src/enterprise/power/contracts/
├─ power-field-contract.js
└─ power-metric-contract.js
```

共享能力继续位于：

```text
src/enterprise/contracts/
```

要求：

- 电力只能有一份活动 Field Contract；
- 电力只能有一份活动 Metric Contract；
- 表格、新增、编辑全部从电力 Field Contract 派生；
- 统计和点击筛选使用同一 Metric `where`；
- 旧 `src/config` 电力字段配置迁移完成后删除，不保留 fallback/re-export；
- 不在电力阶段修改其他业务模块。

---

## 3. 电力最终 28 个业务字段

### 3.1 客户信息（1—6）

| order | canonical key | 用户可见字段 | 目标来源 |
|---:|---|---|---|
| 1 | `region` | 地区部 | 客户主数据关联 |
| 2 | `representativeOffice` | 代表处 | 客户主数据关联 |
| 3 | `country` | 国家 | 客户主数据关联 |
| 4 | `customerId` | 客户ID | 用户追加关系字段；业务表保存 `customer_id` |
| 5 | `customerName` | 客户名称 | 客户主数据关联 |
| 6 | `industry` | 行业 | 客户主数据关联 |

电力不包含 `客户类别`。

新增：复用当前地区部、代表处等联动，最终定位唯一客户并自动取得 `customer_id`；不允许手填客户ID。

编辑：以上客户信息全部只读，编辑其他字段不得改变 `customer_id`。

### 3.2 电力微波业务（7—14）

| order | canonical key | 用户可见字段 | 数据/控件规则 |
|---:|---|---|---|
| 7 | `microwaveApplicationScenario` | 微波应用场景 | enum |
| 8 | `microwaveSolution` | 解决方案 | enum |
| 9 | `installedMicrowaveLinkCount` | 现网微波链路数量（跳） | number |
| 10 | `ourShare` | 我司份额（%） | percent |
| 11 | `substationCount` | 变电站数量（个） | number |
| 12 | `substationFiberizationRate` | 变电站光纤化率（%） | percent |
| 13 | `powerTowerCount` | 电力塔数量（个） | number |
| 14 | `competitorSpaceHops` | 友商空间（跳） | number |

`微波应用场景`确认选项：

- 输变电站微波互连；
- 输电智能巡检；
- 无线回传。

`解决方案`业务含义为 licensed / unlicensed 两类微波方案，不是三个选项。实施必须读取电力 Sheet 的 Data Validation 或输入说明，复制精确字符串：

- 若 Excel 为 `licensed` / `unlicensed`，使用这两个值；
- 若 Excel 为 `licensed微波` / `unlicensed微波`，使用这两个完整值；
- 禁止添加第三个“微波”选项；
- 禁止由现有数据 distinct values 推导枚举。

数量与百分比必须建立明确存储格式。百分比不得在 `50` 与 `0.5` 之间隐式转换；Contract、formatter、API 和数据库应明确采用同一语义。

### 3.3 作战情况（15—28）

| order | canonical key | 用户可见字段 | 规则 |
|---:|---|---|---|
| 15 | `overallSpaceTier` | 整体空间 | enum |
| 16 | `focusProject` | 作战分类-是否重点项目 | enum |
| 17 | `spaceInsight` | 空间洞察 | enum |
| 18 | `projectStatus` | 项目状态 | enum |
| 19 | `projectRiskStatus` | 项目风险状态 | 风险标识 |
| 20 | `overallSpaceHops` | 整体空间（跳） | number |
| 21 | `overallSpaceMusd` | 整体空间（M$） | number |
| 22 | `space2026Hops` | 26年空间（跳） | number |
| 23 | `orderSpace2026Musd` | 26年订货空间（$M） | number |
| 24 | `orderedHops` | 已下单数量（跳） | number |
| 25 | `orderedAmountMusd` | 已下单金额（$M） | number |
| 26 | `representativeOfficeHasSystemDepartment` | 代表处是否有系统部 | enum：是/否 |
| 27 | `frontlineContact` | 一线接口人 | text |
| 28 | `battleProgress` | 作战进展 | 特殊进展编辑器 |

确认规则：

- `整体空间`：肥肉 / 瘦肉 / 骨头；
- `作战分类-是否重点项目`：是 / 否；
- `空间洞察`：已孵化 / 孵化中；
- `项目状态`：已签单 / 推进中 / 跟踪；
- `项目风险状态`：用于标识高风险；
- `代表处是否有系统部`和`一线接口人`是项目记录字段，不属于客户主数据；
- 两者放在表单后部；
- `作战进展`固定为最后一项，使用 MOX 已验证的特殊新增、编辑、保存和回填机制；
- 不新增备注、服务接口人或目标外字段。

`作战分类-是否重点项目`必须直接驱动页面重点项目筛选，不得拆成两个字段或创建重复数据库列。

---

## 4. 新增与编辑分组

新增/编辑使用三个区块：

1. 客户信息；
2. 电力微波业务；
3. 作战情况。

要求：

- 分组、顺序、label、控件和权限全部来自 Contract；
- 表格不显示组标题，但按 1—28 顺序展开；
- `代表处是否有系统部`、`一线接口人`位于作战情况后部；
- `作战进展`固定最后；
- 客户信息在编辑时全部只读；
- 新增和编辑不得另建完整业务字段数组。

---

## 5. Excel Authority 与 Field Contract

每个 source=excel 字段必须从电力 Sheet 写入真实：

```js
authority: {
  source: 'excel',
  sheet: '电力',
  column: '实际列字母',
  row2Group: '实际Row2分类',
  row3Label: '实际Row3原文'
}
```

`customerId`使用 requirement 来源。

每个字段同时必须明确：

- canonical key；
- 规范化 label；
- group/order；
- data type/unit；
- table/create/edit Projection；
- input control / option set；
- API read/create/update 字段；
- `database.js`映射；
- SQLite 列和类型；
- Validation；
- special behavior。

Excel 原文与规范化 label 可不同，但二者必须分别保存。不得为了单位规范化伪造 Excel Row3 原文。

---

## 6. Metric Contract 与点击筛选

电力使用统一 9 项规则：

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

当前“当年项目”不额外增加年份过滤。

同一 `where` 同时服务统计和点击筛选；九项指标全部可点击；点击仅改变表格结果，不错误重算顶部统计。

---

## 7. 页面结构

电力页面按以下结构建设：

```text
电力专项
→ 三个并列统计大模块
→ Heatmap
→ 新增/表格/编辑
```

要求：

- `电力专项`复用 MOX/TOB/ISP 专项模块已验证的视觉结构；
- 电力专项定义文案未由用户确认前不得编造，可显示明确待配置状态；
- 三个统计大模块参考骨干页面，标题和指标文字居中；
- 指标必须在三个大模块内部，不拆成九张顶级卡；
- Heatmap 真实规则未另行冻结前不自行设计，只保证字段重构无回归；
- 表格、新增、编辑以电力 Field Contract 为唯一字段来源。

---

## 8. 数据库最终态

电力业务表最终只保存：

- 电力业务字段；
- 作战情况字段；
- 代表处是否有系统部；
- 一线接口人；
- 作战进展；
- `customer_id`；
- 项目主键和明确必要技术列。

客户展示信息通过客户表关联读取，不在电力业务表中重复维护为 Authority。

旧字段处理：

- 同义字段只在一次性 Migration 中迁移后删除；
- 无目标对应字段直接删除；
- 不保留运行时 legacy alias、fallback、双读或双写；
- 所有结构变化必须走 `V*.sql + _migrations + database.js`；
- Migration 必须注册、事务执行、失败回滚；
- 新建库与升级库最终 Schema 必须一致。

---

## 9. Validator 门禁

至少验证：

- 28 个 canonical key 唯一；
- order 1—28 连续；
- 电力不包含客户类别；
- 国家与行业均存在；
- `友商空间`正式 label 为 `友商空间（跳）`；
- 应用场景枚举准确；
- 解决方案只有 licensed/unlicensed 两类；
- 数量、百分比、金额类型明确；
- API/DB映射完整且唯一；
- 表格、新增、编辑没有 Contract 外字段；
- `focusProject`驱动重点项目筛选；
- `battleProgress`使用特殊编辑器；
- 9 个 Metric key 唯一且统计与筛选共用 `where`；
- 旧电力 Schema/配置无活动引用。

---

## 10. 测试与完成门槛

必须同步测试：

- 28 字段、三个分组与顺序；
- Excel Authority 元数据；
- 表格/新增/编辑消费同一 Contract；
- 目标外字段为 0；
- 应用场景与解决方案枚举；
- 变电站、电力塔、链路、份额、光纤化率的数据类型；
- `customer_id`新增、保存、查询与编辑不变；
- 代表处是否有系统部、一线接口人、作战进展；
- 重点项目筛选；
- 9 个统计和 9 个点击筛选；
- Migration、新建库和升级库一致性；
- 全量 Vitest、build、lint/typecheck（如配置）。

人工页面验收由用户完成。

电力只有在代码、测试、自动验证、文档完成并经独立审查后，才能标记 VERIFIED。
