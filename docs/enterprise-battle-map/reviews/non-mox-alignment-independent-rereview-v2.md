# Non-MOX Alignment Independent Re-Review V2

**状态：CURRENT RE-REVIEW AUTHORITY**  
**适用模块：TOB、ISP、电力、大企**  
**前置：`non-mox-alignment-independent-review-findings-remediation-v2.md` 已实施并提交**  
**目标：独立证明上一轮 7 个 blocking finding 全部真实关闭，且实施报告与代码事实一致**

---

## 1. 审查性质

本轮只读，禁止修改生产代码、测试、Migration、SQLite、业务 Authority。

必须固定：

```text
REVIEWED_HEAD=<修复后的代码HEAD>
```

审查期间 HEAD 变化则立即返回：

```text
REVIEW_INVALIDATED_HEAD_CHANGED
```

---

## 2. 必读

- `enterprise-contract-architecture-v5.md`
- `architecture/enterprise-runtime-field-options-contract-v1.md`
- `mox-canonical-authority-v6.md`
- `remediation/non-mox-modules-mox-reference-alignment-v1.md`
- `reviews/non-mox-modules-mox-reference-independent-review-v1.md`
- `remediation/non-mox-alignment-independent-review-findings-remediation-v2.md`
- 本地上一轮 independent review report
- 本地 7-finding closure matrix
- 本地 remediation report V2
- 当前真实代码、测试、database.js、Migration/SQLite

---

## 3. 第一门禁：7 Finding Closure Matrix 必须逐项独立复核

从上一轮独立审查报告恢复全部 7 个 blocking finding。

对每个 finding 独立验证：

```text
FINDING_ID
PREVIOUS_CODE_FACT
REMEDIATION_CLAIM
CURRENT_CODE_FACT
PRODUCTION_PATH
TEST_EVIDENCE
STATIC_EVIDENCE
STATUS=CLOSED/OPEN
```

要求：

- finding 数量必须恰好为 7；
- 不允许 implementation report 自述替代代码证据；
- 任何一项 OPEN，则整体 FAIL；
- 如 finding 被“删除测试/改变断言/改文档”而非修复生产路径关闭，仍判 OPEN。

---

## 4. 已知关键 Finding 必须重新证明

### 4.1 Shared Runtime 真正推广到四模块

必须证明：

```text
TOB
ISP
Power
Large
```

全部消费同一 shared runtime / projection mechanism。

检查：

```text
LOCAL_DUPLICATE_PROJECTIONS=0
MODULE_LOCAL_FORM_SCHEMAS=0
DUPLICATE_RUNTIME_FIELD_MODEL_IMPLEMENTATIONS=0
```

不得只因为文件名类似或 helper 被 import 就判 PASS；必须追实际 Create/Edit/Table production path。

### 4.2 Heatmap canonical identity

Power 之前存在：

```text
valueField="26年空间（跳）"
```

必须确认已改为 canonical key：

```text
space2026Hops
```

并扫描四模块所有 Heatmap：

- dimension
- value/measure
- tooltip lookup
- click filter
- transform
- record access

目标：

```text
HEATMAP_LABEL_AS_FIELD_IDENTITY=0
```

### 4.3 Group Authority

TOB / ISP / Power / Large Create/Edit 顶层 group 必须精确为：

```text
客户信息
业务格局
作战情况
```

Power / Large 不得残留：

```text
业务信息
```

禁止 alias/fallback。

### 4.4 Section / Group Renderer 单一路径

必须证明：

```text
Field Contract.group
→ shared runtime grouping
→ shared Create/Edit group renderer
```

目标：

```text
DUPLICATE_SECTION_RENDER_PATHS=0
MODULE_LOCAL_SECTION_SCHEMA=0
```

---

## 5. 其余 3 Finding

必须从上一轮独立审查报告按原 finding ID 和代码事实逐项恢复并复核。

不得概括为“其他问题已修”。

任何一项无法从代码和真实 production path 证明关闭，判 OPEN。

---

## 6. 报告真实性门禁

将 remediation report 中每一项 PASS 与代码事实对照。

如存在任一：

```text
REPORT_PASS_BUT_CODE_FAIL
REPORT_ZERO_BUT_SCAN_NONZERO
REPORT_SHARED_BUT_RUNTIME_LOCAL
REPORT_CANONICAL_BUT_LABEL_LOOKUP_EXISTS
```

则记录：

```text
IMPLEMENTATION_REPORT_INTEGRITY=FAIL
```

整体审查 FAIL。

---

## 7. 端到端回归

在 7 finding 全 CLOSED 后，还必须验证：

- Table/Create/Edit bidirectional Contract Conformance；
- Runtime Field options 使用 fieldDef/Contract metadata；
- Customer customer_id shared chain；
- Progress History single source；
- Progress popup；
- Progress double write/fallback = 0；
- Metric calculation/click-filter same where；
- API canonical-only；
- database.js / SQLite round-trip；
- active legacy key = 0；
- undeclared canonical consumer = 0；
- MOX regression；
- TOB/ISP/Power/Large suites；
- enterprise suite；
- full Vitest；
- build；
- lint/typecheck（如已有）。

---

## 8. V0.2 边界

本轮只验证现有 V0.1 Authority 下的实现机制。

如果差异明确属于尚未 Authority 化的 V0.2 业务字段变化，标记：

```text
BLOCKED_BY_V0_2_AUTHORITY
```

不得修复或自行解释。

---

## 9. 输出报告

覆盖更新：

```text
D:\BattleMap\battle-map\docs\enterprise\reviews\non-mox-modules-mox-reference-independent-review.md
```

并追加明确的 `RE-REVIEW V2` section，记录：

- REVIEWED_HEAD；
- 7-finding closure table；
- implementation report integrity；
- remaining duplicate mechanisms；
- remaining label identity；
- remaining wrong groups；
- remaining hidden consumers；
- tests/build。

---

## 10. 完成条件

只有同时满足以下条件才可 PASS：

```text
7_FINDINGS_CLOSED=7/7
SHARED_RUNTIME_ALL_4=PASS
LOCAL_DUPLICATE_PROJECTIONS=0
DUPLICATE_SECTION_RENDER_PATHS=0
HEATMAP_LABEL_IDENTITY=0
WRONG_GROUP_NAMES=0
IMPLEMENTATION_REPORT_INTEGRITY=PASS
ACTIVE_LEGACY_KEYS=0
UNDECLARED_CONSUMERS=0
MOX_REGRESSION=PASS
FULL_TESTS=PASS
BUILD=PASS
```

否则整体结果必须为 FAIL/PARTIAL。

最终短回执：

```text
NON-MOX ALIGNMENT INDEPENDENT RE-REVIEW V2
RESULT=PASS/FAIL/PARTIAL
REVIEWED_HEAD=
FINDINGS_CLOSED=x/7
OPEN_FINDINGS=NONE或ID列表
SHARED_RUNTIME_ALL_4=PASS/FAIL
LOCAL_DUPLICATE_PROJECTIONS=数量
DUPLICATE_SECTION_RENDER_PATHS=数量
WRONG_GROUP_NAMES=数量
HEATMAP_LABEL_IDENTITY=数量
IMPLEMENTATION_REPORT_INTEGRITY=PASS/FAIL
CUSTOMER_CHAIN=PASS/FAIL
PROGRESS_SINGLE_SOURCE=PASS/FAIL
METRIC_ENGINE=PASS/FAIL
API_DB=PASS/FAIL
ACTIVE_LEGACY_KEYS=数量
UNDECLARED_CONSUMERS=数量
MOX_REGRESSION=PASS/FAIL
FULL_TESTS=PASS/FAIL
BUILD=PASS/FAIL
V0_2_BLOCKERS=NONE或内容
BLOCKING_FINDINGS=NONE或内容
NEXT=USER_MANUAL_ACCEPTANCE/REMEDIATION/V0_2_AUTHORITY_REVIEW
```
