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
| 4 | `remediation/non-mox-modules-mox-reference-alignment-v1.md` | TOB/ISP/电力/大企全面向 MOX 已验证机制对齐：Runtime、Create/Edit、Customer、Progress、Heatmap、Metric、API/DB、隐藏消费者 | **当前下一实施阶段** |
| 5 | `investigation/enterprise-excel-v0.1-v0.2-diff-survey-v1.md` | 企业作战地图基表 V0.1→V0.2 Schema/Contract 差异调查 | 可与 Gap Matrix 并行；业务字段变化需先 Authority Review |
| 6 | `remediation/enterprise-form-options-root-cause-remediation-v2.md` | `f.options is not iterable` 根因级修复 | 已实施并经用户确认 Create/Edit 可打开 |
| 7 | `remediation/enterprise-form-options-and-group-spacing-remediation-v1.md` | options runtime 与共享 group 视觉间距第一轮修复 | options部分被V2取代；spacing为历史/回归参考 |
| 8 | `remediation/enterprise-customer-data-fetch-unification-v2.md` | Customer SQL/customer_id 贯穿修复及长期回归门禁 | 已修复，统一机制回归项 |
| 9 | `reviews/mox-end-to-end-canonical-independent-review-v1.md` | MOX 端到端独立审查规范 | 最新复审 PASS |
| 10 | `remediation/mox-4-group-render-chain-repair-v1.md` | MOX 4-group renderer 断链修复 | 已实施并通过复审 |
| 11 | `remediation/mox-end-to-end-canonical-convergence-v1.md` | MOX 端到端 canonical 收敛 | 已实施，作为 Reference baseline |
| 12 | `investigation/enterprise-runtime-implementation-survey-v1.md` | 已完成的实际运行链调查规范 | 事实证据来源 |
| 13 | `integration/parallel-module-integration-plan-v1.md` | TOB/ISP/电力+大企合并规则 | 集成历史/回归参考 |
| 14 | `integration/local-worktree-layout-v1.md` | 本地真实 worktree 路径 | 本地执行必读 |
| 15 | `tob-canonical-authority-v2.md` | TOB 当前字段和3-group业务基线 | 字段暂冻结，V0.2后可能升级 |
| 16 | `isp-canonical-authority-v2.md` | ISP 当前字段和3-group业务基线 | 字段暂冻结，V0.2后可能升级 |
| 17 | `power-canonical-authority-v2.md` | 电力当前字段和3-group业务基线 | 字段暂冻结，V0.2后可能升级 |
| 18 | `large-enterprise-canonical-authority-v2.md` | 大企当前字段和3-group业务基线 | 字段暂冻结，V0.2后可能升级 |
| 19 | `enterprise-home-canonical-authority-v2.md` | 企业首页旧阶段设计 | DEFERRED；最后重新冻结 |

---

## 2. 当前阶段判断

用户人工确认：MOX 当前整体实现机制基本正确；TOB / ISP / 电力 / 大企虽然已能打开 Create/Edit，但页面与运行实现整体仍存在明显问题，不能继续按“局部 bug 修复”推进。

因此当前正式判断：

```text
MOX = VERIFIED REFERENCE CANDIDATE
TOB / ISP / POWER / LARGE = MECHANISM NOT ALIGNED
```

四模块下一步必须全面向 MOX 已验证后的机制收敛，但不得复制 MOX 业务字段。

---

## 3. 当前 Reference Alignment 原则

共享的是：

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

不共享/不复制的是：

```text
MOX 41字段
MOX 4-group业务结构
MOX专属无线/微波字段
MOX专属Heatmap业务规则
MOX数据库业务列
```

TOB / ISP / 电力 / 大企继续使用自己的 Canonical Contract 和 3-group：

```text
客户信息
业务格局
作战情况
```

---

## 4. `f.options` 根因已闭合

最新根因：

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

## 6. Excel V0.2 与 Reference Alignment 协调

V0.1→V0.2 Excel Diff Survey 可以与四模块 Gap Matrix 并行。

允许先做：

- shared runtime alignment；
- renderer alignment；
- customer/progress/heatmap/metric/API/DB mechanism alignment；
- hidden consumer cleanup。

暂不允许 Agent 自行依据 V0.2 改业务字段。

如果 V0.2 导致：

```text
field added/removed/renamed
group changed
option-set changed
semantic changed
```

必须先经过 Authority Review，发布对应模块新的 Canonical Authority，再实施字段变化。

---

## 7. 当前推进顺序

```text
1. 更新Authority镜像
2. 运行 non-mox-modules-mox-reference-alignment-v1.md
   - 先建 Gap Matrix
   - 再收敛 shared runtime
   - TOB → ISP → Power → Large 逐模块接入
3. 同时运行 Excel V0.1→V0.2 Diff Survey（只读）
4. V0.2 Authority Review
5. 如V0.2有业务字段变化，发布模块新Authority并补实施
6. Non-MOX Independent Review
7. 用户逐模块人工验收
8. 企业模块统一 VERIFIED
9. 企业首页最终建设
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

当前 Reference Alignment 应在主工作树统一实施，禁止多个写 Agent 同时操作该 worktree。

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
- 人工视觉/交互验收由用户执行；
- 不确定的 V0.2 业务变化必须标记 `BLOCKED_BY_V0_2_AUTHORITY`，不得猜测。
