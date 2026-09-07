# 企业作战地图 Authority 文档索引

**状态：CURRENT AUTHORITY INDEX**  
**文档分支：`enterprise-battle-map-authority`**  
**长期代码分支：`feature/enterprise-battle-map`**

---

## 1. 当前正式 Authority

| 顺序 | 文档 | 用途 | 当前门禁 |
|---:|---|---|---|
| 1 | `enterprise-contract-architecture-v5.md` | 端到端 canonical identity、真实 Runtime Projection、API canonical-only、Customer 主键贯穿、Heatmap canonical key、Progress 单一事实源、DB/Conformance Gate | 所有企业任务必读 |
| 2 | `architecture/enterprise-runtime-field-options-contract-v1.md` | Runtime Field View Model、select/options 判定、动态 options 生命周期、错误边界与五模块回归门禁 | 长期 Runtime Options Authority |
| 3 | `mox-canonical-authority-v6.md` | MOX 41字段、4 group、Create/Edit runtime、Heatmap、legacy key、Progress、Customer、DB/测试最终目标 | 已验证业务 Reference baseline |
| 4 | `remediation/five-module-shared-form-renderer-convergence-v3.md` | 验证 MOX 是否也存在 local form builder；从 MOX 已验证行为提炼唯一 shared form renderer，并让 MOX/TOB/ISP/Power/Large 全部消费同一真实生产 render path | 用户报告已实施；待独立核验 |
| 5 | `remediation/non-mox-shared-form-renderer-convergence-v1.md` | 仅针对 4x non-MOX module-local form builders 的第一版方案 | **SUPERSEDED BY FIVE-MODULE V3** |
| 6 | `reviews/non-mox-full-independent-review-rerun-v3.md` | 固定新 HEAD，完整重跑原始审查；覆盖五模块真实渲染链、全部历史 findings 和新增问题 | **当前执行门禁：五模块完整独立审查** |
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
| 24 | `enterprise-home-canonical-authority-v2.md` | 企业首页旧阶段设计 | DEFERRED；最后重新冻结 |

---

## 2. 当前阶段判断

修复前的完整 Independent Review 曾确认：TOB / ISP / Power / Large 仍存在 4 套 module-local form HTML builders。它们可能共享部分 Contract、Projection 和 Runtime Field，但最终 Create/Edit Vue render tree 仍由模块本地 builder 解释。

同时，`4x` finding 只证明四个 non-MOX builder 存在，**不能证明 MOX 自己已经是 shared form renderer consumer**。

2026-09-07 用户报告 Five-Module Shared Form Renderer Convergence V3 已完成。当前会话尚未读取本地实施报告/代码，不能把用户完成回执升级为独立 VERIFIED。当前状态：

```text
MOX = VERIFIED BUSINESS/BEHAVIOR REFERENCE
V3 IMPLEMENTATION = IMPLEMENTED_REPORTED
FIVE-MODULE FORM RENDERER SHARING = PENDING_INDEPENDENT_REVIEW
CURRENT_GATE = FULL_INDEPENDENT_REVIEW_RERUN_V3
```

MOX 的“已验证”表示其行为/字段/端到端结果可作为提炼 shared renderer 的参考，不表示 MOX 可以永久保留一套私有 form builder。

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

## 6. 本轮实施基线与当前审查

本轮实施依据：

```text
remediation/five-module-shared-form-renderer-convergence-v3.md
```

Five-Module V3 取代 V2 的执行规范，V2 仅保留设计背景；Non-MOX V1 不再是当前执行入口。

用户报告 V3 已实施完成。下一步读取本地 `docs/enterprise/remediations/five-module-shared-form-renderer-convergence-report-v3.md`，按 `reviews/non-mox-full-independent-review-rerun-v3.md` 完整执行独立审查；审查中不实施修复。

---

## 7. 完整 Independent Review 仍是最终门禁

本 blocker 修复后，不能只复核 form renderer finding。

新的代码 HEAD 必须完整执行：

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

1. 更新 Authority 镜像，记录 AUTHORITY_HEAD。
2. 读取 V3 实施报告、历史完整审查与全部 finding；核对本地分支、干净工作树、无并发写入并固定 REVIEWED_HEAD。
3. 独立执行原始 Review V1 全部审查域 + Full Rerun V3 的五模块当前门禁。
4. 核实五模块真实 Create/Edit render tree、全部历史 finding 关闭情况，主动发现新问题；重跑必要测试/build。
5. 保留旧报告，在固定路径写完整新报告、原始证据和简短回执。
6. FAIL：进入有证据的 remediation；PARTIAL：补足未完成验证；不直接人工验收。
7. PASS 且无 blocking finding：进入用户人工视觉/交互验收。
8. 完成 Excel V0.2 Authority Review，必要时发布新模块 Canonical Authority，只实施 V0.2 delta。
9. 企业模块统一验证与人工验收完成后，再建设企业首页。

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
