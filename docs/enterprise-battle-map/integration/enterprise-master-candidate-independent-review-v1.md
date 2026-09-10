# 企业 master 集成候选：完整独立审查 V1

**状态：CURRENT REVIEW AUTHORITY / 新候选完成后执行**  
**前置：integration/enterprise-master-candidate-failure-remediation-v1.md 已形成固定提交**  
**职责：只读核验，不修改生产代码/测试/数据库迁移，不更新master、不push**

## 1. 审查对象与事实边界

用户报告前候选存在 server.js、server/db/database.js 原始冲突标记、docs/enterprise/ 50+文件混入及47个测试失败；这些是强制回归集，不是本轮全部审查范围。
本轮必须对新的代码候选完整核验企业模块与主线受影响功能，主动发现新问题。旧HEAD的PASS和实施者自报IMPLEMENTED均不能代替本轮证据。
云端只制定规范，实际路径、提交、日志和数据库事实由本地审查者读取；不得要求用户上传业务代码、工作簿或真实数据库。

## 2. 输入与版本固定

Authority：D:\BattleMap\BattleMapenterprise-authority\docs\enterprise-battle-map
读取 authority-index.md、本文件、integration/enterprise-master-candidate-failure-remediation-v1.md 及其全部适用规范。
读取本地 D:\BattleMap\local-reports\enterprise-master-remediation-v1\ 下最新对应候选的 report.md、plan.md、findings-closure.md、transfer-manifest.csv、docs-inventory.csv、test-failure-matrix.csv及证据；结合前轮 enterprise-master-merge-report.md 和 enterprise-master-merge-candidate-review.md 交叉定位，不凭修改时间选错版本。
原代码根 D:\BattleMap\battle-map 和旧候选 D:\BattleMap\battle-map-master-integration 只读，rebase现场不动。新候选目录/分支/模式以实施回执和真实Git记录核实。

记录 AUTHORITY_HEAD、SOURCE_SHA、MASTER_BASE_SHA、FAILED_CANDIDATE_SHA、REVIEWED_HEAD、CANDIDATE_MODE、实际运行目录及原master引用。检查候选无merge/rebase未完成状态、无未提交执行依赖。报告/日志可以留在仓库外，不强求用提交报告清空工作树。
使用固定SHA的干净核验worktree；已有核验目录版本不符时另建唯一detached worktree，不覆盖。仅允许写测试生成物/隔离测试库及仓库外报告，不修改受审源码或锁文件。任何受审源码变化或运行实例不是该SHA，相关结果失效。

## 3. 全范围核验矩阵

必须为以下每项记录真实文件/函数/生产路径、验证方式、日志与结论，不能只填PASS：

| 范围 | 必须独立证明 |
|---|---|
| Git候选与来源完整性 | 完整企业来源已按约定模式纳入、master有效改动未丢、人工冲突解决没有遗漏；不能把rebase中途HEAD当完整来源 |
| 整棵提交树与后端 | 提交blob无原始冲突标记；后端语法、模块导入/依赖及隔离启动/代表性API通过；不能只看前端build |
| docs与历史 | 最终tree、暂存/提交内容、新可达祖先均无本次禁止docs；master已有文档保留；归档tag和备份不上传 |
| Contract/Projection/渲染 | 五模块使用各自当前Contract和同一共享生产渲染链，Table/Create/Edit按visibility/mode双向一致，无私有完整builder |
| Options/Customer | fieldDef metadata权威、select options数组、点击新增/编辑可打开；customer_id从query经normalization到保存不丢失 |
| Progress | 新增、编辑表单内展开录入和独立弹窗三入口共用History写入；主题/内容和父记录关联正确，无text双写/fallback；最新只读摘要正确 |
| Heatmap/Metric/筛选 | canonical key lookup，既有业务结果和点击条件不漂移，标签仅用于显示 |
| API/database.js | 路由/CRUD接线完整，canonical-only边界，主线独立API功能保留，无重复函数覆盖或丢import/export |
| Schema/Migration | 历史SQL不可变，生产完整链与新建库终态一致，物理列独立预期、客户关系/进展历史/金额跳数数据保留，CRUD round-trip |
| 首页/已确认Excel增量 | 首页当前V4及路由、已确认删除分类和大企名称、行业选项等受影响行为不回退；不将未授权Excel差异视作新需求 |
| 主线受影响范围 | 从实际合并diff推导涉及的非企业模块/共享服务，运行对应回归，不能只测企业 |
| 重复机制与隐藏消费者 | 全企业生产源码重扫私有Projection/form builder、label identity、旧key、重复进展写入、私有客户查询和旧schema旁路 |
| 测试可信度 | 测真实生产路径，没有mock掉关键实现、伪造schema、弱化断言或删除有效测试来消灭失败 |

完整执行 reviews/non-mox-modules-mox-reference-independent-review-v1.md 与 reviews/non-mox-full-independent-review-rerun-v3.md 的机制范围，并覆盖MOX；相关历史数量以当前模块Authority/已确认增量为准，不能照旧41等数字回改代码。首页与Progress专属审查要求并入对应范围，不重复设计。
旧7 findings、后续builder finding和这轮候选三类失败按原ID列closure；新finding另编号，不能因历史项关闭而停止审查。

## 4. 代码提交树和后端门禁

检查 REVIEWED_HEAD 的 git show/git grep 结果，而不是只读某个已被手动改好的工作区。整棵生产源码扫描 <<<<<<<、|||||||、=======、>>>>>>>，刻意测试标记/合法分隔文本命中逐条分类，不整目录豁免。
同时核对未解决索引项、暂存diff、git diff --check；这些辅助项不能替代提交树扫描。

在候选真实Node/包管理器版本下执行 server.js、server/db/database.js 语法检查、必要模块解析，随后用项目既有隔离测试配置启动真实后端。确认数据库路径/外部服务不会触及真实业务环境，再执行health及Customer、企业read/write、Progress代表性API。缺少隔离能力则NOT_RUN/BLOCKED，不冒险运行真实库。
读取build脚本与实际产物，记录其覆盖边界；构建通过与后端启动通过分别报告。

## 5. docs排除与集成模式判定

不得仅接受“docs已删除/已打tag/已ignore”的声明。

NORMAL_MERGE：核实master和完整来源的祖先关系、merge父节点和两侧有效内容；所有本次新引入历史必须满足docs规则。若原来源新历史含禁止docs，本模式不合规。

CODE_ONLY_NET_DELTA：独立核实新候选以MASTER_BASE_SHA为祖先，未把含docs的失败merge/来源新提交接入祖先；根据transfer-manifest、共同祖先和双方diff验证功能净增量完整。此模式SOURCE_ANCESTRY_IMPORTED=NO是预期，不能伪报原feature已经祖先合并。

两种模式均验证：
1. MASTER_BASE_SHA与REVIEWED_HEAD的docs/最终差异为0；本次仓库外报告、Excel/真实DB未入提交。
2. 枚举相对MASTER_BASE_SHA新可达的全部提交，检查docs子树及所有父边，不只first-parent；没有本次禁止文档进入历史后又删除的情况。
3. 原master早已有的文档历史未被越权重写。若本次禁止docs早已在master，单独报告限制，不宣布已抹除远端历史。
4. 归档tag指向真实既有文档版本，未提交文档有独立备份；tag仅本地，不是通过标志或排除证明。
5. 原rebase现场、失败候选、master和来源分支引用没有被实施者擅自改动。

仓库治理若要求原feature祖先完整保留而与docs历史排除冲突，报告HISTORY_POLICY_CONFLICT；代码正确不能替代交付策略决定。

## 6. 测试失败与Schema独立对账

复核上轮47个失败的实际口径及每项归因，不能全部当过期测试。对于修复语法后自然消失的级联失败，也需对应当前日志。
比较修复前后测试内容，检查是否skip/only、删除用例、宽松断言、动态生成expected或mock掉真实链；任何弱化造成假通过记BLOCKING_TEST_GAP。

按 remediation/enterprise-migration-schema-test-alignment-v1.md 区分历史Vn结构与当前完整生产终态，检查当前业务字段数与物理列数不同。不得为了通过而改已执行SQL、伪造_migrations、预先把旧fixture变成新schema。
如恢复了合并丢失的既有migration登记，核对来源证据与顺序；如果实质新增了生产迁移设计，检查授权范围，越权即finding。
复跑原完整测试命令和所有必需模块/后端/数据库回归、build及已有lint/typecheck。记录SHA、cwd、命令、版本、真实退出码、日志。未执行/环境阻塞不能记PASS；已知残余失败不能以“主线原来就有”自动豁免。

## 7. 报告与结论

报告只写：
```text
D:\BattleMap\local-reports\enterprise-master-remediation-v1\<FAILED_CANDIDATE_SHORT_SHA>\independent-review-<REVIEWED_SHORT_SHA>.md
```
同名历史报告不覆盖；追加run编号。不得写回代码docs或提交报告。

报告包含完整覆盖矩阵、旧finding关闭表、新finding、docs树/历史清单、语义合并对照、失败分类核验、测试/后端日志、原rebase/master保留证明和剩余授权决策。

RESULT=PASS仅在完整范围执行、全部必需门禁通过、全部阻塞为0时可用。测试/关键环境不可验证用PARTIAL/BLOCKED；任何确定性代码/文档交付/数据完整性缺陷用FAIL。PASS只表示候选通过，不表示master已经更新。
CODE_ONLY模式须明确交付拓扑与来源映射，下一步先确认接受该干净交付分支，再执行另行授权的master落地；不能偷偷按旧“feature直接merge”口径报告。

## 8. 短回执

```text
ENTERPRISE MASTER CANDIDATE INDEPENDENT REVIEW V1
RESULT=PASS/FAIL/PARTIAL/BLOCKED
REVIEWED_HEAD=
CANDIDATE_MODE=
FULL_REVIEW_COMPLETED=YES/NO
SOURCE_CODE_AND_MASTER_PRESERVATION=PASS/FAIL/NOT_PROVEN
CONFLICT_MARKERS_IN_COMMIT=
BACKEND_SYNTAX_AND_SMOKE=PASS/FAIL/NOT_RUN
DOCS_TREE_INDEX_HISTORY=PASS/FAIL/NOT_PROVEN
SCHEMA_MIGRATION_AND_DATA=PASS/FAIL/NOT_RUN
PREVIOUS_FAILURES_ACCOUNTED=
FULL_TESTS=PASS/FAIL/NOT_RUN
BUILD=PASS/FAIL/NOT_RUN
ORIGINAL_REBASE_AND_MASTER_UNCHANGED=YES/NO
KNOWN_OPEN_FINDINGS=
NEW_BLOCKING_FINDINGS=
REPORT_PATH=
NEXT=MASTER_LANDING_DECISION/REMEDIATION/RESOLVE_SPECIFIC_BLOCKER
```
