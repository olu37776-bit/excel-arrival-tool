# 企业作战地图 Authority 文档索引

**状态：CURRENT AUTHORITY INDEX**  
**文档分支：`enterprise-battle-map-authority`**  
**长期代码分支：`feature/enterprise-battle-map`**

---

## 0. 当前测试残留修复与本地 Excel 直接核验

用户报告联合审查已结束且阻塞，摘要包括测试残留、Excel 实施报告缺失及无法验证工作簿修改。云端未读取具体报告，不虚构 finding ID 或测试明细。
用户已明确：工作簿不需要进 Git，表就在本地根目录。当前直接读取根目录实际 Excel 核对，独立 Excel 实施报告不是检查前置；不能因文件未跟踪或缺少该报告而直接判定无法验证。
执行 remediation/enterprise-confirmed-delta-test-expectation-alignment-v1.md，读取本地审查报告，修正测试残留，并把实际工作簿路径/hash、sheet/字段核对结果写入本轮已有报告。修复后再按联合独立复核 V1 复核新 HEAD。
只删除指定分类字段、大企增加交通、其他字段和业务规则保留的范围不变；工作簿未读取前不能称已验证，真实内容不符仍须如实记录。

## 1. 当前正式 Authority

| 顺序 | 文档 | 用途 | 当前门禁 |
|---:|---|---|---|
| 1 | `enterprise-contract-architecture-v5.md` | 端到端 canonical identity、真实 Runtime Projection、API canonical-only、Customer 主键贯穿、Heatmap canonical key、Progress 单一事实源、DB/Conformance Gate | 所有企业任务必读 |
| 2 | `architecture/enterprise-runtime-field-options-contract-v1.md` | Runtime Field View Model、select/options 判定、动态 options 生命周期、错误边界与五模块回归门禁 | 长期 Runtime Options Authority |
| 3 | `mox-canonical-authority-v6.md` | MOX 40字段、4 group、Create/Edit runtime、Heatmap、legacy key、Progress、Customer、DB/测试最终目标 | 历史已验证机制 Reference；字段增量待本地证据 |
| 3b | `remediation/tob-shared-form-production-path-repair-v1.md` | 修复 TOB 本地完整表单构建器，迁入真实共享 Create/Edit 渲染链，补强漏检门禁 | 用户报告修复及后续检查完成；保留回归 |
| 3a | `remediation/five-module-shared-operation-convergence-v1.md` | 根据最新本地审查报告，对其他操作建立五模块生产路径清单，收敛重复机制并修复阻塞 | 历史实施基线；保留回归 |
| 4 | `remediation/five-module-shared-form-renderer-convergence-v3.md` | 验证 MOX 是否也存在 local form builder；从 MOX 已验证行为提炼唯一 shared form renderer，并让 MOX/TOB/ISP/Power/Large 全部消费同一真实生产 render path | 已报告实施；当前修复须回归 |
| 5 | `remediation/non-mox-shared-form-renderer-convergence-v1.md` | 仅针对 4x non-MOX module-local form builders 的第一版方案 | **SUPERSEDED BY FIVE-MODULE V3** |
| 6 | `reviews/non-mox-full-independent-review-rerun-v3.md` | 固定新 HEAD，完整重跑原始审查；覆盖五模块真实渲染链、全部历史 findings 和新增问题 | 既有五模块机制审查与回归基线 |
| 7 | `reviews/non-mox-modules-mox-reference-independent-review-v1.md` | 原始全量 Independent Review Authority：shared runtime、Create/Edit、Customer、Progress、Heatmap、Metric、API/DB、重复机制、hidden consumers、测试可信度 | 五模块机制修复的完整审查基线；首页按专属范围 |
| 8 | `remediation/non-mox-alignment-independent-review-findings-remediation-v2.md` | 关闭前次独立审查 7 个 blocking findings | 已实施；历史回归集 |
| 9 | `reviews/non-mox-alignment-independent-rereview-v2.md` | 仅围绕7个finding的定向复核草案 | SUPERSEDED BY V3 |
| 10 | `remediation/non-mox-modules-mox-reference-alignment-v1.md` | TOB/ISP/电力/大企全面向MOX已验证机制对齐 | 历史实施背景；其 PASS 曾被独立审查推翻 |
| 11 | `investigation/enterprise-excel-v0.1-v0.2-diff-survey-v1.md` | 企业作战地图基表V0.1→V0.2 Schema/Contract差异调查 | 只读调查；两项已确认增量按专属文档实施 |
| 12 | `remediation/enterprise-form-options-root-cause-remediation-v2.md` | `f.options is not iterable` 根因级修复 | 已实施并经用户确认Create/Edit可打开 |
| 13 | `remediation/enterprise-customer-data-fetch-unification-v2.md` | Customer SQL/customer_id贯穿修复及长期回归门禁 | 已修复，统一机制回归项 |
| 14 | `reviews/mox-end-to-end-canonical-independent-review-v1.md` | MOX端到端独立审查规范 | 历史复审PASS；不代表新增字段变更已验证 |
| 15 | `remediation/mox-4-group-render-chain-repair-v1.md` | MOX 4-group renderer断链修复 | 已实施并通过复审 |
| 16 | `remediation/mox-end-to-end-canonical-convergence-v1.md` | MOX端到端canonical收敛 | 已实施，作为行为 Reference baseline |
| 17 | `investigation/enterprise-runtime-implementation-survey-v1.md` | 已完成的实际运行链调查规范 | 事实证据来源 |
| 18 | `integration/parallel-module-integration-plan-v1.md` | TOB/ISP/电力+大企合并规则 | 集成历史/回归参考 |
| 19 | `integration/local-worktree-layout-v1.md` | 本地真实worktree路径 | 本地执行必读 |
| 20 | `tob-canonical-authority-v2.md` | TOB当前字段和3-group业务基线 | 已同步两项确认增量；其他字段不变 |
| 21 | `isp-canonical-authority-v2.md` | ISP当前字段和3-group业务基线 | 已同步两项确认增量；其他字段不变 |
| 22 | `power-canonical-authority-v2.md` | 电力当前字段和3-group业务基线 | 已同步两项确认增量；其他字段不变 |
| 23 | `large-enterprise-canonical-authority-v2.md` | 大企当前字段和3-group业务基线 | 已同步两项确认增量；其他字段不变 |
| 24 | `enterprise-home-canonical-authority-v4.md` | 首页间距、全局场景卡样式/数字、已下单金额实时汇总、空间拓展及双层导航；含本地实施步骤/产物 | 业务基线；当前联合独立复核 |
| 25 | `enterprise-excel-confirmed-delta-v1.md` | 删除指定分类字段、更新大企表名、对应契约和验证 | 用户报告字段删除完成；具体两项与输出待核验 |
| 26 | `remediation/enterprise-home-route-blocker-repair-v1.md` | 读取本地报告、修复真实点击链路、浏览器导航证据 | 用户报告修复完成；待独立复核 |
| 27 | `reviews/authority-consistency-audit-2026-09-07.md` | 2026-09-07文档一致性核对快照 | 历史核对；当前状态以本索引为准 |
| 28 | `reviews/enterprise-home-and-excel-delta-independent-review-v1.md` | 同一新HEAD核验首页修复、Excel增量与联合回归 | 修复后复核基线；已按根目录工作簿澄清证据要求 |
| 29 | `remediation/enterprise-confirmed-delta-test-expectation-alignment-v1.md` | 测试失败分类、过期预期/fixture维护及真实回归处理 | **当前执行：测试残留修复及根目录工作簿直接核对** |

---

## 2. 当前阶段判断

此前用户人工检查后提出首页布局、样式、真实金额和导航调整；后续独立审查发现跳转阻塞。2026-09-08 用户报告首页与删除字段两项均完成；后续联合审查已报告阻塞，现进入测试残留修复与根目录工作簿实物核对。
这是人工检查反馈，不是云端重新核验本地代码/测试的声明。前轮报告继续作为原 HEAD 的历史证据，本轮新 HEAD 的验证另行记录。

当前：
```text
PREVIOUS_REVIEW = USER_REPORTED_NO_BLOCKERS
PREVIOUS_MANUAL_CHECK = BASICALLY_ACCEPTABLE_WITH_HOME_ISSUES
CURRENT_TASK = TEST_ALIGNMENT_AND_LOCAL_WORKBOOK_VERIFICATION
EXCEL_CONFIRMED_DELTA_V1 = IMPLEMENTED_REPORTED
HOME_ROUTE_REPAIR = IMPLEMENTED_REPORTED
HOME_V4_PREVIOUS_REVIEW = USER_REPORTED_BLOCKER
CURRENT_INDEPENDENT_REVIEW = USER_REPORTED_BLOCKED
TEST_FAILURES = USER_REPORTED_RESIDUALS_PENDING_LOCAL_DETAIL
TEST_ALIGNMENT = CURRENT_AUTHORIZED_IMPLEMENTATION
EXCEL_SOURCE = USER_CONFIRMED_LOCAL_ROOT_FILE
EXCEL_GIT_TRACKING_REQUIRED = NO
SEPARATE_EXCEL_IMPLEMENTATION_REPORT_REQUIRED = NO
HOME_V4_IMPLEMENTATION = IMPLEMENTED_REPORTED
MANUAL_ACCEPTANCE_AFTER_REPAIR = PENDING
```

旧首页报告与人工检查曾发现跳转阻塞，现用户报告首页和字段删除均已完成。本轮先按测试预期对齐 V1 处理报告残留，再以新 HEAD 和本地实物确认旧 findings 的处置；其他检查不因用户简短回执自动 PASS。既有机制保持受影响范围回归。

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
当前先处理联合报告中的测试残留并核对本地 Excel，再按联合独立复核 V1 复核新 HEAD；旧首页 findings 和实施基线保留。

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

两项确认增量已正式进入当前字段 Authority：仅删除“整体空间（肥肉/瘦肉/骨头）”分类字段，大企表名为“大企（油气矿、广电、交通）”。其他字段、金额、跳数及业务规则保持不变。
当前目标字段总数：MOX 40、TOB 33、ISP 24、电力27、大企25。视图字段按各 Contract 的 visibility/mode 派生；这些数字不表示 Excel、代码或数据库已经完成迁移。

其他尚未确认的 V0.2 差异继续只读调查，只有这些未确认差异使用 BLOCKED_BY_V0_2_AUTHORITY。已确认两项不得再以旧冻结说明阻塞。
首页路由任务与 Excel 字段任务分别恢复本地进度、记录实现提交和证据；首页修复不因新的字段目标而被迫混入尚未实施的 Excel 改动。若 Excel 已实施，其实际受影响消费者按新契约回归。

---

## 10. 当前推进顺序

1. 更新 Authority，读取已完成的联合审查报告与测试日志，恢复实际 findings。
2. 直接定位根目录 Excel，读取实际内容；未入 Git、缺少独立 Excel 实施报告均不是自动阻塞。
3. 按测试预期对齐 V1 修正真实过期测试/fixture；有效断言失败则修复真实回归，不放宽测试掩盖问题。
4. 在指定实施报告记录失败处置、工作簿实物核对及验证结果，保留旧独立报告。
5. 固定新 HEAD 独立复核，基于实物和新证据重新评估旧 finding；通过后人工验收。

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

当前联合独立审查报告：

```text
D:\BattleMap\battle-map\docs\enterprise\reviews\enterprise-home-and-excel-delta-independent-review.md
```

旧首页独立审查报告（保留 findings 来源）：

```text
D:\BattleMap\battle-map\docs\enterprise\reviews\enterprise-home-v4-independent-review.md
```

既有五模块完整独立审查报告：

```text
D:\BattleMap\battle-map\docs\enterprise\reviews\non-mox-modules-mox-reference-independent-review.md
```

根目录 Excel 定位：先检查 D:\BattleMap\battle-map 的根目录；如项目实际资料根为既有 D:\BattleMap，也检查该目录的直属 Excel 文件。使用文件系统枚举，包括 ignored/untracked 文件，不能仅用 git ls-files。记录最终真实路径及 SHA-256，工作簿保持在本地。
当前只允许一个写 Agent 操作主工作树。

---

## 12. 文档维护规则

- 页面“长得一样”不能作为共享机制证据；
- MOX“已验证”不能作为保留私有 renderer 的理由；
- shared runtime 必须一直贯穿到 actual Vue render tree；
- 不允许任何模块 local full form builder 成为第二业务结构 Authority；
- 测试必须证明真实页面 production path 经过 shared renderer；
- 每个修复后新 HEAD 都必须重新证明本次范围；五模块机制修复走第7节完整审查，首页/Excel任务按其专属验证与真实影响复核；
- 独立审查代码事实优先于 Implementation Report 自报状态；
- 不保留长期 legacy alias/fallback/双写；
- Excel V0.2 未 Authority 化变化不得混入本轮 remediation；
- 人工视觉/交互验收由用户执行。

## 13. 文档一致性维护

当前阶段与用户回执状态集中维护在本索引；模块规范描述最终目标，执行规范描述 WRITE_SCOPE 与步骤，本地报告描述对应 HEAD 的事实。三者不能互相替代。
每次需求变更须同步：索引、相关字段表/枚举/order/数量、共享架构引用、Sheet 名称、消费者与验证断言、执行计划及报告入口。不得只在新文档顶部增加覆盖声明而让当前字段表继续自相矛盾。
历史版本与已执行报告保留，旧数量和旧名称仅在明确的历史语境有效；已有 PASS 不延伸到新 HEAD 或新业务目标。本轮核对记录见 reviews/authority-consistency-audit-2026-09-07.md。
