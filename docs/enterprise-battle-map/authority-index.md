# 企业作战地图 Authority 文档索引

**状态：CURRENT AUTHORITY INDEX**  
**文档分支：`enterprise-battle-map-authority`**  
**长期代码分支：`feature/enterprise-battle-map`**

---

## 0. 当前先收口未提交改动并固定复核版本

用户最新补充：之前独立复核返回大量改动未提交，无法在稳定HEAD完成核验。先由实施者按 `integration/enterprise-review-snapshot-preparation-v1.md` 盘点并提交已授权企业实现，固定实际运行的候选版本；独立审查者不代提交、不边审边改。云端未读取本地完整报告和git状态，不推定原报告全部结论。
本地commit不需联网或先push。受审代码/测试及可执行依赖必须完整进入候选；Excel继续用真实路径/hash固定，报告/证据及已证明不影响运行的本地文件不要求清空或入Git。
三个迁移/DB测试仍按专项V1恢复实际完成状态；已执行历史SQL不改，真实完整链仍须验证最终结构。行业选项V1保留已授权及实际进度，不重做、不混入无关修改。稳定版本与测试通过分别记录，未关闭finding不因提交自动消失。

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
| 21 | `isp-canonical-authority-v2.md` | ISP当前字段和3-group业务基线 | 已同步字段删除及行业选项V1 |
| 22 | `power-canonical-authority-v2.md` | 电力当前字段和3-group业务基线 | 已同步字段删除及行业选项V1 |
| 23 | `large-enterprise-canonical-authority-v2.md` | 大企当前字段和3-group业务基线 | 已同步字段删除及行业选项V1 |
| 24 | `enterprise-home-canonical-authority-v4.md` | 首页间距、全局场景卡样式/数字、已下单金额实时汇总、空间拓展及双层导航；含本地实施步骤/产物 | 业务基线；当前联合独立复核 |
| 25 | `enterprise-excel-confirmed-delta-v1.md` | 删除指定分类字段、更新大企表名、对应契约和验证 | 用户报告字段删除完成；具体两项与输出待核验 |
| 26 | `remediation/enterprise-home-route-blocker-repair-v1.md` | 读取本地报告、修复真实点击链路、浏览器导航证据 | 用户报告修复完成；待独立复核 |
| 27 | `reviews/authority-consistency-audit-2026-09-07.md` | 2026-09-07文档一致性核对快照 | 历史核对；当前状态以本索引为准 |
| 28 | `reviews/enterprise-home-and-excel-delta-independent-review-v1.md` | 同一新HEAD核验首页修复、Excel增量与联合回归 | 用户报告未提交改动导致版本不稳定；先准备候选再复核 |
| 29 | `remediation/enterprise-confirmed-delta-test-expectation-alignment-v1.md` | 测试失败分类、过期预期/fixture维护及真实回归处理 | 此前修复已报告；最新迁移残留按专项V1 |
| 30 | `enterprise-industry-options-authority-v1.md` | ISP/电力/大企行业选项、共享链路和测试同步 | 已授权，完成状态待回执；与迁移测试修复分开 |
| 31 | `remediation/enterprise-migration-schema-test-alignment-v1.md` | 历史迁移不可改、版本化schema预期、完整链与物理列集合 | 已授权；恢复实际进度并纳入候选，尚无完成回执 |
| 32 | `integration/enterprise-review-snapshot-preparation-v1.md` | 盘点未提交实现、精确本地提交、隔离候选及交接 | **当前执行：先形成完整稳定的受审版本** |

---

## 2. 当前阶段判断

此前用户人工检查后提出首页布局、样式、真实金额和导航调整；后续独立审查发现跳转阻塞。2026-09-08 用户报告首页与删除字段两项均完成；后续联合审查曾报告阻塞，用户随后报告此前修复完成，但最新仍有三个迁移/DB测试失败，先处理本轮定向残留。用户最新另报告前轮复核因大量未提交改动无法固定HEAD，本轮将实际修复与本地提交/版本交接衔接，不据此推断新的功能缺陷。
这是人工检查反馈，不是云端重新核验本地代码/测试的声明。前轮报告继续作为原 HEAD 的历史证据，本轮新 HEAD 的验证另行记录。

当前：
```text
PREVIOUS_REVIEW = USER_REPORTED_NO_BLOCKERS
PREVIOUS_MANUAL_CHECK = BASICALLY_ACCEPTABLE_WITH_HOME_ISSUES
CURRENT_TASK = ENTERPRISE_REVIEW_SNAPSHOT_PREPARATION_V1
INDUSTRY_OPTIONS = AUTHORIZED_PENDING_IMPLEMENTATION
EXCEL_CONFIRMED_DELTA_V1 = IMPLEMENTED_REPORTED
HOME_ROUTE_REPAIR = IMPLEMENTED_REPORTED
HOME_V4_PREVIOUS_REVIEW = USER_REPORTED_BLOCKER
PREVIOUS_JOINT_REVIEW = USER_REPORTED_BLOCKED
PREVIOUS_POST_TEST_ALIGNMENT_REVIEW = USER_REPORTED_UNSTABLE_HEAD
REVIEW_SNAPSHOT = AUTHORIZED_PENDING_PREPARATION
UNCOMMITTED_CHANGES = USER_REPORTED_REVIEW_BLOCKER
CODE_PUSH_REQUIRED_FOR_LOCAL_REVIEW = NO
INDUSTRY_OPTIONS_REVIEW = NOT_STARTED
TEST_FAILURES = USER_REPORTED_MIGRATION_SCHEMA_RESIDUALS
TEST_ALIGNMENT = PREVIOUS_FIX_REPORTED_WITH_RESIDUALS
MIGRATION_SCHEMA_TEST_ALIGNMENT = AUTHORIZED_PENDING_IMPLEMENTATION
EXECUTED_HISTORICAL_SQL = IMMUTABLE
PRODUCTION_MIGRATION_GAP = NOT_YET_ASSESSED
EXCEL_SOURCE = USER_CONFIRMED_LOCAL_ROOT_FILE
EXCEL_GIT_TRACKING_REQUIRED = NO
SEPARATE_EXCEL_IMPLEMENTATION_REPORT_REQUIRED = NO
HOME_V4_IMPLEMENTATION = IMPLEMENTED_REPORTED
MANUAL_ACCEPTANCE_AFTER_REPAIR = PENDING
```

旧首页报告与人工检查曾发现跳转阻塞，现用户报告首页和字段删除均已完成。此前测试修复回执后又报告迁移Schema残留，尚不能关闭测试finding；行业选项及迁移专项完成状态尚未获新回执；用户已补充前轮复核存在未提交改动的版本缺口，完整结论仍以实际报告为准。具体历史结论按对应HEAD保存。既有机制保持受影响范围回归。

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
首页业务规则不变；前轮复核版本缺口先按快照准备V1处理，首页实现须真实包含于候选。迁移测试修复及行业选项按实际影响核验首页与共享消费者；旧报告不改写。

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

行业选项另有用户已确认增量 `enterprise-industry-options-authority-v1.md`，已同步三模块规范；不受下面“未确认差异”冻结限制，不改变字段总数。

两项确认增量已正式进入当前字段 Authority：仅删除“整体空间（肥肉/瘦肉/骨头）”分类字段，大企表名为“大企（油气矿、广电、交通）”。其他字段、金额、跳数及业务规则保持不变。
当前目标字段总数：MOX 40、TOB 33、ISP 24、电力27、大企25。视图字段按各 Contract 的 visibility/mode 派生；这些数字不是DB物理列数，也不表示Excel、代码或数据库已经完成迁移。历史SQL不可改与最终结构必须收敛并不矛盾，迁移测试按专项V1区分历史阶段与真实生产终态。

其他尚未确认的 V0.2 差异继续只读调查，只有这些未确认差异使用 BLOCKED_BY_V0_2_AUTHORITY。已确认两项不得再以旧冻结说明阻塞。
首页路由任务与 Excel 字段任务分别恢复本地进度、记录实现提交和证据；首页修复不因新的字段目标而被迫混入尚未实施的 Excel 改动。若 Excel 已实施，其实际受影响消费者按新契约回归。

---

## 10. 当前推进顺序

1. 更新Authority，读取最近独立报告，盘点全部暂存/未暂存及未跟踪实现，按已授权需求建立文件/必要hunk归属与依赖矩阵；不重复启动对脏工作树的完整审查。
2. 恢复三个迁移/DB测试修复及行业选项的真实进度。迁移测试尚未完成则按其专项执行；已经完成的实现不重做，已执行历史SQL不改。
3. 按快照准备V1精确暂存并本地提交已核实的企业实现、完整依赖及必要报告，保留无关工作与Excel；不要求push，不全量add，不reset/clean。
4. 固定REVIEW_CANDIDATE_HEAD与实际运行目录；原工作树其他源码可能影响核验时从候选创建隔离review worktree。记录可信验证、剩余失败、Excel路径/hash和排除文件，SNAPSHOT_READY不等于功能PASS。
5. 新独立会话按联合复核V1第9节恢复准确候选，再执行第7/8节及实际业务范围。若仍有具体缺口/有效失败，按既有授权继续对应修复，不靠提交或改预期掩盖。

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
当前只允许一个写 Agent 操作主工作树。实际独立复核目录以快照准备报告的REVIEW_WORKTREE为准；采用隔离候选时不再用主工作树旧服务证明其行为。

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
