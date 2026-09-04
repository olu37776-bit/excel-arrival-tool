# 企业作战地图：契约驱动架构 V4

**状态：CURRENT SHARED ARCHITECTURE AUTHORITY**  
**取代：`enterprise-contract-architecture-v3.md` 中与本文件冲突的内容**  
**代码长期分支：`feature/enterprise-battle-map`**

---

## 1. 本次修正依据

当前 MOX 运行时调查已经确认：

- Field Contract 当前实际使用 `group` 语义，而不是 Authority V3 中描述的统一 `section` 语义；
- 新增真实运行路径调用 `getCreateFields()`；
- 编辑真实运行路径调用 `getEditFields()`；
- 随后通过当前 `getFromSectionKey()` 等分组映射逻辑生成最终表单分组；
- `getCreateProjection()` / `getEditProjection()` 不是当前新增/编辑真实渲染路径，但部分测试却验证了它们；
- 因此当前存在“运行时投影路径”和“测试投影路径”不一致的问题；
- 当前测试还存在仅从 Projection 指向 Contract 的单向检查，缺少从 Contract 反向证明所有目标字段都进入实际运行时输出；
- `customerCategory` option-set 测试曾遗漏合法空值。

本文件不推倒现有 Contract 架构，而是收敛已有实现中的重复投影语义和测试盲区。

---

## 2. 核心架构不变

企业板块继续采用：

```text
模块 Field Contract
├─ Table runtime projection
├─ Create runtime projection
├─ Edit runtime projection
├─ API Mapping
├─ database.js Mapping
└─ SQLite Persistence

模块 Metric Contract
├─ Metric Calculation
└─ Click-to-Filter
```

canonical key 继续串联 UI、API、`database.js` 与 SQLite。

数据库治理继续使用：

```text
V*.sql + database.js migration registry + _migrations
```

不得建立长期 legacy compatibility、双读、双写或旧 Schema re-export。

---

## 3. `group` 是表单分组唯一业务语义

Field Contract 的表单分组属性统一称为：

```text
group
```

不得同时维护具有相同职责的 `group` 和 `section` 两套业务 Authority。

推荐每个字段至少包含：

```js
{
  key,
  label,
  group,
  order,
  authority,
  data,
  ui,
  runtime,
  validation,
  behavior
}
```

如果现有实现内部仍存在 `sectionKey` 等技术命名，只允许作为 renderer 内部临时结构，不得成为第二份业务分组定义。

---

## 4. 各模块最终 group Authority

### 4.1 MOX

MOX 新增和编辑固定为 **4 个顶层 group**：

```text
客户信息
无线格局
微波格局
作战情况
```

MOX **不得出现“业务格局”顶层 group**。

MOX 字段顺序：

- 客户信息：1—6；
- 无线格局：7—18；
- 微波格局：19—28；
- 作战情况：29—41。

### 4.2 TOB / ISP / 电力 / 大企

其他四个模块固定为 **3 个顶层 group**：

```text
客户信息
业务格局
作战情况
```

模块专属业务字段统一放入“业务格局”，具体字段由各自 Canonical Authority 决定。

---

## 5. 运行时 Projection 必须只有一套权威路径

当前真实新增/编辑路径已经确认使用：

```text
Field Contract
→ getCreateFields() / getEditFields()
→ group mapping
→ Create/Edit renderer
```

因此正式 Runtime Authority 必须围绕这条真实路径收敛。

### 5.1 禁止双投影实现

如果 `getCreateProjection()` / `getEditProjection()` 与 `getCreateFields()` / `getEditFields()` 分别实现不同的过滤、排序或分组算法，则属于重复业务 Authority。

最终必须满足以下之一：

1. 删除没有真实运行时消费者的旧 Projection API；或
2. 将其改为对唯一运行时 Projection 实现的薄包装，不允许拥有独立逻辑。

禁止：

```text
getCreateProjection() → A算法
getCreateFields()     → B算法
```

然后测试 A、页面运行 B。

### 5.2 分组映射规则

分组函数只能把字段按 Contract 的 `group` 组织为 UI group，不得重新定义业务归属。

尤其禁止：

```text
MOX 无线格局 + 微波格局
→ 自动折叠成“业务格局”
```

MOX 必须保持四组；其他模块 Contract 本身已经使用“业务格局”，因此自然形成三组。

---

## 6. 表格 / 新增 / 编辑的一致性

Field Contract 是唯一字段 Authority。

```text
Field Contract
├─ table fields
├─ create fields
└─ edit fields
```

页面组件不得维护第二套完整字段列表、完整 group 列表或完整排序。

允许的差异仅来自 Contract 中明确的：

- visible；
- editable；
- controlId；
- editorId；
- formatterId。

---

## 7. 双向 Conformance Gate

原有单向检查不足。今后必须做双向集合相等验证。

### 7.1 Create

```text
EXPECTED_CREATE_KEYS
= Contract 中 ui.create.visible=true 的全部 key

ACTUAL_CREATE_KEYS
= 真实运行时 getCreateFields() 最终交给 renderer 的全部 key

必须：
EXPECTED_CREATE_KEYS == ACTUAL_CREATE_KEYS
```

同时验证：

- 无缺失；
- 无额外字段；
- 每个 key 恰好一次；
- order 一致；
- group 一致。

### 7.2 Edit

同理：

```text
EXPECTED_EDIT_KEYS == ACTUAL_EDIT_KEYS
```

### 7.3 Table

同理验证：

```text
EXPECTED_TABLE_KEYS == ACTUAL_TABLE_KEYS
```

测试不得只验证“实际 Projection 中的字段都能在 Contract 找到”，因为这无法发现 Contract 字段被静默遗漏。

---

## 8. Group Conformance Gate

运行时最终 group 集合必须等于模块 Authority。

MOX：

```text
客户信息 / 无线格局 / 微波格局 / 作战情况
```

TOB / ISP / 电力 / 大企：

```text
客户信息 / 业务格局 / 作战情况
```

同时验证 group 顺序和 group 内字段顺序。

---

## 9. Option-set Conformance

所有 enum/select 字段必须验证完整合法值域，而不是仅验证部分值存在。

MOX `customerCategory` 合法状态固定为：

```text
空值
核心NA
战略NA
```

测试必须验证空值也是合法状态，不能只断言两个非空值。

---

## 10. UI 视觉分组

运行时 group 正确不等于视觉分组合格。

Create/Edit renderer 对每个顶层 group 必须提供：

- 明确标题层级；
- 与上一 group 有稳定垂直间距；
- 标题与字段区存在可识别分隔；
- 新增和编辑使用同一套 group 样式；
- 不允许“作战情况”标题紧贴上一组最后一个字段。

样式属于共享 renderer 机制，不应五个模块分别维护一套 CSS。

---

## 11. API / database.js / SQLite 仍是 Contract 链正式消费者

本次分组修正不得弱化端到端契约要求。

每个 canonical key 仍必须具有完整、唯一的：

```text
UI field
→ API read/create/update mapping
→ database.js mapping
→ SQLite column / relation
```

Contract runtime mapping 或独立 Persistence Map 可以物理拆分，但必须使用相同 canonical key，并由 Validator 验证一一对应。

数据库测试必须覆盖：

- CRUD；
- Migration；
- 新建库 / 升级库一致；
- Authority 外旧字段清理；
- round-trip read/write。

---

## 12. Metric 与 Heatmap

Metric Contract 继续独立于 Field Contract，并通过 canonical key 引用字段。

Heatmap 当前已存在共享 `HeatmapChart` 和模块级 Heatmap 设计要求，但真实执行链仍需 Runtime Survey 进一步恢复。

在真实链调查完成前：

- 不新增假 Heatmap 业务规则；
- 不用中文 label 或 DB column 作为长期字段身份；
- 已确认的 Heatmap 字段引用应使用 canonical key；
- Heatmap 的数据来源、转换、聚合、tooltip、点击筛选需在调查后决定是否正式纳入共享 Contract 模型。

---

## 13. Progress

`battleProgress` 保留为当前 canonical 业务身份，但其特殊新增/追加/历史存储模型必须以现有真实实现调查结果为准。

在调查完成前不得把独立“新增进展”能力降级成普通 textarea，也不得自行新增另一套 Progress 模型。

---

## 14. 测试治理新增硬门禁

必须删除或重建以下测试：

- 验证未被真实页面消费的 Projection API，却声称代表 Create/Edit runtime 的测试；
- 只做 Projection → Contract 单向检查的测试；
- 将 MOX 误断言为 3 个 group 的测试；
- 将 TOB/ISP/电力/大企误断言为 4 个 group 的测试；
- 遗漏 enum 合法空值的测试；
- 复制生产字段数组形成第二 Authority 的测试。

测试必须直接调用真实运行时使用的 Projection 函数或其唯一公共实现。

---

## 15. 当前完成标准

企业 Field Contract runtime 机制只有同时满足以下条件才算收敛：

1. 每个模块只有一份字段 Authority；
2. 每个模块只有一套真实 Create/Edit Projection 算法；
3. 测试验证的就是实际 renderer 使用的 Projection；
4. Create/Edit/Table 双向字段集合一致；
5. MOX 四组正确且无“业务格局”；
6. 其他四模块三组正确；
7. group 视觉样式统一；
8. option-set 完整；
9. API/DB/SQLite mapping 继续完整；
10. 全量测试与 build 通过。
