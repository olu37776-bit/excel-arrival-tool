# 企业作战地图：TOB / ISP / 电力 / 大企向 MOX Reference Implementation 全面对齐 V1

**状态：CURRENT REMEDIATION / IMPLEMENTATION AUTHORITY**  
**适用模块：TOB、ISP、电力、大企**  
**参考实现：当前已通过 End-to-End Canonical Independent Review 的 MOX 实现**  
**共享架构：`enterprise-contract-architecture-v5.md`**  
**运行时字段规则：`architecture/enterprise-runtime-field-options-contract-v1.md`**  
**代码工作树：`D:\BattleMap\battle-map`**  
**代码分支：`feature/enterprise-battle-map`**

---

## 1. 背景与结论

当前人工验收已经确认：MOX 的整体页面与运行机制已经经过多轮 Contract 收敛、4-group renderer 修复、Customer relation 修复、Heatmap canonical 化、Progress 单一事实源和独立审查；而 TOB / ISP / 电力 / 大企虽然各自已有 Canonical Authority，但实际页面实现仍然存在明显偏差。

最新已确认的典型问题包括：

- 四模块 Create 曾在打开弹窗时因错误检查 `f.type` 而不是 `fieldDef.type`，导致 select 字段 `options` 未初始化并报 `f.options is not iterable`；
- 该错误证明四模块仍存在与 MOX 不一致的 Runtime Field View Model / options enrichment 实现；
- 现有四模块 Authority 仍引用早期共享架构版本，无法完整表达 MOX 后续已验证的 runtime canonical-only、真实 renderer conformance、Heatmap canonical key、Progress History single source 等要求；
- 当前不能再把四模块视为“只剩局部 bug”，而应视为 **MOX Reference Implementation 机制未真正推广到四模块**。

因此下一阶段目标不是复制 MOX 字段，而是把四模块的 **实现机制** 全面收敛到当前 MOX Reference Implementation。

---

## 2. 核心原则：参考机制，不复制业务字段

目标：

```text
MOX verified mechanism
        ↓
shared runtime / renderer / adapters / validators
        ↓
TOB Field Contract
ISP Field Contract
Power Field Contract
Large Enterprise Field Contract
```

禁止：

```text
TOB import MOX field array
ISP copy MOX Create component
Power hardcode MOX fields
Large Enterprise reuse MOX DB columns
```

必须做到：

- 共享机制来自 MOX 已验证实现；
- 各模块字段集合、顺序、group、枚举、API/DB mapping 由自己的 Canonical Authority 决定；
- 模块间共享的是 **engine / adapter / renderer / validator / customer relation / progress mechanism / metric execution pattern**；
- 不建立 cross-module business field dependency。

---

## 3. 当前业务字段 Authority 暂不在本轮重定义

在 Excel V0.1 → V0.2 差异调查和 Authority Review 完成前，本轮不得自行增加、删除、改名 TOB / ISP / 电力 / 大企的业务字段。

当前字段基线暂沿用：

- `tob-canonical-authority-v2.md`
- `isp-canonical-authority-v2.md`
- `power-canonical-authority-v2.md`
- `large-enterprise-canonical-authority-v2.md`

本文件只取代这些 V2 文档中与“共享实现机制 / shared architecture version / runtime implementation”相关且与当前 V5 架构冲突的内容。

Excel V0.2 如改变字段、group、option set 或业务语义，应先由 Authority Review 发布对应模块新版本，再实施最终字段变化。

---

## 4. MOX Reference Implementation 需要推广的机制清单

### 4.1 Field Contract 是唯一字段 Authority

四模块都必须做到：

```text
Module Field Contract
├─ Table runtime
├─ Create runtime
├─ Edit runtime
├─ API canonical mapping
├─ database.js mapping
├─ SQLite persistence/relation
├─ Metric field references
├─ Heatmap field references
└─ Progress special projection
```

页面组件不得维护第二套完整字段数组、分组数组、排序数组或 enum 字典。

### 4.2 Runtime Field View Model

必须复用 MOX 已验证的 field definition → runtime field model 机制。

字段静态定义 Authority 来源：

```text
fieldDef.type
fieldDef.controlId / editorId
fieldDef.validation / optionSetId
fieldDef.group
fieldDef.order
```

Runtime Field View Model 只追加动态状态，例如：

```text
value
options
readonly/loading/error
```

不得再出现：

```text
fieldDef.type = select
但 f.type = undefined
然后 runtime 根据 f.type 判断 select
```

所有 options-bearing control 必须由明确的 Dynamic Options Provider 生成 Array contract。

### 4.3 Create / Edit Renderer

TOB / ISP / 电力 / 大企统一使用 MOX 已验证后的共享 Create/Edit shell、group renderer、field renderer、validation presentation 和 spacing mechanism。

四模块正确 group 均为：

```text
客户信息
业务格局
作战情况
```

要求：

- group 来自 Contract；
- 不写死 3 组字段数组；
- Create/Edit 使用同一 shared renderer；
- group 间距、标题层级、分隔方式与当前 MOX 使用同一共享样式；
- 模块差异仅由 Contract projection 决定。

### 4.4 Runtime Projection

每个模块只能有一套真实 runtime projection 算法。

必须验证：

```text
Contract expected Table keys == actual Table renderer keys
Contract expected Create keys == actual Create renderer keys
Contract expected Edit keys == actual Edit renderer keys
```

并验证：

- 无缺失；
- 无额外；
- 无重复；
- order 一致；
- group 一致；
- control/editor 一致。

测试必须覆盖 Production 真实调用路径。

### 4.5 Customer Relation

五模块统一使用当前已验证的 Customer 共享链：

```text
customers.customer_id
→ database.js customer query
→ shared customer API
→ frontend normalization
→ dynamic customer options
→ unique customer selection
→ business record.customer_id
```

四模块不得拥有独立 customer SQL / private customer fetch / customer name relation。

Create 初始化异常必须区分：

```text
CUSTOMER_FETCH_FAILED
CUSTOMER_RESPONSE_CONTRACT_FAILED
OPTIONS_PROVIDER_FAILED
FORM_RUNTIME_FAILED
```

禁止再次把 Runtime TypeError 包装成“获取客户数据失败”。

### 4.6 Progress

四模块必须和当前 MOX 保持同一 Progress 机制：

```text
Progress History = 唯一持久化事实源
battleProgress = latest/current canonical projection
独立进展弹窗 = History 新增/编辑入口
```

要求：

- 页面行操作进入独立进展弹窗；
- 不退化为普通 textarea；
- 不在业务表维护第二份可写 progress text；
- 不双写、不 fallback；
- 表格/详情读取 latest/current projection；
- 若当前 TOB/ISP/Power/Large 仍存在不同 Progress 实现，向 verified shared mechanism 收敛。

### 4.7 Heatmap

Heatmap 继续使用共享 `HeatmapChart`，但四模块所有业务字段 identity 必须 canonical。

```text
Heatmap canonical field key
→ module record canonical field
```

禁止：

- 中文 label 作为 record lookup key；
- SQLite column 直接进入前端 Heatmap identity；
- 复制 MOX Heatmap 业务字段/规则到其他模块。

各模块业务 Heatmap 规则未冻结的部分保持 empty-state，不造假。

### 4.8 Metric

四模块使用当前共享 Metric execution mechanism：

```text
Metric Contract.where
→ calculation
→ click-to-filter
```

同一 where 必须同时负责指标计算和点击筛选。

不得页面内再维护另一份 if/switch 条件。

### 4.9 API canonical-only

四模块的 active API request/response 必须使用 canonical key。

禁止：

- legacy alias；
- 中文 label payload；
- runtime fallback；
- 模块私有旧字段翻译层。

一次性 Migration 可以识别旧字段，runtime 不可以。

### 4.10 database.js / SQLite

每个 canonical key 必须通过 module persistence mapping 对应唯一 DB column / relation。

要求：

- CRUD round-trip；
- customer_id relation；
- Progress History relation；
- 新建库和 Migration 后 Schema 一致；
- legacy runtime mapping = 0；
- 模块之间不得 import 对方 persistence mapping。

---

## 5. 页面层全面对齐范围

本轮“页面向 MOX 对齐”至少包括以下用户可见结构和交互机制。

### 5.1 模块主页骨架

```text
模块专项
→ 空间洞察 / 当年项目 / 空间拓展
→ Heatmap
→ 新增 + 表格
```

页面结构、spacing、卡片风格、表格壳、按钮位置、空状态、loading/error presentation 应使用同一共享设计语言。

模块业务文案和字段内容仍各自独立。

### 5.2 Table

全面对齐：

- Contract projection；
- column renderer；
- formatter；
- filter/search/sort；
- Metric click filter；
- row actions；
- Edit；
- Progress popup action；
- loading/error/empty state。

特别检查是否存在中文 label / legacy key / module-local column array 绕过 Contract。

### 5.3 Create

全面对齐：

- modal shell；
- group renderer；
- customer initialization；
- dynamic options provider；
- select/textarea/number/percent controls；
- validation；
- submit payload；
- error boundary；
- close/reset lifecycle。

### 5.4 Edit

全面对齐：

- shared modal shell；
- same Contract-driven renderer；
- customer fields readonly；
- customer_id 不可被编辑流程改变；
- special progress editor/history behavior；
- update canonical payload；
- validation/error handling。

---

## 6. 先做 Gap Matrix，再实施

Implementation Agent 不得一上来复制 MOX 文件。

必须先为每个模块建立：

```text
MOX verified mechanism
vs
TOB actual
vs
ISP actual
vs
Power actual
vs
Large actual
```

至少覆盖：

1. Field Contract source；
2. Table Projection；
3. Create Projection；
4. Edit Projection；
5. Runtime Field View Model；
6. Dynamic Options Provider；
7. shared modal/renderer；
8. Customer query/normalization；
9. Create payload；
10. Edit payload；
11. Progress popup/history；
12. Heatmap field identity；
13. Metric engine；
14. filter/search/sort；
15. API canonical mapping；
16. database.js mapping；
17. SQLite relation/schema；
18. tests；
19. hidden legacy consumers。

每项分类：

```text
ALIGNED
DUPLICATED_MECHANISM
LEGACY_PATH
LOCAL_REIMPLEMENTATION
MISSING
BUSINESS_DIFFERENCE_EXPECTED
BLOCKED_BY_V0_2_AUTHORITY
```

只有建立 Gap Matrix 后才能改代码。

---

## 7. 实施策略

### Phase A：共享 Runtime 收敛

先收敛真正应该共享的机制：

- runtime projection helpers；
- Runtime Field View Model；
- dynamic options；
- Create/Edit shell；
- group renderer/style；
- customer relation；
- error boundary；
- Progress shared mechanism；
- Metric execution helper；
- Heatmap canonical field adapter；
- conformance validators。

要求 MOX 回归全部通过。

### Phase B：模块接入

按顺序：

```text
TOB
→ ISP
→ Power
→ Large Enterprise
```

每个模块接入自己的 Contract，不复制 MOX Contract。

每完成一个模块立即执行模块级测试和 MOX regression。

### Phase C：统一清理

完成四模块接入后清理：

- module-local duplicate runtime helpers；
- legacy field arrays；
- old options enrichment；
- private customer fetch；
- duplicated Progress writes；
- label-based lookup；
- dead Projection API；
- obsolete tests。

不得在未确认无消费者前删除。

---

## 8. 与 Excel V0.2 的协调

当前 V0.1 → V0.2 Excel Diff Survey 可与本轮 Gap Matrix 并行进行。

规则：

- shared mechanism 可以先对齐；
- **业务字段新增/删除/改名/group/option-set 变化必须等待 V0.2 Authority Review**；
- 如果实施过程中某模块字段问题明显来自 V0.2 变化，标记 `BLOCKED_BY_V0_2_AUTHORITY`，不要自行猜测；
- V0.2 Authority 更新后再完成最终 Contract projection。

这样避免重新建设四套错误页面，同时也避免刚改完 V0.1 字段又因 V0.2 重做。

---

## 9. 自动门禁

### 每模块

必须覆盖：

- exact Contract key count；
- Table/Create/Edit bidirectional conformance；
- exact 3 groups；
- Create dialog opens；
- Edit dialog opens；
- options-bearing field uses fieldDef/static definition authority；
- customer_id chain；
- customer readonly on Edit；
- Progress popup/history；
- Progress double write = 0；
- Heatmap canonical key；
- Metric values + click filter；
- API canonical-only；
- database round-trip。

### 全企业

必须覆盖：

```text
MOX regression
TOB suite
ISP suite
Power suite
Large suite
enterprise suite
full Vitest
build
lint/typecheck（如已有）
```

### Hidden Consumer Gate

企业代码范围扫描目标：

```text
MODULE_LOCAL_FULL_FIELD_ARRAYS = 0（除Contract定义）
LEGACY_RUNTIME_KEYS = 0
LABEL_AS_FIELD_IDENTITY = 0
DUPLICATE_CUSTOMER_FETCH = 0
PROGRESS_DOUBLE_WRITE = 0
DUPLICATE_PROJECTION_ALGORITHMS = 0
UNDECLARED_OPTIONS_TYPE_AUTHORITY = 0
```

---

## 10. 人工验收

自动验证通过后，用户逐模块人工检查：

### TOB / ISP / 电力 / 大企

- 点击新增能正常打开；
- 三个 group 结构和视觉与 MOX 同一设计语言；
- 字段内容是模块自己的，不混入 MOX 字段；
- 动态下拉正常；
- 编辑能打开且正确回填；
- 客户信息 edit readonly；
- Progress 独立弹窗正常；
- Heatmap 正常或按 Authority empty-state；
- Table/筛选/统计交互正常。

页面视觉“同机制”不要求模块业务字段数量完全相同。

---

## 11. WRITE_SCOPE

允许：

- enterprise shared runtime / renderer / adapter / validator；
- TOB / ISP / Power / Large 页面及 Contract 接入；
- customer shared runtime；
- Progress shared runtime；
- module Heatmap canonical adapter；
- module API/database mapping；
- tests；
- 必要 remediation report。

暂时禁止（等待 V0.2 Authority Review）：

- 自行改变四模块业务字段集合；
- 自行改变 Excel-derived label/group/option-set；
- 企业首页；
- MOX 已冻结业务字段；
- 非企业模块。

如果 V0.2 Authority 在任务期间发布，Agent 必须明确记录所采用 Authority version，不能混用新旧版本。

---

## 12. 实施报告

创建：

```text
docs/enterprise/remediations/non-mox-modules-mox-reference-alignment-report.md
```

至少记录：

- BASE_HEAD / FINAL_HEAD；
- Gap Matrix；
- shared mechanisms extracted/reused；
- per-module changed files；
- duplicate mechanisms removed；
- customer chain；
- Progress chain；
- Heatmap canonical result；
- API/DB result；
- tests/build；
- V0.2-blocked items；
- remaining hidden consumers。

最终短回执：

```text
NON-MOX MODULES → MOX REFERENCE ALIGNMENT
RESULT=COMPLETE/PARTIAL/BLOCKED
BASE_HEAD=
FINAL_HEAD=
GAP_MATRIX=CREATED/FAIL
SHARED_RUNTIME=PASS/FAIL
TOB=PASS/FAIL/BLOCKED_V0_2
ISP=PASS/FAIL/BLOCKED_V0_2
POWER=PASS/FAIL/BLOCKED_V0_2
LARGE=PASS/FAIL/BLOCKED_V0_2
CREATE_EDIT_RUNTIME=PASS/FAIL
CUSTOMER_CHAIN=PASS/FAIL
PROGRESS_SINGLE_SOURCE=PASS/FAIL
HEATMAP_CANONICAL=PASS/FAIL
METRIC=PASS/FAIL
API_DB=PASS/FAIL
HIDDEN_CONSUMERS=0或数量
MOX_REGRESSION=PASS/FAIL
FULL_TESTS=PASS/FAIL
BUILD=PASS/FAIL
V0_2_BLOCKERS=NONE或内容
OUT_OF_SCOPE_CHANGES=NO/YES
NEXT=INDEPENDENT_REVIEW/WAIT_V0_2_AUTHORITY/REMEDIATION
```
