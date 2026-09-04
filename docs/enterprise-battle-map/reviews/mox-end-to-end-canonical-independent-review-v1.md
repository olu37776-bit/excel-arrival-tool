# MOX End-to-End Canonical Independent Review V1

**状态：CURRENT REVIEW AUTHORITY**  
**审查对象：MOX End-to-End Canonical Convergence 完成后的固定提交**  
**代码工作树：`D:\BattleMap\battle-map`**  
**代码分支：`feature/enterprise-battle-map`**  
**本地 Authority：`D:\BattleMap\BattleMapenterprise-authority`**  
**审查性质：独立、只读，不实施 remediation，不修改生产代码/测试/Migration/数据库**  
**通过后的下一门禁：用户人工验收 → MOX REFERENCE_IMPLEMENTATION_V1 冻结**

---

## 1. 审查目的

本轮不是只证明“测试通过”，而是证明 MOX 已经真正形成一条单一、可维护、端到端 canonical 运行链：

```text
Canonical Authority / Excel
        ↓
MOX Field Contract
        ↓
唯一 Runtime Projection
        ↓
Table / Create / Edit
        ↓
API canonical payload / response
        ↓
database.js canonical mapping
        ↓
SQLite / customer relation / progress history
```

并同时证明旁路消费者没有重新创造第二套字段身份：

```text
Metric
Heatmap
Customer
Progress
Filter / Search / Sort
Payload / Response mapper
Validation / JSON initialization
Store / composable / helper
```

通过标准不是“主要功能可用”，而是：

> canonical key 是跨层唯一业务身份；中文 label 只负责展示；DB column 只负责持久化；旧 key、重复 Projection、Progress 双写、隐藏字段映射均不得继续作为活动运行时语义。

---

## 2. 审查安全前置

开始前必须先更新本地 Authority：

```powershell
git -C "D:\BattleMap\BattleMapenterprise-authority" pull --ff-only origin enterprise-battle-map-authority
```

然后在代码工作树记录：

```powershell
git -C "D:\BattleMap\battle-map" branch --show-current
git -C "D:\BattleMap\battle-map" status --short
git -C "D:\BattleMap\battle-map" log -1 --oneline
git -C "D:\BattleMap\battle-map" diff --stat
```

必须满足：

- 当前分支为 `feature/enterprise-battle-map`；
- Convergence Agent 已停止写入；
- 本轮实施已经形成一个本地 commit；
- 工作树干净；
- 不存在进行中的 merge/rebase/cherry-pick；
- 记录 `REVIEWED_HEAD=<当前HEAD>`；
- 审查全过程只对该 SHA 负责。

如果审查期间 HEAD 或工作树被其他 Agent 修改：

```text
RESULT=BLOCKED
BLOCKER=CONCURRENT_MUTATION_DURING_REVIEW
```

不得继续把混合状态当作正式审查证据。

---

## 3. 必读 Authority 与 Evidence

必须完整读取：

```text
D:\BattleMap\BattleMapenterprise-authority\docs\enterprise-battle-map\enterprise-contract-architecture-v5.md
D:\BattleMap\BattleMapenterprise-authority\docs\enterprise-battle-map\mox-canonical-authority-v6.md
D:\BattleMap\BattleMapenterprise-authority\docs\enterprise-battle-map\remediation\mox-end-to-end-canonical-convergence-v1.md
```

同时读取本地实施证据：

```text
docs/enterprise/remediations/mox-end-to-end-canonical-convergence-report.md
```

并读取：

- Runtime Survey 报告；
- MOX Create/Edit Contract Audit；
- Customer Fetch remediation report；
- 当前真实 MOX Contract / Projection / renderer；
- MOX Heatmap；
- API/client/server/database.js；
- Progress UI/API/history table；
- V34—V39（如存在）；
- 相关测试。

实施 Agent 的报告只能作为线索，不能作为事实 Authority。所有关键结论必须由当前 `REVIEWED_HEAD` 的代码、测试、Schema 或 Git 事实重新证明。

---

## 4. Finding 分级

### BLOCKING

满足任一即可阻塞：

- 41 字段集合或 canonical identity 错误；
- MOX Create/Edit 仍不是 4 group；
- 真实 renderer 与测试仍走不同 Projection 算法；
- Create/Edit/Table 任一存在 Contract 字段缺失、额外、重复或顺序错误；
- Heatmap 仍使用中文 label 或 DB column 作为字段身份；
- `updateMoxNetwork()` 或等价 runtime 仍接受旧 key；
- Progress History 与业务表文本仍双写/互相 fallback；
- 独立进展弹窗被删除或降级成普通 textarea；
- Customer 链再次丢失 `customer_id`；
- API/database.js/SQLite canonical mapping 断裂；
- Migration 失败、顺序错误、新库/升级库不一致；
- 关键测试或 build 失败；
- 发现活动 hidden consumer 绕过 canonical key。

### HIGH

- 无消费者旧 Projection/helper 仍保留且可独立定义业务逻辑；
- 测试仍只做单向检查；
- group 结构正确但共享样式机制明显分叉；
- implementation report 与代码事实明显不一致；
- 有 legacy key/中文 label 身份残留在活动路径，但当前用例未触发。

### MEDIUM / LOW

仅限不影响进入人工验收的问题，例如非阻塞命名、文档证据不足、可延后的小范围整理。

---

## 5. Phase A：41 字段与唯一 Field Authority

必须验证：

1. MOX 业务字段恰好 41 个；
2. canonical key 唯一；
3. order 1—41 连续；
4. group 只属于：

```text
客户信息
无线格局
微波格局
作战情况
```

5. MOX 不存在顶层 `业务格局`；
6. 两组“频谱状态”和两组“26年机会点”使用不同 canonical key；
7. `customerCategory` 合法状态完整为：空值 / 核心NA / 战略NA；
8. `battleProgress` 仍为第 41 个 canonical 业务身份；
9. `src/config/enterprise` 内不存在第二份活动 MOX Schema/Contract；
10. `src/enterprise` 或其他旧路径没有活动 Field Authority。

全仓企业范围搜索旧 MOX Field Schema / duplicate array / duplicate order / duplicate group 定义。

结果记录：

```text
FIELD_COUNT=41
DUPLICATE_FIELD_AUTHORITIES=0
```

---

## 6. Phase B：真实 Runtime Projection 单链

先从 Create/Edit renderer 反向追踪实际调用：

```text
Create renderer
→ runtime function
→ filtering
→ ordering
→ grouping

Edit renderer
→ runtime function
→ filtering
→ ordering
→ grouping
```

确认最终实际使用的是 `getCreateFields()` / `getEditFields()` 或共同底层唯一实现。

必须列出：

- `getCreateFields()` 调用方；
- `getEditFields()` 调用方；
- `getCreateProjection()` 调用方；
- `getEditProjection()` 调用方；
- `getMoxFromSections()` 调用方；
- `getFromSectionKey()` / 等价 group mapper 调用方。

目标：

```text
PROJECTION_ALGORITHMS=1
```

允许旧 API 存在的唯一情况：它们只是对同一底层实现的薄包装，没有自己的 filter/order/group 逻辑。

无消费者 helper 应删除；如仍存在但完全无调用且可重新引入另一套业务语义，记录 HIGH。

---

## 7. Phase C：Table / Create / Edit 双向 Conformance

不得读取实施 Agent 手写 expected array 作为第二 Authority。

### Create

从真实 Contract 计算：

```text
EXPECTED_CREATE_KEYS = ui.create.visible=true
```

从真实 renderer 输入获得：

```text
ACTUAL_CREATE_KEYS
```

必须验证：

```text
EXPECTED_CREATE_KEYS == ACTUAL_CREATE_KEYS
```

并逐项比较：

- count；
- set；
- duplicate；
- order；
- group；
- controlId/editorId；
- editable。

### Edit

同样验证。

### Table

同样验证 `ui.table.visible=true` 与真实表格字段。

禁止仅验证：

```text
actual ⊆ contract
```

因为这无法发现 Contract 字段被静默漏掉。

目标：

```text
CREATE_CONFORMANCE=PASS
EDIT_CONFORMANCE=PASS
TABLE_CONFORMANCE=PASS
```

---

## 8. Phase D：MOX 4-group 与 UI 结构

真实 Create/Edit group 必须精确为：

```text
客户信息
无线格局
微波格局
作战情况
```

顺序不得变化。

验证 renderer 结构/class：

- 每个 group 有独立标题元素；
- group 之间存在统一 spacing/container/divider 机制；
- Create/Edit 共用相同 group 样式机制；
- 不为 MOX 复制一份完全独立 CSS；
- “作战情况”结构上与上一组分开。

本轮不做人工视觉裁定；结构测试通过后由用户人工验收“标题是否明显、留白是否专业”。

---

## 9. Phase E：Customer `customer_id` 端到端回归

这是已修复缺陷，必须成为永久门禁。

恢复真实链：

```text
customers.customer_id
→ database.js SELECT
→ customer API response
→ frontend normalization
→ candidate.customer_id
→ unique selection
→ create payload.customer_id
→ server existence validation
→ MOX business record.customer_id
```

必须检查 SQL 实际 SELECT 包含 `customer_id`。

测试至少覆盖：

- 正常客户有 `customer_id`；
- query 成功但缺 `customer_id` 必须失败；
- 同名客户不取第一条；
- customer_id 不存在时业务保存失败；
- MOX 创建链；
- TOB/ISP/电力/大企客户初始化关键回归。

结果：

```text
CUSTOMER_ID_CHAIN=PASS
```

---

## 10. Phase F：Heatmap canonical identity

恢复 MOX Heatmap 的真实数据输入、transform、dimension、measure、tooltip、click/filter 链。

必须证明：

1. 所有 record lookup 使用 canonical key；
2. 不存在：

```js
record['中文字段名']
```

作为业务数据 lookup；
3. 中文 label 只用于显示；
4. SQLite column 不直接作为 Heatmap 前端业务身份；
5. Heatmap 引用的所有 canonical key 都存在于 MOX Field Contract；
6. 本轮没有擅自改变未冻结的 Heatmap 业务聚合规则；
7. label 文案改变时，数据 lookup 测试仍通过。

企业相关范围搜索：

- 中文 label lookup；
- label→field 业务 identity map；
- DB column→Heatmap 直接绑定。

目标：

```text
HEATMAP_CANONICAL_KEYS=PASS
HEATMAP_LABEL_IDENTITY=0
```

---

## 11. Phase G：API canonical-only 与 legacy key 清零

重点审查：

```text
updateMoxNetwork()
```

以及所有直接/间接 payload mapper。

已确认必须清除的旧 key：

```text
office
customer
major_project
progress
```

必须证明：

- 当前 UI 不再发送这些旧 key；
- API/update runtime 不再接受、翻译、fallback 这些旧 key；
- unknown/legacy key 有可诊断失败或被明确拒绝；
- legacy key 只允许出现在：一次性 Migration、历史文档、legacy rejection 测试。

同时扫描：

- create/update payload builders；
- response normalizers；
- server route adapters；
- database.js mapping/validation；
- Store/composable/helper；
- filter/search/sort。

目标：

```text
ACTIVE_LEGACY_RUNTIME_KEYS=0
```

---

## 12. Phase H：Progress 独立弹窗与单一事实源

这是 BLOCKING 核心项。

### 12.1 必须保留的用户行为

表格记录旁的独立 Progress 操作仍存在，并可打开进展录入/编辑弹窗。

必须保持：

```text
记录
→ 独立进展弹窗
→ 新增/追加/编辑进展
```

禁止：

- 删除独立弹窗；
- 把它改成普通 MOX Edit textarea；
- 用 `battleProgress` 文本字段替代历史能力。

### 12.2 唯一持久化事实源

必须证明：

```text
Progress History table = 唯一持久化 Authority
```

写入链必须为：

```text
Progress popup
→ Progress API
→ Progress History
```

不得同时写 MOX business table progress text。

读取链必须为：

```text
Progress History
→ latest/current projection
→ canonical battleProgress
→ Table/Edit/display
```

不得从 business text fallback。

### 12.3 数据收敛证据

读取 convergence report 中 A/B/C/D/E 分类，但必须抽查/重算代码与 Migration 逻辑是否真实对应。

如果实施过程中存在 D 类冲突数据，必须验证没有静默丢弃。

如使用 V39：

- V39 唯一；
- SQL 正确；
- database.js 注册正确；
- 事务；
- 回滚；
- 幂等；
- `_migrations` 成功后登记；
- 新库与升级库最终一致。

如果实现报告标记 NOT_REQUIRED，也必须证明 business progress text 已经不存在活动持久化/双写。

目标：

```text
PROGRESS_POPUP=PASS
PROGRESS_HISTORY_AUTHORITY=PASS
PROGRESS_DOUBLE_WRITE=0
PROGRESS_TEXT_FALLBACK=0
```

---

## 13. Phase I：database.js / SQLite 端到端映射

数据库是正式 Contract 消费者，不是可忽略实现细节。

必须检查 MOX：

```text
canonical key
→ API field
→ database.js mapping
→ SQLite column/relation
```

检查：

- mapping 唯一；
- CRUD create/read/update round-trip；
- Customer relation；
- Progress relation；
- legacy runtime mapping=0；
- Authority 外旧业务列无活动引用；
- V34—V38 不回归；
- V39（如有）顺序正确；
- 新建库 Schema == 从旧库连续升级后的 Schema。

Round-trip 不能只验证单个字段，应至少覆盖：

- 普通 text；
- enum；
- number/money；
- customer relation；
- progress projection。

---

## 14. Phase J：Metric Contract 回归

9 个 Metric 业务公式不得改变。

检查：

- Metric field references 使用 canonical key；
- calculation 与 click-to-filter 仍使用同一个 `where`；
- active metric 不串模块；
- 9 个统计固定样例通过；
- 本轮 convergence 没有为了其他修复改变 Metric 定义。

结果：

```text
METRICS=9/9
CLICK_TO_FILTER=PASS
```

---

## 15. Phase K：隐藏消费者 / Canonical bypass scan

对企业代码范围做一次穷举式静态扫描，重点不是找所有 import，而是找“谁还在重新定义业务字段身份”。

必须检查：

### UI / helper

- 本地完整字段数组；
- 本地完整 group 数组；
- `if field === 中文label`；
- `record['中文字段名']`；
- legacy field fallback。

### Filter / Search / Sort

- `major_project` / `office` / `customer` / `progress`；
- 中文 label 作为数据 key；
- DB column 直接进入页面逻辑。

### API / mapper

- legacy→canonical runtime adapter；
- canonical→legacy runtime adapter；
- 重复 payload/response mapping。

### database.js

- CRUD mapping；
- Validation；
- JSON initialization/seed；
- migration-only key 是否误进入 runtime。

### Store / composable

- 字段 rename/default/fallback；
- module-specific hidden field mapping。

### Heatmap / Metric

- label identity；
- duplicate condition。

### Progress

- business text read/write/fallback。

最终目标：

```text
UNDECLARED_CANONICAL_BYPASSES=0
```

允许存在的旧 key/旧 label 使用必须逐条解释为：

```text
MIGRATION_ONLY
DOC_ONLY
LEGACY_REJECTION_TEST_ONLY
DISPLAY_ONLY
```

任何无法分类的活动使用都记录 finding。

---

## 16. Phase L：测试可信度审查

必须验证测试真的覆盖 production runtime，而不是再次测试平行 helper。

检查：

- Create/Edit 测试直接覆盖真实 renderer 使用函数；
- Contract↔runtime 双向集合相等；
- 4-group；
- customerCategory 三态含空值；
- Heatmap canonical key；
- legacy key rejection；
- Customer `customer_id`；
- Progress popup/history/single-source；
- CRUD round-trip；
- Migration；
- Metric。

禁止测试通过复制生产 Contract 数组形成第二 Authority。

必须重新运行项目真实测试命令，包括：

1. MOX Contract/Projection；
2. Create/Edit；
3. Heatmap；
4. API legacy rejection；
5. Customer；
6. Progress；
7. database/Migration；
8. Metric；
9. TOB/ISP/Power/Large关键回归；
10. enterprise suite；
11. full Vitest；
12. build；
13. lint/typecheck（如存在）。

---

## 17. 审查报告

创建：

```text
docs/enterprise/reviews/mox-end-to-end-canonical-independent-review.md
```

必须记录：

- REVIEWED_HEAD；
- 实施 commit；
- changed files 复核；
- 41字段与4-group结果；
- Projection调用图；
- 双向Conformance结果；
- Customer完整链；
- Heatmap key inventory；
- legacy key扫描；
- Progress popup/read/write/persistence链；
- A/B/C/D/E数据收敛证据；
- database mapping / Migration；
- hidden consumer scan；
- 测试结果；
- findings。

审查报告可以提交本地 commit，但不得修改任何生产/测试文件。若提交报告，必须明确 `REVIEWED_HEAD` 指向提交报告前的代码 SHA。

---

## 18. 结果门禁

结果只能是：

```text
PASS
PASS_WITH_NONBLOCKING_FINDINGS
BLOCKED
```

只有以下全部成立才允许 PASS：

- 41 fields correct；
- MOX 4 group correct；
- runtime Projection 单一；
- Table/Create/Edit 双向 Conformance；
- Customer `customer_id` 全链；
- Heatmap canonical；
- active legacy key = 0；
- Progress popup 保留；
- Progress History 唯一持久化事实源；
- double write/fallback = 0；
- database canonical round-trip；
- Migration chain正确；
- 9 Metric无回归；
- hidden canonical bypass = 0；
- full tests/build通过。

PASS 后：

```text
NEXT_GATE=USER_MANUAL_ACCEPTANCE
```

BLOCKED 后：

```text
NEXT_GATE=MOX_CANONICAL_REMEDIATION
```

本轮不得自行继续 remediation。

---

## 19. 最终短回执

```text
MOX END-TO-END CANONICAL INDEPENDENT REVIEW
RESULT=PASS/PASS_WITH_NONBLOCKING_FINDINGS/BLOCKED
REVIEWED_HEAD=SHA
FIELD_COUNT=41/实际
GROUPS=客户信息|无线格局|微波格局|作战情况 或 FAIL
PROJECTION_ALGORITHMS=1/实际
CREATE_CONFORMANCE=PASS/FAIL
EDIT_CONFORMANCE=PASS/FAIL
TABLE_CONFORMANCE=PASS/FAIL
CUSTOMER_CATEGORY=PASS/FAIL
CUSTOMER_ID_CHAIN=PASS/FAIL
HEATMAP_CANONICAL_KEYS=PASS/FAIL
HEATMAP_LABEL_IDENTITY=0/实际
ACTIVE_LEGACY_RUNTIME_KEYS=0/实际
PROGRESS_POPUP=PASS/FAIL
PROGRESS_HISTORY_AUTHORITY=PASS/FAIL
PROGRESS_DOUBLE_WRITE=0/实际
PROGRESS_TEXT_FALLBACK=0/实际
DB_CANONICAL_ROUNDTRIP=PASS/FAIL
MIGRATION_CHAIN=PASS/FAIL
METRICS=9/9或实际
CLICK_TO_FILTER=PASS/FAIL
UNDECLARED_CANONICAL_BYPASSES=0/实际
ENTERPRISE_REGRESSION=PASS/FAIL
FULL_TESTS=PASS/FAIL
BUILD=PASS/FAIL
BLOCKING_FINDINGS=最多5项
HIGH_FINDINGS=最多5项
REMEDIATION_REQUIRED=YES/NO
NEXT_GATE=USER_MANUAL_ACCEPTANCE/MOX_CANONICAL_REMEDIATION
CODE_CHANGED=NO
```
