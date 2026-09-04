# 企业作战地图：Form Options 根因闭环修复 V2

**状态：CURRENT BLOCKING REMEDIATION AUTHORITY**  
**取代：`enterprise-form-options-and-group-spacing-remediation-v1.md` 中关于 `f.options is not iterable` 的修复策略**  
**代码工作树：`D:\BattleMap\battle-map`**  
**代码分支：`feature/enterprise-battle-map`**  
**适用模块：TOB、ISP、电力、大企；MOX 作为对照回归**

---

## 1. 当前事实

上一轮 remediation 已声明完成，但用户人工验收再次确认：

```text
获取客户数据失败：f.options is not iterable
```

仍然存在于 TOB / ISP / 电力 / 大企新增流程。

因此上一轮关于该问题的结论作废，当前状态：

```text
ROOT_CAUSE_NOT_CLOSED
MANUAL_ACCEPTANCE=FAIL
```

当前不得再假设 SQL、Customer API、Field Contract、options provider 中任何一层已经正确；必须重新从真实运行时证据定位。

---

## 2. 本轮目标

本轮只解决一个 blocking defect：

> 找到并修复 `f.options is not iterable` 的唯一真实根因，使 TOB / ISP / 电力 / 大企新增页面在真实运行时不再报错。

本轮不修改 MOX 41 字段，不修改 Metric、Heatmap、Progress、企业首页，不修改业务字段含义。

---

## 3. 禁止猜测和禁止“防御性兜底修复”

在获得完整证据前，禁止直接提交以下类型修复作为根因修复：

```js
f.options || []
Array.isArray(f.options) ? f.options : []
[...(f.options ?? [])]
try/catch 后忽略异常
```

这些代码只有在明确的 Runtime Field Contract 设计中属于正确语义时才允许存在；不得用于隐藏未定义、错误类型或错误字段进入 options path 的事实。

同样禁止：

- 再次盲改 Customer SQL；
- 为四个模块分别复制 patch；
- 把错误改成空候选后让页面“能打开”；
- 将所有异常继续包装成“获取客户数据失败”；
- 删除失败测试或降低断言。

---

## 4. 修复前必须完成的根因证据

代码修改前必须得到并写入 report 的证据表。

### 4.1 精确异常位置

必须拿到真实 stack trace，并记录：

```text
ERROR_FUNCTION=
ERROR_FILE=
ERROR_LINE=
CALLER_FUNCTION=
MODULE=
```

如果浏览器错误被 catch 包装，允许临时增加诊断日志或在测试中直接调用真实函数，但最终诊断代码不得残留无必要噪声。

### 4.2 精确 `f`

在抛错瞬间记录：

```text
FIELD_KEY=
FIELD_LABEL=
CONTROL_ID=
EDITOR_ID=
FIELD_GROUP=
F_OPTIONS_VALUE=
F_OPTIONS_TYPE=
FIELD_SOURCE=
```

必须回答：

- `f` 是哪个字段；
- 为什么该字段进入 options 处理；
- 该字段按 Contract 是否应该有 options；
- `f.options` 正常来源应是什么；
- 当前是谁把它变成 undefined/null/object/function/其他非 iterable 值。

### 4.3 Customer 链事实

在同一次失败中必须证明：

```text
CUSTOMER_REQUEST_STARTED=YES/NO
CUSTOMER_HTTP_STATUS=
CUSTOMER_RESPONSE_HAS_ROWS=YES/NO
CUSTOMER_RESPONSE_HAS_CUSTOMER_ID=YES/NO
NORMALIZED_CUSTOMER_COUNT=
```

如果 Customer API 已成功且 normalized customer 正常，则本轮不得再修改 SQL/Customer API。

如果 API 在 options error 之前根本没成功，则必须报告真实先后顺序，不得把两个异常混为一谈。

### 4.4 四模块比较

必须分别记录 TOB / ISP / 电力 / 大企：

```text
same failing function?
same FIELD_KEY?
same F_OPTIONS_TYPE?
same runtime adapter?
```

如果四模块同根因，必须修共享路径；如果不同，必须分别证明，不能默认统一。

### 4.5 与 MOX 的差异

MOX 当前新增可正常进入客户链，必须比较：

```text
MOX runtime field projection
vs
TOB/ISP/Power/Large runtime field projection

MOX options enrichment
vs
other modules options enrichment
```

找出为什么 MOX 不触发相同异常。

---

## 5. 需要调查的 Runtime 链

至少恢复：

```text
Module Field Contract
→ getCreateFields()/shared projection
→ runtime field clone/view model
→ dynamic options enrichment/provider
→ group model
→ Create renderer
```

以及：

```text
Create dialog init
→ customer fetch
→ customer normalization
→ region/office/country/customer option derivation
→ field options assignment
```

重点搜索并列出所有对 `.options` 的：

- spread；
- for-of；
- concat；
- map/filter；
- mutation；
- assignment；
- destructuring。

必须区分静态 enum options 与动态 customer-related options。

---

## 6. 正确目标 Runtime Contract

动态 options 不属于静态 Field Contract 中的客户数据本身，但 runtime field model 必须有确定语义。

对 options-bearing control：

```text
runtimeOptions = Array
```

合法无候选时：

```text
[]
```

但 API/query/error 失败必须以错误状态表达，不能用 `[]` 冒充成功。

对非 options-bearing control：

- 不应进入需要迭代 options 的 renderer/provider 分支；
- 不要求人为给每个 field 填 `options: []` 以掩盖分支判定错误。

静态枚举和动态候选必须有明确来源，不允许同一 `options` 属性在不同阶段随机出现不同类型。

---

## 7. 错误边界必须拆分

最终用户/日志错误至少可区分：

```text
CUSTOMER_FETCH_FAILED
CUSTOMER_RESPONSE_CONTRACT_FAILED
OPTIONS_PROVIDER_FAILED
FORM_RUNTIME_FAILED
```

禁止 `options` runtime TypeError 最终继续显示为“获取客户数据失败”。

用户提示可以友好，但诊断信息必须保留真实错误类型和 root cause。

---

## 8. 测试必须复现真实失败

修复前先新增一个最小失败测试，要求在当前 broken HEAD 上能稳定重现 `f.options is not iterable` 或等价真实错误。

测试不得人工构造一个与生产链无关的 helper。

至少覆盖：

1. TOB Create 真实初始化；
2. ISP Create 真实初始化；
3. Power Create 真实初始化；
4. Large Enterprise Create 真实初始化；
5. MOX 对照；
6. Customer API 成功 + options runtime 成功；
7. Customer API 失败时错误分类正确；
8. 合法空 options 为 `[]`；
9. 非 options-bearing field 不进入 options iterable path；
10. customer candidate 仍保留 `customer_id`。

修复后同一 reproduction test 必须 PASS。

---

## 9. WRITE_SCOPE

允许修改：

- 企业共享 runtime projection / runtime field model；
- dynamic options provider/enrichment；
- Create form renderer 与 options control 判定；
- TOB/ISP/Power/Large Create 接入；
- Customer client/normalization 仅在证据证明根因确实位于此处时；
- 错误边界与诊断；
- 直接相关测试；
- remediation report。

禁止修改：

- MOX 41 字段；
- 五模块 Canonical 字段集合；
- Metric；
- Heatmap；
- Progress persistence；
- 数据库 Migration，除非根因证据明确证明本问题由 schema 缺失导致；
- 企业首页；
- 非企业模块。

---

## 10. 完成标准

只有全部满足才可标记 COMPLETE：

1. 有真实 stack trace 和具体 failing field；
2. `f.options` 实际类型和错误来源被证明；
3. Customer API 是否成功被独立证明；
4. 修复针对真正根因，不是 fallback；
5. 四模块真实 Create 页面不再出现该异常；
6. MOX 无回归；
7. options-bearing / non-options-bearing runtime contract 清晰；
8. 错误边界不再把 runtime error 包装成 customer fetch error；
9. reproduction test 先 FAIL 后 PASS；
10. enterprise suite / full Vitest / build 通过；
11. 用户人工验收通过前不得宣称 VERIFIED。

---

## 11. 实施报告

创建：

```text
docs/enterprise/remediations/enterprise-form-options-root-cause-report-v2.md
```

必须包含：

```text
BASE_HEAD=
FINAL_HEAD=
ERROR_FUNCTION=
ERROR_FILE_LINE=
FIELD_KEY=
FIELD_LABEL=
F_OPTIONS_VALUE=
F_OPTIONS_TYPE=
OPTIONS_EXPECTED_SOURCE=
ACTUAL_BAD_SOURCE=
CUSTOMER_HTTP_STATUS=
CUSTOMER_ID_PRESENT=
MOX_DIFFERENCE=
ROOT_CAUSE=
FIX=
REPRO_TEST_BEFORE=FAIL
REPRO_TEST_AFTER=PASS
TOB=PASS/FAIL
ISP=PASS/FAIL
POWER=PASS/FAIL
LARGE=PASS/FAIL
MOX=PASS/FAIL
ERROR_BOUNDARY=PASS/FAIL
FULL_TESTS=PASS/FAIL
BUILD=PASS/FAIL
BLOCKERS=
```

最终短回执：

```text
ENTERPRISE FORM OPTIONS ROOT-CAUSE REMEDIATION V2
RESULT=COMPLETE/PARTIAL/BLOCKED
ROOT_CAUSE=
ERROR_FUNCTION=
FIELD_KEY=
F_OPTIONS_TYPE=
CUSTOMER_API=PASS/FAIL/NOT_REACHED
TOB=PASS/FAIL
ISP=PASS/FAIL
POWER=PASS/FAIL
LARGE=PASS/FAIL
MOX_REGRESSION=PASS/FAIL
REPRO_TEST=PASS/FAIL
ERROR_BOUNDARY=PASS/FAIL
FULL_TESTS=PASS/FAIL
BUILD=PASS/FAIL
BLOCKERS=NONE或内容
NEXT=USER_MANUAL_ACCEPTANCE
```
