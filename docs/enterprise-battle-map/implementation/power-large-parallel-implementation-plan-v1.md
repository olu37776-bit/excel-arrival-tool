# 企业作战地图：电力与大企并行实施计划 V1

**状态：CURRENT IMPLEMENTATION PLAN**  
**任务分支：`task/enterprise-power-large`**  
**长期集成分支：`feature/enterprise-battle-map`**  
**Migration预留：电力 `V37.sql`；大企 `V38.sql`**  
**实施性质：两个缺失模块的完整建设；共用机制、独立契约与持久化**

---

## 1. 必读 Authority

按顺序读取：

1. `enterprise-contract-architecture-v3.md`；
2. `parallel-module-execution-v1.md`；
3. `power-canonical-authority-v2.md`；
4. `large-enterprise-canonical-authority-v2.md`；
5. 本地“企业作战地图基表”的电力 Sheet 与 `大企（油气矿、广电等）` Sheet；
6. 当前 MOX Contract/Projection/Metric和页面结构，仅参考机制；
7. 当前电力/大企基础路由骨架、API、`database.js`、SQLite和测试。

字段业务分别以电力/大企 Authority 为准；目录、Contract形态、三个Section、数据库和测试治理以共享架构 V3 为准。

---

## 2. 分支与边界

从冻结的 `feature/enterprise-battle-map`同一 `BASE_HEAD`创建：

```text
task/enterprise-power-large
```

使用独立 worktree/环境。不得在长期集成分支直接工作。

本任务只处理电力和大企。禁止修改 TOB、ISP、MOX业务Contract和企业首页。

两个模块可以共用已经存在的页面外壳、Projection、Metric Engine、客户关系和Heatmap组件，但必须分别拥有：

- 独立 Field Contract；
- 独立 Metric Contract；
- 独立页面/route身份；
- 独立 API；
- 独立数据库表；
- 独立 Migration；
- 独立测试。

禁止建立把电力和大企字段混在一起的联合业务Schema。

---

## 3. 目标页面

电力：

```text
电力专项
→ 空间洞察 / 当年项目 / 空间拓展三个并列统计模块
→ 电力Heatmap
→ 新增 / 表格 / 编辑
```

大企：

```text
大企专项
→ 空间洞察 / 当年项目 / 空间拓展三个并列统计模块
→ 大企Heatmap
→ 新增 / 表格 / 编辑
```

新增与编辑都使用三个同级 Section：

```text
客户信息 ｜ 业务格局 ｜ 作战情况
```

专项定义文案尚未确认时不得自行编写业务口号，可使用现有统一空状态或仅显示专项标题。

Heatmap业务规则未冻结时使用共享组件的安全空状态，不生成假数据，不阻塞其余页面建设。

---

## 4. Contract目标

建立：

```text
src/config/enterprise/power-field-contract.js
src/config/enterprise/power-metric-contract.js
src/config/enterprise/large-enterprise-field-contract.js
src/config/enterprise/large-enterprise-metric-contract.js
```

表格、新增、编辑必须从各自 Field Contract 派生；统计和点击筛选必须从各自 Metric Contract 同一 `where`派生。

共享内核默认只读。架构级缺口返回 `SHARED_BLOCKER`，不得在本任务中自行建立第二套共享引擎。

---

## 5. 电力字段实施

电力字段集合、canonical key、顺序和枚举以 `power-canonical-authority-v2.md`为准，目标总数为 28。

关键门禁：

- 客户信息：地区部、代表处、国家、客户ID、客户名称、行业；无客户类别；
- 业务格局包含：微波应用场景、解决方案、现网微波链路数量（跳）、我司份额（%）、变电站数量（个）、变电站光纤化率、电力塔数量（个）、友商空间（跳）；
- 微波应用场景：输变电站微波互连、输电智能巡检、无线回传；
- 解决方案：licensed微波、unlicensed微波；
- 作战情况、客户关系、作战进展、重点项目筛选和9项Metric按Authority；
- table/create/edit目标外字段均为0；
- 所有Excel字段必须写实列、Row2、Row3和Validation。

---

## 6. 大企字段实施

大企字段集合、canonical key、顺序和枚举以 `large-enterprise-canonical-authority-v2.md`为准，目标总数为 26。

关键门禁：

- 客户信息：地区部、代表处、国家、客户ID、客户名称、行业；无客户类别；
- 业务格局包含：微波应用场景、解决方案、现网微波链路数量（跳）、我司份额（%）、友商空间（跳）、油气矿井数量（个）；
- `油气矿井数量（个）`保持一个完整字段，不拆成多列；
- 微波应用场景：骨干汇聚微波互联、2B专线、基站回传；
- 解决方案：licensed微波、unlicensed微波；
- 作战情况、客户关系、作战进展、重点项目筛选和9项Metric按Authority；
- table/create/edit目标外字段均为0；
- 必须读取并使用 Excel Sheet 精确名称与列信息。

---

## 7. 客户关系

两个模块均保存 `customer_id`。

要求：

- 复用地区部、代表处等现有客户联动；
- 新增最终定位唯一客户并自动取得 `customer_id`；
- 客户ID不可手填；
- 同名客户不得取第一条；
- 编辑客户信息全部只读；
- 编辑业务字段不得改变 `customer_id`；
- API校验客户真实存在；
- 行业通过客户表关系读取，不在业务表建立重复客户属性Authority。

如果当前路由骨架没有客户数据链路，复用共享客户服务，不复制第二套查询实现。

---

## 8. 数据库与 V37/V38

电力使用 `V37.sql`，大企使用 `V38.sql`。

每个Migration必须独立：

- 注册到 `database.js`真实Migration链；
- 成功后写 `_migrations`；
- 在事务中执行，失败回滚；
- 新建库Schema与旧库连续升级结果一致；
- 创建最终目标表、索引和必要约束；
- 同步CRUD、字段映射、Validation和API；
- 具备执行、回滚、幂等和最终Schema测试。

不得把两个模块塞入一个无法独立判定状态的Migration。

如果V37或V38已占用，停止并返回 `MIGRATION_VERSION_CONFLICT`。

---

## 9. Metric与点击筛选

两个模块各自建立9项Metric：

- 已孵化、孵化中；
- 当年项目总项目数、已签单、推进中、高风险；
- 可参与总空间、空间拓展总项目、已落地。

要求：

- 同一 `where`同时用于统计与点击表格筛选；
- 当前不增加年份过滤；
- `annual.total`与`expansion.total`不同；
- 高风险使用“推进中 AND 高风险”；
- 可参与总空间对符合条件记录的 `overallSpaceMusd`求和；
- 九个指标全部可点击；
- 点击只改变本模块表格，不串到另一个模块；
- 顶部统计不因自身筛选错误重算；
- 三个大模块并列、文字居中，不拆成9张顶级卡。

---

## 10. 页面与状态隔离

电力和大企必须具有独立：

- route name/path；
- active menu identity；
- 数据请求；
- loading/error状态；
- active metric；
- 表格筛选；
- 新增/编辑状态；
- Field/Metric Contract。

切换页面时不得：

- 复用另一模块记录；
- 残留另一模块active metric；
- 将新增记录写入错误表；
- 将编辑请求发送到错误API；
- 将两个页面都指向同一Contract或同一数据库表。

---

## 11. 测试治理

代码与测试同轮完成。

电力至少覆盖：

- 28字段、三个Section、精确顺序和Excel Authority；
- table/create/edit同一Contract；
- 国家和行业存在、客户类别不存在；
- 应用场景、解决方案、单位和百分比口径；
- customer_id；
- focusProject筛选；
- 作战进展特殊编辑器；
- 9个Metric和点击筛选；
- V37、新建库和升级库；
- Heatmap空状态/生命周期；
- route、页面和CRUD。

大企至少覆盖：

- 26字段、三个Section、精确顺序和Excel Authority；
- table/create/edit同一Contract；
- 国家和行业存在、客户类别不存在；
- 油气矿井数量保持单字段；
- 应用场景、解决方案、单位和百分比口径；
- customer_id；
- focusProject筛选；
- 作战进展特殊编辑器；
- 9个Metric和点击筛选；
- V38、新建库和升级库；
- Heatmap空状态/生命周期；
- route、页面和CRUD。

交叉隔离测试必须覆盖：

- 两模块Contract、API、DB表、active metric和表格数据不串；
- V37失败不错误登记V38，V38失败不破坏已完成V37；
- 电力新增不写入大企，大企新增不写入电力。

执行模块测试、企业相关测试、全量Vitest、build、lint/typecheck（如配置）。不得执行人工页面检查。

---

## 12. 实施报告与完成门槛

创建：

```text
docs/enterprise/implementations/power-large-implementation-report.md
```

分别记录电力和大企：字段数、Contract、API、数据库表、Migration、测试、未完成项；同时记录共享文件修改和交叉隔离验证。

只有以下全部满足才可 `IMPLEMENTED_NOT_VERIFIED`：

- 电力28字段与三处Projection正确；
- 大企26字段与三处Projection正确；
- 两模块API/DB映射、customer_id、9项Metric和点击筛选正确；
- V37/V38正确且连续升级通过；
- 页面/route/状态完全隔离；
- Heatmap安全空状态或现有明确规则正确；
- 测试和build通过；
- 未修改TOB、ISP、MOX业务Contract或企业首页；
- 已提交到 `task/enterprise-power-large`；
- 未合并、未审查。

最终等待统一集成和统一独立审查。
