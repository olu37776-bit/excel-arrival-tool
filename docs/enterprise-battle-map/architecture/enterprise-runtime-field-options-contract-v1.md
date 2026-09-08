# 企业作战地图：Runtime Field Options Contract V1

**状态：CURRENT ARCHITECTURE ADDENDUM**  
**适用：MOX、TOB、ISP、电力、大企 Create/Edit Runtime**  
**上位 Authority：`enterprise-contract-architecture-v5.md`**

---

## 1. 背景与已确认根因

人工验收曾在 TOB / ISP / 电力 / 大企新增页面稳定出现：

```text
获取客户数据失败：f.options is not iterable
```

最终根因已通过真实调用链定位：

- Customer API 已成功；
- 客户数据链不是本次错误根因；
- 受影响字段包括：`region`、`representativeOffice`、`country`、`customerName`；
- Field Contract / `fieldDef` 中这些字段的权威类型为：

```text
fieldDef.type = 'select'
```

- 运行时代码错误检查：

```text
f.type
```

- 但当前 Runtime Field View Model `f.type` 为 `undefined`；
- 因此 select 字段没有进入正确的 options 初始化 / enrichment 路径；
- 最终 `f.options` 保持 `undefined`；
- renderer 后续将 `f.options` 当 iterable 使用，触发 TypeError；
- 外层错误边界又把该 Runtime 错误包装成“获取客户数据失败”。

根因分类：

```text
IMPLEMENTATION_NONCONFORMANCE
+
TEST_GAP
+
RUNTIME_CONSUMER_CONTRACT_GAP
```

这不是 Customer SQL/API 的新故障，也不是需要新增另一套字段 Schema。

---

## 2. Authority 原则

字段静态业务定义的唯一 Authority 是 Module Field Contract / `fieldDef`。

Runtime Field View Model 只是运行时投影，不得成为第二份字段定义 Authority。

因此以下静态属性必须由 Field Contract / `fieldDef` 决定：

- `type`；
- `controlId`；
- `editorId`；
- `validation`；
- `optionSetId`；
- `group`；
- `order`；
- create/edit/table visibility/editability。

Runtime View Model 可以携带这些属性的投影值，但如果携带，必须来自同一 Contract Projection，并由 Conformance Gate 验证一致；不得由页面、composable、options helper 再维护一份独立静态定义。

---

## 3. Options-bearing Field 判定

是否需要 options，必须由权威字段定义判断，而不是依赖一个可能未投影的临时字段属性。

允许的判定来源：

```text
fieldDef.type
fieldDef.controlId
fieldDef.editorId
```

具体使用哪个属性，应服从当前 Field Contract 约定；但只能有一套确定规则。

禁止：

```text
Runtime f.type 与 fieldDef.type 分别承担同一业务判断
```

尤其禁止在 `f.type` 未由唯一 Projection 明确保证存在时，以它判断 select/options 行为。

---

## 4. Runtime Options 生命周期

正确链：

```text
Field Contract / fieldDef
→ Runtime Projection
→ 判断 options-bearing control
→ Dynamic Options Provider / static optionSet
→ Runtime Field View Model.options
→ Renderer
```

对于 options-bearing 字段，进入 renderer 前必须满足：

```text
Array.isArray(runtimeField.options) === true
```

合法无候选：

```text
options = []
```

但 `[]` 只能表示“查询成功且当前没有候选”或“合法初始空状态”，不能用于吞掉：

- Customer API failure；
- response contract failure；
- options provider failure；
- runtime projection failure。

对于非 options-bearing 字段：

- renderer 不得无条件迭代 `options`；
- 没有 `options` 属性是合法状态。

---

### 4.1 字面“（空）”选项与真正空值分离

用户明确删除的是实际下拉中显示字面文字“（空）”的选项，不是真正的null/空字符串。具体范围见 `../remediation/enterprise-empty-option-removal-v1.md`。
按实际显示label定位静态/动态来源和控件注入，不能按value是否为空或真假值全局过滤。合法0/false、真正空状态、nullable/required与客户主键保持。
受影响控件未选择时显示灰色不可选“请选择”placeholder，已有值正常回显，不默认首项、不保存占位文字。其他未命中控件不改；MOX客户类别现无该文字选项，原合法空值规则继续有效。
测试区分“菜单不提供字面（空）”与“字段允许未填写”，不得删除真实空值测试或把API/provider异常吞成空列表。

---

## 5. Customer 级联字段

当前客户级联字段包括至少：

```text
region
representativeOffice
country
customerName
```

它们属于 Customer Relation 的 UI Projection，但其静态字段定义仍来自各模块 Field Contract。

正确链：

```text
customers.customer_id + display fields
→ shared customer API
→ frontend normalization
→ Runtime Options Provider
→ region options
→ representativeOffice options
→ country options
→ customerName candidates
→ unique customer_id
```

`customer_id` 必须在级联筛选全过程保留。

不得通过 `customerName` 代替关系主键。

---

## 6. 错误边界

必须区分：

```text
CUSTOMER_FETCH_FAILED
CUSTOMER_RESPONSE_CONTRACT_FAILED
OPTIONS_PROVIDER_FAILED
FORM_RUNTIME_FAILED
```

Runtime Field Model / renderer 的 TypeError 不得再被包装成“获取客户数据失败”。

错误边界的目的是诊断，不是把异常静默转换成空 options。

---

## 7. Conformance Gate

至少验证：

### 7.1 Static field authority

对每个 options-bearing field：

```text
Contract field type/control/editor
==
Production runtime判定所使用的Authority
```

不得测试一套 metadata，Production 使用另一套 metadata。

### 7.2 Runtime options contract

对 `region`、`representativeOffice`、`country`、`customerName` 等动态选择字段：

- Production Create 初始化后 `options` 为 Array；
- 级联变化后仍为 Array；
- customer candidate 保留真实 `customer_id`；
- API failure 不被转换为空数组成功状态；
- 非 select 字段不会进入 options iterable 路径。

### 7.3 五模块

MOX / TOB / ISP / 电力 / 大企必须使用同一共享 Runtime Options 机制或同一底层算法，不得再次形成 MOX 正常、其他四模块走另一套类型判断的分叉。

### 7.4 Production-path reproduction

任何该类回归测试必须覆盖真实 Production Create/Edit 初始化链。

禁止仅构造手工 field mock 并断言 helper 局部行为后，就声称页面链通过。

---

## 8. Excel / Contract 后续维护影响

未来 Excel 发生字段 label、group、order、option-set 或字段新增调整时：

- Runtime Options 逻辑不得通过中文 label 判断字段类型；
- 不应为新增 select 字段到页面代码中额外维护第二份 `type`；
- Field Contract 更新后，Runtime Projection 与 Options Provider 应通过 canonical key + authoritative fieldDef 自动继承；
- 如果新字段需要动态 options，应通过明确 provider/editor/control binding 接入，而不是页面内针对字段名硬编码。

这条规则是后续降低 Excel 变更维护成本的重要组成部分。

---

## 9. 完成状态

本次已确认的根因：

```text
错误：检查 f.type（undefined）
正确 Authority：fieldDef.type（'select'）
受影响：region / representativeOffice / country / customerName
Customer API：PASS
```

实施修复完成后，仍需用户人工复验 TOB / ISP / 电力 / 大企 Create 页面，人工 PASS 前不得把该缺陷标记为 USER_ACCEPTED。
