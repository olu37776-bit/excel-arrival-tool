# Local State Reconciliation V1

> **状态：CURRENT TASK**  
> **任务类型：只读状态恢复 / Authority Bootstrap**  
> **入口：** `docs/swap-knowledge-reconstruction/authority-index.md`

## 1. Context

此前 Swap / GBrain 知识库重建长期依赖聊天提示词和本地 `.ai-local` 产物解释当前状态。

现在切换到 Repository Authority-Driven 工作方式。

GitHub Authority 必须先基于本机真实 Artifact 恢复 Batch #2 / Batch #3、Knowledge Repo HEAD、Baseline / Convention 的准确状态，之后才能继续下一阶段。

本任务不是知识重建任务，不修改正式 Knowledge Page。

## 2. Proven Facts

已知本地路径：

- 正式 Swap Knowledge Repo：`D:\gbrain-knowledge\swap-kb\`
- 正式 Microwave Knowledge Repo：`D:\gbrain-knowledge\microwave-kb\`
- Raw Sources：`D:\swap-knowledge-sources\`
- 本地治理根目录：当前 Swap 源码仓中的 `.ai-local\knowledge\reconstruction\`

已知历史阶段：

- Survey V1 已形成冻结 Reconstruction Baseline；
- Golden Slice #1 已完成验证并形成 Knowledge Baseline #1；
- Knowledge Construction Convention V1 已形成；
- Batch #2 = `Core Swap Processing Architecture`；
- Batch #2 已执行 Reconstruction、Independent Review 与 Remediation；其最终独立复验 / Baseline 状态必须从本地 Artifact 恢复；
- Batch #3 = `Source Configuration Ingestion & Normalization`；
- Batch #3 已执行 Reconstruction；其 Review / Remediation / Baseline 状态必须从本地 Artifact 恢复。

## 3. Objective

只读检查本地真实 Artifact 和 Git HEAD，生成一个可供远程 Authority 更新的确定性状态报告。

必须回答：

1. Batch #2 当前真实状态；
2. Batch #3 当前真实状态；
3. `swap-kb` 当前 HEAD / clean state；
4. `microwave-kb` 当前 HEAD / clean state；
5. 当前已存在的 Baseline 与 Convention；
6. 当前下一合法动作。

## 4. WRITE_SCOPE

允许写入的唯一位置：

`.ai-local\knowledge\reconstruction\authority-reconciliation\v1\`

允许创建：

- `local-state-report.md`
- `local-state.json`

除此之外默认只读。

## 5. OUT_OF_SCOPE

禁止：

- 修改 `D:\gbrain-knowledge\swap-kb\` Knowledge Page；
- 修改 `D:\gbrain-knowledge\microwave-kb\` Knowledge Page；
- commit / reset / checkout 两个 Knowledge Repo；
- 修改 Swap production code；
- 修改 Raw Sources；
- 补做 Reconstruction / Remediation；
- 重新做 Survey；
- 开始新 Batch；
- 根据聊天历史猜测缺失阶段。

如果发现缺少关键 Artifact，只记录真实缺口。

## 6. Required Inspection

### 6.1 Baseline / Convention

检查：

`.ai-local\knowledge\reconstruction\baselines\`

`.ai-local\knowledge\reconstruction\conventions\v1\`

记录实际存在的：

- Reconstruction Baseline；
- Knowledge Baseline；
- Convention V1；
- 相关最终 Decision / frozen status。

不要因为目录名存在就默认已经 VERIFIED；读取实际内容。

### 6.2 Batch #2

检查至少以下实际存在路径：

`.ai-local\knowledge\reconstruction\batches\batch-2\`

`.ai-local\knowledge\reconstruction\reviews\batch-2-v1\`

`.ai-local\knowledge\reconstruction\remediation\batch-2-v1\`

`.ai-local\knowledge\reconstruction\reviews\batch-2-v1-remediation\`

以及任何明确关联 B2 的 Baseline Update Artifact。

Batch #2 状态只允许使用以下之一：

- `VERIFIED_AND_BASELINED`
- `VERIFIED_NOT_BASELINED`
- `REMEDIATED_NOT_VERIFIED`
- `REVIEW_REMEDIATION_REQUIRED`
- `RECONSTRUCTED_NOT_REVIEWED`
- `BLOCKED`
- `UNKNOWN_MISSING_EVIDENCE`

判定规则：

- 独立复验明确 `APPROVED_FOR_BASELINE_UPDATE` 且 Baseline 已记录 B2 → `VERIFIED_AND_BASELINED`；
- 独立复验已通过但没有 Baseline Update → `VERIFIED_NOT_BASELINED`；
- Remediation 已完成但找不到独立复验 → `REMEDIATED_NOT_VERIFIED`；
- Review 明确要求整改且无已验证关闭 Evidence → `REVIEW_REMEDIATION_REQUIRED`；
- 只有 Reconstruction，没有 Review → `RECONSTRUCTED_NOT_REVIEWED`；
- 明确存在阻塞 Finding → `BLOCKED`；
- Artifact 不足无法裁决 → `UNKNOWN_MISSING_EVIDENCE`。

### 6.3 Batch #3

检查至少：

`.ai-local\knowledge\reconstruction\coverage\source-configuration-v1\`

`.ai-local\knowledge\reconstruction\batches\batch-3\reconstruction-v1\`

`.ai-local\knowledge\reconstruction\reviews\batch-3-v1\`

`.ai-local\knowledge\reconstruction\remediation\batch-3-v1\`

`.ai-local\knowledge\reconstruction\reviews\batch-3-v1-remediation\`

以及任何明确关联 B3 的 Baseline Update Artifact。

Batch #3 状态使用与 B2 相同状态集合和判定原则。

### 6.4 Knowledge Repo Git State

对：

`D:\gbrain-knowledge\swap-kb\`

`D:\gbrain-knowledge\microwave-kb\`

只读执行等价检查：

- `git rev-parse HEAD`
- `git status --porcelain`
- 当前 branch
- 最近与 Golden Slice / B2 / B3 有关的 commits（只需用于定位，不做历史重写）

记录：

- HEAD SHA；
- branch；
- clean / dirty；
- 若 dirty，列出文件路径但不要修改。

## 7. Evidence Rules

所有状态判断必须给出 Artifact 路径和明确 Decision / Evidence。

不得使用：

- “我记得做过”；
- 聊天历史自报 READY；
- Reconstruction Agent 自己声明 PASS；

替代 Independent Verification Evidence。

## 8. Output Contract

### 8.1 `local-state.json`

至少包含：

```json
{
  "reconciledAt": "...",
  "batch2": {
    "status": "...",
    "evidence": []
  },
  "batch3": {
    "status": "...",
    "evidence": []
  },
  "swapKb": {
    "path": "D:\\gbrain-knowledge\\swap-kb\\",
    "head": "...",
    "branch": "...",
    "clean": true
  },
  "microwaveKb": {
    "path": "D:\\gbrain-knowledge\\microwave-kb\\",
    "head": "...",
    "branch": "...",
    "clean": true
  },
  "baselines": [],
  "convention": {},
  "blockers": [],
  "nextLegalAction": "..."
}
```

### 8.2 `local-state-report.md`

使用中文，简要说明：

- B2 状态及证据；
- B3 状态及证据；
- 两个 Knowledge Repo HEAD / clean state；
- Baseline / Convention 现状；
- blocker；
- 下一合法动作。

不要复制长篇历史内容。

## 9. Completion Gate

只有以下全部成立才可完成：

- B2 状态基于本地真实 Artifact 判定；
- B3 状态基于本地真实 Artifact 判定；
- 两个 Knowledge Repo HEAD 与 clean state 已记录；
- Baseline / Convention 已检查；
- 没有修改正式知识 / 源码 / Raw Sources；
- 报告可供远程 Authority 更新者直接使用。

## 10. Final Receipt

成功仅返回：

```text
SWAP_KNOWLEDGE_LOCAL_STATE_RECONCILED
B2=<status>
B3=<status>
SWAP_KB_HEAD=<sha>
MICROWAVE_KB_HEAD=<sha>
REPORT=.ai-local/knowledge/reconstruction/authority-reconciliation/v1/local-state-report.md
```

如无法完成：

```text
SWAP_KNOWLEDGE_LOCAL_STATE_RECONCILIATION_BLOCKED
reason=<one-line blocker>
```

完成后停止，不执行下一阶段。
