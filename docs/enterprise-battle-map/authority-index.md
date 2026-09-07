# 企业作战地图 Authority 文档索引

**状态：CURRENT AUTHORITY INDEX**  
**文档分支：`enterprise-battle-map-authority`**  
**长期代码分支：`feature/enterprise-battle-map`**

---

## 0. 当前新增业务变更（优先执行）

用户已确认新版 Excel 的两项变更：所有业务表仅整列删除取值为“肥肉/瘦肉/骨头”的“整体空间”分类字段，其他字段与数据不动；大企表名改为“大企（油气矿、广电、交通）”。
执行 `enterprise-excel-confirmed-delta-v1.md`，其中包含准确范围、本地工作簿修改、字段契约同步、验证与报告要求。
本文件下方关于 V0.2 冻结和首页先行的旧阶段安排，对这两项已确认变更不构成阻塞；其他未确认差异继续冻结。旧模块字段数和旧大企表名按此增量覆盖。首页 V4 的独立核验状态仍待报告，不视为通过。

## 1. 当前正式 Authority

| 顺序 | 文档 | 用途 | 当前门禁 |
|---:|---|---|---|
| 1 | `enterprise-contract-architecture-v5.md` | 端到端 canonical identity、真实 Runtime Projection、API canonical-only、Customer 主键贯穿、Heatmap canonical key、Progress 单一事实源、DB/Conformance Gate | 所有企业任务必读 |
| 2 | `architecture/enterprise-runtime-field-options-contract-v1.md` | Runtime Field View Model、select/options 判定、动态 options 生命周期、错误边界与五模块回归门禁 | 长期 Runtime Options Authority |
| 3 | `mox-canonical-authority-v6.md` | MOX 41字段、4 group、Create/Edit runtime、Heatmap、legacy key、Progress、Customer、DB/测试最终目标 | 已验证业务 Reference baseline |
| 3b | `remediation/tob-shared-form-production-path-repair-v1.md` | 修复 TOB 本地完整表单构建器，迁入真实共享 Create/Edit 渲染链，补强漏检门禁 | 用户报告修复及后续检查完成；保留回归 |
| 3a | `remediation/five-module-shared-operation-convergence-v1.md` | 根据最新本地审查报告，对其他操作建立五模块生产路径清单，收敛重复机制并修复阻塞 | 历史实施基线；保留回归 |
| 4 | `remediation/five-module-shared-form-renderer-convergence-v3.md` | 验证 MOX 是否也存在 local form builder；从 MOX 已验证行为提炼唯一 shared form renderer，并让 MOX/TOB/ISP/Power/Large 全部消费同一真实生产 render path | 已报告实施；当前修复须回归 |
| 5 | `remediation/non-mox-shared-form-renderer-convergence-v1.md` | 仅针对 4x non-MOX module-local form builders 的第一版方案 | **SUPERSEDED BY FIVE-MODULE V3** |
| 6 | `reviews/non-mox-full-independent-review-rerun-v3.md` | 固定新 HEAD，完整重跑原始审查；覆盖五模块真实渲染链、全部历史 findings 和新增问题 | 既有五模块机制审查与回归基线 |
| 7 | `reviews/non-mox-modules-mox-reference-independent-review-v1.md` | 原始全量 Independent Review Authority：shared runtime、Create/Edit、Customer、Progress、Heatmap、Metric、API/DB、重复机制、hidden consumers、测试可信度 | 每个新 HEAD 必须完整重跑 |
| 8 | `remediation/non-mox-alignment-independent-review-findings-remediation-v2.md` | 关闭前次独立审查 7 个 blocking findings | 已实施；历史回归集 |
| 9 | `reviews/non-mox-alignment-independent-rereview-v2.md` | 仅围绕7个finding的定向复核草案 | SUPERSEDED BY V3 |
| 10 | `remediation/non-mox-modules-mox-reference-alignment-v1.md` | TOB/ISP/电力/大企全面向MOX已验证机制对齐 | 历史实施背景；其 PASS 曾被独立审查推翻 |
| 11 | `investigation/enterprise-excel-v0.1-v0.2-diff-survey-v1.md` | 企业作战地图基表V0.1→V0.2 Schema/Contract差异调查 | 可并行只读；业务字段变化需先Authority Review |
| 12 | `remediation/enterprise-form-options-root-cause-remediation-v2.md` | `f.options is not iterable` 根因级修复 | 已实施并经用户确认Create/Edit可打开 |
| 13 | `remediation/enterprise-customer-data-fetch-unification-v2.md` | Customer SQL/customer_id贯穿修复及长期回归门禁 | 已修复，统一机制回归项 |
| 14 | `reviews/mox-end-to-end-canonical-independent-review-v1.md` | MOX端到端独立审查规范 | 最新复审PASS |
| 15 | `remediation/mox-4-group-render-chain-repair-v1.md` | MOX 4-group renderer断链修复 | 已实施并通过复审 |
| 16 | `remediation/mox-end-to-end-canonical-convergence-v1.md` | MOX端到端canonical收敛 | 已实施，作为行为 Reference baseline |
| 17 | `investigation/enterprise-runtime-implementation-survey-v1.md` | 已完成的实际运行链调查规范 | 事实证据来源 |
| 18 | `integration/parallel-module-integration-plan-v1.md` | TOB/ISP/电力+大企合并规则 | 集成历史/回归参考 |
| 19 | `integration/local-worktree-layout-v1.md` | 本地真实worktree路径 | 本地执行必读 |
| 20 | `tob-canonical-authority-v2.md` | TOB当前字段和3-group业务基线 | 字段暂冻结，V0.2后可能升级 |
| 21 | `isp-canonical-authority-v2.md` | ISP当前字段和3-group业务基线 | 字段暂冻结，V0.2后可能升级 |
| 22 | `power-canonical-authority-v2.md` | 电力当前字段和3-group业务基线 | 字段暂冻结，V0.2后可能升级 |
| 23 | `large-enterprise-canonical-authority-v2.md` | 大企当前字段和3-group业务基线 | 字段暂冻结，V0.2后可能升级 |
| 24 | `enterprise-home-canonical-authority-v4.md` | 首页间距、全局场景卡样式/数字、已下单金额实时汇总、空间拓展及双层导航；含本地实施步骤/产物 | **本轮实施基线；当前执行第17节独立核验** |

---

## 2. 当前阶段判断

用户在前轮网络/Authority核对后反馈“好了”，并人工检查“基本没什么问题”；本轮明确提出企业首页的布局、样式、真实金额和点击导航调整。
这是人工检查反馈，不是云端重新核验本地代码/测试的声明。前轮报告继续作为原 HEAD 的历史证据，本轮新 HEAD 的验证另行记录。

当前：
```text
PREVIOUS_REVIEW = USER_REPORTED_NO_BLOCKERS
PREVIOUS_MANUAL_CHECK = BASICALLY_ACCEPTABLE_WITH_HOME_ISSUES
CURRENT_TASK = EXCEL_CONFIRMED_DELTA_V1
EXCEL_CONFIRMED_DELTA_V1 = AUTHORIZED_PENDING_LOCAL_IMPLEMENTATION
HOME_V4_INDEPENDENT_REVIEW = PENDING_RESULT
HOME_V4_IMPLEMENTATION = IMPLEMENTED_REPORTED
MANUAL_ACCEPTANCE_V4 = PENDING
```

用户现已报告首页V4实施完成，尚无本轮独立核验结果。执行 `enterprise-home-canonical-authority-v4.md` 第17节。本轮不重新实施已修复的五模块共享表单和其他操作链；保持其规则与必要回归。

---

## 3. 当前 Five-Module Shared Renderer 目标

唯一允许的最终主链：

```text
Module Field Contract
→ shared Projection
→ shared Runtime Field View Model
→ shared Dynamic Options / Control / Editor Registry
→ shared Form Shell
→ shared Group Renderer
→ shared Field Renderer
→ actual Vue render tree
```

必须分别证明：

```text
MOX_USES_SHARED_FORM_RENDERER=PASS
TOB_USES_SHARED_FORM_RENDERER=PASS
ISP_USES_SHARED_FORM_RENDERER=PASS
POWER_USES_SHARED_FORM_RENDERER=PASS
LARGE_USES_SHARED_FORM_RENDERER=PASS
```

以及：

```text
MODULE_LOCAL_FORM_HTML_BUILDERS=0
MODULE_LOCAL_SECTION_SCHEMAS=0
DUPLICATE_SECTION_RENDER_PATHS=0
DUPLICATE_FIELD_RENDERERS=0
DUPLICATE_FORM_SHELLS=0
DUPLICATE_VALIDATION_RENDERERS=0
```

---

## 4. MOX 的特殊处理规则

以下为 V3 已要求的实施路径，独立审查需核对 Inventory、真实代码与回归证据；不得因 MOX 先前通过业务审查而豁免本轮渲染链验证。

如果：

```text
MOX_LOCAL_FORM_BUILDER=NO
```

则以 MOX 当前真实 shared path 作为基线，迁入其他模块。

如果：

```text
MOX_LOCAL_FORM_BUILDER=YES
```

则必须：

```text
从 MOX 已验证行为提炼 shared renderer
→ MOX 自己先迁入 shared renderer
→ MOX full regression PASS
→ TOB
→ ISP
→ Power
→ Large
```

不得把 MOX local renderer 当作可长期复制的“参考模板”。

---

## 5. 业务结构保持独立

共享 renderer 不改变模块业务 Field Contract。

MOX：

```text
客户信息
无线格局
微波格局
作战情况
```

TOB / ISP / Power / Large：

```text
客户信息
业务格局
作战情况
```

renderer 必须根据 Contract 自然产生 4-group 或 3-group，不允许通过完整 module-specific template branch 表达业务布局。

---

## 6. 本轮首页实施入口

当前完整 Authority 为 `enterprise-home-canonical-authority-v4.md`，取代首页 V1/V2/V3。
本轮：
- 企业专项、三卡和空间拓展用正常布局流分隔，消除重叠；
- 三卡和空间拓展复用全局首页“骨干场景/企业场景/单域自治”卡片和数字样式；
- 目标保留 xx M$，实时汇总各模块已下单金额；
- ISP&大企实时包含 ISP、电力、大企；空间拓展维持已冻结公式；
- 全局首页企业场景进入企业首页，MOX/TOB/ISP&大企三卡进入各自约定子页。

本轮用户已明确授权首页工作，旧“首页 DEFERRED/最后建设”的阶段安排不阻塞此任务。Excel V0.2 未授权字段变化继续独立处理。
具体本地步骤、WRITE_SCOPE生成、验证、报告和回执以V4第16节为准。

---

## 7. 既有五模块机制独立审查门禁

以下为共享表单/共享操作链机制的完整复审基线。本轮首页改动首先按首页 V4 范围独立核验；若实际修改触及共享业务机制，再按影响执行相关既有门禁。

针对五模块机制修复的新代码 HEAD 必须完整执行：

```text
reviews/non-mox-modules-mox-reference-independent-review-v1.md
+
reviews/non-mox-full-independent-review-rerun-v3.md
```

重新审查：

- Field Contract / shared runtime；
- Table/Create/Edit真实Projection；
- Runtime Field View Model / Dynamic Options；
- five-module shared form shell / group renderer / field renderer；
- Customer relation；
- Progress History / popup / single-source；
- Heatmap canonical identity；
- Metric calculation / click-filter；
- Table/filter/search/sort hidden consumers；
- API canonical-only；
- database.js / SQLite / Migration / round-trip；
- duplicate mechanisms；
- active legacy keys；
- undeclared canonical consumers；
- tests是否覆盖真实 Production path；
- MOX regression；
- full tests/build。

历史 findings 继续作为强制回归集，但不是完整审查边界。

---

## 8. 长期统一规则继续有效

### Runtime Field

Field Contract / `fieldDef` 是 type/control/editor/group/order 等静态 metadata 唯一 Authority；Runtime Field View Model 只承载动态状态。

### Customer

```text
customers.customer_id
→ shared query
→ shared API
→ normalization
→ dynamic options
→ unique selection
→ business customer_id
```

### Progress

```text
Progress History = 唯一持久化事实源
battleProgress = latest/current canonical projection
独立进展弹窗 = History 新增/编辑入口
```

### Heatmap

field identity 必须 canonical；中文 label 只展示。

---

## 9. Excel V0.2 协调

V0.1→V0.2 Excel Diff Survey 可以继续只读并行。

当前 shared form renderer blocker 是现有实现机制问题，不能用尚未 Authority 化的 V0.2 字段变化掩盖。

如果具体字段差异确属 V0.2，标记：

```text
BLOCKED_BY_V0_2_AUTHORITY
```

不得在本轮擅自修改业务字段集合。

---

## 10. 当前推进顺序

1. 新独立 Agent 更新Authority，读取首页V4及本地实施计划/报告，固定新REVIEWED_HEAD。
2. 按V4第17节核验布局/共享样式、真实金额与空间指标、路由和状态刷新；验证本轮实际受影响范围。
3. 保存指定独立报告与证据，保留历史记录；不现场修复。
4. PASS后由用户人工确认首页；FAIL进入首页修复；PARTIAL补齐具体缺项。
5. 首页V4独立及人工确认完成后，再恢复Excel V0.2等其他待办的真实进度。

---

## 11. 本地路径

Authority：

```text
D:\BattleMap\BattleMapenterprise-authority
```

更新：

```powershell
git -C "D:\BattleMap\BattleMapenterprise-authority" pull --ff-only origin enterprise-battle-map-authority
```

代码主工作树：

```text
D:\BattleMap\battle-map
```

完整独立审查报告：

```text
D:\BattleMap\battle-map\docs\enterprise\reviews\non-mox-modules-mox-reference-independent-review.md
```

当前只允许一个写 Agent 操作主工作树。

---

## 12. 文档维护规则

- 页面“长得一样”不能作为共享机制证据；
- MOX“已验证”不能作为保留私有 renderer 的理由；
- shared runtime 必须一直贯穿到 actual Vue render tree；
- 不允许任何模块 local full form builder 成为第二业务结构 Authority；
- 测试必须证明真实页面 production path 经过 shared renderer；
- 每个修复后新 HEAD 都必须完整重新审查；
- 独立审查代码事实优先于 Implementation Report 自报状态；
- 不保留长期 legacy alias/fallback/双写；
- Excel V0.2 未 Authority 化变化不得混入本轮 remediation；
- 人工视觉/交互验收由用户执行。
