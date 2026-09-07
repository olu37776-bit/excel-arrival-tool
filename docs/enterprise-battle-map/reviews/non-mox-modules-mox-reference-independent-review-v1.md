# TOB / ISP / 电力 / 大企 → MOX Reference Alignment Independent Review V1

**状态：CURRENT INDEPENDENT REVIEW AUTHORITY**  
**适用模块：TOB、ISP、电力、大企**  
**参考实现：当前已通过独立审查的 MOX**  
**代码工作树：`D:\BattleMap\battle-map`**  
**代码分支：`feature/enterprise-battle-map`**  
**前置实施：`remediation/non-mox-modules-mox-reference-alignment-v1.md`**

---

## 1. 目标

本轮不是再次实现功能，也不是简单复跑测试。

目标是独立证明：TOB / ISP / 电力 / 大企已经真正接入 MOX 已验证的共享机制，而不是仅在页面效果上看起来相似，内部仍保留四套局部实现、legacy path 或 hidden consumer。

独立审查必须固定代码 HEAD，只读执行，不得修改生产代码、测试、Migration、SQLite 或业务 Authority。

---

## 2. Authority

审查按以下顺序：

1. `enterprise-contract-architecture-v5.md`
2. `architecture/enterprise-runtime-field-options-contract-v1.md`
3. `mox-canonical-authority-v6.md`
4. `remediation/non-mox-modules-mox-reference-alignment-v1.md`
5. TOB / ISP / Power / Large 当前 Canonical Authority
6. alignment implementation report
7. 当前真实代码、API、database.js、SQLite、测试

Excel V0.2 尚未正式发布的新业务字段变化不属于本轮机制审查 Authority；发现时标记 `BLOCKED_BY_V0_2_AUTHORITY`，不得自行解释。

---

## 3. 固定审查 HEAD

开始前执行并记录：

```text
git branch --show-current
git status --short
git log -1 --oneline
```

要求：

- 分支必须为 `feature/enterprise-battle-map`；
- alignment implementation 已 commit；
- 工作树干净；
- 无其他 Agent 同时写入。

固定：

```text
REVIEWED_HEAD=<当前HEAD>
```

审查期间 HEAD 变化则结果自动失效。

---

## 4. 核心审查问题

本轮必须回答：

> 四个模块是否真正共享 MOX 已验证的 engine / adapter / renderer / validator / relation / progress / metric / heatmap canonical mechanism，而不是继续维护自己的等价实现？

不是只回答页面能不能打开。

---

## 5. Shared Runtime Alignment

独立恢复实际调用链并比较：

```text
MOX
TOB
ISP
Power
Large
```

至少验证：

### 5.1 Field Contract

- 每模块只有一份当前业务字段 Authority；
- 页面无第二套完整字段数组；
- Table/Create/Edit 都从模块自己的 Contract 派生；
- 不 import MOX business field array；
- 不 cross-module import business field definitions。

### 5.2 Runtime Projection

分别恢复 Table/Create/Edit 的真实 Production path。

必须证明每模块：

```text
Contract expected keys == actual renderer keys
```

并检查：

- 无缺失；
- 无额外；
- 无重复；
- order 一致；
- group 一致；
- control/editor 一致。

不得用未被真实页面消费的 Projection API 代替。

### 5.3 Runtime Field View Model / Options

必须验证：

```text
fieldDef.type / controlId / editorId
→ runtime projection
→ options provider
→ runtime field.options
→ renderer
```

不得重新出现：

```text
fieldDef.type='select'
f.type=undefined
runtime却检查f.type
```

四模块 Create 打开真实 Production path 必须通过。

---

## 6. Create / Edit UI Mechanism

四模块正确顶层 group 都是：

```text
客户信息
业务格局
作战情况
```

必须验证：

- shared modal shell；
- shared group renderer；
- shared spacing / validation presentation；
- Create/Edit 使用同一机制；
- 模块差异来自 Contract，而非复制组件；
- 没有 module-local 完整 form schema；
- Edit customer fields readonly；
- customer_id 不因 Edit 改变。

用户视觉效果最终由人工验收，本轮自动审查验证结构和共享机制。

---

## 7. Customer Relation

五模块必须共享同一客户关系链：

```text
customers.customer_id
→ database.js query
→ shared API
→ frontend normalization
→ dynamic customer options
→ unique customer selection
→ business record.customer_id
```

审查必须确认：

- 无模块私有 customer SQL；
- 无模块私有 customer fetch；
- 不以 customerName 作为关系身份；
- 同名客户不默认取第一条；
- `customer_id` 不在 normalization / options / payload 中丢失；
- Customer API failure 与 Runtime/Options failure 错误边界分离。

---

## 8. Progress

四模块必须和 MOX 使用同一 Progress 模型：

```text
Progress History = 唯一持久化事实源
battleProgress = latest/current canonical projection
独立Progress弹窗 = History新增/编辑入口
```

必须证明：

- 四模块都有独立 Progress popup 行操作；
- 不退化成业务表 textarea；
- business-table progress text 双写 = 0；
- progress fallback = 0；
- 表格/详情 latest projection 来源明确；
- MOX Progress 无回归。

---

## 9. Heatmap

逐模块检查 Heatmap 的所有业务字段 lookup。

要求：

```text
HEATMAP_REFERENCED_KEYS ⊆ MODULE_FIELD_CONTRACT_KEYS
LABEL_AS_FIELD_IDENTITY = 0
DB_COLUMN_AS_FRONTEND_IDENTITY = 0
```

允许 label 用于 tooltip 展示，不允许 label 作为 record lookup identity。

不得因“参考 MOX”复制 MOX 的 Heatmap 业务字段和未确认业务规则。

---

## 10. Metric / Filter

四模块必须使用共享 Metric execution mechanism。

对 9 项 Metric 独立验证：

- field reference canonical；
- calculation 使用 Contract `where`；
- click-to-filter 使用同一个 `where`；
- 页面没有第二套 if/switch 条件；
- 点击统计后只筛下方明细，不反向重算顶层 Metric；
- MOX Metric 无回归。

---

## 11. Table / Filter / Search / Sort Hidden Consumers

全仓企业范围扫描：

- 中文 label 作为 `row[...]` identity；
- DB column 直接进入前端逻辑；
- legacy key；
- module-local column array；
- module-local filter condition；
- module-local formatter/parser 重复定义；
- 未声明的 canonical mapping。

对所有发现分类：

```text
VALID_PRESENTATION_ONLY
IMPLEMENTATION_NONCONFORMANCE
DEAD_CODE
TEST_ONLY
MIGRATION_ONLY
BLOCKED_BY_V0_2_AUTHORITY
```

---

## 12. API Canonical-only

逐模块验证 Create / Edit / Read：

```text
Module canonical key
→ request/response mapping
→ database.js persistence mapping
```

必须满足：

- active runtime legacy alias = 0；
- 中文 label payload = 0；
- fallback/double-read = 0；
- unknown/legacy key 不被静默接受；
- 模块之间不共享对方 business mapping。

一次性 Migration 中出现旧字段不算 runtime violation。

---

## 13. database.js / SQLite

逐模块验证：

- canonical persistence mapping 唯一；
- customer_id relation；
- Progress relation；
- CRUD round-trip；
- 新建库与升级库最终 Schema 一致；
- legacy runtime mapping = 0；
- 模块之间没有 cross-import persistence mapping；
- Migration registry / `_migrations` 无回归。

如果 Excel V0.2 的新字段尚未 Authority 化，不得因当前 Schema 不含新字段而判定 runtime alignment 失败，标记 `BLOCKED_BY_V0_2_AUTHORITY`。

---

## 14. Duplicate Mechanism / Hidden Consumer Gate

本轮最重要的结果之一是确认重复机制数量。

必须至少统计：

```text
DUPLICATE_PROJECTION_IMPLEMENTATIONS
MODULE_LOCAL_FORM_SCHEMAS
PRIVATE_CUSTOMER_FETCH_IMPLEMENTATIONS
PROGRESS_DOUBLE_WRITE_PATHS
LABEL_IDENTITY_LOOKUPS
ACTIVE_LEGACY_KEYS
MODULE_LOCAL_METRIC_LOGIC
UNDECLARED_CANONICAL_CONSUMERS
```

目标全部为 0，除非明确属于业务差异或 V0.2 blocker。

---

## 15. 测试可信度

不能仅看测试 PASS。

必须检查：

- 测试是否调用真实 Production path；
- 是否复制字段数组形成第二 Authority；
- 是否只做 actual→Contract 单向检查；
- 是否 mock 掉真正应该验证的 runtime mechanism；
- Create/Edit 打开测试是否覆盖真实 options enrichment；
- Progress tests 是否验证 history single-source；
- Heatmap tests 是否验证 canonical lookup；
- API/DB tests 是否验证 round-trip。

发现“测试 PASS 但不覆盖真实运行路径”必须记为 blocking TEST_GAP。

---

## 16. 自动验证

只读审查可以执行现有测试和 build，但不得修改测试来使其通过。

至少执行：

1. TOB production-path suite；
2. ISP production-path suite；
3. Power production-path suite；
4. Large production-path suite；
5. MOX regression suite；
6. Customer relation tests；
7. Progress tests；
8. Heatmap canonical tests；
9. Metric tests；
10. API/database tests；
11. enterprise suite；
12. full Vitest；
13. build；
14. lint/typecheck（如已有）。

---

## 17. Finding Classification

Finding 必须分类：

```text
BLOCKING_IMPLEMENTATION_NONCONFORMANCE
BLOCKING_TEST_GAP
NON_BLOCKING_CLEANUP
BUSINESS_DIFFERENCE_EXPECTED
BLOCKED_BY_V0_2_AUTHORITY
```

不得在审查中修复。

---

## 18. 审查报告

写入：

```text
D:\BattleMap\battle-map\docs\enterprise\reviews\non-mox-modules-mox-reference-independent-review.md
```

报告必须记录：

- REVIEWED_HEAD；
- alignment implementation report；
- shared runtime 调用图；
- 四模块 Gap Matrix 独立复核；
- duplicate mechanism / hidden consumer 数量；
- Customer；
- Progress；
- Heatmap；
- Metric；
- API/DB；
- tests/build；
- V0.2 blockers；
- blocking findings。

---

## 19. PASS 条件

只有全部满足才能 PASS：

1. 四模块真实复用 shared runtime mechanism；
2. 每模块业务字段仍独立；
3. Table/Create/Edit bidirectional conformance 通过；
4. Runtime Field/Options Authority 正确；
5. Customer chain 统一；
6. Progress history single-source；
7. Heatmap canonical；
8. Metric/shared filter mechanism；
9. API canonical-only；
10. DB round-trip；
11. duplicate/legacy/hidden consumer blocking count = 0；
12. MOX 无回归；
13. full tests/build通过；
14. 无 blocking finding。

V0.2 尚未 Authority 化的纯业务字段变化可以记录 blocker，但不能被误修。

---

## 20. 最终短回执

```text
NON-MOX → MOX REFERENCE INDEPENDENT REVIEW
RESULT=PASS/FAIL/PARTIAL
REVIEWED_HEAD=
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
DUPLICATE_MECHANISMS=0或数量
ACTIVE_LEGACY_KEYS=0或数量
UNDECLARED_CONSUMERS=0或数量
MOX_REGRESSION=PASS/FAIL
FULL_TESTS=PASS/FAIL
BUILD=PASS/FAIL
V0_2_BLOCKERS=NONE或内容
BLOCKING_FINDINGS=NONE或内容
NEXT=USER_MANUAL_ACCEPTANCE/V0_2_AUTHORITY_REVIEW/REMEDIATION
```
