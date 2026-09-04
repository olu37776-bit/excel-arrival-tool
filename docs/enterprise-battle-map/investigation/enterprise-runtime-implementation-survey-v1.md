# 企业作战地图：Enterprise Runtime Implementation Survey V1

**状态：CURRENT INVESTIGATION AUTHORITY**  
**性质：只读事实调查，不实施修复，不重构，不修改业务 Authority**  
**代码长期分支：`feature/enterprise-battle-map`**  
**代码主工作树：`D:\BattleMap\battle-map`**  
**本地 Authority 镜像：`D:\BattleMap\BattleMapenterprise-authority`**  
**调查对象：当前合并后的企业模块实际运行链路与现有 Authority 的真实落地情况**

---

## 1. 为什么需要本次调查

当前企业板块已经完成多轮 Contract、页面、数据库和并行模块建设，但人工验收仍发现：

- MOX 新增/编辑最终 UI 与期望存在偏差；
- MOX Contract 调查已发现多个 HIGH finding；
- TOB / ISP / 电力 / 大企曾出现“获取客户数据失败”；
- 作战进展仍存在特殊弹窗/历史机制，当前 Field Contract 与真实持久化关系尚未完全恢复；
- Heatmap 已存在于多个页面，但共享架构与真实数据流尚未形成完整事实图；
- `database.js` 同时承担 Schema、Migration、CRUD、字段映射和 Validation，合并后的真实模块边界需要重新恢复；
- 测试曾通过但人工仍发现明显问题，说明需要核实测试到底覆盖了哪些真实运行消费者。

因此本调查不再基于“应该怎么设计”推断当前实现，而是从代码、测试、Migration 和 SQLite 事实反向恢复当前系统。

目标回答：

```text
Authority 规定了什么？
当前代码实际做了什么？
哪一层发生了偏离？
哪些共享机制真的共用？
哪些只是文档上共用？
哪些隐性消费者尚未被现有 Contract / Validator 覆盖？
```

---

## 2. 调查执行安全规则

本调查必须针对一个固定代码提交：

```text
SURVEY_HEAD=<SHA>
```

### 2.1 启动条件

如果 `D:\BattleMap\battle-map` 当前仍有 Implementation / Remediation Agent 正在写代码，或者工作树存在未提交修改：

- 不得直接在变化中的工作树上执行正式调查；
- 可以先等待当前写任务提交完成；
- 或由操作者提供一个独立只读 worktree 路径，再针对固定 SHA 调查；
- 调查 Agent 不得自行猜测或创建新的本地目录。

正式调查开始后必须记录：

```powershell
git -C "D:\BattleMap\battle-map" branch --show-current
git -C "D:\BattleMap\battle-map" status --short
git -C "D:\BattleMap\battle-map" rev-parse HEAD
git -C "D:\BattleMap\battle-map" worktree list --porcelain
```

如果调查使用的工作树不是主工作树，报告必须记录其精确路径。

### 2.2 只读规则

禁止：

- 修改生产代码；
- 修改测试；
- 修改 Migration；
- 修改数据库文件；
- 自动执行 remediation；
- 自动格式化；
- reset / rebase / clean；
- 根据调查结果直接重构；
- 为了“验证想法”增加临时代码并留在工作树。

允许：

- 读取源代码；
- 读取测试；
- 读取 SQL；
- 使用只读/临时数据库副本执行查询；
- 运行不会修改源代码的测试与 build；
- 运行静态搜索；
- 创建调查报告文档。

---

## 3. 必读 Authority

开始前至少读取：

1. `authority-index.md`；
2. `enterprise-contract-architecture-v3.md`；
3. `mox-canonical-authority-v4.md`；
4. `tob-canonical-authority-v2.md`；
5. `isp-canonical-authority-v2.md`；
6. `power-canonical-authority-v2.md`；
7. `large-enterprise-canonical-authority-v2.md`；
8. `integration/parallel-module-integration-plan-v1.md`；
9. `integration/local-worktree-layout-v1.md`；
10. 当前 remediation / review 文档；
11. 当前代码仓库中的 implementation / integration / review / remediation reports。

调查时 Authority 用于定义“目标”；当前代码、API、`database.js`、SQLite 和测试用于恢复“实际”。

禁止把旧本地 Schema / config 重新提升为业务需求 Authority。

---

## 4. 最终调查产物

必须创建：

```text
docs/enterprise/investigations/enterprise-runtime-implementation-survey.md
```

报告必须包含以下五类核心产物：

### A. Runtime Topology Map

画出真实链路，例如：

```text
MOX Page
→ table/create/edit consumer
→ Field Contract / Projection
→ API client
→ server route
→ database.js method
→ SQLite table/column
```

以及：

```text
records
→ Metric Engine
→ stats
→ click filter

records / API
→ Heatmap transform
→ HeatmapChart

customer dialog
→ customer request
→ customer API
→ database.js
→ customer table

progress action
→ progress dialog
→ progress API
→ database.js
→ progress persistence
```

不能只写抽象框图，必须写真实文件、函数、endpoint、表名。

### B. Module Conformance Matrix

每个模块分别列：

```text
Field Contract
Table Projection
Create Projection
Edit Projection
Metric Contract
Heatmap
API
Persistence / DB
Customer
Progress
Tests
```

每项状态只能是：

```text
IMPLEMENTED_AS_AUTHORITY
PARTIAL
NOT_IMPLEMENTED
EXTRA_IMPLEMENTATION
UNKNOWN
```

### C. Canonical Key Flow Matrix

至少选择各模块代表性字段验证：

- relation 字段；
- enum 字段；
- number / amount 字段；
- risk/status 字段；
- progress 字段。

逐层记录：

```text
canonical key
→ UI projection
→ request key
→ server handler key
→ database.js mapping
→ SQLite table.column
→ read response key
→ edit refill
```

MOX 必须覆盖全部 41 key 的 mapping inventory；其他模块至少验证全部 Contract key 是否有 mapping entry，再抽代表字段做深链路。

### D. Hidden Consumer Inventory

找出所有可能改变业务语义但没有在 Authority 中显式表达的消费者：

- 页面本地字段数组；
- 页面本地 Section / group 数组；
- hidden / visible 条件；
- formatter/parser；
- option set；
- store / Pinia 转换；
- composable；
- API client normalization；
- server.js 字段转换；
- `database.js` 中英文映射；
- JSON 初始化；
- Heatmap transform；
- Metric transform；
- Progress transform；
- import/export helper；
- legacy fallback；
- 测试专用配置。

每个 hidden consumer 必须记录：

```text
FILE=
FUNCTION/CONST=
MODULE=
WHAT_SEMANTIC_IT_CAN_CHANGE=
AUTHORITY_GOVERNED=YES/NO/PARTIAL
```

### E. Gap Classification

每个 finding 必须归类为：

```text
IMPLEMENTATION_NONCONFORMANCE
DOCUMENT_GAP
ARCHITECTURE_GAP
TEST_GAP
DEAD_OR_LEGACY_PATH
UNKNOWN_REQUIRES_USER_CONFIRMATION
```

禁止把一个实现 bug 自动升级成 Architecture Gap。

---

## 5. 调查阶段 1：代码与目录真实拓扑

先建立企业相关文件 inventory。

至少覆盖：

```text
src/config/enterprise/**
企业相关 Vue 页面/组件
企业相关 stores/composables/services
server.js 企业 route
企业 API client
数据库相关 JS
migrations/V34...V38
企业测试
docs/enterprise/**
```

记录：

- 当前活动 Contract 文件；
- 是否仍有 `src/enterprise` 活动 Authority；
- 是否仍有旧 `mox-field-schema.js` / duplicate config；
- 是否存在 `*-new` / `*-copy` / `*-v2` 等重复实现；
- 哪些文件仍被实际 import；
- 哪些文件无引用。

输出真实依赖图，不要仅按文件名判断是否活动。

---

## 6. 调查阶段 2：Field Contract → UI Projection → Renderer

针对 MOX、TOB、ISP、电力、大企分别恢复：

```text
Field Contract
→ table projection
→ create projection
→ edit projection
→ renderer
```

必须回答：

1. 当前 Field Contract 文件精确路径；
2. Contract key 数量；
3. section 值集合；
4. table/create/edit projection 函数；
5. 页面实际 import 哪个 Projection；
6. renderer 是否还有二次 filter/group/sort；
7. 是否存在本地字段数组；
8. 是否存在本地 section/group 配置；
9. 特殊控件如何通过 `controlId/editorId`解析；
10. Contract 中 `visible/editable/controlId/section/order` 哪些属性真正被 runtime 使用，哪些只存在但未消费。

### MOX 强制深查

MOX 必须生成：

```text
41 Canonical Fields
→ table visible set
→ create visible set
→ edit visible set
→ rendered section model
```

对人工发现的“4个分组”和审查 Agent 的 5 个 HIGH，逐项追到根因层。

不能只说“renderer uses contract”，必须指出：

```text
哪一个函数形成 group？
它根据哪个属性？
为什么产生第四组？
字段在哪个步骤被漏掉/重分组？
```

---

## 7. 调查阶段 3：API 与 canonical key 转换

恢复企业模块真实 API surface。

每个模块列出：

```text
LIST/READ endpoint
CREATE endpoint
UPDATE endpoint
DELETE endpoint（如有）
CUSTOMER endpoint
PROGRESS endpoint（如有）
HEATMAP endpoint（如有）
```

对每个 endpoint 记录：

```text
METHOD
PATH
FRONTEND_CALLER
SERVER_HANDLER
DATABASE_FUNCTION
REQUEST_SHAPE
RESPONSE_SHAPE
ERROR_SHAPE
```

必须回答：

- canonical key 在哪里进入 API；
- 是否在 frontend client 转换字段名；
- 是否在 server.js 再转换；
- 是否在 `database.js` 再转换；
- 是否存在同一字段三处不同 alias；
- 是否存在旧中文/英文 mapping 仍参与活动请求；
- 是否存在 fallback 或兼容字段；
- 五个模块是否使用相同 API 模式还是各自独立。

---

## 8. 调查阶段 4：database.js 与 SQLite

这是本调查最高优先级之一。

必须恢复 `database.js` 当前真实职责和企业模块分支。

### 8.1 Schema Inventory

列出实际数据库中的：

- customers / 客户主表；
- MOX 表；
- TOB 表；
- ISP 表；
- Power 表；
- Large Enterprise 表；
- Progress 相关表（如有）；
- `_migrations`；
- 相关 index / constraint / foreign key。

每张表记录：

```text
TABLE=
PRIMARY_KEY=
CUSTOMER_ID=
BUSINESS_COLUMNS=
TECHNICAL_COLUMNS=
LEGACY_COLUMNS=
FOREIGN_KEYS=
INDEXES=
```

### 8.2 New DB vs Upgraded DB

调查实际代码是否存在两条 Schema 来源：

```text
新建数据库建表定义
旧数据库 V*.sql migration
```

核实最终 Schema 是否一致。

### 8.3 Migration Chain

核实：

```text
V34
V35
V36
V37
V38
```

分别：

- 文件存在；
- 语义对应模块；
- `database.js` 已注册；
- 执行顺序；
- `_migrations`登记；
- transaction / rollback；
- idempotency；
- 是否存在编号冲突或空壳 migration。

### 8.4 Runtime Mapping

针对每模块验证：

```text
Contract runtime.dbColumn / persistence map
↔ database.js CRUD
↔ SQLite column
```

必须找出：

- DB 中存在但 Authority 不允许的 legacy column；
- Authority 字段有 mapping 但 DB 无 column；
- DB column存在但没有 read/write；
- write 和 read 使用不同 key；
- customer relation 被重复存进业务表；
- progress 数据可能被错误压进普通业务列。

---

## 9. 调查阶段 5：Customer 真实链路

无论当前 remediation 是否已修复，都必须恢复最终真实链：

```text
Create Dialog
→ customer fetch caller
→ client/service/composable
→ endpoint
→ server handler
→ database query
→ customer table
→ normalization
→ region/office/customer selection
→ unique customer_id
```

五个模块分别标记：

```text
MOX=
TOB=
ISP=
POWER=
LARGE_ENTERPRISE=
```

必须回答：

- 是否真正共享一套 customer fetch；
- 若共享，精确共享文件/函数；
- 若不共享，有多少重复实现；
- 模块差异是否只存在 UI projection；
- 编辑时 customer_id 是否保持不变；
- MOX customerCategory 当前如何读写客户主数据。

---

## 10. 调查阶段 6：Progress 真实模型

本阶段只恢复事实，不修改现有 `battleProgress` 设计。

从当前仍可工作的 TOB 进展交互开始追踪：

```text
表格行操作
→ 进展弹窗
→ submit handler
→ API
→ database.js
→ SQLite
→ read / refill
```

必须回答：

1. 一条业务记录能否保存多条进展；
2. 进展是否有独立 ID / 时间 / 用户 / 内容；
3. 数据保存在业务表一列、JSON、还是独立 progress table；
4. `latest_progress` 历史上代表什么；
5. `battleProgress` 当前 runtime 实际代表什么；
6. 新增/追加/编辑分别调用什么；
7. 表格展示的是最新一条、全部、摘要还是普通字段；
8. MOX 当前是否已经真正复用了 TOB 机制；
9. 五个模块是否共享同一 progress 实现。

调查结论只能写事实。

若发现 `battleProgress` 与多条历史进展模型冲突，分类为：

```text
DOCUMENT_GAP 或 ARCHITECTURE_GAP_CANDIDATE
```

但不得自行修改 Authority。

---

## 11. 调查阶段 7：Metric 真实执行链

针对每模块恢复：

```text
records source
→ metric contract
→ metric engine
→ displayed stats
→ active metric
→ table filter
```

必须确认：

- 是否只有一份 Metric Engine；
- 9个指标是否使用当前模块 Metric Contract；
- calculation 和 click-to-filter 是否共用同一 `where`；
- records 是否是 canonical shape；
- 是否存在页面硬编码第二套条件；
- active metric 是否跨模块串状态；
- 顶部统计是否会错误基于筛选结果重算。

---

## 12. 调查阶段 8：Heatmap 真实执行链

Heatmap 是当前共享架构事实不完整的重点调查项。

每个模块分别恢复：

```text
页面
→ Heatmap component
→ data source
→ transform / aggregation
→ HeatmapChart
→ tooltip
→ click behavior
→ table filter（如有）
```

必须回答：

1. MOX / TOB / ISP / Power / Large Enterprise 是否都使用同一个 `HeatmapChart`；
2. Heatmap 输入来自当前页面 records 还是独立 API；
3. 聚合发生在哪个文件/函数；
4. 使用哪些字段，字段是 canonical key / 中文label / DB column中的哪一种；
5. 是否存在模块自己的 transform；
6. 是否已经存在 `*-heatmap-contract.js`；
7. 文档要求存在但实际没有的 Heatmap Contract 有哪些；
8. tooltip规则在哪里；
9. 点击 Heatmap 是否筛选表格；
10. 如果筛选，条件是否和 Heatmap aggregation 使用同一业务定义；
11. Heatmap 当前是否存在 fake/placeholder 数据；
12. 未冻结规则是否正确保持空状态。

结论必须区分：

```text
IMPLEMENTATION_NONCONFORMANCE
DOCUMENT_GAP
ARCHITECTURE_GAP_CANDIDATE
```

---

## 13. 调查阶段 9：State / Store / Composable 隐性转换

搜索企业相关 Pinia、computed、watch、composable、adapter、helper。

记录所有会改变以下内容的逻辑：

- 字段名；
- 默认值；
- Section；
- visible/editable；
- enum；
- customer fields；
- metric records；
- Heatmap records；
- API response shape；
- progress shape。

重点查找：

```text
map/reduce/filter
Object.keys / Object.fromEntries
label-key map
Chinese-English map
legacy alias
fallback
module-specific if/switch
```

这些都是潜在 hidden consumer。

---

## 14. 调查阶段 10：初始化 / Import / Seed 旁路

恢复数据库初始化链：

- JSON 初始化；
- seed data；
- Excel import（如当前存在）；
- localStorage / cache（如存在）；
- mock/fallback data。

必须回答这些入口是否绕过当前 API / mapping / validation 直接写 SQLite。

若旁路能写入 Authority 外字段或旧字段，记录 HIGH finding。

---

## 15. 调查阶段 11：测试真实覆盖能力

不要只统计测试数量。

对当前企业测试分类：

```text
CONTRACT_STRUCTURE
PROJECTION
RENDERER
API
DATABASE
MIGRATION
CUSTOMER
PROGRESS
METRIC
HEATMAP
ROUND_TRIP
ARCHITECTURE_CONFORMANCE
```

必须找出：

- 哪些测试只是字符串存在检查；
- 哪些测试复制 expected field array 形成第二 Authority；
- 哪些测试 mock 掉了真实 Projection / API / DB；
- 是否存在 Create → API → DB → Read → Edit refill round-trip；
- 是否真正验证 rendered section model；
- 是否真正验证 Heatmap input；
- 是否真正验证 progress persistence；
- 哪些人工发现的问题当前测试无法捕获，以及为什么。

输出：

```text
TEST_GAP_MATRIX
```

---

## 16. 调查阶段 12：死代码与旧路径

只调查企业模块及直接依赖。

寻找：

- 无引用旧 Contract；
- 旧 Schema；
- 旧 API client；
- 旧 customer fetch；
- 旧 progress handler；
- old field mapping；
- legacy test；
- duplicate renderer/helper；
- merge 后留下的 duplicate implementation。

本次只登记，不删除。

每项记录：

```text
PATH=
REFERENCE_COUNT=
WHY_SUSPECTED_DEAD=
SAFE_TO_REMOVE_CANDIDATE=YES/NO/UNKNOWN
```

---

## 17. Finding 分级

### BLOCKING

例如：

- Contract 与 API/DB 持久化链断裂；
- 数据写入错误模块/错误表；
- Migration 链错误导致数据结构不可信；
- customer_id 关系不成立；
- Create/Edit 保存或回填丢关键字段；
- Progress 历史数据有丢失风险；
- 模块之间明显串数据。

### HIGH

例如：

- Contract 正确但 Runtime Projection / Renderer 产生错误字段或 Section；
- API存在第二套字段 Authority；
- DB存在活动 legacy fields；
- Heatmap使用非canonical字段且容易随字段修改失效；
- 测试无法发现当前已知人工缺陷；
- 同一共享能力有多套活动实现。

### MEDIUM / LOW

不影响当前业务正确性但增加维护成本的问题。

---

## 18. 调查报告固定结构

报告必须按以下章节输出：

```text
1. Survey Snapshot
2. Executive Findings
3. Runtime Topology
4. Module Conformance Matrix
5. Field/UI Runtime
6. API Surface and Mapping
7. Database and Migration Reality
8. Customer Flow
9. Progress Flow
10. Metric Flow
11. Heatmap Flow
12. Hidden Consumers
13. Initialization / Bypass Paths
14. Test Coverage Reality
15. Dead / Legacy Candidates
16. Findings
17. Unknowns Requiring User Confirmation
18. Recommended Next Remediation Boundaries
```

“Recommended Next Remediation Boundaries”只能建议修复边界，不能在调查 Agent 中直接实施。

---

## 19. 调查完成门槛

只有以下事实全部恢复后才能标记 COMPLETE：

- 五模块 Field Contract 实际路径和消费者明确；
- MOX 41字段的 UI/API/DB mapping inventory 完整；
- 五模块 Create/Edit/Table 实际 projection/renderer 链明确；
- 企业 API surface 明确；
- `database.js` 企业职责、表、CRUD、mapping 明确；
- V34—V38 实际状态明确；
- customer 共享/重复实现明确；
- progress 真实数据模型明确；
- metric 真实链明确；
- Heatmap 真实链明确；
- hidden consumers 明确；
- 初始化/旁路明确；
- 测试覆盖与缺口明确；
- 所有不能确认的事项被显式列为 UNKNOWN，而不是猜测。

---

## 20. 最终短回执

```text
ENTERPRISE RUNTIME IMPLEMENTATION SURVEY
RESULT=COMPLETE/PARTIAL/BLOCKED
SURVEY_HEAD=SHA
SURVEY_WORKTREE=路径
FIELD_CONTRACT_RUNTIME=PASS/PARTIAL/FAIL
MOX_41_FIELD_FLOW=COMPLETE/PARTIAL
CREATE_EDIT_RENDERING=PASS/PARTIAL/FAIL
API_MAPPING=PASS/PARTIAL/FAIL
DATABASE_REALITY=COMPLETE/PARTIAL
MIGRATION_V34_V38=PASS/PARTIAL/FAIL
CUSTOMER_FLOW=PASS/PARTIAL/FAIL
PROGRESS_MODEL=CONFIRMED/PARTIAL/UNKNOWN
METRIC_FLOW=PASS/PARTIAL/FAIL
HEATMAP_FLOW=CONFIRMED/PARTIAL/UNKNOWN
HIDDEN_CONSUMERS=数量
TEST_GAPS=数量
DEAD_LEGACY_CANDIDATES=数量
BLOCKING_FINDINGS=数量
HIGH_FINDINGS=数量
DOCUMENT_GAPS=数量
ARCHITECTURE_GAP_CANDIDATES=数量
UNKNOWNS_REQUIRING_USER=数量
CODE_CHANGED=NO
NEXT=DESIGN_RECONCILIATION
```
