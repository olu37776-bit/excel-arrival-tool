# 企业作战地图：并行模块实施与统一集成协议 V1

**状态：CURRENT EXECUTION AUTHORITY**  
**文档分支：`enterprise-battle-map-authority`**  
**长期本地集成分支：`feature/enterprise-battle-map`**  
**并行任务：TOB、ISP、电力+大企**  
**统一审查：三个任务全部集成后执行**

---

## 1. 目标

允许三个本地 Agent 同时实施：

1. TOB；
2. ISP；
3. 电力与大企。

并行只用于缩短建设时间，不改变以下长期规则：

- `feature/enterprise-battle-map`仍是唯一长期建设与集成分支；
- 各模块必须使用同一套共享 Contract 机制；
- 每个模块保留独立 Field Contract 与 Metric Contract；
- 三个任务完成后先统一集成，再统一独立审查；
- 不允许多个 Agent 在同一个工作树中同时切换分支或修改文件。

---

## 2. 并行隔离方式

在启动三个 Agent 前，冻结 `feature/enterprise-battle-map`，不得再直接向该分支写入。

三个 Agent 必须从同一个基线提交创建临时任务分支：

```text
task/enterprise-tob
task/enterprise-isp
task/enterprise-power-large
```

推荐使用独立 Git worktree：

```text
../battle-map-tob
../battle-map-isp
../battle-map-power-large
```

每个 Agent 必须记录：

```text
BASE_HEAD=<feature/enterprise-battle-map启动并行任务时的SHA>
TASK_BRANCH=<自己的任务分支>
```

禁止：

- 三个 Agent 共用同一工作目录；
- 在 `feature/enterprise-battle-map`上直接并行提交；
- 从不同基线开始；
- Agent 自行 merge 其他任务分支；
- Agent 自行 rebase、force push、reset其他任务成果。

如任务已运行在三个完全独立 clone/沙箱中，可不使用 worktree，但仍须使用对应任务分支，并以同一 `BASE_HEAD`为起点。

---

## 3. Authority

所有任务必须读取：

1. `enterprise-contract-architecture-v3.md`；
2. 当前模块 Canonical Authority；
3. 当前模块 Implementation Plan；
4. 本地“企业作战地图基表”对应 Sheet；
5. 当前 MOX 实现，仅作为契约机制和页面结构参考；
6. 当前真实代码、API、`database.js`、SQLite与测试。

优先级：

```text
当前模块 Canonical Authority
→ 对应 Excel Sheet 精确来源
→ 用户最新明确修正
→ 共享架构 Authority
→ 当前代码/API/数据库现状
→ 本地旧文档、旧Schema和旧配置
```

MOX 尚未最终 VERIFIED 时：

- 可以参考其 Contract、Projection、Metric Engine、客户关系和页面结构；
- 不得无条件复制 MOX 当前缺陷、旧字段、Migration编号或模块业务字段；
- 模块 Authority 与 MOX 当前实现冲突时，以当前模块 Authority 为准。

---

## 4. 共享文件写入规则

以下属于共享内核：

```text
src/config/enterprise/field-contract.js
src/config/enterprise/field-projections.js
src/config/enterprise/contract-validator.js
src/config/enterprise/metric-engine.js
src/config/enterprise/option-sets.js
共享企业页面/表单基础组件
共享客户查询服务
共享Heatmap组件
server.js
database.js
```

### 4.1 默认规则

三个并行 Agent 默认只读共享内核，优先新增或修改自己的模块文件。

不得各自在任务分支中重构出不同版本的共享引擎。

### 4.2 允许的最小共享修改

只有当前模块无法在既有共享能力上实现 Authority 时，才允许最小修改共享文件，并必须：

- 在实施报告中列出 `SHARED_FILES_CHANGED`；
- 说明为什么不能只改模块文件；
- 不改变其他模块行为；
- 添加共享回归测试；
- 不格式化整个共享文件；
- 不顺带清理无关代码。

### 4.3 共享能力缺口

如果需要架构级新能力，且三个 Agent 可能采取不同方案：

- 不得各自实现；
- 返回 `SHARED_BLOCKER`；
- 由后续统一集成 Agent设计一次并应用。

---

## 5. 模块文件边界

推荐模块契约路径：

```text
src/config/enterprise/tob-field-contract.js
src/config/enterprise/tob-metric-contract.js
src/config/enterprise/isp-field-contract.js
src/config/enterprise/isp-metric-contract.js
src/config/enterprise/power-field-contract.js
src/config/enterprise/power-metric-contract.js
src/config/enterprise/large-enterprise-field-contract.js
src/config/enterprise/large-enterprise-metric-contract.js
```

各 Agent 只修改自己模块的：

- Contract；
- 页面；
- 表格；
- 新增与编辑；
- API route/service；
- `database.js`模块分支；
- Migration；
- 模块测试；
- 模块实施报告。

禁止修改其他并行模块的 Contract、页面、API、数据库表或测试。

---

## 6. Migration编号预留

为防止并行冲突，预留：

```text
TOB：V35.sql
ISP：V36.sql
电力：V37.sql
大企：V38.sql
```

规则：

- 使用仓库现有实际命名大小写和目录；
- 如果预留编号已存在或被其他未集成工作占用，不得自行改用新编号；
- 返回 `MIGRATION_VERSION_CONFLICT`，等待统一协调；
- 每个 Migration 必须注册到 `database.js`，成功后由 `_migrations`登记；
- Migration失败必须回滚；
- 新建库与升级库最终Schema一致；
- 不允许不同任务共用同一版本文件。

电力与大企由同一个 Agent 实施，但必须使用两个独立 Migration，避免一个模块失败导致另一个模块状态不清。

---

## 7. database.js并行修改纪律

`database.js`是共享高冲突文件。各 Agent只允许：

- 添加当前模块 Migration注册；
- 添加或修正当前模块建表、CRUD、字段映射、Validation；
- 删除当前模块的旧活动字段分支；
- 不移动或重排其他模块代码；
- 不全文件格式化；
- 不修改 MOX 或其他并行模块逻辑。

统一集成时由集成 Agent逐项合并三个任务对 `database.js`的改动，并重新执行所有数据库测试。

---

## 8. 测试与文档冲突控制

每个任务必须：

- 新建或修改模块专属测试；
- 不修改其他模块测试；
- 仅在确有必要时修改共享测试；
- 删除/重建当前模块的过期测试和死代码；
- 不更新共享 `enterprise-status.md`，避免并行冲突；
- 创建独立实施报告：

```text
docs/enterprise/implementations/tob-implementation-report.md
docs/enterprise/implementations/isp-implementation-report.md
docs/enterprise/implementations/power-large-implementation-report.md
```

报告必须记录：基线SHA、任务分支、changed files、Migration、共享文件修改、测试、build、阻塞和未完成项。

---

## 9. 每个任务完成门槛

每个 Agent 必须在同一轮完成：

```text
代码
→ 模块测试
→ 数据库/Migration测试
→ 全量Vitest
→ build
→ 实施报告
→ 提交任务分支
→ 停止
```

不做独立审查，不合并到长期分支，不自动开始下一模块。

如果全量测试因其他并行分支尚未集成而无法覆盖未来组合状态，仍须保证：

- 自己任务分支全量测试通过；
- 当前基线已有功能无回归；
- 实施报告明确组合风险。

---

## 10. 统一集成顺序

三个任务完成后，由单独的 Integration Agent 在 `feature/enterprise-battle-map`执行：

1. 确认三个任务使用相同 `BASE_HEAD`；
2. 依次集成 TOB、ISP、电力+大企；
3. 手工解析共享文件冲突，不使用“ours/theirs”整体覆盖；
4. 合并 `database.js`的四个 Migration注册和各模块映射；
5. 校验 V35/V36/V37/V38 顺序；
6. 运行新建库和旧库连续升级；
7. 运行 Contract Validator；
8. 运行所有企业模块测试、全量Vitest、build；
9. 清查重复共享代码、重复Contract和路径污染；
10. 创建统一集成报告；
11. 停止并进入统一独立审查。

统一审查之前，任何模块都只能标记 `IMPLEMENTED_NOT_VERIFIED`。

---

## 11. 统一审查范围

后续统一独立审查必须覆盖：

- TOB、ISP、电力、大企各自字段、Section和顺序；
- 表格/新增/编辑是否消费各自唯一Contract；
- `customer_id`关系；
- API/`database.js`/SQLite映射；
- V35—V38 Migration与幂等；
- 9项Metric和点击筛选；
- 专项、统计卡、Heatmap与表格页面结构；
- 模块之间是否串字段、串状态、串数据；
- 共享引擎是否只存在一份；
- 并行合并是否引入死代码、重复测试或旧配置。

用户人工页面验收在统一自动审查之后执行。

---

## 12. 并行阶段禁止事项

- 不实施企业首页最终数据绑定；
- 不建设首页Heatmap；
- 不修改MOX业务Contract；
- 不清理非企业模块死代码；
- 不建立全企业超级Schema；
- 不复制MOX字段到其他模块；
- 不在多个任务分支中分别改造同一个共享引擎；
- 不在任务完成后自动合并或审查。
