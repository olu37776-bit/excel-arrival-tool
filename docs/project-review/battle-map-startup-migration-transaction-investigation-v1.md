# BattleMap 启动初始化与 Migration 事务错误调查 V1

**状态：CURRENT / 优先只读调查；未授权修复**  
**业务代码：D:\BattleMap\battle-map；目标主线：master，实际分支/版本须核实**  
**Authority：D:\BattleMap\BattleMapenterprise-authority**  
**指导文档分支：olu37776-bit/excel-arrival-tool / enterprise-battle-map-authority**  
**本地产物：D:\BattleMap\local-reports\battle-map-startup-migration-investigation-v1\**

## 1. 本轮目标与已知事实

用户报告启动时出现 `protected migrations`，多个版本的SQL执行失败，其中有：

```text
cannot start a transaction within a transaction
```

用户描述初始化有三个阶段：先创建表，再导入JSON，最后执行migration；当前业务数据看起来正常，但migration报错。用户认为一个版本的SQL只会执行一次。

以上均为用户转述，尚不是读取当前本地调用栈、SQL、迁移账本和数据库后的核验结论。`protected migrations` 的准确日志文本、输出函数、保护策略、实际失败版本和三个函数的真实名称均待调查。不预设是JSON导入错误，也不预设是SQL文件和runner重复BEGIN。

本轮必须回答：

1. 完整启动链和三个阶段分别由谁调用，是否串行等待，使用几个数据库实例/底层连接？
2. `protected migrations` 是什么实际机制，如何判断待执行、跳过、成功、失败？
3. 第一条原始错误是什么；触发事务错误时，当前事务是谁开启、为何未结束，第二次BEGIN在哪个文件/函数/版本SQL？
4. 多版本失败是独立错误还是首个失败后的级联；失败后如何回滚、继续或退出？
5. 创建表、JSON导入、版本化迁移是否针对同一结构基线，是否重复承担Schema演进？
6. 物理Schema、业务数据、迁移账本和磁盘持久化是否一致；“数据看起来正常”的证据究竟来自哪里？
7. 最小修复应该落在哪些真实函数/边界，需要哪些回归测试，哪些数据状态需要单独处理？

输出调查事实和修复建议，不实施修复、不重建真实数据库、不替迁移补成功记录。

## 2. 与全项目Review及既有规范的关系

本文件是 `battle-map-full-project-independent-review-v1.md` 中启动/数据库/迁移范围的优先深查入口，不替代、不缩减全项目Review。其他已冻结范围可继续独立只读核验，但不得共用可变测试库或旧服务；若代码SHA/快照不同，证据不能混用。

从Authority读取：
- `docs/enterprise-battle-map/authority-index.md`；
- 本文件及 `docs/project-review/battle-map-full-project-independent-review-v1.md` 的版本、安全隔离和证据规则；
- `docs/enterprise-battle-map/remediation/enterprise-migration-schema-test-alignment-v1.md`；
- `docs/enterprise-battle-map/enterprise-contract-architecture-v5.md`；
- 实际涉及的当前模块契约、`enterprise-excel-confirmed-delta-v1.md`及Progress单一存储规范。

读取规范只用于对照目标，不执行旧文档中的实施/提交步骤。历史SQL不可改，当前Schema与历史阶段预期应分开；新建库和升级库都须核验终态。业务身份数量不是SQLite列数，不因旧测试或旧Schema恢复已删除字段。

本地输入包括：适用AGENTS.md、当前启动脚本、依赖锁文件、真实数据库driver、server.js和server/db/database.js（如路径已变则追真实替代者）、初始化/JSON/迁移/保存helper、全部实际登记的SQL、启动原日志、前轮合并/Review/47失败日志及当前全项目Review产物。缺失证据明确MISSING，不生成假报告替代。

Authority更新仅在文档镜像执行：
```powershell
git -C "D:\BattleMap\BattleMapenterprise-authority" pull --ff-only origin enterprise-battle-map-authority
```
先核实目录/分支及未提交文档状态。失败记录真实本地AUTHORITY_HEAD和错误，不自动覆盖、不声称最新。

## 3. 只读边界与安全隔离

### 3.1 严禁操作

- 不修改/提交生产代码、项目测试、依赖锁文件、历史SQL、迁移登记、业务Contract或JSON源文件。
- 不改真实DB及迁移账本，不补成功记录、清空版本表、跳过失败版本、删库重建、手工ALTER/DROP，不在真实库重跑失败迁移。
- 不为消除异常先加无条件COMMIT/ROLLBACK，不把BEGIN批量替换为SAVEPOINT，不剥离SQL事务语句后作为“原脚本复现”。
- 不调整三个初始化函数的顺序来试修；不改保护/checksum规则；不执行当前项目Git提交、merge/rebase/abort/quit/reset/clean/stash/tag/push。
- 不向业务仓库docs或GitHub上传调查报告、源码、JSON、真实DB或业务数据；不要为了获取新日志重启/终止用户正在用的服务。

### 3.2 允许的调查产物

允许在本轮仓库外目录写报告、静态清单、只读诊断脚本、测试fixture、隔离数据库及日志。可以按全项目Review规则使用固定SHA的独立核验worktree；未提交的手动修改必须按hash快照核实，不能悄悄审旧HEAD，也不代提交。

默认先用合成数据与现有测试fixture重现。真实DB必要时只读取一致性副本：先查当前driver和数据库形态，优先使用已有可靠备份。不能只拷贝活动WAL数据库主文件就称完整快照，也不能为备份在生产连接调用可能改变连接状态的export/close。没有安全副本则报告缺口，不停服、不冒险。

复制后的测试库允许原生产初始化/迁移代码写入，仅用于调查。报告区分副本中观察与真实业务库状态；合成fixture成功不能证明实库正常。不要在副本中伪造迁移账本后声称复现真实故障；有意构造的异常fixture必须单独标明。

任何import或启动可能有自动建表/迁移/seed/落盘副作用。执行前必须证明DB输入/输出、备份路径、定时保存和外部连接均指向隔离资源；无法隔离则保留静态结果、动态标BLOCKED，不先运行再检查。

## 4. 固定版本与运行环境

记录以下信息：

```text
AUTHORITY_HEAD
REVIEW_MODE=COMMIT/WORKTREE_SNAPSHOT
REVIEWED_HEAD或SNAPSHOT_ID（以及BASE_HEAD）
ACTUAL_BRANCH / MASTER_HEAD
SOURCE_WORKTREE / INSPECTION_WORKTREE / RUNTIME_CWD
NODE_VERSION / PACKAGE_MANAGER_VERSION
DB_DRIVER_NAME_AND_LOCKED_VERSION
SQLITE_VERSION（只有实际driver允许只读获取时记录）
DATABASE_INPUT_PATH / DATABASE_OUTPUT_PATH
PROCESS_ID / STARTUP_COMMAND / ISOLATED_PORT
ORIGINAL_GIT_OPERATION
```

路径从真实配置和运行参数恢复，不默认进程使用当前目录的DB，不默认仍为sql.js，也不把CLI系统sqlite版本当作应用嵌入版本。

已提交检查提交blob与实际执行文件一致；快照记录可执行文件hash。原rebase/merge若仍存在只记录，不处理；当前状态不足以代表完整项目时明确诊断对象限制。

相关启动源码、migration SQL、注册清单和fixture记录hash。调查前后不改变受审输入；诊断插桩副本另记差异。与其他Review并行时各自测试库、进程和输出目录隔离。

## 5. 静态恢复：真实初始化、事务与迁移机制

### 5.1 找出真实启动链

从实际启动命令一路追踪到数据库对象创建、打开已有文件、PRAGMA设置、创建表、JSON导入、migration、保存、监听服务。分别列首次启动/已有库启动/测试启动的条件分支，不能把用户口述的三个函数名当成代码事实。

逐阶段记录：文件/函数/行区间、调用者、运行条件、输入结构版本、使用连接、BEGIN/COMMIT/ROLLBACK或SAVEPOINT位置、成功返回、异常/提前返回、是否调用save/export、是否等待Promise。检查是否存在重复初始化、多处migration入口、并发启动、async forEach或Promise.all等共享连接交错；出现这些写法只是线索，必须用实际执行证据判断。

### 5.2 protected migrations

从日志原文定位输出位置，再追调用者与真实runner；必要时宽松搜索protected、migration、错误正文，不把“protected migrations”当SQLite内建术语。

回答保护的是哪一项：事务包装、历史版本不可修改、checksum、跳过已应用版本、Schema守卫、异常汇总或其他机制。列实际登记版本、磁盘脚本、执行排序、分组及前置条件，确认是否有两个runner或重复版本登记。不默认只有V34—V38，也不猜版本号。

### 5.3 事务拥有者与脚本执行方式

枚举应用层、driver wrapper、各版本SQL中的真实事务控制：BEGIN的各变体、COMMIT/END TRANSACTION、ROLLBACK、SAVEPOINT/RELEASE/ROLLBACK TO及隐式事务helper。

每项说明谁开启、谁负责结束、下层是否又开启、失败是否结束、是否结束了不属于自己的外层事务。区分SQL触发器/复合语句内的BEGIN...END、字符串/注释和真正事务控制；正则命中不是结论。

核实runner是整段执行还是拆语句执行，检查现存split(';')/正则删除BEGIN等逻辑是否损坏字符串、触发器或事务边界。调查脚本不得自己用简单分号分割来改变原行为；准备所有DDL之后的语句也可能依赖前一语句执行，不能通过一次性预编译全部SQL替代真实runner。

### 5.4 迁移账本与“只执行一次”

查实际表/字段/内存缓存/文件标记，不假定一定只有 `_migrations`。分别恢复：待执行判断、attempt、成功登记、提交、落盘、下次启动读取和skip逻辑。列版本、文件hash、执行条件、账本状态、最后错误及证据。

必须区分：尝试一次、SQL调用返回、事务提交、Schema效果达成、账本登记、持久化完成、下一次启动跳过。不能因为日志说executed或数据库里有某列就自动认定该版本成功应用。

关注失败是否在catch/finally也登记成功，先标成功后执行/保存，成功记录和SQL不在同一原子边界，版本只存在内存未落盘，或失败后循环继续污染后续版本。只记录与现有实现相关的风险，不自行修账本。

## 6. 动态证据：同连接事务时间线

优先读取现有完整启动日志和driver现有trace/debug能力；需要额外观察时只在隔离副本/进程通过外置诊断脚本记录调用。插桩必须保持原参数、this、执行顺序、同步/异步语义、返回/异常行为，不吞异常、不加事务、不改变重试策略。

每次冷启动给RUN_ID，每个数据库JS实例及底层重开代次给CONNECTION_ID/GENERATION；两个实例指向同一文件不等于同一连接。逐事件记录：

```text
SEQ / TIME / RUN_ID / CONNECTION_ID / GENERATION
STAGE / INIT_CALL_ID / MIGRATION_VERSION
FILE / FUNCTION / LINE_OR_SQL_STATEMENT_POSITION
EVENT=ENTER_STAGE/SQL/RETURN/THROW/BEGIN/COMMIT/ROLLBACK/SAVEPOINT/RELEASE/EXPORT/CLOSE/REOPEN/LEDGER_WRITE/FILE_SAVE
SQL摘要与来源hash（不输出敏感绑定值）
CALL_STACK
STATE_BEFORE / STATE_AFTER / STATE_EVIDENCE_KIND
RESULT / ERROR_CODE / ERROR_MESSAGE
```

必须同时保留：本次启动第一条原始异常、第一次开启当前未结束事务的位置、触发第二次BEGIN的精确位置、失败处理中的回滚结果、下一个版本的行为。不要从最后一条nested transaction消息倒推所有版本同根因。

状态取证约束：
- 若当前driver真实暴露可靠只读事务/自动提交状态接口，记录API及版本并使用；SQLite C API存在不等于JavaScript绑定暴露，不臆造PRAGMA transaction_state、db.inTransaction或SQL函数。[S1][S2]
- 若只能从完整调用序列推导，明确STATE_EVIDENCE_KIND=TRACE_INFERRED；wrapper布尔值不等于数据库状态实测。不够证明时记UNKNOWN。
- 不把没有写操作、未读表或sqlite3_txn_state的某个单一返回值直接当成显式BEGIN必已结束；尤其核对DEFERRED事务边界。[S1]
- 不靠探测性执行BEGIN/COMMIT/ROLLBACK判断原连接状态，这会改变被调查对象。
- 发现export/close/reopen后，必须重新识别底层连接代次和状态，不沿用旧观测。

若精确SQL语句位置暂无法观察，保留原脚本完整hash与runner栈，缩小到可证实边界；不能编造行号。可另做更细的隔离诊断，但必须标出与原执行方式的差别。

## 7. 假设矩阵：逐项证实或排除，不预选答案

| 假设 | 必须取得的证据 |
|---|---|
| H1 runner外层事务与SQL内BEGIN重叠 | 同一连接：外层成功开启且未结束→具体SQL内BEGIN失败；给runner/SQL双侧代码与trace |
| H2 创建表或JSON导入遗留事务 | 该阶段确实开启事务，正常/异常/提前返回漏结束，migration使用同一连接并再次BEGIN |
| H3 首个migration先因其他SQL失败，后续事务错误为级联 | 首条非事务原始错误、未完成回滚、后续版本BEGIN；不能只提交后续错误日志 |
| H4 初始化或runner重入/异步交错 | 两次实际调用的时间线、同连接ID及交错事务，不仅是两个进程名或代码里用了async |
| H5 export/save/close使生命周期判断失真 | 实际调用位置、driver版本/行为、重开前后连接/PRAGMA/账本/文件状态；此项是待核对风险，不预设必导致nested BEGIN |
| H6 新建表结构/JSON结构与迁移起点不一致 | 当前各阶段Schema、版本预期、重复建列/搬表/导入证据及首个SQL失败；与事务错误的因果关系需单独证明 |
| H7 观察的代码/服务/DB不是同一版本 | 工作树/SHA、进程cwd、DB输入输出路径、旧dist或副本差异；用户看到的数据与报错属于哪一个实例 |

允许新增有证据的假设；最终区分PRIMARY_CAUSE、SECONDARY_DEFECT、CASCADE_FAILURE和NOT_PROVEN。需要精确说明受影响版本，而不是写“migration整体有问题”。

## 8. 建表、JSON、Migration的Schema职责对账

为以下阶段建立独立对照：打开前原库→建表后→JSON导入后→每个迁移前后→迁移循环结束→保存后重开。记录物理表/列/类型/默认值/约束/索引、账本与受影响数据摘要，不只记行数。

创建表：是历史基础结构、当前最新版结构、仅CREATE TABLE IF NOT EXISTS，还是包含额外ALTER？已有表不会因为CREATE IF NOT EXISTS自动变成最新Schema，具体预期需从SQL/迁移确认。
JSON导入：输入格式属于哪个结构阶段，字段映射/关联键来源是什么，首次导入判定是什么，是否每次启动执行，是否覆盖用户数据，是否调用共享CRUD而间接开启事务/保存。真实JSON只读核对结构与必要脱敏样例，不能上传业务内容。
Migration：声明的起点与前两阶段实际结构是否一致，哪些变更已被前置阶段实施、哪些必须由迁移做；不能仅凭表/列存在就跳过包括数据迁移、约束或索引的整个版本。

必须回答目前三个函数的顺序是：有清晰历史基线且可成立、存在重复Schema所有权、JSON结构阶段不匹配，还是证据不足。调查不自动决定调序，更不把任意“create→migrate→seed”作为无条件修复。

## 9. 数据、事务提交和落盘分别核实

用户“数据都对”目前只作为观察。分别验证：同连接查询、独立只读连接或独立打开持久化副本、通过真实保存流程后重新启动隔离应用，是否看到相同Schema/业务结果/账本。同连接读取未提交结果不能独立证明已经持久化。[S3]

对实际driver区分：
- 原生SQLite文件连接：检查真实文件、journal/WAL及一致性副本方式，不用另起连接造成不受控写入。
- 如果确为sql.js：核实锁定版本、db.export调用及文件写入/替换流程；官方文档说明export会关闭并重新打开DB并重置PRAGMA，但本地具体影响要以锁定实现和隔离复现为准，不直接把在线最新版当当前版本。[S4]

特别检查save helper是否在事务中间、finally、每条插入后或失败后执行；是否导出和账本写入顺序不同；导出成功是否真代表磁盘写入成功；文件保存失败是否被吞掉；重启是否再次从JSON重建使数据“看起来恢复”。调查不得为观察在活动事务中额外调用export改变状态。

验证范围用合成代表值：非零金额/跳数、0/合法空值、客户ID及不同父记录的进展。实体数据、迁移成功记录、落盘结果分别记录；未重开/未证明的项保留NOT_PROVEN。

## 10. 隔离复现矩阵与最小测试范围

先完成原始生产启动基线复现，再做诊断对照，所有用例各用独立初始fixture/库，不跨用前一个失败后已污染的连接。禁止修完再只留下成功日志。

| 用例 | 输入/入口 | 调查目标 |
|---|---|---|
| T1 空库首次启动 | 原生产启动顺序＋最小合法JSON/既有fixture | 建表/导入/首个迁移事务边界与真实第一个错误 |
| T2 真实历史结构升级 | 对应受影响版本之前的历史fixture，经原生产完整runner | 版本顺序、首因/级联、提交/回滚/账本、数据保留 |
| T3 受影响现存库副本 | 已安全取得的一致性副本；无副本则标缺口 | 与用户故障条件是否一致，不让合成测试替代实库事实 |
| T4 已完成初始化的测试库再次启动 | T1/T2实际成功后的库或明确来源的既有成功fixture | 已成功版本是否正确跳过、JSON是否重复、两次启动账本/数据是否稳定；不能手工补成功记录创建此用例 |
| T5 同次失败后的继续与下次重试 | 原runner错误处理，不手工清理事务/账本；新进程使用实际保存结果 | 后续版本是否只是级联，失败是否误标成功，下次运行状态是否一致 |

T1/T2若当前实现失败，原样记录，不能改到通过。可用单个SQL在新连接独立执行与原runner执行作对照，但只能说明包装差异，不能证明完整启动链正确。需要的故障注入仅在合成fixture/外置harness中，说明注入点和与真实错误的区别；不得修改历史SQL本体。

运行现有启动/JSON/迁移/DB相关测试及原47失败中确实相关的用例，记录真实命令、退出码、输入版本和日志。完整项目Review继续负责全量范围；本次不要为追求full build/全量绿灯而扩成全项目修复，也不以build通过结束调查。

## 11. 报告必须给出的判断与后续建议

正文开头给出以下事实摘要，详细证据放后面：

```text
protected migrations实际机制
真实启动顺序与三个函数
PRIMARY_ERROR（启动第一条错误）
当前未结束事务的开启者
第二次BEGIN位置及版本
事务拥有者冲突或泄漏的完整因果链
哪些版本独立失败/哪些级联/哪些未执行/哪些成功
Schema vs账本 vs持久化一致性
数据正常观察是否仅同连接或旧服务
最小修复边界与数据处理风险
```

修复建议必须用真实文件/函数给出，不直接实施。至少说明：保留哪一层事务拥有权、其余层如何协作、错误返回/回滚/成功登记/落盘应在什么边界完成、保护历史SQL如何兼容、现存部分执行状态是否需要另行数据修复，以及应新增哪些生产路径回归用例。

SAVEPOINT是可嵌套的机制，但不能机械替换全部BEGIN：release内部savepoint不等于外层事务或落盘已经成功，rollback to也不等于结束全部事务。[S5] 若建议使用，说明它解决的确切拥有权问题及对当前不可变历史脚本/版本账本的影响。不得默认删历史脚本BEGIN、全局正则剥离事务语句、关闭protected检查、启动前无条件rollback或把有列的版本直接标成功。

本轮发现先记INV-TXN-001等稳定ID，附严重性、版本/输入、实际路径/栈、可复制步骤、expected依据、actual、因果证据强度、最小建议和未来文件级WRITE_SCOPE。根因未证实明确HYPOTHESIS；任何新迁移、数据修复、初始化调序或历史基线采用方案须下一轮明确授权。

## 12. 本地产物与完成口径

根目录：
```text
D:\BattleMap\local-reports\battle-map-startup-migration-investigation-v1\<短SHA或SNAPSHOT_ID>\run-001\
```
已有目录递增run编号，不覆盖旧证据。固定产物：
- `report.md`：唯一综合调查报告，包含最小修复建议，不另造长期业务Authority；
- `startup-chain.md`：真实调用链与各阶段责任/事务拥有者矩阵；
- `transaction-trace.jsonl`：完整关键事件、连接代次、首条异常、回滚与保存；
- `migration-status.csv`：真实版本/hash/登记/执行前后/首因或级联/重开状态；
- `reproduction-matrix.csv`：T1—T5的输入、状态、证据与未执行原因；
- `schema-ledger-persistence.md`：阶段结构、账本、数据与落盘对账；
- `evidence/`、`scratch/`：原始日志、只读清单和必要外置诊断；
- 根目录 `LATEST.txt`：本轮准确路径及结果，便于回传，不上传。

RESULT=COMPLETE仅表示本轮调查范围完成、主要因果链有真实证据，不表示问题已修复。确有复现且程序仍失败可以是调查COMPLETE，APPLICATION_FIXED始终为NO。
动态复现/精确边界/实库状态缺证据时，结论注明限制；关键因果链未闭合用PARTIAL/BLOCKED，不把一段通用嵌套事务示例当当前代码根因。不能写“全部migration已验证”或“数据无损”而没有对应输入/落盘证据。

已有全项目Review不因该专项COMPLETE自动PASS；本轮证据交回其R02/R08/R09/R15/R18相关范围，其他模块仍需完整审查。若全项目Agent在读取同一代码，保持只读、各自隔离DB/输出；任何后续修复需先结束相应受审快照。

## 13. 最终短回执

```text
BATTLEMAP STARTUP MIGRATION TRANSACTION INVESTIGATION V1
RESULT=COMPLETE/PARTIAL/BLOCKED
REVIEWED_HEAD_OR_SNAPSHOT=
DB_DRIVER_AND_VERSION=
PROTECTED_MIGRATIONS_MEANING=
ACTUAL_STARTUP_FUNCTIONS_AND_ORDER=
PRIMARY_ERROR=版本/文件/函数/语句/错误
OPEN_TRANSACTION_OWNER=连接/开启位置/未结束原因/证据类型
SECOND_BEGIN=连接/版本/文件/函数/语句
ROOT_CAUSE=一句话因果链/NOT_PROVEN
CAUSE_CONFIDENCE=REPRODUCED_AND_TRACED/STATIC_ONLY/HYPOTHESIS
FAILED_VERSIONS_AND_CASCADE=
SCHEMA_LEDGER_PERSISTENCE=CONSISTENT/INCONSISTENT/NOT_PROVEN
DATA_CORRECTNESS_EVIDENCE=可证明范围/未证明范围
JSON_IMPORT_ROLE=
EXPORT_OR_SAVE_ROLE=已证实影响/排除/NOT_APPLICABLE/NOT_PROVEN
REPRODUCTION=已执行用例/未执行及原因
MINIMAL_REMEDIATION_SCOPE=
PRODUCTION_CODE_AND_SQL_UNCHANGED=YES/NO
REAL_DATABASE_UNMODIFIED=YES/NO
APPLICATION_FIXED=NO
REPORT_PATH=
BLOCKERS=
NEXT=AUTHORITY_REMEDIATION_DESIGN/COMPLETE_MISSING_EVIDENCE
```

## 14. 技术参考与证据优先级

以下为官方机制参考，不是当前应用已经采用某个driver/API的证据。以本地锁定版本与真实调用链确认适用性：

- [S1] SQLite Transaction，BEGIN不可在既有BEGIN/SAVEPOINT事务中重入，语句错误不保证整个事务结束： https://www.sqlite.org/lang_transaction.html
- [S2] SQLite sqlite3_get_autocommit，C接口与自动提交状态： https://www.sqlite.org/c3ref/get_autocommit.html
- [S3] SQLite Isolation，同连接可见性与不同连接的隔离： https://www.sqlite.org/isolation.html
- [S4] sql.js Database.export，关闭/重开与PRAGMA重置说明；仅在应用实际使用相应版本时适用： https://sql.js.org/documentation/Database.html
- [S5] SQLite Savepoints，嵌套、RELEASE与ROLLBACK TO边界： https://www.sqlite.org/lang_savepoint.html

项目规则（历史SQL不可改、字段/关系目标、本地报告不提交）来自当前Authority和用户确认；SQLite参考用于解释机制，不能据此跳过本地证据。
