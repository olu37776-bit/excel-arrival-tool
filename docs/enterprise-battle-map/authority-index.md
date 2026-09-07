# 企业作战地图 Authority 文档索引

**状态：CURRENT AUTHORITY INDEX**  
**文档分支：`enterprise-battle-map-authority`**  
**长期代码分支：`feature/enterprise-battle-map`**

---

## 1. 当前正式 Authority

| 顺序 | 文档 | 用途 | 当前门禁 |
|---:|---|---|---|
| 1 | `enterprise-contract-architecture-v5.md` | 端到端 canonical identity、真实 Runtime Projection、API canonical-only、Customer 主键贯穿、Heatmap canonical key、Progress 单一事实源、DB/Conformance Gate | 所有企业任务必读 |
| 2 | `architecture/enterprise-runtime-field-options-contract-v1.md` | Runtime Field View Model、select/options 判定、动态 options 生命周期、错误边界与五模块回归门禁 | **新增长期 Runtime Options Authority** |
| 3 | `mox-canonical-authority-v6.md` | MOX 41字段、4 group、Create/Edit runtime、Heatmap、legacy key、Progress、Customer、DB/测试最终目标 | 当前 MOX 唯一业务 Authority |
| 4 | `remediation/enterprise-form-options-root-cause-remediation-v2.md` | `f.options is not iterable` 根因级修复：真实调用栈、Production-path reproduction、错误边界 | 已实施，等待用户人工复验 |
| 5 | `remediation/enterprise-form-options-and-group-spacing-remediation-v1.md` | 人工验收发现的 options runtime 与共享 group 视觉间距第一轮修复 | options 部分已被 V2 根因修复取代；spacing 仍有效 |
| 6 | `remediation/enterprise-customer-data-fetch-unification-v2.md` | Customer SQL/customer_id 贯穿修复及长期回归门禁 | 已修复，当前只做回归 |
| 7 | `reviews/mox-end-to-end-canonical-independent-review-v1.md` | MOX 端到端独立审查规范 | 最新复审已 PASS |
| 8 | `remediation/mox-4-group-render-chain-repair-v1.md` | MOX 4-group renderer 断链修复 | 已实施并通过复审 |
| 9 | `remediation/mox-end-to-end-canonical-convergence-v1.md` | MOX 端到端 canonical 收敛 | 已实施，作为回归基线 |
| 10 | `investigation/enterprise-runtime-implementation-survey-v1.md` | 已完成的实际运行链调查规范 | 事实证据来源 |
| 11 | `investigation/enterprise-excel-v0.1-v0.2-diff-survey-v1.md` | 企业作战地图基表 V0.1→V0.2 的 Schema/Contract 差异调查 | 当前可并行只读调查 |
| 12 | `integration/parallel-module-integration-plan-v1.md` | TOB/ISP/电力+大企合并规则 | 集成历史/回归参考 |
| 13 | `integration/local-worktree-layout-v1.md` | 本地真实 worktree 路径 | 本地执行必读 |
| 14 | `tob-canonical-authority-v2.md` | TOB 字段和 3-group 目标 | 当前业务 Authority |
| 15 | `isp-canonical-authority-v2.md` | ISP 字段和 3-group 目标 | 当前业务 Authority |
| 16 | `power-canonical-authority-v2.md` | 电力字段和 3-group 目标 | 当前业务 Authority |
| 17 | `large-enterprise-canonical-authority-v2.md` | 大企字段和 3-group 目标 | 当前业务 Authority |
| 18 | `enterprise-home-canonical-authority-v2.md` | 企业首页旧阶段设计 | DEFERRED；最后重新冻结 |

---

## 2. 当前阶段状态

MOX End-to-End Canonical Convergence、4-group render chain repair 和后续独立复审已经通过自动门禁。

当前状态：

```text
MOX AUTOMATED / INDEPENDENT REVIEW = PASS
OPTIONS ROOT CAUSE = FIXED IN IMPLEMENTATION
USER MANUAL ACCEPTANCE = PENDING RETEST
```

最新 `f.options is not iterable` 根因已经通过真实 Production 路径确认：

```text
Customer API = PASS

受影响字段：
region
representativeOffice
country
customerName

Field Contract / fieldDef：
fieldDef.type = 'select'

错误运行时判断：
f.type

实际：
f.type = undefined

结果：
select字段未进入正确options初始化/enrichment
→ f.options保持undefined
→ renderer迭代f.options
→ TypeError
→ 被错误包装成“获取客户数据失败”
```

因此该故障不是 Customer SQL/API 的再次失败，而是 Runtime Field View Model / Options Consumer 使用了错误 metadata authority。

---

## 3. Runtime Field / Options 当前规则

Field Contract / `fieldDef` 是字段静态定义的唯一 Authority。

Runtime Field View Model 只是投影，不得成为第二份字段定义来源。

正确链：

```text
Field Contract / fieldDef
→ Runtime Projection
→ options-bearing判定
→ Dynamic Options Provider / optionSet
→ Runtime Field View Model.options
→ Renderer
```

硬规则：

- `type` / `controlId` / `editorId` 的业务判定必须来自权威 Field Contract / fieldDef 或其唯一受验证 Projection；
- 不得在 `f.type` 未保证存在时，以它判断 select/options 行为；
- options-bearing field 进入 renderer 前 `options` 必须是 Array；
- 合法无候选可为 `[]`；
- API failure / options provider failure 不能静默转换成 `[]`；
- 非 options-bearing field 不得无条件迭代 `options`；
- Production tests 必须走真实 Create/Edit 初始化链。

详细规则见：

```text
architecture/enterprise-runtime-field-options-contract-v1.md
```

---

## 4. Customer 当前规则

已修复过的 Customer 根因：原 SQL 漏 `customer_id`。

长期必须保持：

```text
customers.customer_id
→ database query
→ API
→ frontend candidate
→ unique selection
→ business record.customer_id
```

当前 options 根因已经证明 `Customer API=PASS`，不得因为前端 Runtime TypeError 再次修改 Customer SQL/API。

错误边界必须区分：

```text
CUSTOMER_FETCH_FAILED
CUSTOMER_RESPONSE_CONTRACT_FAILED
OPTIONS_PROVIDER_FAILED
FORM_RUNTIME_FAILED
```

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

当前视觉要求：

- 非首 group 稳定顶部间距；
- group title 与上一组字段明显分离；
- Create/Edit 一致；
- 不插空字段、不插 `<br>`、不复制 MOX 专属布局逻辑。

---

## 6. Progress 当前规则

保持：

```text
Progress History table = 唯一持久化 Authority
battleProgress = latest/current canonical projection
独立进展弹窗 = Progress History 新增/编辑入口
```

不得恢复 business table text 双写或 fallback。

---

## 7. 当前推进顺序

```text
enterprise-form-options-root-cause-remediation-v2 已实施
→ 用户人工复验 TOB / ISP / 电力 / 大企 Create
→ 同时复验 MOX/共享 group spacing 与 Progress popup
→ 如人工 PASS，关闭本轮 Runtime remediation
→ 完成 Excel V0.1→V0.2 只读差异调查
→ Authority Review 决定 V0.2 的 label/group/option/field/persistence 变化
→ 再进入五模块统一收敛 / MOX Reference freeze
```

人工复验重点：

```text
TOB Create
ISP Create
Power Create
Large Enterprise Create
region → representativeOffice → country → customerName 级联
最终 customer_id
```

在用户人工 PASS 前，不得把该缺陷标记为 USER_ACCEPTED。

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
- `remediation/enterprise-form-options-and-group-spacing-remediation-v1.md` 中与 V2 options 根因修复冲突的内容
- 任何与当前 V5/V6/Runtime Options Authority 冲突的旧 Schema、Projection 测试、Review 结论或字段清单。

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
- Runtime View Model 不得重新创造 Field Contract 已定义的静态 metadata Authority；
- 人工视觉验收不由自动测试替代。
