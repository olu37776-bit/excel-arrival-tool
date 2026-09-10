# 企业作战地图 Authority 文档索引

**状态：CURRENT AUTHORITY INDEX**  
**指导文档仓库：olu37776-bit/excel-arrival-tool / enterprise-battle-map-authority**  
**业务代码：D:\BattleMap\battle-map；目标主线：master**  
**Authority镜像：D:\BattleMap\BattleMapenterprise-authority**

## 0. 当前任务：字段、API与持久化单源重构计划，先执行P0调查

用户最新要求由云端制定抽象架构和重构计划，本地Agent结合真实实现先调查、提出落地方案，随后按获授权的文件级范围实施。用户进一步明确：版本SQL用于对已有数据库执行一次变更；真正的维护问题是改字段需要手工同步CREATE TABLE、INSERT、SELECT/API、config、UPDATE函数、Metric Contract六处。

**当前主计划：`refactoring/field-api-persistence-single-source-refactor-plan-v1.md`**

```text
D:\BattleMap\BattleMapenterprise-authority\docs\enterprise-battle-map\refactoring\field-api-persistence-single-source-refactor-plan-v1.md
```

当前只执行主计划P0，技术调查复用 `investigation/field-api-sql-and-startup-ownership-survey-v1.md`，不重复创建泛化调查。主计划第16节为当前短回执；旧专项第12节是兼容的历史调查回执，不替代主计划新增的六点矩阵和landing-plan。

```text
CURRENT_PLAN=FIELD_API_PERSISTENCE_SINGLE_SOURCE_REFACTOR_V1
CURRENT_PHASE=P0_SURVEY_AND_LOCAL_DESIGN
PRODUCTION_WRITE_SCOPE=EMPTY
LOCAL_LANDING_PLAN=PROPOSED_NOT_AUTHORIZED
VERSION_SQL=RETAIN_VERSIONED_ONCE_SUCCESSFULLY_APPLIED_MIGRATIONS
MAIN_GOAL=REMOVE_DUPLICATE_MANUAL_FIELD_DEFINITIONS_NOT_REMOVE_MIGRATIONS
SIX_MAINTENANCE_ROLES=CREATE_TABLE/INSERT/SELECT_API/CONFIG/UPDATE/METRIC
STARTUP_FAILURE=USER_REPORTED_ROOT_CAUSE_NOT_PROVEN
FULL_PROJECT_REVIEW=REMAINS_IN_SCOPE
NEXT_GATE=P1_ARCHITECTURE_AND_WRITE_SCOPE_FREEZE
CODE_PUSH_MERGE_TAG_OR_REBASE_CHANGES=NO
```

本轮已发布抽象目标及后续P1—P5阶段计划，但本地当前只收集真实代码事实、复现/归因、列出保留/派生/删除入口、提出文件级WRITE_SCOPE、Bootstrap/事务方案与VerificationPlan。不能仅凭计划存在就开始重构；不能把所有六处搬到一个shared文件后仍各维护一遍。

版本SQL仍保留：成功应用并可靠登记后不重复执行，失败不能假登记。要消除的是CREATE最新版清单、INSERT/SELECT/UPDATE/API重复字段映射；Metric只在实际统计业务或字段引用语义变化时修改，显示名/物理列变化不能迫使改公式。

此前用户报告protected migrations与cannot start a transaction within a transaction，描述启动顺序建表→JSON→migration。P0继续追首个原始错误、第一/第二BEGIN拥有者、结构版本/账本和落盘；不预判JSON导入是根因，不直接调顺序或删历史事务语句。前轮冲突标记、docs混入和47测试失败是历史线索，不能推定当前已关闭或仍存在。

云端未访问本地最新完整代码、日志和实际数据库，不声称实现已收敛。当前master、分支、手动修改、Git操作和实际服务版本由本地核实；原rebase或失败候选仅按真实状态保留，不继续旧合并任务。

## 1. 分工与产物边界

云端负责架构、业务边界、阶段/验证门禁、根据本地证据冻结正式WRITE_SCOPE并维护GitHub文档。本地负责真实文件/函数/SQL/API调查、方案与后续获授权实施；独立Review负责验证实际生产路径与维护成本，不接受自报PASS。

GitHub Authority继续存指导文档，本地拉取。业务代码库的本次docs、报告、Excel与真实DB不提交、不上传；master原有文档保留，不重开用户已关闭的文档合并请求。应用必须的可执行Contract属于源码，不因为名字含配置就当docs排除。

P0复用以下专项产物根，历史run保留：
```text
D:\BattleMap\local-reports\field-api-sql-startup-survey-v1\<SURVEY_SHORT_SHA或SNAPSHOT_ID>\run-001\
```
已有同一版本调查先引用，再补主计划要求，不重新造一套相同Evidence。关键新增产物为 `six-point-maintenance-matrix.csv`、`landing-plan.md`、`field-change-rehearsal.md`，以及可转交云端的脱敏 `handoff.txt`。详细结构按主计划第14节。

独立全项目Review仍使用：
```text
D:\BattleMap\local-reports\battle-map-full-review-v1\<版本>\run-001\
```
双方可引用同一版本证据；并行只读时独立测试DB/报告，不能竞争写入或缩减全项目范围。旧docs报告可读取但不新增提交，旧要求“报告一起入库”在本轮不适用。

## 2. 正式 Authority 与执行入口

阅读旧实施文档只提供业务目标和历史线索，不授权在P0中修改。主计划定义新重构目标，现行模块Contract继续定义业务语义；结构目标不等于已经实现。

| 文档 | 用途与状态 |
|---|---|
| `refactoring/field-api-persistence-single-source-refactor-plan-v1.md` | **CURRENT主计划**：抽象架构、六处处理、保留版本SQL、P0调查/本地方案、P1冻结及后续实施、维护演练与验收 |
| `investigation/field-api-sql-and-startup-ownership-survey-v1.md` | **P0技术清单**：字段/API/SQL真实归属、重复定义、操作差异、启动事务/版本；复用原证据，不独立开竞争任务 |
| `../project-review/battle-map-full-project-independent-review-v1.md` | **CURRENT全项目Review**：18类范围继续有效，专项提供深入证据，不缩减非企业覆盖 |
| `integration/enterprise-master-candidate-failure-remediation-v1.md` | 前轮候选修复规范，用户改为手动处理；非当前执行任务，仅历史/回归依据 |
| `integration/enterprise-master-candidate-independent-review-v1.md` | 原候选审查范围；集成/文档/Schema规则参考，不限完整Review边界 |
| `enterprise-contract-architecture-v5.md` | 企业canonical、共享机制、API/DB、Progress单一事实源；后端单源派生的具体重构按新主计划补齐 |
| `architecture/enterprise-runtime-field-options-contract-v1.md` | fieldDef静态metadata与动态options唯一来源、错误边界 |
| `mox-canonical-authority-v6.md` | 当前MOX业务目标，已同步确认增量；40个业务身份，不是物理列数 |
| `tob-canonical-authority-v2.md` | 当前TOB业务目标，已同步确认增量；33个业务身份 |
| `isp-canonical-authority-v2.md` | 当前ISP业务目标，已同步删除分类与行业选项；24个业务身份 |
| `power-canonical-authority-v2.md` | 当前电力业务目标，已同步删除分类与行业选项；27个业务身份 |
| `large-enterprise-canonical-authority-v2.md` | 当前大企业务目标，已同步确认增量；25个业务身份 |
| `enterprise-excel-confirmed-delta-v1.md` | 仅删除指定分类字段、更新大企名称；用户此前报告完成，当前核对实际代码 |
| `enterprise-industry-options-authority-v1.md` | ISP/电力/大企已确认行业选项，保持既有目标 |
| `enterprise-home-canonical-authority-v4.md` | 当前完整首页目标，第18节展示/布局/单位/标题；不受旧DEFERRED约束 |
| `remediation/enterprise-migration-schema-test-alignment-v1.md` | 历史SQL不改、按版本测试、真实完整链与物理列集合；本轮读其规则不执行修复 |
| `remediation/enterprise-confirmed-delta-test-expectation-alignment-v1.md` | 过期预期、fixture、真实回归分类；不削弱测试 |
| `integration/enterprise-review-snapshot-preparation-v1.md` | 可运行版本与证据规则；P0版本/报告按新计划，不代用户提交 |
| `reviews/non-mox-modules-mox-reference-independent-review-v1.md` | 原完整企业机制审查基线，不只看已知finding |
| `reviews/non-mox-full-independent-review-rerun-v3.md` | 新HEAD完整范围重审，历史finding额外回归，主动发现新问题 |
| `reviews/enterprise-progress-single-source-independent-review-v1.md` | 五模块Progress三入口、主题/内容、父记录、历史保留、最新投影、无双写 |
| `reviews/enterprise-home-and-excel-delta-independent-review-v1.md` | 首页/确认字段增量联合核验，旧证据不代新SHA |
| `reviews/mox-end-to-end-canonical-independent-review-v1.md` | MOX既有审查，旧PASS不延伸当前版本 |
| `remediation/five-module-shared-form-renderer-convergence-v3.md` | 五模块真实共享渲染目标，历史实施/回归基线，不重造表单 |
| `remediation/five-module-shared-operation-convergence-v1.md` | 共享操作生产路径基线 |
| `remediation/tob-shared-form-production-path-repair-v1.md` | TOB残留本地builder修复，用户此前报告完成，当前仍核验 |
| `remediation/enterprise-form-options-root-cause-remediation-v2.md` | f.options根因修复回归；用户此前确认Create/Edit可打开 |
| `remediation/enterprise-customer-data-fetch-unification-v2.md` | customer_id查询/标准化/保存关系链回归 |
| `remediation/enterprise-empty-option-removal-v1.md` | 仅移除字面“（空）”选项，placeholder请选择，真实空值规则保留 |
| `remediation/enterprise-home-route-blocker-repair-v1.md` | 首页真实点击导航修复基线 |
| `investigation/enterprise-form-progress-legacy-parity-survey-v2.md` | 底栏、同一进展结构与主题/内容映射的历史本地输入 |
| `investigation/enterprise-form-scroll-progress-survey-v1.md` | SUPERSEDED，历史背景 |
| `investigation/enterprise-runtime-implementation-survey-v1.md` | 历史运行链规范；当前需真实代码证据 |
| `investigation/enterprise-excel-v0.1-v0.2-diff-survey-v1.md` | 未确认差异只读；两项增量及行业选项按专属Authority |
| `remediation/mox-4-group-render-chain-repair-v1.md` | 历史MOX四组断链修复回归 |
| `remediation/mox-end-to-end-canonical-convergence-v1.md` | 历史canonical收敛，旧数量以当前业务目标更新 |
| `remediation/non-mox-modules-mox-reference-alignment-v1.md` | 历史四模块对齐；实施PASS曾被独立审查推翻 |
| `remediation/non-mox-alignment-independent-review-findings-remediation-v2.md` | 历史7个阻塞回归，不限制完整范围 |
| `remediation/non-mox-shared-form-renderer-convergence-v1.md` | SUPERSEDED BY FIVE-MODULE V3 |
| `reviews/non-mox-alignment-independent-rereview-v2.md` | SUPERSEDED BY FULL RERUN V3，不仅复核7项 |
| `integration/parallel-module-integration-plan-v1.md` | 历史worktree集成，不授权当前合并 |
| `integration/local-worktree-layout-v1.md` | 历史布局，当前实际Git与报告优先 |
| `reviews/authority-consistency-audit-2026-09-07.md` | 历史文档对账，不是当前验收 |

## 3. 重构不得改变的已确认业务与架构边界

### 3.1 字段与分组

各模块自己的Field Contract定义业务集合，不因master旧实现恢复已废弃字段，也不复制MOX业务字段。MOX四组“客户信息/无线格局/微波格局/作战情况”，其他四模块三组“客户信息/业务格局/作战情况”，真实共享Renderer消费它们。

已确认Excel增量只删除“整体空间（肥肉/瘦肉/骨头）”分类，金额/跳数保留；大企名称“大企（油气矿、广电、交通）”。40/33/24/27/25是业务身份数，按mode/visibility产生UI/API投影，不能直接作为物理列数。未确认V0.2变化不实施。

业务语义/config与后端绑定可以按职责拆文件，但不得新建完整重复schema。src/config契约归属和既有有效结构优先保留；跨端纯模块拆分须在P1依据代码冻结，不能未经许可重新铺目录。

### 3.2 API与CRUD

同一字段的身份、逻辑类型、单位与基础规则只定义一次；API的Create/Update/Read按操作引用，不要求字段集合全相等。服务端允许写入策略/对象权限不能由UI readonly/hidden代替。

常规SQL列/alias/参数/读回来自唯一后端持久化绑定与操作投影，取消重复完整清单。服务端不接受任意客户端表/列，也不能把整个req.body自动UPDATE。关系、最新投影、复杂业务JOIN保留必要专属语义，不生成普通列双写。

新字段需要明确声明参与哪些操作，不能为“只改config”自动扩大接口暴露。字段变更演练检验减少的是机械重复维护，不要求业务决策、迁移和测试也全部消失。

### 3.3 Customer、Options与Progress

fieldDef/Contract是静态type/control/editor来源；runtime model不创建第二份schema。Customer真实ID贯穿查询、normalization、options、payload与持久化，不以同名首条关联。
Progress History是唯一持久化事实源，battleProgress是最新/当前投影。新增/编辑都有只读最新摘要、可展开新增按钮、主题/内容两个可编辑输入；独立进展弹窗是另一入口，不替代表单内能力。不能恢复业务text双写/fallback。跨模块与父记录关系、取消/失败、历史保留须回归。
用户认可的双滚动/既有视觉不为重构而改。旧报告的“已修”或“待报告”均不代当前代码事实。

### 3.4 Metric、Heatmap与首页

企业Metric/Heatmap以canonical key引用，label仅展示。Metric维护统计公式与条件，不重复DB列/基础类型；label/物理列名变化且语义不变不应修改Metric。字段删除/单位含义/统计规则改变则必须明确处理真实业务影响。
首页仍按V4及第18节：目标/实时并列、单一M$后缀、三卡/空间拓展布局与指定对齐等高、企业专项蓝色、ISP&大企汇总三个模块和正确导航。重构不重新设计这些需求；非企业模块按各自Authority回归，不强套企业规则。

### 3.5 版本SQL、建库与事务

版本SQL保留，已执行历史不得编辑/删改/重编号/重排，不改账本/checksum消除失败。成功应用且可靠登记后才跳过，失败不假登记。
当前CREATE最新版字段清单不再独立手写：P0对比完整版本链建库A与受验证生成快照B，提出一项推荐；P1只冻结一种实际路线。旧库仍走批准的版本转换；最新字段定义不动态改变旧SQL。快照方式不允许伪造历史数据迁移成功。
建表、JSON输入格式/生命周期、迁移起始/目标版本、事务拥有者及export/写盘必须一致。先证实首个错误和重复BEGIN，再设计，不直接调顺序、删BEGIN、套SAVEPOINT或在真实库COMMIT/ROLLBACK清场。
新库与旧库升级必须以实际物理结构、索引/约束、数据关系和重启持久化证明终态一致，不能拿业务字段数当列数。后端语法/启动与前端build分别验证。

## 4. 当前路径、只读许可与输出

```text
代码：D:\BattleMap\battle-map
目标主线：master
指导文档镜像：D:\BattleMap\BattleMapenterprise-authority
主计划：docs\enterprise-battle-map\refactoring\field-api-persistence-single-source-refactor-plan-v1.md
P0技术清单：docs\enterprise-battle-map\investigation\field-api-sql-and-startup-ownership-survey-v1.md
P0产物：D:\BattleMap\local-reports\field-api-sql-startup-survey-v1\
全项目Review：docs\project-review\battle-map-full-project-independent-review-v1.md
全项目产物：D:\BattleMap\local-reports\battle-map-full-review-v1\
前轮合并报告：D:\BattleMap\local-reports\enterprise-master-merge-report.md
前轮候选审查：D:\BattleMap\local-reports\enterprise-master-merge-candidate-review.md
前轮修复产物：D:\BattleMap\local-reports\enterprise-master-remediation-v1\（若存在，仅历史）
```

已提交实现固定SHA隔离核验；未提交手动成果按全项目Review hash快照规则做诊断，不代提交、不忽略修改去审旧HEAD。实际正在执行的Git操作只记录，不处理。禁止真实库写入、修改生产源码/SQL/现有测试/锁文件、提交或推送；允许自建隔离测试环境与仓库外证据。

不能把本地landing-plan自动当正式实施许可；P0结束等待云端据事实冻结与用户后续实施授权。此处不要求上传业务仓库，本地只交可复制的脱敏handoff。

## 5. 推进顺序

1. 云端发布本计划与索引；本地更新Authority，开始P0，不继续旧合并修复。
2. 固定当前真实版本，复用已有调查，完成六点矩阵、API/SQL链、版本/事务和A/B建库对比。
3. 本地给出REUSE/MODIFY/DERIVE/DELETE/SPECIAL真实文件清单、拟议WRITE_SCOPE、VerificationPlan、MOX试点与推广顺序、变更演练和未决项；返回后停止。
4. P1云端结合handoff冻结职责、文件范围、迁移/Bootstrap/事务与API边界；取得实施授权。
5. P2处理有证据的必需启动止血与共享基础；P3做MOX完整读写试点；P4逐模块接入且回归共享消费者。
6. P5独立完整Review验证新版本、真实维护点下降和业务/数据保留，再交用户验收。旧finding仅回归集，不限制完整范围。

## 6. 状态维护规则

CURRENT阶段在本索引和主计划第0节一致。业务Contract定义目标，本地报告描述对应SHA/快照，实施/Review状态不能互相替代。P0调查COMPLETE不等于应用PASS；Implementation之后也不能自行VERIFIED。

六处维护成本是当前重构的关键验收，不能用增加更多报告/gate替代移除重复定义，不能承诺所有改字段只改一个文件。版本迁移与独立语义测试保留，合法专属业务差异不强行共享。

旧已授权成果和历史证据保留，不因本计划重做所有页面。当前专项技术清单继续适用，不新开竞争调查；全项目Review继续覆盖整个应用。业务语义/数据处置或跨职责改动不明确时给事实和候选方案，不猜测执行。
