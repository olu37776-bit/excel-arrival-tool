# 企业五模块：共享操作链收敛与审查阻塞修复 V1

**状态：HISTORICAL IMPLEMENTATION BASELINE / SHARED OPERATION REGRESSION RULES**
**适用模块：MOX、TOB、ISP、电力、大企**
**代码目录：D:\BattleMap\battle-map**
**代码分支：feature/enterprise-battle-map**
**Authority 目录：D:\BattleMap\BattleMapenterprise-authority**

## 1. 历史任务目标与事实边界

最新阶段以 authority-index.md 为准；此文件保留既有操作链整改与回归规则，不代表用户最新报告的是该轮阻塞。已确认 Excel 增量和首页工作按各自当前规范独立实施，下面的旧 WRITE_SCOPE 不撤销后续授权。

用户报告完整独立审查阻塞，并进一步明确：主要问题是需要像 V3 收敛新增/编辑一样，将其他操作中的重复机制收敛到实际共享生产路径。

当前云端未取得本地审查报告正文。本文件定义执行方法和范围约束，不预设 finding ID、数量、具体有问题的操作或根因。具体修复项必须从最新本地报告和当前代码恢复，不能把下文调查范围当成已经确认的缺陷。

本轮目标：
- 修复报告中全部可执行的 blocking findings；
- 以报告指出的其他操作为入口，找出同根因的五模块重复实现；
- 将共性行为集中到唯一共享机制，各模块通过自身 Contract、业务配置和最小 adapter 接入；
- 修复代码、真实生产路径测试和实施记录保持一致；
- 完成后提交新 HEAD，等待完整独立复审。实施者不能声明 VERIFIED。

## 2. 必读资料

Authority 目录下：
- docs/enterprise-battle-map/authority-index.md
- docs/enterprise-battle-map/enterprise-contract-architecture-v5.md
- docs/enterprise-battle-map/architecture/enterprise-runtime-field-options-contract-v1.md
- docs/enterprise-battle-map/remediation/five-module-shared-form-renderer-convergence-v3.md
- docs/enterprise-battle-map/remediation/five-module-shared-operation-convergence-v1.md
- docs/enterprise-battle-map/reviews/non-mox-modules-mox-reference-independent-review-v1.md
- docs/enterprise-battle-map/reviews/non-mox-full-independent-review-rerun-v3.md
- mox-canonical-authority-v6.md、tob-canonical-authority-v2.md、isp-canonical-authority-v2.md、power-canonical-authority-v2.md、large-enterprise-canonical-authority-v2.md（均位于 docs/enterprise-battle-map）。

代码目录下：
- docs/enterprise/reviews/non-mox-modules-mox-reference-independent-review.md
- 该报告引用的历史 finding、证据和测试日志；
- docs/enterprise/remediations/five-module-shared-form-renderer-convergence-report-v3.md；
- 当前生产代码、测试、package.json、API、database.js、Migration；
- 相关本地 AGENTS.md。

报告的 finding 和实际代码必须相互核对。报告结论不可静默改写；若 finding 无法复现，记录证据与 REVIEW_REQUIRED，不得自行撤销独立审查结论。

## 3. Phase 0：恢复受审状态与全部 findings

先更新 Authority 镜像，记录 AUTHORITY_HEAD；更新失败不得使用旧文件冒充本规范。

在代码工作树记录 BRANCH、BASE_HEAD、git status --short、报告的 REVIEWED_HEAD，以及报告文件的 SHA-256。确认只有当前一个写 Agent。不得 reset、rebase、clean、丢弃或覆盖其他修改。

上一轮审查按规范可能只留下未提交的报告/证据文件：识别这些文件并保留，不把这种已知产物误当成生产代码未提交而阻塞。若存在来源不明或冲突的代码/测试修改，停止受影响写入，不擅自提交它们。

若 BASE_HEAD 与 REVIEWED_HEAD 不同，先检查祖先关系和差异：
- 仅报告/证据变化：记录后可以继续；
- 含代码、测试、配置或 Migration 变化：重新定位并复现相关 finding，不能直接套用旧位置；
- 报告缺失：先查该报告的规范归档目录和 Git 历史，不虚构报告；确实无法恢复则标记 MISSING_REVIEW_REPORT。

修改前保存原报告副本至：
docs/enterprise/remediations/evidence/shared-operation-convergence/<BASE_HEAD>/input-review.md

从报告恢复全部 findings，保留原 ID、严重度、Authority 引用、生产路径、复现证据、原状态。分类为：
IMPLEMENTATION_NONCONFORMANCE / TEST_GAP / EVIDENCE_OR_ENVIRONMENT_GAP / AUTHORITY_CONFLICT / NON_BLOCKING。
不能把全部阻塞一律当成需要重写代码的问题。

## 4. Phase 1：五模块操作清单与根因调查

重点采用 V3 的方法：从真实入口追到实际行为，比较五模块的机制实现，不能只检查是否 import 共享 helper。

以报告指出的操作为必查入口，检查这些实际存在的关联消费者：
- 表格加载、列投影、格式化、刷新；
- 搜索、筛选、排序、状态清理；
- 指标计算、指标点击筛选及与表格筛选的关系；
- Heatmap 转换、tooltip、点击交互（仅已有能力）；
- 客户候选获取、关联选择和 customer_id 传递；
- Progress 弹窗打开、历史读取、新增、编辑及最新投影；
- 报告涉及的其他已有行操作、批量操作或请求/持久化路径。
列表用于发现同根因漏项，不要求新增操作或强制把每个模块的业务行为做成一样。

每个相关操作逐模块记录：
OPERATION / MODULE / UI_ENTRY / EVENT_HANDLER / CONTRACT_OR_CONFIG /
SHARED_ENGINE_OR_CONTROLLER / MODULE_ADAPTER / API_SERVICE /
DATABASE_OR_HISTORY_TARGET / RESULT_REFRESH_PATH /
ACTUAL_PRODUCTION_CONSUMER / TEST_ENTRY /
LOCAL_DUPLICATE_IMPLEMENTATION / EXPECTED_BUSINESS_DIFFERENCE。

区分：
1. SHARED_AND_USED：已共享，保留并回归；
2. DUPLICATE_MECHANISM：同一规则/生命周期重复实现，应收敛；
3. BUSINESS_DIFFERENCE_EXPECTED：业务字段、查询条件、合法数据源或模块 adapter 差异，必须保留；
4. DEAD_PATH：证明无消费者后清理；
5. TEST_ONLY_OR_MIGRATION_ONLY：单独分类，不算活动生产重复；
6. UNKNOWN：继续取证，不能按共享或重复作结论。

共享操作边界按实际职责决定。不同操作可有不同共享实现，不要求合成一个处理所有事件的超级引擎。

## 5. Phase 2：先写具体修复计划，然后直接实施

先在下列文件形成可执行计划：
docs/enterprise/remediations/five-module-shared-operation-convergence-plan-v1.md

必须写明：
- BASE_HEAD、REVIEWED_HEAD、AUTHORITY_HEAD、报告哈希；
- 全部 finding 清单及五模块操作清单；
- 每个根因组的 finding IDs、当前真实路径、目标共享路径；
- 每项操作保留哪个已有共享实现，或从哪条已证实正确的路径提炼；
- shared mechanism / module Contract / module adapter 各自职责；
- 精确 WRITE_SCOPE 文件列表；移除的重复路径及现有消费者迁移列表；
- 实施依赖顺序；
- 回归测试、生产路径证明、负向输入/错误处理、清理完成条件；
- 每个 finding 的可检查验收条件。

目标共享行为必须符合现有 Authority；不能简单假设 MOX 的所有其他操作天然正确。

计划完成并完成约束自检后，在当前用户授权内直接实施，不停在“计划已生成”要求用户再批准。不额外要求云端读取本地报告才能开始。

如需要改变正式业务定义或 Authority 相互冲突，记录具体冲突并只阻塞相关部分；其他独立修复继续。不得自行改写 Authority 解除约束。

## 6. 实施原则

对每个根因组按以下顺序执行：
1. 复现报告中的实际行为或结构缺陷；
2. 在真实生产入口建立有判别力的回归测试；已有可信测试可直接复用；
3. 提炼/修正唯一共享机制；
4. 让全部受影响模块实际接入；
5. 验证 UI/event → shared implementation → API/结果/状态更新的完整链；
6. 确认无消费者后删除旧路径；
7. 执行当前组回归，更新计划/报告/证据，再处理下一组。

硬规则：
- 五模块业务 Field/Metric Contract 保持独立，不 cross-import 对方业务字段或持久化映射；
- 不复制 MOX 操作实现到其他模块，不在 shared 文件内保留五套完整操作分支；
- 共享外壳加模块本地完整处理链不算共享；
- 模块保留绑定、业务配置、规范化和持久化等必要 adapter；不把这些合法差异机械清零；
- 指标计算与点击筛选使用同一 Metric Contract.where；点击筛选不能反向重算顶层指标；
- customer_id 关系身份、Progress History 唯一事实源、Heatmap canonical identity、API canonical-only 继续有效；
- 不恢复 legacy alias/fallback、双写或模块私有客户查询；
- 不改变未授权的业务字段、Metric公式、Heatmap口径，不引入 Excel V0.2 delta，不建设首页或非企业功能；
- 如有报告证明的 DB/Migration 缺陷，允许按现有目标契约修复；先写入 WRITE_SCOPE，使用新 Migration/现有注册机制并验证数据保留、事务、回滚、幂等。不得改写用户业务数据库或已应用迁移来绕过问题。

## 7. 验证要求

测试应回答“用户从真实入口触发该操作时，是否使用共享机制并得到正确行为”。
禁止 mock 掉待验证的共享机制后只检查 props 或调用次数；外部网络等系统边界可合理隔离。

按实际操作覆盖：
- 正常结果、空结果、错误边界；
- 合同规定的选择/筛选/重置/刷新状态；
- 客户同名与身份保留；
- Progress 写入后读取与表格刷新一致；
- 异步重入、重复提交或旧响应覆盖等问题，仅在实际路径存在相关风险时验证；
- 五模块状态及数据隔离；
- 真实 production consumer 的共享路径；
- 静态/架构门禁能识别被修复的重复机制，不能仅打印计数。

依次执行根因组测试、受影响操作五模块回归、V3 五模块 Create/Edit 和共享 renderer 回归、Customer/Progress/Heatmap/Metric/API/DB 相关现有回归、enterprise suite、full Vitest、build、已有 lint/typecheck。重叠 suite 可通过一次运行提供覆盖证据，不为重复统计反复运行相同测试。

使用项目真实命令，保存退出码与日志。测试/Migration 使用隔离临时数据库或副本，不改写用户真实数据。
必要验证未运行则记 NOT_RUN 并解释，不能记 PASS；测试缺口必须补足，不能只改报告。
不降低断言、不删除失败测试、不跳过 required gate 以制造通过。

## 8. 固定产物、状态与提交

计划：
docs/enterprise/remediations/five-module-shared-operation-convergence-plan-v1.md
实施报告：
docs/enterprise/remediations/five-module-shared-operation-convergence-report-v1.md
Finding 矩阵：
docs/enterprise/remediations/five-module-shared-operation-convergence-findings-v1.md
证据：
docs/enterprise/remediations/evidence/shared-operation-convergence/<BASE_HEAD>/

本轮重复执行时，先把上述已存在且对应不同 BASE_HEAD 的三份产物保存至当前证据目录的 prior-artifacts/，保持原文件名，不覆盖不同内容的历史文件。

矩阵包含 finding ID、根因组、代码/测试修改、真实路径证据、测试结果、状态：
IMPLEMENTED_PENDING_REVIEW / UNRESOLVED / BLOCKED_AUTHORITY / REVIEW_REQUIRED。
实施者不能将独立审查 finding 标为 CLOSED 或 VERIFIED。

不覆盖独立审查报告，不把其 FAIL/BLOCKED 改为 PASS。原报告保持针对原 REVIEWED_HEAD 的历史事实；新代码等待新审查。

全部实现和验证完成后：
- 检查 git diff 与 WRITE_SCOPE；
- 更新相关本地实现记录、测试说明和上述产物；不得改权威需求；
- 只 stage 本轮明确拥有的代码、测试、计划与证据文件，不 git add 全仓；
- 对前次尚未提交的独立审查报告/证据，确认属于上轮只读产物且内容原样保留后，可单独提交保存原始证据，不能将其混称为本轮实现；
- 本地提交本轮代码、测试与实施产物，不 push、merge、rebase；
- 记录 IMPLEMENTATION_HEAD 为本轮实现提交 SHA。若随后补写 SHA 到报告形成 docs-only 提交，记录其关系；最终短回执的 FINAL_HEAD 必须为真实最终 git rev-parse HEAD，不能伪造自引用 SHA；
- 下一独立审查固定 FINAL_HEAD，先证明 IMPLEMENTATION_HEAD 到 FINAL_HEAD 仅为报告/证据差异。

## 9. 完成条件与后续

RESULT=COMPLETE 仅当：
- 全部可执行 blocking findings 均有实施和测试证据；
- 报告涉及的重复操作机制及同根因生产消费者已收敛；
- V3 新增/编辑和其他必要回归无退化；
- 必要验证通过；
- 无未解决 blocker、越界修改、未提交实施文件。

仍有未完成修复/验证则 RESULT=PARTIAL；存在必须人工处理的 Authority、缺失输入或访问阻塞则 RESULT=BLOCKED，明确已完成与剩余部分。

实现者状态始终为 IMPLEMENTED，不声明 VERIFIED。COMPLETE 后 NEXT=FULL_INDEPENDENT_REVIEW_RERUN_V3，必须对新 HEAD 完整重跑 Review V1 + Full Rerun V3，并将本轮全部 findings 与受影响操作加入回归。不能只复核修复项，不能直接进入人工验收。

除真正的阻塞外，持续完成全部根因组，不因计划、单个 finding 或一次测试成功就结束。

## 10. 最终短回执

```text
FIVE-MODULE SHARED OPERATION CONVERGENCE
RESULT=COMPLETE/PARTIAL/BLOCKED
STATUS=IMPLEMENTED
AUTHORITY_HEAD=
REVIEWED_HEAD=
BASE_HEAD=
IMPLEMENTATION_HEAD=
FINAL_HEAD=
FINDINGS_IMPLEMENTED=x/N
AFFECTED_OPERATIONS=
SHARED_PRODUCTION_PATHS=PASS/FAIL/NOT_RUN
UNRESOLVED_FINDINGS=NONE或ID
REVIEW_REQUIRED=NONE或ID
V3_CREATE_EDIT_REGRESSION=PASS/FAIL/NOT_RUN
FULL_TESTS=PASS/FAIL/NOT_RUN
BUILD=PASS/FAIL/NOT_RUN
OUT_OF_SCOPE_CHANGES=NO/YES
PLAN_PATH=
REPORT_PATH=
FINDINGS_PATH=
BLOCKERS=NONE或具体内容
NEXT=FULL_INDEPENDENT_REVIEW_RERUN_V3/CONTINUE_REMEDIATION/AUTHORITY_DECISION
```

用户办公电脑无法上传，最终只需复制回执；无需上传代码或完整报告。
