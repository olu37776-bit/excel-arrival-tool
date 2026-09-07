# Five-Module Shared Form Renderer Convergence V2

**状态：CURRENT BLOCKING REMEDIATION**  
**取代：`non-mox-shared-form-renderer-convergence-v1.md` 中“MOX 已天然使用 shared renderer”的假设**  
**适用模块：MOX、TOB、ISP、电力、大企**  
**代码工作树：`D:\BattleMap\battle-map`**  
**代码分支：`feature/enterprise-battle-map`**

---

## 1. 已确认问题与本版修正

最新完整 Independent Review 已确认：TOB / ISP / Power / Large 仍存在 4 套 module-local form HTML builder。它们虽然可能在视觉上接近 MOX，并且部分 Field Contract / Projection / Runtime Field 已开始共享，但最终 Create/Edit Vue render tree 仍由模块本地 builder 构造。

同时，当前证据只证明“4 个 non-MOX builder 存在”，**不能据此推断 MOX 已经是 shared renderer consumer**。

因此本版首先增加一个必须回答的问题：

```text
MOX 当前真实 Create/Edit production path
是否也由 MOX-local form builder / template 构造？
```

最终目标不是：

```text
MOX local renderer = reference
→ 其他四模块照着复制
```

而是：

```text
MOX 已验证行为
→ 提炼 shared renderer mechanism
→ MOX 自己迁入 shared renderer
→ TOB / ISP / Power / Large 使用同一 shared renderer
```

只有五个模块最终汇入同一条 production renderer path，才算真正完成共享。

---

## 2. 最终目标架构

五模块 Create/Edit 必须形成：

```text
Module Field Contract
        ↓
Shared Table/Create/Edit Projection
        ↓
Shared Runtime Field View Model
        ↓
Shared Dynamic Options / Control / Editor Registry
        ↓
Shared Form Shell
        ↓
Shared Group Renderer
        ↓
Shared Field Renderer
        ↓
Actual Vue Render Tree
```

模块业务差异只能来自：

- 各自 Field Contract；
- `group` / `order` / `type` / `controlId` / `editorId` / `formatterId` / validation；
- shared registry 中已登记的特殊 editor/control；
- 极少量、明确有业务 Authority 的 adapter / slot / hook。

禁止：

- module-local 完整 Create/Edit HTML builder；
- module-local 完整 section/group schema；
- module-local field type switch；
- module-local validation DOM；
- module-local options DOM；
- module-local dialog shell；
- 把五套 builder 搬进一个 shared 文件但继续按 module switch 维护五套模板；
- 通过复制 MOX 字段或 MOX 业务 group 来实现共享。

---

## 3. 业务结构必须保持独立

共享 renderer 不改变任何业务字段 Authority。

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

字段集合保持当前正式 Canonical Authority；Excel V0.2 尚未 Authority 化的字段变化不在本轮实施。

shared renderer 必须能够仅依赖 Contract 产生不同 group 数量和字段集合，不允许在 renderer 中写：

```text
if module === 'MOX' ...
if module === 'TOB' ...
```

来维护完整业务布局。

---

## 4. Phase 0：先恢复五模块真实 render path

修改代码前必须建立 Five-Module Form Render Inventory。

逐模块记录：

```text
MODULE
CREATE_ROUTE/PAGE
CREATE_ACTION
CREATE_PROJECTION
CREATE_RUNTIME_FIELD_BUILDER
CREATE_FORM_SHELL
CREATE_GROUP_RENDERER
CREATE_FIELD_RENDERER
EDIT_ROUTE/PAGE
EDIT_ACTION
EDIT_PROJECTION
EDIT_RUNTIME_FIELD_BUILDER
EDIT_FORM_SHELL
EDIT_GROUP_RENDERER
EDIT_FIELD_RENDERER
LOCAL_HTML_BUILDER_FILE/FUNCTION/TEMPLATE_REGION
SHARED_COMPONENTS_ACTUALLY_USED
```

特别要求恢复 MOX：

```text
MOX_ACTUAL_CREATE_RENDER_PATH
MOX_ACTUAL_EDIT_RENDER_PATH
MOX_LOCAL_FORM_BUILDER=YES/NO
```

不得通过组件名或 import 推断“已共享”；必须追到实际 production render tree。

### 4.1 根据调查结果分支

如果：

```text
MOX_LOCAL_FORM_BUILDER=NO
```

则以 MOX 当前真实 shared path 为基线，迁入其他四模块。

如果：

```text
MOX_LOCAL_FORM_BUILDER=YES
```

则必须：

1. 从 MOX 已验证行为中提炼 shared shell/group/field renderer；
2. 先让 MOX 迁入 shared renderer；
3. 运行 MOX 全量回归；
4. MOX PASS 后，再依次迁入 TOB / ISP / Power / Large。

不得让“MOX 是 Reference”成为保留 MOX 私有 builder 的理由。

---

## 5. Shared Form Renderer 责任边界

### 5.1 Shared Form Shell

唯一 shared shell 负责：

- modal/dialog container；
- title/close；
- loading/error；
- form lifecycle；
- submit/cancel；
- form-level validation presentation；
- group container；
- stable spacing；
- disabled/submitting state。

模块页面只能提供：

- module id / form mode；
- runtime field collection；
- form model；
- submit handler / adapter；
- 必要且已登记的 extension hook。

### 5.2 Shared Group Renderer

唯一业务来源：

```text
field.group
```

shared group renderer 只做：

```text
group order
→ group wrapper
→ group title
→ field iteration
```

不能重新定义 group 名称、字段归属或 module-specific section map。

### 5.3 Shared Field Renderer

唯一 dispatch 来源：

```text
fieldDef.type
fieldDef.controlId
fieldDef.editorId
```

由 shared registry 分发：

- select；
- text；
- textarea；
- number；
- percent；
- readonly；
- special registered editor。

模块不得维护独立 `if/switch` 版 field renderer。

### 5.4 Create / Edit 共用 renderer

Create/Edit 的区别来自 Projection / editable / readonly / editorId / validation，不来自另一套 HTML Authority。

必须：

```text
Create runtime fields → shared form renderer
Edit runtime fields   → shared form renderer
```

---

## 6. Customer / Options 必须保持已修复机制

共享 renderer 迁移不能破坏：

```text
fieldDef.type='select'
→ options-bearing detection
→ shared Dynamic Options Provider
→ runtime field.options:Array
→ shared field renderer
```

五模块至少验证：

- region；
- representativeOffice；
- country；
- customerName；
- `customer_id` 全链保留；
- Create 打开不报 `f.options is not iterable`；
- Runtime/Options failure 不被包装成 Customer Fetch failure。

Runtime Field View Model 不得再次创建第二份 `type/control/editor` Authority。

---

## 7. Progress 边界

Progress History 继续是唯一持久化事实源：

```text
Progress History
→ latest/current projection
→ battleProgress
```

独立 Progress popup 保留。

本轮 shared form renderer 只处理 `battleProgress` 在 Create/Edit 中被 Contract 投影出来时的特殊 editor binding；不得：

- 把独立 popup 降级为 textarea；
- 恢复 business-table progress text；
- 恢复 double-write / fallback。

---

## 8. 不允许“伪共享”

以下实现全部判定为 FAIL：

### 8.1 一个文件里的五套模板

```text
SharedForm.vue
  if MOX → template A
  if TOB → template B
  if ISP → template C
  ...
```

如果每个分支维护完整表单结构，仍然属于五套 builder。

### 8.2 shared wrapper + module-local body

如果 shared shell 只包 dialog，但 group/field DOM 仍由模块页面独立构建，仍判：

```text
MODULE_LOCAL_FORM_BUILDERS > 0
```

### 8.3 shared helper import but production path bypass

仅 import shared renderer/helper 不算通过；实际 render tree 必须经过它。

### 8.4 测试共享、生产不共享

测试直接调用 shared renderer，而页面生产路径仍调用本地 builder，判 FAIL。

---

## 9. 五模块迁移顺序

如果 MOX 仍有 local builder：

```text
MOX
→ TOB
→ ISP
→ Power
→ Large
```

如果 MOX 已经真正走 shared renderer：

```text
TOB
→ ISP
→ Power
→ Large
```

每迁入一个模块必须立即运行：

```text
该模块 Create/Edit production-path tests
+ MOX regression
+ shared renderer tests
```

不得四模块一次性改完才第一次验证。

---

## 10. Dead Code / Duplicate Authority 清理

所有模块迁入后，全仓企业范围扫描：

```text
module-local full form HTML builders
module-local section/group schema
module-local field renderer switches
module-local validation renderer
module-local options renderer
module-local Create shell
module-local Edit shell
```

确认无 production consumer 后删除。

测试不得继续引用已废弃 builder，使其作为第二 Authority 存活。

---

## 11. 必须新增的架构门禁

目标不仅是本次删除重复，还要防止以后重新长出来。

必须具备静态/架构测试，验证：

```text
FIVE_MODULES_USE_SHARED_FORM_RENDERER=PASS
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

static scan 必须扫描真实 production source，不得只扫描测试目录。

---

## 12. Production-Path Tests

必须从真实页面入口证明每个模块 Create/Edit 进入 shared renderer。

### MOX

- Create/Edit → shared renderer；
- 41 字段双向 Conformance；
- 4 groups exact；
- customer/options；
- Progress behavior；
- no regression。

### TOB

- Create/Edit → shared renderer；
- 34 字段双向 Conformance；
- 3 groups exact。

### ISP

- Create/Edit → shared renderer；
- 25 字段双向 Conformance；
- 3 groups exact。

### Power

- Create/Edit → shared renderer；
- 28 字段双向 Conformance；
- 3 groups exact。

### Large

- Create/Edit → shared renderer；
- 26 字段双向 Conformance；
- 3 groups exact。

测试不得 mock 掉 shared renderer 后只检查 props。

---

## 13. 视觉与交互回归

shared renderer 收敛后必须保持：

- MOX 4-group 视觉间距；
- Non-MOX 3-group 同一视觉机制；
- Create/Edit 样式一致；
- validation presentation 一致；
- select/textarea/number/percent 控件行为一致；
- customer fields Edit readonly；
- submit/cancel/reset lifecycle 不回归。

自动测试验证结构与 class；最终视觉人工验收仍由用户执行。

---

## 14. WRITE_SCOPE

允许修改：

- enterprise shared form shell/group renderer/field renderer；
- shared control/editor registry；
- runtime field model 与 form renderer 的直接接口；
- 五模块 Create/Edit 接入代码；
- 与废弃 local form builder 直接相关的 dead code；
- production-path tests / architecture tests；
- remediation report。

禁止修改：

- 五模块业务字段集合；
- Metric 业务公式；
- Heatmap 业务口径；
- Customer 数据模型；
- Progress persistence model；
- 企业首页；
- Excel V0.2 尚未 Authority 化的字段变化；
- 非企业模块。

---

## 15. 自动验证顺序

至少执行：

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

---

## 16. 实施报告真实性

Implementation Agent 只能声明 `IMPLEMENTED`。

每个 PASS/0 都必须带：

```text
CODE_EVIDENCE=file:function/component
PRODUCTION_PATH_EVIDENCE=test/call chain
STATIC_SCAN_EVIDENCE=query/result
```

禁止再次出现：

```text
REPORT_SHARED_BUT_RUNTIME_LOCAL
REPORT_ZERO_BUT_SCAN_NONZERO
REPORT_TESTED_BUT_NOT_PRODUCTION_PATH
```

---

## 17. 完成门槛

只有全部满足才能声明本轮 Implementation COMPLETE：

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
MOX_REGRESSION=PASS
FULL_TESTS=PASS
BUILD=PASS
```

即使全部通过，也只能声明 `IMPLEMENTED`，不能自行声明 VERIFIED。

下一门禁必须是：

```text
reviews/non-mox-modules-mox-reference-independent-review-v1.md
+
reviews/non-mox-full-independent-review-rerun-v3.md
```

对新的代码 HEAD 做完整全量独立审查，而不是只复核 Form Renderer finding。

---

## 18. 实施产物

创建：

```text
D:\BattleMap\battle-map\docs\enterprise\remediations\five-module-shared-form-renderer-convergence-report-v2.md
```

至少记录：

- BASE_HEAD；
- FINAL_HEAD；
- original review finding ID；
- Five-Module Form Render Inventory；
- MOX local/shared 判定；
- 提炼后的 shared renderer 路径；
- 五模块 final production paths；
- removed local builders；
- static gate results；
- production-path tests；
- full tests/build；
- blockers。

最终短回执：

```text
FIVE-MODULE SHARED FORM RENDERER CONVERGENCE V2
RESULT=COMPLETE/PARTIAL/BLOCKED
BASE_HEAD=
FINAL_HEAD=
ORIGINAL_FINDING_ID=
MOX_LOCAL_FORM_BUILDER_BEFORE=YES/NO
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
MOX_REGRESSION=PASS/FAIL
FULL_TESTS=PASS/FAIL
BUILD=PASS/FAIL
OUT_OF_SCOPE_CHANGES=NO/YES
BLOCKERS=NONE或内容
NEXT=FULL_NON_MOX_INDEPENDENT_REVIEW_RERUN_V3
```
