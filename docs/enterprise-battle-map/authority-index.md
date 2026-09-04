# 企业作战地图 Authority 文档索引

**状态：CURRENT AUTHORITY INDEX**  
**文档分支：`enterprise-battle-map-authority`**  
**长期代码分支：`feature/enterprise-battle-map`**

---

## 1. 当前正式 Authority

| 顺序 | 文档 | 用途 | 当前门禁 |
|---:|---|---|---|
| 1 | `enterprise-contract-architecture-v5.md` | 端到端 canonical identity、真实 Runtime Projection、API canonical-only、Customer 主键贯穿、Heatmap canonical key、Progress 单一事实源、DB/Conformance Gate | 所有企业任务必读 |
| 2 | `mox-canonical-authority-v6.md` | MOX 41字段、4 group、Create/Edit runtime、Heatmap、legacy key、Progress、Customer、DB/测试最终目标 | 当前 MOX 唯一业务 Authority |
| 3 | `remediation/mox-4-group-render-chain-repair-v1.md` | 独立审查发现的 MOX 4-group runtime→renderer 断链定向修复 | **当前阻塞 remediation** |
| 4 | `remediation/mox-end-to-end-canonical-convergence-v1.md` | Runtime Survey 后 MOX 端到端收敛实施计划 | 已实施，作为修复背景/回归基线 |
| 5 | `reviews/mox-end-to-end-canonical-independent-review-v1.md` | 字段、Projection、Heatmap、legacy key、Customer、Progress popup/history、DB、隐藏消费者和测试可信度的独立审查规范 | 4-group 修复后重新执行 |
| 6 | `investigation/enterprise-runtime-implementation-survey-v1.md` | 已完成的实际运行链调查规范 | 事实证据来源 |
| 7 | `remediation/enterprise-customer-data-fetch-unification-v2.md` | Customer SQL/customer_id 贯穿修复及长期回归门禁 | 已修复项/回归 Authority |
| 8 | `integration/parallel-module-integration-plan-v1.md` | TOB/ISP/电力+大企合并规则 | 集成历史/回归参考 |
| 9 | `integration/local-worktree-layout-v1.md` | 本地真实 worktree 路径 | 本地执行必读 |
| 10 | `tob-canonical-authority-v2.md` | TOB 字段和 3-group 目标 | 后续统一收敛 |
| 11 | `isp-canonical-authority-v2.md` | ISP 字段和 3-group 目标 | 后续统一收敛 |
| 12 | `power-canonical-authority-v2.md` | 电力字段和 3-group 目标 | 后续统一收敛 |
| 13 | `large-enterprise-canonical-authority-v2.md` | 大企字段和 3-group 目标 | 后续统一收敛 |
| 14 | `enterprise-home-canonical-authority-v2.md` | 企业首页旧阶段设计 | DEFERRED；最后重新冻结 |

---

## 2. 当前最新阻塞事实

最新 MOX End-to-End Canonical Independent Review 已确认：

> MOX 4-group 从 runtime projection 到 Create/Edit renderer 的链路仍然断裂，导致“无线格局”和“微波格局”无法作为真实可见分组进入 Create/Edit 表单。

这不是新的字段 Contract 设计问题。当前 Authority 保持：

```text
MOX Create/Edit 顶层 group：
客户信息
无线格局
微波格局
作战情况
```

字段集合仍为 41 项；不得把 MOX 改回“客户信息 / 业务格局 / 作战情况”。

当前唯一修复范围：

```text
Field Contract
→ getCreateFields() / getEditFields() 或唯一公共底层实现
→ group model
→ Create/Edit renderer
```

修复必须以本地最新 Review 报告中的具体断裂点为事实依据。

---

## 3. 已确认的其他端到端规则继续有效

### Customer

已修复 SQL 漏 `customer_id` 问题。长期必须保持：

```text
customers.customer_id
→ query
→ API
→ frontend candidate
→ unique selection
→ business record.customer_id
```

### Heatmap

字段 identity 必须使用 canonical key，中文 label 仅用于展示。

### API legacy key

活动 runtime 不得接受：

```text
office
customer
major_project
progress
```

### Progress

```text
Progress History = 唯一持久化 Authority
battleProgress = latest/current canonical projection/editor binding
```

独立进展弹窗必须保留并只操作 Progress History，不允许 history + business text 双写或 fallback。

### Metric / DB

9 个 Metric 公式不变；API/database.js/SQLite/Migration/round-trip 继续按 `enterprise-contract-architecture-v5.md` 约束。

本轮 4-group repair 不得顺带重构这些已收敛能力，只做回归保护。

---

## 4. group 规则

MOX：

```text
客户信息
无线格局
微波格局
作战情况
```

TOB / ISP / 电力 / 大企：

```text
客户信息
业务格局
作战情况
```

共享 renderer 必须根据 Contract group 动态渲染 group 数量，不得写死“三组”或为 MOX 复制第二套字段 Authority。

---

## 5. 当前推进顺序

```text
MOX End-to-End Canonical Independent Review 发现 4-group blocker
→ 按 remediation/mox-4-group-render-chain-repair-v1.md 修复
→ 本地 commit + 工作树干净
→ 新 Agent 重新执行 reviews/mox-end-to-end-canonical-independent-review-v1.md
→ 用户人工验收（Create/Edit 4-group、视觉分隔、进展弹窗、Heatmap）
→ MOX REFERENCE_IMPLEMENTATION_V1
→ 将相同 Conformance Gate 应用到 TOB/ISP/电力/大企
→ 企业模块统一审查
→ 企业首页最终建设
```

当前 Repair Agent 必读：

```text
enterprise-contract-architecture-v5.md
mox-canonical-authority-v6.md
remediation/mox-end-to-end-canonical-convergence-v1.md
remediation/mox-4-group-render-chain-repair-v1.md
本地最新 docs/enterprise/reviews/mox-end-to-end-canonical-independent-review.md
```

---

## 6. 已被取代

与当前版本冲突时不再作为 Authority：

- `enterprise-contract-architecture-v1.md`
- `enterprise-contract-architecture-v2.md`
- `enterprise-contract-architecture-v3.md`
- `enterprise-contract-architecture-v4.md`
- `mox-canonical-authority-v3.md`
- `mox-canonical-authority-v4.md`
- `mox-canonical-authority-v5.md`
- `remediation/mox-post-manual-review-remediation-v1.md`
- `remediation/mox-post-manual-review-remediation-v2.md`
- `remediation/enterprise-customer-data-fetch-unification-v1.md`
- 任何与 V5/V6 冲突的本地旧 Schema、Projection 测试、Review 结论或字段清单。

旧文件仅保留历史证据，Agent 不得新旧折中。

---

## 7. 本地路径

Authority 镜像：

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

其他已确认 worktree：

```text
D:\BattleMap\tob-worktree
D:\BattleMap\battle-map-isp
D:\BattleMap\power-large-task
```

---

## 8. 文档维护规则

- 业务和架构修正统一进入 Authority 分支；
- 本地代码仓库不维护第二套长期设计 Authority；
- 新版本发布后旧版本自动 superseded；
- 实际实现发现必须先分类为 IMPLEMENTATION_NONCONFORMANCE / DOCUMENT_GAP / ARCHITECTURE_GAP / TEST_GAP；
- 不确定事实标记 OPEN / NEED_USER_CONFIRMATION；
- 不允许本地 Agent 自行扩字段、改业务规则或恢复 legacy compatibility；
- 独立审查报告可以单独 commit，但必须记录其对应的代码 `REVIEWED_HEAD`。
