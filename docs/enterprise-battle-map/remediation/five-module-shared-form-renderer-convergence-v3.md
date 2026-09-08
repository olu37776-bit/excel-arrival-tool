# Five-Module Shared Form Renderer Convergence V3

**状态：HISTORICAL IMPLEMENTATION BASELINE / SHARED RENDERER REGRESSION RULES**  
**取代：`five-module-shared-form-renderer-convergence-v2.md` 作为本轮实施执行规范；V2保留设计背景**  
**适用模块：MOX、TOB、ISP、电力、大企**  
**代码工作树：`D:\BattleMap\battle-map`**  
**代码分支：`feature/enterprise-battle-map`**

---

当前执行任务以 authority-index.md 为准；本文件保留共享渲染链规则，不代表当前仍有同一阻塞。下面的字段数量已与当前模块规范同步；已授权 Excel 两项改动按独立任务实施，不能用本文件的旧字段冻结限制撤销该授权。

## 1. 本轮唯一目标

该轮历史 Independent Review 曾证明：企业模块虽然部分 Contract / Projection / Runtime Field 已开始共享，但 Create/Edit 到真实 Vue Render Tree 的最后一段仍存在 module-local form builder。

本轮必须把五个模块真正收敛到一条生产渲染链：

```text
Module Field Contract
→ Shared Table/Create/Edit Projection
→ Shared Runtime Field View Model
→ Shared Dynamic Options / Control / Editor Registry
→ Shared Form Shell
→ Shared Group Renderer
→ Shared Field Renderer
→ Actual Vue Render Tree
```

本轮不是“让页面长得一样”，也不是“把五套代码搬到shared目录”，而是让五个模块的真实 Create/Edit production path 最终消费同一套 renderer mechanism。

---

## 2. 实施前置与安全要求

开始前必须执行并记录：

```text
git branch --show-current
git status --short
git log -1 --oneline
```

必须满足：

- 当前分支为 `feature/enterprise-battle-map`；
- 只有当前一个写 Agent 操作 `D:\BattleMap\battle-map`；
- 记录 `BASE_HEAD`；
- 不 reset；
- 不 rebase；
- 不 clean；
- 不丢弃现有成果；
- 不覆盖尚未提交的其他修改。

如存在并发写 Agent，返回：

```text
BLOCKED_CONCURRENT_WRITER
```

---

## 3. 必读 Authority

必须完整读取：

```text
D:\BattleMap\BattleMapenterprise-authority\docs\enterprise-battle-map\authority-index.md
D:\BattleMap\BattleMapenterprise-authority\docs\enterprise-battle-map\enterprise-contract-architecture-v5.md
D:\BattleMap\BattleMapenterprise-authority\docs\enterprise-battle-map\architecture\enterprise-runtime-field-options-contract-v1.md
D:\BattleMap\BattleMapenterprise-authority\docs\enterprise-battle-map\mox-canonical-authority-v6.md
D:\BattleMap\BattleMapenterprise-authority\docs\enterprise-battle-map\remediation\five-module-shared-form-renderer-convergence-v3.md
```

同时读取：

```text
D:\BattleMap\battle-map\docs\enterprise\reviews\non-mox-modules-mox-reference-independent-review.md
```

以及当前：

```text
tob-canonical-authority-v2.md
isp-canonical-authority-v2.md
power-canonical-authority-v2.md
large-enterprise-canonical-authority-v2.md
```

Excel V0.2 尚未 Authority 化的业务字段变化不在本轮实施。

---

## 4. Phase 0：Five-Module Form Render Inventory

**修改任何代码前必须先完成本阶段。**

分别恢复 MOX、TOB、ISP、Power、Large 的真实 Create 和 Edit production path。

每模块记录：

```text
MODULE
CREATE_ROUTE_OR_PAGE
CREATE_ACTION
CREATE_FIELD_CONTRACT
CREATE_PROJECTION
CREATE_RUNTIME_FIELD_BUILDER
CREATE_OPTIONS_PROVIDER
CREATE_FORM_SHELL
CREATE_GROUP_RENDERER
CREATE_FIELD_RENDERER
CREATE_ACTUAL_TEMPLATE_OR_RENDER_FUNCTION
CREATE_FINAL_RENDER_TREE_ENTRY

EDIT_ROUTE_OR_PAGE
EDIT_ACTION
EDIT_FIELD_CONTRACT
EDIT_PROJECTION
EDIT_RUNTIME_FIELD_BUILDER
EDIT_OPTIONS_PROVIDER
EDIT_FORM_SHELL
EDIT_GROUP_RENDERER
EDIT_FIELD_RENDERER
EDIT_ACTUAL_TEMPLATE_OR_RENDER_FUNCTION
EDIT_FINAL_RENDER_TREE_ENTRY

LOCAL_FORM_BUILDER_FILE
LOCAL_FORM_BUILDER_FUNCTION_OR_TEMPLATE_REGION
SHARED_COMPONENTS_IMPORTED
SHARED_COMPONENTS_ACTUALLY_USED_IN_PRODUCTION_PATH
```

必须明确：

```text
MOX_LOCAL_FORM_BUILDER=YES/NO
TOB_LOCAL_FORM_BUILDER=YES/NO
ISP_LOCAL_FORM_BUILDER=YES/NO
POWER_LOCAL_FORM_BUILDER=YES/NO
LARGE_LOCAL_FORM_BUILDER=YES/NO
```

禁止通过文件名、import、测试代码推断“已经共享”；必须追到真实页面 render tree。

Inventory 写入实施报告的第一部分。

---

## 5. 根据 MOX 调查结果选择实施路径

### 5.1 MOX 已经真实共享

如果：

```text
MOX_LOCAL_FORM_BUILDER=NO
```

则以 MOX 当前真实 production shared path 为实现基线，依次迁入：

```text
TOB → ISP → Power → Large
```

### 5.2 MOX 仍是 local builder

如果：

```text
MOX_LOCAL_FORM_BUILDER=YES
```

则必须：

```text
MOX 已验证行为
→ 提炼 Shared Form Shell / Group Renderer / Field Renderer
→ MOX 自己先迁入 shared renderer
→ MOX Production-path tests
→ MOX regression PASS
→ TOB
→ ISP
→ Power
→ Large
```

MOX 的业务行为是 Reference，MOX 的私有 builder 不是长期 Reference。

---

## 6. Shared Form Renderer 责任边界

### 6.1 Shared Form Shell

唯一 shared shell 负责：

- dialog/modal container；
- title、close；
- loading；
- error presentation；
- empty state；
- submitting/disabled state；
- submit/cancel lifecycle；
- reset/close lifecycle；
- form-level validation presentation；
- group container；
- group spacing；
- form-level layout；
- 按本地主分支MOX/TOB对应模式保留固定取消/保存底栏及按钮样式，内容滚动时操作栏不被卷走；本次不扩大为其他字段或整体表单样式改造。

模块页面只允许提供：

- module identity；
- mode（create/edit）；
- runtime fields；
- form model；
- submit adapter/handler；
- 经过 Authority 证明的最小 extension hook。

模块页面不得继续构造完整 form DOM。

### 6.2 Shared Group Renderer

唯一 group Authority：

```text
field.group
```

shared group renderer 只能执行：

```text
group order
→ group wrapper
→ group title
→ field iteration
```

不得重新定义 group 名称、字段归属、module section map。

业务 group：

MOX：

```text
客户信息
无线格局
微波格局
作战情况
```

TOB / ISP / Power / Large：

```text
客户信息
业务格局
作战情况
```

### 6.3 Shared Field Renderer

字段控件 dispatch 的唯一静态来源：

```text
fieldDef.type
fieldDef.controlId
fieldDef.editorId
```

由 shared registry / renderer 分发至少：

- text；
- select；
- textarea；
- number；
- percent；
- readonly；
- registered special editor。

模块不得维护完整本地 `if/switch` 字段渲染器。

### 6.4 Create/Edit 共用 renderer

必须形成：

```text
Create Projection → shared runtime fields → shared renderer
Edit Projection   → shared runtime fields → shared renderer
```

Create/Edit 差异只能来自：

- visible；
- editable/readonly；
- controlId/editorId；
- validation；
- runtime value/options/state。

不得继续维护 Create template A + Edit template B 作为第二业务 Authority。

---

## 7. 明确禁止的“伪共享”实现

以下任何一种都判定本轮失败：

### 7.1 Shared 文件内维护五套完整模板

```text
if module === MOX → A
if module === TOB → B
if module === ISP → C
...
```

如果每个 branch 都维护完整 form 结构，仍然是五套 builder。

### 7.2 Shared Shell + Module-local Body

shared 组件只负责 dialog 外壳，而 group/field DOM 仍在各页面本地构造，仍判：

```text
MODULE_LOCAL_FORM_HTML_BUILDERS > 0
```

### 7.3 Import Shared Helper 但生产路径绕过

存在 import 不代表使用。actual render tree 必须真正经过 shared renderer。

### 7.4 测试共享、生产不共享

测试直接调用 shared renderer，但真实页面仍使用 local builder，判 FAIL。

### 7.5 复制 MOX Template

复制 MOX 的正确模板到其他模块不属于共享。

---

## 8. Runtime Field / Dynamic Options 回归要求

必须保持已修复链：

```text
Field Contract / fieldDef
→ Runtime Projection
→ options-bearing detection
→ Dynamic Options Provider
→ runtime field.options:Array
→ Shared Field Renderer
```

不得重新出现：

```text
fieldDef.type='select'
f.type=undefined
runtime却检查f.type
```

五模块至少验证：

```text
region
representativeOffice
country
customerName
```

并验证：

- Create dialog 正常打开；
- `f.options is not iterable` 不再出现；
- `customer_id` 保留；
- 合法无候选为 `[]`；
- Customer API failure 不伪装成空 options；
- Runtime/Options failure 不被包装成 Customer Fetch failure。

---

## 9. Customer 回归边界

Customer 模型不在本轮重构。

必须保持：

```text
customers.customer_id
→ shared database query
→ shared API
→ frontend normalization
→ dynamic options
→ unique selection
→ business record.customer_id
```

禁止重新引入：

- module-private customer SQL；
- module-private customer fetch；
- 以 customerName 作为关系 identity；
- 同名客户默认第一条；
- customer_id 在 options/payload 中丢失。

---

## 10. Progress 回归边界

Progress History 仍是唯一持久化事实源：

```text
Progress History
→ latest/current projection
→ battleProgress
```

独立Progress popup必须保留，但不能代替原表单内新增入口。主分支MOX/TOB对应模式原有能力须由共享特殊editor承载；Create/Edit原本不同，不能强制相同或把某模式的摘要/展开编辑复制到另一模式。原本具备摘要、展开新增按钮及主题/内容编辑的入口不得退化成整个区域readonly。
用户仅要求进展可见文案加“作战”，保留限定词及原模式功能/保存语义；当前只对照底栏按钮样式和进展区域两块，其他表单字体/布局不动。双滚动用户确认可接受，不以滚动条数量判断共享失败。当前先按 `investigation/enterprise-form-progress-legacy-parity-survey-v2.md` 只读对照，不继承本文件历史实施写入权限。

Shared Form Renderer 只处理 Contract 投影到表单时的 editor binding，不得：

- 把popup或原表单内特殊editor降级为普通textarea/仅readonly摘要；
- 因独立popup存在而删除表单内原有新增按钮与展开区；
- 恢复 business-table progress text；
- double write；
- fallback。

---

## 11. Heatmap / Metric / API / DB 不得回归

本轮不改变这些业务规则，但必须回归验证：

### Heatmap

```text
LABEL_AS_FIELD_IDENTITY=0
```

字段 lookup 必须 canonical key。

### Metric

```text
Metric Contract.where
→ calculation
→ click-to-filter
```

必须继续使用同一个 where。

### API

active runtime 必须 canonical-only，无 legacy alias/fallback。

### database.js / SQLite

必须保持 canonical mapping、customer relation、Progress relation、CRUD round-trip、新库/升级库一致。

---

## 12. 五模块迁移顺序与每步门禁

### 若 MOX 需要迁移

```text
MOX
→ TOB
→ ISP
→ Power
→ Large
```

### 若 MOX 已共享

```text
TOB
→ ISP
→ Power
→ Large
```

每完成一个模块立即执行：

```text
该模块 Create production-path test
该模块 Edit production-path test
shared renderer tests
MOX regression
```

任一步失败必须先修复，不能继续迁下一个模块。

---

## 13. Dead Code / Duplicate Authority 清理

五模块全部进入 shared renderer 后，全仓企业 production source 扫描：

```text
module-local full form HTML builders
module-local section/group schemas
module-local field renderer switches
module-local validation renderers
module-local options renderers
module-local Create shells
module-local Edit shells
```

确认无 Production consumer 后删除。

测试不得继续引用废弃 builder，使其以 test-only 形式成为第二 Authority。

最终目标：

```text
MODULE_LOCAL_FORM_HTML_BUILDERS=0
MODULE_LOCAL_SECTION_SCHEMAS=0
DUPLICATE_SECTION_RENDER_PATHS=0
DUPLICATE_FIELD_RENDERERS=0
DUPLICATE_FORM_SHELLS=0
DUPLICATE_VALIDATION_RENDERERS=0
```

---

## 14. Architecture / Static Gate

必须建立防回归门禁，扫描真实 production source：

```text
MOX_USES_SHARED_FORM_RENDERER=PASS
TOB_USES_SHARED_FORM_RENDERER=PASS
ISP_USES_SHARED_FORM_RENDERER=PASS
POWER_USES_SHARED_FORM_RENDERER=PASS
LARGE_USES_SHARED_FORM_RENDERER=PASS
MODULE_LOCAL_FORM_HTML_BUILDERS=0
MODULE_LOCAL_SECTION_SCHEMAS=0
DUPLICATE_SECTION_RENDER_PATHS=0
DUPLICATE_FIELD_RENDERER_SWITCHES=0
DUPLICATE_FORM_SHELLS=0
DUPLICATE_VALIDATION_RENDERERS=0
```

门禁必须能失败，不能只是统计信息。

---

## 15. Production-path Conformance Tests

必须从真实页面入口证明：

```text
page/route
→ Create/Edit action
→ module Contract
→ shared Projection
→ shared Runtime Field Model
→ shared Form Renderer
→ actual render tree
```

### MOX

- 40项最终业务字段完整；视图集合按当前 Contract 的 visibility/mode 派生并双向核对；
- 4 groups exact；
- Create/Edit 都走 shared renderer。

### TOB

- 33项最终业务字段完整；视图集合按当前 Contract 的 visibility/mode 派生并双向核对；
- 3 groups exact；
- Create/Edit 都走 shared renderer。

### ISP

- 24项最终业务字段完整；视图集合按当前 Contract 的 visibility/mode 派生并双向核对；
- 3 groups exact；
- Create/Edit 都走 shared renderer。

### Power

- 27项最终业务字段完整；视图集合按当前 Contract 的 visibility/mode 派生并双向核对；
- 3 groups exact；
- Create/Edit 都走 shared renderer。

### Large

- 25项最终业务字段完整；视图集合按当前 Contract 的 visibility/mode 派生并双向核对；
- 3 groups exact；
- Create/Edit 都走 shared renderer。

测试不得 mock 掉 shared renderer 后只检查 props。

---

## 16. 视觉与交互回归

自动测试验证结构/class；最终视觉由用户人工验收。

必须保持：

- MOX 4-group spacing；
- Non-MOX 3-group 使用同一 spacing mechanism；
- Create/Edit样式一致；
- validation presentation一致；
- select/text/textarea/number/percent行为一致；
- Edit customer fields readonly；
- submit/cancel/reset lifecycle正常。

---

## 17. WRITE_SCOPE

允许修改：

- enterprise shared Form Shell；
- shared Group Renderer；
- shared Field Renderer；
- shared Control/Editor Registry；
- Runtime Field Model 与 renderer 的直接接口；
- 五模块 Create/Edit 接入；
- 直接相关 dead code；
- Production-path tests；
- Architecture/static tests；
- 实施报告。

禁止修改：

- 五模块业务字段集合；
- Metric业务公式；
- Heatmap业务口径；
- Customer数据模型；
- Progress persistence model；
- 企业首页；
- Excel V0.2尚未Authority化字段；
- 非企业模块。

---

## 18. 自动验证顺序

按顺序至少执行：

1. shared form renderer tests；
2. architecture/static duplicate gate；
3. MOX Create/Edit production-path suite；
4. TOB Create/Edit production-path suite；
5. ISP Create/Edit production-path suite；
6. Power Create/Edit production-path suite；
7. Large Create/Edit production-path suite；
8. Runtime Field/Options tests；
9. Customer tests；
10. Progress tests；
11. Heatmap canonical regression；
12. Metric regression；
13. API/database regression；
14. enterprise suite；
15. full Vitest；
16. build；
17. lint/typecheck（如已有）。

不得通过删除测试、降低断言、恢复local builder或恢复legacy fallback使测试通过。

---

## 19. 实施报告

必须创建：

```text
D:\BattleMap\battle-map\docs\enterprise\remediations\five-module-shared-form-renderer-convergence-report-v3.md
```

报告必须包含：

### 19.1 Execution Identity

```text
BASE_HEAD
FINAL_HEAD
BRANCH
```

### 19.2 Five-Module Form Render Inventory

完整记录 Phase 0 的五模块 Create/Edit production path。

### 19.3 Before / After

至少记录：

```text
MOX_LOCAL_FORM_BUILDER_BEFORE
TOB_LOCAL_FORM_BUILDER_BEFORE
ISP_LOCAL_FORM_BUILDER_BEFORE
POWER_LOCAL_FORM_BUILDER_BEFORE
LARGE_LOCAL_FORM_BUILDER_BEFORE

FINAL_SHARED_FORM_SHELL
FINAL_SHARED_GROUP_RENDERER
FINAL_SHARED_FIELD_RENDERER
FINAL_SHARED_REGISTRY
```

### 19.4 Removed Duplicate Paths

列出所有删除/废弃 builder、section schema、field renderer、form shell。

### 19.5 Evidence

每一个 PASS 或 `=0` 必须附：

```text
CODE_EVIDENCE=file:function/component
PRODUCTION_PATH_EVIDENCE=test/call-chain
STATIC_SCAN_EVIDENCE=query/result
```

### 19.6 Verification

记录所有 suite / full Vitest / build / lint-typecheck 结果。

Implementation Agent 只能声明：

```text
IMPLEMENTED
```

不得声明 VERIFIED。

---

## 20. 完成门槛

只有以下全部满足才可声明 Implementation COMPLETE：

```text
MOX_USES_SHARED_FORM_RENDERER=PASS
TOB_USES_SHARED_FORM_RENDERER=PASS
ISP_USES_SHARED_FORM_RENDERER=PASS
POWER_USES_SHARED_FORM_RENDERER=PASS
LARGE_USES_SHARED_FORM_RENDERER=PASS
MODULE_LOCAL_FORM_HTML_BUILDERS=0
MODULE_LOCAL_SECTION_SCHEMAS=0
DUPLICATE_SECTION_RENDER_PATHS=0
DUPLICATE_FIELD_RENDERERS=0
DUPLICATE_FORM_SHELLS=0
DUPLICATE_VALIDATION_RENDERERS=0
RUNTIME_FIELD_OPTIONS=PASS
CUSTOMER_REGRESSION=PASS
PROGRESS_REGRESSION=PASS
HEATMAP_REGRESSION=PASS
METRIC_REGRESSION=PASS
API_DB_REGRESSION=PASS
MOX_REGRESSION=PASS
FULL_TESTS=PASS
BUILD=PASS
OUT_OF_SCOPE_CHANGES=NO
```

如任一失败，结果只能为 PARTIAL/BLOCKED。

---

## 21. 最终短回执

最终只返回：

```text
FIVE-MODULE SHARED FORM RENDERER CONVERGENCE V3
RESULT=COMPLETE/PARTIAL/BLOCKED
BASE_HEAD=
FINAL_HEAD=
MOX_LOCAL_FORM_BUILDER_BEFORE=YES/NO
TOB_LOCAL_FORM_BUILDER_BEFORE=YES/NO
ISP_LOCAL_FORM_BUILDER_BEFORE=YES/NO
POWER_LOCAL_FORM_BUILDER_BEFORE=YES/NO
LARGE_LOCAL_FORM_BUILDER_BEFORE=YES/NO
MOX_USES_SHARED_FORM_RENDERER=PASS/FAIL
TOB_USES_SHARED_FORM_RENDERER=PASS/FAIL
ISP_USES_SHARED_FORM_RENDERER=PASS/FAIL
POWER_USES_SHARED_FORM_RENDERER=PASS/FAIL
LARGE_USES_SHARED_FORM_RENDERER=PASS/FAIL
MODULE_LOCAL_FORM_HTML_BUILDERS=
MODULE_LOCAL_SECTION_SCHEMAS=
DUPLICATE_SECTION_RENDER_PATHS=
DUPLICATE_FIELD_RENDERERS=
DUPLICATE_FORM_SHELLS=
DUPLICATE_VALIDATION_RENDERERS=
RUNTIME_FIELD_OPTIONS=PASS/FAIL
CUSTOMER_REGRESSION=PASS/FAIL
PROGRESS_REGRESSION=PASS/FAIL
HEATMAP_REGRESSION=PASS/FAIL
METRIC_REGRESSION=PASS/FAIL
API_DB_REGRESSION=PASS/FAIL
MOX_REGRESSION=PASS/FAIL
FULL_TESTS=PASS/FAIL
BUILD=PASS/FAIL
OUT_OF_SCOPE_CHANGES=NO/YES
BLOCKERS=NONE或内容
NEXT=FULL_NON_MOX_INDEPENDENT_REVIEW_RERUN_V3
```

---

## 22. 后续门禁

本轮完成后，禁止直接进入人工验收。

对新 HEAD 必须完整执行：

```text
reviews/non-mox-modules-mox-reference-independent-review-v1.md
+
reviews/non-mox-full-independent-review-rerun-v3.md
```

不是只复核 renderer finding。

只有完整 Independent Review：

```text
RESULT=PASS
BLOCKING_FINDINGS=NONE
NEW_BLOCKING_FINDINGS=0
```

才进入用户人工验收。
