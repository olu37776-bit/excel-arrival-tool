# Swap / GBrain 知识库重建 Authority Index

> **状态：CURRENT**  
> **Authority Carrier：** `olu37776-bit/excel-arrival-tool` 仅作为本支线 Authority 文档的远程载体；本目录与 Excel 工具自身业务/代码建设相互隔离。  
> **本地正式知识：** `D:\gbrain-knowledge\swap-kb\`、`D:\gbrain-knowledge\microwave-kb\`  
> **本地原始资料：** `D:\swap-knowledge-sources\`

## 1. Authority 规则

本目录中的 CURRENT 文档是 Swap / GBrain 知识库重建支线的长期执行 Authority。

聊天记录不是长期 Authority；聊天只用于指向 CURRENT 文档、传递短回执和处理需要用户裁决的事项。

发生冲突时：

1. 当前真实代码 / 配置 / 正式设备与 MML 资料 / 测试 Evidence 优先于实施报告；
2. 本索引标记的 CURRENT Authority 优先于 SUPERSEDED 文档；
3. 业务语义或 Authority 冲突无法从事实源裁决时，必须记录 `NEED_USER_CONFIRMATION` 或 `BLOCKED_BY_AUTHORITY`，禁止猜测。

## 2. CURRENT Authority

| 文档 | 状态 | 作用 |
|---|---|---|
| `docs/swap-knowledge-reconstruction/authority-index.md` | CURRENT | 当前阶段、状态、唯一任务与下一门禁 |
| `docs/swap-knowledge-reconstruction/architecture/knowledge-reconstruction-authority-v1.md` | CURRENT | 长期知识边界、目录、事实源、构建/审查规则 |
| `docs/swap-knowledge-reconstruction/tasks/local-state-reconciliation-v1.md` | CURRENT TASK | 从本机真实 Artifact 恢复 B2/B3 与 Knowledge Repo 的准确状态 |

## 3. SUPERSEDED / 非 Authority

以下内容不得作为当前长期执行 Authority：

- 聊天中历史长提示词；
- 旧低质量 LLM Wiki（只能作为 clue）；
- 未经 Independent Verification 的 Reconstruction/Remediation 自报 PASS；
- `.ai-work` 中一次性实验产物；
- 与 CURRENT 文档冲突的旧设计或旧阶段说明。

## 4. 已知建设基线

以下为当前已知事实；其中涉及本地阶段状态的部分必须由 CURRENT TASK 从本机 Artifact 重新证明：

- GBrain 已在本机通过源码编译运行；当前知识建设不依赖 Embedding。
- 正式 Knowledge Repo 已固定为：
  - `D:\gbrain-knowledge\swap-kb\`
  - `D:\gbrain-knowledge\microwave-kb\`
- 两个 Knowledge Repo 应分别为独立 Git Repository / GBrain Source。
- Raw Sources 固定为 `D:\swap-knowledge-sources\`，不直接等于 Brain Knowledge。
- `Survey V1` 已完成 Survey、独立审查、Remediation 与复验，并已形成冻结的 Reconstruction Baseline。
- Golden Slice #1 已完成 Reconstruction、Independent Review、Remediation、Independent Verification，并已提炼 `Knowledge Construction Convention V1`。
- Batch #2 主题为 **Core Swap Processing Architecture**；已知 Reconstruction 与 Remediation 已执行，但最终独立复验 / Baseline 状态必须以本机 Artifact 为准。
- Batch #3 主题为 **Source Configuration Ingestion & Normalization**；已知 Reconstruction 已执行，但 Review / Remediation / Baseline 状态必须以本机 Artifact 为准。

## 5. 当前阶段

**Authority Bootstrap → Local State Reconciliation**

当前先把聊天历史中的进度转换为可由新 Agent 独立恢复的事实状态。

## 6. 当前唯一允许执行的任务

**`Local State Reconciliation V1`**

Authority：

`docs/swap-knowledge-reconstruction/tasks/local-state-reconciliation-v1.md`

本任务只读恢复本地状态，不继续新增或修改正式 Knowledge Page。

## 7. 当前 Blocker

`B2/B3_FINAL_STATE_NOT_YET_RECONCILED_IN_REPOSITORY_AUTHORITY`

原因：GitHub Authority 尚未基于本机真实 Artifact 固化 Batch #2 / Batch #3 的最终独立验证状态与 Knowledge Repo HEAD。

## 8. 下一门禁

Local State Reconciliation 必须提供：

- Batch #2 真实阶段状态；
- Batch #3 真实阶段状态；
- `swap-kb` 当前 HEAD 与 clean/dirty 状态；
- `microwave-kb` 当前 HEAD 与 clean/dirty 状态；
- 当前 Baseline / Convention 的可定位证据；
- 下一合法动作建议（仅依据现有 Authority 和本地事实）。

在该门禁通过前，不开始 Batch #4，不扩大知识覆盖。

## 9. 后续推进顺序

1. Local State Reconciliation V1；
2. 根据短回执，由远程 Authority 维护者更新本索引并创建下一 CURRENT TASK；
3. 若 B2/B3 存在未完成 Verification/Remediation，先补对应 Gate；
4. 若 B2/B3 均完成，更新 Knowledge Baseline；
5. 再规划下一知识批次；
6. 每批继续保持 Reconstruction 与 Independent Verification 分离。

## 10. 本地 Agent 恢复入口

本地 Authority Checkout 推荐固定为：

`D:\ai-authority\excel-arrival-tool\`

每次执行前先拉取 `main`，然后从本文件开始恢复状态。
