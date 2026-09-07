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
| 4 | `reviews/non-mox-alignment-independent-rereview-v2.md` | 对 7 个 blocking finding remediation 后新 HEAD 做逐项 closure re-review，并验证实施报告与代码事实一致 | **当前下一门禁** |
| 5 | `remediation/non-mox-alignment-independent-review-findings-remediation-v2.md` | 关闭前次独立审查发现的 7 个 blocking findings | 已实施，等待独立复审 |
| 6 | `reviews/non-mox-modules-mox-reference-independent-review-v1.md` | TOB/ISP/电力/大企 alignment 初次固定 HEAD 独立审查 | 初审 FAIL / 7 blockers，作为前置证据 |
| 7 | `remediation/non-mox-modules-mox-reference-alignment-v1.md` | TOB/ISP/电力/大企全面向 MOX 已验证机制对齐 | 前序实施报告 PASS 已被初审推翻，只作背景 |
| 8 | `investigation/enterprise-excel-v0.1-v0.2-diff-survey-v1.md` | 企业作战地图基表 V0.1→V0.2 Schema/Contract 差异调查 | 可并行只读；业务字段变化需先 Authority Review |
| 9 | `remediation/enterprise-form-options-root-cause-remediation-v2.md` | `f.options is not iterable` 根因级修复 | 已实施并经用户确认 Create/Edit 可打开 |
| 10 | `remediation/enterprise-customer-data-fetch-unification-v2.md` | Customer SQL/customer_id 贯穿修复及长期回归门禁 | 已修复，统一机制回归项 |
| 11 | `reviews/mox-end-to-end-canonical-independent-review-v1.md` | MOX 端到端独立审查规范 | 最新复审 PASS |
| 12 | `remediation/mox-4-group-render-chain-repair-v1.md` | MOX 4-group renderer 断链修复 | 已实施并通过复审 |
| 13 | `remediation/mox-end-to-end-canonical-convergence-v1.md` | MOX 端到端 canonical 收敛 | 已实施，作为 Reference baseline |
| 14 | `investigation/enterprise-runtime-implementation-survey-v1.md` | 已完成的实际运行链调查规范 | 事实证据来源 |
| 15 | `integration/parallel-module-integration-plan-v1.md` | TOB/ISP/电力+大企合并规则 | 集成历史/回归参考 |
| 16 | `integration/local-worktree-layout-v1.md` | 本地真实 worktree 路径 | 本地执行必读 |
| 17 | `tob-canonical-authority-v2.md` | TOB 当前字段和3-group业务基线 | 字段暂冻结，V0.2后可能升级 |
| 18 | `isp-canonical-authority-v2.md` | ISP 当前字段和3-group业务基线 | 字段暂冻结，V0.2后可能升级 |
| 19 | `power-canonical-authority-v2.md` | 电力当前字段和3-group业务基线 | 字段暂冻结，V0.2后可能升级 |
| 20 | `large-enterprise-canonical-authority-v2.md` | 大企当前字段和3-group业务基线 | 字段暂冻结，V0.2后可能升级 |
| 21 | `enterprise-home-canonical-authority-v2.md` | 企业首页旧阶段设计 | DEFERRED；最后重新冻结 |

---

## 2. 当前阶段判断

Non-MOX Alignment 初次独立审查发现 7 个 blocking finding，前序 implementation report 的 PASS 已被证明与代码事实不一致。随后已按：

```text
remediation/non-mox-alignment-independent-review-findings-remediation-v2.md
```

完成 remediation 并提交新的代码 HEAD。

当前正式状态：

```text
MOX = VERIFIED REFERENCE BASELINE
TOB / ISP / POWER / LARGE = 7-FINDING REMEDIATION IMPLEMENTED
INDEPENDENT RE-REVIEW = PENDING
VERIFIED = NO
```

Implementation Agent 只能声明 IMPLEMENTED；只有新的固定 HEAD Independent Re-Review 可以关闭 finding 并宣布 PASS。

---

## 3. 当前 Re-Review 唯一目标

新的独立审查必须读取上一轮 review、7-finding Closure Matrix、remediation report 和当前真实代码，并逐项复核 7 个 finding。

完成标准：

```text
7_FINDINGS_CLOSED=7/7
SHARED_RUNTIME_ALL_4=PASS
LOCAL_DUPLICATE_PROJECTIONS=0
DUPLICATE_SECTION_RENDER_PATHS=0
HEATMAP_LABEL_IDENTITY=0
WRONG_GROUP_NAMES=0
IMPLEMENTATION_REPORT_INTEGRITY=PASS
ACTIVE_LEGACY_KEYS=0
UNDECLARED_CONSUMERS=0
MOX_REGRESSION=PASS
FULL_TESTS=PASS
BUILD=PASS
```

任一 finding 仍 OPEN，则整体 FAIL。

---

## 4. 已知关键 Findings 回归门禁

### Shared Runtime

TOB / ISP / Power / Large 必须全部走同一 shared projection/runtime mechanism，不能只有 TOB 使用 shared `field-projections.js` 而其他模块保留本地实现。

### Heatmap

Power 等模块 Heatmap 的字段 identity 必须使用 canonical key；例如不得继续：

```text
valueField="26年空间（跳）"
```

应使用：

```text
space2026Hops
```

### Group

TOB / ISP / Power / Large Create/Edit 顶层 group 必须精确为：

```text
客户信息
业务格局
作战情况
```

不得残留“业务信息”及 alias/fallback。

### Renderer

唯一允许的主链：

```text
Field Contract.group
→ shared runtime grouping
→ shared Create/Edit group renderer
```

module-local section schema / duplicate renderer 必须归零。

其余 3 个 finding 必须继续按上一轮独立审查原 finding ID 和代码事实复核，不得概括省略。

---

## 5. 报告真实性门禁

本轮必须把 remediation report 的每项 PASS 与代码和 production path 对照。

如出现：

```text
REPORT_PASS_BUT_CODE_FAIL
REPORT_ZERO_BUT_SCAN_NONZERO
REPORT_SHARED_BUT_RUNTIME_LOCAL
REPORT_CANONICAL_BUT_LABEL_LOOKUP_EXISTS
```

则：

```text
IMPLEMENTATION_REPORT_INTEGRITY=FAIL
```

整体审查 FAIL。

---

## 6. 长期统一规则

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

当前 re-review 判断的是现有 Authority 下的实现机制是否真正收敛。尚未 Authority 化的 V0.2 字段新增/删除/改名/group/option-set/语义变化不得混入本轮修复。

如确实依赖 V0.2，标记：

```text
BLOCKED_BY_V0_2_AUTHORITY
```

---

## 8. 当前推进顺序

```text
1. 7-finding remediation 已完成并commit
2. 固定新的代码 HEAD
3. 新 Agent 执行 reviews/non-mox-alignment-independent-rereview-v2.md
4. FINDINGS_CLOSED 必须 7/7 且 BLOCKING_FINDINGS=NONE
5. 如 FAIL → 只修 OPEN findings → 再复审
6. 如 PASS → 用户逐模块人工验收
7. 完成 Excel V0.2 Authority Review
8. 发布必要的新模块 Canonical Authority并只实施V0.2 delta
9. 企业模块统一 VERIFIED
10. 企业首页最后建设
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

初次独立审查报告：

```text
D:\BattleMap\battle-map\docs\enterprise\reviews\non-mox-modules-mox-reference-independent-review.md
```

7-finding Closure Matrix：

```text
D:\BattleMap\battle-map\docs\enterprise\remediations\non-mox-alignment-review-findings-closure-matrix.md
```

当前只允许新的只读 Review Agent 检查固定 HEAD；审查期间禁止写 Agent 修改主工作树。

---

## 10. 文档维护规则

- 独立审查代码事实优先于 Implementation Report 自报状态；
- 业务字段和共享实现机制分开治理；
- 不保留长期 legacy alias/fallback/双写；
- Production 与测试必须走同一真实 runtime 路径；
- Implementation Report 每个 PASS 必须有 file/function + test/static evidence；
- Implementation Agent 不得自行标记 finding 为 VERIFIED；
- Excel V0.2 未 Authority 化变化不得混入本轮 re-review；
- 人工视觉/交互验收由用户执行。
