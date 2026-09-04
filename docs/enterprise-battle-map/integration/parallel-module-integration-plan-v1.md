# 企业作战地图：并行模块统一集成计划 V1

**状态：CURRENT INTEGRATION AUTHORITY**  
**文档分支：`enterprise-battle-map-authority`**  
**长期集成分支：`feature/enterprise-battle-map`**  
**待集成任务分支：`task/enterprise-tob`、`task/enterprise-isp`、`task/enterprise-power-large`**  
**集成结果状态：`INTEGRATED_NOT_VERIFIED`**  
**下一门禁：统一独立审查**

---

## 1. 目标与边界

本计划用于将三个并行实施分支按受控顺序集成回长期建设分支：

```text
task/enterprise-tob
→ task/enterprise-isp
→ task/enterprise-power-large
→ feature/enterprise-battle-map
```

本轮是 **Integration**，不是模块重新设计，也不是独立审查。

允许：

- 合并三个任务分支；
- 解析共享文件和数据库 Migration 冲突；
- 做仅由合并引起的最小集成修复；
- 运行模块、数据库、企业联合和全量自动验证；
- 创建集成报告并更新状态。

禁止：

- 修改各模块已经冻结的业务字段 Authority；
- 重新设计 TOB、ISP、电力或大企；
- 开始企业首页最终数据绑定；
- 建设首页 Heatmap；
- 修改 MOX 业务 Contract；
- 借集成清理非企业模块代码；
- 为通过测试删除仍然有效的测试；
- 在集成完成后自行宣布 VERIFIED；
- 在同一 Agent 中继续执行独立审查。

---

## 2. 必读 Authority

Integration Agent 开始前必须完整读取：

1. 共享架构：`enterprise-contract-architecture-v3.md`；
2. 并行协议：`implementation/parallel-module-execution-v1.md`；
3. MOX 当前 Authority：`mox-canonical-authority-v4.md`；
4. TOB Authority 与实施计划；
5. ISP Authority 与实施计划；
6. 电力 Authority；
7. 大企 Authority；
8. 电力+大企联合实施计划；
9. 三个任务分支各自的 implementation report；
10. 当前 `feature/enterprise-battle-map` 代码、测试、`database.js`、Migration 和状态文档。

Authority 顺序：

```text
模块 Canonical Authority
→ 对应 Excel Sheet 精确来源
→ 共享架构与并行协议
→ 当前任务分支实现和实施报告
→ 当前长期分支代码
→ 本地旧文档、旧 Schema 和旧配置
```

集成 Agent 不得根据冲突方便程度改写业务 Authority。

---

## 3. 集成前置门禁

### 3.1 工作树与分支

先执行并记录：

```text
git worktree list
git branch --show-current
git status --short
git log -1 --oneline
git diff --stat
```

要求：

- 使用一个单独、干净的集成工作树；
- 该工作树必须 checkout `feature/enterprise-battle-map`；
- 不得在 TOB、ISP 或电力+大企任务 worktree 中执行集成；
- 当前工作树不得存在未提交修改；
- 不得存在正在进行中的 merge、rebase、cherry-pick 或 revert；
- 不得使用 `reset --hard`、`clean`、强制 checkout 或 force push。

如长期分支工作树不干净，返回 `BLOCKED_DIRTY_INTEGRATION_WORKTREE`，不得继续。

### 3.2 三个任务分支必须存在并已提交

检查：

```text
git show-ref --verify refs/heads/task/enterprise-tob
git show-ref --verify refs/heads/task/enterprise-isp
git show-ref --verify refs/heads/task/enterprise-power-large
```

每个任务分支必须：

- 没有依赖未提交工作树内容；
- 包含对应 implementation report；
- 报告状态为 `IMPLEMENTED_NOT_VERIFIED`；
- 记录 `BASE_HEAD`、任务提交、Migration、测试、build、共享文件改动和 blocker；
- 模块测试通过；
- 任务分支全量测试没有本任务引入失败；
- build 通过；
- 没有未解决 blocker。

如任务分支只有部分完成、测试失败或报告缺失，不得先合并后再猜测修复，返回对应 blocker。

### 3.3 基线一致性

从三个 implementation report 读取 `BASE_HEAD`。

必须确认：

```text
TOB_BASE_HEAD = ISP_BASE_HEAD = POWER_LARGE_BASE_HEAD
```

并执行：

```text
git merge-base --is-ancestor <BASE_HEAD> task/enterprise-tob
git merge-base --is-ancestor <BASE_HEAD> task/enterprise-isp
git merge-base --is-ancestor <BASE_HEAD> task/enterprise-power-large
git merge-base --is-ancestor <BASE_HEAD> feature/enterprise-battle-map
```

说明：并行期间长期分支可能因经过批准的 MOX 修复而前进。只要共同 `BASE_HEAD` 仍是当前长期分支祖先，不得重置长期分支；应在当前最新长期分支 HEAD 上集成并记录 `BASE_DRIFT`。

以下情况必须阻塞：

- 三个任务使用不同 BASE_HEAD；
- 任一任务分支不是该 BASE_HEAD 的后代；
- 当前长期分支不是该 BASE_HEAD 的后代；
- Agent 试图通过 rebase 或 reset 隐藏基线差异。

### 3.4 记录集成快照

记录：

```text
COMMON_BASE_HEAD=
PRE_INTEGRATION_HEAD=
TOB_TIP=
ISP_TIP=
POWER_LARGE_TIP=
```

这些值必须写入集成报告。

---

## 4. 集成策略

采用顺序 merge，不假设每个任务只有一个提交。

统一使用：

```text
git merge --no-ff --no-commit <task-branch>
```

每个任务的流程固定为：

```text
开始 merge
→ 解析冲突
→ 检查 changed files
→ 运行当前模块和集成烟测
→ 通过后提交 merge commit
→ 再进入下一任务
```

禁止：

- 只 cherry-pick implementation report 中的一条提交而遗漏任务分支其他必要提交；
- 对共享文件直接采用整体 `ours` 或 `theirs`；
- 让后合入模块覆盖先合入模块；
- 在冲突未解释时提交 merge；
- 删除测试来消除冲突。

如果当前分支 merge 无法安全解析：

```text
git merge --abort
```

停止并报告。不得留下半合并状态。

---

## 5. 固定集成顺序

### 5.1 第一阶段：TOB

执行：

```text
git merge --no-ff --no-commit task/enterprise-tob
```

必须确认：

- TOB Field Contract 和 Metric Contract进入最终标准目录；
- TOB 表格、新增、编辑、API、数据库和测试均被包含；
- V35 存在且只注册一次；
- V35 不覆盖或跳过 V34；
- MOX 文件没有被无授权覆盖；
- TOB implementation report保留。

冲突解析后至少运行：

- TOB Contract/Projection测试；
- TOB CRUD/API测试；
- V35 Migration测试；
- MOX关键回归测试；
- 企业路由烟测；
- build或项目规定的快速构建门禁。

通过后提交：

```text
merge(enterprise): integrate TOB module
```

记录 `TOB_MERGE_COMMIT`。

### 5.2 第二阶段：ISP

执行：

```text
git merge --no-ff --no-commit task/enterprise-isp
```

必须确认：

- ISP Contract、UI、API、数据库和测试完整；
- V36 存在且只注册一次；
- `database.js` 同时保留 V34、V35、V36；
- ISP 不覆盖 TOB 或 MOX Contract；
- ISP implementation report保留。

冲突解析后至少运行：

- ISP Contract/Projection测试；
- ISP CRUD/API测试；
- V35→V36连续 Migration烟测；
- TOB和MOX关键回归测试；
- 企业路由烟测；
- build快速门禁。

通过后提交：

```text
merge(enterprise): integrate ISP module
```

记录 `ISP_MERGE_COMMIT`。

### 5.3 第三阶段：电力 + 大企

执行：

```text
git merge --no-ff --no-commit task/enterprise-power-large
```

必须确认：

- 电力和大企拥有两份独立 Field Contract；
- 电力和大企拥有两份独立 Metric Contract；
- 两个模块拥有独立页面、API、数据库表和测试；
- 不存在联合业务 Schema；
- V37 和 V38 是两个独立 Migration；
- V37、V38各自只注册一次；
- V38不能代替或吞并V37；
- 两个模块之间不存在字段、store、API或表名串用；
- 联合 implementation report保留。

冲突解析后至少运行：

- 电力模块测试；
- 大企模块测试；
- 电力/大企隔离测试；
- V35→V36→V37→V38连续 Migration烟测；
- MOX、TOB、ISP关键回归测试；
- 企业路由烟测；
- build快速门禁。

通过后提交：

```text
merge(enterprise): integrate power and large-enterprise modules
```

记录 `POWER_LARGE_MERGE_COMMIT`。

---

## 6. 冲突处理规则

### 6.1 `src/config/enterprise`

目标：共享内核只有一份，各模块 Contract 相互独立。

必须保留：

- 一份共享 Field Contract 类型；
- 一份 Projection实现；
- 一份 Contract Validator；
- 一份 Metric Engine；
- 一份 option sets 注册机制；
- 每个模块自己的一份 Field Contract和Metric Contract。

禁止：

- `field-contract-v2.js`、`field-contract-new.js`等重复共享实现；
- 同时保留旧Schema与新Contract；
- 模块自行复制Validator或Metric Engine；
- 后合入分支覆盖已集成模块注册；
- 为某模块在共享引擎中硬编码字段名。

如果不同任务对共享引擎提出互不兼容的设计，集成 Agent不得任意选一套，应返回 `SHARED_ARCHITECTURE_CONFLICT`。

### 6.2 `option-sets`

- 合并各模块需要的枚举；
- 同义选项只保留一份共享定义；
- 模块特有枚举使用模块级名称，不能覆盖其他模块；
- 不允许因合并导致枚举值变化；
- 不允许从历史 distinct values自动补选项。

### 6.3 `contract-validator`

- 保留已有MOX门禁；
- 追加TOB、ISP、电力、大企所需通用校验；
- 不得为了让新模块通过而放宽原有唯一性、映射完整性、order或禁止字段门禁；
- Validator不得在Vue每次render中执行。

### 6.4 `field-projections`和共享表单组件

- 必须保持模块无关；
- Section、order、visible、editable、control均来自模块Contract；
- 不允许共享组件写死 `if module === tob/isp/...` 的字段清单；
- 模块特殊行为通过Contract中的behavior/editorId或注册器接入；
- 合并后MOX现有行为不得回归。

### 6.5 `metric-engine`

- 保持单一引擎；
- 统计计算与点击筛选使用同一个`where`；
- 不允许每个模块复制一套Metric Engine；
- 不允许合并时把一个模块的记录集合传入另一个模块；
- active metric状态必须按页面/模块隔离。

### 6.6 `database.js`

这是最高风险共享文件，禁止整体选择 `ours`或`theirs`。

必须逐项组合：

1. 保留当前 MOX/V34 注册和MOX最终映射；
2. 加入TOB/V35；
3. 加入ISP/V36；
4. 加入电力/V37；
5. 加入大企/V38；
6. 保留各模块独立建表、CRUD、字段映射和Validation；
7. 不移动或删除无关模块逻辑；
8. 不重复注册Migration；
9. 不改变既有Migration编号含义；
10. 不因合并重排旧Migration历史。

最终Migration顺序必须为：

```text
... → V34 → V35 → V36 → V37 → V38
```

### 6.7 API与`server.js`

- 每个模块API route必须唯一；
- 不允许后注册路由覆盖前一个模块；
- 不允许不同模块调用同一错误service或数据库表；
- 客户查询服务可共享，但返回/保存必须保持模块记录隔离；
- `ISP&大企`导航/父入口继续进入ISP，不得回到企业首页；
- 不修改企业首页最终数据口径。

### 6.8 页面、store和筛选状态

- 各模块页面使用各自Field/Metric Contract；
- 表格、新增、编辑不得读取其他模块Contract；
- Pinia/store状态必须按模块或页面隔离；
- 统计点击筛选不得影响其他页面；
- 一个模块切换active metric时，不得改变另一模块active metric；
- 路由切换后不得残留上一个模块的表格筛选。

### 6.9 测试冲突

- 保留所有仍验证当前Authority的测试；
- 同名测试文件冲突时按模块拆分或合并真实覆盖，不得简单删除一方；
- 过期测试只能在有明确旧Authority证据时删除；
- 不得修改期望值去迎合错误代码；
- 不得复制生产配置后测试复制品；
- 不得以skip、only或注释测试作为集成完成方式。

### 6.10 依赖与lockfile

并行模块原则上不应引入新依赖。

如出现package或lockfile冲突：

- 先确认是否确有Authority授权的新依赖；
- 无授权依赖必须移除；
- 不升级无关包；
- 使用项目当前包管理器重新生成一致lockfile；
- 记录原因和验证结果。

---

## 7. 数据库联合门禁

所有数据库测试使用临时库、fixture或副本，不得修改真实业务数据库。

### 7.1 Migration注册

检查：

- V34、V35、V36、V37、V38均存在；
- 每个版本在`database.js`实际执行链中恰好注册一次；
- `_migrations`只在对应事务整体成功后登记；
- SQL文件名、注册版本号和`_migrations`记录一致；
- 不存在跳号、重复号或顺序错乱。

### 7.2 新建数据库

从空数据库执行当前初始化，确认：

- MOX、TOB、ISP、电力、大企最终表均存在；
- 每个表只包含自己的目标持久化列、`customer_id`、主键和必要技术列；
- Contract runtime映射中的DB列都存在；
- 没有Authority外旧业务列；
- 必要索引和约束存在；
- API CRUD可工作。

### 7.3 旧库连续升级

从仅完成到V34的基线数据库副本开始：

```text
V35 → V36 → V37 → V38
```

确认：

- 每个Migration顺序执行；
- 每一步事务成功后才登记；
- 数据搬迁不串模块；
- 旧字段按各模块Authority处理；
- 最终Schema与新建库一致；
- 原MOX数据无回归。

### 7.4 幂等

在已经完成V38的数据库上再次执行`init()`：

- V35—V38不得重复执行；
- `_migrations`不得重复记录；
- 不得重复建表、重复列或破坏数据；
- 应用可以正常启动。

### 7.5 回滚

使用现有Migration测试方式模拟中间失败，至少证明：

- 失败版本不写入`_migrations`；
- 该版本结构变更完整回滚；
- 之前已成功版本保持有效；
- 后续版本不会在前一版本失败时继续执行。

### 7.6 客户关系

- 各模块新增必须验证`customer_id`对应真实客户；
- 编辑其他字段不得改变`customer_id`；
- 同名客户不得默认取第一条；
- 当前不得借集成未经专项验证全局开启SQLite foreign keys；
- 即使运行时外键约束尚未全局启用，API仍必须阻止新无效引用。

---

## 8. Contract与页面联合门禁

### 8.1 单一共享内核

最终必须只有一份活动：

- FieldContract定义；
- Field Projection；
- Contract Validator；
- Metric Engine；
- option sets机制。

### 8.2 模块独立Contract

必须分别存在并相互隔离：

- MOX Field/Metric Contract；
- TOB Field/Metric Contract；
- ISP Field/Metric Contract；
- 电力 Field/Metric Contract；
- 大企 Field/Metric Contract。

不得出现全企业超级Field Schema或电力+大企联合业务Contract。

### 8.3 三处Projection

每个模块都必须满足：

```text
Field Contract
→ Table Projection
→ Create Projection
→ Edit Projection
```

表格、新增、编辑不得各自维护完整业务字段数组。

### 8.4 页面统一结构

各业务子页面应保持：

```text
模块专项
→ 三个并列统计大模块
→ 当前模块Heatmap
→ 新增 / 表格 / 编辑
```

- 三个统计大模块内部展示9个指标；
- 不得拆成9张顶级卡；
- 统计和点击筛选使用同一Metric Contract条件；
- 现有TOB/ISP Heatmap只做保留和防回归；
- 电力/大企Heatmap规则未冻结时使用安全空状态，不生成假数据。

### 8.5 模块隔离

至少验证：

- TOB只读取TOB Contract/API/表；
- ISP只读取ISP Contract/API/表；
- 电力只读取电力Contract/API/表；
- 大企只读取大企Contract/API/表；
- 模块切换不会显示上一个模块的数据；
- 统计筛选不会跨模块生效；
- 新增/编辑不会写入错误模块表；
- 字段名相同也不会复用错误DB列。

---

## 9. 每次merge后的验证

每合入一个任务分支后必须立即运行该模块测试和关键回归，不得等全部合完才发现首个模块已被覆盖。

最低门禁：

```text
TOB合入后：TOB + MOX关键测试 + Migration烟测
ISP合入后：ISP + TOB + MOX关键测试 + Migration烟测
电力/大企合入后：电力 + 大企 + 隔离测试 + MOX/TOB/ISP关键测试 + Migration烟测
```

如果当前merge引入失败：

- 在该merge尚未提交时修复冲突或`git merge --abort`；
- 不得把已知失败提交后继续合并下一模块；
- 不得把失败归因给后续统一审查。

---

## 10. 全部集成后的联合验证

所有分支合入后必须执行项目真实命令，至少覆盖：

1. 共享 Contract Validator；
2. MOX完整回归测试；
3. TOB完整模块测试；
4. ISP完整模块测试；
5. 电力完整模块测试；
6. 大企完整模块测试；
7. 电力/大企隔离测试；
8. 跨模块Contract和状态隔离测试；
9. 客户查询与`customer_id`测试；
10. V34—V38 Migration测试；
11. 新建库测试；
12. 旧库连续升级测试；
13. Migration幂等与回滚测试；
14. 企业导航和路由测试；
15. 9项Metric及点击筛选测试；
16. 企业模块测试集合；
17. 全量Vitest；
18. build；
19. lint/typecheck（如项目已配置）。

不得只运行新模块测试后宣布集成完成。

失败分类：

- `MERGE_CONFLICT_DEFECT`；
- `SHARED_KERNEL_CONFLICT`；
- `MIGRATION_CHAIN_DEFECT`；
- `CROSS_MODULE_LEAKAGE`；
- `MODULE_IMPLEMENTATION_DEFECT`；
- `PRE_EXISTING_BASELINE_FAILURE`；
- `TEST_ENVIRONMENT_FAILURE`。

如果失败属于模块业务实现缺陷，而不是简单集成冲突，记录为 blocker，不得在集成阶段擅自重新设计模块Authority。

---

## 11. 集成阶段允许的最小修复

允许：

- 解决import路径和名称冲突；
- 合并共享注册表；
- 合并`database.js`Migration注册与模块分支；
- 修复route/API重复注册；
- 修复因合并造成的测试fixture冲突；
- 补充跨模块隔离测试；
- 修复纯集成层的类型、lint或build错误。

不允许：

- 重写某模块字段Contract；
- 改变模块字段数量、顺序、枚举或统计规则；
- 替任务Agent完成未实现的大段业务功能；
- 重新设计共享架构；
- 删除有效测试；
- 修改企业首页；
- 处理非企业模块技术债。

若完成集成必须突破上述边界，返回`INTEGRATION_SCOPE_BLOCKER`并停止。

---

## 12. 集成报告与状态

创建：

```text
docs/enterprise/integrations/parallel-modules-integration-report.md
```

报告至少包含：

1. COMMON_BASE_HEAD；
2. PRE_INTEGRATION_HEAD；
3. 三个任务分支TIP；
4. 三个任务implementation report路径；
5. merge顺序与merge commit；
6. BASE_DRIFT；
7. changed files汇总；
8. 共享文件冲突与解析；
9. `database.js`最终注册；
10. V35—V38状态；
11. 新库/升级库/幂等/回滚结果；
12. Contract与模块隔离结果；
13. 每阶段测试；
14. 最终全量测试、build、lint/typecheck；
15. 未解决blocker和风险；
16. 最终状态。

更新：

```text
docs/enterprise/enterprise-status.md
```

集成成功后只能标记：

```text
INTEGRATED_NOT_VERIFIED
```

下一步必须为：

```text
ENTERPRISE_MODULES_UNIFIED_INDEPENDENT_REVIEW
```

不得标记任一新模块为VERIFIED。

不得删除三个任务分支或worktree，至少保留到统一独立审查通过。

---

## 13. 完成判定

### COMPLETE

仅当以下全部满足：

- 三个任务分支使用同一BASE_HEAD；
- 三个任务全部按顺序合入；
- 所有merge冲突已受控解析；
- 共享内核只有一份；
- 各模块Contract相互独立；
- V35、V36、V37、V38均存在、注册唯一、顺序正确；
- 新建库和升级库最终Schema一致；
- Migration幂等和回滚测试通过；
- 模块之间无字段、状态、API或数据库串用；
- MOX无集成回归；
- 模块测试、企业测试、全量测试和build通过；
- 集成报告和状态文档完成；
- 没有进入独立审查或企业首页建设。

### PARTIAL

仅部分任务合入或联合验证尚未完成。必须明确停在哪一步，不得继续宣称整体已集成。

### BLOCKED

存在不同BASE_HEAD、未完成任务、共享架构冲突、Migration版本冲突、无法安全解决的数据库或业务冲突。

---

## 14. 最终短回执

Integration Agent 最终只返回：

```text
ENTERPRISE PARALLEL INTEGRATION COMPLETE/PARTIAL/BLOCKED
COMMON_BASE_HEAD=SHA
PRE_INTEGRATION_HEAD=SHA
TOB_TIP=SHA
ISP_TIP=SHA
POWER_LARGE_TIP=SHA
TOB_MERGED=YES/NO
ISP_MERGED=YES/NO
POWER_LARGE_MERGED=YES/NO
MERGE_COMMITS=TOB_SHA/ISP_SHA/POWER_LARGE_SHA
BASE_DRIFT=NONE或提交数量
SHARED_CONFLICTS=数量
DATABASE_JS=PASS/PARTIAL/FAIL
MIGRATIONS=V35状态/V36状态/V37状态/V38状态
FRESH_DB=PASS/FAIL
UPGRADE_DB=PASS/FAIL
MIGRATION_IDEMPOTENCY=PASS/FAIL
CROSS_MODULE_ISOLATION=PASS/FAIL
MOX_REGRESSION=NO/YES
ENTERPRISE_TESTS=通过/失败
FULL_TESTS=通过/失败
BUILD=PASS/FAIL
LINT_TYPECHECK=PASS/FAIL/NOT_CONFIGURED
INTEGRATION_REPORT=路径
STATUS=INTEGRATED_NOT_VERIFIED/PARTIAL/BLOCKED
BLOCKERS=NONE或最多3项
NEXT=ENTERPRISE_MODULES_UNIFIED_INDEPENDENT_REVIEW
REVIEW_STARTED=NO
```

完成后立即停止。