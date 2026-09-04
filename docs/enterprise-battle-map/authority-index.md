# 企业作战地图 Authority 文档索引

**状态：CURRENT AUTHORITY INDEX**  
**文档分支：`enterprise-battle-map-authority`**  
**长期本地集成分支：`feature/enterprise-battle-map`**

---

## 1. 当前正式 Authority

| 顺序 | 文档 | 用途 | 当前门禁 |
|---:|---|---|---|
| 1 | `enterprise-contract-architecture-v3.md` | `src/config/enterprise`目录、Field/Metric Contract、三个同级Section、Projection、Validator、数据库和测试治理 | 所有企业任务必读 |
| 2 | `implementation/parallel-module-execution-v1.md` | TOB、ISP、电力+大企并行分支/worktree、Migration预留和共享文件纪律 | 所有并行任务必读 |
| 3 | `integration/parallel-module-integration-plan-v1.md` | 三个任务分支按顺序合并、冲突解析、V35—V38联合验证、集成报告和状态门禁 | 三个任务完成后的唯一集成Authority |
| 4 | `mox-canonical-authority-v4.md` | MOX 41字段、三个Section、客户类别、进展、V34、UI/API/DB、统计与筛选 | MOX唯一业务Authority |
| 5 | `remediation/mox-post-manual-review-remediation-v2.md` | MOX当前人工审查后定向修复WRITE_SCOPE | MOX修复必读 |
| 6 | `tob-canonical-authority-v2.md` | TOB字段、页面、API/DB和统计目标 | TOB业务Authority |
| 7 | `implementation/tob-parallel-implementation-plan-v1.md` | TOB并行实施范围、V35、测试和报告要求 | TOB任务必读 |
| 8 | `isp-canonical-authority-v2.md` | ISP字段、页面、API/DB和统计目标 | ISP业务Authority |
| 9 | `implementation/isp-parallel-implementation-plan-v1.md` | ISP并行实施范围、V36、测试和报告要求 | ISP任务必读 |
| 10 | `power-canonical-authority-v2.md` | 电力字段、页面、API/DB和统计目标 | 电力业务Authority |
| 11 | `large-enterprise-canonical-authority-v2.md` | 大企字段、页面、API/DB和统计目标 | 大企业务Authority |
| 12 | `implementation/power-large-parallel-implementation-plan-v1.md` | 电力+大企并行实施范围、V37/V38、隔离和测试要求 | 电力+大企任务必读 |
| 13 | `enterprise-home-canonical-authority-v2.md` | 企业首页历史设计 | DEFERRED；等待后续新版首页Authority |

当前流程：

```text
三个任务分支并行实施
→ 各分支 IMPLEMENTED_NOT_VERIFIED
→ 按 integration/parallel-module-integration-plan-v1.md 统一合并
→ 长期分支标记 INTEGRATED_NOT_VERIFIED
→ 新 Agent 统一独立审查
```

企业首页最终汇总和首页Heatmap仍不得在本阶段实施。

---

## 2. 已被取代或暂停使用的文档

以下文件仅保留历史记录，不再作为当前实施、集成或审查 Authority：

- `enterprise-contract-architecture-v1.md`
- `enterprise-contract-architecture-v2.md`
- `mox-canonical-authority-v3.md`
- `remediation/mox-post-manual-review-remediation-v1.md`
- `tob-canonical-authority-v1.md`
- `isp-canonical-authority-v1.md`
- `power-canonical-authority-v1.md`
- `large-enterprise-canonical-authority-v1.md`
- `enterprise-home-canonical-authority-v1.md`
- 任何与当前 GitHub Authority 冲突的本地字段清单、Schema、Contract、WRITE_SCOPE和Review结论

`enterprise-home-canonical-authority-v2.md`当前也不得用于实施首页最终统计口径。首页将在最后阶段重新发布当前版本。

本地 Agent 不得同时读取新旧版本后自行折中。

---

## 3. Authority 与 Excel

判断顺序：

```text
当前模块Canonical Authority
→ 本地“企业作战地图基表”对应Sheet的精确列、Row2、Row3和Validation
→ 用户最新明确修正
→ 共享架构Authority
→ 当前代码/API/database.js/SQLite现状
→ 本地旧文档、旧Schema和旧配置
```

规则：

- GitHub Canonical Authority 是经用户确认后的目标定义；
- Excel 是字段原始需求来源，实施时必须核实字段位置和输入约束；
- Excel与当前Canonical Authority发生实质冲突时，不得自行折中或扩充字段，应记录冲突；
- 当前代码和数据库只用于判断差距，不能反向创造需求；
- 表格、新增、编辑必须消费同一模块 Field Contract；
- 统计与点击筛选必须消费同一 Metric Contract 条件；
- 代码、测试、自动验证和实施报告必须同轮完成；
- 人工页面验收由用户执行。

---

## 4. 当前代码目录规则

企业领域 Contract 配置位于：

```text
src/config/enterprise/
```

不得继续使用 `src/enterprise` 或 `src/features` 作为活动 Contract Authority目录。

页面、组件、API和数据库代码仍位于项目现有职责目录；本规则只约束 Field/Metric Contract、Projection、Validator、Metric Engine和option sets。

---

## 5. 表单 Section 规则

所有企业业务模块的新增和编辑使用三个同级 Section：

```text
客户信息 ｜ 业务格局 ｜ 作战情况
```

MOX 的无线与微波字段均位于“业务格局”，可保留内部子类元数据，但不得渲染成额外顶级Section。

其他模块的业务专属字段统一位于“业务格局”。具体字段由各模块 Authority 决定。

表格不显示Section标题，按模块Contract的全局order展开；作战进展固定为作战情况最后一项。

---

## 6. 并行实施纪律

三个模块任务必须从同一个 `feature/enterprise-battle-map`基线SHA创建独立任务分支和worktree：

```text
task/enterprise-tob
task/enterprise-isp
task/enterprise-power-large
```

共享内核默认只读；确需共享修改时必须在模块实施报告中声明。架构级共享缺口不得由三个Agent分别实现。

Migration预留：

```text
TOB V35
ISP V36
电力 V37
大企 V38
```

各任务完成后只提交自己的任务分支，不自行合并、不自行审查、不开始下一模块。

---

## 7. 统一集成纪律

三个任务全部完成后，只使用：

```text
integration/parallel-module-integration-plan-v1.md
```

进行统一集成。

固定顺序：

```text
TOB
→ ISP
→ 电力+大企
```

统一集成必须：

- 在干净的 `feature/enterprise-battle-map` 工作树执行；
- 核实三个任务使用相同 BASE_HEAD；
- 不重置长期分支已批准的MOX进展；
- 每次merge后立即执行该模块和关键回归测试；
- 对`database.js`和共享Contract逐项合并，不使用整体ours/theirs；
- 验证V35、V36、V37、V38的注册、顺序、事务、幂等和回滚；
- 验证新库和旧库升级结果一致；
- 验证模块Contract、API、数据库、状态和筛选互相隔离；
- 创建统一集成报告；
- 最终只标记 `INTEGRATED_NOT_VERIFIED`；
- 停止后由新Agent做统一独立审查。

不得在集成Agent中同时执行独立审查。

---

## 8. 页面结构与Heatmap

业务子页面统一：

```text
模块专项
→ 三个并列统计大模块
→ 当前模块Heatmap
→ 新增 / 表格 / 编辑
```

三个统计大模块：空间洞察、当年项目、空间拓展。每个模块内部显示指标，不得一个指标一张顶级卡。

现有TOB/ISP Heatmap优先保留并防回归。电力/大企在规则未冻结时使用安全空状态，不生成假数据。

企业首页最终汇总和首页Heatmap当前延后。

---

## 9. 当前推进与统一门禁

```text
冻结共同BASE_HEAD
→ 三个任务分支并行实施
→ 每个分支完成代码、测试、数据库验证、全量测试、build和实施报告
→ Integration Agent按正式计划合回feature/enterprise-battle-map
→ 连续验证V35/V36/V37/V38
→ 企业模块统一自动验证
→ 标记INTEGRATED_NOT_VERIFIED
→ 统一独立审查
→ 用户人工验收
```

并行任务完成只允许标记：

```text
IMPLEMENTED_NOT_VERIFIED
```

集成完成只允许标记：

```text
INTEGRATED_NOT_VERIFIED
```

不得在任务分支或集成阶段标记模块 VERIFIED。

---

## 10. Raw地址

总索引：

```text
https://raw.githubusercontent.com/olu37776-bit/excel-arrival-tool/enterprise-battle-map-authority/docs/enterprise-battle-map/authority-index.md
```

共享架构V3：

```text
https://raw.githubusercontent.com/olu37776-bit/excel-arrival-tool/enterprise-battle-map-authority/docs/enterprise-battle-map/enterprise-contract-architecture-v3.md
```

并行执行协议：

```text
https://raw.githubusercontent.com/olu37776-bit/excel-arrival-tool/enterprise-battle-map-authority/docs/enterprise-battle-map/implementation/parallel-module-execution-v1.md
```

统一集成计划：

```text
https://raw.githubusercontent.com/olu37776-bit/excel-arrival-tool/enterprise-battle-map-authority/docs/enterprise-battle-map/integration/parallel-module-integration-plan-v1.md
```

TOB Authority：

```text
https://raw.githubusercontent.com/olu37776-bit/excel-arrival-tool/enterprise-battle-map-authority/docs/enterprise-battle-map/tob-canonical-authority-v2.md
```

TOB实施计划：

```text
https://raw.githubusercontent.com/olu37776-bit/excel-arrival-tool/enterprise-battle-map-authority/docs/enterprise-battle-map/implementation/tob-parallel-implementation-plan-v1.md
```

ISP Authority：

```text
https://raw.githubusercontent.com/olu37776-bit/excel-arrival-tool/enterprise-battle-map-authority/docs/enterprise-battle-map/isp-canonical-authority-v2.md
```

ISP实施计划：

```text
https://raw.githubusercontent.com/olu37776-bit/excel-arrival-tool/enterprise-battle-map-authority/docs/enterprise-battle-map/implementation/isp-parallel-implementation-plan-v1.md
```

电力Authority：

```text
https://raw.githubusercontent.com/olu37776-bit/excel-arrival-tool/enterprise-battle-map-authority/docs/enterprise-battle-map/power-canonical-authority-v2.md
```

大企Authority：

```text
https://raw.githubusercontent.com/olu37776-bit/excel-arrival-tool/enterprise-battle-map-authority/docs/enterprise-battle-map/large-enterprise-canonical-authority-v2.md
```

电力+大企实施计划：

```text
https://raw.githubusercontent.com/olu37776-bit/excel-arrival-tool/enterprise-battle-map-authority/docs/enterprise-battle-map/implementation/power-large-parallel-implementation-plan-v1.md
```

---

## 11. 文档维护规则

- 业务和架构修正由该Authority分支统一维护；
- 本地实施分支不维护第二套长期设计Authority；
- 新版本发布后旧版本自动superseded；
- 字段变更必须同步字段表、Contract、Validator、数据库门禁和测试标准；
- 实施状态和审查证据可以留在本地，但不得覆盖GitHub目标设计；
- 三个并行任务全部集成后，再发布统一独立审查规范；
- 统一独立审查通过前不得删除任务分支或worktree。