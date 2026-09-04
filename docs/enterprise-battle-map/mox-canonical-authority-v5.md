# 企业作战地图：MOX Canonical Authority V5

**状态：CURRENT MOX AUTHORITY**  
**取代：`mox-canonical-authority-v4.md` 中与本文件冲突的内容**  
**共享架构：`enterprise-contract-architecture-v4.md`**

---

## 1. 本次修正

根据当前实际运行链调查与用户最新确认，MOX 新增/编辑的最终顶层分组不是 3 个，而是 4 个：

```text
客户信息
无线格局
微波格局
作战情况
```

MOX 不使用“业务格局”作为顶层分组。

当前代码实际新增/编辑运行链使用：

```text
mox Field Contract
→ getCreateFields() / getEditFields()
→ 当前 group/section 映射逻辑
→ renderer
```

`getCreateProjection()` / `getEditProjection()` 不是当前页面真实渲染链，不能再由测试把它们当作 Create/Edit runtime Authority。

---

## 2. MOX 最终 41 个业务字段

字段集合保持 41 项不变。

### 客户信息（1—6）

1. 地区部
2. 代表处
3. 国家
4. 客户ID
5. 客户名称
6. 客户类别

### 无线格局（7—18）

7. 阶段
8. 无线空间（MUSD）
9. 窄带格局
10. 宽带格局
11. 宽带站点数
12. 宽带频谱
13. 频谱状态（无线 canonical 独立）
14. 26年机会点（无线 canonical 独立）
15. 26年空间（基站数量）
16. 27-28年机会空间（基站数据量）
17. 基站单价（xxx美金/站）
18. 优先级

### 微波格局（19—28）

19. 光纤化率
20. 微波存量总链路数
21. 存量我司格局
22. 现网友商份额
23. 频谱状态（微波 canonical 独立）
24. 友商空间（跳数）
25. 26年机会点（微波 canonical 独立）
26. 26年基站回传空间（微波跳数）
27. 26年视频回传空间（微波跳数）
28. 26年GAP

### 作战情况（29—41）

29. 整体空间
30. 作战分类-是否重点项目
31. 空间洞察
32. 项目状态
33. 项目风险状态
34. 整体空间（跳）
35. 整体空间（M$）
36. 26年空间（跳）
37. 26年订货空间（$M）
38. 已下单数量（跳）
39. 已下单金额（$M）
40. 一线接口人
41. 作战进展

canonical key、API/DB mapping、枚举和旧字段删除规则继续沿用 V4 中已冻结内容，除非本文件明确修正。

---

## 3. Field Contract 分组规则

MOX Field Contract 的分组业务语义统一使用：

```text
group
```

每个字段必须直接属于四个目标 group 之一。

禁止通过通用映射把：

```text
无线格局 + 微波格局
```

折叠为：

```text
业务格局
```

如果现有 `getFromSectionKey()` 等函数产生这种折叠，则属于 MOX runtime nonconformance，必须修复或替换为不会改变 Contract group Authority 的通用分组实现。

---

## 4. Create / Edit 真实运行时门禁

MOX Create runtime 以实际 renderer 使用的 `getCreateFields()` 路径为准；Edit runtime 以 `getEditFields()` 路径为准。

必须证明：

```text
Contract create-visible keys
==
真实 renderer create keys
```

以及：

```text
Contract edit-visible keys
==
真实 renderer edit keys
```

要求：

- 无遗漏；
- 无额外字段；
- 无重复字段；
- order 一致；
- group 一致；
- 实际 group 集合恰好为 4 个目标 group。

---

## 5. 重复 Projection API

当前已知：

- `getCreateProjection()` / `getEditProjection()` 可产生与真实运行时不同的分组结果；
- 当前页面实际消费 `getCreateFields()` / `getEditFields()`；
- 旧测试曾验证错误的 Projection API。

最终状态不得保留两套独立投影算法。

处理规则：

1. 如旧 Projection API 无真实消费者，删除；
2. 如仍需兼容内部调用，改为调用唯一 runtime projection 实现的薄包装；
3. 不保留独立过滤、排序、分组逻辑；
4. 测试必须覆盖实际 renderer 使用的路径。

---

## 6. 客户类别

MOX `customerCategory` 固定合法状态：

```text
空值
核心NA
战略NA
```

空值是合法状态，不是缺失测试数据。

Create/Edit option-set 与测试均必须完整覆盖三个状态。

---

## 7. UI 视觉分组

四个 group 必须在新增和编辑中具备明显视觉层级。

至少要求：

- 标题字号/字重明显高于字段 label；
- 每组开始前有统一垂直间距；
- 标题与上一组字段不得贴在一起；
- 组间有可识别分隔；
- 新增/编辑共用同一 group 样式；
- “作战情况”必须与“微波格局”最后字段明确分开。

---

## 8. 客户关系、API、数据库与 SQLite

V4 中端到端规则继续有效：

```text
canonical key
→ UI
→ API read/create/update
→ database.js mapping
→ SQLite persistence/relation
```

客户展示字段通过 `customer_id` 关联客户主数据；客户类别写入客户主数据 Authority，不在 MOX 表复制一列。

V34、`_migrations`、新建库/升级库一致、旧字段清理等要求保持不变。

---

## 9. 作战进展

`battleProgress` 继续作为 canonical 业务身份。

独立“新增进展”弹窗和真实存储模型需要 Runtime Survey 进一步恢复；调查完成前不得：

- 删除独立进展录入机制；
- 把它降级为普通 textarea；
- 新造另一套进展数据模型。

现有正确 TOB 进展交互仍作为行为参考。

---

## 10. Metric 与 Heatmap

9 个 Metric 规则保持 V4 冻结内容不变。

MOX Heatmap 当前真实数据链由 `Enterprise Runtime Implementation Survey` 调查，不在本次 group 修正中猜测或重构。

---

## 11. 测试修正门禁

必须重建以下测试：

1. 直接验证真实 `getCreateFields()` / `getEditFields()` runtime；
2. Contract → runtime 与 runtime → Contract 双向集合相等；
3. Create group 精确为：客户信息/无线格局/微波格局/作战情况；
4. Edit group 同上；
5. group 顺序与字段顺序正确；
6. `customerCategory` 包含空值/核心NA/战略NA；
7. 不再用未被 renderer 消费的 Projection API 证明页面正确；
8. 如删除旧 Projection API，删除只验证旧 API 的过期测试。

---

## 12. 当前已知问题分类

当前 MOX runtime audit 中相关 HIGH finding 应重新归类：

- Contract 使用 group、旧 Authority 写 section：`DOCUMENT_GAP`，本 V5 已修正；
- `getCreateProjection/getEditProjection` 与真实 runtime 不一致：`ARCHITECTURE/IMPLEMENTATION DUPLICATION`；
- 测试验证错误 Projection API：`TEST_GAP`；
- 单向测试无法发现缺字段：`TEST_GAP`；
- customerCategory 测试漏空值：`TEST_GAP`。

不得因为旧 Authority 写错而把当前正确的 4-group 逻辑改成 3-group。

---

## 13. 完成标准

MOX Create/Edit 本轮只有全部满足才可通过：

- 41 字段 Authority 不变；
- Create/Edit 实际运行路径只有一套投影算法；
- MOX 四个 group 正确；
- 页面不存在“业务格局”顶层 group；
- 双向字段完整性测试通过；
- customerCategory 三态测试通过；
- group 视觉分隔专业、统一；
- API/DB/SQLite 无回归；
- 全量 Vitest 与 build 通过。
