# 企业作战地图：ISP Canonical Authority V2

**状态：READY AFTER MOX VERIFIED**  
**文档分支：`enterprise-battle-map-authority`**  
**本地实施分支：`feature/enterprise-battle-map`**  
**取代文档：`isp-canonical-authority-v1.md`**  
**共享架构：`enterprise-contract-architecture-v2.md`**

---

## 1. 实施原则

ISP 全面参考 MOX 验证后的契约机制，但只使用 ISP 自己的字段 Contract。

必须复用：FieldContract、Table/Create/Edit Projection、Validator、Metric Engine、Heatmap Engine、`customer_id`关系模式、`V*.sql + _migrations + database.js`治理和测试/审查闭环。

Authority 顺序：本文件 → 本地 ISP Sheet → 用户最新修正 → 当前代码/API/DB → 旧文档。

旧代码存在某字段不能作为保留理由。最终集合之外的旧业务字段必须从 UI、API 活动契约、`database.js` 和最终数据库 Schema 删除。

---

## 2. 新增与编辑的同级 Section

ISP 新增与编辑统一使用三个同级区块：

```text
客户信息 ｜ 业务格局 ｜ 作战情况
```

要求：

- 复用 MOX 验证后的弹窗外壳和 Section 样式；
- 三个 Section 是同级并列区块，不是先后流程；
- 表格不显示 Section 标题，但按全局 order 展开；
- `作战进展`在作战情况最后；
- 新增与编辑不得维护独立完整字段数组。

---

## 3. ISP 最终 25 个业务字段

### 3.1 客户信息（1—6）

| order | canonical key | 用户可见字段 |
|---:|---|---|
| 1 | `region` | 地区部 |
| 2 | `representativeOffice` | 代表处 |
| 3 | `country` | 国家 |
| 4 | `customerId` | 客户ID |
| 5 | `customerName` | 客户名称 |
| 6 | `industry` | 行业 |

ISP 不包含客户类别。

新增保留现有地区部、代表处等联动，最终匹配唯一客户并自动取得 `customer_id`。编辑时客户信息全部只读。

### 3.2 业务格局（7—11）

| order | canonical key | 用户可见字段 | 类型/枚举 |
|---:|---|---|---|
| 7 | `microwaveApplicationScenario` | 微波应用场景 | enum |
| 8 | `solutionType` | 解决方案 | enum |
| 9 | `installedMicrowaveLinkCount` | 现网微波链路数量（跳） | number |
| 10 | `ourShare` | 我司份额（%） | percent |
| 11 | `competitorSpaceHops` | 友商空间（跳） | number |

微波应用场景固定值：

- 骨干汇聚微波互联；
- 2B专线；
- 基站回传。

解决方案固定值：

- licensed微波；
- unlicensed微波。

不得把“licensed / unlicensed微波”错误拆成第三个独立“微波”选项。

份额字段必须在 Contract 中明确数据库存储口径是 0—1 还是 0—100，并通过 parser/formatter 保证一致。

### 3.3 作战情况（12—25）

| order | canonical key | 用户可见字段 |
|---:|---|---|
| 12 | `overallSpaceTier` | 整体空间 |
| 13 | `focusProject` | 作战分类-是否重点项目 |
| 14 | `spaceInsight` | 空间洞察 |
| 15 | `projectStatus` | 项目状态 |
| 16 | `projectRiskStatus` | 项目风险状态 |
| 17 | `overallSpaceHops` | 整体空间（跳） |
| 18 | `overallSpaceMusd` | 整体空间（M$） |
| 19 | `space2026Hops` | 26年空间（跳） |
| 20 | `orderSpace2026Musd` | 26年订货空间（$M） |
| 21 | `orderedHops` | 已下单数量（跳） |
| 22 | `orderedAmountMusd` | 已下单金额（$M） |
| 23 | `representativeOfficeHasSystemDepartment` | 代表处是否有系统部 |
| 24 | `frontlineContact` | 一线接口人 |
| 25 | `battleProgress` | 作战进展 |

确认枚举：

- 整体空间：肥肉 / 瘦肉 / 骨头；
- 作战分类-是否重点项目：是 / 否；
- 空间洞察：已孵化 / 孵化中；
- 项目状态：已签单 / 推进中 / 跟踪；
- 代表处是否有系统部：是 / 否。

`作战分类-是否重点项目`是一个完整字段；页面重点项目筛选必须直接使用 `focusProject`。

`作战进展`固定为最后一个字段并使用 MOX 验证后的特殊进展编辑器。

---

## 4. Field Contract 与 Excel Authority

每个 source=excel 字段必须从 ISP Sheet 填写真实：Sheet、列、Row2分类、Row3原文和 Data Validation。

`customerId`标记为 `source: 'requirement'`。

每个字段必须定义：canonical key、label、section、order、data type/unit、table/create/edit、API read/create/update、`database.js`映射、SQLite列、Validation和特殊行为。

表格、新增、编辑必须从同一 ISP Field Contract 派生，目标外业务字段数量均为0。

所有单位使用中文全角括号。规范化 label 与 Excel 原始 Row3 可不同，但 Contract 必须同时保留 Excel 原文和规范显示名。

---

## 5. 页面结构与 Heatmap

ISP 页面：

```text
ISP专项
→ 空间洞察 / 当年项目 / 空间拓展三个并列模块
→ ISP Heatmap
→ 新增 / 表格 / 编辑
```

要求：

- 三个统计大模块内部展示9个指标，不拆成9张顶级卡；
- 标题和指标文字居中；
- Heatmap 使用共享 `HeatmapChart` 和独立 `isp-heatmap-contract.js`；
- Heatmap 的维度、聚合值、Tooltip和点击行为必须有明确业务 Authority；未冻结时只显示空状态，不生成假数据；
- 如 Heatmap 点击需要筛选表格，必须通过同一 Contract 条件产生过滤结果。

---

## 6. Metric Contract

ISP 使用共享9项规则：

- 已孵化：`spaceInsight=已孵化`；
- 孵化中：`spaceInsight=孵化中`；
- 当年项目总项目数：`projectStatus IN（已签单，推进中）`；
- 已签单：`projectStatus=已签单`；
- 推进中：`projectStatus=推进中`；
- 高风险：`projectStatus=推进中 AND projectRiskStatus=高风险`；
- 可参与总空间：`spaceInsight=已孵化 AND projectStatus=跟踪`，sum `overallSpaceMusd`；
- 空间拓展总项目：`projectStatus=跟踪`；
- 已落地：`spaceInsight=已孵化 AND projectStatus=跟踪`。

同一 `where` 同时用于统计计算和点击筛选；当前不额外增加年份过滤。

---

## 7. 数据库与清理

最终 ISP 表只保留目标业务列、`customer_id`、主键和必要技术列。

- 同义旧字段通过一次性 Migration 搬迁后删除；
- 无目标对应旧字段直接删除；
- Migration 注册到 `database.js`，成功后写 `_migrations`，失败回滚；
- 新库 Schema 与旧库升级结果一致；
- 不保留 fallback、双读、双写或旧 Schema re-export；
- `src/config` 不得继续保留活动 ISP Authority。

当前已知 ISP `customer_id`链路如仍缺失，必须按 MOX 已验证方式补齐，而不是创建另一套客户模型。

---

## 8. 自动门禁

至少验证：

1. 25个key唯一、order 1—25连续；
2. Section仅为客户信息/业务格局/作战情况；
3. ISP有行业、没有客户类别；
4. 应用场景和解决方案枚举正确；
5. 表格/新增/编辑真实消费同一 Contract；
6. 客户字段编辑只读，`customer_id`新增保存和编辑不变；
7. 重点项目筛选使用 `focusProject`；
8. 作战进展特殊编辑器有效；
9. 9个统计和9个点击筛选正确；
10. Heatmap生命周期和空状态正确；
11. API/DB映射完整；
12. Migration、新库、升级库、全量测试和build通过。

人工页面验收由用户执行。

---

## 9. 完成门槛

ISP 只有在字段、三个 Projection、API、数据库、统计、点击筛选、Heatmap、自动测试、独立审查和用户人工验收全部通过后才能标记 VERIFIED。
