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
| 3 | `mox-canonical-authority-v6.md` | MOX 41字段、4 group、Create/Edit runtime、Heatmap、legacy key、Progress、Customer、DB/测试最终目标 | 当前已验证参考实现业务 Authority |
| 4 | `reviews/non-mox-modules-mox-reference-independent-review-v1.md` | TOB/ISP/电力/大企对齐后的固定HEAD独立审查：shared runtime、Create/Edit、Customer、Progress、Heatmap、Metric、API/DB、重复机制和隐藏消费者 | **当前下一门禁** |
| 5 | `remediation/non-mox-modules-mox-reference-alignment-v1.md` | TOB/ISP/电力/大企全面向 MOX 已验证机制对齐 | 已实施，作为独立审查基线 |
| 6 | `investigation/enterprise-excel-v0.1-v0.2-diff-survey-v1.md` | 企业作战地图基表 V0.1→V0.2 Schema/Contract 差异调查 | 可并行只读；业务字段变化需先 Authority Review |
| 7 | `remediation/enterprise-form-options-root-cause-remediation-v2.md` | `f.options is not iterable` 根因级修复 | 已实施并经用户确认 Create/Edit 可打开 |
| 8 | `remediation/enterprise-form-options-and-group-spacing-remediation-v1.md` | options runtime 与共享 group 视觉间距第一轮修复 | options部分被V2取代；spacing为历史/回归参考 |
| 9 | `remediation/enterprise-customer-data-fetch-unification-v2.md` | Customer SQL/customer_id 贯穿修复及长期回归门禁 | 已修复，统一机制回归项 |
| 10 | `reviews/mox-end-to-end-canonical-independent-review-v1.md` | MOX 端到端独立审查规范 | 最新复审 PASS |
| 11 | `remediation/mox-4-group-render-chain-repair-v1.md` | MOX 4-group renderer 断链修复 | 已实施并通过复审 |
| 12 | `remediation/mox-end-to-end-canonical-convergence-v1.md` | MOX 端到端 canonical 收敛 | 已实施，作为 Reference baseline |
| 13 | `investigation/enterprise-runtime-implementation-survey-v1.md` | 已完成的实际运行链调查规范 | 事实证据来源 |
| 14 | `integration/parallel-module-integration-plan-v1.md` | TOB/ISP/电力+大企合并规则 | 集成历史/回归参考 |
| 15 | `integration/local-worktree-layout-v1.md` | 本地真实 worktree 路径 | 本地执行必读 |
| 16 | `tob-canonical-authority-v2.md` | TOB 当前字段和3-group业务基线 | 字段暂冻结，V0.2后可能升级 |
| 17 | `isp-canonical-authority-v2.md` | ISP 当前字段和3-group业务基线 | 字段暂冻结，V0.2后可能升级 |
| 18 | `power-canonical-authority-v2.md` | 电力当前字段和3-group业务基线 | 字段暂冻结，V0.2后可能升级 |
| 19 | `large-enterprise-canonical-authority-v2.md` | 大企当前字段和3-group业务基线 | 字段暂冻结，V0.2后可能升级 |
| 20 | `enterprise-home-canonical-authority-v2.md` | 企业首页旧阶段设计 | DEFERRED；最后重新冻结 |

---

## 2. 当前阶段判断

TOB / ISP / 电力 / 大企向 MOX Reference Implementation 的机制对齐已经完成并提交。

当前状态：

```text
MOX = VERIFIED REFERENCE CANDIDATE
TOB / ISP / POWER / LARGE = ALIGNMENT IMPLEMENTED / INDEPENDENT REVIEW PENDING
```

因此当前禁止继续无审查地修改 shared runtime。下一门禁是对本次 alignment commit 做固定 HEAD 的只读独立审查。

---

## 3. 当前独立审查目标

独立审查不是只确认页面能打开，而是重新证明四模块真正共享 MOX 已验证机制：

```text
Field Contract machinery
Runtime Projection
Runtime Field View Model
Dynamic Options Provider
Create/Edit shell + group renderer
Customer relation
Progress History + popup
Metric execution
Heatmap canonical adapter
API canonical-only mapping
Persistence mapping / DB conformance
Tests / hidden-consumer gates
```

必须特别检查：

```text
DUPLICATE_PROJECTION_IMPLEMENTATIONS
MODULE_LOCAL_FORM_SCHEMAS
PRIVATE_CUSTOMER_FETCH_IMPLEMENTATIONS
PROGRESS_DOUBLE_WRITE_PATHS
LABEL_IDENTITY_LOOKUPS
ACTIVE_LEGACY_KEYS
MODULE_LOCAL_METRIC_LOGIC
UNDECLARED_CANONICAL_CONSUMERS
```

目标 blocking 数量为 0。

四模块仍使用自己的业务 Field Contract，不复制 MOX 字段；正确 group 均为：

```text
客户信息
业务格局
作战情况
```

---

## 4. `f.options` 根因已闭合

已确认根因：

```text
fieldDef.type = 'select'
f.type = undefined
runtime错误检查f.type
→ select字段未初始化options
→ f.options undefined
→ renderer TypeError
```

受影响：region / representativeOffice / country / customerName。

Customer API=PASS。

长期要求：Field Contract / fieldDef 是静态字段 metadata 唯一 Authority，Runtime Field View Model 不得自行形成第二份 type/control/editor schema。

---

## 5. Customer / Progress / Heatmap 当前统一规则

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

所有 field identity 使用 canonical key；中文 label 仅展示。

---

## 6. Excel V0.2 与当前独立审查协调

V0.1→V0.2 Excel Diff Survey 可以与本轮独立审查并行。

本轮独立审查判断的是**机制是否对齐**，不是提前实施 V0.2 业务字段变化。

如果审查发现差异明显来自 V0.2 尚未 Authority 化的：

```text
field added/removed/renamed
group changed
option-set changed
semantic changed
```

标记：

```text
BLOCKED_BY_V0_2_AUTHORITY
```

不得在审查中修复或自行解释。

---

## 7. 当前推进顺序

```text
1. alignment implementation 已完成并commit
2. 固定当前代码HEAD
3. 执行 reviews/non-mox-modules-mox-reference-independent-review-v1.md
4. 同时完成 Excel V0.1→V0.2 Diff Survey（只读）
5. 若独立审查 FAIL → 仅修 blocking implementation/test findings → 复审
6. 若独立审查 PASS → 用户逐模块人工验收
7. 对 Excel V0.2 结果做 Authority Review
8. 如 V0.2 有业务字段变化，发布 TOB/ISP/Power/Large 新 Canonical Authority 并实施 delta
9. 最终企业模块统一审查 / VERIFIED
10. 企业首页最后建设
```

---

## 8. 当前本地路径

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

其他历史 worktree：

```text
D:\BattleMap\tob-worktree
D:\BattleMap\battle-map-isp
D:\BattleMap\power-large-task
```

当前独立审查必须只针对主工作树固定 `REVIEWED_HEAD`，审查期间禁止任何写 Agent 修改该 worktree。

---

## 9. 已被取代/历史参考

与当前版本冲突时不再作为 Authority：

- `enterprise-contract-architecture-v1.md` ~ `v4.md`
- `mox-canonical-authority-v3.md` ~ `v5.md`
- `remediation/mox-post-manual-review-remediation-v1.md`
- `remediation/mox-post-manual-review-remediation-v2.md`
- `remediation/enterprise-customer-data-fetch-unification-v1.md`
- `remediation/enterprise-form-options-and-group-spacing-remediation-v1.md` 中与 V2 options 根因冲突的部分
- TOB/ISP/Power/Large V2 中引用旧 shared architecture 的实现机制说明，以 `enterprise-contract-architecture-v5.md` + `non-mox-modules-mox-reference-alignment-v1.md` 为准；其业务字段集合继续有效直到 V0.2 Authority Review 发布新版本。

---

## 10. 文档维护规则

- 业务字段和共享实现机制分开治理；
- 模块业务字段由各自 Canonical Authority 管理；
- 共享 mechanism 由当前 shared architecture + reference alignment 管理；
- Runtime View Model 不得重新创造静态 Field metadata Authority；
- 不保留长期 legacy alias/fallback/双写；
- 每次实现必须有真实 Production-path test；
- 独立审查必须固定 HEAD，只读执行；
- 人工视觉/交互验收由用户执行；
- 不确定的 V0.2 业务变化必须标记 `BLOCKED_BY_V0_2_AUTHORITY`，不得猜测。
