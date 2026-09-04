# 企业作战地图：并行模块合并正确性独立审查 V1

**状态：CURRENT REVIEW AUTHORITY**  
**审查对象：`D:\BattleMap\battle-map` 中 `feature/enterprise-battle-map` 的合并后 HEAD**  
**审查阶段：第一层 Merge Integrity Review**  
**后续阶段：企业模块统一 Contract / DB / UI / Metric 独立审查**  
**审查性质：只读，不实施修复**

---

## 1. 目标

本轮只回答一个问题：

> TOB、ISP、电力、大企三个并行任务，是否完整、无覆盖、无漏项地集成到了长期分支？

本轮不重新审查每个模块全部业务字段，不重新定义需求，也不进行页面人工验收。

只有 Merge Integrity Review 通过后，才进入第二层统一业务/契约审查。

---

## 2. 固定本地路径

必须使用以下真实路径：

```text
长期集成工作树：D:\BattleMap\battle-map
TOB worktree：D:\BattleMap\tob-worktree
ISP worktree：D:\BattleMap\battle-mao-isp
电力+大企 worktree：D:\BattleMap\power-large-task
```

对应分支：

```text
D:\BattleMap\battle-map      → feature/enterprise-battle-map
D:\BattleMap\tob-worktree    → task/enterprise-tob
D:\BattleMap\battle-mao-isp  → task/enterprise-isp
D:\BattleMap\power-large-task→ task/enterprise-power-large
```

不得重命名、移动或重新创建 worktree。

---

## 3. 审查 Authority

开始前必须读取：

1. `enterprise-contract-architecture-v3.md`；
2. `implementation/parallel-module-execution-v1.md`；
3. `integration/parallel-module-integration-plan-v1.md`；
4. `integration/local-worktree-layout-v1.md`；
5. 三个任务分支 implementation report；
6. 集成报告 `docs/enterprise/integrations/parallel-modules-integration-report.md`；
7. 当前合并后代码、测试、Migration 和 Git 历史。

本轮不以本地旧需求文档作为 Authority。

---

## 4. Git 合并完整性

在 `D:\BattleMap\battle-map` 中记录：

```powershell
git branch --show-current
git status --short
git log --graph --decorate --oneline --all -80
git worktree list --porcelain
```

必须确认：

- 当前分支是 `feature/enterprise-battle-map`；
- 工作树干净；
- 不存在未完成 merge/rebase/cherry-pick；
- 三个任务分支仍存在；
- 三个任务成果均已进入当前 HEAD 的祖先历史；
- 不存在只复制文件而未真正合并任务分支的情况。

分别验证：

```powershell
git merge-base --is-ancestor task/enterprise-tob feature/enterprise-battle-map
git merge-base --is-ancestor task/enterprise-isp feature/enterprise-battle-map
git merge-base --is-ancestor task/enterprise-power-large feature/enterprise-battle-map
```

三条都必须成功。

---

## 5. Merge Commit 与任务内容完整性

读取三个 implementation report 中的：

- `BASE_HEAD`；
- 最终任务 commit/tip；
- changed files；
- Migration；
- 共享文件修改；
- 测试结果；
- blocker。

逐个对比当前长期分支，确认：

### TOB

- TOB Field Contract存在；
- TOB Metric Contract存在；
- TOB页面、表格、新增、编辑相关实现存在；
- TOB API/DB实现存在；
- V35如任务报告要求则存在并注册；
- TOB测试存在；
- TOB implementation report存在。

### ISP

- ISP Field Contract存在；
- ISP Metric Contract存在；
- ISP页面、表格、新增、编辑相关实现存在；
- ISP API/DB实现存在；
- V36如任务报告要求则存在并注册；
- ISP测试存在；
- ISP implementation report存在。

### 电力 + 大企

- 电力和大企是两份独立 Field Contract；
- 电力和大企是两份独立 Metric Contract；
- 两个页面/路由/API/DB均存在；
- V37/V38如计划要求则分别存在并注册；
- 两模块测试存在；
- 联合 implementation report存在；
- 不存在把两个模块合成一张业务表或一份超级 Schema。

若任务分支有文件但长期分支缺失，记录 `MISSING_MERGED_ARTIFACT`。

---

## 6. 共享文件冲突审查

重点审查实际合并后的：

```text
src/config/enterprise/*
database.js
server.js / API route注册
共享表单/Projection/Validator/Metric Engine
option sets
企业路由
企业测试基础设施
```

必须确认：

1. 共享 Field Contract 内核只有一份；
2. Projection只有一份；
3. Validator只有一份；
4. Metric Engine只有一份；
5. 各模块 Contract独立存在；
6. 后合并模块没有覆盖先合并模块注册；
7. 没有产生 `*-new`、`*-v2`、`*-copy` 等重复共享实现；
8. 没有 `ours/theirs` 整体覆盖造成模块能力丢失；
9. 没有残留 Git 冲突标记：`<<<<<<<`、`=======`、`>>>>>>>`；
10. 共享组件没有写死某一个模块字段集合。

搜索整个企业相关范围的冲突标记和重复 Contract/Engine 文件。

---

## 7. Migration 合并完整性

重点验证：

```text
... → V34 → V35 → V36 → V37 → V38
```

检查：

- V34仍存在且未被覆盖；
- V35/V36/V37/V38与任务实施报告一致；
- 每个版本只注册一次；
- `database.js`中顺序正确；
- 没有跳号覆盖、重复编号或同一版本服务两个模块；
- `_migrations`机制仍被使用；
- 新建库Schema包含所有已集成模块；
- 连续升级路径能够从合并前数据库升级至当前；
- 失败回滚和重复启动幂等测试仍存在。

如果某任务报告写 `NOT_REQUIRED`，不得为了满足编号表强行创建空 Migration；必须核对实际任务报告。

---

## 8. 模块隔离烟测

本轮不做完整业务审查，但必须确认不存在明显串模块：

- TOB Contract不被ISP页面引用；
- ISP Contract不被电力页面引用；
- 电力和大企不共用同一业务表；
- API路由不指向错误模块service；
- store/activeMetric状态不跨页面串用；
- 一个模块新增/编辑不会调用另一个模块API；
- 企业导航中的TOB、ISP、电力、大企均指向自己的页面。

发现明显串模块属于 BLOCKING。

---

## 9. 测试合并完整性

检查三个任务分支的模块测试在长期分支中是否都存在，没有在冲突中被覆盖或删除。

必须重新运行：

- TOB模块测试；
- ISP模块测试；
- 电力模块测试；
- 大企模块测试；
- 电力/大企隔离测试；
- MOX关键回归测试；
- V34—V38 Migration测试；
- 企业路由测试；
- 全量Vitest；
- build；
- lint/typecheck（如项目配置）。

如果测试失败，区分：

- `MERGE_REGRESSION`；
- `PRE_EXISTING`；
- `TEST_ENVIRONMENT`。

Merge Review 不允许通过删除测试解决失败。

---

## 10. 集成报告一致性

检查：

```text
docs/enterprise/integrations/parallel-modules-integration-report.md
```

报告必须真实记录：

- 四个本地路径；
- `COMMON_BASE_HEAD`；
- `PRE_INTEGRATION_HEAD`；
- 三个任务TIP；
- 三个merge commit；
- `POST_INTEGRATION_HEAD`；
- 冲突文件；
- 冲突决策；
- V35—V38最终状态；
- 测试/build结果；
- 最终状态 `INTEGRATED_NOT_VERIFIED`。

报告与Git事实冲突时，以Git事实为准，并记录 finding。

---

## 11. Finding 分级

### BLOCKING

包括但不限于：

- 任一任务分支不是长期分支祖先；
- 任务分支有关键实现未进入长期分支；
- `database.js`丢失某模块Migration/CRUD/映射；
- Migration重复、覆盖或顺序错误；
- 共享Contract/Validator/Metric Engine出现两套活动实现；
- 模块明显串API、串表、串Contract；
- 合并后关键模块测试或build失败；
- 长期工作树仍存在未完成merge状态。

### HIGH

包括：

- implementation report与实际合并内容明显不一致；
- 某模块测试被合并冲突误删；
- 共享文件存在无必要大规模重写；
- 明显重复配置/死注册由合并产生；
- 路由指向错误页面但不影响构建。

### MEDIUM / LOW

仅限不影响进入下一层统一业务审查的问题。

---

## 12. 审查结果

结果只能是：

```text
PASS
PASS_WITH_NONBLOCKING_FINDINGS
BLOCKED
```

通过条件：

- 三个任务完整进入长期分支；
- 合并历史可信；
- 共享文件没有覆盖或重复实现；
- Migration链完整；
- 模块基本隔离；
- 合并后自动验证通过。

通过后：

```text
NEXT_GATE=ENTERPRISE_UNIFIED_INDEPENDENT_REVIEW
```

阻塞则：

```text
NEXT_GATE=INTEGRATION_REMEDIATION
```

本轮不得直接执行下一层审查。

---

## 13. 审查产物

创建：

```text
docs/enterprise/reviews/post-integration-merge-review.md
```

只记录审查证据和 finding，不修改生产代码。

最终短回执：

```text
POST-INTEGRATION MERGE REVIEW
RESULT=PASS/PASS_WITH_NONBLOCKING_FINDINGS/BLOCKED
REVIEWED_HEAD=SHA
TOB_MERGED=YES/NO
ISP_MERGED=YES/NO
POWER_LARGE_MERGED=YES/NO
MISSING_MERGED_ARTIFACTS=0或数量
SHARED_CORE=PASS/PARTIAL/FAIL
DUPLICATE_SHARED_IMPLEMENTATIONS=0或数量
MIGRATION_CHAIN=PASS/PARTIAL/FAIL
V34_V38_REGISTRATION=PASS/PARTIAL/FAIL
MODULE_ISOLATION=PASS/PARTIAL/FAIL
MERGE_REGRESSION_TESTS=PASS/FAIL
FULL_TESTS=通过/失败
BUILD=PASS/FAIL
BLOCKING_FINDINGS=最多3项
HIGH_FINDINGS=最多3项
REMEDIATION_REQUIRED=YES/NO
NEXT_GATE=ENTERPRISE_UNIFIED_INDEPENDENT_REVIEW/INTEGRATION_REMEDIATION
CODE_CHANGED=NO
```
