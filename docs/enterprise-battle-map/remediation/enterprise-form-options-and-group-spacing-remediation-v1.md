# 企业作战地图：表单 Options 运行时与 Group 间距修复 V1

**状态：CURRENT REMEDIATION AUTHORITY**  
**代码工作树：`D:\BattleMap\battle-map`**  
**代码分支：`feature/enterprise-battle-map`**  
**适用模块：TOB、ISP、电力、大企；MOX 仅做客户回归与 group 样式修复**  
**前置状态：MOX End-to-End Canonical Independent Review 已 PASS**

---

## 1. 本轮人工验收事实

用户在独立审查 PASS 后继续人工验收，确认三个事实：

1. 除 MOX 外，TOB / ISP / 电力 / 大企打开新增仍报客户数据失败，控制台真实异常为：

```text
f.options is not iterable
```

2. MOX 新增中的“无线格局”“微波格局”与上一顶层 group 之间没有足够垂直间距，视觉上粘连；4-group 结构本身已经正确。

3. 用户再次确认“进展历史”弹窗与表格中的“作战进展”的关系。本轮不重新设计 Progress：现行 Authority 保持——Progress History 是唯一持久化事实源，`battleProgress` 是 latest/current canonical projection；独立进展弹窗继续操作 History。

因此本轮只有两个实施缺口：

```text
A. TOB/ISP/Power/Large 表单动态 options runtime 异常
B. 共享 Create/Edit group 视觉间距不足
```

Progress 仅做回归确认，不做新的 Schema/API/模型改造。

---

## 2. Authority

按以下顺序执行：

1. 本文件；
2. `enterprise-contract-architecture-v5.md`；
3. 各模块当前 Canonical Authority；
4. `enterprise-customer-data-fetch-unification-v2.md`；
5. 当前已经 PASS 的 MOX End-to-End Canonical Review 结果；
6. 真实运行代码和调用栈。

不得使用旧 Customer remediation V1、旧 3-section 规则或任何 legacy field alias 作为修复依据。

---

## 3. 问题 A：`f.options is not iterable`

### 3.1 当前判断

本异常发生在前端运行时对象处理阶段，错误文本表明某段代码正在将 `f.options` 当作 iterable 使用，例如：

```js
[...f.options]
```

或：

```js
for (const option of f.options) { ... }
```

但至少一个实际 field runtime object 的 `options` 为 `undefined`、`null`、对象或其他非 iterable 值。

当前 UI 仍提示“获取客户数据失败”，不等于客户 API 本身失败。必须首先通过真实调用栈证明：

```text
customer request 是否成功
→ response 是否带 customer_id
→ normalization 是否成功
→ 哪个 field/options enrichment 开始执行
→ 哪个具体 field 触发 f.options is not iterable
→ 外层哪个 catch 将其错误包装成“获取客户数据失败”
```

不得因为文案相同就再次修改 customer SQL。

### 3.2 必须先定位具体 field

修复前必须记录：

- 触发异常的模块；
- Create 页面/组件；
- 具体函数；
- `f.key`；
- `f.controlId` / `editorId`；
- `typeof f.options`；
- `f.options` 实际值；
- 当前代码为什么认为该字段一定拥有 iterable options；
- 此 options 来源是 Contract 静态 option-set、Customer 动态候选、Region/Office 级联，还是其他 runtime enrichment。

四个失败模块分别检查，不允许只验证一个模块后假设另外三个完全相同。

### 3.3 Customer API 必须先被证明成功或失败

每个失败模块必须区分：

```text
CUSTOMER_FETCH_FAILED
FORM_OPTIONS_RUNTIME_FAILED
```

如果 HTTP/API/DB 客户查询已经成功且候选包含真实 `customer_id`，则本轮禁止再次修改 SQL/customer API 业务契约。

如果实际又发现 customer API 自身回归，则必须记录为独立 finding；不得把 API 与 options runtime 混在一个修复里。

---

## 4. Options 的正确模型

### 4.1 Field Contract 静态数据与 Runtime 动态数据分离

字段的静态 Contract 可以描述：

- control/editor 类型；
- option-set identity；
- validation；
- 是否需要动态 options provider。

但动态客户、地区部、代表处等候选不应修改 Canonical Field Contract 成为可变全局状态。

目标应为类似：

```text
Field Contract
→ Runtime Projection
→ Runtime Field View Model
→ options provider / dynamic options
→ Renderer
```

Contract 保持静态、稳定。

### 4.2 Renderer 只能迭代明确为 options-bearing 的字段

禁止通用逻辑对所有字段无条件做：

```js
[...field.options]
```

正确实现必须根据现有 control/editor 契约判断字段是否需要 options。

如果一个 select 字段在合法状态下允许暂时没有候选，其 runtime options 应明确为：

```js
[]
```

而不是 `undefined`。

但不得通过在所有 field 上统一塞 `options: []` 来掩盖模型错误。

### 4.3 不允许危险兜底

禁止以以下方式作为最终修复：

```js
[...(f.options || [])]
```

```js
Array.isArray(f.options) ? f.options : []
```

如果这种代码只是 renderer 最外层防御性保护，可以存在，但前提是：

1. upstream runtime model 已被修正；
2. 非 options-bearing field 不应走 options enrichment；
3. 需要 options 的字段在 runtime model 中保证 array contract；
4. 测试能在 upstream 错误时失败，而不是静默显示空下拉。

客户查询失败和“合法无候选”必须可区分。

---

## 5. 四模块客户表单 Runtime 统一要求

TOB / ISP / 电力 / 大企应共享同一客户数据获取能力，但 UI projection 有模块差异。

模块客户字段：

- TOB：地区部、代表处、国家、客户ID、客户名称；
- ISP / 电力 / 大企：地区部、代表处、国家、客户ID、客户名称、行业。

本轮必须验证：

```text
shared customer query
→ canonical customer candidates with customer_id
→ module runtime field model
→ dynamic options
→ renderer
```

不得为四个模块分别复制一套相同 customer options builder。

如果当前存在一个共享 options/enrichment helper，应修共享层并由四模块消费。

如果四模块实际并非同一根因，必须分别修真实原因，不允许为了“统一”强行抽象。

---

## 6. 错误边界修复

当前“获取客户数据失败”不能继续包住与网络/API无关的 runtime TypeError。

目标至少区分：

```text
customer fetch / API error
customer response contract error
form runtime projection error
options provider/enrichment error
```

用户 UI 可保持简洁，但开发日志/测试必须能够识别真实 error stage。

禁止：

- 大范围 `try/catch` 把所有 Create 初始化错误都改写成“获取客户数据失败”；
- catch 后返回空 customer list 继续渲染；
- 吞掉 TypeError。

---

## 7. Options Runtime Conformance Gate

增加自动验证：

### 7.1 Field-level

对真实 Create renderer 输入验证：

- 所有需要 options 的 control/editor：`options` 最终为 Array；
- 非 options-bearing field 不依赖 `options`；
- dynamic customer options 保留 `customer_id`；
- region/office/customer 级联后 options 仍是 array；
- empty result 是 `[]`，但 API failure 不是 `[]`。

### 7.2 模块级

TOB / ISP / 电力 / 大企分别验证：

- 打开 Create 不抛 `f.options is not iterable`；
- Customer query 成功；
- runtime form model 成功；
- 地区部/代表处/客户候选可生成；
- customer candidate 保留真实 `customer_id`；
- 模块特有字段仍按自己的 Contract 渲染；
- create payload 最终保存正确 `customer_id`。

### 7.3 MOX 回归

MOX 原有 Customer Create 流程继续 PASS，不得因共享 helper 修复而回归。

---

## 8. 问题 B：共享 Group 视觉间距

### 8.1 当前事实

MOX 4-group 结构及 renderer 链已经通过独立审查，但用户人工验收发现：

```text
客户信息
无线格局
微波格局
作战情况
```

其中无线格局、微波格局等新 group 开始位置与上一组末尾缺乏明显垂直间距。

这是视觉层级 nonconformance，不是 Field Contract/group 结构错误。

### 8.2 修复位置

优先修共享 Create/Edit group wrapper / renderer CSS。

禁止：

- 在 Contract 中加入空字段；
- 插 `<br>`；
- 给 MOX 41字段之间手工插 spacer；
- 为 MOX Create 和 Edit 分别复制 CSS；
- 修改 group 业务定义。

目标：

```text
Group Wrapper
├─ group title
├─ title/content separation
├─ fields
└─ stable next-group spacing
```

### 8.3 视觉要求

所有非首 group 必须具有稳定且明显的顶部空间。

推荐基于当前 UI scale 使用约 `20–24px` 的组间视觉间距，但 Agent 应优先复用现有 spacing token / CSS variable；不得为了符合数字破坏现有设计体系。

同时要求：

- group title 字重/字号明显高于 field label；
- 与上一组最后一行不粘连；
- Create/Edit 一致；
- 分隔线/容器边界如已存在必须保持协调；
- TOB/ISP/电力/大企共享 renderer 的 3-group 页面不得出现样式回归。

结构/class 可自动测试，最终视觉仍由用户人工验收。

---

## 9. Progress 回归边界

本轮不修改 Progress 架构。

必须保持：

```text
Progress History table = 唯一持久化事实源
battleProgress = latest/current canonical projection
独立进展弹窗 = Progress History 的新增/编辑入口
```

这意味着“作战进展”是同一个业务概念，但不是业务表中重新维护一个可写 text 字段。

本轮仅执行回归：

- 独立进展弹窗仍能打开；
- 进展读写仍走 History；
- 不重新引入 business-text 双写或 fallback。

除非发现本轮修改造成回归，否则禁止修改 Progress API、Schema、Migration。

---

## 10. WRITE_SCOPE

允许修改：

- 企业共享 Create/Edit runtime field view-model / projection / options enrichment；
- shared customer options/provider 接入；
- TOB/ISP/电力/大企直接相关 Create 初始化；
- Create 初始化错误边界；
- shared group renderer / shared Create/Edit group CSS；
- 相关测试；
- remediation report。

仅在真实证据证明回归时允许修改：

- shared customer client/service/API normalization。

禁止修改：

- 各模块 Field Contract 字段集合；
- canonical key；
- Metric 公式；
- Heatmap 业务规则；
- Progress Schema/API/History 模型；
- V34–V39 Migration；
- 企业首页；
- 非企业模块；
- legacy compatibility。

---

## 11. 自动验证顺序

必须按以下顺序执行：

1. shared runtime/options unit tests；
2. TOB Create tests；
3. ISP Create tests；
4. Power Create tests；
5. Large Enterprise Create tests；
6. MOX Create customer regression；
7. shared group renderer structural tests；
8. MOX Create/Edit 4-group regression；
9. other module 3-group regression；
10. Progress popup/history regression；
11. enterprise suite；
12. full Vitest；
13. build；
14. lint/typecheck（如已有）。

不得通过删除断言、伪造空 options、恢复旧字段兼容来通过。

---

## 12. 完成标准

全部满足才可 COMPLETE：

1. TOB/ISP/电力/大企 Create 不再出现 `f.options is not iterable`；
2. 真实根因字段和函数已记录；
3. customer API 是否成功已与 form runtime error 明确分离；
4. options-bearing 字段拥有明确 array contract；
5. 非 options-bearing 字段不会进入错误的 options 迭代链；
6. customer candidate `customer_id` 不丢失；
7. 四模块客户选择和 create payload 成功；
8. MOX customer 无回归；
9. MOX Create/Edit 4-group 有明显稳定组间距；
10. 其他四模块 3-group 视觉无回归；
11. Progress popup/history 单事实源无回归；
12. full Vitest 和 build PASS；
13. 无 out-of-scope 修改。

---

## 13. 实施报告

创建：

```text
docs/enterprise/remediations/enterprise-form-options-and-group-spacing-report.md
```

必须记录：

- BASE_HEAD；
- FINAL_HEAD；
- `f.options` 真实 stack/function/field key；
- Customer API 在异常发生前是否已成功；
- root cause；
- 修复前/后 runtime field model；
- 是否修改 shared helper；
- TOB/ISP/Power/Large 结果；
- MOX customer regression；
- group spacing 实际 CSS/token/class；
- MOX 4-group regression；
- other module 3-group regression；
- Progress regression；
- tests/build；
- blockers。

最终短回执：

```text
ENTERPRISE FORM OPTIONS + GROUP SPACING REMEDIATION
RESULT=COMPLETE/PARTIAL/BLOCKED
BASE_HEAD=
FINAL_HEAD=
F_OPTIONS_ROOT_CAUSE=
FAILING_FIELD_KEYS=
CUSTOMER_API_BEFORE_OPTIONS_ERROR=PASS/FAIL/NOT_PROVEN
TOB_CREATE=PASS/FAIL
ISP_CREATE=PASS/FAIL
POWER_CREATE=PASS/FAIL
LARGE_CREATE=PASS/FAIL
MOX_CUSTOMER_REGRESSION=PASS/FAIL
OPTIONS_ARRAY_CONTRACT=PASS/FAIL
ERROR_BOUNDARY=PASS/FAIL
MOX_GROUP_SPACING=IMPLEMENTED/FAIL
OTHER_MODULE_GROUP_REGRESSION=PASS/FAIL
PROGRESS_REGRESSION=PASS/FAIL
FULL_TESTS=PASS/FAIL
BUILD=PASS/FAIL
OUT_OF_SCOPE_CHANGES=NO/YES
BLOCKERS=NONE或内容
NEXT=USER_MANUAL_ACCEPTANCE/REMEDIATION
```
