# 企业作战地图：TOB Canonical Authority V2

**状态：READY AFTER MOX VERIFIED**  
**文档分支：`enterprise-battle-map-authority`**  
**本地实施分支：`feature/enterprise-battle-map`**  
**取代文档：`tob-canonical-authority-v1.md`**  
**共享架构：`enterprise-contract-architecture-v2.md`**

---

## 1. 实施原则

TOB 全面参考 MOX 验证后的实现机制，但不复制 MOX 字段。

必须复用：

- 共享 FieldContract 类型；
- Table/Create/Edit Projection；
- Contract Validator；
- Metric Contract 与点击筛选引擎；
- Heatmap 共享组件与生命周期；
- `customer_id` 关系模式；
- `V*.sql + _migrations + database.js` 数据库治理；
- 代码、测试、自动验证、独立审查闭环。

Authority 顺序：本文件 → 本地 TOB Sheet → 用户最新修正 → 当前代码/API/DB → 旧文档。

旧页面或数据库存在某字段不能作为保留理由。最终字段集合之外的旧业务字段必须从 UI、API 活动契约、`database.js` 和最终数据库 Schema 删除。

---

## 2. 新增与编辑的同级 Section

TOB 新增和编辑统一使用三个同级区块：

```text
客户信息 ｜ 业务格局 ｜ 作战情况
```

它们是同级 Section，不是先后依赖流程。

要求：

- 复用 MOX 验证后的弹窗外壳、Section 样式、按钮和校验呈现；
- 不再把“存量与份额”“建网与交付”做成顶级 Section；
- 这些语义只作为业务格局内部字段说明；
- 表格不显示 Section 标题，但按全局 order 展开；
- `作战进展`在作战情况最后。

---

## 3. TOB 最终 34 个业务字段

### 3.1 客户信息（1—5）

| order | canonical key | 用户可见字段 |
|---:|---|---|
| 1 | `region` | 地区部 |
| 2 | `representativeOffice` | 代表处 |
| 3 | `country` | 国家 |
| 4 | `customerId` | 客户ID |
| 5 | `customerName` | 客户名称 |

TOB 不包含客户类别和行业。

新增保留现有地区部、代表处等联动，最终定位唯一客户并自动取得 `customer_id`；客户ID不可手填。编辑时以上客户信息全部只读。

### 3.2 业务格局（6—21）

| order | canonical key | 用户可见字段 | 类型/说明 |
|---:|---|---|---|
| 6 | `backboneMicrowaveLinkCount` | 大网微波链路数量 | number |
| 7 | `tobInstalledMicrowaveLinkCount` | ToB微波链路数量-存量 | number |
| 8 | `tobInstalledOurShare` | ToB微波我司份额-存量 | percent |
| 9 | `tobInstalledNokiaShare` | ToB微波NOKIA份额-存量 | percent |
| 10 | `tobInstalledAdditionalVendorShare` | 以 TOB Excel Row3 精确原文为准 | percent |
| 11 | `tobInstalledEricssonShare` | ToB微波Ericsson份额-存量 | percent |
| 12 | `tobInstalledNceShare` | ToB微波NCE份额-存量 | percent |
| 13 | `tobInstalledSiaeShare` | ToB微波SIAE份额-存量 | percent |
| 14 | `tobInstalledCeragonShare` | ToB微波Ceragon份额-存量 | percent |
| 15 | `tobNewMicrowaveShareReference` | ToB微波份额（New，供参考） | percent |
| 16 | `tobNetworkScenario` | ToB建网场景 | Excel Validation决定 |
| 17 | `tenderType` | 招标类型 | Excel Validation决定 |
| 18 | `solutionSelection` | 方案选择 | Excel Validation决定 |
| 19 | `deliveryMode` | 交付方式 | Excel Validation决定 |
| 20 | `customerVoice` | 客户声音（问题/需求） | textarea |
| 21 | `orderAmount2025Musd` | 25年订货（M$） | number |

第10项用户口述曾使用 `XX` 占位。本地 Agent 必须从 TOB Sheet 的真实 Row3 读取厂商名称，禁止将 `XX` 写入页面或 Contract。

份额字段按百分比语义处理。Contract 必须明确数据库存储是 0—1 还是 0—100，并通过 formatter/parser 保证 UI、API、DB 一致。

固定下拉只能来自 Excel Data Validation、明确输入说明或用户确认，禁止根据历史 distinct values 自动生成。

### 3.3 作战情况（22—34）

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

确认枚举：

- 整体空间：肥肉 / 瘦肉 / 骨头；
- 作战分类-是否重点项目：是 / 否；
- 空间洞察：已孵化 / 孵化中；
- 项目状态：已签单 / 推进中 / 跟踪；
- TOB 存在项目风险状态；
- 作战进展复用 MOX 验证后的特殊进展编辑机制并固定最后；
- 不新增备注或服务接口人。

`作战分类-是否重点项目`是一个完整字段，现有重点项目筛选必须直接使用 canonical `focusProject`。

---

## 4. Field Contract 与 Excel Authority

每个 Excel 字段必须填写：

```js
authority: {
  source: 'excel',
  sheet: 'TOB实际Sheet名',
  column: '实际列字母',
  row2Group: '实际Row2分类',
  row3Label: '实际Row3原文'
}
```

`customerId`标记为 `source: 'requirement'`。

每项 Contract 必须同时定义：canonical key、label、section、order、data type/unit、table/create/edit、API read/create/update、`database.js`映射、SQLite列、Validation和特殊行为。

表格、新增、编辑必须从同一 TOB Field Contract 派生，目标外业务字段数量均为0。

---

## 5. 页面结构与 Heatmap

TOB 页面统一结构：

```text
TOB专项
→ 空间洞察 / 当年项目 / 空间拓展三个并列模块
→ TOB Heatmap
→ 新增 / 表格 / 编辑
```

要求：

- 三个统计大模块内部展示9个指标，不拆成9张顶级卡；
- 标题与指标文字居中；
- Heatmap 使用共享 `HeatmapChart` 和独立 `tob-heatmap-contract.js`；
- TOB Heatmap 的维度、聚合值、Tooltip和点击行为必须从 Excel/用户规则冻结；未冻结前只保留空状态，不生成假数据；
- 如 Heatmap 点击需要筛选明细，必须通过 Heatmap Contract 的统一条件产生表格过滤。

---

## 6. Metric Contract

TOB 使用共享9项规则：

- 已孵化：`spaceInsight=已孵化`；
- 孵化中：`spaceInsight=孵化中`；
- 当年项目总项目数：`projectStatus IN（已签单，推进中）`；
- 已签单：`projectStatus=已签单`；
- 推进中：`projectStatus=推进中`；
- 高风险：`projectStatus=推进中 AND projectRiskStatus=高风险`；
- 可参与总空间：`spaceInsight=已孵化 AND projectStatus=跟踪`，sum `overallSpaceMusd`；
- 空间拓展总项目：`projectStatus=跟踪`；
- 已落地：`spaceInsight=已孵化 AND projectStatus=跟踪`。

同一 `where` 同时用于统计和点击筛选。当前不额外增加年份过滤。

---

## 7. 数据库与清理

最终 TOB 表只保留目标业务列、`customer_id`、主键和必要技术列。

- 同义旧字段通过一次性 `V*.sql` Migration 搬迁后删除；
- 无目标对应旧字段直接删除；
- Migration 必须注册到 `database.js`，成功后写 `_migrations`，失败回滚；
- 新建库 Schema 与旧库升级结果一致；
- 不保留 fallback、双读、双写或旧 Schema re-export；
- `src/config` 不得继续保留活动 TOB Authority。

---

## 8. 自动门禁

至少验证：

1. 34个key唯一、order 1—34连续；
2. Section仅为客户信息/业务格局/作战情况；
3. TOB无客户类别和行业；
4. 第10项已从Excel解析真实厂商名称；
5. 表格/新增/编辑真实消费同一 Contract；
6. 客户字段编辑只读，`customer_id`新增保存和编辑不变；
7. 重点项目筛选使用 `focusProject`；
8. 作战进展特殊编辑器有效；
9. 9个统计和9个点击筛选正确；
10. Heatmap生命周期和空状态正确；
11. API/DB映射完整；
12. Migration、新库、升级库和全量测试通过。

人工页面验收由用户执行。

---

## 9. 完成门槛

TOB 只有在字段、三处 Projection、API、数据库、统计、点击筛选、Heatmap、测试、独立审查和用户人工验收全部通过后才能标记 VERIFIED。
