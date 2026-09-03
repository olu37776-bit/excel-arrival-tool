# 企业作战地图：MOX Canonical V3 独立审查规范 V1

**状态：CURRENT REVIEW AUTHORITY**  
**文档分支：`enterprise-battle-map-authority`**  
**本地实施分支：`feature/enterprise-battle-map`**  
**审查对象：MOX Canonical V3 当前实现、V34 Migration、字段契约、UI Projection、API/数据库映射、统计与点击筛选**  
**审查性质：只读独立审查，不实施修复**

---

## 1. 审查目标

本次审查用于判断当前 MOX 是否已经达到：

```text
MOX VERIFIED
REFERENCE_IMPLEMENTATION_V1 候选
```

审查不能只看“测试是否通过”，必须证明以下链路一致：

```text
MOX Excel / 已确认需求
→ Canonical Field Contract
→ 表格
→ 新增弹窗
→ 编辑弹窗
→ API
→ database.js
→ SQLite 最终 Schema

MOX Metric Contract
→ 统计数值
→ 点击指标
→ 下方表格筛选结果
```

审查通过后，MOX 才能作为 TOB、ISP、电力和大企后续建设的实现参考。

---

## 2. 审查角色与边界

审查 Agent 必须使用新的上下文，不依赖实施 Agent 的完成声明。

本轮只允许：

- 读取 Git 状态、代码、测试、Excel、数据库 Schema 和 Authority；
- 执行只读或隔离测试环境中的自动验证；
- 创建独立 Review 证据文档；
- 更新本地状态文档中的 Review 结果（如现有流程要求）。

本轮禁止：

- 修改生产代码；
- 修改测试以使失败消失；
- 修改 Excel；
- 修改真实数据库；
- 修改 `database.js`；
- 修改或重写 V34；
- 执行 remediation；
- 开始其他业务模块；
- 进行人工页面验收。

页面人工验收由用户完成。

---

## 3. 必读 Authority

审查开始前必须读取：

1. 共享架构：

```text
https://raw.githubusercontent.com/olu37776-bit/excel-arrival-tool/enterprise-battle-map-authority/docs/enterprise-battle-map/enterprise-contract-architecture-v2.md
```

2. MOX 唯一业务与实现 Authority：

```text
https://raw.githubusercontent.com/olu37776-bit/excel-arrival-tool/enterprise-battle-map-authority/docs/enterprise-battle-map/mox-canonical-authority-v3.md
```

3. 本审查规范：

```text
https://raw.githubusercontent.com/olu37776-bit/excel-arrival-tool/enterprise-battle-map-authority/docs/enterprise-battle-map/reviews/mox-canonical-v3-independent-review-spec-v1.md
```

4. 本地“企业作战地图基表”的 MOX Sheet；
5. 当前本地实施分支的代码、测试、Migration 和 Review 证据。

Authority 使用原则：

- `mox-canonical-authority-v3.md` 是当前规范化目标；
- Excel 是原始字段来源，用于核实列、Row2、Row3、Data Validation 和说明；
- 若 Authority 与 Excel 发生不能解释的冲突，记录 BLOCKING finding，不得自行折中；
- 当前代码、API、`database.js`、SQLite 只代表实现现状，不能反向修改需求；
- 本地旧字段文档、旧 Schema 和旧 config 不得作为当前字段 Authority。

---

## 4. Git 与审查基线

必须记录：

```bash
git branch --show-current
git status --short
git log -1 --oneline
git diff --stat
```

必须确认：

```text
CURRENT_BRANCH=feature/enterprise-battle-map
```

Review 文档必须记录：

- reviewed HEAD；
- 工作区是否存在未提交变更；
- 本轮审查实际读取的 Authority 版本；
- V34 文件及其注册代码所在版本；
- 测试执行环境。

若工作区存在无法区分来源的大量未提交变更，应记录审查可信度风险；不得擅自清理。

---

## 5. 当前真实代码拓扑恢复

审查 Agent 必须先列出与 MOX 相关的实际文件，而不是假设文件结构正确。

至少识别：

- 共享 Field Contract 类型；
- Field Projection；
- Contract Validator；
- Option Sets；
- Metric Engine；
- MOX Field Contract；
- MOX Metric Contract；
- MOX 表格字段来源；
- MOX 新增字段来源；
- MOX 编辑字段来源；
- MOX API Route / Handler / DTO；
- `database.js` 中 MOX CRUD、字段映射和 Validation；
- MOX SQLite 建表定义；
- V34 SQL；
- `database.js` Migration registry / ordered list；
- `_migrations` 执行记录机制；
- MOX 测试。

Review 中必须画出当前真实依赖关系，并标明：

- ACTIVE AUTHORITY；
- PROJECTION；
- ADAPTER；
- DEAD / UNUSED；
- DUPLICATE AUTHORITY。

---

## 6. 契约目录与单一 Authority

目标目录：

```text
src/enterprise/contracts/
src/enterprise/mox/contracts/
```

不得将 MOX 领域契约继续作为通用配置放在 `src/config`。

审查以下历史文件及其所有引用：

- `mox-field-contract.js`；
- `mox-field-schema.js`；
- `mox-metric-contract.js`；
- 任何近似命名的 MOX fields / columns / form schema 文件。

通过条件：

1. 只有一份活动 MOX Field Contract；
2. 只有一份活动 MOX Metric Contract；
3. 旧 `mox-field-schema.js` 已删除，或其能力已完全吸收到共享 Projection，且不再定义字段；
4. `src/config` 中不存在活动 MOX 字段或统计 Authority；
5. 不存在旧文件 re-export、fallback、动态加载或第二路径；
6. 表格、新增、编辑没有各自的完整字段 Authority。

以下任一情况为 BLOCKING：

- 两份字段集合同时影响运行；
- 新 Contract 已创建，但页面仍主要读取旧 Schema；
- 通过 fallback 在新旧字段间切换；
- `src/config` 旧配置仍是实际运行入口。

---

## 7. Field Contract 对象完整性

每个字段的逻辑契约至少必须表达：

### 7.1 Identity

- `key`；
- `label`；
- `group`；
- `order`。

### 7.2 Excel / Requirement Authority

- `source`；
- `sheet`；
- `column`；
- `row2Group`；
- `row3Label`。

### 7.3 Data Semantics

- `data.type`；
- `data.unit`（适用时）。

### 7.4 UI Projection

- table visible / formatter；
- create visible / editable / control；
- edit visible / editable / control。

### 7.5 Runtime Mapping

- API read field；
- API create field；
- API update field；
- `database.js` mapping；
- SQLite column；
- SQLite type；
- runtime source（business-table / customer-relation）。

### 7.6 Validation

- required；
- option set；
- min / max 或其他必要校验。

### 7.7 Special Behavior

- editor / handler / formatter identifier。

允许 Persistence Mapping 物理拆分到独立文件，但必须使用相同 canonical `key` 一一连接，并由 Validator 发现缺失或重复。

若所谓 Contract 仅包含 `key + label + order`，结果不得为 PASS。

---

## 8. MOX 最终字段集合与顺序

最终业务字段必须为 **41 项**。技术主键和操作列不计入 41 项。

### 8.1 客户信息（1—6）

1. 地区部
2. 代表处
3. 国家
4. 客户ID
5. 客户名称
6. 客户类别

MOX 不包含“行业”。

### 8.2 无线格局（7—18）

7. 阶段
8. 无线空间（MUSD）
9. 窄带格局
10. 宽带格局
11. 宽带站点数
12. 宽带频谱
13. 频谱状态（无线 canonical 字段）
14. 26年机会点（无线 canonical 字段）
15. 26年空间（基站数量）
16. 27-28年机会空间（基站数据量）
17. 基站单价（xxx美金/站）
18. 优先级

### 8.3 微波格局（19—28）

19. 光纤化率
20. 微波存量总链路数
21. 存量我司格局
22. 现网友商份额
23. 频谱状态（微波 canonical 字段）
24. 友商空间（跳数）
25. 26年机会点（微波 canonical 字段）
26. 26年基站回传空间（微波跳数）
27. 26年视频回传空间（微波跳数）
28. 26年GAP

### 8.4 作战情况（29—41）

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

关键门禁：

- `作战分类-是否重点项目` 是一个完整字段；
- 不得拆成“作战分类”和“重点项目”两个字段；
- 现有重点项目筛选必须使用该字段对应的 canonical `focusProject`；
- `作战进展`属于作战情况并固定最后；
- 表格按 1—41 展开；
- 新增和编辑按四个同级 Section 渲染：客户信息｜无线格局｜微波格局｜作战情况。

任何字段数、分组或顺序偏差都至少为 HIGH；产生字段错位或数据错写时为 BLOCKING。

---

## 9. 枚举、单位与输入控件

必须确认：

- 阶段：孵化 / 突破 / 纵深；
- 优先级：A / B / C / D；
- 整体空间：肥肉 / 瘦肉 / 骨头；
- 作战分类-是否重点项目：是 / 否；
- 空间洞察：已孵化 / 孵化中；
- 项目状态：已签单 / 推进中 / 跟踪；
- 无线与微波 26年机会点分别使用其正确 Y/N 语义。

所有带单位的用户可见字段必须使用中文全角括号，例如：

- 无线空间（MUSD）；
- 基站单价（xxx美金/站）；
- 友商空间（跳数）；
- 整体空间（M$）；
- 26年订货空间（$M）；
- 已下单金额（$M）。

数值、百分比、枚举和特殊进展字段不得统一退化为普通文本输入。

---

## 10. Excel Authority 映射审查

每个 source=excel 字段必须记录实际：

- Sheet；
- column；
- Row2 分类；
- Row3 原文；
- Data Validation 或说明（如存在）。

已确认：

```text
MOX F列 = 阶段
```

`customerId`属于明确追加的 requirement 字段，允许没有 Excel 列。

审查必须回答：

1. Excel 中当前 Authority 目标字段是否全部有精确映射；
2. Contract 中每个业务字段是否都有 Excel 或明确 requirement 来源；
3. 是否存在通过旧文档猜测的 column / Row2 / Row3；
4. 是否有同一 Excel 列错误映射给两个业务字段；
5. 用户可见规范 label 与 Excel 原始 Row3 是否被正确区分。

不得根据旧 UI 或数据库列名反推 Excel Authority。

---

## 11. 重名字段独立映射

必须验证：

```text
wirelessSpectrumStatus ≠ microwaveSpectrumStatus
wirelessOpportunity2026 ≠ microwaveOpportunity2026
```

两组重名字段必须分别拥有：

- 不同 canonical key；
- 不同 Excel column；
- 不同 API field；
- 不同 `database.js` mapping；
- 不同 SQLite column。

还必须有新增保存、编辑回填和查询返回的独立测试。

任意一层共用同一持久化字段均为 BLOCKING。

---

## 12. 表格、新增、编辑是否真正消费 Contract

审查不能只检查存在 Contract 文件。

必须追踪真实 import 和运行路径，确认：

```text
MOX Field Contract
├─ Table Projection
├─ Create Projection
└─ Edit Projection
```

通过条件：

- 字段集合来自 Contract；
- group 和 order 来自 Contract；
- label 和单位来自 Contract；
- input control 和 option set 来自 Contract；
- create/edit 权限来自 Contract；
- 特殊 editor 通过 registry 接入；
- 组件未再次维护完整字段数组。

目标：

```text
EXTRA_TABLE_FIELDS=0
EXTRA_CREATE_FIELDS=0
EXTRA_EDIT_FIELDS=0
```

允许少量布局代码、操作列和必要技术字段；不允许它们成为第二套业务字段 Authority。

---

## 13. 客户数据与 customer_id

必须验证点击新增时不再发生：

```text
获取客户数据失败
```

客户链路要求：

- 保留当前地区部、代表处等联动；
- 最终匹配唯一客户；
- 自动取得 `customer_id`；
- 不允许手工输入 `customer_id`；
- 同名客户不得直接取第一条；
- API 必须验证客户存在；
- SQLite 必须保存真实 `customer_id`；
- 编辑时客户信息全部只读；
- 编辑其他字段不得改变 `customer_id`。

MOX 目标态只以 `customer_id`建立客户关系。地区部、代表处、国家、客户名称和客户类别由客户主数据关联读取，不应继续作为 MOX 的重复业务 Authority。

---

## 14. 作战进展特殊交互

最终字段只允许：

```text
作战进展 / battleProgress
```

旧 `最新进展 / latest_progress` 不得继续作为活动字段。

但是必须继承原有特殊能力：

- 添加进展方式；
- 编辑进展方式；
- 特殊控件；
- 保存；
- 回填。

Contract 必须通过 `editorId` / `handlerId` 或等价机制挂接既有能力，不得退化为普通 input / textarea。

如果字段名称正确但特殊交互丢失，至少为 HIGH。

---

## 15. 重点项目映射与筛选

最终完整字段：

```text
作战分类-是否重点项目
```

canonical key：

```text
focusProject
```

必须验证：

- 表格、新增、编辑使用同一字段；
- 选项为“是 / 否”；
- 当前页面已有重点项目筛选继续工作；
- 筛选直接使用 `focusProject`；
- 不存在第二个“重点项目”字段；
- 不存在“作战分类”独立字段。

---

## 16. 明确废弃字段与运行时清理

以下已知字段必须退出最终运行态：

- `dpm`；
- `remark`；
- `service_interface`；
- `entered_amount`；
- `space_26`；
- `produce_owner`；
- `industry`；
- `latest_progress`；
- `phase_wireless`；
- 其他不属于 41 项、且不属于明确技术白名单的 MOX 业务字段。

删除范围：

- 活动 Field Contract / Schema；
- 表格；
- 新增；
- 编辑；
- API 请求和响应；
- `database.js` CRUD、mapping、Validation；
- SQLite 最终 Schema；
- 活动测试目标。

不允许长期存在：

- legacy alias；
- fallback 读取；
- 新旧双写；
- 旧字段 re-export；
- 旧配置动态切换。

旧字段只允许在一次性 V34 Migration 及对应 Migration 测试中出现。

---

## 17. V34 Migration 独立审查

当前已知历史问题：

- V34 SQL 曾写错；
- V34 曾未注册到 `database.js`；
- 最终数据库列曾缺失；
- `database.js` 曾保留旧字段映射。

必须验证：

1. V34 SQL 当前语法有效；
2. V34 已注册到 `database.js`实际 Migration registry / ordered list；
3. 执行顺序正确；
4. 迁移在事务中完成；
5. 全部成功后才写入 `_migrations`；
6. 失败会回滚，不留下半迁移状态；
7. 重复启动不会重复执行 V34；
8. 新建数据库的 MOX Schema 与旧数据库执行 V34 后完全一致；
9. `entered_amount`数据如有确定对应，迁移至最终已下单金额字段；
10. `latest_progress`数据迁移至 `battleProgress`；
11. 无对应目标的旧字段不复制；
12. 最终数据库不包含已废弃业务列；
13. CRUD、mapping、Validation、API 与最终 Schema 同步。

不得以“SQL 文件存在”代替“已注册且能执行”的证据。

---

## 18. Metric Contract 与三模块 UI

MOX 顶部必须只有三个并列大模块：

1. 空间洞察；
2. 当年项目；
3. 空间拓展。

每个模块内部展示指标，不能把九个指标拆成九张顶级卡片。

三个模块文字居中，并保持已经确认的骨干页面参考结构。

Metric Contract 每项至少包括：

- key；
- group；
- label；
- unit；
- where；
- aggregate。

同一个 `where`必须同时用于统计计算和点击后的表格筛选。

---

## 19. 九项统计与点击筛选

### 19.1 空间洞察

- 已孵化：`spaceInsight = 已孵化`，count；
- 孵化中：`spaceInsight = 孵化中`，count。

### 19.2 当年项目

当前不增加年份过滤。

- 总项目数：`projectStatus IN（已签单，推进中）`，count；
- 已签单：`projectStatus = 已签单`，count；
- 推进中：`projectStatus = 推进中`，count；
- 高风险：`projectStatus = 推进中 AND projectRiskStatus = 高风险`，count。

### 19.3 空间拓展

- 可参与总空间：`spaceInsight = 已孵化 AND projectStatus = 跟踪`，sum `overallSpaceMusd`；
- 总项目：`projectStatus = 跟踪`，count；
- 已落地：`spaceInsight = 已孵化 AND projectStatus = 跟踪`，count。

点击筛选门禁：

- 九个指标全部可点击；
- 点击后下方表格使用同一 `where`；
- `annual.total`与`expansion.total`必须使用不同 key 和条件；
- 高风险必须是 AND 条件；
- 可参与总空间与已落地点击后得到同一记录集合；
- 点击只改变下方表格；
- 顶部统计不得因自身筛选而错误重算。

---

## 20. Contract Validator 审查

Validator 至少必须发现：

1. canonical key 重复；
2. order 重复、缺失或不连续；
3. 非法 group；
4. Excel / requirement Authority 缺失；
5. 同一 Excel 列错误映射多个字段；
6. API / DB 映射缺失或重复；
7. 两个频谱状态共用技术字段；
8. 两个 26年机会点共用技术字段；
9. select 字段缺少 option set；
10. 单位 label 未使用中文全角括号；
11. `battleProgress`缺少特殊 editor；
12. 废弃字段进入最终 Contract；
13. 表格、新增、编辑存在 Contract 外业务字段；
14. `src/config`旧 MOX Authority 仍被引用；
15. V34 未注册；
16. V34 后最终 SQLite Schema 仍含废弃列。

Validator 应在测试/开发门禁中执行，不得在每次 Vue render 中重复运行。

---

## 21. ISP&大企导航回归检查

本轮同时验证已知导航修复：

```text
点击或进入 ISP&大企
→ ISP 页面
```

不得链接回企业首页。

该检查只是已知修复的回归门禁，不允许借此审查或修改 ISP 字段实现。

---

## 22. 测试质量审查

必须检查真实测试是否覆盖：

- 41 字段和精确顺序；
- 四个同级 Section；
- Excel / requirement Authority；
- 三处真实消费同一 Contract；
- 目标外字段数量为 0；
- 重名字段独立映射、保存和回填；
- 客户数据请求和 `customer_id`；
- 客户编辑只读；
- 重点项目字段与筛选；
- 作战进展特殊交互；
- V34 语法、注册、事务、回滚、幂等；
- 新建库和升级库最终 Schema 一致；
- 废弃字段不在最终 Schema；
- 九项统计；
- 九项点击筛选；
- ISP&大企进入 ISP；
- build。

禁止接受以下低质量测试：

- 复制生产逻辑后测试复制品；
- 只断言字符串存在；
- 过度 mock 核心路径；
- 只检查 Contract 文件存在，不检查消费者；
- 只检查 V34 文件存在，不检查注册和实际执行。

---

## 23. 独立自动验证

根据项目 `package.json` 和现有数据库验证脚本，独立执行：

- MOX Contract / Validator 测试；
- MOX Table / Create / Edit Projection 测试；
- MOX API / CRUD / DB mapping 测试；
- V34 Migration 测试；
- MOX Metric / Click-to-Filter 测试；
- MOX 全部测试；
- Phase 1 导航相关回归测试；
- 全量 Vitest；
- build；
- lint / typecheck（如配置）。

数据库验证必须在隔离测试数据库中执行，不修改用户真实业务数据库。

Review 文档必须记录：

- command；
- exit code；
- passed / failed；
- 失败分类：IMPLEMENTATION / TEST / ENVIRONMENT / PRE_EXISTING。

---

## 24. Finding 分级

### BLOCKING

包括但不限于：

- 两份活动 Field Authority；
- 表格、新增或编辑未真正使用 Contract；
- 41 字段、分组或顺序导致实际数据错位；
- 重名字段共用持久化列；
- `customer_id`保存或编辑保护错误；
- V34 SQL错误、未注册、非事务或无法升级旧库；
- 最终数据库缺目标列或仍含废弃业务列；
- 核心 API / DB 映射错误；
- 统计公式或点击筛选错误；
- build失败；
- ISP&大企仍进入企业首页。

### HIGH

包括但不限于：

- Contract 对象缺少关键层级属性；
- 字段 Authority 大量缺失；
- 作战进展特殊交互丢失；
- 重点项目筛选未使用 `focusProject`；
- 目标外 UI 字段仍存在；
- 测试无法防止核心回归。

### MEDIUM / LOW / INFORMATIONAL

不得用来掩盖核心链路缺失。死代码若不参与运行且不影响本次目标，可登记为 DEFERRED_TECH_DEBT，不阻塞当前 Review。

---

## 25. 审查结果与门禁

结果只能是：

```text
PASS
PASS_WITH_NONBLOCKING_FINDINGS
BLOCKED
```

只有以下全部成立，才允许进入 MOX VERIFIED 候选：

- 单一 Field Authority；
- 单一 Metric Authority；
- Contract 对象完整；
- 41 字段准确；
- 表格、新增、编辑使用同一 Contract；
- API、`database.js`、SQLite 映射完整；
- V34 正确、已注册、可升级、可回滚、幂等；
- 旧字段退出最终运行态；
- 客户数据与 `customer_id`正确；
- 重点项目筛选正确；
- 作战进展特殊交互正确；
- 九项统计与九项点击筛选正确；
- 自动测试和 build 通过；
- ISP&大企进入 ISP。

若结果为 PASS 或可接受的 PASS_WITH_NONBLOCKING_FINDINGS：

```text
NEXT_GATE=USER_MANUAL_ACCEPTANCE
```

用户人工验收通过后，才可发布：

```text
MOX VERIFIED
REFERENCE_IMPLEMENTATION_V1
```

若存在阻塞：

```text
NEXT_GATE=MOX_REMEDIATION
```

---

## 26. 本地 Review 证据文档

本地 Agent 应创建：

```text
docs/enterprise/reviews/mox-canonical-v3-independent-review.md
```

该文件仅记录审查证据，不得重写业务 Authority。

至少包含：

1. Review Result；
2. Reviewed HEAD；
3. Authority Versions；
4. Current Topology；
5. Field Contract Shape；
6. Exact 41-Field Verification；
7. Excel Authority Verification；
8. Table/Create/Edit Consumption；
9. Customer ID；
10. Duplicate-Name Field Mapping；
11. Focus Project Filter；
12. Battle Progress Special Editor；
13. V34 Migration；
14. Final SQLite Schema；
15. Metric Contract；
16. Click-to-Filter；
17. Test Quality；
18. Independent Verification；
19. Findings；
20. Next Gate。

---

## 27. 最终短回执

最终聊天只输出：

```text
MOX CANONICAL V3 INDEPENDENT REVIEW

RESULT=PASS/PASS_WITH_NONBLOCKING_FINDINGS/BLOCKED
REVIEWED_HEAD=短SHA或WORKTREE
FIELD_AUTHORITY=路径
METRIC_AUTHORITY=路径
DUPLICATE_AUTHORITIES=数量
OLD_SCHEMA_ACTIVE=YES/NO
CONTRACT_SHAPE=PASS/PARTIAL/FAIL
FIELD_COUNT=数量
GROUP_ORDER=PASS/FAIL
EXCEL_AUTHORITY=PASS/PARTIAL/FAIL
TABLE_USES_CONTRACT=YES/NO
CREATE_USES_CONTRACT=YES/NO
EDIT_USES_CONTRACT=YES/NO
EXTRA_FIELDS=table/create/edit数量
CUSTOMER_DATA=PASS/PARTIAL/FAIL
CUSTOMER_ID=PASS/PARTIAL/FAIL
DUPLICATE_FIELD_MAPPING=PASS/FAIL
FOCUS_PROJECT_FILTER=PASS/FAIL
PROGRESS_SPECIAL_EDITOR=PASS/FAIL
V34_SQL=PASS/FAIL
V34_REGISTERED=YES/NO
V34_MIGRATION=PASS/PARTIAL/FAIL
FINAL_DB_SCHEMA=PASS/PARTIAL/FAIL
OBSOLETE_RUNTIME_FIELDS=数量
METRICS=9/9或实际数量
CLICK_TO_FILTER=PASS/PARTIAL/FAIL
ISP_GROUP_TARGET=ISP/OTHER
TEST_QUALITY=PASS/PARTIAL/FAIL
MOX_TESTS=通过/失败
FULL_TESTS=通过/失败
BUILD=PASS/FAIL
BLOCKING_FINDINGS=最多3项
HIGH_FINDINGS=最多3项
REMEDIATION_REQUIRED=YES/NO
NEXT_GATE=USER_MANUAL_ACCEPTANCE/MOX_REMEDIATION
REVIEW_DOC=docs/enterprise/reviews/mox-canonical-v3-independent-review.md
CODE_CHANGED=NO
```

输出后立即停止。