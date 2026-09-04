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
| 3 | `remediation/mox-end-to-end-canonical-convergence-v1.md` | Runtime Survey 后 MOX 端到端收敛实施计划 | 当前下一实施任务 |
| 4 | `investigation/enterprise-runtime-implementation-survey-v1.md` | 已完成的实际运行链调查规范 | 事实证据来源 |
| 5 | `remediation/enterprise-customer-data-fetch-unification-v2.md` | Customer SQL/customer_id 贯穿修复及长期回归门禁 | 已修复项/回归 Authority |
| 6 | `integration/parallel-module-integration-plan-v1.md` | TOB/ISP/电力+大企合并规则 | 集成历史/回归参考 |
| 7 | `integration/local-worktree-layout-v1.md` | 本地真实 worktree 路径 | 本地执行必读 |
| 8 | `tob-canonical-authority-v2.md` | TOB 字段和 3-group 目标 | 后续统一收敛 |
| 9 | `isp-canonical-authority-v2.md` | ISP 字段和 3-group 目标 | 后续统一收敛 |
| 10 | `power-canonical-authority-v2.md` | 电力字段和 3-group 目标 | 后续统一收敛 |
| 11 | `large-enterprise-canonical-authority-v2.md` | 大企字段和 3-group 目标 | 后续统一收敛 |
| 12 | `enterprise-home-canonical-authority-v2.md` | 企业首页旧阶段设计 | DEFERRED；最后重新冻结 |

---

## 2. 当前已确认事实

### MOX Runtime

- 41 个 Field Contract 业务字段保持不变；
- MOX 正确顶层 group：客户信息 / 无线格局 / 微波格局 / 作战情况；
- MOX 不使用“业务格局”；
- 真实 Create/Edit runtime 使用 `getCreateFields()` / `getEditFields()` 或其底层实现；
- 旧 `getCreateProjection()` / `getEditProjection()` 曾与真实 renderer 不一致；
- `getMoxFromSections()` 已确认未被使用；
- 原测试存在错误 Projection 路径、单向检查和 option-set 漏测。

### Customer

已确认原 SQL 类似：

```sql
SELECT region, office, country, customer FROM customers
```

漏掉 `customer_id`，造成关系主键链路断开。修复后长期必须验证：

```text
customers.customer_id
→ database query
→ API
→ frontend candidate
→ unique selection
→ business record.customer_id
```

### Heatmap

- 当前存在使用中文 label 作为字段 identity 的实现；
- 目标必须使用 canonical key；
- label 仅展示；
- 本轮不改变未冻结的 Heatmap 业务规则。

### Legacy API key

`updateMoxNetwork()` 当前仍接受旧 key：

```text
office
customer
major_project
progress
```

目标 runtime legacy key 数量必须为 0。

### Progress

当前存在：

```text
Progress history table
+
battleProgress text
```

双写不可接受。目标：

```text
Progress history = 唯一持久化 Authority
battleProgress = latest/current progress canonical projection/editor binding
```

不得再双写或 fallback。

---

## 3. 当前架构原则

企业模块继续坚持：

```text
Canonical Authority
→ Field Contract
→ Runtime Projection
→ UI / API
→ database.js mapping
→ SQLite / Relation / History
```

旁路消费者 Metric / Heatmap / Customer / Progress 必须使用同一 canonical identity。

核心规则：

- canonical key 是跨层稳定业务身份；
- 中文 label 只用于展示；
- DB column 只用于持久化；
- 不保留长期 legacy alias/fallback/双读/双写；
- Production 和 tests 必须验证同一真实 runtime 路径；
- Contract expected 与 actual runtime 必须双向相等。

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

Create/Edit 顶层 group 样式必须共享、清晰、有稳定间距和分隔。

---

## 5. 当前下一步

正式推进顺序：

```text
确认当前写操作全部 commit
→ MOX End-to-End Canonical Convergence
→ 自动验证
→ 新 Agent 独立 End-to-End Review
→ 用户人工验收
→ MOX REFERENCE_IMPLEMENTATION_V1
→ 将相同 Conformance Gate 应用到 TOB/ISP/电力/大企
→ 企业模块统一审查
→ 企业首页最终建设
```

当前实施必须读取：

```text
enterprise-contract-architecture-v5.md
mox-canonical-authority-v6.md
remediation/mox-end-to-end-canonical-convergence-v1.md
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
- 不允许本地 Agent 自行扩字段、改业务规则或恢复 legacy compatibility。
