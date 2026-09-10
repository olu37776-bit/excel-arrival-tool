# 字段 → API → SQL 与启动事务归属专项调查 V1

**状态：CURRENT READ-ONLY INVESTIGATION / 不授权生产修复或重构**  
**代码入口：D:\BattleMap\battle-map；目标主线master，实际受查分支/版本必须核实**  
**Authority镜像：D:\BattleMap\BattleMapenterprise-authority**  
**本地输出：D:\BattleMap\local-reports\field-api-sql-startup-survey-v1\**

## 1. 为什么调查，当前究竟已知什么

用户最新反馈：实现与预期架构不一致，多轮字段修改后SQL查询字段难维护，API中的字段也不一致。此前启动日志出现protected migrations及cannot start a transaction within a transaction；用户描述启动顺序为创建表→导入JSON→执行migration，页面数据看似正确但多个迁移报错。之前已明确要求调查事务，本专项将该要求与字段/API/SQL归属调查一起落实。

以上属于用户报告。云端未读取本地当前API、SQL、三个初始化函数、完整报错栈或实际数据库；不能提前认定所有问题同根因，不能断言JSON导入必然是事务泄漏来源。protected migrations必须定位项目原始日志输出/调用者，不能凭名字解释含义。

本轮任务不是继续发一轮“全量修复然后自报PASS”，而是回答：
1. 哪些字段事实在不同层由人重复维护？哪些消费者已经自动派生，哪些仅在文档上串联？
2. API差异是同义字段命名/类型漂移，还是合法的查询、命令、关系/投影差异？
3. 查询列、写入列、别名、校验、结果转换分别由谁决定，有没有多套活动定义？
4. 建表、JSON导入、migration各依据哪个Schema版本，谁拥有事务，哪两次BEGIN冲突，最早原始错误是什么？
5. 下一轮最小结构性收敛应复用哪个现有入口、删除哪些重复定义，而不是再叠加一份配置？

本文件只授权调查和隔离复现。第8节是供方案评估的建议，不是已批准的新API/Schema；不得直接照建议重构或修改业务规则。

## 2. 先读已存在的证据，不重新从零泛查

先核实Authority镜像目录/分支及未提交修改，再执行：
```powershell
git -C "D:\BattleMap\BattleMapenterprise-authority" pull --ff-only origin enterprise-battle-map-authority
```
记录AUTHORITY_HEAD。失败保留错误及实际版本，不强制覆盖，不假称最新。

读取镜像中的：
- docs/enterprise-battle-map/authority-index.md、本文件；
- enterprise-contract-architecture-v5.md，特别是API、Customer、Progress、Persistence和验证门禁；
- architecture/enterprise-runtime-field-options-contract-v1.md；
- 五模块当前Canonical Authority及enterprise-excel-confirmed-delta-v1.md、enterprise-industry-options-authority-v1.md；
- remediation/enterprise-migration-schema-test-alignment-v1.md（只用其历史/终态规则，不执行修复）；
- docs/project-review/battle-map-full-project-independent-review-v1.md。
以上相对路径未写完整前缀的，均位于docs/enterprise-battle-map/。

V3可作为历史设计证据：曾允许apiReadField/apiCreateField/apiUpdateField/dbColumn分开描述，并要求多处同步。不得把它过期的分组、字段数、状态或路径规则作为当前目标。V5/current要求与历史描述冲突必须记录来源，不折中实现。

读取本地适用AGENTS.md、package/lock、server.js、实际数据库入口、字段/表单/API契约、生产runner和SQL文件；从local-reports枚举已有全项目Review、启动日志、失败矩阵，按SHA和内容定位。已有对应新版本证据可引用，不复制一个虚构新报告。找不到本地报告继续读代码并标MISSING，不创建空证据替代。

全项目Review继续保留。本专项可作为其API/DB/启动领域的深入证据；同一版本证据允许互相引用，避免两个调查Agent反复跑同一完整测试。若并行，使用各自只读隔离环境和输出目录，不竞争写入报告/测试DB。

## 3. 版本、只读与数据保护边界

用git状态、HEAD、master、worktree list、暂存/未暂存/未跟踪执行依赖核实用户实际当前代码。不要默认原feature分支、旧候选或rebase中途HEAD就是完整目标，不切分支、不解决Git操作。

已提交的完整实现按固定SHA建立或复用经核实的隔离核验环境。未提交的手动改动按全项目Review的WORKTREE_SNAPSHOT规则做hash固定输入诊断，不代提交、不忽略修改去审旧HEAD。报告SURVEY_MODE、SURVEY_HEAD或SNAPSHOT_ID，明确是否实际调查了master。

禁止修改生产代码、业务Contract、运行时映射、API、SQL/Migration、业务数据库、账本/checksum、业务Excel、现有测试或锁文件；禁止commit/push/merge/rebase/reset/clean/stash/abort/quit、修改分支引用、删worktree或创建/推送tag。不要在真实启动前加COMMIT/ROLLBACK“清场”。

允许在仓库外记录清单、日志、必要最小复现脚本及自建隔离测试数据库。运行真实启动入口前必须先确认不会触及真实DB、文件导出路径或外部服务；无法安全隔离就记录NOT_RUN并继续静态追踪。必要的诊断hook只存在于明确标注的隔离复现，不冒称原代码未修改的运行证据，也不得吞错、替换事务或改变SQL含义。

## 4. 字段事实清单：统计“独立维护点”，不是仅统计出现次数

范围：先枚举整个项目的API/SQL入口和共享数据库生命周期；企业五模块完成全部当前字段的深层对账，其他模块的重复定义/共享启动依赖按现有全项目Review证据纳入，不强迫其采用企业业务字段。

每个企业canonical key至少记录：
- 模块、业务含义、当前权威文档条目、可执行字段定义真实文件/符号；
- label、逻辑类型、单位、nullable、enum来源及当前值的表示方式；
- Table/Create/Edit可见/可编辑行为，真实runtime/projector/renderer调用；
- Create/Update/List/Detail请求与响应中该字段的真实位置和名称；
- 客户端payload构造、HTTP client、路由、validator、service及结果serializer；
- SQL SELECT表达式/alias、INSERT列/参数绑定、UPDATE列/绑定、WHERE/ORDER BY、对应table.column或关系/投影；
- JSON/seed/import输入及转换位置；
- Metric/Heatmap/首页/过滤/排序等读消费者；
- 当前DB物理结构、旧/新库及对应版本证据；
- 每一层属于权威定义、引用、自动派生、合法边界转换还是独立手写副本；
- 发现的缺失、多余、类型/单位冲突、旧key、隐藏旁路及运行影响。

不要把customerId与某个名为id的项目主键自动当同义，也不要把customerName当关系ID。大小写/下划线不同不直接代表业务冲突，但必须有唯一明确转换边界，不能各层反复翻译。

“独立维护点”的定义：修改同一个业务事实时，必须由维护者另改此处才能继续正确工作的定义。使用同一个key的多个合法引用不是重复Authority；查询声明选取哪些字段是合法业务选择，但在该查询中再次抄DB列名/单位转换则要追溯来源。

生成field-lineage.csv与ownership-summary.csv，每模块汇总：事实类型、现有权威、重复维护位置、派生/引用位置、影响消费者、证据、建议保留/移除入口。无穷举依据不得报“隐藏消费者=0”。

## 5. API对账必须覆盖六段，不能只查route里一个mapper

逐个实际endpoint记录：method/path、调用方、请求envelope/键集合、校验规则、handler/service、response envelope/键集合、实际消费方。

恢复完整链：
```text
表单/动作输入
→ frontend payload builder
→ HTTP client
→ route request parsing/validation
→ service/database write/read
→ response serialization
→ frontend response normalization
→ 实际页面/统计消费者
```

分别对Create、Update/Patch、List、Detail和已有特殊操作调查。每个差异分类：
- SAME_SEMANTICS_NAME_DRIFT：同义字段命名漂移；
- TYPE_UNIT_NULL_DRIFT：类型、单位、空/缺省规则不一致；
- LOST_OR_EXTRA_FIELD：转换中丢字段/夹带字段；
- DUPLICATE_MANUAL_DEFINITION：相同规则重复手写；
- LEGITIMATE_OPERATION_PROJECTION：创建/更新/读取集合合理不同；
- RELATION_OR_DERIVED_FIELD：关系属性或只读投影；
- IDENTITY_SCOPE_DIFFERENCE：实体/项目/客户/历史ID语义不同；
- EXTERNAL_BOUNDARY_ADAPTER：确有外部协议约束的明确边界；
- UNKNOWN_REQUIRES_EVIDENCE。

重点检验：
1. missing、null、空字符串、0、false是否错误合并；PATCH未提供字段是否被默认值清空；值清空规则是否有Authority。
2. Read字段多于Update是否因为只读客户属性/最新进展，而不是误判接口“必须所有字段相等”。
3. server端是否独立执行允许写入字段/类型/枚举/权限校验；UI readonly/hidden不能作为后端授权依据。
4. 是否将整个req.body或读取返回对象直接UPDATE全部列；是否对未知/旧key静默丢弃或接受；schema只被定义却未接入route的情况。
5. client与server是否使用同一可执行操作定义或派生物，是否各有手写完整properties/required/allowedFields/序列化清单。
6. 是否把DB列名泄漏到企业API，随后又在前端转一次；customer_id在已有客户API中的传输约定与企业canonical customerId的边界准确登记，不能按名字全项目批量替换。
7. Progress新建/编辑表单内录入与独立弹窗的输入是History命令，battleProgress最新摘要是读投影。不得因为属于同一业务领域就认为读写JSON形状必须一致；必须核查它们最终写同一历史模型、父ID/模块正确。

实际运行允许使用已有测试的有效/非法请求和隔离数据，不能测试真实客户记录或伪造成功。日志只保存脱敏代表字段及必要ID，不复制整库内容。

## 6. SQL与映射调查：定位谁还在手写完整字段清单

枚举活动query/CRUD、校验、list/detail、customer查询、progress查询、汇总/heatmap、import/seed入口。不能只搜索SELECT字面量，要追query builder/template/helper/动态列数组及实际调用方。

逐条记录SQL来源文件/函数、调用endpoint、字段集合如何生成、表别名/列名映射、绑定顺序、返回alias、结果对象构造方式、JOIN关系和cardinality。检查：
- SELECT/INSERT/UPDATE三份列表是否独立手写，列与values顺序是否能错位；
- 同一持久化字段是否存在多个column mapping，mapper有定义但未被生产SQL使用；
- raw row→canonical、canonical→legacy→db、response→前端二次重命名是否并存；
- 删字段后查询/排序/聚合/JSON seed仍引用旧列；
- 当前schema没有列却用undefined/null/0静默兜底；
- SELECT *是否掩盖读模型边界或泄漏列；不要用SELECT *替代治理；
- 关联属性是否被错误写入业务表，latestProgress是否被当普通text持久化；
- 1:N progress JOIN是否扩大主记录行数，导致分页、项目数或金额重复；查询取最新值是否确定且与现有业务排序规则一致；
- NULL关系是否因INNER JOIN导致整条业务记录丢失；必须依据当前关系约束判断；
- SQL值绑定与标识符来源：用户值应走参数绑定，table/column/order字段只从受信声明及允许操作中解析，不拼接外部字符串；
- custom SQL是否确有复杂业务需求，可通过canonical字段引用构造，还是重新维护整个字段schema。

输出query-inventory.csv，区分“一份有意的查询投影”和“多份相同字段映射”，不能以SQL条数作为重复数量。用一条模块完整读写链证明改一个普通字段目前要改哪几个真实文件，不停留于列表存在性检查。

## 7. 创建表→JSON→Migration：事务和版本一起调查

### 7.1 恢复真实启动图

从server入口追数据库构造、createTables、JSON导入、migration runner、protected migrations输出、_migrations读取/成功登记、数据库export/落盘。函数名以实际代码为准，不能假定用户举例就是符号名。

记录实际驱动及版本、SQLite版本、每个connection实例的身份、函数调用是否同步/await、是否有重复init/并行启动、同一连接是否重入。首要问题是“第一笔事务是谁开的，第二次BEGIN是谁执行的”，不是先调换三个函数顺序。

对每个BEGIN/COMMIT/ROLLBACK/SAVEPOINT/RELEASE记录所属文件/函数/SQL版本、正常/异常/提前返回路径、调用顺序、连接是否一致、成功账本何时写、失败是否仍继续后续版本。protected migrations的真正职责必须有原代码证据。

### 7.2 先找首个原始失败

优先分辨：
A. runner已BEGIN而SQL脚本自身再次BEGIN；
B. 建表或JSON导入开事务后遗漏结束；
C. 较早migration先因缺列/重复列等报错，未正确回滚，后续版本才连带报嵌套事务；
D. 同一连接初始化/迁移重入或异步顺序错误；
E. 其他有证据的情况。

这些是调查假设，不是预设根因。必须记录最早错误、原stack、具体语句/版本和后续级联关系。失败版本不等于“执行过一次所以应跳过”，核对成功账本是否误记、已有部分修改是否可见、重启是否持久保存。

若驱动提供可靠只读事务状态接口，可记录；没有则按真实SQL顺序、受控故障复现和连接身份证明，不能用尝试BEGIN、COMMIT或ROLLBACK去探测真实库状态。不得假设Python驱动行为等于当前sql.js。

### 7.3 结构版本归属

对照：
- 建表函数创建历史基础schema还是当前最新schema；
- JSON源格式版本、首次/每次导入策略、哪些表/字段被覆盖；
- migration预期起始结构和目标结构；
- 真实物理schema、迁移账本、索引/FK与数据是否一致；
- 空库和历史库各走哪条路径、能否达到相同终态；
- 失败后应用是否仍正常提供写服务，是否误显示启动成功。

数据“看起来正确”不证明版本/事务已正确完成。CREATE TABLE IF NOT EXISTS不会自动把已有表同步到新定义；因此要比较实际列/约束，不能用该语句存在当schema一致证据。

若仍使用sql.js，核实具体export/save实现和调用位置、版本对应行为、写盘失败处理；必须分别证明SQLite事务提交与文件可靠保存。不能在没有证据时断言export必然导致本次报错。

### 7.4 安全复现最小矩阵

在隔离环境用真实初始化路径覆盖：全新库、具有待迁移版本的历史fixture、同一库第二次启动、JSON导入失败、某一migration中途失败后的状态与下一次启动。至少实际复现本次错误或明确无法复现的环境差异；若缺fixture，不伪造历史版本账本来“证明”历史库已升级。

保留实际历史SQL，不删除事务语句、不批量替换BEGIN为SAVEPOINT、不强制登记成功、不删库重建、不吞错继续启动。需要这些改动才运行得通时，应作为后续修复建议和边界，不在本轮实施。

## 8. 待证据确认的收敛方向，不是本轮实施许可

建议评估现有Field Contract与Persistence Map能否通过以下最小变化达成目标，禁止先新增另一套平行Schema或立即更换ORM：

### 8.1 同一业务事实只定义一次，不同职责不混成一份超级对象

业务字段的key、逻辑类型、单位、合法值规则在现有可执行定义中归一；UI仅持有展示/顺序/分组等视图信息。后端保留自身的写权限与业务操作策略，不从前端visible/editable推导授权。数据库列/关系映射只有一个后端来源，不能把物理SQL和服务实现直接打包进浏览器。

允许物理拆文件，但必须说明每个属性/规则的唯一拥有者以及派生链。文档说明目标，代码中可执行定义参与运行；文档本身不是应用运行时依赖。

### 8.2 API做操作投影，不再手抄第二套字段事实

Create、Patch/Update、List、Detail分别有明确操作定义；相同字段的类型/枚举引用主定义，操作仅声明成员、required、read/write权限和必要业务约束。客户端payload、服务端输入验证、输出serializer/类型尽量由该可执行定义派生。特殊操作如History写入保留独立命令语义，不能盲目把读取对象原样保存。

UI字段集合、API read/create/update集合、DB物理列不应被要求全相等；验证各自操作投影的精确预期和合法转换，而不是全字段暴露/全字段可写。

### 8.3 常规SQL由映射产生，保留必要显式业务查询

评估从同一server-side持久化映射和明确的查询/命令字段投影生成SELECT列/alias、INSERT/UPDATE列与绑定、读回对象、允许过滤/排序字段。简单列重复清单可取消；复杂JOIN/聚合/History latest仍须明确业务关系和实现，不能声称一个万能生成器已解决全部SQL。

未知field、mapping缺失、类型不支持应可诊断失败；合法null/空关系按操作定义处理，不用fallback吞掉结构错误。不能在运行时接收任意客户端table/column。

### 8.4 迁移历史与当前运行定义分开治理

当前契约定义目标，历史迁移描述版本转换；不能让最新字段定义动态改写旧迁移。评估优先使用一条版本化生产迁移链处理空库/旧库；若保留快照建库，该快照须可复现且与真实升级终态受验证，不能继续两份手工最新schema。

JSON导入必须有明确输入格式和生命周期，不能暗中修改schema/迁移账本。事务必须有明确拥有者及失败处理，但具体由runner还是已有脚本拥有、如何兼容历史脚本，必须根据第7节证据再设计，不能先删历史BEGIN。

### 8.5 以实际变更成本验证方案

选MOX的代表字段及其他模块一个查询，不改生产代码，在报告完成变更演练：
- 仅改label：哪些代码理论不应改，当前为何还要改SQL/API；
- 普通持久化字段增加：一份字段事实/一个存储绑定/必要新迁移，哪些派生产物自动变化，哪些操作业务策略仍需明确；
- 删除当前已确认分类字段：哪些活动消费者还引用它，旧历史SQL为何允许保留；
- 修改enum/null规则：UI/API/校验如何引用同一语义；
- 关系/Progress变化：为什么不能当普通列直接生成写操作。

输出before/after ownership矩阵及最小试点计划，明确“保留现有哪一份、替换哪些手工副本、哪些差异合法、有哪些必需验证”。不要再提交一个只有增加更多gate、更多报告而不减少维护点的方案。

## 9. 不混淆问题类别与完成条件

每个finding记录原始事实、真实文件/函数/endpoint/SQL位置、HEAD或snapshot、影响、已证实根因/待验证假设、所属类别、最小建议与建议WRITE_SCOPE。

分类至少区分：IMPLEMENTATION_NONCONFORMANCE、DOCUMENT_OR_DESIGN_GAP、DUPLICATE_FIELD_AUTHORITY、API_OPERATION_SEMANTIC_DIFFERENCE、QUERY_MAPPING_GAP、SCHEMA_LIFECYCLE_GAP、TRANSACTION_OWNERSHIP_GAP、TEST_GAP、ENVIRONMENT_GAP、NEED_USER_CONFIRMATION。

不能将所有API差异归成bug；不能把所有测试失败归成过期预期；不能因为规范存在就判实现已收敛；也不能因为一段API和SQL之间有必要转换就宣称架构全错。

调查完成意味着关键链路有证据和缺口解释，不意味着应用通过。结果分为COMPLETE/PARTIAL/BLOCKED；已知严重错误可以使应用状态FAIL而调查COMPLETE。无运行能力继续给静态调查结果，动态未验证必须列明。

## 10. 输出路径与交接

本地产物按<SURVEY_SHORT_SHA或SNAPSHOT_ID>\run-001\保存，已存在递增run，不覆盖历史：
```text
D:\BattleMap\local-reports\field-api-sql-startup-survey-v1\<版本>\run-001\
  report.md
  field-lineage.csv
  ownership-summary.csv
  api-contract-diff.csv
  query-inventory.csv
  startup-transaction-timeline.csv
  schema-version-matrix.csv
  findings.md
  convergence-options.md
  evidence\
```
report.md先列有证据的根因/关键未决点、API/SQL重复维护热点、启动first/second BEGIN及首个失败，再给详细矩阵索引。convergence-options.md只给待决方案，不成为本地第二套长期Authority。

为了云端能据事实写下一版实施规范，另生成可直接复制的handoff.txt：仅包含关键finding ID、每项一两句事实、实际文件/函数、建议与未决点，不含客户数据/源码大段/秘密。短回执与handoff不替代完整本地证据；不要求用户上传整个仓库。

不在聊天仅报“API不统一”“SQL难维护”或自报待建架构PASS。下一阶段由云端依据这些实际位置设计收敛与精确WRITE_SCOPE，本地另一个实施操作执行；全项目Review的既有finding继续保留。

## 11. 技术参考与使用限制

以下仅为通用行为参考，不证明当前项目执行了某段代码：
- SQLite事务： https://www.sqlite.org/lang_transaction.html 。BEGIN事务不支持BEGIN嵌套；具体第一/第二事务拥有者须本地证明。
- SQLite CREATE TABLE： https://www.sqlite.org/lang_createtable.html 。同名表存在时IF NOT EXISTS不更新其结构。
- JSON Schema对象： https://json-schema.org/understanding-json-schema/reference/object 。properties、required、additionalProperties是不同约束；现有validator是否实际启用严格规则须核验。本专项不要求引入JSON Schema或更换库。

技术文档与具体驱动版本不一致时按已安装版本查证，不根据通用文档臆测sql.js连接/落盘实现。不得为了外部查证上传本地代码或业务数据。

## 12. 最终短回执

```text
FIELD API SQL AND STARTUP OWNERSHIP SURVEY V1
RESULT=COMPLETE/PARTIAL/BLOCKED
SURVEY_HEAD_OR_SNAPSHOT=
AUTHORITY_HEAD=
MODULES_AND_ENDPOINTS_COVERED=
DUPLICATE_DEFINITION_HOTSPOTS=实际文件/符号摘要
API_DIFFERENCES=命名/类型漂移与合法操作差异分别列
SQL_MAPPING_OWNERS=现状与旁路摘要
FIRST_STARTUP_ERROR=
FIRST_BEGIN_OWNER=
SECOND_BEGIN_OWNER=
TRANSACTION_ROOT_CAUSE=PROVEN/HYPOTHESIS/NOT_PROVEN及一句话
SCHEMA_INIT_IMPORT_MIGRATION_CONSISTENCY=
RECOMMENDED_REUSE_AND_REMOVE=
NEED_USER_CONFIRMATION=
REPORT_PATH=
HANDOFF_PATH=
NO_PRODUCTION_OR_DB_MODIFICATIONS=YES/NO
NEXT=EVIDENCE_BASED_CONVERGENCE_DESIGN
```
