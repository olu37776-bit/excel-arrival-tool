# 企业分支合入 master：失败候选修复与代码交付隔离 V1

**状态：CURRENT IMPLEMENTATION AUTHORITY / 候选审查失败，待本地执行**  
**业务来源：feature/enterprise-battle-map；交付目标：master**  
**本轮只准备新的本地候选，不更新 master、不 push、不发布**  
**后续门禁：integration/enterprise-master-candidate-independent-review-v1.md**

## 1. 当前事实、证据边界与本轮目标

用户转述最新候选审查结果：
- CRITICAL：候选提交的 server.js、server/db/database.js 中仍含原始 Git 冲突标记。
- HIGH：docs/enterprise/ 中 50+ 文件会随合并进入 master，与本地文档不提交、不上传要求冲突。
- build 报告通过，但测试报告有 47 个失败，涉及 MOX Schema 不匹配。
- 原工作树此前处于 rebase，另一个工作树已经准备过 merge 候选。

这些是用户转述的审查发现，不是云端已经读取本地源码、完整日志或实际数据库后的结论。47 是上一轮报告数量；必须核对是用例数、文件数还是其他口径，不猜测所有失败同根因，不猜测 moxSchema 的实际标识符。

本轮目标：保护原 rebase 和所有有效修改，修复真实集成语义，得到不携带本次本地 docs 的代码候选；以候选提交的文件内容、后端可解析/可启动、完整测试和数据库证据交接独立审查。不能继续把失败候选视为 READY_TO_UPDATE_MASTER。

## 2. 两个仓库职责必须分开

| 对象 | 本轮规则 |
|---|---|
| GitHub olu37776-bit/excel-arrival-tool 的 enterprise-battle-map-authority 分支 | 云端维护指导文档；本地只拉取。不是待合入业务 master 的代码分支 |
| D:\BattleMap\BattleMapenterprise-authority | 上述 Authority 的本地镜像，不复制进业务代码仓库 |
| D:\BattleMap\battle-map | 原业务工作树；此前有 rebase 现场，本轮保护、只读 |
| D:\BattleMap\battle-map-master-integration | 前轮失败候选预期工作树；核对实际记录，不覆盖、不清场 |
| 业务仓库 docs/，尤其 docs/enterprise/ | 本次新增文档/改动不得作为交付内容提交或进入 master；master 原有 docs 保持原样 |
| 本次实施、审查报告、证据、备份 | 只放 D:\BattleMap\local-reports 下，不加入代码提交、不上传 |

“本地 docs 不上库”不等于“停用 GitHub Authority”。此前规范中要求把报告写入 docs 并提交的内容，在本轮被本节明确取代；读取历史 docs 作为证据仍允许。不得重新开启用户已关闭的文档合并请求。

## 3. 必读与当前业务目标

更新 Authority 前确认镜像目录确属文档仓库，工作树无不明修改，分支正确：
```powershell
git -C "D:\BattleMap\BattleMapenterprise-authority" pull --ff-only origin enterprise-battle-map-authority
```
失败则记录实际错误和本地 AUTHORITY_HEAD，不切到其他分支、不假称最新。

从 Authority 的 docs/enterprise-battle-map/ 完整读取：
- authority-index.md、本文件、integration/enterprise-master-candidate-independent-review-v1.md；
- enterprise-contract-architecture-v5.md、architecture/enterprise-runtime-field-options-contract-v1.md；
- 各模块当前 Canonical Authority、enterprise-excel-confirmed-delta-v1.md、enterprise-industry-options-authority-v1.md；
- remediation/enterprise-migration-schema-test-alignment-v1.md、remediation/enterprise-confirmed-delta-test-expectation-alignment-v1.md；
- reviews/non-mox-modules-mox-reference-independent-review-v1.md、reviews/non-mox-full-independent-review-rerun-v3.md；
- reviews/enterprise-progress-single-source-independent-review-v1.md、enterprise-home-canonical-authority-v4.md 及当前受影响专项。

读取本地：
- D:\BattleMap\local-reports\enterprise-master-merge-report.md；
- D:\BattleMap\local-reports\enterprise-master-merge-candidate-review.md；
- 上述文件引用的真实日志、来源/候选 SHA、备份及各次修复报告；
- 代码仓库适用 AGENTS.md、package scripts、锁文件、实际服务启动和数据库隔离配置。
若文件名不同，先在 local-reports 中枚举、对照标题与 SHA 定位，不创建空报告替代；找不到的证据标 MISSING。

当前已确认字段增量是删除“整体空间（肥肉/瘦肉/骨头）”分类，不删除整体空间金额/跳数；当前业务身份数量为 MOX40、TOB33、ISP24、电力27、大企25。它们不是数据库物理列数，也不是每个 mode 必须渲染的控件数。不要恢复历史41/34/25/28/26预期来通过测试；未授权的其他 Excel 变化不实施。

## 4. Phase 0：保护现场、固定版本与报告

原 rebase 禁止 continue/abort/quit/skip；不删除 .git/rebase-*，不 reset --hard、clean、stash、强制 checkout，不移动 master/来源分支，不重写原历史。已有候选分支也不 amend/强制移动；保留失败证据。

用只读 Git 命令定位真实工作树、git-dir/common-dir、当前操作、reflog 与引用，记录：
```text
AUTHORITY_HEAD
ORIGINAL_WORKTREE / ORIGINAL_OPERATION
SOURCE_SHA（完整企业来源，不是 rebase 中途 HEAD）
MASTER_BASE_SHA（本轮固定目标基线）
FAILED_CANDIDATE_SHA / FAILED_CANDIDATE_PARENTS
MERGE_BASE_SHA
ORIGINAL_REBASE_BRANCH / ORIG_HEAD / ONTO（仅记录，不盲信）
SOURCE_AND_MASTER_REMOTE_STATUS（仅核对已知状态，本轮不 pull 业务仓库）
```
交叉核对前轮报告、分支引用、rebase head-name/orig-head/onto/done/todo 及 reflog。todo 不是工作区备份；不能仅根据 ORIG_HEAD 决定完整来源。

核验此前备份确实含冲突文件、index、暂存/未暂存修改、未跟踪执行依赖和 rebase 元数据，并有校验记录；缺少则先补本地备份。只读扫描也不得泄漏客户/业务数据到远端。

本轮固定产物目录：
```text
D:\BattleMap\local-reports\enterprise-master-remediation-v1\<FAILED_CANDIDATE_SHORT_SHA>\
  plan.md
  report.md
  findings-closure.md
  test-failure-matrix.csv
  transfer-manifest.csv
  docs-inventory.csv
  evidence\
  backups\
```
若同 SHA 已有产物，保留原运行记录，使用 run-02 等新子目录；记录实际 RUN_ROOT。
plan.md 先列精确文件级 WRITE_SCOPE、来源/目标/候选及处置步骤。保留审查原 finding ID；本文件的三类问题不能代替报告中全部 findings。

## 5. docs 排除：先区分文件树与历史

必须分别核对：
1. master 基线已经存在的 docs：不得删除或重写。
2. 来源分支新增/修改的 docs，包括 docs/enterprise/ 的实际文件清单及对应提交。
3. 失败候选的 docs 最终差异，以及它所有新可达祖先中的 docs。
4. 暂存/未暂存/未跟踪的本地报告和文档。

每项记录路径、master/source/candidate blob、变更类型、是否已在 master 历史、归档位置与处置。不要把“50+”当作精确结果。

以下都不能证明 docs 已从历史排除：新增 .gitignore、git rm --cached、在含 docs 的 merge 后补删除提交、恢复最终 docs 目录、创建归档标签。普通 merge 会保留来源祖先；最终树清理与历史清理是两件事。

如果 docs 仅是未提交文件且来源全部新祖先均无本次禁止 docs，可在独立新分支按普通 merge 准备不含文档的候选，并证明上述事实。
如果本次禁止 docs 已进入来源/失败 merge 的祖先，不再把失败候选的后续提交当作可交付版本。按第6节制作全新的 CODE_ONLY_NET_DELTA 候选；这不会重写、删除原分支，且原 rebase 不动。

用户此前要求的本地归档标签 enterprise-docs-archive-v1：只在已核实的代码仓库、指向真实包含所需已提交 docs 的完整版本时创建附注标签；存在则核对、不覆盖、不推送。不得指向不明的 rebase 中途 HEAD；未提交文档用文件备份及 hash 保留。标签注明“本地文档归档，非交付/验收通过”。打标签不是这轮代码候选的依赖或历史排除手段。

如果 docs 在本轮 master 基线前已进入主线历史，报告既有边界，不许为了这次要求追溯重写 master。若业务代码库已被推送，也不得谎称从未上传。

## 6. 含文档历史时：新建纯代码交付候选

本节明确授权在本地新分支准备代码净增量候选；不授权更新 master、push、改写来源历史或声称原 feature 分支已做祖先合并。

新 worktree：D:\BattleMap\battle-map-master-code-only-v1
新分支：integration/enterprise-master-code-only-v1
起点：已核实 MASTER_BASE_SHA。
路径/分支已占用时核对用途并追加 -02，不覆盖、不使用 worktree add -B/--force。原 rebase 和失败候选目录保持不变。

### 6.1 搬入可审查的代码净增量，不搬祖先

先对比 master、完整来源、失败候选及共同祖先，建立 transfer-manifest.csv。逐文件记录：来源改动、master改动、失败候选合并结果、是否已知冲突、待移植代码/测试/配置/必要生成物、排除文档/数据的依据。

失败候选仅作为待审材料，不是正确实现 Authority。其自动合并成功的内容也需要语义核对；当前有冲突标记，不能整体复制后立即提交。

可使用 Git 自身生成从 MASTER_BASE_SHA 到 FAILED_CANDIDATE_SHA 的 binary/full-index diff，并按已批准的精确代码路径清单提取；排除 docs 及本地报告/真实数据。要求：
- 使用 Git --output 或二进制安全工具输出 patch，避免 Windows 文本管道重编码破坏内容。
- 不使用 git archive 导出不完整树来代替差异；注意新增、删除、文件模式和二进制变更。
- 重命名跨 docs/代码边界时单独核查；不把文档换目录后混入交付。
- 在起点恰好为 MASTER_BASE_SHA 的新工作树先 git apply --check，再应用。失败停下定位基线/路径差异，不用 --reject、忽略错误或随意三方覆盖掩盖。
- 不 merge/cherry-pick 失败候选或含 docs 的祖先进入新交付分支。
- 原 rebase 中已人工处理的有效代码按备份逐段对照纳入，不能丢失，也不能把半完成冲突文件覆盖到候选。

通过 manifest 逐项证明完整企业功能和 master 独立有效改动保留。缺失既有修复则从明确版本/本地备份恢复，并记录证据；无法判定的语义保持具体 blocker。

### 6.2 明确提交拓扑

CODE_ONLY_NET_DELTA 新提交只以 master 基线及新干净交付提交为父，不以失败 merge 或原含 docs 的 feature 为父。它是经过对照的代码集成候选，不是“原 feature 提交全部成为 master 祖先”。在报告记录 SOURCE_ANCESTRY_IMPORTED=NO 和 CODE_DELTA_COMPLETENESS。

后续可以通过正式 merge 将这条干净交付分支纳入 master，但本轮不执行；是否要求保留原 feature 的完整祖先拓扑必须显式决策，不能同时宣称“保留含 docs 的原祖先”和“本次 docs 历史完全不进入 master”。若现有仓库治理强制原祖先合并，则在完成安全诊断/候选准备后报 HISTORY_POLICY_CONFLICT，不绕过。

## 7. CRITICAL：冲突标记与后端真实合并

先证明标记确实存在于 FAILED_CANDIDATE_SHA 的 blob，不只看磁盘文件：
```text
git show <FAILED_CANDIDATE_SHA>:server.js
git show <FAILED_CANDIDATE_SHA>:server/db/database.js
```
用 git grep 对候选整棵受跟踪源码树扫描原始 <<<<<<<、|||||||、=======、>>>>>>> 标记，并在新工作树、暂存区、最终提交各复查一次。扫描覆盖整个实际生产源，不只这两个文件；测试 fixture 中刻意测试标记的命中需逐项列证据，不能全目录豁免。

git ls-files -u 为空只能证明没有未解决索引条目；git diff --check 只能辅助检查所比较的差异，不能单独证明既有提交整棵树无冲突标记。

每个冲突区块比对共同祖先、master、完整 feature、失败候选和已保存人工修改：
- server.js：导入/导出、路由注册、校验与错误边界、中间件顺序、服务启动；
- server/db/database.js：初始化、CRUD、canonical mapping、客户主键、进展历史读写、migration registry及调用关系；
- 同时检查自动合并成功的直接调用方，防止重复函数、丢失路由、旧列回流、两份 migration registry 或旧进展双写。

禁止只删除标记并拼接两侧、整文件 ours/theirs、拿最新时间戳选代码。冲突解决必须记录语义取舍和对应回归用例。

先在新候选目录使用项目要求的 Node 版本执行：
```text
node --check server.js
node --check server/db/database.js
```
再按仓库真实模块制式检查导入/启动。--check 不执行业务，也不能代替依赖解析和启动冒烟。启动前证明使用隔离临时库/测试配置，不能意外连接真实业务库或使用原工作树旧服务。

build PASS 只记录为该命令实际覆盖范围的结果。读取 package scripts 和构建配置，说明是否覆盖 server；无后端覆盖时不得把前端 build 作为后端可用证据。

## 8. 47 个测试失败：先归因，再修复

保留上轮原命令、日志、执行目录、版本和失败数。先修语法/导入导致的级联失败，再用同一完整命令复现剩余失败；原失败已消失也要注明原因，不能漏报。

test-failure-matrix.csv 每项至少包含：真实文件/用例、失败阶段、错误摘要、原/新候选SHA、预期来源、实际结果、分类、根因、修复文件、前后命令/退出码/日志、状态。47是历史观察，不是允许只修47项或最终总数上限。

允许分类：
- MERGE_SYNTAX_OR_IMPORT：冲突标记、丢 import/export、错误接线等集成损坏；修生产代码。
- MERGE_SEMANTIC_REGRESSION：漏掉既有合法 Contract/CRUD/迁移登记/字段删除等；从正确事实恢复集成。
- HISTORICAL_SCHEMA_EXPECTATION：只执行到旧Vn的测试，却拿当前终态预期；按明确历史版本修测试。
- TRUNCATED_TEST_MIGRATION_CHAIN：测试未调用完整生产链；修测试接线，不造专属DROP或伪账本。
- STALE_FIXTURE_OR_ASSERTION：已有已确认业务增量而fixture/断言过期；先证明生产正确再更新。
- PRODUCTION_MIGRATION_GAP：真实完整升级链或新库终态不符合目标；不是降低测试预期可解决的问题。
- DOC_DEPENDENCY：测试/运行脚本依赖要排除的本地报告；区分纯文档质量测试与真正功能覆盖，不为运行而重新把本地docs纳入交付。
- ENVIRONMENT_OR_PREEXISTING：依赖/环境或主线既有失败；必须有同版本对照证据，不能用猜测豁免。

MOX Schema 核验至少区分：字段 Contract、API对象、业务表物理结构、历史迁移阶段、最新完整迁移终态。保持独立预期列名集合及类型/默认值/空值/主外键/索引适用断言；不从 PRAGMA 实际输出生成自己的 expected。

历史已执行SQL不可编辑、删改、重排、重编号，不改 _migrations/checksum 绕过失败。业务字段数量不等于物理列数。历史fixture保留历史意义，当前完整链覆盖不删。

本轮允许修复在合并时丢失/重复的既有生产接线，必须证明正确接线已存在于双方合法实现且无版本冲突；这不是授权新设计迁移。若两侧同一已执行版本SQL不同，或生产需要新的增量迁移，报 MIGRATION_VERSION_CONFLICT / PRODUCTION_MIGRATION_GAP 并提供建议，暂停该处，不修改历史SQL、不擅自占用新编号；其他独立修复继续。

禁止通过 skip/only、删除有效测试、放松相等为部分包含、全量盲刷快照、恢复旧key/旧列/双写、mock掉被测链或吞异常来归零。文档工具从业务代码仓库移出需逐项证明原用例仅验证本地报告且由独立Authority流程承接；不得删功能断言伪装文档排除。

## 9. WRITE_SCOPE 与不变量

可修改范围须先具体化到 plan.md：
- 新隔离交付工作树中的 server.js、server/db/database.js 及有证据的集成直接依赖；
- 已授权企业分支有效代码/测试/配置净增量，按 transfer-manifest 搬入；
- 真实失败测试及必要 helper/fixture/版本化预期；
- 本项目既有脚本/验证入口中后端语法检查、提交树冲突检查的最小新增门禁；
- 本轮不提交的本地报告与备份。

禁止改业务需求、重构无关主线功能、重新复制五套renderer、全仓升级依赖；只读取本地Excel和现库证据，不修改或上传工作簿/真实数据库。不在 master、原 rebase、Authority 镜像里实施生产修复。

必须保留双方有效实现，包括最新已确认字段增量、共享渲染与options、客户 customer_id、作战进展History单一事实源、只读最新摘要与展开主题/内容输入及独立弹窗、canonical Heatmap/Metric、首页已授权布局/导航和主线其他模块。它们是回归目标，不能据本文件声称已经通过。

## 10. 提交和验证顺序

1. 固定版本/备份，建立 findings、docs、代码搬运和失败矩阵。
2. 建立合规新候选工作树，搬入明确代码净增量；不得带本地 docs。
3. 逐块解决语义冲突，扫描整棵生产源码树，后端语法/导入验证。
4. 在隔离数据库复现并关闭测试失败，验证当前schema及完整生产迁移。
5. 跑企业五模块真实Create/Edit、options/customer、三入口进展、Heatmap/Metric、首页导航和主线受影响功能；再跑原完整测试命令、build、已有lint/typecheck、后端隔离启动/健康与代表性API冒烟。
6. 精确暂存批准代码文件/删除项，不git add .、add -A、commit -a。核查完整暂存diff、路径范围、无docs/报告/数据，hooks正常执行，不--no-verify。
7. 在新交付分支创建本地候选提交，记录SOURCE/MASTER/FAILED_CANDIDATE/NEW_CANDIDATE。发现hook改源码须重新核验，不能拿提交前另一版输出充证据。
8. 从最终提交创建唯一detached核验worktree，在干净可执行源码上重跑完整测试、build、后端语法及隔离启动；确认最终blob、暂存/工作树与受验SHA一致。失败保留可诊断候选并标PARTIAL，不能PASS。
9. 独立审查按下一文档完整执行；本轮不移动 master，不推送任何分支或tag、不发布、不清理原现场。

同一结果须保存命令、cwd、版本、SHA、退出码、日志。PowerShell管道/Tee输出不应掩盖原进程退出码，逐条记录真实exit code。环境不可执行则NOT_RUN/BLOCKED，不能把未跑记PASS。

## 11. 三层交付排除门禁

本轮排除root docs/及确认的本地报告/数据；master原有内容保持：
- TREE：git diff MASTER_BASE_SHA NEW_CANDIDATE_SHA -- docs/ 必须无差异。
- INDEX：新增提交前暂存diff不含本次docs/报告/业务数据。
- HISTORY：枚举 NEW_CANDIDATE_SHA 相对 MASTER_BASE_SHA 新可达的每个提交，检查docs子树及所有父边，不能只看first-parent或最终一次diff；新提交不引入本次禁止的docs版本或祖先。

CODE_ONLY模式额外要求：master基线是新候选祖先；含本次docs的来源/失败候选新提交不是新候选祖先；每项有效代码改动有manifest映射。不能用SOURCE_IS_ANCESTOR=PASS替代净增量完整性，因为该模式本来不导入来源祖先。

普通merge模式也必须满足三层门禁；来源本身含本次禁止docs时不能声称普通merge合规。原master早已有的文档历史不在本轮删除授权内。

标签、原分支和失败候选可在本地保留，仅作为证据；将来发布须单独审批明确refs，不能push --all/--tags/--mirror把归档资料送出。

## 12. 完成门槛和下一步

IMPLEMENTED只表示新的候选已完成本轮实现和自测，不等于独立VERIFIED或master已合入。
必需门禁：
- 候选提交生产源码原始冲突标记0；未解决index项0。
- server.js与server/db/database.js语法、真实后端隔离启动/API冒烟通过。
- docs TREE/INDEX/HISTORY全部通过；原文档/未提交内容本地可恢复。
- 47个历史失败全部有归因和当前证据；完整命令当前失败0，无新skip/弱化掩盖。
- 完整生产迁移终态、旧库数据保留、CRUD round-trip及五模块/主线回归通过。
- CODE_ONLY/普通MERGE模式如实记录，来源代码与主线改动完整性已证明。
- master、原feature/rebase引用及原现场未被本轮移动/清理；不push。

任何门禁未完成返回PARTIAL/BLOCKED并列明可执行剩余范围；新失败同样必须记录。后续新Agent按 integration/enterprise-master-candidate-independent-review-v1.md 做完整合并候选审查，不仅关闭这三类问题。

## 13. 固定短回执

```text
ENTERPRISE MASTER CANDIDATE REMEDIATION V1
RESULT=IMPLEMENTED/PARTIAL/BLOCKED
AUTHORITY_HEAD=
SOURCE_SHA=
MASTER_BASE_SHA=
FAILED_CANDIDATE_SHA=
NEW_CANDIDATE_SHA=
CANDIDATE_MODE=NORMAL_MERGE/CODE_ONLY_NET_DELTA/UNDECIDED
WORKTREE=
CONFLICT_MARKERS_IN_COMMIT=
BACKEND_SYNTAX_AND_SMOKE=PASS/FAIL/NOT_RUN
DOCS_TREE_INDEX_HISTORY=PASS/FAIL/NOT_PROVEN
DOCS_ARCHIVE_TAG_AND_TARGET=
PREVIOUS_FAILURES_ACCOUNTED=
CURRENT_FULL_TEST_FAILURES=
SCHEMA_AND_MIGRATION=PASS/FAIL/NOT_RUN
SOURCE_CODE_AND_MASTER_PRESERVATION=PASS/FAIL/NOT_PROVEN
BUILD=PASS/FAIL/NOT_RUN
ORIGINAL_REBASE_AND_MASTER_UNCHANGED=YES/NO
REPORT_PATH=
BLOCKERS=
NEXT=INDEPENDENT_CANDIDATE_REVIEW/CONTINUE_REMEDIATION/NEED_HISTORY_OR_MIGRATION_DECISION
```

## 14. Git与Node命令语义参考

这些资料只解释工具行为，不替代仓库业务Authority：
- https://git-scm.com/docs/git-merge （merge祖先、no-commit/fast-forward边界）
- https://git-scm.com/docs/git-worktree （工作树与分支占用保护）
- https://git-scm.com/docs/git-diff （两棵树差异、binary/full-index及check范围）
- https://git-scm.com/docs/git-apply （patch校验与应用）
- https://git-scm.com/docs/git-rev-list （新可达提交范围）
- https://nodejs.org/api/cli.html#-c---check （仅语法检查，不执行业务）
