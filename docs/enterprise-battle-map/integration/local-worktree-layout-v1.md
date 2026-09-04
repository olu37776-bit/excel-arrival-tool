# 企业作战地图：本地 Worktree 路径与集成执行 Authority V1

**状态：CURRENT LOCAL EXECUTION AUTHORITY**  
**文档分支：`enterprise-battle-map-authority`**  
**适用环境：Windows，D 盘本地仓库**  
**配套集成计划：`parallel-module-integration-plan-v1.md`**

---

## 1. 已确认的本地目录

以下路径是当前真实目录，Integration Agent 不得自行改名、猜测或重新创建另一套 worktree：

| 角色 | 精确路径 | 预期分支 |
|---|---|---|
| 长期建设与统一集成工作树 | `D:\BattleMap\battle-map` | `feature/enterprise-battle-map` |
| TOB 任务 worktree | `D:\BattleMap\tob-worktree` | `task/enterprise-tob` |
| ISP 任务 worktree | `D:\BattleMap\battle-mao-isp` | `task/enterprise-isp` |
| 电力 + 大企任务 worktree | `D:\BattleMap\power-large-task` | `task/enterprise-power-large` |

特别注意：

- ISP 当前真实目录名是 `battle-mao-isp`；
- 不得擅自将其改成 `battle-map-isp`；
- 本地目录名与任务分支名不要求相同；
- 所有路径都直接位于 `D:\BattleMap` 根目录下；
- 统一集成只能在 `D:\BattleMap\battle-map` 中进行，不能在三个任务 worktree 中进行。

---

## 2. 集成前路径与分支核验

Integration Agent 开始时必须先执行：

```powershell
git -C "D:\BattleMap\battle-map" worktree list --porcelain

git -C "D:\BattleMap\battle-map" branch --show-current
git -C "D:\BattleMap\battle-map" status --short
git -C "D:\BattleMap\battle-map" log -1 --oneline

git -C "D:\BattleMap\tob-worktree" branch --show-current
git -C "D:\BattleMap\tob-worktree" status --short
git -C "D:\BattleMap\tob-worktree" log -1 --oneline

git -C "D:\BattleMap\battle-mao-isp" branch --show-current
git -C "D:\BattleMap\battle-mao-isp" status --short
git -C "D:\BattleMap\battle-mao-isp" log -1 --oneline

git -C "D:\BattleMap\power-large-task" branch --show-current
git -C "D:\BattleMap\power-large-task" status --short
git -C "D:\BattleMap\power-large-task" log -1 --oneline
```

预期结果：

```text
D:\BattleMap\battle-map          → feature/enterprise-battle-map
D:\BattleMap\tob-worktree        → task/enterprise-tob
D:\BattleMap\battle-mao-isp       → task/enterprise-isp
D:\BattleMap\power-large-task     → task/enterprise-power-large
```

如任一路径不存在、分支不符、存在未提交修改或处于 merge/rebase/cherry-pick 状态：

- 不得自行移动目录；
- 不得强制切换分支；
- 不得 reset、clean 或丢弃修改；
- 返回精确 blocker 并停止。

---

## 3. 工作树职责边界

### `D:\BattleMap\battle-map`

这是唯一长期建设和集成工作树。

只允许它承载：

- `feature/enterprise-battle-map`；
- 三个任务分支的顺序合并；
- 集成冲突处理；
- 联合数据库 Migration 验证；
- 企业模块联合测试；
- 全量 Vitest、build、lint/typecheck；
- 统一集成报告；
- 后续统一独立审查所针对的最终 HEAD。

### 三个任务 worktree

分别只承载自己的任务分支和实施产物：

- `tob-worktree`：TOB；
- `battle-mao-isp`：ISP；
- `power-large-task`：电力和大企。

禁止在任务 worktree 中：

- 合并其他任务分支；
- 合并到长期分支；
- 执行统一冲突处理；
- 修改其他模块；
- 宣布集成或 VERIFIED。

每个任务 worktree 在被集成前必须是干净状态，全部必要变更必须已经提交到对应任务分支。

---

## 4. 固定集成执行位置

所有 merge 命令必须显式作用于：

```text
D:\BattleMap\battle-map
```

推荐使用带 `-C` 的命令，避免 Agent 当前目录错误：

```powershell
git -C "D:\BattleMap\battle-map" merge --no-ff --no-commit task/enterprise-tob
git -C "D:\BattleMap\battle-map" merge --no-ff --no-commit task/enterprise-isp
git -C "D:\BattleMap\battle-map" merge --no-ff --no-commit task/enterprise-power-large
```

固定顺序：

```text
TOB
→ ISP
→ 电力 + 大企
```

不得在 `D:\BattleMap\tob-worktree`、`D:\BattleMap\battle-mao-isp` 或 `D:\BattleMap\power-large-task` 中运行上述 merge。

---

## 5. 任务完成检查

合并前分别在三个任务 worktree 中确认：

1. 工作树干净；
2. 当前分支正确；
3. implementation report 已提交；
4. 状态为 `IMPLEMENTED_NOT_VERIFIED`；
5. 模块测试通过；
6. 全量测试没有本任务引入失败；
7. build 通过；
8. `BASE_HEAD`、任务 tip、Migration 和共享文件修改已记录；
9. 没有未解决 blocker。

如果某个任务 worktree 仍有未提交文件，不能通过从工作目录直接复制文件到集成工作树的方式“补合并”。必须先让对应任务 Agent 正确提交。

---

## 6. 基线和分支关系验证

从三个 implementation report 读取共同 `BASE_HEAD`，并在集成工作树执行：

```powershell
git -C "D:\BattleMap\battle-map" merge-base --is-ancestor <BASE_HEAD> task/enterprise-tob
git -C "D:\BattleMap\battle-map" merge-base --is-ancestor <BASE_HEAD> task/enterprise-isp
git -C "D:\BattleMap\battle-map" merge-base --is-ancestor <BASE_HEAD> task/enterprise-power-large
git -C "D:\BattleMap\battle-map" merge-base --is-ancestor <BASE_HEAD> feature/enterprise-battle-map
```

三个任务必须来自同一个 `BASE_HEAD`。长期分支在并行期间如因经批准的 MOX 修复而前进，应记录 `BASE_DRIFT`，不得将长期分支重置回旧基线。

---

## 7. 路径安全门禁

以下情况必须阻塞：

- Integration Agent 当前工作目录是某个任务 worktree；
- `D:\BattleMap\battle-map` 未检出 `feature/enterprise-battle-map`；
- 任一任务路径映射到错误分支；
- 任一 worktree 不干净；
- 任务分支成果只存在工作目录而未提交；
- ISP 路径被错误改写为不存在的目录；
- Agent 试图重新创建已有 worktree；
- Agent 试图通过复制文件代替 Git merge；
- Agent 使用 `reset --hard`、`git clean`、强制 checkout 或 rebase 隐藏差异。

---

## 8. 集成报告必须记录

统一集成报告必须记录：

```text
INTEGRATION_WORKTREE=D:\BattleMap\battle-map
TOB_WORKTREE=D:\BattleMap\tob-worktree
ISP_WORKTREE=D:\BattleMap\battle-mao-isp
POWER_LARGE_WORKTREE=D:\BattleMap\power-large-task

INTEGRATION_BRANCH=feature/enterprise-battle-map
TOB_BRANCH=task/enterprise-tob
ISP_BRANCH=task/enterprise-isp
POWER_LARGE_BRANCH=task/enterprise-power-large

COMMON_BASE_HEAD=
PRE_INTEGRATION_HEAD=
TOB_TIP=
ISP_TIP=
POWER_LARGE_TIP=
POST_INTEGRATION_HEAD=
```

最终状态仍只能是：

```text
INTEGRATED_NOT_VERIFIED
```

完成统一集成和自动验证后停止，由新的独立 Agent 审查 `D:\BattleMap\battle-map` 中的合并后 HEAD。
