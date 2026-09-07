# 企业五模块：完整独立审查重跑 V3

**状态：CURRENT REVIEW RERUN AUTHORITY**  
**适用模块：MOX、TOB、ISP、电力、大企；五模块均验证真实 Create/Edit 生产路径**  
**前置：TOB 真实共享表单路径定向修复、共享表单 V3 与 `remediation/five-module-shared-operation-convergence-v1.md` 修复已实施并提交；本地审查者核实报告与实际 HEAD**  
**阶段：用户已报告实施完成，当前为 IMPLEMENTED_REPORTED / PENDING_INDEPENDENT_REVIEW，尚未 VERIFIED**  
**基础审查 Authority：`reviews/non-mox-modules-mox-reference-independent-review-v1.md`**

---

## 1. 核心纠正

本轮不是“只复核上一轮 7 个 blocking finding”。

修复后的代码 HEAD 发生了实质变化，因此必须把新 HEAD 当成新的审查对象，**从头完整重新执行 `non-mox-modules-mox-reference-independent-review-v1.md` 的全部审查范围**。

历史 7 个 blocking finding，加上后续完整审查发现的 module-local form builders 等全部未关闭问题，共同作为：

```text
KNOWN_FINDINGS_REGRESSION_SET
```

它们必须逐项重新证明关闭，但不得替代新的全量独立审查。

正确关系：

```text
FULL ORIGINAL INDEPENDENT REVIEW
+
ALL KNOWN FINDINGS CLOSURE CHECK
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
- 共享表单 V3 和共享操作链 V1 remediation 均已 commit；
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
remediation/five-module-shared-form-renderer-convergence-v3.md
remediation/five-module-shared-operation-convergence-v1.md
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
上一轮 independent review report（覆盖更新前先归档）
历史 7-finding closure matrix 与后续新增 findings
历史 remediation report V2
历史 docs/enterprise/remediations/five-module-shared-form-renderer-convergence-report-v3.md
本轮 docs/enterprise/remediations/five-module-shared-operation-convergence-plan-v1.md
本轮 docs/enterprise/remediations/five-module-shared-operation-convergence-report-v1.md
本轮 docs/enterprise/remediations/five-module-shared-operation-convergence-findings-v1.md
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

五模块分别重新验证：

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

重新确认五模块真正使用同一个 shared form shell、shared group renderer、shared field renderer、shared control/editor registry 和 shared validation presentation，逐模块覆盖 Create 与 Edit 共十条真实入口。

正确 group：MOX 为客户信息、无线格局、微波格局、作战情况四组；TOB/ISP/Power/Large 为客户信息、业务格局、作战情况三组。

业务字段总数基线分别为 MOX 41、TOB 34、ISP 25、Power 28、Large 26。各视图 expected keys 必须依据 Contract 的 visibility/mode 派生，不能把总字段数直接当成 Create/Edit 可见字段数。

检查任何 module-local section schema / renderer / alias。必须追到 actual Vue render tree；shared shell 内的 module-local body、shared 文件中的五套完整模板、只 import 不消费、测试 mock 掉 renderer 均不能证明共享。

每模块记录 page/action → Contract → Projection → Runtime Field → Options → Shell → Group → Field → actual render tree 的 file:function/component 和测试证据。独立重算以下数量：

```text
MODULE_LOCAL_FORM_HTML_BUILDERS=0
MODULE_LOCAL_SECTION_SCHEMAS=0
DUPLICATE_SECTION_RENDER_PATHS=0
DUPLICATE_FIELD_RENDERERS=0
DUPLICATE_FORM_SHELLS=0
DUPLICATE_VALIDATION_RENDERERS=0
```

静态搜索结果必须逐项分类，不能把不同模块合法的业务 Contract、adapter 或展示 label 误报成重复机制。

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

## 5. 全部历史 Finding 是额外必检项

在完整原始审查之外，必须从覆盖更新前的历史 report、closure matrix 和后续完整复审恢复全部 finding，保留原 ID。历史 7 个与后续 renderer findings 均不得漏项；逐项检查：

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
KNOWN_FINDINGS_CLOSED=N/N
```

N 是实际恢复出的全部必检历史 finding 数量，至少包含原 7 个及后续 renderer finding；不得虚构 ID 或以固定 7 为上限。历史记录缺失时标记 EVIDENCE_GAP，继续可完成的审查，但不能声称全部关闭或整体 PASS。

即使 N/N CLOSED，只要新审查发现 blocking finding，整体仍然 FAIL。

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
shared form renderer tests
architecture/static duplicate gates
MOX Create/Edit production-path suite
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

先把原报告逐字归档至 `docs/enterprise/reviews/history/non-mox-modules-mox-reference-independent-review-before-<REVIEWED_HEAD>.md`（使用完整40位 SHA）。若同名归档已存在，校验内容一致后复用，不覆盖不同内容。然后覆盖更新：

```text
D:\BattleMap\battle-map\docs\enterprise\reviews\non-mox-modules-mox-reference-independent-review.md
```

报告必须是一份完整的新 HEAD 独立审查，不是仅追加“7 finding closure”附录。

至少包含：

- REVIEWED_HEAD；
- full shared runtime call graph；
- 五模块全量 conformance；
- Customer；
- Progress；
- Heatmap；
- Metric；
- API/DB；
- hidden consumers；
- duplicate mechanisms；
- test credibility；
- 全部历史 finding closure table（含原 7 个和后续 renderer finding）；
- NEW findings；
- implementation report integrity；
- tests/build；
- V0.2 blockers。

---

## 11. PASS 条件

只有同时满足：

```text
FULL_ORIGINAL_REVIEW_COMPLETED=YES
KNOWN_FINDINGS_CLOSED=N/N
NEW_BLOCKING_FINDINGS=0
DUPLICATE_PROJECTION_IMPLEMENTATIONS=0
MODULE_LOCAL_FORM_SCHEMAS=0
MODULE_LOCAL_FORM_HTML_BUILDERS=0
MODULE_LOCAL_SECTION_SCHEMAS=0
DUPLICATE_FIELD_RENDERERS=0
DUPLICATE_FORM_SHELLS=0
DUPLICATE_VALIDATION_RENDERERS=0
FIVE_MODULE_CREATE_EDIT_RENDER_PATHS=PASS
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
KNOWN_FINDINGS_CLOSED=x/N
KNOWN_FINDINGS_TOTAL=N
NEW_BLOCKING_FINDINGS=数量
OPEN_FINDINGS=NONE或ID列表
SHARED_RUNTIME=PASS/FAIL
MOX=PASS/FAIL
FIVE_MODULE_CREATE_EDIT_RENDER_PATHS=PASS/FAIL/NOT_RUN
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


## 13. 本轮执行边界与证据完整性

本节补充并优先于基础 V1 中与本轮五模块范围、历史 finding 数量或报告写入边界冲突的旧表述；其余原始审查域全部保留。

- 使用新的独立 Agent 会话审查。实施报告是待验证声明，不能替代独立读取生产代码。
- Authority 镜像固定为 `D:\BattleMap\BattleMapenterprise-authority`，先在该目录执行 `git pull --ff-only origin enterprise-battle-map-authority`；记录 AUTHORITY_HEAD。更新失败时报告，不 reset/rebase/clean 或用旧规范冒充已更新。
- 代码工作树固定为 `D:\BattleMap\battle-map`，分支必须为 `feature/enterprise-battle-map`。记录完整 REVIEWED_HEAD、工作树状态，并核对 V3 报告的 BASE_HEAD / FINAL_HEAD 与 Git 历史。不在审查中代替实施者提交未完成代码。
- 若报告 FINAL_HEAD 为报告提交之前的实现 SHA，必须证明它是 REVIEWED_HEAD 的祖先，且其后差异仅为报告/证据文件；若含生产代码、测试、配置或 Migration 变更，不得按同一实现宣称匹配。
- 审查只允许写本节指定的报告、历史归档和证据目录。不得修改生产代码、现有测试、Migration、业务 Authority；不执行 git commit、merge 或 push。
- 证据目录固定为 `docs/enterprise/reviews/evidence/five-module-full-review/<REVIEWED_HEAD>/`，保存 commands.md（命令、工作目录、退出码、时间）、测试/build日志和扫描结果。不得依赖聊天中不可追溯的 PASS。
- 从 package.json 和现有测试配置确定真实命令，不编造 suite 名称或补写测试。缺少必要 production-path 测试记为 BLOCKING_TEST_GAP。
- 测试与迁移使用隔离临时数据库/副本，不连接或改写用户业务数据库。启动应用仅使用隔离测试数据。无法安全隔离时记录该验证 NOT_RUN 和具体原因。
- HEAD 固定期间完成整个审查；结束重新检查 HEAD 和 git diff。允许上述报告/证据路径变更及已识别的忽略态测试/build临时输出；其他受审源码/测试/配置变化即使 HEAD 未变也使审查失效，记录 REVIEW_INVALIDATED_WORKTREE_CHANGED。
- 每条 finding 附 ID、严重度、file:function/行号、违反的 Authority 条款、实际生产路径、复现或测试证据、影响和修复方向；不得现场修复。
- 必需验证未运行、证据不足或环境阻塞时 RESULT=PARTIAL，相关项使用 NOT_RUN/BLOCKED，不可记 PASS；已确认阻塞缺陷时 RESULT=FAIL。仅记录纯 Excel V0.2 未来需求差异不影响当前冻结基线的机制结论，但不得声称 V0.2 已验收。
- 只有全部审查和必要自动验证通过、无 blocking finding、HEAD/受审文件未变时 RESULT=PASS，NEXT=USER_MANUAL_ACCEPTANCE；人工验收仍为 PENDING。发现实现/测试缺陷则 NEXT=REMEDIATION；仅证据不足则 NEXT=COMPLETE_REVIEW_EVIDENCE。
- 最终回执在第12节基础上附 AUTHORITY_HEAD、HEAD_UNCHANGED、REVIEWED_SOURCE_UNCHANGED、REPORT_PATH、EVIDENCE_DIR、MANUAL_ACCEPTANCE=PENDING。不要求上传本地代码或报告；用户可直接复制短回执。

## 14. 共享操作链修复后的必检项

用户已报告 Shared Operation Convergence V1 修复完成。本轮是新 HEAD 的完整独立复审，不能沿用前次 PASS，也不能仅检查本轮修复文件。

### 14.1 恢复本轮身份与声明

读取第3节新增的计划、实施报告、finding 矩阵和其引用的原始证据；核对 REVIEWED_HEAD（前次）、BASE_HEAD、IMPLEMENTATION_HEAD、FINAL_HEAD 的祖先关系与差异。当前审查固定新的 REVIEWED_HEAD。
若 IMPLEMENTATION_HEAD 后有仅报告/证据提交，记录 docs-only 关系；如还有受审源码/测试/配置变更，必须重新检查这些变化，不将旧测试结果作为新 HEAD 证据。

### 14.2 五模块真实操作路径

从前次阻塞报告恢复全部受影响操作，独立核实计划的操作清单是否遗漏同根因消费者。逐操作、逐模块追踪：
真实 UI/事件入口 → handler → Contract/config → 共享机制 → 模块 adapter → API/持久化（如适用）→ 结果与页面状态刷新。

对实际存在的表格加载/刷新、搜索/筛选/排序、指标计算与点击筛选、Heatmap交互、客户关联、Progress弹窗及报告涉及的其他操作执行检查。不要求新增不存在的操作。

每条路径记录 file:function/component、生产消费者、可信测试与实际行为。明确区分共性机制和合法业务差异，不把模块 Contract、薄 adapter 或独立状态实例误算为重复机制。
判定失败的情形包括：仅提取 helper 但主路径仍重复、共享外壳加本地完整处理链、shared 文件内五套完整业务分支、生产路径绕过共享实现、测试 mock 掉待验证机制。

### 14.3 行为与回归

除共享结构，还要核实操作结果：筛选/重置/刷新状态正确；指标点击不会反向重算顶部统计；customer_id 不丢失；Progress History 单一事实源且写后读一致；模块状态隔离。根据真实异步风险检查旧响应覆盖、重复提交等已有场景。
保持各模块业务字段、Metric/Heatmap口径和必要 adapter 边界。完整回归五模块 V3 Create/Edit、Customer/Progress/Heatmap/Metric/API/DB 与原始审查全部门禁。

### 14.4 Finding 闭环与结果

本轮 finding 矩阵中的 IMPLEMENTED_PENDING_REVIEW 只是待核实声明。恢复全部历史问题，逐项以新 HEAD 的生产路径与测试证据决定 CLOSED/OPEN；REVIEW_REQUIRED 不能静默撤销。
任何新的 blocking finding、漏掉的生产消费者、实现与报告不一致、关键 production-path TEST_GAP 都阻止整体 PASS。

在完整审查报告中增加：
- 五模块共享操作路径矩阵；
- 本轮修复声明与独立核验对照；
- 活动重复操作机制及合法差异清单；
- 新旧 findings 与实际证据；
- 本轮测试命令、退出码和日志位置。

新增 PASS 条件：
SHARED_OPERATION_PRODUCTION_PATHS=PASS
DUPLICATE_ACTIVE_OPERATION_MECHANISMS=0
OPERATION_BEHAVIOR_REGRESSION=PASS
MODULE_STATE_ISOLATION=PASS
值必须来自独立证据；数量只统计违反既有共享要求的活动重复机制，不能机械计算全部模块 handler。

最终短回执附上述四项和 V3_CREATE_EDIT_REGRESSION。所有必检项通过才 NEXT=USER_MANUAL_ACCEPTANCE；存在缺陷则 NEXT=REMEDIATION；缺验证证据则 NEXT=COMPLETE_REVIEW_EVIDENCE。
本轮只读审查，沿用第10/13节的固定报告/证据路径、旧报告归档和 HEAD/受审文件稳定性规则；不要现场修复或提交代码。

## 15. TOB 定向修复后的完整复审入口

用户报告 TOB Shared Form Production Path Repair V1 已修复。本轮使用新的独立会话，固定修复后的新 REVIEWED_HEAD；前次“已共享”声明与测试 PASS 都不能替代当前代码证据。

额外完整读取：
- Authority：remediation/tob-shared-form-production-path-repair-v1.md；
- 本地：docs/enterprise/remediations/tob-shared-form-production-path-plan-v1.md；
- 本地：docs/enterprise/remediations/tob-shared-form-production-path-report-v1.md；
- 对应 evidence/tob-shared-form-repair/<BASE_HEAD>/ 下的原报告、测试与门禁证据。

按第13节核对实现提交、报告提交和当前 HEAD，检查是否还有未提交的受审代码。先对以下内容取证，再继续完整审查；发现缺陷应记录并继续其他可独立完成的检查。

1. 分别从 TOB 页面实际 Create/Edit 动作追到最终 render tree，证明确实消费已有唯一 shared shell/group/field renderer，未绕回本地完整 builder。
2. 核实旧本地构建器、替代入口、完整 slot body、条件 fallback、重复 group/控件分发的活动消费者均已清理。
3. 将 .map() 按输入、输出、实际消费者分类；合法数据投影、薄绑定、共享 renderer 内部迭代不能误报，改写循环语法也不能当作修复。
4. 检查真实页面入口测试是否挂载实际共享 renderer；不能通过 mock/stub 待验证机制、只检查 import/props 或调用未被生产消费的 helper 获得 PASS。
5. 审核修复前快照/隔离实验的证据，确认补强的门禁确实能够识别旧本地 builder，且失败原因对应目标架构缺陷。不得在受审工作树回退或改写代码；证据不足记 TEST_GAP/EVIDENCE_GAP。
6. 核实 TOB 字段视图、三组结构、Options、客户身份/只读规则、Progress入口和提交/取消/重开行为正确，同时回归其余四模块。

本节是强制专项，不能替代第1—14节。必须完成五模块所有原始审查域、全部历史 findings、新问题发现和必要自动验证；报告中单独列出 TOB 的修复前后路径与防漏检证据。

在原有 PASS 条件和最终短回执中补充：
TOB_CREATE_USES_SHARED_RENDERER=PASS/FAIL/NOT_RUN
TOB_EDIT_USES_SHARED_RENDERER=PASS/FAIL/NOT_RUN
TOB_LOCAL_FULL_FORM_BUILDERS=数量或NOT_ASSESSED
OLD_TOB_FORM_CONSUMERS=数量或NOT_ASSESSED
REGRESSION_GATE_DETECTS_LOCAL_BUILDER=PASS/FAIL/NOT_RUN

TOB两条入口、补强门禁必须PASS，活动本地完整builder/旧消费者必须为0；同时其他必需门禁通过且无blocking finding，才整体PASS并进入USER_MANUAL_ACCEPTANCE。
报告/历史归档/证据目录继续使用第10/13节指定路径，不另建平行最终报告。实施记录只作为输入，不现场修复，不改测试、不提交、不上传。
