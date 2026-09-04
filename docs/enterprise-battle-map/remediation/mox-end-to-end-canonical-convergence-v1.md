# MOX End-to-End Canonical Convergence Remediation V1

**状态：CURRENT IMPLEMENTATION PLAN**  
**唯一 MOX Authority：`mox-canonical-authority-v6.md`**  
**共享架构 Authority：`enterprise-contract-architecture-v5.md`**  
**代码工作树：`D:\BattleMap\battle-map`**  
**代码分支：`feature/enterprise-battle-map`**  
**下一门禁：独立 End-to-End Canonical Review**

---

## 1. 本轮目标

本轮不是继续零散修补，而是把 Runtime Survey 已确认的所有 MOX canonical 分叉一次性收敛。

必须解决：

1. Create/Edit 将 MOX 四个 Contract group 压缩成 3-section；
2. Production 使用 `getCreateFields()` / `getEditFields()`，测试却曾验证另一套 Projection；
3. `getCreateProjection()` / `getEditProjection()` 与真实 runtime 不一致；
4. `getMoxFromSections()` 未被使用；
5. Heatmap 使用中文 label 作为字段 identity；
6. `updateMoxNetwork()` 仍接受旧 key：`office/customer/major_project/progress`；
7. Progress history 与 `battleProgress` text 双写；
8. `customerCategory` 测试漏合法空值；
9. 原测试只有单向 Projection→Contract 检查；
10. group 视觉层级弱、间距不足；
11. 客户查询 SQL 漏 `customer_id` 已由独立 remediation 修复，本轮只做回归证明，不重复设计。

---

## 2. 安全前置

开始前记录：

```text
git branch --show-current
git status --short
git log -1 --oneline
git diff --stat
```

要求：

- 当前分支必须为 `feature/enterprise-battle-map`；
- 当前工作树必须没有其他 Agent 正在写入；
- 客户数据统一修复如已完成，必须已经 commit；
- 记录 `BASE_HEAD`；
- 不 reset、不 rebase、不 clean、不丢弃未提交成果。

若当前工作树仍被其他写 Agent 使用，返回 `BLOCKED_CONCURRENT_WRITER`。

---

## 3. 必读

本地 Authority：

```text
D:\BattleMap\BattleMapenterprise-authority\docs\enterprise-battle-map\enterprise-contract-architecture-v5.md
D:\BattleMap\BattleMapenterprise-authority\docs\enterprise-battle-map\mox-canonical-authority-v6.md
D:\BattleMap\BattleMapenterprise-authority\docs\enterprise-battle-map\remediation\mox-end-to-end-canonical-convergence-v1.md
```

同时读取：

- Runtime Survey 本地报告；
- MOX Create/Edit Contract Audit 报告；
- Customer Fetch remediation report；
- 当前 `src/config/enterprise`；
- MOX 页面、新增、编辑、Heatmap、API、`database.js`；
- Progress API、history table、相关 Migration；
- 真实测试。

本地旧 Authority 不得覆盖 V5/V6。

---

## 4. WRITE_SCOPE

允许修改：

- `src/config/enterprise` 中共享 Projection/Validator/option-set 和 MOX Contract 直接相关文件；
- MOX Create/Edit renderer 及共享 group renderer 样式；
- MOX Heatmap 数据转换/field lookup；
- MOX API/client/service；
- `updateMoxNetwork()` 及直接调用方；
- Progress API/history persistence/MOX progress projection；
- `database.js` 中 MOX canonical mapping、Progress 直接相关逻辑；
- 必要 V39 Migration（前提：V39 未占用）；
- MOX/enterprise 直接相关测试；
- 本轮 remediation report。

允许修改共享文件时必须保持 TOB/ISP/电力/大企无回归。

禁止：

- 改动 41 个业务字段集合；
- 改动 9 个 Metric 业务公式；
- 改写 Heatmap 未冻结的业务规则；
- 修改其他模块业务字段 Contract；
- 企业首页；
- 非企业模块；
- 新增长期 legacy compatibility；
- 为通过测试删除有效断言。

---

## 5. Step 1：恢复并固定真实 Runtime 路径

建立调用图：

```text
Create renderer
→ 实际调用函数
→ field filtering
→ ordering
→ grouping

Edit renderer
→ 实际调用函数
→ field filtering
→ ordering
→ grouping
```

确认 Production 当前以 `getCreateFields()` / `getEditFields()` 或其共享底层实现为真实入口。

列出：

- `getCreateProjection()` 所有调用方；
- `getEditProjection()` 所有调用方；
- `getMoxFromSections()` 所有调用方；
- `getFromSectionKey()` 所有调用方。

不得先删除文件，先建立 reference 清单。

---

## 6. Step 2：收敛 Projection 为唯一算法

目标：

```text
Contract
→ 唯一 filter/order/group 实现
→ Create/Edit runtime
```

要求：

- Production 和 tests 使用同一底层实现；
- `getCreateProjection()` / `getEditProjection()` 无真实需要则删除；
- 如仍有调用方，只做薄包装；
- `getMoxFromSections()` 无引用则删除；
- 不保留另一套 group mapping；
- 不通过模块名硬编码 41 个字段数组。

MOX group 必须直接来自 field `group`：

```text
客户信息
无线格局
微波格局
作战情况
```

不得再通过 `getFromSectionKey()` 或等价逻辑把无线/微波压成“业务格局”。

其他模块已有“业务格局”的 Contract 不得被本轮破坏。

---

## 7. Step 3：双向 Runtime Conformance

新增测试/Validator：

### Create

```text
EXPECTED = Contract ui.create.visible=true keys
ACTUAL = 真实 Create renderer 输入 keys
EXPECTED == ACTUAL
```

### Edit

同理。

### Table

同理。

分别检查：

- set equality；
- length；
- duplicate；
- order；
- group；
- visibility；
- control/editor id。

必须直接覆盖 Production 路径，不能用未被 renderer 消费的 API 替代。

---

## 8. Step 4：修正 group 视觉层级

共享 renderer/group 样式必须保证：

- 标题明显；
- 每组顶部有统一留白；
- 标题与上一组字段不贴连；
- 有分隔线/背景/容器边界中的至少一种清晰分组方式；
- Create/Edit 相同；
- MOX 四组全部一致。

不得为五个模块复制五套近似 CSS。

自动测试只验证结构/class，最终视觉由用户人工验收。

---

## 9. Step 5：customerCategory 完整值域

合法状态：

```text
空值
核心NA
战略NA
```

要求：

- Contract option-set完整；
- Create/Edit 可选择空值；
- 测试验证 exact option set，不仅检查两个非空值；
- customer_id 不因修改类别改变；
- Customer Fetch 已修复链继续返回真实 `customer_id`。

---

## 10. Step 6：Heatmap canonical key 收敛

先建立当前 Heatmap field lookup 清单，找出所有中文 label 作为 key 的位置。

目标：

```text
record[canonicalKey]
```

禁止：

```text
record['中文字段名']
```

以及以 label→field 的长期业务映射作为主身份。

要求：

- 所有 Heatmap 引用 key 存在于 MOX Field Contract；
- tooltip 显示可以继续使用 label；
- 数据 lookup 必须 canonical；
- 不改变当前 Heatmap 聚合和视觉业务规则；
- 增加测试保证 label 文案变化不会改变数据 lookup；
- 搜索并证明 MOX Heatmap `LABEL_AS_FIELD_IDENTITY=0`。

---

## 11. Step 7：移除 `updateMoxNetwork()` legacy runtime key

已确认旧 key：

```text
office
customer
major_project
progress
```

实施：

1. 列出所有真实调用方；
2. 将仍发送旧 key 的当前代码改为 canonical key；
3. 删除 `updateMoxNetwork()` 中旧 key 翻译/兼容；
4. 删除对应 runtime fallback；
5. 增加 legacy key rejection/non-acceptance tests；
6. 全局搜索企业模块，旧 key 只能在 Migration/历史说明/测试 legacy rejection case 中出现。

不得留下“先读 canonical，读不到再读旧 key”的逻辑。

---

## 12. Step 8：Progress 单一事实源收敛

### 12.1 恢复真实 schema

必须列出：

- Progress history table 名称；
- primary key；
- business record FK；
- progress content column；
- timestamp/order column；
- create/edit/delete/read API；
- MOX business table 当前 Progress text column；
- 双写发生函数。

### 12.2 数据一致性盘点

对所有 MOX 记录分类：

```text
A. business text empty + history exists
B. business text == latest history
C. business text only
D. business text != latest history
E. both empty
```

记录数量并写入 report。

### 12.3 目标

Progress history table 成为唯一持久化 Authority。

- 独立进展弹窗只写 history；
- `battleProgress` read 从 history latest/current projection 获得；
- Create/Edit 特殊 editor 不再写 business text；
- API 不双写；
- database.js 不双写；
- business text 不再作为 fallback。

### 12.4 历史数据处理

- A/B/E：可直接停止 business text 写入；
- C：迁入 history 后再删除/废弃 text；
- D：不得静默覆盖，必须记录冲突；若能根据可靠证据确定 text 是未入 history 的新进展，则迁入，否则返回 blocker。

严禁为了完成任务丢弃 D 类数据。

### 12.5 Migration

如需删除 MOX business table 的 Progress text column，预期使用 `V39`。

开始前检查：

```text
V39.sql 是否已存在
migration registry 是否已有 version 39
```

如占用：

```text
MIGRATION_VERSION_CONFLICT
```

停止，不自行换号。

Migration 必须事务、回滚、幂等、成功后登记 `_migrations`，并验证新建库和升级库一致。

---

## 13. Step 9：Customer 修复回归

不重复重构 Customer，只验证已修复事实：

```text
SELECT ... customer_id ... FROM customers
→ API response.customer_id
→ frontend customer candidate.customer_id
→ unique selection
→ save customer_id
```

MOX、TOB、ISP、电力、大企客户初始化均不得回归。

---

## 14. Step 10：Metric 与数据库回归

Metric：

- 9 项数值正确；
- click-to-filter 同一 where；
- field reference canonical；
- 本轮不得改公式。

数据库：

- V34—V38 注册不回归；
- 如有 V39 则正确接续；
- CRUD round-trip；
- 新库/升级库一致；
- legacy runtime mapping=0；
- Progress double write=0；
- customer_id relation 完整。

---

## 15. Step 11：测试治理和死代码

删除/重建：

- 只验证旧 `getCreateProjection/getEditProjection` 的测试；
- 单向 Projection→Contract 测试；
- 断言 MOX 3-group 的测试；
- 遗漏 customerCategory 空值的测试；
- 依赖 Heatmap 中文 label identity 的测试；
- 断言 legacy key runtime compatibility 的测试；
- 断言 Progress 双写的测试；
- 无消费者的 Projection/helper 测试。

保留并增强真实行为测试。

死代码仅限本轮确认无消费者的企业相关 helper/compatibility path。

---

## 16. 自动验证顺序

必须按顺序执行：

1. MOX Contract/Projection tests；
2. MOX Create/Edit tests；
3. group runtime tests；
4. Heatmap canonical tests；
5. API canonical/legacy rejection tests；
6. Progress history/single-source tests；
7. Customer regression tests；
8. database/Migration tests；
9. Metric tests；
10. TOB/ISP/Power/Large关键企业回归；
11. enterprise suite；
12. full Vitest；
13. build；
14. lint/typecheck（如配置）。

失败不得通过删除测试、降低断言或恢复兼容层解决。

---

## 17. 实施报告

创建：

```text
docs/enterprise/remediations/mox-end-to-end-canonical-convergence-report.md
```

必须记录：

- BASE_HEAD；
- FINAL_HEAD；
- changed files；
- Projection 收敛前后路径；
- removed unused helpers；
- Create/Edit actual groups；
- Heatmap label lookup 清单与修复；
- legacy key 清理清单；
- Progress A/B/C/D/E 数据分类数量；
- Progress 单一事实源最终链；
- Migration version/result；
- Customer regression；
- tests/build；
- blockers。

---

## 18. 完成标准

全部满足才可 `COMPLETE`：

```text
MOX_FIELDS=41
MOX_GROUPS=4
BUSINESS_LANDSCAPE_GROUP=ABSENT
RUNTIME_PROJECTION_ALGORITHMS=1
CREATE_CONFORMANCE=PASS
EDIT_CONFORMANCE=PASS
TABLE_CONFORMANCE=PASS
CUSTOMER_CATEGORY=PASS
HEATMAP_CANONICAL_KEY=PASS
HEATMAP_LABEL_IDENTITY=0
LEGACY_RUNTIME_KEYS=0
CUSTOMER_ID_CHAIN=PASS
PROGRESS_PERSISTENCE_AUTHORITIES=1
PROGRESS_DOUBLE_WRITE=0
PROGRESS_DATA_CONFLICTS=0 或 BLOCKED_WITH_EVIDENCE
MIGRATION=PASS/NOT_REQUIRED
METRICS=PASS
ENTERPRISE_REGRESSION=PASS
FULL_TESTS=PASS
BUILD=PASS
OUT_OF_SCOPE_CHANGES=NO
```

如果 Progress D 类数据无法可靠处理，不允许 COMPLETE。

---

## 19. 最终短回执

```text
MOX END-TO-END CANONICAL CONVERGENCE
RESULT=COMPLETE/PARTIAL/BLOCKED
BASE_HEAD=
FINAL_HEAD=
MOX_FIELDS=
MOX_GROUPS=
RUNTIME_PROJECTION_ALGORITHMS=
CREATE_CONFORMANCE=
EDIT_CONFORMANCE=
TABLE_CONFORMANCE=
CUSTOMER_CATEGORY=
HEATMAP_CANONICAL_KEY=
HEATMAP_LABEL_IDENTITY=
LEGACY_RUNTIME_KEYS=
CUSTOMER_ID_CHAIN=
PROGRESS_PERSISTENCE_AUTHORITIES=
PROGRESS_DOUBLE_WRITE=
PROGRESS_DATA_CONFLICTS=
MIGRATION=
METRICS=
ENTERPRISE_REGRESSION=
FULL_TESTS=
BUILD=
OUT_OF_SCOPE_CHANGES=
BLOCKERS=
NEXT=MOX_END_TO_END_INDEPENDENT_REVIEW
```
