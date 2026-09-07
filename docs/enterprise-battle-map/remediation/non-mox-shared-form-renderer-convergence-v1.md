# Non-MOX Shared Form Renderer Convergence V1

**状态：CURRENT BLOCKING REMEDIATION**  
**适用模块：TOB、ISP、电力、大企**  
**参考实现：已通过独立审查的 MOX runtime / renderer 机制**  
**代码工作树：`D:\BattleMap\battle-map`**  
**代码分支：`feature/enterprise-battle-map`**

---

## 1. 已确认阻塞事实

最新完整 Non-MOX Independent Review 在修复后的新 HEAD 上仍发现 blocking finding：

```text
module-local form HTML builders = 4x
```

即 TOB / ISP / Power / Large 当前虽然视觉效果相似、部分 runtime/projection 已共享，但 Create/Edit 页面最终 HTML/form builder 仍由各模块独立实现。

因此当前状态不能视为“真正共享 renderer”。

本 finding 的本质不是 CSS 重复，也不是业务字段差异，而是：

```text
shared Contract/runtime
→ 到达 module page 后
→ 又被四套独立 form HTML builder 重新解释
```

这会重新引入第二份业务结构 Authority，使后续 group、field order、control/editor、validation、options、readonly、spacing、error presentation 等再次漂移。

因此该 finding 属于：

```text
BLOCKING_IMPLEMENTATION_NONCONFORMANCE
+ ARCHITECTURAL_DUPLICATION_IN_RUNTIME_PATH
```

---

## 2. 目标状态

最终 Create/Edit 生产链必须收敛为：

```text
Module Field Contract
→ shared Table/Create/Edit Projection
→ shared Runtime Field View Model
→ shared Dynamic Options / Editor Registry
→ shared Form Shell
→ shared Group Renderer
→ shared Field Renderer
→ actual Vue render tree
```

TOB / ISP / Power / Large 不得各自维护一份完整 form HTML builder。

模块业务差异只能来自：

- 自己的 Field Contract；
- Contract 中的 `group` / `order` / `type` / `controlId` / `editorId` / `formatterId` / validation；
- 已登记在 shared editor/control registry 中的特殊控件；
- 必要且被明确证明为业务差异的最小 slot / hook。

禁止通过整段 module-local template、独立 section builder、独立 field switch、独立 validation DOM 或独立 options renderer 表达模块差异。

---

## 3. Authority 与边界

本轮必须读取并遵循：

1. `enterprise-contract-architecture-v5.md`
2. `architecture/enterprise-runtime-field-options-contract-v1.md`
3. `mox-canonical-authority-v6.md`
4. `remediation/non-mox-modules-mox-reference-alignment-v1.md`
5. `reviews/non-mox-modules-mox-reference-independent-review-v1.md`
6. `reviews/non-mox-full-independent-review-rerun-v3.md`
7. 本地最新 `docs/enterprise/reviews/non-mox-modules-mox-reference-independent-review.md`
8. TOB / ISP / Power / Large 当前 Canonical Authority

本轮只解决共享 form renderer blocker及其直接测试/死代码清理。

不得：

- 修改模块业务字段集合；
- 根据尚未 Authority 化的 Excel V0.2 改字段；
- 修改 Metric 业务公式；
- 修改 Heatmap 业务口径；
- 修改 Customer / Progress 数据模型；
- 重写 MOX 41字段；
- 建立新的 module-specific form framework。

---

## 4. 第一步：恢复真实 4x module-local builder

修改前必须从最新 Independent Review report 恢复该 finding 的完整证据。

记录：

```text
FINDING_ID
TOB_BUILDER_FILE / FUNCTION / TEMPLATE_REGION
ISP_BUILDER_FILE / FUNCTION / TEMPLATE_REGION
POWER_BUILDER_FILE / FUNCTION / TEMPLATE_REGION
LARGE_BUILDER_FILE / FUNCTION / TEMPLATE_REGION
CURRENT_SHARED_RENDERER_FILE / COMPONENT
MOX_ACTUAL_RENDER_PATH
```

必须画出当前真实调用链：

```text
TOB Contract → ... → TOB local builder → DOM
ISP Contract → ... → ISP local builder → DOM
Power Contract → ... → Power local builder → DOM
Large Contract → ... → Large local builder → DOM
MOX Contract → ... → verified shared renderer → DOM
```

不得仅通过文件名推断；必须追 Production path。

---

## 5. 共享 Renderer 收敛原则

### 5.1 只有一个 Form Shell

Create / Edit modal/dialog 的以下职责必须共享：

- dialog shell；
- loading/error/empty state；
- submit/cancel lifecycle；
- form-level validation presentation；
- group container；
- group spacing/title；
- field iteration；
- field error presentation。

模块页面不得复制这些 DOM 结构。

### 5.2 只有一个 Group Renderer

Group 只能来自：

```text
field.group
```

shared renderer 负责：

```text
group order
→ group wrapper
→ group title
→ group fields
```

TOB / ISP / Power / Large 正确 group 都是：

```text
客户信息
业务格局
作战情况
```

不得在 module page 定义 `sections/groups` 常量或 template 分支重新定义业务归属。

### 5.3 只有一个 Field Renderer / Editor Dispatch

字段控件必须通过 shared registry / renderer dispatch：

```text
fieldDef.type / controlId / editorId
→ shared renderer/editor registry
```

不得各模块自己维护：

```text
if select ...
if textarea ...
if percent ...
if number ...
```

整套独立 switch / template。

如果存在特殊业务控件，必须用共享 registry 的稳定 ID 扩展，不得复制 form builder。

### 5.4 Create 与 Edit 不能各有一套 HTML Authority

Create/Edit 可以通过 projection、readonly、editable、editorId 等不同，但最终都必须落到同一个 shared form renderer。

目标：

```text
Create projection → shared renderer
Edit projection   → shared renderer
```

而不是：

```text
Create module template A
Edit module template B
```

---

## 6. 允许存在的模块差异

以下差异是合法的，但必须由 Contract/registry/adapter 表达：

- TOB 34字段；
- ISP 25字段；
- Power 28字段；
- Large 26字段；
- 各模块业务格局字段不同；
- ISP/Power/Large 有行业，TOB没有；
- 模块枚举不同；
- 特殊 formatter/parser/editor；
- Heatmap business contract 不同；
- 页面专项文案不同。

这些差异不能成为保留整套 module-local form HTML builder 的理由。

---

## 7. 特殊控件与 Progress

Progress 独立弹窗继续保留。

shared form renderer 如遇 `battleProgress`，必须遵循当前 canonical behavior/editor 规则，不得恢复普通 textarea 或业务表 text 双写。

如果 Progress 行操作不属于 Create/Edit form 本体，则保持当前 verified 行操作/弹窗机制；本轮不得把它硬塞进 shared form shell。

---

## 8. Customer / Dynamic Options 回归

共享 renderer 收敛后必须保证之前修复的真实链不回归：

```text
fieldDef.type='select'
→ shared runtime options-bearing detection
→ dynamic options provider
→ runtime field.options:Array
→ shared field renderer
```

必须重新验证：

- region；
- representativeOffice；
- country；
- customerName；
- customer_id 保留；
- Create dialog 可打开；
- Runtime/Options failure 不被包装成 Customer fetch failure。

---

## 9. 必须删除的重复 Authority

完成共享 renderer 接入后，对以下内容做引用扫描：

```text
module-local full form HTML builders
module-local section/group arrays
module-local field renderer switches
module-local duplicated validation DOM
module-local duplicated options DOM
module-local duplicated Create/Edit shell
```

确认无 Production consumer 后删除。

目标：

```text
MODULE_LOCAL_FORM_HTML_BUILDERS=0
MODULE_LOCAL_SECTION_SCHEMAS=0
DUPLICATE_FIELD_RENDERERS=0
DUPLICATE_FORM_SHELLS=0
DUPLICATE_VALIDATION_RENDERERS=0
```

不得留下“已不使用但测试还引用”的旧 builder 作为第二 Authority。

---

## 10. Production-path Conformance Tests

本轮测试必须证明的不是组件文件存在，而是真实页面走 shared renderer。

每模块分别验证：

```text
route/page
→ Create action
→ module projection
→ shared runtime field model
→ shared form renderer
→ rendered groups/fields
```

以及 Edit 同链。

至少断言：

### TOB
- Create/Edit 实际 shared renderer；
- 3 groups exact；
- 34字段双向完整性。

### ISP
- Create/Edit 实际 shared renderer；
- 3 groups exact；
- 25字段双向完整性。

### Power
- Create/Edit 实际 shared renderer；
- 3 groups exact；
- 28字段双向完整性。

### Large
- Create/Edit 实际 shared renderer；
- 3 groups exact；
- 26字段双向完整性。

同时验证 MOX 仍保持4-group并走相同共享 renderer mechanism。

测试不得 mock 掉 shared renderer 本体后只验证传参。

---

## 11. 静态门禁

必须新增或强化静态扫描/架构测试，使未来不能重新长出4套 form builder。

至少检查：

```text
MODULE_LOCAL_FORM_HTML_BUILDERS=0
MODULE_LOCAL_SECTION_SCHEMAS=0
DUPLICATE_SECTION_RENDER_PATHS=0
DUPLICATE_FIELD_RENDERER_SWITCHES=0
```

如果采用 AST/import graph/static pattern 方式，必须针对真实 Production source，不得只扫描测试目录。

---

## 12. 实施报告真实性

本轮 Implementation Agent 只能声明 `IMPLEMENTED`。

报告每个 PASS/0 都必须给出：

```text
CODE_EVIDENCE=file:function/component
PRODUCTION_PATH_EVIDENCE=test/call-chain
STATIC_SCAN_EVIDENCE=query/result
```

不得再次出现：

```text
REPORT_SHARED_BUT_RUNTIME_LOCAL
REPORT_ZERO_BUT_SCAN_NONZERO
```

---

## 13. 自动验证

完成后至少执行：

1. shared form renderer tests；
2. TOB Create/Edit production-path tests；
3. ISP Create/Edit production-path tests；
4. Power Create/Edit production-path tests；
5. Large Create/Edit production-path tests；
6. MOX Create/Edit regression；
7. Runtime Field/Options tests；
8. Customer regression；
9. Progress regression；
10. Heatmap canonical regression；
11. Metric regression；
12. API/database regression；
13. enterprise suite；
14. full Vitest；
15. build；
16. lint/typecheck（如已有）。

---

## 14. 完成条件

Implementation 只有以下全部满足才能声明 COMPLETE：

```text
MODULE_LOCAL_FORM_HTML_BUILDERS=0
MODULE_LOCAL_SECTION_SCHEMAS=0
DUPLICATE_SECTION_RENDER_PATHS=0
DUPLICATE_FIELD_RENDERERS=0
DUPLICATE_FORM_SHELLS=0
TOB_SHARED_FORM_RENDERER=PASS
ISP_SHARED_FORM_RENDERER=PASS
POWER_SHARED_FORM_RENDERER=PASS
LARGE_SHARED_FORM_RENDERER=PASS
MOX_REGRESSION=PASS
FULL_TESTS=PASS
BUILD=PASS
```

但即使全部通过，也只能声明 IMPLEMENTED。

下一门禁仍然是：

> 对修复后的新 HEAD 完整重新执行 `reviews/non-mox-modules-mox-reference-independent-review-v1.md` + `reviews/non-mox-full-independent-review-rerun-v3.md`。

不得只复核本 finding。

---

## 15. 实施产物

创建：

```text
D:\BattleMap\battle-map\docs\enterprise\remediations\non-mox-shared-form-renderer-convergence-report.md
```

报告至少包含：

- BASE_HEAD；
- FINAL_HEAD；
- original finding ID；
- 4x local builder 文件/函数；
- MOX/shared verified path；
- final shared renderer path；
- removed/dead builder list；
- Production-path tests；
- static scan results；
- MOX regression；
- full tests/build；
- blockers。

最终短回执：

```text
NON-MOX SHARED FORM RENDERER CONVERGENCE
RESULT=COMPLETE/PARTIAL/BLOCKED
BASE_HEAD=
FINAL_HEAD=
ORIGINAL_FINDING_ID=
MODULE_LOCAL_FORM_HTML_BUILDERS=
MODULE_LOCAL_SECTION_SCHEMAS=
DUPLICATE_SECTION_RENDER_PATHS=
DUPLICATE_FIELD_RENDERERS=
DUPLICATE_FORM_SHELLS=
TOB_SHARED_FORM_RENDERER=PASS/FAIL
ISP_SHARED_FORM_RENDERER=PASS/FAIL
POWER_SHARED_FORM_RENDERER=PASS/FAIL
LARGE_SHARED_FORM_RENDERER=PASS/FAIL
RUNTIME_FIELD_OPTIONS=PASS/FAIL
CUSTOMER_REGRESSION=PASS/FAIL
PROGRESS_REGRESSION=PASS/FAIL
HEATMAP_REGRESSION=PASS/FAIL
METRIC_REGRESSION=PASS/FAIL
MOX_REGRESSION=PASS/FAIL
FULL_TESTS=PASS/FAIL
BUILD=PASS/FAIL
OUT_OF_SCOPE_CHANGES=NO/YES
BLOCKERS=NONE或内容
NEXT=FULL_NON_MOX_INDEPENDENT_REVIEW_RERUN
```
