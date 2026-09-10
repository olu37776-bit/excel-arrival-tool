# 企业字段、API 与持久化单源重构计划 V1

**状态：CURRENT ARCHITECTURE PLAN；当前仅开放 P0 调查与本地落地方案**  
**指导文档：olu37776-bit/excel-arrival-tool / enterprise-battle-map-authority**  
**Authority 镜像：D:\BattleMap\BattleMapenterprise-authority**  
**业务代码入口：D:\BattleMap\battle-map；目标主线 master，真实分支与版本由本地核实**  
**云端负责架构目标、边界与验收；本地负责代码事实、文件级方案与后续获授权实施**

## 0. 阅读入口与执行状态

本文件是本轮重构的主计划。先完整读本文件，再按 P0 调用既有 `investigation/field-api-sql-and-startup-ownership-survey-v1.md` 的技术调查清单；不要另做一轮与既有调查平行、重复的泛化审查。

```text
CURRENT_PHASE = P0_SURVEY_AND_LOCAL_DESIGN
PRODUCTION_WRITE_SCOPE = EMPTY
DATABASE_WRITE_SCOPE = ISOLATED_TEST_DATABASES_ONLY
LOCAL_IMPLEMENTATION_PLAN = PROPOSED_NOT_AUTHORIZED
NEXT_GATE = P1_ARCHITECTURE_AND_WRITE_SCOPE_FREEZE
```

下面的架构目标与最终验收是重构设计，不表示当前代码已经具备这些机制，也不授权本次调查直接实施 P2—P5。P0 完成就交回事实与方案，不自选“最优实现”直接开始改生产代码。既有全项目 Review 保持完整范围，本专项提供其中字段/API/持久化/启动的深入证据，不取代它。

## 1. 用户问题与本轮目标

用户已明确：版本 SQL 用于对已有数据库执行一次结构或数据变更，成功应用后不重复执行。这项机制必须保留，不是本轮要取消的维护点。

用户报告当前改一个字段至少要手动同步六处：

```text
CREATE TABLE
INSERT 语句
SELECT 语句 / API
config
UPDATE 函数
Metric Contract
```

因此目标不是让 Agent 更仔细地同步六份清单，而是减少同一业务事实的独立手工定义。一般字段改动不应要求重新编辑通用 INSERT、SELECT、UPDATE 实现；显示名变化不应迫使改 SQL、API 身份或统计公式。

另有待调查的启动错误：protected migrations、cannot start a transaction within a transaction，用户描述顺序为建表→JSON 导入→migration。它与字段重复定义可能相互影响，但目前不能认定同根因。必须分别查明字段归属、结构版本和事务归属。前轮冲突标记、47 个测试失败及 Schema 不匹配也是历史线索，不预判当前已关闭或仍存在。

云端没有本地最新源码/数据库。本计划规定目标和判断标准，不虚构真实文件、函数、库版本、旧 migration 编号或已执行结论。

## 2. 分工：架构由云端维护，真实落地由本地提出

| 角色 | 负责 | 不负责 |
|---|---|---|
| 云端架构/文档维护 | 目标模型、唯一来源边界、六处维护点的处理原则、阶段门禁、迁移安全、最终验收；根据本地证据更新 GitHub 正式计划 | 凭记忆猜具体函数或声称看过本地代码；把不明确业务语义直接定成实现 |
| 本地调查 Agent（当前） | 固定真实版本，恢复全部相关生产链，复现/归因，选现有可复用入口，提出精确文件级方案、测试计划和风险 | 修改生产代码、SQL、迁移账本；把本地 proposed 方案自行升级为 Authority |
| 本地 Implementation Agent（后续） | 按冻结文件范围完成代码、必要测试、受控迁移和本地证据；可选择不影响架构/业务的局部实现细节 | 扩大范围、恢复兼容旁路、自行声明 VERIFIED、修改历史 SQL |
| 独立 Review Agent（后续） | 固定新版本，独立核验实际链路、维护点减少、业务与数据不变、报告可信度 | 顺手修代码或直接接受实施报告 PASS |
| 用户 | 确认业务含义、风险和阶段授权，人工验收真实交互 | 不应承担逐文件抄字段和推导事务实现 |

本地可提出真实文件拆分、函数接口、已有库复用及执行顺序；必须给出理由与引用。框架更换、协议变化、历史数据处置、Bootstrap 路线改变、物理列改名或通用层越界均是需返回的决策，不因“结合实际执行”自动放权。

## 3. 范围与不变量

首轮重构对象是企业五模块的字段/config、前后端 API 读写链、SQL 常规读写、受影响新库创建及共享数据库启动。全项目入口必须枚举以发现共享消费者，但不强迫非企业业务改成企业 Contract。共享数据库生命周期改变时，所有使用该连接/初始化入口的非企业模块必须回归。

优先复用当前 Field Contract、Persistence Map、Runtime Projection、现有库和目录；不是重建整个项目。保留用户确认的 `src/config` 契约归属约束。若其中混入 Vue/Pinia/browser-only 依赖导致服务端不能直接用，本地提出纯数据拆分和精确路径，不能未经冻结另造 server/client 两份相同字段定义。

业务不变量按当前 Authority，而非旧报告：
- MOX 四组：客户信息 / 无线格局 / 微波格局 / 作战情况；其余四模块三组：客户信息 / 业务格局 / 作战情况。
- 当前业务身份数 MOX40、TOB33、ISP24、电力27、大企25。不是 SQLite 物理列数，也不是每个模式实际控件数。
- 已确认删除的是“整体空间（肥肉/瘦肉/骨头）”分类，金额/跳数保留；大企名称与行业选项按当前正式规范。
- Customer 使用真实客户 ID 关联；不能按名称取首条。具体旧公共客户接口 `customer_id` 与企业 canonical `customerId` 的边界须查明，不全仓替换字符串。
- Progress History 为唯一持久化事实源；`battleProgress` 是最新/当前投影。新增/编辑表单内只读摘要、展开新增入口、主题/内容及独立进展弹窗都保留，共用 History 操作，不恢复业务 text 双写。
- 首页、指标公式、金额/百分比口径、既有权限、用户已接受的双滚动及样式不趁机重做。

不新增 Excel 自动比对工具，不强制换 ORM/数据库/包管理器，不把本计划做成通用低代码平台，不改未确认字段语义，不顺手修合并/rebase 或清理业务数据。

## 4. 目标架构：每项事实一个来源，不等于所有职责塞进同一文件

以下是职责模型，不要求本地机械创建同名新类或六层框架。现有文件能清晰承担职责则原位复用。

```text
模块可执行字段定义（纯数据/纯规则，无 UI 或 DB 连接副作用）
  │
  ├─ UI 展示投影 → 既有共享 Runtime / Renderer
  ├─ 操作定义（Create / Update / Read 等，按 key 引用）
  │      ├─ 客户端请求构造 / 响应消费
  │      └─ 服务端真实校验 / 序列化 / 允许写入策略
  └─ 服务端唯一持久化绑定（按 key 关联，物理列/关系/转换）
         ├─ 常规 SELECT 列/alias 与读回
         ├─ 常规 INSERT 列/参数
         ├─ 常规 UPDATE 列/参数
         └─ 当前物理结构描述与建库/升级终态校验

版本 SQL：不可变的历史结构/数据转换；成功应用并可靠登记后跳过
Metric Contract：统计业务规则；引用 key，不重定义物理列与基础字段语义
```

### 4.1 唯一来源表

| 事实 | 唯一拥有者 | 下游仅引用/派生 |
|---|---|---|
| canonical key、含义、逻辑类型、单位、允许值等基础规则 | 当前模块可执行字段定义 | UI、API 校验、codec、Metric 引用 |
| label、分组、顺序、控件/formatter ID | 字段 UI metadata / 既有展示配置 | Table/Create/Edit/展示文本；不是 SQL 身份 |
| 某个操作读/写哪些字段，required、不可变项 | 操作策略，按字段 key 引用基础规则 | client payload、server validator、serializer、repository 投影 |
| 身份/对象级访问权限、跨字段业务不变量 | 服务端操作/业务服务 | 运行时授权与事务编排；不能由前端 visibility 代替 |
| 物理列名、存储类型及必要存储编码、表/关系 | 唯一后端持久化绑定 | SELECT/INSERT/UPDATE/读回/物理结构检查 |
| 金额/份额等逻辑值与存储值转换 | 唯一明确 codec，绑定引用 | 各类数据库读写；UI 格式化只是显示，不能重复缩放 |
| 查询的业务选择、JOIN、聚合与分页 | 查询/读模型定义 | 常规字段片段来自绑定；复杂业务查询可显式存在 |
| 指标公式、where、aggregate | Metric Contract | 计算和点击筛选共用条件 |
| 旧版本如何升级 | 对应不可变版本 SQL 与受治理 runner | 新库/旧库执行路径；不读取最新字段生成旧版本 DDL |

物理拆文件可以，重复定义同一事实不可以。操作 required 不必等于数据库 NOT NULL；API 可省略字段可能由服务端或数据库提供已定义默认值。差异要有一处明确策略，不能分别猜值。新增字段默认不能自动暴露在全部 API 或变成全部操作可写。

### 4.2 前后端共享的范围

前后端可共享基础字段语义和公开的操作形状/派生物；后端物理表名、SQL、连接和敏感授权逻辑不为“共享”而直接导入浏览器。共享不意味着运行时加载 GitHub Markdown、Excel 或本地报告。应用需要的可执行定义属于代码交付，不属于被排除的文档。

优先直接复用无副作用的纯模块与已有工具。如确有语言/模块系统边界需要生成产物，规定唯一生成源、生成命令、可复现校验与禁止手改；不能让产物再成为第二份手工 Authority。不得新增一份 schema 后继续保留旧活动 config/mapper 不删。

## 5. 六处维护点的具体处理原则

| 当前维护点 | 重构方向 | 完成证明 |
|---|---|---|
| config | 从已存在有效定义中选唯一入口，补齐缺的职责信息；不要新旧双轨 | 同一事实的保留入口唯一，所有活动调用方真实引用 |
| CREATE TABLE | 消除独立手写“当前最新版字段清单”；第7节选择一种可验证的 Bootstrap 路线 | 以后新增普通字段不再额外手改 createTables 长列表；新建与升级终态一致 |
| INSERT | 从操作可写字段与持久化绑定生成列、占位符及参数 | 列与值从同一有序entry序列产生，新增字段无需改通用 INSERT 函数 |
| SELECT / API | 读投影声明需要的 key；物理列、alias、codec 由绑定提供；请求/响应按操作定义校验与派生 | 不在 route/query/serializer 再抄三份列名与类型；list/detail 真实调用，非仅 helper 存在 |
| UPDATE | 从已授权且本次实际提供的字段与绑定产生赋值 | missing 不清空、0/false/null按策略保留、不可写字段拒绝，函数无逐字段赋值模板 |
| Metric Contract | 保留统计规则，依稳定 key 取值；去掉重复列名、基础类型/单位映射 | label/物理列改名且语义不变时 Metric 无需编辑；统计本身变化才改其业务规则 |

这是六种角色，不预设恰好六个文件。P0 必须按实际代码统计每个事实有多少“需要人工同步的地方”；合法引用、历史迁移和有意的查询投影不是重复配置。

版本 SQL 单列为必要升级工作，不算要消灭的第七份重复运行定义。测试/数据转换/明确操作策略仍可能需要人工维护，不承诺所有变化只改一个文件。

## 6. CRUD/API 的实现约束

### 6.1 通用数据访问机制的最低职责

常规读写可由现有 helper 演进，不要求完整 ORM。模块入口如 updateMoxNetwork 可以保留，负责明确的业务操作并委托共享机制，不能继续内部逐列手写另一份 schema。

概念流程如下，名字不是指定生产 API：
```text
resolveRead(module, operation, actor)
  → 已授权 read keys
  → 唯一绑定 / 必要关系读模型
  → 列 / alias / 参数 / codec

resolveWrite(module, operation, input, actor)
  → 严格输入与服务端权限验证
  → 此操作允许且本次存在的 keys
  → 唯一绑定和存储编码
  → 同一entry序列生成列与values
```

必须满足：
- table/column/sort 标识符来自受信绑定和允许集合；输入值用参数绑定。不能从客户端接受任意表/列字符串。SQLite 参数用来绑定值，不应被当成替换表名的机制。[S3]
- SELECT 不用 `*` 掩盖投影；不把查询返回的全对象自动作为 UPDATE。
- INSERT missing/default/null、UPDATE missing/null、空字符串、0、false 分开处理；删除字段值必须遵守显式清空规则。
- 无可更新字段时有明确结果，不能生成非法 SQL 或把空更新当全量覆盖。必须由服务端限定目标 ID/模块/权限，不能意外无 WHERE 更新全表。
- 未知 key、缺 mapping、重复 canonical identity、重复物理列写入、缺 alias/结果必需列、未知 codec 等可诊断失败；合法空关联可返回 null，不伪造默认0吞结构错误。
- 并发/多步操作事务由该操作的唯一拥有者编排；helper不能随意BEGIN、COMMIT或export打断外层事务。
- 公共请求/响应 envelope、HTTP状态、行为在纯重构时保持；确需清除现存legacy入口时先枚举所有调用方并在同一获授权切换范围迁完，不能偷偷改变外部协议。
- 查询里的技术主键、关系连接键等可以由受信查询机制补齐，不因 UI 不显示被遗漏；它们不自动变成客户端可写字段。

### 6.2 关系与派生不是普通列

字段绑定至少能区分普通持久化字段、关系属性、计算/最新投影和技术列。形式由本地依据已有模型提出，不强制增加复杂枚举框架。

Customer显示属性来自客户关系；项目 customerId 与客户名称不能混用。Progress最新摘要属于读模型，追加/编辑历史是命令；保留专属操作，不把摘要UPDATE到业务text列。复杂JOIN/最新记录选择/聚合允许显式查询，但基础列片段必须引用唯一绑定；要证明1:N关联不放大项目行数、分页和金额，latest排序在相同时间等情况下行为确定并有业务依据。

### 6.3 Metric 与过滤

Metric保持自己的公式，不直接抄SQL物理列。字段 label/order/物理列改变且语义不变，不应改Metric。字段删除或语义/单位真正改变会影响统计业务，必须显式决策，不能自动改key后假称公式无变化。

前端和数据库侧若同时执行统计/筛选，同一业务条件来源需明确，NULL/数值/枚举等执行语义须测试一致；不为满足“共享”引入本轮未需要的通用查询语言。

## 7. 数据库生命周期：版本 SQL 保留，当前结构不得再独立手写

### 7.1 冻结原则

“执行一次”指每个数据库中成功应用并可靠登记后跳过，不是尝试过即跳过；失败不能假登记。当前字段定义描述目标，版本 SQL 描述从某一状态到另一状态的转换。最新字段变化不能动态改变已发布/执行的历史 SQL。

同名表存在时，CREATE TABLE IF NOT EXISTS 不会更新其列结构。[S1] 因此自动生成当前CREATE也不能代替旧库升级。

P0 必须比较以下两种落地路线，给出一个有事实依据的推荐；P1只冻结一个实际运行路线，不长期保留两份手写最新结构。

**A：完整版本链建库，优先评估。** 新库从明确不可变的基础版本经真实版本 SQL 到当前；旧库从已成功版本继续。createTables仅委托初始化链或保留必要不变基础，不再人工追随每次字段新增。当前持久化定义提供目标结构与终态验证，历史SQL仍是升级步骤。需验证历史脚本能从空库启动、数据依赖/JSON时机、启动成本和已有迁移账本语义。

**B：生成的当前结构快照建库，仅在A有实际障碍时评估。** 当前结构从唯一持久化定义生成，有明确版本、生成来源和可复现检查；空库使用快照，旧库执行历史版本SQL。快照初始化与成功版本记录必须是明确批准的基线协议，不能对失败旧库补账或声称未执行的数据迁移已经执行。证明快照包含该版本所有必需数据/约束/初始化结果，新建与真实升级语义等价；不能“先建最新表，再无差别重放所有旧ALTER”。

本计划不授权直接选B后批量写_migrations，也不授权删库、重建现网表或仅改账本消除报错。若二者都不能安全满足现有数据需求，记录具体障碍并返回，不由本地猜测历史数据处置。

### 7.2 JSON与事务

JSON明确是何版本输入、第一次/每次/显式导入、哪些数据不可覆盖，依赖的结构版本是什么。它不承担偷偷改schema或填迁移账本的职责。不能仅因为抽象图写“迁移后导入”就调换当前函数，历史迁移若依赖旧格式数据必须单独冻结步骤。

SQLite的BEGIN事务不能用另一条BEGIN嵌套。[S2] P0追溯：第一BEGIN拥有者、第二BEGIN拥有者、相同连接、最早错误、成功/异常/提前返回的事务状态、版本登记、export/写盘及启动失败后是否仍放行应用。

未来要求每次迁移/操作有明确事务拥有者、可靠成功记录与失败恢复。历史脚本自带BEGIN与runner包事务存在冲突时，先查清实际执行模式和原子性；不得正则剥除历史事务语句、统一换SAVEPOINT、直接COMMIT/ROLLBACK清场。具体适配必须在P1冻结，不能用“只执行一次”掩盖半成功状态。

若实际驱动为sql.js，核实真实版本及export/save实现，区分数据库事务提交、内存状态和文件可靠保存；在隔离库做重启/写盘失败证据。不能将API可读数据直接视为迁移与持久化已成功。

启动关键迁移失败应被明确上报并阻止把数据库声明为可写就绪；业务是否有经授权只读降级模式需核实，不由本地新增。

## 8. P0：现在执行的调查与本地方案

### 8.1 输入与安全固定

读取本文件、authority-index.md和既有专项调查V1；企业各模块、行业选项、确认Excel增量、全项目Review及迁移测试规则按专项引用读完整。读取代码库实际AGENTS.md、package/lock、配置、真实生产入口与已有本地报告。

固定AUTHORITY_HEAD、SURVEY_HEAD或SNAPSHOT_ID、actual branch、master引用、实际运行目录/驱动。已提交则在隔离固定SHA核验；未提交手动成果按全项目Review快照规则冻结并如实标注，不代提交、不仅审旧HEAD。Git若仍进行rebase/merge只记录完整性风险，原现场不处理。需要动态复现时先核实不会连接真实DB/外部写服务。

先复用已有同一版本调查证据；若已有专项报告，补本计划要求的六点矩阵和落地方案，不重新执行所有无变化检查。不同SHA只复用被证明等价的部分，不能直接继承结论。

### 8.2 实际调查的交付物

执行既有专项V1各技术检查，并额外明确：
1. 五模块的config、CREATE、INSERT、SELECT/API、UPDATE、Metric六种维护点每个真实文件/函数、行号/调用方、独立字段清单与派生关系。未用项给证据，不按口述假设全部模块一样。
2. 每个模块当前全部业务字段在API和持久化的映射完整性；每种绑定/控件/codec类别至少一条动态代表路径。MOX为首选完整试点，不因页面此前正常就假定其后台映射正确。
3. 请求构造、server校验、query、response、frontend normalization是否重复手写；合法Create/Update/Read差异与漂移分别标记。
4. 建表/JSON/migration真实版本矩阵，启动first/second BEGIN及首个原始失败；失败后是否错误继续登记/启动/保存。
5. 旧SQL/新库CREATE/current mapping哪些是必要历史，哪些是独立维护的最新版副本；A/B建库路线可行性与推荐。
6. 一项普通持久化字段现在修改时实际涉及的文件清单，以及label、物理列名、enum、删除字段、Metric语义变化各情形下哪些改动属于必要业务决策、哪些机械重复。

### 8.3 本地必须提出可执行方案，不只交问题列表

本地 landing-plan.md 必须含：
- REUSE：保留的现有字段定义/映射/函数，真实路径及为何合适；
- MODIFY：在这些入口补什么职责，谁是最终唯一来源；
- DERIVE：哪些列/验证/别名/serializer由什么来源通过哪个机制派生；
- DELETE：准备删除的重复清单、旧helper及全部调用方迁移证明，不能先删仍有人用的能力；
- SPECIAL：关系/History/复杂查询等保留的业务适配与理由，不能用SPECIAL为整套CRUD副本豁免；
- FILE_WRITE_SCOPE_PROPOSAL：文件级计划，shared文件的必要符号/hunk、只读依赖、禁止项、生成物/lock变动需求；
- STARTUP_PLAN：事务原始根因与修复候选、A/B路线选择、JSON位置、版本登记/失败恢复/持久化；不确定点不能伪装成已决；
- API_CUTOVER：现有调用方与请求/响应兼容性对照、保留路径/需同步迁移路径；
- VERIFICATION_PLAN：真实测试命令/文件、缺失测试计划、隔离DB/fixtures、基线失败归因、未来变更演练；
- DELIVERY_SLICES：每步可运行的提交边界、必要依赖、文件单写者、回退/数据恢复风险；不估算无证据工期；
- DECISIONS_NEEDED：云端需冻结的明确选项及证据，不笼统写“请确认架构”。

提出最小方案，默认复用现有JavaScript/Node模块系统，不为重构一次性换ORM或引入代码生成平台。不要拿“文件都在同目录”“公共函数被import”作为消费同一机制的证明。

### 8.4 P0许可与停止点

允许：只读代码/提交/历史/日志；隔离测试/副本；仓库外记录事实、诊断脚本和拟议接口。禁止：生产代码/Contract/SQL/测试/账本修改，真实DB写入，导入真实JSON到业务库，提交/推送/合并/变基/改tag。

P0完成调查与方案后停止，返回第16节回执与handoff摘要。首个启动失败无法动态复现不应阻止已能确定的重复维护调查；标PARTIAL和准确缺口，不能猜根因。调查COMPLETE不等于应用PASS。

## 9. 后续阶段计划（尚未开放执行）

| 阶段 | 工作 | 退出门禁 |
|---|---|---|
| P1 架构/文件范围冻结 | 云端根据P0证据确认唯一来源、现有入口复用、A/B建库路线、事务模式、API边界；把精确文件scope与验证要求写回GitHub执行章节，再取得实施授权 | 已固定实际代码基线、精确scope/单写者、数据保护/恢复方案；重大语义未知为0 |
| P2 必需启动止血与共享基础 | 如启动问题阻断真实验证，先按已证实根因做最小独立修复；再补现有定义/映射的缺失职责、API/SQL通用机制及自身测试。若无启动缺陷则以证据跳过修复 | 历史SQL不变、空/旧库初始化与失败恢复可验证；基础接口可运行，无平行schema；不能把基础helper成功当模块已接入 |
| P3 MOX纵向试点 | 接入MOX真实Create/Update/List/Detail全部现有字段链，UI只做必要接入；带上Customer、Progress特殊绑定、Metric/Heatmap读消费，删MOX重复清单 | 完整原生产路径通过，未接入字段为0，六点维护矩阵减少；第11节变更演练通过 |
| P4 逐模块推广 | TOB→ISP→电力→大企按各自字段接入同一机制；每个模块独立完成读写/回归再继续，不复制MOX业务字段 | 五模块不再各写一套CRUD字段清单；每步MOX及共享数据库非企业回归通过 |
| P5 清理、完整独立Review与交接 | 清理确认无消费者的旧定义，核验实际构建/后端/数据库/历史与交付范围；新Agent重跑约定完整项目Review并验证维护演练 | 全部阻塞关闭，真实完整范围和变更成本证据充分；用户页面/数据验收通过后才交付 |

物理列或业务字段纯重构默认不改；若持久化布局确需变化，版本SQL作为独立获授权增量，在可验证备份/副本上先证明，再明确真实库执行许可。不能用停机重建空库作为默认“回退”。

每个模块切换须让当前部署/候选中一个操作只有一条活动读写路径。开发中可以存在尚未切换的模块，但每阶段记录清楚；测试比较可并行，不能靠长期生产双读/双写/fallback作为迁移完成。P3/P4结束前清除已替代路径，不把五套分支藏进一个shared文件。

## 10. 实施范围与并行原则

当前P0生产WRITE_SCOPE为空。后续只在P1冻结的具体文件/符号范围实施，不使用“整个src/server均允许”替代范围。

预期类别：现有企业字段配置与相关纯规则、操作投影、服务端持久化绑定/常规SQL构造、模块现有调用入口、已证实必要的启动/版本接线、相关测试。server.js/database.js若为共享大文件必须限定功能段，不能顺带格式化/改名全文件增加合并风险。

共享字段机制、schema/ledger、生成物、测试套件接线、lock均只有一名写者；一个生产工作树不允许多个写Agent。局部调查可并行，只读证据按同一版本归并。后续可按阶段提交代码和必要可执行生成物，但业务docs/报告/Excel/真实DB只留本地，不提交、不上传；不自动push、merge或移动master。

云端只把长期架构与执行规范写入Authority仓库；本地报告不是第二套可长期改需求的规范。具体函数命名/代码风格可由本地遵循项目既有实践，但不得改变上述职责与验收。

## 11. 最重要的验收：字段变更演练

P0先用实际文件做纸面/清单演练，不改生产。P3以后在自建测试模块/隔离schema变体中调用真实共享实现验证；测试专用字段不得混入真实企业需求或真实数据库，不用第二套测试生成器冒充生产。

| 演练 | 允许的人工语义改动 | 不能再要求手工改 |
|---|---|---|
| A 仅改label、顺序或UI分组 | 对应UI metadata；必要独立展示预期 | SQL/API身份/UPDATE函数/Metric公式 |
| B 新增普通持久化字段 | 字段声明、唯一物理绑定、显式操作策略与必要版本迁移；独立验收测试 | 通用CREATE最新版列列表、INSERT/SELECT/UPDATE的逐字段函数体和API重复schema |
| C 物理列改名，canonical与含义不变 | 唯一绑定与获授权版本迁移/数据验证 | UI请求/响应key、Metric公式、每条CRUD手工换列名 |
| D 修改枚举或合法空值 | 该规则唯一来源、需要的历史数据策略与测试 | 在UI/API/DB helper分别抄一套相同新枚举；漏改后靠空数组/默认值兜底 |
| E 删除字段 | 删除当前声明/绑定，明确受影响操作/指标和历史数据处置，增量迁移 | 留活动旧SQL/别名/fallback；改写已执行SQL |
| F 改统计公式但字段语义不变 | Metric规则与专属业务测试 | config/CRUD列清单/表结构 |

每个演练记录manual semantic edits、necessary migration edits、test edits和generated outputs，分开计数。依据语义重复而非文件数评价；同一事实抄在一个文件六段依然是六处，合法业务投影和历史迁移不能被误扣分。

B必须显式检查新字段并非自动授权全部接口；D检查非法值被真实服务端拒绝。C只在测试隔离环境示范机制，不授权生产改名。E若已有Metric引用，必须可诊断并经业务决策处理，不能自动删除指标掩盖影响。

重构完成的核心标准：重复机械性维护点被移除、真实路径消费唯一来源；不是只新增“检查六处一致”的测试。变更演练仍需手改通用CRUD函数或新增另一张字段映射表，则该试点未通过。

## 12. 验证系统与数据安全门禁

### 12.1 自动定义与真实运行都验证

检查单源定义唯一、操作投影/绑定完整且不越权、关系/derived不被误写、codecs/alias唯一、SQL列与参数同序。静态扫描必须列真实生产范围和排除理由，不能把合法历史SQL中的字段字样当活动违规。

动态必须走按钮/页面或实际HTTP入口→生产validator/service/query→隔离DB→读取/回填。不能mock掉核心renderer、mapper、query、migration/History后宣称端到端通过。适当模拟外部服务，但不替代被验证的应用能力。

### 12.2 最小回归矩阵

- 普通字段读写round-trip：非零/0、合法null、缺省、边界数值/枚举；非法输入、不可写字段、unknown key和无权限对象被拒绝且数据不变。
- Update只改指定字段，其余值保留；row ID/customer ID正确；Create/Update不同必填/默认/不可变策略；List/Detail投影不同也各自精确完整。
- Customer真实ID贯穿、不按同名首条关联；进展三入口、父ID/模块隔离、取消/失败、历史保留/最新确定性，无text双写/fallback。
- Metric/Heatmap/首页/筛选仍按原规则与单位；关系JOIN不放大行数；修改label后查询结果/指标不变。
- 新库、真实历史fixture升级、第二次启动、migration中途失败/恢复、JSON失败与重复启动、落盘/重启数据一致。历史SQL hash不变，不能改账本、运行测试专属DDL去伪造终态。
- 五模块共享链与受影响非企业模块回归；后端解析/隔离启动、前端真实构建和必要UI路径、全量现有测试、已有lint/typecheck分别记结果。
- 第11节变更演练及“其他字段生产消费没有漏接”的静态/动态联合证据。

expected不能全由被测生成器生成后与自己比较。适当的派生一致性测试之外，还须有独立语义样例、物理列/关系/版本预期、实际SQL参数与真实DB往返结果。数量相等不足以证明字段相等；业务字段数不可用作物理列数。

前轮47失败按真实日志口径复核、逐项归因；共享问题可分组但保留各用例关联，新增失败另记。不把所有失败视作过期断言，不删测试/skip/弱化断言换PASS。

## 13. 风险与必须返回的决策

以下不能由本地为赶进度猜测：
- 精确业务含义、单位比例、空值/默认/枚举变更、读写权限或外部API协议；
- 某字段到底是业务列、客户主数据、技术关系键、History命令还是派生值；
- 旧DB已被部分改动但未登记、账本与结构冲突的修复策略；
- A/B Bootstrap选择及版本基线/JSON依赖；
- 历史SQL自管事务与runner事务的安全兼容；
- 任何真实库破坏性修改、未经验证重放、迁移编号碰撞/持久化失败恢复；
- 为跨端共享移动契约目录、换库或引入构建生成链的必要性。

对每项写已知事实、推荐方案、替代方案、影响、需要谁决策。其余可完成调查继续，不用一个局部疑问阻塞所有事实收集。云端收到证据后负责抽象和冻结，不用聊天长提示词替代正式计划。

## 14. 固定产物与Authority交接

P0复用既有专项产物根，不再创建第二套相同调查目录：
```text
D:\BattleMap\local-reports\field-api-sql-startup-survey-v1\<SURVEY_SHORT_SHA或SNAPSHOT_ID>\run-001\
```
同目录已存在则核实版本：已有调查作为只读输入；新增run承接其有效证据，不覆盖。既有专项规定report.md、field-lineage.csv、api-contract-diff.csv、query-inventory.csv、startup-transaction-timeline.csv、schema-version-matrix.csv、findings.md和evidence/继续保留；不得捏造空报告凑数。

本计划新增三个关键交付：
1. `six-point-maintenance-matrix.csv`：module、change_scenario、canonical_key、maintenance_role、file、symbol、current_owner、derived_or_handwritten、evidence、target_owner、REUSE/MODIFY/DERIVE/DELETE/SPECIAL、必要人工改动原因。
2. `landing-plan.md`：第8.3节全部内容；包含精确范围proposal、A/B推荐、最小startup修复（如需）、MOX试点及四模块推广、VerificationPlan、回退和未决项。它只是实现建议，不是第二份长期Authority。
3. `field-change-rehearsal.md`：第11节六种演练的当前实际修改点与目标修改点，区分业务、迁移、测试和机械重复。

`handoff.txt`给云端的内容必须足够设计：TOP_FINDINGS原ID+文件/函数+事实、保留的权威定义/映射、需要删除的真实副本、startup首错与两次BEGIN、推荐Bootstrap、建议scope/验证、未决项。控制为可复制摘要，不含真实客户数据、凭据或大段源码；不能仅写计数或“报告里有”。

后续云端据handoff更新本文件的P1冻结章节或链接明确的当前实施附录，并同步索引。文件级范围未获冻结与实施授权前，不能把本地landing-plan当执行许可证。后续实施/独立审查报告继续在local-reports对应阶段与SHA目录，不写代码docs，不上传。

## 15. 文档关系、完成判定与来源

- 本计划负责目标架构、减少六点维护的验收、分工和重构阶段；现有专项调查V1负责逐项技术追踪；二者组合为当前P0入口。
- 本计划不取消现有业务Contract和全项目Review，不继承旧HEAD PASS。不再将历史V3“多处手工同步”当目标；当前普通CRUD由单源派生是本轮设计要求，尚需实际落地。
- P0 RESULT=COMPLETE表示调查与proposal完整，不表示应用或重构通过。关键证据缺失用PARTIAL/BLOCKED；已知缺陷与调查完成可同时成立。
- Implementation以后只能声明IMPLEMENTED；完整独立Review决定VERIFIED。新SHA必须按冻结完整范围重证，旧finding只是强制回归，不是审查上限。

通用技术依据仅用于约束，不能替代本地版本/代码证据：
- [S1] SQLite CREATE TABLE：https://www.sqlite.org/lang_createtable.html 。IF NOT EXISTS不是已有表的升级机制。
- [S2] SQLite Transactions：https://www.sqlite.org/lang_transaction.html 。BEGIN不嵌套，错误后的事务状态要核实；本计划不因此预判具体哪个函数有错。
- [S3] SQLite参数绑定：https://www.sqlite.org/c3ref/bind_blob.html 。值通过参数传递；具体Node驱动接口按本地已安装版本确认。

## 16. P0 最终短回执

```text
ENTERPRISE FIELD API PERSISTENCE REFACTOR PLAN V1 — P0
RESULT=COMPLETE/PARTIAL/BLOCKED
SURVEY_HEAD_OR_SNAPSHOT=
AUTHORITY_HEAD=
CURRENT_BRANCH_AND_MASTER=
SIX_POINT_MATRIX=COMPLETE/PARTIAL
VERIFIED_CURRENT_OWNERS=关键定义与映射的真实文件/符号
RECOMMENDED_REUSE_DERIVE_DELETE=摘要
API_OPERATION_DIFFERENCES=合法差异/真实漂移摘要
STARTUP_FIRST_ERROR_AND_TRANSACTION_OWNERS=
BOOTSTRAP_RECOMMENDATION=A/B/BLOCKED及依据
FILE_WRITE_SCOPE_PROPOSAL=路径
FIELD_CHANGE_REHEARSAL=COMPLETE/PARTIAL
CRITICAL_UNKNOWN_DECISIONS=
REPORT_PATH=
LANDING_PLAN_PATH=
HANDOFF_PATH=
PRODUCTION_AND_ORIGINAL_DB_UNCHANGED=YES/NO
NEXT=P1_ARCHITECTURE_AND_WRITE_SCOPE_FREEZE
```

同时返回handoff.txt的脱敏文本。返回后停止，不自行开始P1之后的写操作。
