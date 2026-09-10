# BattleMap 全项目完整独立 Review V1

**状态：CURRENT REVIEW AUTHORITY / 用户改由手动处理集成后，要求全项目审查**  
**目标代码仓库：D:\BattleMap\battle-map；目标主线：master**  
**指导文档仓库：olu37776-bit/excel-arrival-tool / enterprise-battle-map-authority**  
**本地指导文档镜像：D:\BattleMap\BattleMapenterprise-authority**  
**性质：只读审查与隔离验证，不实施修复，不提交代码，不更新分支，不 push**

## 1. 本轮任务与事实边界

用户最新决定：合并问题改由本人手动处理，现在要求对整个 BattleMap 项目进行全面 Review。不要继续执行上一轮合并候选修复，也不要求先完成旧 remediation 才能开始本轮。

本轮不是企业板块专项，不是 diff-only review，不是只关闭旧 finding，不是仅执行测试或前端 build。范围是当前实际交付状态下的整个应用：所有现存业务模块、页面、后端入口、API、共享组件、状态/数据层、数据库、初始化/迁移、现存导入导出能力、测试、构建、启动与交付边界。

前轮用户转述：server.js 和 server/db/database.js 的候选提交内存在冲突标记；docs/enterprise/ 的50+文件可能进入master；build通过但报告47个测试失败，涉及MOX Schema。它们是本轮强制回归集，不是已经证实仍存在的新结论，也不限制完整审查范围。47的统计口径、具体失败和手动修复结果均须本地核实。

云端没有读取本地最新代码、完整报告和真实数据库。本文件是执行规范，不是全项目已通过的证明。不默认master已更新，不默认rebase仍在进行，也不把旧代码HEAD当作用户刚手动处理的结果。

## 2. Authority、代码与报告的职责

1. 云端继续把指导文档维护在独立Authority分支；本地Agent拉取后执行。不把该仓库的默认分支或Excel工具代码当成BattleMap业务源码。
2. BattleMap源码、配置、真实入口、package scripts、锁文件和适用AGENTS.md用于恢复实际实现；已有本地README/业务文档按其版本和适用范围使用。
3. 企业部分读取镜像中docs/enterprise-battle-map/authority-index.md及当前业务规范。该目录中的企业Contract不能强加到非企业模块；非企业模块依据各自正式需求和已确认行为审查。
4. 非企业业务规则缺乏权威证据时，记录AUTHORITY_GAP/NEED_USER_CONFIRMATION；仍须审查代码一致性、运行链和数据正确性。不把当前代码的行为自动升级成需求，也不因缺需求文档放弃整个模块。
5. 旧implementation/review报告只提供历史事实和回归线索，结论必须绑定其原SHA。文档写PASS、文件名包含shared、组件被import、总测试通过都不能单独证明当前实现正确。
6. 本轮所有报告、日志、临时脚本、截图、测试数据库只留在D:\BattleMap\local-reports\battle-map-full-review-v1\。不写入业务仓库docs，不提交、不上传源码/报告/工作簿/真实业务数据。不重开文档合并请求，不创建或推送tag。

建议先在确认目录/分支无不明改动后更新镜像：
```powershell
git -C "D:\BattleMap\BattleMapenterprise-authority" pull --ff-only origin enterprise-battle-map-authority
```
拉取失败记录实际AUTHORITY_HEAD与原因，不假称最新，不自动覆盖镜像修改。

## 3. 先固定真正要审的版本，不能审错目录

### 3.1 原工作树只读盘点

读取git status、branch、HEAD、master引用、worktree list、暂存/未暂存/未跟踪可执行文件清单，以及真实git-dir中的进行中操作。原目录是D:\BattleMap\battle-map；旧候选D:\BattleMap\battle-map-master-integration及其他worktree仅作为线索，不能自动选最新修改时间的目录。

记录：AUTHORITY_HEAD、ORIGINAL_WORKTREE、ACTUAL_BRANCH、MASTER_HEAD、HEAD、OPERATION_STATE、实际启动目录/命令、是否存在用户手动修改及其归属。结合local-reports中的合并报告确认手动结果在哪里；不凭“完成了”推定全部修改已提交。

禁止commit、amend、merge、rebase、abort、quit、skip、reset、clean、stash、checkout强制覆盖、update-ref、移动master、删除worktree或恢复旧失败候选。不要替用户再次处理Git流程。

### 3.2 已提交：固定提交审查

若目标实现已完整提交，记录REVIEW_MODE=COMMIT、REVIEWED_HEAD及MASTER_REVIEWED=YES/NO，说明master与该提交关系。默认从该SHA建立唯一detached核验worktree：D:\BattleMap\battle-map-full-review-<短SHA>；目录存在则核对，冲突时使用新run后缀，不覆盖。

依赖安装/生成物只能发生在该隔离目录，并按实际锁文件和既有流程；不得改变受审锁文件/源码。不拷贝旧node_modules或旧dist来冒充可复现构建。记录开始/结束源码hash、运行目录、构建来源及实际监听端口，不能连到原工作树旧服务。

### 3.3 手动改动未提交：先完整诊断，不冒称审查了master提交

不得为了形式干净替用户提交，也不得悄悄忽略手动修改只审旧HEAD。在仓库外建立只读输入快照，纳入所有影响运行的已跟踪/未跟踪源码、静态资源、测试、fixture、配置与锁文件，记录文件SHA-256、基准HEAD及差异清单；不要复制真实DB、凭据、node_modules、旧构建和无关资料。

记录REVIEW_MODE=WORKTREE_SNAPSHOT、SNAPSHOT_ID、BASE_HEAD、UNCOMMITTED_EXECUTABLE_CHANGES，继续可完成的全项目静态/隔离验证。核验所需配置使用安全的本地测试配置；不能复制真实凭据到报告。无法完整冻结则明确版本缺口。

这种结果可以给出具体finding，但FORMAL_COMMIT_VERIFIED=NO、整体不得声称master或可交付提交PASS。用户后续提交后须对正式SHA核对内容等价并完成对应审查，不能继承脏工作区的PASS。

### 3.4 原rebase/merge仍在进行

若目标目录尚处于中途操作，明确“当前tree可能不是完整项目”。保留现场，允许对冻结的现状做诊断；正式完整交付门禁记BLOCKED/PARTIAL。其他已冻结完整候选可辅助比较，但不得替代用户实际交付目标。具体缺口单列，不以一次环境问题停止所有独立可审范围。

## 4. 必须先建立全项目清单，再开始逐域结论

从文件系统、路由注册、页面入口、后端挂载、脚本与构建配置交叉枚举，而非只列五个企业模块。对孤立文件、动态加载、全局注册、初始化入口、未在菜单显示的服务同样检查。node_modules/第三方vendor及生成缓存可排除逐行审查，但其依赖/构建/交付角色要记录。

建立以下清单：
- modules.csv：每个实际业务模块、页面入口、API/服务、数据表、所属需求与关键流程；全局首页、导航和所有非企业模块必须出现。名称由实际项目发现，不凭空编造模块。
- routes-and-apis.csv：所有前端路由/动态入口，后端method+path、handler、鉴权/校验/持久化、调用方与验证覆盖；有意只供外部调用的API单独说明。
- data-and-migrations.csv：所有应用持久化表/视图、关系、初始化/seed/import入口、迁移登记及当前目标版本。
- coverage.csv：每项Review ID × 模块/子系统的代码路径、静态证据、动态证据、结论、未覆盖原因。

清单中每一项都必须有审查状态。N/A必须有范围事实；NOT_RUN不是N/A；“未改动”不是免审理由。不能交一份标题为全项目、正文只有enterprise/目录的报告。

## 5. 执行顺序：先发现致命问题，再完成全范围

1. 固定输入与全项目清单。
2. 优先检查提交/快照冲突标记、后端语法/入口、安全隔离、实际启动和数据库初始化，尽早在本地报告记录关键阻塞。
3. 恢复原47个失败并重跑原完整命令；不要等待测试全部成功才开始代码审查。
4. 按第6节覆盖所有Review ID，既查现有问题也查手动合并新引入的问题。
5. 聚合旧finding闭环、新finding、测试失败原因与全项目覆盖缺口，最后形成唯一总报告。

允许本地工具支持时按前端/运行、后端/数据、测试/交付分工只读分析，但所有子审查必须使用同一SHA/快照，不能多人改工作树；总审查者合并证据、去重并负责覆盖完整性。没有子Agent也必须完成同一范围。
发现阻塞不在审查中修复。只有安全、输入完整性或资源风险阻止的动态范围才停止，其他可独立完成的静态检查继续。

## 6. 全项目 Review Matrix

以下是最低完整范围；发现新模块必须纳入相应行，不得以表格未点名为由忽略。

| ID | 领域 | 具体核验 |
|---|---|---|
| R01 | 项目状态与手动集成 | 审查目标是否真实包含手动结果；从共同祖先、原master、完整企业来源及当前代码对照双方有效改动，检查遗漏提交、重复函数、覆盖export、删除有效路由/测试、旧实现回流。无法取得旧SHA则明确证据缺口，不虚构merge-base |
| R02 | 源码完整性与启动 | 全生产源码及关键配置检查冲突标记、语法、import/export、模块解析、环境参数、大小写敏感路径、重复注册、循环初始化；单独核验前端、后端、数据库初始化和现存其他实际启动入口 |
| R03 | 全模块页面与导航 | 所有菜单/路由/首页卡片到实际页面；直接访问、刷新/深链接、非法参数、返回、模块切换、loading/空状态/错误。按现存能力验证页面主要操作，不只看能打开 |
| R04 | 真实业务闭环 | 每个模块最少覆盖一条主要成功链和一条失败链；适用时从新增按钮→初始化→控件/校验→保存→API→DB→重读→编辑回填→刷新。编辑A再编辑B无旧值串用；取消无意外保存；删除/批量操作仅对隔离测试记录执行 |
| R05 | 架构边界和维护性 | 真实依赖方向、重复业务规则、隐藏字段/数据消费者、模块间越权依赖、失效抽象、死代码。用调用链证明共享，不把所有局部适配器/业务不同组件都算重复；非企业模块不被强制改成企业Contract架构 |
| R06 | 前端状态与表单 | 实际store/composable/helper、字段定义/动态状态边界、options来源、响应式失效、请求竞态、watcher/事件清理、重复监听、并发提交、取消/重开/重试；共享表单的按钮和间距、只读与可编辑权限是否保持 |
| R07 | 全部API与服务 | 所有路由挂载/handler/service/data层接线；输入允许集合、类型/空值/边界验证、错误状态码与业务错误、序列化、更新遗漏、重复注册顺序；未知ID/越权ID/非法数据不能静默成功。兼容策略按所属模块Authority，不将enterprise禁旧key机械套到全项目 |
| R08 | 全数据库与持久化 | 所有表/关系、物理列类型/默认值/空值/主外键/索引；真实初始化、事务边界、失败回滚、重复写、进程重启持久化与资源释放；应用若用内存SQLite再导出文件，核查落盘链而非只验证内存查询 |
| R09 | Schema与迁移 | 历史阶段预期和当前完整生产终态分开；新建库与含历史数据库升级一致；登记/顺序/幂等/失败恢复/checksum完整；不得编辑已执行SQL、伪造迁移账本或测试专属改表来掩盖终态错误 |
| R10 | Customer与Progress | 五模块Customer真实ID贯穿query/API/normalization/options/save；Progress三入口到History单一存储、父记录和模块隔离、主题/内容、追加与编辑、最新摘要/刷新、取消/失败不产生误写，不能恢复business text双写/fallback |
| R11 | 统计/图表/筛选 | 全项目实际聚合、Metric、Heatmap、表格搜索/排序/分页、点击筛选与数据来源/单位/空值/0/百分比一致性；企业采用canonical key和同一where，label变动不能改变取值；非企业依其既有字段契约核验 |
| R12 | 已存在的文件/导入导出/初始化 | 确认有哪些真实入口；检查字段转换、编码/大小写/空值、非法文件、边界尺寸、文件路径、失败回滚、ID/历史数据保留；没有该能力则有证据N/A，不临时新增需求或测试真实用户文件 |
| R13 | 安全与数据隔离 | 先核实部署/信任边界；鉴权与对象级权限、输入→SQL/HTML/文件路径/命令等敏感汇点、存储型XSS、路径越界、敏感日志/硬编码凭据、适用CORS/CSRF、上传限制；安全测试仅本地授权测试实例，不对真实系统做攻击或把秘密写入报告 |
| R14 | 性能与稳定性 | 热路径N+1查询、无索引过滤、大量数据全量拉取、同步阻塞、重复图表实例/事件/轮询、取消后的晚到响应、多模块缓存串用；用小型可控测试规模、耗时/查询数/内存证据定位，不编造SLA或跑破坏性压力测试 |
| R15 | 测试可信度 | 测试发现范围、skip/only/todo、吞异常、空断言、镜像式expected、mock掉核心实现、只查Projection不查真实DOM/保存、旧fixture先变新库；确认47失败的统计口径与每个原始用例，新失败另列 |
| R16 | 构建/依赖/配置/交付 | 实际包管理器/锁文件/版本、构建脚本覆盖前后端哪些入口、依赖完整性、安装脚本风险、启动/部署脚本、静态资源/后端文件/Migration的打包遗漏、环境配置默认值与本地路径依赖；不执行audit fix、升级依赖或改锁文件 |
| R17 | docs与历史交付边界 | master原有docs不得误删，本次本地docs/报告/工作簿/真实DB不作为新增交付内容；核验tree/index及相对有效主线基线的新可达历史，标签不等于排除；已被手动合入的禁止内容如实记录，不重写历史/删文件/改tag |
| R18 | 项目整体可运行性与报告一致性 | 在同一受审版本上完成前端构建、后端解析/隔离启动、全模块主要流程、全量测试/必要检查；报告中每个PASS/0/共享都可追到实际证据。明确前端build通过不能替代其未覆盖入口的验证 |

## 7. 企业专属基线：沿用最新规范，不恢复旧数字

企业五模块使用自己的当前Field Contract，MOX四组“客户信息/无线格局/微波格局/作战情况”，其余三组“客户信息/业务格局/作战情况”；实际新增、编辑都进入共享shell/group/field renderer，不接受仅同样式或import未执行。

已确认Excel增量只删除“整体空间（肥肉/瘦肉/骨头）”分类；整体空间金额/跳数保留，大企名称为“大企（油气矿、广电、交通）”。当前MOX40、TOB33、ISP24、电力27、大企25是业务身份数量，不是SQLite列数，也不表示每个mode都应出现这么多输入框。分别按visibility、readonly、relation和special editor验证字段集合、顺序、所属组与值的往返。

Options的静态type/control/editor来自fieldDef/Contract，不能复发f.type缺失导致options未初始化；合法无候选、无值、加载失败与定义错误区分。行业选项按enterprise-industry-options-authority-v1.md；仅去掉字面“（空）”，无值placeholder按规范，不擅自取消合法空值。

Progress History是唯一持久化事实源。新增/编辑均是“只读最新摘要＋可展开新增入口＋主题/内容两个可编辑输入”；独立弹窗与之共用History能力，不能只测独立弹窗而漏表单内提交。记录三个入口的真实endpoint/function/table/父ID；跨模块相同数字ID不能串历史。Create父记录尚未存在时验证原先约定的创建与进展保存生命周期；不自行新增事务/幂等设计，只把实际错误或不明确语义列finding。双滚动是此前用户认可的行为，不能因审查者喜好判缺陷。

企业首页按enterprise-home-canonical-authority-v4.md及确认增量：真实数据聚合、目标占位/实时区别、M$单位、ISP&大企包含ISP/电力/大企、专项/卡片/空间拓展布局与正确路由。不能把历史DEFERRED或旧41字段等说明当成当前目标。

完整纳入以下既有审查范围，而非仅已知finding：
- reviews/non-mox-modules-mox-reference-independent-review-v1.md；
- reviews/non-mox-full-independent-review-rerun-v3.md，并把MOX纳入真实共享渲染核验；
- reviews/enterprise-progress-single-source-independent-review-v1.md；
- reviews/enterprise-home-and-excel-delta-independent-review-v1.md；
- remediation/enterprise-migration-schema-test-alignment-v1.md中的迁移与断言规则。
以上均位于Authority的docs/enterprise-battle-map/，作为审查依据，不授权本轮执行其中写代码步骤。非企业模块同样覆盖R01—R18适用项，不因企业清单详细而被边缘化。

## 8. 冲突标记、后端与47失败的证据要求

### 8.1 不只检查working tree

COMMIT模式同时检查提交blob和实际执行文件；只跑git diff --check或只看未合并index不能证明提交无标记。全生产源码扫描Git常见冲突标记并逐条分类；合法分隔文本、测试夹具中的故意样例不能误判，也不能整目录豁免。单列server.js、server/db/database.js当前存在性、blob/hash、语法与调用入口证据，路径变化须跟踪实际替代者。

根据项目真实Node/语言/模块系统和现有脚本做解析检查；解析通过再核验入口依赖。启动/导入可能触发初始化或迁移，必须先证明测试DB路径和外部连接已隔离，不能先import生产入口再考虑数据安全。记录前后端各自检查命令与退出码。

### 8.2 47失败不能用一个总数结案

先定位原日志/失败矩阵，区分失败用例数、文件数、collection错误及其级联。为每个可恢复原失败记录测试文件/用例、旧错误、当前结果、实际expected/actual与分类；同根因可分组，但保留所有case对应关系。

分类至少包含：SOURCE_SYNTAX、IMPORT_OR_WIRING、BUSINESS_REGRESSION、PRODUCTION_SCHEMA_GAP、MIGRATION_CHAIN_GAP、HISTORICAL_EXPECTATION_MISMATCH、FIXTURE_OR_TEST_GAP、ENVIRONMENT_FAILURE、CASCADE_FROM_OTHER_FAILURE、NOT_REPRODUCED、NOT_PROVEN。MOX Schema的实际名称和缺列由日志/映射核实，不能仅根据用户口述拼写检索一个不存在标识符。

原日志无法取得也要执行当前完整测试，旧47项追溯标EVIDENCE_MISSING，不伪造关闭数量。当前新失败单列。确认是旧预期不代表允许本轮改测试；任何现存必需门禁失败仍须列出，不以“主线原来就这样”免除交付风险。

### 8.3 数据库真实终态

新建库走生产初始化链；升级库从真实历史结构fixture开始走完整生产runner，比较最终独立预期列名/类型/约束/索引和数据，不能只比较列数或用实际输出生成expected。
测试记录非零金额/跳数、0、合法空值、客户关系、多个父记录/多个模块进展，检查保存重读及应用支持的持久化重启路径。不修改已执行SQL、账本或真实业务DB。生产链本身不满足目标就是缺陷，不靠测试侧DROP COLUMN或宽松断言处理。

## 9. 如何证明真正共享、怎样统计隐藏消费者

至少对企业五模块逐一追route/page→新增/编辑action→Contract/projection→runtime/options→实际shell/group/control→提交适配→API→DB→回显。测试必须从真实入口发起，不能直接mount一个生产从未调用的shared组件后宣布页面共享。

扫描范围含页面本地helper、内联HTML/template builder、store、composable、validator、formatter/parser、payload/response mapper、database.js、seed/import及统计/图表转换。扫描数值只对已枚举范围有意义；UNDECLARED_CONSUMERS=0不是“全项目绝无未知代码”的承诺。

每个命中写明file/function、实际可达调用方、业务语义拥有者及分类：合法展示、合法专属业务、薄适配、活动违规、历史迁移、测试样例、确认死代码、未判明。四份模板搬进同一shared文件仍是重复；合法传参/生命周期包装不算另一套表单。非企业独立业务组件不因没用企业renderer就判阻塞。

对比实现报告和当前证据，REPORT_SHARED_BUT_RUNTIME_LOCAL、REPORT_ZERO_BUT_SCAN_NONZERO、REPORT_TESTED_BUT_NOT_PRODUCTION_PATH等记录真实性finding。不要无证据指控执行者意图。

## 10. 动态验证与安全边界

先读取实际package scripts、测试配置、依赖版本和启动代码，再生成可复制命令清单，不猜测端口、health路由、npm script或文件扩展名。

依次执行：源码/配置解析与架构检查→安全隔离的后端初始化和API冒烟→现有模块/数据库/集成测试→前端浏览器主要路径→实际项目全量测试→build与已有lint/typecheck→构建产物代表性运行。可按独立范围并行但不能共用可变测试DB。

测试边界允许模拟外部网络/第三方服务，不可mock掉被验证的应用projection/renderer/query/migration/History机制。网络访问默认限本地测试实例；不得让通知、邮件、收费、删除、外部写操作落到真实服务。

所有写入仅发生在自建隔离测试库/fixture。读取真实库如非必要不做；必要时只读副本且记录来源/脱敏范围，绝不改原库。浏览器无能力运行时记NOT_RUN/覆盖缺口，不伪造截图或视觉PASS。视觉问题能以实际渲染/截图证实时可列finding；产品最终人工验收另列PENDING。

现有测试覆盖不足时，允许把最小复现脚本保存在本轮仓库外scratch目录，通过受审版本真实入口验证；不得改源码/测试/快照来通过。复现需额外依赖或无法隔离时记录建议与缺口，不私自安装全新框架。

依赖风险核验可以只读检查锁文件与可靠公告；联网审计仅在项目允许且不上传源码/凭据时进行，记录版本与适用性，不能把扫描工具风险计数直接当成已证实可利用漏洞。禁止audit fix、自动升级、修改锁文件或关闭校验钩子。

## 11. docs审查边界

指导文档在GitHub Authority分支继续维护；代码库本次docs/enterprise/及其他本地报告不进入交付；master原有docs不得删除。审查不执行清理或归档。

分别记录：当前tree/index的docs、本次相对合并前有效MASTER_BASE_SHA的docs差异、新可达祖先中的本次docs变更、master原有文档是否被删。基线从此前报告/reflog/真实历史核实，不拿当前master与自己比较后报0。

正常merge、squash或代码净增量集成按实际拓扑记录，不能因SOURCE不是祖先就一律判代码遗漏，也不能凭父节点关系证明所有有效行为保留。标签不能消除已有可达历史。

本轮只给DOCS_TREE_STATUS、DOCS_NEW_HISTORY_STATUS、MASTER_EXISTING_DOCS_PRESERVED及证据。若禁止docs已由用户手动合入，仍报告与当前要求的冲突；不擅自视为用户撤销规则，不重写历史或对标签做操作。

## 12. Finding与证据格式

每个finding使用稳定ID BM-FULL-001等，包含：severity、blocking、review ID、模块、实际文件/符号/行区间、REVIEWED_HEAD或snapshot、复现步骤/输入、expected依据、actual、用户/数据影响、根因是否已证实、日志/截图/测试证据、最小修复建议及建议文件范围。

分类：IMPLEMENTATION_NONCONFORMANCE、INTEGRATION_REGRESSION、DATA_INTEGRITY、SECURITY、TEST_GAP、DOCUMENT_DELIVERY_CONFLICT、AUTHORITY_GAP、ENVIRONMENT_GAP、MAINTAINABILITY。根因推断明确标HYPOTHESIS，不把怀疑写成已证实。

Critical通常用于真实入口无法解析/启动、广泛核心功能失效、可验证严重数据损坏或严重安全风险；High用于关键链路/持久化/交付规则失败等。重复代码如违反已冻结共享Authority且仍在生产路径可判阻塞；单纯代码风格或更偏好另一种架构列非阻塞建议，不能为了统一而无限扩大重构。

旧finding保留原ID、旧SHA与本轮CLOSED/OPEN/NOT_PROVEN。当前所有新finding单列；旧7项关闭或module-local builder归零不代表全项目通过。

## 13. 本地产物：固定结构，不污染代码库

产物根：D:\BattleMap\local-reports\battle-map-full-review-v1\
每轮目录：<REVIEWED_SHORT_SHA或SNAPSHOT_ID>\run-001\；已存在递增编号，保留旧结果。

必需产物：
- report.md：唯一综合报告；开头先写Critical/High、当前是否可交付和未验证范围，再写项目地图、运行链、全范围矩阵与结论。
- inventory/ 下 modules.csv、routes-and-apis.csv、data-and-migrations.csv、source-manifest.csv：全项目范围和输入版本。
- coverage.csv：R01—R18逐模块的静态/动态覆盖和证据。
- findings.md：全部发现及最小建议；不在本轮实施。
- previous-findings-closure.csv：旧finding完整追踪；原47用例归入test-failures.csv。
- test-failures.csv：原失败/current失败/根因组/运行结果，不能只写47→0。
- commands.csv与evidence/：cwd、版本、命令、退出码、时间、SHA/快照和日志/截图；敏感信息脱敏。
- scratch/：仅必要复现脚本/测试隔离配置，不成为第二生产实现。

可更新仓库外的LATEST.txt记录本轮目录、REVIEWED_HEAD和RESULT，便于用户定位；不得覆盖上轮综合报告或将本地证据上传指导文档仓库。

## 14. 结论与完成条件

分别报告REVIEW_EXECUTION_STATUS、CODE_READINESS、DELIVERY_POLICY_STATUS、FORMAL_COMMIT_VERIFIED、MANUAL_ACCEPTANCE，不把这些混为一个PASS。

整体RESULT规则：
- FAIL：存在已证实blocking finding或必需门禁失败，即使其他范围因环境未运行也不隐藏已知失败。
- BLOCKED：尚无可成立的完整受审版本，或关键运行/安全隔离缺口使完整核验无法成立；保留已完成诊断。
- PARTIAL：没有已证实blocking，但仍有实质覆盖/需求/证据缺口；工作区快照不得作为正式提交PASS。
- PASS：COMMIT模式下，实际全项目范围已枚举且全部适用范围完成、所有必需测试与构建/后端验证通过、旧blocking可证明关闭、无新blocking、docs交付规则满足、未覆盖项只有有证据的N/A。

FULL_PROJECT_REVIEW_COMPLETED=YES要求所有范围已完成判断；可以完整审查后FAIL。仅跑全量测试、只审enterprise、只审最近diff、只关闭旧finding均不能填YES。

没有浏览器/测试数据库/必要配置不能写PASS；不得把NOT_RUN改成0失败。全量测试PASS也不替代代码/数据/安全/交付审查。PASS仅适用于本轮固定版本及已声明边界，不等于已发布；人工视觉/业务验收未收到用户确认时保持PENDING。

本轮绝不修复、commit、push、移动master、改tag或处理原rebase。审查完成后停止，由用户/后续Authority决定针对发现的修复。

## 15. 最终短回执

```text
BATTLEMAP FULL PROJECT INDEPENDENT REVIEW V1
RESULT=PASS/FAIL/PARTIAL/BLOCKED
REVIEW_MODE=COMMIT/WORKTREE_SNAPSHOT
REVIEWED_HEAD_OR_SNAPSHOT=
ACTUAL_BRANCH_AND_MASTER_HEAD=
MASTER_REVIEWED=YES/NO
FORMAL_COMMIT_VERIFIED=YES/NO
FULL_PROJECT_REVIEW_COMPLETED=YES/NO
MODULES_REVIEWED=x/y（企业与非企业分别列出）
UNREVIEWED_SCOPE=NONE或具体范围
CRITICAL/HIGH/MEDIUM/LOW=
BLOCKING_FINDINGS=NONE或ID与一句话事实
CONFLICT_MARKERS=数量/NOT_PROVEN
BACKEND_SYNTAX_AND_RUNTIME=PASS/FAIL/NOT_RUN
SCHEMA_MIGRATION_AND_DATA=PASS/FAIL/NOT_RUN
PREVIOUS_47_FAILURES=已追溯/关闭/仍失败/未证明数量及口径
CURRENT_FULL_TESTS=通过/失败/跳过数量与退出码
BUILD_AND_ARTIFACT_SMOKE=PASS/FAIL/NOT_RUN
DOCS_TREE_AND_NEW_HISTORY=PASS/FAIL/NOT_PROVEN
CODE_READINESS=PASS/FAIL/NOT_PROVEN
DELIVERY_POLICY_STATUS=PASS/FAIL/NOT_PROVEN
MANUAL_ACCEPTANCE=CONFIRMED/PENDING
REPORT_PATH=
NEXT=TARGETED_REMEDIATION/RESOLVE_REVIEW_GAPS/USER_ACCEPTANCE
```
