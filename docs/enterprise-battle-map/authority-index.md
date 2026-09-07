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
| 4 | `reviews/non-mox-full-independent-review-rerun-v3.md` | 修复后新 HEAD 必须完整重跑原始 Non-MOX Independent Review；7个旧finding仅作为额外强制回归集，同时主动发现新finding | **当前下一门禁** |
| 5 | `reviews/non-mox-modules-mox-reference-independent-review-v1.md` | 原始全量 Independent Review Authority：shared runtime、Create/Edit、Customer、Progress、Heatmap、Metric、API/DB、重复机制、hidden consumers、测试可信度 | V3要求完整重新执行本文件全部范围 |
| 6 | `remediation/non-mox-alignment-independent-review-findings-remediation-v2.md` | 关闭前次独立审查发现的7个blocking findings | 已实施，等待完整全量复审 |
| 7 | `reviews/non-mox-alignment-independent-rereview-v2.md` | 仅围绕7个finding的定向复核草案 | **SUPERSEDED BY V3；不得作为独立审查边界** |
| 8 | `remediation/non-mox-modules-mox-reference-alignment-v1.md` | TOB/ISP/电力/大企全面向MOX已验证机制对齐 | 前序实施报告PASS已被初审推翻，只作背景 |
| 9 | `investigation/enterprise-excel-v0.1-v0.2-diff-survey-v1.md` | 企业作战地图基表V0.1→V0.2 Schema/Contract差异调查 | 可并行只读；业务字段变化需先Authority Review |
| 10 | `remediation/enterprise-form-options-root-cause-remediation-v2.md` | `f.options is not iterable`根因级修复 | 已实施并经用户确认Create/Edit可打开 |
| 11 | `remediation/enterprise-customer-data-fetch-unification-v2.md` | Customer SQL/customer_id贯穿修复及长期回归门禁 | 已修复，统一机制回归项 |
| 12 | `reviews/mox-end-to-end-canonical-independent-review-v1.md` | MOX端到端独立审查规范 | 最新复审PASS |
| 13 | `remediation/mox-4-group-render-chain-repair-v1.md` | MOX 4-group renderer断链修复 | 已实施并通过复审 |
| 14 | `remediation/mox-end-to-end-canonical-convergence-v1.md` | MOX端到端canonical收敛 | 已实施，作为Reference baseline |
| 15 | `investigation/enterprise-runtime-implementation-survey-v1.md` | 已完成的实际运行链调查规范 | 事实证据来源 |
| 16 | `integration/parallel-module-integration-plan-v1.md` | TOB/ISP/电力+大企合并规则 | 集成历史/回归参考 |
| 17 | `integration/local-worktree-layout-v1.md` | 本地真实worktree路径 | 本地执行必读 |
| 18 | `tob-canonical-authority-v2.md` | TOB当前字段和3-group业务基线 | 字段暂冻结，V0.2后可能升级 |
| 19 | `isp-canonical-authority-v2.md` | ISP当前字段和3-group业务基线 | 字段暂冻结，V0.2后可能升级 |
| 20 | `power-canonical-authority-v2.md` | 电力当前字段和3-group业务基线 | 字段暂冻结，V0.2后可能升级 |
| 21 | `large-enterprise-canonical-authority-v2.md` | 大企当前字段和3-group业务基线 | 字段暂冻结，V0.2后可能升级 |
| 22 | `enterprise-home-canonical-authority-v2.md` | 企业首页旧阶段设计 | DEFERRED；最后重新冻结 |

---

## 2. 当前阶段判断

Non-MOX Alignment 初次独立审查发现7个blocking finding，前序implementation report的PASS已被证明与代码事实不一致。随后已完成7-finding remediation并提交新的代码HEAD。

当前正式状态：

```text
MOX = VERIFIED REFERENCE BASELINE
TOB / ISP / POWER / LARGE = REMEDIATION IMPLEMENTED
FULL INDEPENDENT REVIEW RERUN = PENDING
VERIFIED = NO
```

重要纠正：新的代码HEAD不能只做“7个finding closure re-review”。必须把新HEAD当成新的完整审查对象，重新执行原始 `reviews/non-mox-modules-mox-reference-independent-review-v1.md` 全部范围。

---

## 3. 当前 Full Independent Review Rerun 规则

当前唯一正确审查关系：

```text
FULL ORIGINAL NON-MOX INDEPENDENT REVIEW
+
KNOWN 7 FINDINGS REGRESSION CHECK
+
NEW FINDING DISCOVERY
```

禁止缩减成：

```text
7 FINDINGS ONLY
```

必须重新从零审查：

- Field Contract / shared runtime；
- Table/Create/Edit真实Projection；
- Runtime Field View Model / Dynamic Options；
- shared modal / group renderer；
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

上一轮7个finding必须逐项恢复原ID并验证 `CLOSED=7/7`，但即使7/7关闭，只要新HEAD发现新的blocking finding，整体仍然FAIL。

---

## 4. Full Review 必须重新统计的门禁

不得沿用remediation report中的数字，必须从新HEAD重新扫描：

```text
DUPLICATE_PROJECTION_IMPLEMENTATIONS
MODULE_LOCAL_FORM_SCHEMAS
DUPLICATE_RUNTIME_FIELD_MODEL_IMPLEMENTATIONS
DUPLICATE_SECTION_RENDER_PATHS
PRIVATE_CUSTOMER_FETCH_IMPLEMENTATIONS
PROGRESS_DOUBLE_WRITE_PATHS
PROGRESS_TEXT_FALLBACK_PATHS
LABEL_IDENTITY_LOOKUPS
ACTIVE_LEGACY_KEYS
MODULE_LOCAL_METRIC_LOGIC
UNDECLARED_CANONICAL_CONSUMERS
```

目标blocking数量全部为0。

---

## 5. 7个已知Finding只是额外回归集

上一轮review的7个blocking finding必须逐项独立复核：

```text
FINDING_ID
PREVIOUS_CODE_FACT
REMEDIATION_CLAIM
CURRENT_CODE_FACT
PRODUCTION_PATH
TEST_EVIDENCE
STATIC_EVIDENCE
STATUS=CLOSED/OPEN
```

要求：

```text
KNOWN_FINDINGS_CLOSED=7/7
```

但它不是PASS的充分条件。

---

## 6. Implementation Report Integrity

完整复审必须重新将remediation report / closure matrix的每个PASS与当前代码事实核对。

出现任一：

```text
REPORT_PASS_BUT_CODE_FAIL
REPORT_ZERO_BUT_SCAN_NONZERO
REPORT_SHARED_BUT_RUNTIME_LOCAL
REPORT_CANONICAL_BUT_LABEL_LOOKUP_EXISTS
REPORT_TESTED_BUT_NOT_PRODUCTION_PATH
```

则：

```text
IMPLEMENTATION_REPORT_INTEGRITY=FAIL
```

并形成blocking finding。

---

## 7. Excel V0.2协调

V0.1→V0.2 Excel Diff Survey可继续只读并行。

本轮完整Independent Review仍以当前正式业务Authority为准。若差异明确只来自尚未Authority化的V0.2业务变化，标记：

```text
BLOCKED_BY_V0_2_AUTHORITY
```

不得在审查中修复，也不得借V0.2掩盖现有实现不一致。

---

## 8. 当前推进顺序

```text
1. 7-finding remediation已完成并commit
2. 固定新的代码HEAD
3. 新Agent执行 reviews/non-mox-full-independent-review-rerun-v3.md
4. 按V3完整重跑 reviews/non-mox-modules-mox-reference-independent-review-v1.md 全部范围
5. 同时逐项验证上一轮7个finding CLOSED=7/7
6. 主动扫描新finding
7. 只有 FULL_ORIGINAL_REVIEW_COMPLETED=YES 且 BLOCKING_FINDINGS=NONE 才PASS
8. PASS后用户逐模块人工验收
9. 完成Excel V0.2 Authority Review
10. 发布必要的新模块Canonical Authority并只实施V0.2 delta
11. 企业模块统一VERIFIED
12. 企业首页最后建设
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

独立审查报告：

```text
D:\BattleMap\battle-map\docs\enterprise\reviews\non-mox-modules-mox-reference-independent-review.md
```

7-finding Closure Matrix：

```text
D:\BattleMap\battle-map\docs\enterprise\remediations\non-mox-alignment-review-findings-closure-matrix.md
```

当前只允许新的只读Review Agent检查固定HEAD；审查期间禁止写Agent修改主工作树。

---

## 10. 文档维护规则

- 每个新HEAD都必须按当前review scope重新证明，不得继承旧HEAD的PASS；
- 7个历史finding是回归集，不是完整审查边界；
- 独立审查代码事实优先于Implementation Report自报状态；
- 业务字段和共享实现机制分开治理；
- 不保留长期legacy alias/fallback/双写；
- Production与测试必须走同一真实runtime路径；
- Implementation Agent不得自行标记finding为VERIFIED；
- Excel V0.2未Authority化变化不得混入本轮review；
- 人工视觉/交互验收由用户执行。
