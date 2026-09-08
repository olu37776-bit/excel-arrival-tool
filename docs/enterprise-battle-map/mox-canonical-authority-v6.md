# 企业作战地图：MOX Canonical Authority V6

**状态：CURRENT MOX AUTHORITY**  
**取代：`mox-canonical-authority-v5.md` 中与本文件冲突的内容**  
**共享架构：`enterprise-contract-architecture-v5.md`**

---

## 1. 本版依据

本版原有机制问题为历史实施依据，不能据此推定当前仍未修复；当前本地状态以 authority-index.md 及对应 HEAD 报告为准。已确认的 Excel 增量同步进入下面的最终字段集合：

- MOX 依照 `enterprise-excel-confirmed-delta-v1.md` 删除“整体空间（肥肉/瘦肉/骨头）”分类字段，最终为40项；其他字段不变；
- MOX Create/Edit 正确顶层 group 为 4 个：客户信息、无线格局、微波格局、作战情况；
- 实际渲染链使用 `getCreateFields()` / `getEditFields()`；
- `getCreateProjection()` / `getEditProjection()` 曾与真实 runtime 不一致；
- `getMoxFromSections()` 已确认未被使用；
- Heatmap 当前存在使用中文 label 而不是 canonical key 的实现；
- `updateMoxNetwork()` 仍接受旧 key：`office`、`customer`、`major_project`、`progress`；
- Progress 当前“历史表 + `battleProgress` 文本”双写；
- Customer SQL 曾漏 `customer_id`，问题已定位并修复，后续作为回归门禁。

本版目标是把 MOX 收敛成真正可推广的端到端参考实现。

---

## 2. 40 个业务字段与 group

字段集合以 V5/V6 既有41项为基线，仅删除上述分类字段。整体空间金额与跳数保留；这里是目标契约，不表示本地已完成实施。

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
13. 频谱状态（无线）
14. 26年机会点（无线）
15. 26年空间（基站数量）
16. 27-28年机会空间（基站数据量）
17. 基站单价（xxx美金/站）
18. 优先级

### 微波格局（19—28）

19. 光纤化率
20. 微波存量总链路数
21. 存量我司格局
22. 现网友商份额
23. 频谱状态（微波）
24. 友商空间（跳数）
25. 26年机会点（微波）
26. 26年基站回传空间（微波跳数）
27. 26年视频回传空间（微波跳数）
28. 26年GAP

### 作战情况（29—40）

29. 作战分类-是否重点项目
30. 空间洞察
31. 项目状态
32. 项目风险状态
33. 整体空间（跳）
34. 整体空间（M$）
35. 26年空间（跳）
36. 26年订货空间（$M）
37. 已下单数量（跳）
38. 已下单金额（$M）
39. 一线接口人
40. 作战进展

MOX 不允许出现“业务格局”顶层 group。

---

## 3. Create/Edit Runtime Projection

生产 runtime 必须只有一套业务算法。

目标：

```text
Field Contract
→ getCreateFields() / getEditFields() 或其唯一公共底层实现
→ 按 field.group 分组
→ renderer
```

要求：

- 不再将无线格局/微波格局折叠成业务格局；
- `getFromSectionKey()` 如继续存在，只能进行无语义改变的技术组织；
- `getCreateProjection()` / `getEditProjection()` 不得保留另一套过滤/排序/分组逻辑；
- `getMoxFromSections()` 无消费者则删除；
- 实际 renderer、测试、辅助函数最终指向同一算法。

Create/Edit 必须分别双向验证字段完整性、顺序和 group。

---

## 4. Group UI 样式

新增与编辑四组共用共享样式。

至少保证：

- group 标题明显高于字段 label；
- 每个 group 开始前有统一垂直间距；
- 有明确分隔线、背景或等价视觉边界；
- “作战情况”不紧贴微波格局最后一项；
- Create/Edit 风格一致；
- 不为 MOX 单独复制一份 CSS，优先共享 renderer/group 样式能力。

---

## 5. Customer relation

客户显示信息来自客户主数据，MOX 业务记录通过 `customer_id` 关联。

已修复问题：客户 SQL 曾漏选 `customer_id`。

永久门禁：

```text
customers.customer_id
→ query
→ API
→ frontend candidate
→ unique selection
→ create/update relation
```

客户类别固定合法状态：

```text
空值
核心NA
战略NA
```

空值必须进入 option-set 测试。

---

## 6. `updateMoxNetwork()` 与 API canonical-only

当前旧 key 支持必须删除：

```text
office
customer
major_project
progress
```

对应业务必须只使用最终 canonical key。

规则：

- 当前 UI 调用先迁移到 canonical key；
- 活动 update path 不再翻译 legacy key；
- legacy key 仅可在一次性 migration/remediation 中出现；
- 测试必须证明 legacy key 不再被 runtime update 接受；
- 不保留 alias/fallback/双写。

---

## 7. Heatmap canonical 化

当前 Heatmap 业务展示逻辑暂不重新设计，但内部字段身份必须 canonical 化。

要求：

- 所有 field lookup 使用 canonical key；
- 中文 label 仅用于展示；
- 不通过 label 读取 record value；
- 不直接使用 SQLite column 作为前端业务字段身份；
- Heatmap 引用 key 必须存在于 MOX Field Contract；
- 修复前后现有 Heatmap 业务结果保持一致；
- 增加 canonical-key conformance 测试。

---

## 8. Progress 单一事实源

历史发现的“进展历史表 + `battleProgress` 文本双写”不可接受；用户最新称MOX无此问题，须按实际候选回归核实。

最终：

```text
Progress history table = 唯一持久化 Authority
```

`battleProgress` 仍是第 40 个 canonical 业务身份，但属于关系/投影视图：

```text
Progress history
→ latest/current progress projection
→ battleProgress
```

独立新增/编辑进展弹窗继续操作 Progress History。

Create/Edit中的作战进展通过特殊progress editor/history projection承载同一UI结构：只读最新摘要、表单内可展开新增按钮、主题和内容两个可编辑输入。两者均不能仅保留readonly摘要并让独立popup替代；新增无历史时保留结构并显示合法空摘要。Create/Edit的父记录ID、草稿及保存时机按真实代码分别核实，不得写MOX业务表第二份文本。
新增页、编辑页和独立“新增进展”弹窗必须纳入同一对照：四处原有名称（最新进展、新增进展、进展主题、进展内容）只做“作战”命名调整，其他原有功能、样式和交互不随改名变化。三入口的主题/内容语义、校验、payload、存储归属、父记录关联与保存后回显应一致；新增业务记录尚无ID等必要生命周期差异单独说明，不强行统一提交时机，也不把独立弹窗外壳套进表单。用户报告TOB、ISP、电力、大企仍有作战进展双写，已让本地Agent按调查报告的最小修复建议实施。当前沿用该建议，不另开实施方案；修复完成后按 `reviews/enterprise-progress-single-source-independent-review-v1.md` 独立审查。云端未读取本地报告/代码/实库，不声明已完成或已验证。

仅将可见“进展”文案加“作战”，保留最新/新增等限定词，canonical身份和字段总数不变。当前MOX作为共享进展修复的回归对象，核验三入口、主题/内容存储及latest投影；底栏按实际修复范围核验，其他表单区域不动。当前按 `reviews/enterprise-progress-single-source-independent-review-v1.md` 审查，不据历史finding推断MOX仍双写。

### 数据收敛

实施前比较所有 MOX 记录：

```text
business-table progress text
vs
latest history value
```

- 一致：停止双写后移除 business-text 持久化；
- 仅 business text 有内容：安全迁入 history 后再删除；
- 值冲突：以历史表为目标 Authority，但必须先保存冲突证据并按 remediation 规则处理，禁止静默覆盖；
- 无法可靠迁移历史语义：阻塞，不丢数据。

原 Progress 收敛计划的 V39 是历史任务约束，不是本次 Excel 增量预留编号。本次如需新迁移，应核实真实迁移清单，按当前项目规则分配下一可用版本，不覆盖、重写或复用已执行迁移；真实版本冲突需记录。

---

## 9. Database / API / SQLite

继续要求 canonical key 一路贯穿：

```text
Field Contract
→ API canonical field
→ database.js mapping
→ SQLite column/relation
```

本轮重点验证：

- legacy key active mapping = 0；
- customer_id relation 完整；
- Progress business text 双写 = 0；
- Heatmap 不依赖 DB/中文 label identity；
- 新建库与升级库最终 Schema 一致；
- V34—V38 原有链无回归；
- 历史迁移保持原样；新增迁移的事务、回滚、幂等和 `_migrations` 登记正确。

---

## 10. Metric

9 个 Metric 规则保持不变。

验证所有 Metric field reference 都是 canonical key，并且计算与点击筛选继续使用同一 `where`。

---

## 11. 必须重建的测试门禁

至少覆盖：

1. 真实 `getCreateFields()` / `getEditFields()` runtime；
2. Table/Create/Edit 双向集合相等；
3. MOX 4 group 精确顺序；
4. 无“业务格局”group；
5. `customerCategory` 三态含空值；
6. unused/duplicate Projection API 不再拥有独立业务逻辑；
7. Heatmap 使用 canonical key；
8. `updateMoxNetwork()` 拒绝或不再接受旧 key；
9. Customer 查询结果必须带 `customer_id`；
10. Progress 只写 history，一次操作不会再写 business text；
11. latest progress projection 正确；
12. CRUD round-trip；
13. Migration、新库/升级库一致；
14. 9 Metric 无回归；
15. 全量 Vitest、build、已有 lint/typecheck。

---

## 12. 完成门槛

MOX 只有全部满足才可成为 Reference Implementation 候选：

- 最终40项字段完整，已删除分类字段没有活动消费者；
- 4 group 正确且视觉清晰；
- Create/Edit 只有一套 runtime Projection 算法；
- 双向 Conformance 通过；
- Customer `customer_id` 全链通过；
- Heatmap 使用 canonical key；
- legacy runtime key = 0；
- Progress 只有 history 单一持久化事实源；
- business progress text 双写 = 0；
- API/database.js/SQLite canonical mapping 完整；
- 相关 Migration 正确；
- 全量自动验证通过；
- 独立审查和用户人工验收通过。
