# TOB / ISP / 电力 / 大企 Alignment 独立审查 Blocking Findings Remediation V2

**状态：CURRENT BLOCKING REMEDIATION AUTHORITY**  
**适用模块：TOB、ISP、电力、大企**  
**参考实现：当前已通过独立审查的 MOX mechanism**  
**共享架构：`enterprise-contract-architecture-v5.md`**  
**运行时字段规则：`architecture/enterprise-runtime-field-options-contract-v1.md`**  
**前序实施：`remediation/non-mox-modules-mox-reference-alignment-v1.md`**  
**审查规范：`reviews/non-mox-modules-mox-reference-independent-review-v1.md`**  
**本地审查报告：`D:\BattleMap\battle-map\docs\enterprise\reviews\non-mox-modules-mox-reference-independent-review.md`**  
**代码工作树：`D:\BattleMap\battle-map`**  
**代码分支：`feature/enterprise-battle-map`**

---

## 1. 当前结论

最新独立审查发现 **7 个 blocking finding**。

因此前序 Alignment Implementation Report 中的 `PASS` 结论被独立审查推翻，当前正式状态改为：

```text
NON-MOX ALIGNMENT IMPLEMENTATION = NOT VERIFIED
INDEPENDENT REVIEW = FAIL
BLOCKING_FINDINGS = 7
```

本轮不是重新设计 TOB / ISP / 电力 / 大企业务字段，而是严格关闭独立审查报告中的 7 个 finding。

独立审查报告中的 finding 是本轮实施事实输入。Implementation Agent 不得用前一轮 implementation report 的“PASS”覆盖 review finding。

---

## 2. Phase 0：必须先建立 7-Finding Closure Matrix

在修改任何生产代码前，必须完整读取本地独立审查报告：

```text
D:\BattleMap\battle-map\docs\enterprise\reviews\non-mox-modules-mox-reference-independent-review.md
```

将其中全部 **7 个 blocking finding** 原样登记到：

```text
docs/enterprise/remediations/non-mox-alignment-review-findings-closure-matrix.md
```

每个 finding 至少记录：

```text
finding id / title
severity
module(s)
exact file
exact function/component
observed code fact
violated Authority
root cause
planned remediation
production-path test
static/conformance evidence
status = OPEN/IMPLEMENTED/VERIFIED
```

要求：

- finding 数量必须恰好为 7；
- 如果报告有 finding ID，必须原样保留；
- 不允许合并后导致某个 finding 消失；
- 不允许把两个不同 finding 用一句“shared runtime fixed”同时关闭而没有分别证据；
- 如果 review report 与当前 HEAD 不一致，先记录 `HEAD_DRIFT`，不得猜测。

只有 Closure Matrix 建立完成后才能修改代码。

---

## 3. 已确认 Blocking Finding A：共享 Runtime 未真正推广

独立审查已确认：

```text
TOB 使用 shared field-projections.js
ISP / Power / Large 仍保留各自本地实现
```

这违反 Alignment Authority 的核心目标。

### 3.1 目标状态

TOB / ISP / Power / Large 的 Table/Create/Edit Projection 必须由同一共享 runtime projection mechanism 驱动：

```text
Module Field Contract
→ shared projection engine
→ Table/Create/Edit runtime field model
→ shared renderer
```

模块可提供：

- 自己的 Field Contract；
- module id；
- module-specific business behavior registry entry（仅确有差异时）。

模块不得再维护：

- 本地完整 Projection 算法；
- 本地 filter/order/group 算法；
- 本地完整 Create/Edit field schema；
- 与 shared projection 语义重复的 helper。

### 3.2 实施规则

1. 列出 TOB / ISP / Power / Large 当前 Projection 入口和所有调用方；
2. 以已经验证的 shared mechanism 为目标，不复制 TOB 文件到其他模块；
3. ISP / Power / Large 接入 shared projection；
4. 模块差异只由各自 Contract 数据驱动；
5. 本地 duplicate implementation 在消费者归零后删除；
6. MOX regression 必须保持 PASS。

### 3.3 门禁

必须证明：

```text
NON_MOX_SHARED_PROJECTION_CONSUMERS = TOB, ISP, POWER, LARGE
MODULE_LOCAL_DUPLICATE_PROJECTION_IMPLEMENTATIONS = 0
```

并分别验证四模块：

```text
Contract expected table keys == actual table renderer keys
Contract expected create keys == actual create renderer keys
Contract expected edit keys == actual edit renderer keys
```

同时验证 group / order / type / controlId / editorId。

---

## 4. 已确认 Blocking Finding B：Power Heatmap 使用中文 label 作为 field identity

独立审查已确认 Power 页面存在类似：

```text
valueField = "26年空间（跳）"
```

这是 label-as-identity，违反 canonical identity 规则。

Power Authority 对应 canonical key 为：

```text
space2026Hops
```

### 4.1 目标

业务字段 lookup 必须使用 canonical key：

```text
valueField = space2026Hops
```

中文：

```text
26年空间（跳）
```

只能作为 tooltip / title / label 展示文本。

### 4.2 不只修一个字符串

必须重新扫描四模块 Heatmap：

- dimension field；
- value/measure field；
- tooltip field；
- click-filter field；
- transform/aggregation field access；
- `record[...]` lookup。

门禁：

```text
HEATMAP_LABEL_AS_FIELD_IDENTITY = 0
HEATMAP_DB_COLUMN_AS_FRONTEND_IDENTITY = 0
HEATMAP_REFERENCED_CANONICAL_KEYS ⊆ MODULE_FIELD_CONTRACT_KEYS
```

不得改变尚未冻结的 Heatmap 业务公式。

---

## 5. 已确认 Blocking Finding C：Power / Large group 名称错误

独立审查已确认 Power / Large 使用：

```text
业务信息
```

但当前 Authority 明确要求四个 non-MOX 模块为：

```text
客户信息
业务格局
作战情况
```

### 5.1 修复原则

- 正确业务 Authority 名称必须来自各模块 Field Contract `group`；
- 不允许 renderer 再做“业务信息 ↔ 业务格局”别名；
- 不保留 legacy group fallback；
- 不仅修标题文本，还必须确认 field.group 和 runtime group model 一致。

门禁：

```text
TOB_GROUPS   = 客户信息 / 业务格局 / 作战情况
ISP_GROUPS   = 客户信息 / 业务格局 / 作战情况
POWER_GROUPS = 客户信息 / 业务格局 / 作战情况
LARGE_GROUPS = 客户信息 / 业务格局 / 作战情况
```

Create 与 Edit 都必须 exact match。

---

## 6. 已确认 Blocking Finding D：重复 Section / Group 渲染机制

独立审查报告已确认存在重复 section/group renderer 路径。具体文件、组件、循环和调用关系必须以本地 review report 为准，本文件不猜测。

### 6.1 目标状态

页面只能有一条 group render authority：

```text
Field Contract.group
→ shared runtime grouping
→ shared Create/Edit group renderer
```

禁止：

```text
Contract grouping
+
Page-local sections array
+
第二层 section loop
```

或任何等价双重业务分组定义。

### 6.2 实施

- 从 review finding 中恢复全部重复 renderer 路径；
- 确认哪个是 Production 实际消费路径；
- 收敛到 shared renderer；
- 删除无消费者 local section/group schema；
- 不能通过隐藏一个 DOM 层或 CSS `display:none` 声称完成；
- Create/Edit 必须使用相同 shared mechanism。

门禁：

```text
ACTIVE_GROUP_RENDER_ALGORITHMS = 1
MODULE_LOCAL_SECTION_SCHEMA = 0
DUPLICATE_SECTION_RENDER_PATHS = 0
```

---

## 7. 其余 3 个 Blocking Finding

本文件不根据口述猜测剩余 finding。

Implementation Agent 必须从本地独立审查报告中恢复剩余 3 个 finding，并将其分别写入 Closure Matrix。

每个 finding 都必须：

1. 保留 review 原始 finding ID/标题；
2. 记录 exact code fact；
3. 对照当前 Authority 判断根因；
4. 给出最小正确 remediation；
5. 建立修复前可证明问题存在的 test/static evidence；
6. 修复后用同一 evidence 证明关闭；
7. 不扩大到 V0.2 尚未 Authority 化的业务字段变化。

如果其中任何 finding 实际属于 V0.2 业务变化：

```text
STATUS = BLOCKED_BY_V0_2_AUTHORITY
```

不得自行修改字段 Authority。

---

## 8. Implementation Report False-Pass 治理修复

前序 Implementation Report 声称 PASS，但独立代码审查发现 7 个 blocking finding。

这本身说明验证证据不足。

从本轮起，Implementation Report 的每个 PASS 必须引用真实 evidence：

```text
claim
→ file/function
→ production-path test or deterministic scan
→ observed result
```

禁止仅写：

```text
SHARED_RUNTIME=PASS
HEATMAP_CANONICAL=PASS
```

而没有证明。

### 8.1 Closure Matrix 最终格式

每个 finding 最终必须有：

```text
FINDING_ID=
ROOT_CAUSE=
CHANGED_FILES=
PRODUCTION_PATH=
PRE_FIX_EVIDENCE=
POST_FIX_EVIDENCE=
TESTS=
STATUS=VERIFIED
```

Implementation Agent 只能声明：

```text
IMPLEMENTED
```

不得自行把独立审查 finding 标记为最终 VERIFIED。

最终 VERIFIED 仍由新的 Independent Review Agent 决定。

---

## 9. WRITE_SCOPE

允许修改：

- shared runtime projection / runtime field model；
- TOB / ISP / Power / Large 对 shared runtime 的接入；
- shared Create/Edit renderer/group renderer；
- module-local duplicate Projection/section helpers 的清理；
- Power / 其他模块 Heatmap canonical field references；
- Power / Large 错误 group metadata；
- 独立审查报告中其余 3 finding 直接涉及的 shared/non-MOX 实现；
- 对应 Production-path tests / conformance tests；
- Closure Matrix 与 remediation report。

禁止修改：

- MOX 41 个业务字段；
- TOB / ISP / Power / Large 的业务字段集合，除非已有当前 Authority；
- 9 个 Metric 业务公式；
- 企业首页；
- Excel V0.2 尚未 Authority Review 的变化；
- 非企业模块；
- 恢复 legacy alias/fallback/双写。

---

## 10. 修复顺序

严格按以下顺序：

```text
Phase 0 读取7个findings并建立Closure Matrix
→ Shared Projection 真正推广到四模块
→ 收敛重复 Section/Group Renderer
→ 修正 Power/Large group Authority
→ Heatmap canonical identity 全模块扫描/修复
→ 逐个处理其余3个 blocking finding
→ 清理 duplicate/legacy/dead runtime
→ 每模块 Production-path tests
→ MOX regression
→ enterprise/full tests/build
→ Implementation Report
→ 新 HEAD Independent Review
```

不得四模块并行各自重写。

---

## 11. 自动验证门禁

至少执行并记录：

### Shared Runtime

- TOB shared projection consumer；
- ISP shared projection consumer；
- Power shared projection consumer；
- Large shared projection consumer；
- local duplicate projection = 0。

### Create/Edit

四模块：

- dialog opens；
- exact 3 groups；
- Table/Create/Edit bidirectional conformance；
- Runtime Field View Model metadata 来源正确；
- Dynamic Options 正确；
- duplicate section renderer = 0。

### Heatmap

- label-as-identity = 0；
- canonical reference valid；
- Power `space2026Hops` 等字段通过 canonical key lookup。

### Existing shared mechanisms regression

- Customer `customer_id` chain；
- Progress History single source；
- Progress popup；
- Metric engine；
- API canonical-only；
- DB round-trip；
- active legacy key = 0；
- hidden consumer scan。

### Regression

- MOX suite；
- TOB suite；
- ISP suite；
- Power suite；
- Large suite；
- enterprise suite；
- full Vitest；
- build；
- lint/typecheck（如已有）。

---

## 12. 完成标准

Implementation Agent 只有全部满足才能返回 `COMPLETE`：

1. 7 个 review blocking finding 全部在 Closure Matrix 中；
2. 7 个 finding 全部完成 implementation；
3. shared runtime 真正由 TOB / ISP / Power / Large 共同消费；
4. module-local duplicate projection = 0；
5. duplicate section/group renderer = 0；
6. Power/Large group exact Authority；
7. Heatmap label-as-identity = 0；
8. 其余 3 finding 均有独立 closure evidence；
9. MOX regression PASS；
10. full tests/build PASS；
11. Implementation Report 中每个 PASS 均有 evidence；
12. 没有越权实施 V0.2 业务变化。

注意：即使 Implementation Agent 返回 COMPLETE，也只能表示 `IMPLEMENTED`。必须再次独立审查后才能 VERIFIED。

---

## 13. 实施产物

创建/更新：

```text
D:\BattleMap\battle-map\docs\enterprise\remediations\non-mox-alignment-review-findings-closure-matrix.md
D:\BattleMap\battle-map\docs\enterprise\remediations\non-mox-alignment-independent-review-findings-remediation-report-v2.md
```

最终短回执：

```text
NON-MOX ALIGNMENT REVIEW FINDINGS REMEDIATION V2
RESULT=COMPLETE/PARTIAL/BLOCKED
BASE_HEAD=
FINAL_HEAD=
REVIEW_FINDING_COUNT=7或实际
CLOSURE_MATRIX=PASS/FAIL
SHARED_RUNTIME_ALL_4=PASS/FAIL
LOCAL_DUPLICATE_PROJECTIONS=0或数量
DUPLICATE_SECTION_RENDER_PATHS=0或数量
TOB_GROUP=PASS/FAIL
ISP_GROUP=PASS/FAIL
POWER_GROUP=PASS/FAIL
LARGE_GROUP=PASS/FAIL
HEATMAP_LABEL_IDENTITY=0或数量
REMAINING_3_FINDINGS=IMPLEMENTED/PARTIAL/BLOCKED
CUSTOMER_REGRESSION=PASS/FAIL
PROGRESS_REGRESSION=PASS/FAIL
METRIC_REGRESSION=PASS/FAIL
API_DB_REGRESSION=PASS/FAIL
MOX_REGRESSION=PASS/FAIL
FULL_TESTS=PASS/FAIL
BUILD=PASS/FAIL
IMPLEMENTATION_REPORT_EVIDENCE=PASS/FAIL
V0_2_BLOCKERS=NONE或内容
OUT_OF_SCOPE_CHANGES=NO/YES
NEXT=INDEPENDENT_REVIEW/REMEDIATION/V0_2_AUTHORITY_REVIEW
```
