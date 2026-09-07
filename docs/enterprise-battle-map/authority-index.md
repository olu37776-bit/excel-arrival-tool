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
| 3 | `mox-canonical-authority-v6.md` | MOX 41字段、4 group、Create/Edit runtime、Heatmap、legacy key、Progress、Customer、DB/测试最终目标 | 已验证 Reference baseline |
| 4 | `remediation/non-mox-shared-form-renderer-convergence-v1.md` | 完整 Independent Review 新发现：TOB/ISP/Power/Large 仍有4套 module-local form HTML builders；收敛到唯一 shared form shell/group/field renderer | **当前阻塞 remediation** |
| 5 | `reviews/non-mox-full-independent-review-rerun-v3.md` | 每个修复后新HEAD必须完整重跑原始Non-MOX Independent Review；历史finding只作为额外回归集，同时主动发现新finding | 当前 remediation 完成后的下一门禁 |
| 6 | `reviews/non-mox-modules-mox-reference-independent-review-v1.md` | 原始全量 Independent Review Authority：shared runtime、Create/Edit、Customer、Progress、Heatmap、Metric、API/DB、重复机制、hidden consumers、测试可信度 | 每个新HEAD必须完整重跑 |
| 7 | `remediation/non-mox-alignment-independent-review-findings-remediation-v2.md` | 关闭前次独立审查发现的7个blocking findings | 已实施；历史回归集 |
| 8 | `reviews/non-mox-alignment-independent-rereview-v2.md` | 仅围绕7个finding的定向复核草案 | SUPERSEDED BY V3；不得作为完整审查边界 |
| 9 | `remediation/non-mox-modules-mox-reference-alignment-v1.md` | TOB/ISP/电力/大企全面向MOX已验证机制对齐 | 前序实施报告PASS曾被独立审查推翻，只作背景 |
| 10 | `investigation/enterprise-excel-v0.1-v0.2-diff-survey-v1.md` | 企业作战地图基表V0.1→V0.2 Schema/Contract差异调查 | 可并行只读；业务字段变化需先Authority Review |
| 11 | `remediation/enterprise-form-options-root-cause-remediation-v2.md` | `f.options is not iterable`根因级修复 | 已实施并经用户确认Create/Edit可打开 |
| 12 | `remediation/enterprise-customer-data-fetch-unification-v2.md` | Customer SQL/customer_id贯穿修复及长期回归门禁 | 已修复，统一机制回归项 |
| 13 | `reviews/mox-end-to-end-canonical-independent-review-v1.md` | MOX端到端独立审查规范 | 最新复审PASS |
| 14 | `remediation/mox-4-group-render-chain-repair-v1.md` | MOX 4-group renderer断链修复 | 已实施并通过复审 |
| 15 | `remediation/mox-end-to-end-canonical-convergence-v1.md` | MOX端到端canonical收敛 | 已实施，作为Reference baseline |
| 16 | `investigation/enterprise-runtime-implementation-survey-v1.md` | 已完成的实际运行链调查规范 | 事实证据来源 |
| 17 | `integration/parallel-module-integration-plan-v1.md` | TOB/ISP/电力+大企合并规则 | 集成历史/回归参考 |
| 18 | `integration/local-worktree-layout-v1.md` | 本地真实worktree路径 | 本地执行必读 |
| 19 | `tob-canonical-authority-v2.md` | TOB当前字段和3-group业务基线 | 字段暂冻结，V0.2后可能升级 |
| 20 | `isp-canonical-authority-v2.md` | ISP当前字段和3-group业务基线 | 字段暂冻结，V0.2后可能升级 |
| 21 | `power-canonical-authority-v2.md` | 电力当前字段和3-group业务基线 | 字段暂冻结，V0.2后可能升级 |
| 22 | `large-enterprise-canonical-authority-v2.md` | 大企当前字段和3-group业务基线 | 字段暂冻结，V0.2后可能升级 |
| 23 | `enterprise-home-canonical-authority-v2.md` | 企业首页旧阶段设计 | DEFERRED；最后重新冻结 |

---

## 2. 当前阶段判断

最新完整 Non-MOX Independent Review Rerun 在修复后的新 HEAD 上继续发现 blocking finding：

```text
MODULE_LOCAL_FORM_HTML_BUILDERS = 4
```

TOB / ISP / Power / Large 当前虽然部分 shared runtime/projection 已对齐、页面视觉也可能相似，但最终 Create/Edit form HTML/render builder 仍由各模块独立实现。

因此当前正式状态：

```text
MOX = VERIFIED REFERENCE BASELINE
TOB / ISP / POWER / LARGE = NOT VERIFIED
FULL INDEPENDENT REVIEW = FAIL
CURRENT BLOCKER = MODULE-LOCAL FORM HTML BUILDERS 4x
```

这不是单纯重复代码问题，而是 shared runtime 到实际 Vue render tree 的最后一段仍存在四套独立业务结构解释器。

---

## 3. 当前 Shared Form Renderer 目标

当前唯一允许的目标链：

```text
Module Field Contract
→ shared Projection
→ shared Runtime Field View Model
→ shared Dynamic Options / Editor Registry
→ shared Form Shell
→ shared Group Renderer
→ shared Field Renderer
→ actual render tree
```

TOB / ISP / Power / Large 不得各自保留完整 form HTML builder。

模块差异只能由各自 Contract、shared editor/control registry、经过证明的最小 slot/hook 表达，不得通过整套 module-local template / section builder / field renderer switch 表达。

目标门禁：

```text
MODULE_LOCAL_FORM_HTML_BUILDERS=0
MODULE_LOCAL_SECTION_SCHEMAS=0
DUPLICATE_SECTION_RENDER_PATHS=0
DUPLICATE_FIELD_RENDERERS=0
DUPLICATE_FORM_SHELLS=0
```

---

## 4. 当前 Remediation

当前只允许实施：

```text
remediation/non-mox-shared-form-renderer-convergence-v1.md
```

实施 Agent 必须先读取最新本地完整 Independent Review report，恢复该 finding 的原始 ID、4个 builder 的真实文件/函数/template region，以及 MOX/shared verified render path。

不得根据文件名猜测，也不得简单复制 MOX 页面。

---

## 5. Full Independent Review 仍然是最终门禁

本 blocker 修复后，不能只复核 form renderer finding。

必须对新的代码 HEAD 再次完整执行：

```text
reviews/non-mox-modules-mox-reference-independent-review-v1.md
+
reviews/non-mox-full-independent-review-rerun-v3.md
```

完整重新审查：

- Field Contract / shared runtime；
- Table/Create/Edit真实Projection；
- Runtime Field View Model / Dynamic Options；
- shared form shell / group renderer / field renderer；
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
- tests是否覆盖真实Production path；
- MOX regression；
- full tests/build。

历史7个finding继续作为强制回归集，但不是完整审查边界。

---

## 6. 长期统一规则继续有效

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

### Group

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

---

## 7. Excel V0.2 协调

V0.1→V0.2 Excel Diff Survey 可以继续只读并行。

当前 shared form renderer blocker 是现有实现机制问题，不能用尚未 Authority 化的 V0.2 字段变化掩盖。

如具体字段差异确属 V0.2，标记：

```text
BLOCKED_BY_V0_2_AUTHORITY
```

不得在本轮擅自修改业务字段集合。

---

## 8. 当前推进顺序

```text
1. 读取最新完整Independent Review report
2. 执行 non-mox-shared-form-renderer-convergence-v1.md
3. 将4套module-local form HTML builders收敛为0
4. 本地commit新HEAD
5. 新Agent完整重跑Non-MOX Independent Review V1 + Full Rerun V3
6. 主动发现新finding
7. 只有BLOCKING_FINDINGS=NONE才进入用户人工验收
8. 完成Excel V0.2 Authority Review
9. 发布必要的新模块Canonical Authority并只实施V0.2 delta
10. 企业模块统一VERIFIED
11. 企业首页最后建设
```

---

## 9. 本地路径

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

## 10. 文档维护规则

- 页面“长得一样”不能作为共享机制证据；
- shared runtime 必须一直贯穿到 actual render tree；
- 不允许 module-local full form builder 成为第二业务结构 Authority；
- 每个修复后新HEAD都必须完整重新审查；
- 独立审查代码事实优先于Implementation Report自报状态；
- 不保留长期legacy alias/fallback/双写；
- Production与测试必须走同一真实runtime路径；
- Excel V0.2未Authority化变化不得混入本轮remediation；
- 人工视觉/交互验收由用户执行。
