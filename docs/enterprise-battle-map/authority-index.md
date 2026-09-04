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
| 3 | `remediation/enterprise-form-options-and-group-spacing-remediation-v1.md` | 人工验收发现的四模块 `f.options is not iterable` 与共享 group 视觉间距修复 | **当前实施任务** |
| 4 | `remediation/enterprise-customer-data-fetch-unification-v2.md` | Customer SQL/customer_id 贯穿修复及长期回归门禁 | 已修复，当前只做回归 |
| 5 | `reviews/mox-end-to-end-canonical-independent-review-v1.md` | MOX 端到端独立审查规范 | 最新复审已 PASS |
| 6 | `remediation/mox-4-group-render-chain-repair-v1.md` | MOX 4-group renderer 断链修复 | 已实施并通过复审 |
| 7 | `remediation/mox-end-to-end-canonical-convergence-v1.md` | MOX 端到端 canonical 收敛 | 已实施，作为回归基线 |
| 8 | `investigation/enterprise-runtime-implementation-survey-v1.md` | 已完成的实际运行链调查规范 | 事实证据来源 |
| 9 | `integration/parallel-module-integration-plan-v1.md` | TOB/ISP/电力+大企合并规则 | 集成历史/回归参考 |
| 10 | `integration/local-worktree-layout-v1.md` | 本地真实 worktree 路径 | 本地执行必读 |
| 11 | `tob-canonical-authority-v2.md` | TOB 字段和 3-group 目标 | 当前业务 Authority |
| 12 | `isp-canonical-authority-v2.md` | ISP 字段和 3-group 目标 | 当前业务 Authority |
| 13 | `power-canonical-authority-v2.md` | 电力字段和 3-group 目标 | 当前业务 Authority |
| 14 | `large-enterprise-canonical-authority-v2.md` | 大企字段和 3-group 目标 | 当前业务 Authority |
| 15 | `enterprise-home-canonical-authority-v2.md` | 企业首页旧阶段设计 | DEFERRED；最后重新冻结 |

---

## 2. 当前阶段状态

MOX End-to-End Canonical Convergence、4-group render chain repair 和后续独立复审已经通过自动门禁。

当前状态：

```text
MOX AUTOMATED / INDEPENDENT REVIEW = PASS
USER MANUAL ACCEPTANCE = PARTIAL / FAIL
```

最新人工验收确认两个真实缺口：

### A. TOB / ISP / 电力 / 大企 Create options runtime 异常

用户打开新增时仍看到“获取客户数据失败”，真实前端异常为：

```text
f.options is not iterable
```

当前不能重新假定是 customer SQL 问题。必须先证明：

```text
Customer API 是否成功
→ customer_id 是否保留
→ runtime field model
→ options provider/enrichment
→ renderer
```

然后定位具体 field / function / options value。

当前禁止使用 `f.options || []` 等静默兜底作为根修复。

### B. Create/Edit group 视觉间距不足

MOX 4-group 结构已经正确，但人工验收确认相邻 group 尤其“无线格局”“微波格局”与上一组视觉粘连。

目标是修共享 group renderer/CSS 的稳定垂直间距，不插空字段、不写 `<br>`、不为 MOX 复制独立样式。

---

## 3. Customer 当前规则

已确认并修复过的 Customer 根因：原 SQL 漏 `customer_id`。

长期必须保持：

```text
customers.customer_id
→ database query
→ API
→ frontend candidate
→ unique selection
→ business record.customer_id
```

当前 `f.options is not iterable` 必须先证明发生在这条链的哪一层。

如果 Customer API 已成功并带真实 `customer_id`，本轮不得再次修改 SQL/Customer Contract。

错误边界必须区分：

```text
CUSTOMER_FETCH_FAILED
CUSTOMER_RESPONSE_CONTRACT_FAILED
FORM_RUNTIME_FAILED
OPTIONS_ENRICHMENT_FAILED
```

不能再把所有 Create 初始化异常统一包装成“获取客户数据失败”。

---

## 4. Options Runtime 规则

企业 Create/Edit 动态 options 属于 Field Contract 的运行时消费者。

正确链：

```text
Field Contract
→ Runtime Projection
→ Runtime Field View Model
→ Dynamic Options Provider
→ Renderer
```

硬规则：

- Contract 保持静态，不承载动态 customer/region/office 候选；
- 只有 options-bearing control/editor 才进入 options 逻辑；
- 需要 options 的 runtime field 最终必须是明确 Array contract；
- 合法无候选用 `[]`；
- API failure 不能伪装成 `[]`；
- 非 options-bearing field 不应因为没有 `options` 而失败；
- customer candidate 必须保留真实 `customer_id`。

---

## 5. Group 规则

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

结构 Authority 已冻结。

当前只允许改共享视觉机制：

- 非首 group 稳定顶部间距；
- group title 与上一组字段明显分离；
- Create/Edit 一致；
- 优先复用 spacing token/CSS variable；
- 不改变字段集合、顺序或 group 归属。

---

## 6. Progress 当前规则

本轮不重新设计 Progress。

保持：

```text
Progress History table = 唯一持久化 Authority
battleProgress = latest/current canonical projection
独立进展弹窗 = Progress History 新增/编辑入口
```

“作战进展”是同一业务概念，但不得恢复 business table text 双写或 fallback。

本轮只做回归验证：进展弹窗仍可用、History 单一事实源无回归。

---

## 7. 当前推进顺序

```text
人工验收发现 options runtime + group spacing
→ 按 remediation/enterprise-form-options-and-group-spacing-remediation-v1.md 实施
→ 本地 commit + 自动验证
→ 用户重新人工验收：四模块新增客户链 + MOX/共享group视觉 + Progress popup回归
→ 如人工 PASS，冻结 MOX REFERENCE_IMPLEMENTATION_V1
→ 将已验证 Conformance Gate 应用到 TOB/ISP/电力/大企整体收敛
→ 企业模块统一审查
→ 企业首页最终建设
```

当前 Implementation Agent 必读：

```text
enterprise-contract-architecture-v5.md
mox-canonical-authority-v6.md
remediation/enterprise-customer-data-fetch-unification-v2.md
remediation/enterprise-form-options-and-group-spacing-remediation-v1.md
TOB/ISP/Power/Large 当前 Canonical Authority
```

---

## 8. 已被取代/历史参考

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
- 任何与当前 V5/V6/最新 remediation 冲突的旧 Schema、Projection 测试、Review 结论或字段清单。

旧文件只保留历史证据，不允许新旧折中。

---

## 9. 本地路径

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

## 10. 文档维护规则

- 业务/架构/人工验收 remediation 统一进入 Authority 分支；
- 本地代码仓库不维护第二套长期设计 Authority；
- 实施 Agent 同轮完成代码、测试、自动验证和 remediation report；
- 不确定事实必须先通过真实调用栈证明，不得猜测；
- 不允许为修复 runtime error 恢复 legacy key/fallback；
- 人工视觉验收不由自动测试替代。
