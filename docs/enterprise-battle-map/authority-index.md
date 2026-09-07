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
| 4 | `remediation/non-mox-alignment-independent-review-findings-remediation-v2.md` | 关闭 Non-MOX Alignment 独立审查发现的 7 个 blocking findings；包含 shared runtime、Heatmap canonical、group、重复 renderer 及其余 findings | **当前阻塞 remediation** |
| 5 | `reviews/non-mox-modules-mox-reference-independent-review-v1.md` | TOB/ISP/电力/大企 alignment 固定 HEAD 独立审查规范 | 最新执行结果 FAIL / 7 blockers |
| 6 | `remediation/non-mox-modules-mox-reference-alignment-v1.md` | TOB/ISP/电力/大企全面向 MOX 已验证机制对齐 | 前序实施报告 PASS 已被独立审查推翻；只作背景 |
| 7 | `investigation/enterprise-excel-v0.1-v0.2-diff-survey-v1.md` | 企业作战地图基表 V0.1→V0.2 Schema/Contract 差异调查 | 可并行只读；业务字段变化需先 Authority Review |
| 8 | `remediation/enterprise-form-options-root-cause-remediation-v2.md` | `f.options is not iterable` 根因级修复 | 已实施并经用户确认 Create/Edit 可打开 |
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

最新 Non-MOX → MOX Reference Independent Review 已发现 **7 个 blocking finding**。

前序 Alignment Implementation Report 虽声明 PASS，但独立审查证明其结论与真实代码状态不一致，因此当前正式状态为：

```text
MOX = VERIFIED REFERENCE CANDIDATE
TOB / ISP / POWER / LARGE ALIGNMENT = NOT VERIFIED
INDEPENDENT REVIEW = FAIL
BLOCKING_FINDINGS = 7
```

当前禁止继续按前序 implementation report 的 PASS 状态推进人工验收或 V0.2 字段实施。必须先关闭 7 个 blocking finding 并重新独立审查。

---

## 3. 已确认的 Blocking Facts

当前用户已回报并由独立审查确认的至少包括：

### Shared Runtime 未真正推广

```text
TOB 使用 shared field-projections.js
ISP / Power / Large 仍存在本地实现
```

目标：四模块共同消费同一 shared projection/runtime mechanism；module-local duplicate projection 必须归零。

### Power Heatmap 仍使用中文 label 作为 identity

已确认类似：

```text
valueField = "26年空间（跳）"
```

目标必须使用 Power canonical key：

```text
space2026Hops
```

中文 label 只用于展示。

### Power / Large group 名称错误

当前存在：

```text
业务信息
```

Authority 规定四个 non-MOX 模块均为：

```text
客户信息
业务格局
作战情况
```

### 重复 Section / Group Renderer

独立审查确认存在重复 section/group render path。具体文件和调用路径以本地 review report 为事实源，必须收敛到唯一 shared renderer。

### 其余 Blocking Findings

其余 finding 不在 Authority 中凭口述猜测。Implementation Agent 必须读取本地独立审查报告，恢复全部 7 个 finding 原始 ID/事实并建立 Closure Matrix。

---

## 4. 当前 Remediation 规则

当前只允许实施：

```text
remediation/non-mox-alignment-independent-review-findings-remediation-v2.md
```

实施前必须读取：

```text
D:\BattleMap\battle-map\docs\enterprise\reviews\non-mox-modules-mox-reference-independent-review.md
```

并建立恰好包含 7 个 blocking finding 的 Closure Matrix。

每个 finding 必须具备：

```text
review finding
→ exact code fact
→ root cause
→ changed files/functions
→ production-path test/static evidence
→ implementation status
```

Implementation Agent 只能声明 IMPLEMENTED；最终 VERIFIED 必须由新的固定 HEAD Independent Review 决定。

前一轮“Implementation Report 自报 PASS 但代码不符”必须通过 evidence-based report 门禁修正。

---

## 5. 长期统一机制继续有效

### Runtime Field

Field Contract / `fieldDef` 是 type/control/editor/group/order 等静态 metadata 唯一 Authority；Runtime Field View Model 不得创建第二套 schema。

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

## 6. Excel V0.2 协调

V0.1→V0.2 Excel Diff Survey 可以继续只读并行。

但当前 7 个 blocking finding 属于 implementation/conformance 问题，不能用 V0.2 未 Authority 化的变化掩盖。

如果某个具体 finding 确实依赖 V0.2 新业务字段，则标记：

```text
BLOCKED_BY_V0_2_AUTHORITY
```

不得自行修改字段集合、group 或 option-set。

---

## 7. 当前推进顺序

```text
1. 读取最新独立审查报告
2. 建立 7-Finding Closure Matrix
3. 按 remediation/non-mox-alignment-independent-review-findings-remediation-v2.md 实施
4. 修复并提交新的代码 HEAD
5. 新 Agent 对新 HEAD 重新执行 Non-MOX Independent Review
6. BLOCKING_FINDINGS 必须归零
7. Review PASS 后用户逐模块人工验收
8. 完成 Excel V0.2 Authority Review
9. 发布必要的新模块 Canonical Authority 并只实施 V0.2 delta
10. 企业模块统一 VERIFIED
11. 企业首页最后建设
```

---

## 8. 本地路径

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

当前只允许一个写 Agent 操作主工作树。

---

## 9. 文档维护规则

- 独立审查代码事实优先于 Implementation Report 自报状态；
- 业务字段和共享实现机制分开治理；
- 不保留长期 legacy alias/fallback/双写；
- Production 与测试必须走同一真实 runtime 路径；
- Implementation Report 中每个 PASS 必须关联 file/function + test/static evidence；
- Implementation Agent 不得自行标记 Independent Review finding 为 VERIFIED；
- Excel V0.2 未 Authority 化变化不得混入本轮 remediation；
- 人工视觉/交互验收由用户执行。
