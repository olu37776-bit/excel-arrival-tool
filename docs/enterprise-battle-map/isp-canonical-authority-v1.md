# 企业作战地图：ISP Canonical Authority V1

**状态：READY AFTER MOX VERIFIED**  
**文档分支：`enterprise-battle-map-authority`**  
**本地实施分支：`feature/enterprise-battle-map`**  
**适用范围：ISP 字段、表格、新增、编辑、API、`database.js`、SQLite、Migration、统计与点击筛选**  
**前置门禁：MOX Canonical Contract 独立验证通过并完成人工验收**

---

## 1. 实施原则

ISP 只复用 MOX 已验证的契约机制，不复制 MOX 的业务字段或分组。

必须复用：

- 共享 `FieldContract` 类型；
- table/create/edit Projection；
- Contract Validator；
- Metric Contract 与 Metric Engine；
- `customer_id` 关系模式；
- `V*.sql + _migrations + database.js` 数据库治理；
- 同轮代码、测试、自动验证和文档更新；
- 实施后新 Agent 独立审查。

Authority 顺序：

1. 本文件；
2. “企业作战地图基表”的 ISP Sheet；
3. 用户后续明确修正；
4. 当前代码、API、`database.js`、SQLite；
5. 历史文档、旧 Schema 和旧配置。

当前工作簿中预期 Sheet 名为 `isp`；本地实施必须读取工作簿确认精确大小写。

---

## 2. 代码目标

推荐：

```text
src/enterprise/isp/contracts/
├─ isp-field-contract.js
└─ isp-metric-contract.js
```

共享能力继续位于 `src/enterprise/contracts/`。

要求：

- ISP 只能有一份活动 Field Contract；
- ISP 只能有一份活动 Metric Contract；
- 表格、新增、编辑全部从 Field Contract 派生；
- 统计值和点击筛选全部使用 Metric Contract 的同一 `where`；
- 旧 `src/config` ISP Schema 在调用方迁移后删除，不保留 fallback/re-export；
- 不在 ISP 阶段修改 MOX、TOB、电力或大企。

---

## 3. ISP 最终 25 个业务字段

### 3.1 客户信息（1—6）

| order | canonical key | 用户可见字段 | 目标来源 |
|---:|---|---|---|
| 1 | `region` | 地区部 | 客户主数据关联 |
| 2 | `representativeOffice` | 代表处 | 客户主数据关联 |
| 3 | `country` | 国家 | 客户主数据关联 |
| 4 | `customerId` | 客户ID | 用户追加关系字段；业务表保存 `customer_id` |
| 5 | `customerName` | 客户名称 | 客户主数据关联 |
| 6 | `industry` | 行业 | 客户主数据关联 |

ISP 不包含 `客户类别`。

新增：复用当前地区部、代表处等联动，最终定位唯一客户并自动取得 `customer_id`；客户ID不可手工输入。

编辑：以上客户信息全部只读，编辑其他字段不得改变 `customer_id`。

### 3.2 微波业务（7—11）

| order | canonical key | 用户可见字段 | 数据/控件规则 |
|---:|---|---|---|
| 7 | `microwaveApplicationScenario` | 微波应用场景 | enum |
| 8 | `microwaveSolution` | 解决方案 | enum |
| 9 | `installedMicrowaveLinkCount` | 现网微波链路数量（跳） | number |
| 10 | `ourShare` | 我司份额（%） | percent |
| 11 | `competitorSpaceHops` | 友商空间（跳） | number |

`微波应用场景`确认选项：

- 骨干汇聚微波互联；
- 2B专线；
- 基站回传。

`解决方案`确认的业务含义是 licensed / unlicensed 两类微波方案，不是三个选项。实施时必须直接读取 ISP Sheet 的 Data Validation 或输入说明，使用 Excel 中的精确字符串：

- 若 Excel 原文为 `licensed` / `unlicensed`，使用这两个值；
- 若 Excel 原文为 `licensed微波` / `unlicensed微波`，使用这两个完整值；
- 禁止额外增加第三个“微波”选项；
- 禁止根据历史数据 distinct values 扩大枚举。

### 3.3 作战情况（12—25）

| order | canonical key | 用户可见字段 | 规则 |
|---:|---|---|---|
| 12 | `overallSpaceTier` | 整体空间 | enum |
| 13 | `focusProject` | 作战分类-是否重点项目 | enum |
| 14 | `spaceInsight` | 空间洞察 | enum |
| 15 | `projectStatus` | 项目状态 | enum |
| 16 | `projectRiskStatus` | 项目风险状态 | 风险标识 |
| 17 | `overallSpaceHops` | 整体空间（跳） | number |
| 18 | `overallSpaceMusd` | 整体空间（M$） | number |
| 19 | `space2026Hops` | 26年空间（跳） | number |
| 20 | `orderSpace2026Musd` | 26年订货空间（$M） | number |
| 21 | `orderedHops` | 已下单数量（跳） | number |
| 22 | `orderedAmountMusd` | 已下单金额（$M） | number |
| 23 | `representativeOfficeHasSystemDepartment` | 代表处是否有系统部 | enum：是/否 |
| 24 | `frontlineContact` | 一线接口人 | text |
| 25 | `battleProgress` | 作战进展 | 特殊进展编辑器 |

确认规则：

- `整体空间`：肥肉 / 瘦肉 / 骨头；
- `作战分类-是否重点项目`：是 / 否；
- `空间洞察`：已孵化 / 孵化中；
- `项目状态`：已签单 / 推进中 / 跟踪；
- `项目风险状态`：用于标识高风险；
- `代表处是否有系统部`与`一线接口人`是当前项目记录字段，不属于客户主数据；
- 两个字段放在表单后部，不进入客户信息分组；
- `作战进展`固定为最后一个字段，并复用 MOX 验证后的特殊进展添加、编辑、保存和回填机制；
- 不新增备注、服务接口人或目标外字段。

---

## 4. 新增与编辑分组

新增和编辑使用三个视觉区块：

1. 客户信息；
2. 微波业务；
3. 作战情况。

`代表处是否有系统部`、`一线接口人`位于作战情况后部；`作战进展`固定为最后一项。

要求：

- 分组、字段集合和顺序来自 Contract；
- 表格不显示分组标题，但按 1—25 顺序展开；
- 客户信息在编辑时全部只读；
- 数量、金额、百分比使用对应控件和 formatter；
- 新增和编辑不得另建完整业务字段数组。

---

## 5. Excel Authority 与 Contract 属性

每个 Excel 字段必须填入真实：

```js
authority: {
  source: 'excel',
  sheet: '实际Sheet名',
  column: '实际列字母',
  row2Group: '实际Row2分类',
  row3Label: '实际Row3字段原文'
}
```

`customerId`使用 requirement 来源。

每个字段同时必须明确：

- canonical key；
-规范化 label；
- group/order；
- data type/unit；
- table/create/edit 配置；
- input control / option set；
- API read/create/update 字段；
- `database.js`映射；
- SQLite 列和类型；
- Validation；
- 特殊 behavior。

Excel 原始 label 与规范化 label 可不同，但 Contract 必须同时保存二者，不能伪造 Excel 原文。

---

## 6. Metric Contract 与点击筛选

ISP 使用统一 9 项规则：

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

当前“当年项目”不额外加年份过滤。

同一 `where` 同时服务统计和点击筛选；九项指标全部可点击；点击仅改变表格结果，不错误重算顶部统计。

---

## 7. 页面结构

ISP 页面沿用：

```text
ISP专项
→ 三个并列统计大模块
→ Heatmap
→ 新增/表格/编辑
```

要求：

- 保留当前 ISP 专项成熟结构；
- 三个统计大模块参考骨干页面，文字居中；
- 每个大模块内部展示指标，不拆成九张顶级卡；
- Heatmap 真实规则未另行冻结前，仅保护兼容性；
- 表格、新增、编辑以 ISP Field Contract 为唯一业务字段来源。

---

## 8. 数据库最终态

ISP 业务表最终只保存：

- ISP 专属业务字段；
- 作战情况字段；
- `代表处是否有系统部`；
- `一线接口人`；
- `battleProgress`；
- `customer_id`；
- 项目主键和明确必要技术列。

客户展示字段通过客户关系读取，不在 ISP 表重复作为业务 Authority。

已知当前 ISP `customer_id`链路曾存在缺口。实施必须检查：

- Schema 列；
- API read/create/update；
- `database.js` CRUD、映射和 Validation；
- 旧记录确定性客户匹配；
- 无法匹配或多匹配记录不得取第一条；
- Migration 后新增、查询和编辑均保持正确关系。

旧字段规则：

- 同义旧字段：一次性迁移后删除；
- 无目标对应字段：直接删除；
- 不保留长期 fallback、双读或双写；
- 所有数据库结构变化走 `V*.sql + _migrations + database.js`；
- 新建库与升级库最终 Schema 一致。

---

## 9. Validator 门禁

至少验证：

- 25 个 canonical key 唯一；
- order 1—25 连续；
- ISP 不包含客户类别；
- 每个字段具有 Excel 或 requirement Authority；
- 解决方案只有 licensed/unlicensed 两类，不产生第三个“微波”选项；
- 数量、份额、金额的数据类型和格式明确；
- API/DB映射完整且唯一；
- 表格、新增、编辑没有 Contract 外业务字段；
- `focusProject`驱动现有重点项目筛选；
- `battleProgress`使用特殊进展编辑器；
- 9 个 Metric key 唯一且统计/筛选共用 `where`；
- 旧 ISP Schema/配置无活动引用。

---

## 10. 测试与完成门槛

必须同步测试：

- 25 字段、三个分组和精确顺序；
- Excel Authority 元数据；
- 表格/新增/编辑消费同一 Contract；
- 目标外字段为 0；
- 应用场景与解决方案枚举；
- 数量、百分比、金额输入和显示；
- `customer_id`新增、保存、查询与编辑不变；
- 代表处是否有系统部、一线接口人、作战进展；
- 重点项目筛选；
- 9 项统计和 9 项点击筛选；
- Migration、新建库和升级库最终一致；
- 全量 Vitest、build、lint/typecheck（如配置）。

人工页面验收由用户执行。

ISP 只有在代码、测试、验证、文档完成并经独立审查后，才能标记 VERIFIED。
