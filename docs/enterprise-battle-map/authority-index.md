# 企业作战地图 Authority 文档索引

**状态：CURRENT AUTHORITY INDEX**  
**文档分支：`enterprise-battle-map-authority`**  
**长期本地集成分支：`feature/enterprise-battle-map`**

---

## 1. 当前正式 Authority

| 顺序 | 文档 | 用途 | 当前门禁 |
|---:|---|---|---|
| 1 | `enterprise-contract-architecture-v4.md` | Field/Metric Contract、真实 Runtime Projection、group Authority、API/DB/SQLite 串联和双向 Conformance Gate | 所有企业任务必读 |
| 2 | `investigation/enterprise-runtime-implementation-survey-v1.md` | 恢复五模块真实 Runtime、API、database.js、SQLite、Customer、Progress、Metric、Heatmap 和测试事实 | 当前事实调查 Authority |
| 3 | `integration/parallel-module-integration-plan-v1.md` | 并行模块统一合并、冲突处理、V35—V38 联合验证 | 合并阶段 Authority |
| 4 | `integration/local-worktree-layout-v1.md` | 本地真实 worktree 路径与分支对应 | 本地执行必读 |
| 5 | `mox-canonical-authority-v5.md` | MOX 41字段、4个顶层group、客户类别、进展、V34、UI/API/DB、统计 | 当前 MOX 唯一业务 Authority |
| 6 | `remediation/enterprise-customer-data-fetch-unification-v1.md` | TOB/ISP/电力/大企新增客户数据获取统一修复 | 当前客户链修复 Authority |
| 7 | `tob-canonical-authority-v2.md` | TOB字段和 3-group 页面目标 | TOB业务 Authority |
| 8 | `isp-canonical-authority-v2.md` | ISP字段和 3-group 页面目标 | ISP业务 Authority |
| 9 | `power-canonical-authority-v2.md` | 电力字段和 3-group 页面目标 | 电力业务 Authority |
| 10 | `large-enterprise-canonical-authority-v2.md` | 大企字段和 3-group 页面目标 | 大企业务 Authority |
| 11 | `enterprise-home-canonical-authority-v2.md` | 企业首页历史设计 | DEFERRED；后续重新发布当前版 |

---

## 2. 当前关键修正规则

### MOX

新增/编辑固定 4 个顶层 group：

```text
客户信息
无线格局
微波格局
作战情况
```

MOX 不得出现“业务格局”顶层 group。

### TOB / ISP / 电力 / 大企

新增/编辑固定 3 个顶层 group：

```text
客户信息
业务格局
作战情况
```

### Runtime Projection

当前真实 Create/Edit 路径已确认围绕：

```text
getCreateFields() / getEditFields()
```

收敛。

不得再让未被 renderer 实际消费的 `getCreateProjection()` / `getEditProjection()` 拥有独立过滤、排序或分组业务逻辑，也不得让测试验证一条、运行时走另一条。

### Conformance Gate

Create/Edit/Table 必须做双向集合相等验证：

```text
Contract expected keys == actual runtime keys
```

同时验证 group、order、重复和缺失。

MOX `customerCategory` 合法值必须完整覆盖：空值 / 核心NA / 战略NA。

---

## 3. Authority 优先级

```text
当前模块 Canonical Authority
→ 本地“企业作战地图基表”对应 Sheet 的精确列/Row2/Row3/Validation
→ 用户最新明确修正
→ enterprise-contract-architecture-v4.md
→ 当前真实代码/API/database.js/SQLite（用于判断差距）
→ 本地旧文档/旧Schema/旧配置
```

当前代码不能反向创造需求；但 Runtime Survey 用于证明 Authority 是否已经真正落地。

---

## 4. 端到端契约范围

Field Contract 不是仅前端配置，必须串联：

```text
Canonical Field Contract
├─ Table Runtime
├─ Create Runtime
├─ Edit Runtime
├─ API read/create/update Mapping
├─ database.js Mapping
└─ SQLite Persistence / Relation
```

Metric Contract继续负责统计和点击筛选同一 `where`。

Heatmap 已存在共享组件和模块级设计，但真实数据源/转换/聚合/点击链仍由 Runtime Survey 恢复事实，调查完成前不得凭空设计或造假数据。

Progress 的独立新增/追加机制也必须先恢复真实持久化模型，再决定是否需要补充长期 Contract 表达。

---

## 5. 已被取代或暂停使用

以下文档与当前版本冲突时不再作为 Authority：

- `enterprise-contract-architecture-v1.md`
- `enterprise-contract-architecture-v2.md`
- `enterprise-contract-architecture-v3.md`
- `mox-canonical-authority-v3.md`
- `mox-canonical-authority-v4.md`
- `remediation/mox-post-manual-review-remediation-v1.md`
- `remediation/mox-post-manual-review-remediation-v2.md` 中关于 MOX 3-section / “业务格局”的内容
- `tob-canonical-authority-v1.md`
- `isp-canonical-authority-v1.md`
- `power-canonical-authority-v1.md`
- `large-enterprise-canonical-authority-v1.md`
- `enterprise-home-canonical-authority-v1.md`
- 任何与当前 Authority 冲突的本地字段清单、Schema、Projection测试或 Review 结论

旧文档可保留历史证据，但 Agent 不得新旧折中。

---

## 6. 当前推进顺序

当前允许并行完成已经启动的客户查询修复与既有只读调查，但正式 Runtime Survey 必须针对固定 `SURVEY_HEAD`。

推荐后续：

```text
当前写操作全部提交
→ 固定 SURVEY_HEAD
→ Enterprise Runtime Implementation Survey
→ Authority / Runtime 差距分类
→ 只对 IMPLEMENTATION_NONCONFORMANCE 做 remediation
→ 对 DOCUMENT_GAP 更新 Authority
→ 对真正 ARCHITECTURE_GAP 再升级共享架构
→ 统一独立审查
→ 用户人工验收
```

---

## 7. 本地 Authority 镜像

本地固定路径：

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

ISP worktree 正确路径：

```text
D:\BattleMap\battle-map-isp
```

---

## 8. 文档维护规则

- 后续业务修正统一进入 Authority 分支；
- 本地实施仓库不维护第二套长期设计 Authority；
- 新版本发布后旧版本自动 superseded；
- 字段变更必须同步 Contract、Runtime Projection、Validator、API/DB mapping 和测试门禁；
- 实际实现调查必须记录固定 HEAD；
- 不确定的业务事实标记 OPEN / NEED_USER_CONFIRMATION，不允许 Agent 自行猜测。
