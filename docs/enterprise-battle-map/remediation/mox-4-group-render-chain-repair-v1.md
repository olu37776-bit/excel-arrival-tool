# MOX 4-Group Render Chain Repair V1

**状态：CURRENT BLOCKING REMEDIATION**  
**代码工作树：`D:\BattleMap\battle-map`**  
**代码分支：`feature/enterprise-battle-map`**  
**唯一共享架构 Authority：`enterprise-contract-architecture-v5.md`**  
**唯一 MOX Authority：`mox-canonical-authority-v6.md`**  
**直接证据：本地 `docs/enterprise/reviews/mox-end-to-end-canonical-independent-review.md`**  
**下一门禁：重新执行 MOX End-to-End Canonical Independent Review**

---

## 1. 已确认阻塞

最新独立审查确认：

> MOX 4-group 渲染链路断裂，导致 Create / Edit 表单无法实际渲染“无线格局”和“微波格局”字段分组。

当前业务 Authority 不再讨论：

```text
MOX Create/Edit 顶层 group 必须恰好为：
1. 客户信息
2. 无线格局
3. 微波格局
4. 作战情况
```

字段集合保持 41 项不变：

- 客户信息：1—6；
- 无线格局：7—18；
- 微波格局：19—28；
- 作战情况：29—41。

本次 remediation **不得重新设计字段 Contract，也不得把 MOX 改回 3-group / “业务格局”**。

---

## 2. 本轮目标

只修复真实运行链：

```text
MOX Field Contract
→ getCreateFields() / getEditFields() 或其唯一公共底层实现
→ group organization / render model
→ Create/Edit renderer
→ 4 个实际可见 group
```

完成后必须证明：

```text
Contract group
== Runtime group model
== Renderer actual group
```

而不是只证明函数返回了正确字段。

---

## 3. 必读证据

实施前必须完整读取：

```text
D:\BattleMap\BattleMapenterprise-authority\docs\enterprise-battle-map\enterprise-contract-architecture-v5.md
D:\BattleMap\BattleMapenterprise-authority\docs\enterprise-battle-map\mox-canonical-authority-v6.md
D:\BattleMap\BattleMapenterprise-authority\docs\enterprise-battle-map\remediation\mox-end-to-end-canonical-convergence-v1.md
D:\BattleMap\BattleMapenterprise-authority\docs\enterprise-battle-map\remediation\mox-4-group-render-chain-repair-v1.md
```

以及本地最新独立审查报告：

```text
D:\BattleMap\battle-map\docs\enterprise\reviews\mox-end-to-end-canonical-independent-review.md
```

审查报告中的具体 failing function、文件、调用链和证据优先于任何猜测。不得忽略报告并重新推断根因。

---

## 4. WRITE_SCOPE

### 4.1 允许修改

仅允许修改本 finding 的直接运行链和测试：

- MOX Create/Edit runtime projection / grouping helper；
- Create/Edit renderer 接收 group model 的直接代码；
- 企业共享 group renderer / form renderer（仅当根因确实位于共享层）；
- MOX Create/Edit 直接测试；
- group runtime/conformance 测试；
- 共享 renderer 的直接回归测试；
- 本轮 remediation report。

### 4.2 禁止修改

本轮不得修改：

- 41 个 MOX 业务字段及 canonical key；
- 9 个 Metric 公式；
- Heatmap 业务规则或 canonical 化结果；
- Customer 已修复链；
- Progress History 单一事实源设计；
- `updateMoxNetwork()` canonical-only 规则；
- V34—V39 Migration，除非审查报告明确证明本 finding 由 Schema 导致（正常情况下不应需要）；
- TOB / ISP / 电力 / 大企业务 Contract；
- 企业首页；
- 非企业模块。

不得借本轮修复重新引入 `section` 第二业务 Authority、legacy key、fallback 或另一套 Projection 算法。

---

## 5. Step 1：固定审查基线

记录：

```text
git branch --show-current
git status --short
git log -1 --oneline
git diff --stat
```

要求：

- 分支必须是 `feature/enterprise-battle-map`；
- 当前没有其他 Agent 同时写工作树；
- 记录 `BASE_HEAD`；
- 找到独立 Review 的 `REVIEWED_HEAD`；
- 如果当前 HEAD 已经变化，先确认 finding 仍可复现，不得把旧 finding 套到已变化代码上。

---

## 6. Step 2：恢复真实 4-group 渲染调用链

必须从组件 template / renderer 反向恢复，而不是从测试函数正向猜测。

分别画出：

```text
Create component/template
← renderer data/model
← grouping function
← getCreateFields() / shared projection
← MOX Field Contract
```

```text
Edit component/template
← renderer data/model
← grouping function
← getEditFields() / shared projection
← MOX Field Contract
```

必须记录每一步的：

- 文件；
- 函数/computed；
- 输入 shape；
- 输出 shape；
- group key；
- renderer 实际遍历字段。

明确独立 Review 中“断裂”发生的唯一具体位置。

---

## 7. Step 3：修复 group model，不改变 Contract 语义

目标模型必须直接保持 Field Contract 的 `group`：

```text
客户信息
无线格局
微波格局
作战情况
```

### 7.1 不允许语义压缩

禁止任何映射把：

```text
无线格局 + 微波格局
```

转换为：

```text
业务格局
```

### 7.2 不允许只修字段列表

如果 `getCreateFields()` / `getEditFields()` 已经返回完整字段，但 renderer 输入结构丢了 group，则必须修 group model / renderer adapter。

不能通过：

- 在组件里手写无线字段数组；
- 在组件里手写微波字段数组；
- `if (module === 'mox')` 后复制 41 个字段；
- 新建第二份 `MOX_SECTIONS` 字段 Authority；

来绕过真实链路。

### 7.3 通用 renderer

如果共享 renderer 当前只接受 3-section 结构，应将其改造成**按输入 Contract group 动态渲染任意 group 数量**，而不是为 MOX 单独 hard-code 4。

目标行为：

```text
MOX Contract 4 groups → renderer 4 groups
TOB Contract 3 groups → renderer 3 groups
ISP Contract 3 groups → renderer 3 groups
Power Contract 3 groups → renderer 3 groups
Large Enterprise Contract 3 groups → renderer 3 groups
```

共享 renderer 不知道“无线格局/微波格局”的业务含义，只按 group model 渲染。

---

## 8. Step 4：Create / Edit 字段完整性

修复后必须验证实际 renderer 最终拥有：

### Create

```text
客户信息：create-visible 的目标字段
无线格局：orders 7—18 中 create-visible 字段
微波格局：orders 19—28 中 create-visible 字段
作战情况：orders 29—41 中 create-visible 字段
```

### Edit

同理按 `ui.edit.visible=true`。

必须双向验证：

```text
EXPECTED_CREATE_KEYS == ACTUAL_RENDERED_CREATE_KEYS
EXPECTED_EDIT_KEYS == ACTUAL_RENDERED_EDIT_KEYS
```

同时验证：

- missing=0；
- extra=0；
- duplicate=0；
- order 正确；
- group 正确；
- 无“业务格局”group。

---

## 9. Step 5：真实 renderer 测试

新增/重建测试必须覆盖**Production 实际渲染路径**。

最低要求：

1. Create 最终 group 列表精确等于：

```text
客户信息 / 无线格局 / 微波格局 / 作战情况
```

2. Edit 同上；
3. Create 无线格局包含应显示的 7—18 字段；
4. Create 微波格局包含应显示的 19—28 字段；
5. Edit 无线/微波同样完整；
6. “业务格局”不存在于 MOX renderer model；
7. TOB/ISP/Power/Large Enterprise 仍保持 3-group；
8. 如果 renderer 使用 Vue computed / composable，测试必须调用真实 computed/composable 或 mount 到足以验证最终 render model 的层级；
9. 不得再次用一个未被真实 renderer 消费的 helper 作为页面正确性的代理测试。

---

## 10. Step 6：视觉分隔回归

4-group 真正恢复后，确认现有共享 group style 能应用到四组：

- group 标题明显；
- 无线格局、微波格局、作战情况之间有稳定上间距；
- 作战情况不贴住微波最后字段；
- Create/Edit 风格一致。

只修因 4-group 恢复导致的必要样式接入，不进行无关视觉重构。

---

## 11. Step 7：回归保护

必须确认本轮没有破坏当前已收敛能力：

- Customer `customer_id` 查询和选择链；
- Heatmap canonical key；
- canonical-only API / legacy key rejection；
- Progress History 单一事实源；
- 9 Metric；
- TOB/ISP/Power/Large 3-group；
- database/Migration；
- build。

---

## 12. 自动验证顺序

按顺序执行：

1. MOX Field Contract / projection tests；
2. MOX Create runtime render-group tests；
3. MOX Edit runtime render-group tests；
4. Create/Edit 双向 conformance tests；
5. TOB/ISP/Power/Large group regression tests；
6. MOX相关企业测试；
7. enterprise suite；
8. full Vitest；
9. build；
10. lint/typecheck（如配置）。

失败不得通过：

- 删除有效测试；
- 降低 group 数量断言；
- 恢复 3-section 映射；
- 新建硬编码字段列表；

来解决。

---

## 13. 实施报告

创建：

```text
docs/enterprise/remediations/mox-4-group-render-chain-repair-report.md
```

至少记录：

- BASE_HEAD；
- REVIEWED_HEAD；
- FINAL_HEAD；
- 独立 Review 中的 finding id/原文摘要；
- 断裂点文件/函数；
- 修复前调用链；
- 修复后调用链；
- Create 最终 4-group；
- Edit 最终 4-group；
- Create missing/extra/duplicate counts；
- Edit missing/extra/duplicate counts；
- 其他四模块 group 回归；
- tests/build；
- changed files；
- blockers。

---

## 14. 完成门槛

只有全部满足才可 COMPLETE：

1. MOX Create 实际 renderer 4-group；
2. MOX Edit 实际 renderer 4-group；
3. 无线格局和微波格局字段真实可进入 renderer；
4. MOX 无“业务格局”；
5. Contract expected == actual renderer keys；
6. Production 和 tests 验证同一真实链；
7. 没有第二字段/group Authority；
8. TOB/ISP/Power/Large 3-group 无回归；
9. Customer/Heatmap/Progress/API canonical/Metric/DB 无回归；
10. enterprise tests/full Vitest/build 通过；
11. 本轮有本地 commit；
12. 工作树最终干净。

---

## 15. 最终短回执

```text
MOX 4-GROUP RENDER CHAIN REPAIR
RESULT=COMPLETE/PARTIAL/BLOCKED
BASE_HEAD=
REVIEWED_HEAD=
FINAL_HEAD=
ROOT_CAUSE=
BROKEN_LINK=
CREATE_GROUPS=客户信息/无线格局/微波格局/作战情况 或实际
EDIT_GROUPS=客户信息/无线格局/微波格局/作战情况 或实际
CREATE_MISSING_FIELDS=0或数量
EDIT_MISSING_FIELDS=0或数量
CREATE_EXTRA_FIELDS=0或数量
EDIT_EXTRA_FIELDS=0或数量
BUSINESS_LANDSCAPE_IN_MOX=NO/YES
OTHER_MODULE_GROUP_REGRESSION=NO/YES
CUSTOMER_REGRESSION=PASS/FAIL
HEATMAP_REGRESSION=PASS/FAIL
PROGRESS_REGRESSION=PASS/FAIL
API_CANONICAL_REGRESSION=PASS/FAIL
METRIC_REGRESSION=PASS/FAIL
ENTERPRISE_TESTS=PASS/FAIL
FULL_TESTS=PASS/FAIL
BUILD=PASS/FAIL
COMMIT=SHA
BLOCKERS=NONE或内容
NEXT=RERUN_MOX_END_TO_END_CANONICAL_REVIEW
```
