# Non-MOX → MOX Reference Full Independent Review Rerun V3

**状态：CURRENT REVIEW RERUN AUTHORITY**  
**适用模块：TOB、ISP、电力、大企**  
**前置：`remediation/non-mox-alignment-independent-review-findings-remediation-v2.md` 已实施并提交**  
**基础审查 Authority：`reviews/non-mox-modules-mox-reference-independent-review-v1.md`**

---

## 1. 核心纠正

本轮不是“只复核上一轮 7 个 blocking finding”。

修复后的代码 HEAD 发生了实质变化，因此必须把新 HEAD 当成新的审查对象，**从头完整重新执行 `non-mox-modules-mox-reference-independent-review-v1.md` 的全部审查范围**。

上一轮 7 个 blocking finding 仅作为：

```text
KNOWN_FINDINGS_REGRESSION_SET
```

它们必须逐项重新证明关闭，但不得替代新的全量独立审查。

正确关系：

```text
FULL ORIGINAL INDEPENDENT REVIEW
+
KNOWN 7 FINDINGS CLOSURE CHECK
+
NEW REGRESSION / NEW FINDING DISCOVERY
```

不是：

```text
7 FINDINGS ONLY
```

---

## 2. 固定新的 REVIEWED_HEAD

开始前执行：

```text
git branch --show-current
git status --short
git log -1 --oneline
```

要求：

- 分支：`feature/enterprise-battle-map`；
- remediation 已 commit；
- 工作树干净；
- 无写 Agent 并发修改。

固定：

```text
REVIEWED_HEAD=<当前修复后HEAD>
```

审查期间 HEAD 一旦变化：

```text
REVIEW_INVALIDATED_HEAD_CHANGED
```

立即停止。

---

## 3. 必读 Authority

必须完整读取：

```text
enterprise-contract-architecture-v5.md
architecture/enterprise-runtime-field-options-contract-v1.md
mox-canonical-authority-v6.md
remediation/non-mox-modules-mox-reference-alignment-v1.md
reviews/non-mox-modules-mox-reference-independent-review-v1.md
remediation/non-mox-alignment-independent-review-findings-remediation-v2.md
reviews/non-mox-full-independent-review-rerun-v3.md
```

同时读取：

```text
tob-canonical-authority-v2.md
isp-canonical-authority-v2.md
power-canonical-authority-v2.md
large-enterprise-canonical-authority-v2.md
```

以及本地：

```text
上一轮 independent review report
7-finding closure matrix
本轮 remediation report V2
当前真实代码
当前测试
database.js
Migration / SQLite schema
```

Implementation Report 和 Closure Matrix 只是待验证声明，不是事实 Authority。

---

## 4. 必须完整重跑原始 Independent Review

必须重新执行 `non-mox-modules-mox-reference-independent-review-v1.md` 中的全部审查域，不得因上一轮某项曾 PASS 而跳过。

至少从零重新证明以下全部内容。

### 4.1 Shared Runtime Alignment

重新恢复 MOX / TOB / ISP / Power / Large 的真实 Production path：

```text
Field Contract
→ Table Projection
→ Create Projection
→ Edit Projection
→ Runtime Field View Model
→ Dynamic Options
→ Renderer
```

检查：

```text
DUPLICATE_PROJECTION_IMPLEMENTATIONS
MODULE_LOCAL_FORM_SCHEMAS
DUPLICATE_RUNTIME_FIELD_MODEL_IMPLEMENTATIONS
UNUSED_PARALLEL_PROJECTION_APIS
```

目标 blocking 数量全部为 0。

### 4.2 Table / Create / Edit Conformance

四模块分别重新验证：

```text
Contract expected keys == actual Production renderer keys
```

覆盖：

- 缺失；
- 额外；
- 重复；
- order；
- group；
- control/editor；
- visibility/editability。

不得复用上一轮结论。

### 4.3 Runtime Field / Options

重新验证 `fieldDef` 是 type/control/editor/option metadata 的唯一 Authority。

特别重新走真实 Create 初始化链，防止再次出现：

```text
fieldDef.type='select'
f.type=undefined
runtime错误检查f.type
```

### 4.4 Create / Edit Shared UI Mechanism

重新确认四模块真正使用 shared modal shell、shared group renderer、shared spacing、shared validation presentation。

正确 group：

```text
客户信息
业务格局
作战情况
```

检查任何 module-local section schema / renderer / alias。

### 4.5 Customer Relation

重新独立证明：

```text
customers.customer_id
→ shared DB query
→ shared API
→ normalization
→ options
→ unique selection
→ business record.customer_id
```

检查：

```text
PRIVATE_CUSTOMER_FETCH_IMPLEMENTATIONS=0
PRIVATE_CUSTOMER_SQL=0
CUSTOMER_NAME_AS_IDENTITY=0
```

### 4.6 Progress

重新证明：

```text
Progress History = 唯一持久化事实源
battleProgress = latest/current projection
独立Progress弹窗 = History入口
```

检查：

```text
PROGRESS_DOUBLE_WRITE_PATHS=0
PROGRESS_TEXT_FALLBACK_PATHS=0
MODULE_LOCAL_PROGRESS_PERSISTENCE=0
```

### 4.7 Heatmap

四模块重新扫描所有：

- dimension；
- value/measure；
- tooltip lookup；
- click filter；
- transform；
- record access。

要求：

```text
HEATMAP_REFERENCED_KEYS ⊆ MODULE_FIELD_CONTRACT_KEYS
LABEL_AS_FIELD_IDENTITY=0
DB_COLUMN_AS_FRONTEND_IDENTITY=0
```

### 4.8 Metric / Filter

重新验证 9 个 Metric 的真实实现：

```text
Metric Contract.where
→ calculation
→ click-to-filter
```

检查 `MODULE_LOCAL_METRIC_LOGIC=0`，并确认顶层指标不会被自己的点击筛选反向重算。

### 4.9 Table / Filter / Search / Sort Hidden Consumers

重新全仓企业范围扫描：

```text
中文label作为row identity
DB column直接进入前端业务逻辑
legacy key
module-local column array
module-local filter logic
module-local formatter/parser重复定义
未声明canonical mapping
```

不得只扫描上一轮 finding 涉及文件。

### 4.10 API Canonical-only

逐模块重新验证 Read/Create/Edit：

```text
canonical key
→ API mapping
→ database.js mapping
```

要求：

```text
ACTIVE_LEGACY_KEYS=0
LABEL_PAYLOAD_FIELDS=0
RUNTIME_FALLBACKS=0
DOUBLE_READ_PATHS=0
```

### 4.11 database.js / SQLite

逐模块重新验证：

- canonical mapping 唯一；
- customer_id relation；
- Progress relation；
- CRUD round-trip；
- 新库 / 升级库 Schema 一致；
- migration registry；
- cross-module persistence import = 0；
- legacy runtime mapping = 0。

### 4.12 Duplicate Mechanism / Hidden Consumer Gate

必须重新统计，而不是沿用 remediation report：

```text
DUPLICATE_PROJECTION_IMPLEMENTATIONS
MODULE_LOCAL_FORM_SCHEMAS
PRIVATE_CUSTOMER_FETCH_IMPLEMENTATIONS
PROGRESS_DOUBLE_WRITE_PATHS
LABEL_IDENTITY_LOOKUPS
ACTIVE_LEGACY_KEYS
MODULE_LOCAL_METRIC_LOGIC
UNDECLARED_CANONICAL_CONSUMERS
DUPLICATE_SECTION_RENDER_PATHS
MODULE_LOCAL_SECTION_SCHEMAS
```

### 4.13 测试可信度

重新检查测试本身是否可信：

- 是否真实走 Production path；
- 是否复制字段数组形成第二 Authority；
- 是否只有单向 actual→Contract 检查；
- 是否 mock 掉真正 runtime；
- Create/Edit 是否覆盖真实 options enrichment；
- Progress 是否验证 single-source；
- Heatmap 是否验证 canonical lookup；
- API/DB 是否验证 round-trip。

测试 PASS 但测试路径错误，仍属于 blocking TEST_GAP。

---

## 5. 7 个已知 Finding 是额外必检项

在完整原始审查之外，必须从上一轮 report 恢复全部 7 个 finding，并逐项检查：

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

```text
KNOWN_FINDINGS_CLOSED=7/7
```

但即使 7/7 CLOSED，只要本轮全量重新审查发现新的 blocking finding，整体仍然 FAIL。

---

## 6. 新 Finding 发现机制

本轮必须主动寻找 remediation 引入的新问题。

报告区分：

```text
KNOWN_FINDING_REGRESSION
NEW_BLOCKING_IMPLEMENTATION_NONCONFORMANCE
NEW_BLOCKING_TEST_GAP
NON_BLOCKING_CLEANUP
BLOCKED_BY_V0_2_AUTHORITY
```

不能因为“7个旧问题修完”就停止审查。

---

## 7. Implementation Report Integrity

重新将 remediation report / closure matrix 的每个 PASS 与真实代码比对。

如存在：

```text
REPORT_PASS_BUT_CODE_FAIL
REPORT_ZERO_BUT_SCAN_NONZERO
REPORT_SHARED_BUT_RUNTIME_LOCAL
REPORT_CANONICAL_BUT_LABEL_LOOKUP_EXISTS
REPORT_TESTED_BUT_NOT_PRODUCTION_PATH
```

则：

```text
IMPLEMENTATION_REPORT_INTEGRITY=FAIL
```

并形成 blocking finding。

---

## 8. 自动验证必须完整重跑

至少重新执行：

```text
TOB production-path suite
ISP production-path suite
Power production-path suite
Large production-path suite
MOX regression suite
Customer relation tests
Progress tests
Heatmap canonical tests
Metric tests
API/database tests
enterprise suite
full Vitest
build
lint/typecheck（如已有）
```

不得只跑与 7 个 finding 直接相关的测试。

---

## 9. V0.2 边界

本轮完整审查仍以当前正式业务 Authority 为准。

如果某问题明确只来自尚未 Authority 化的 Excel V0.2 业务变化：

```text
BLOCKED_BY_V0_2_AUTHORITY
```

不得在审查中修复，也不得借此掩盖现有 V0.1 implementation nonconformance。

---

## 10. 报告

覆盖更新：

```text
D:\BattleMap\battle-map\docs\enterprise\reviews\non-mox-modules-mox-reference-independent-review.md
```

报告必须是一份完整的新 HEAD 独立审查，不是仅追加“7 finding closure”附录。

至少包含：

- REVIEWED_HEAD；
- full shared runtime call graph；
- 四模块全量 conformance；
- Customer；
- Progress；
- Heatmap；
- Metric；
- API/DB；
- hidden consumers；
- duplicate mechanisms；
- test credibility；
- known 7 finding closure table；
- NEW findings；
- implementation report integrity；
- tests/build；
- V0.2 blockers。

---

## 11. PASS 条件

只有同时满足：

```text
FULL_ORIGINAL_REVIEW_COMPLETED=YES
KNOWN_FINDINGS_CLOSED=7/7
NEW_BLOCKING_FINDINGS=0
DUPLICATE_PROJECTION_IMPLEMENTATIONS=0
MODULE_LOCAL_FORM_SCHEMAS=0
DUPLICATE_SECTION_RENDER_PATHS=0
PRIVATE_CUSTOMER_FETCH_IMPLEMENTATIONS=0
PROGRESS_DOUBLE_WRITE_PATHS=0
LABEL_IDENTITY_LOOKUPS=0
ACTIVE_LEGACY_KEYS=0
MODULE_LOCAL_METRIC_LOGIC=0
UNDECLARED_CANONICAL_CONSUMERS=0
IMPLEMENTATION_REPORT_INTEGRITY=PASS
MOX_REGRESSION=PASS
FULL_TESTS=PASS
BUILD=PASS
```

才可以 PASS。

---

## 12. 最终短回执

```text
NON-MOX → MOX FULL INDEPENDENT REVIEW RERUN V3
RESULT=PASS/FAIL/PARTIAL
REVIEWED_HEAD=
FULL_ORIGINAL_REVIEW_COMPLETED=YES/NO
KNOWN_FINDINGS_CLOSED=x/7
NEW_BLOCKING_FINDINGS=数量
OPEN_FINDINGS=NONE或ID列表
SHARED_RUNTIME=PASS/FAIL
TOB=PASS/FAIL/BLOCKED_V0_2
ISP=PASS/FAIL/BLOCKED_V0_2
POWER=PASS/FAIL/BLOCKED_V0_2
LARGE=PASS/FAIL/BLOCKED_V0_2
TABLE_CREATE_EDIT_CONFORMANCE=PASS/FAIL
RUNTIME_FIELD_OPTIONS=PASS/FAIL
CUSTOMER_CHAIN=PASS/FAIL
PROGRESS_SINGLE_SOURCE=PASS/FAIL
HEATMAP_CANONICAL=PASS/FAIL
METRIC_ENGINE=PASS/FAIL
API_CANONICAL_ONLY=PASS/FAIL
DATABASE_ROUNDTRIP=PASS/FAIL
DUPLICATE_PROJECTION_IMPLEMENTATIONS=数量
MODULE_LOCAL_FORM_SCHEMAS=数量
DUPLICATE_SECTION_RENDER_PATHS=数量
PRIVATE_CUSTOMER_FETCH_IMPLEMENTATIONS=数量
PROGRESS_DOUBLE_WRITE_PATHS=数量
LABEL_IDENTITY_LOOKUPS=数量
ACTIVE_LEGACY_KEYS=数量
MODULE_LOCAL_METRIC_LOGIC=数量
UNDECLARED_CANONICAL_CONSUMERS=数量
IMPLEMENTATION_REPORT_INTEGRITY=PASS/FAIL
MOX_REGRESSION=PASS/FAIL
FULL_TESTS=PASS/FAIL
BUILD=PASS/FAIL
V0_2_BLOCKERS=NONE或内容
BLOCKING_FINDINGS=NONE或内容
NEXT=USER_MANUAL_ACCEPTANCE/REMEDIATION/V0_2_AUTHORITY_REVIEW
```
