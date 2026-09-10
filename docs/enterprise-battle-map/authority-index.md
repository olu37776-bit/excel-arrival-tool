# 企业作战地图 Authority 文档索引

**状态：CURRENT AUTHORITY INDEX**  
**指导文档仓库：olu37776-bit/excel-arrival-tool / enterprise-battle-map-authority**  
**业务代码来源分支：feature/enterprise-battle-map；目标主线：master**  
**Authority镜像：D:\BattleMap\BattleMapenterprise-authority**

## 0. 当前唯一任务：修复失败的 master 集成候选

用户最新转述本地候选审查FAIL：
- CRITICAL：候选提交内的 server.js 与 server/db/database.js 残留原始冲突标记。
- HIGH：docs/enterprise/ 的50+文件会随合并进入master，违反本地docs不提交、不上传要求。
- build报告通过，但测试报告47个失败，涉及MOX Schema不匹配；具体失败口径、根因和代码位置由本地报告核实。
- 原业务工作树此前处于rebase；另有merge候选和本地备份。不能以“候选准备完成”当作“master已经合入”。

云端只维护设计/执行规范，没有访问本地完整代码、审查报告或实际数据库；不替本地核验声明PASS。当前不重新设计业务，不重复实施已经完成的表单对齐，先收口这轮集成损坏。

```text
CURRENT_TASK=MASTER_CANDIDATE_FAILURE_REMEDIATION_V1
CANDIDATE_REVIEW=USER_REPORTED_FAIL
COMMITTED_CONFLICT_MARKERS=USER_REPORTED_CRITICAL
DOCS_DELIVERY_CONFLICT=USER_REPORTED_HIGH
PREVIOUS_BUILD=USER_REPORTED_PASS
PREVIOUS_TEST_FAILURES=USER_REPORTED_47_PENDING_CLASSIFICATION
MASTER_UPDATE=NOT_AUTHORIZED_IN_CURRENT_TASK
ORIGINAL_REBASE=PROTECT_AND_VERIFY_ACTUAL_STATE
CODE_PUSH_OR_RELEASE=NO
NEXT_GATE=FULL_INDEPENDENT_CANDIDATE_REVIEW
```

当前实施入口：
`integration/enterprise-master-candidate-failure-remediation-v1.md`

实施完成后完整独立审查入口：
`integration/enterprise-master-candidate-independent-review-v1.md`

此前聊天中允许直接更新master、在业务docs写报告并提交的安排，在本轮被以上两份规范取代。失败候选、原rebase、历史报告都保留；不得reset/abort/quit清场。

## 1. 文档治理与业务交付分离

GitHub指导文档继续由云端维护在独立Authority分支，本地Agent先拉取再执行。业务代码仓库的本次docs、实施/审查报告、Excel与真实DB不提交、不上传；master原有文档保留不误删。

本轮所有本地计划、报告、证据、备份写到 D:\BattleMap\local-reports\enterprise-master-remediation-v1\，具体按实施规范的FAILED_CANDIDATE_SHORT_SHA/run目录。
旧文档中的 docs/enterprise/... 是历史证据入口，允许读取；其“报告加入代码提交”条款在本轮不适用。不复制整个Authority镜像到业务代码仓库，不重开用户关闭的文档合并请求。

来源历史已含本次禁止docs时，普通merge后删除最终目录仍不能排除祖先。当前规范允许在独立新分支准备CODE_ONLY_NET_DELTA候选，原分支/失败候选/文档归档留本地；不得伪称原feature祖先已合并。只准备候选、不移动master，最终交付拓扑另行明确决定。
本地归档标签enterprise-docs-archive-v1按真实文档提交核实，禁止覆盖、随意标记rebase中途HEAD或push标签；未提交资料另备份。标签不是排除或验收证据。

## 2. 正式 Authority 与执行入口

| 文档 | 用途与状态 |
|---|---|
| `integration/enterprise-master-candidate-failure-remediation-v1.md` | **CURRENT实施**：原现场保护、候选代码修复、docs树/索引/历史排除、47失败归因、隔离验证 |
| `integration/enterprise-master-candidate-independent-review-v1.md` | **下一门禁**：完整合并候选独立审查，覆盖旧缺陷、新问题及主线受影响功能；不更新master |
| `enterprise-contract-architecture-v5.md` | 端到端canonical、共享机制、API/DB、Progress单一事实源的长期架构 |
| `architecture/enterprise-runtime-field-options-contract-v1.md` | fieldDef静态metadata与动态options唯一来源、错误边界 |
| `mox-canonical-authority-v6.md` | 当前MOX业务目标，已同步确认增量；当前40个业务身份，不是物理列数 |
| `tob-canonical-authority-v2.md` | 当前TOB业务目标，已同步确认增量；33个业务身份 |
| `isp-canonical-authority-v2.md` | 当前ISP业务目标，已同步删除分类与行业选项；24个业务身份 |
| `power-canonical-authority-v2.md` | 当前电力业务目标，已同步删除分类与行业选项；27个业务身份 |
| `large-enterprise-canonical-authority-v2.md` | 当前大企业务目标，已同步确认增量；25个业务身份 |
| `enterprise-excel-confirmed-delta-v1.md` | 仅删除指定分类字段、更新大企名称；用户此前报告完成，候选核对实际代码 |
| `enterprise-industry-options-authority-v1.md` | ISP/电力/大企已确认行业选项，保持既有授权与实际进度 |
| `enterprise-home-canonical-authority-v4.md` | 当前完整首页目标，第18节展示/布局/单位/标题；旧DEFERRED阶段不再阻塞已授权首页工作 |
| `remediation/enterprise-migration-schema-test-alignment-v1.md` | 历史SQL不可改、按版本测试、真实完整链和物理列集合；本轮恢复合并丢失的既有接线依集成专项授权 |
| `remediation/enterprise-confirmed-delta-test-expectation-alignment-v1.md` | 区分过期预期、fixture、真实回归；禁止削弱测试 |
| `integration/enterprise-review-snapshot-preparation-v1.md` | 固定可运行版本与证据的既有规则；本轮工作树/产物/提交文档边界由集成专项取代 |
| `reviews/non-mox-modules-mox-reference-independent-review-v1.md` | 原完整机制审查基线，不能只看已知finding |
| `reviews/non-mox-full-independent-review-rerun-v3.md` | 新HEAD重跑完整范围，历史finding额外回归，主动发现新问题 |
| `reviews/enterprise-progress-single-source-independent-review-v1.md` | 五模块Progress三入口、主题/内容、父记录、历史保留、最新投影、无双写 |
| `reviews/enterprise-home-and-excel-delta-independent-review-v1.md` | 首页/确认字段增量联合核验；本轮旧证据不能代替候选新SHA |
| `reviews/mox-end-to-end-canonical-independent-review-v1.md` | MOX既有审查规范；旧PASS不延伸到合并候选 |
| `remediation/five-module-shared-form-renderer-convergence-v3.md` | 五模块实际共享渲染目标，历史实施/回归基线，不重新复制表单 |
| `remediation/five-module-shared-operation-convergence-v1.md` | 共享操作生产路径基线 |
| `remediation/tob-shared-form-production-path-repair-v1.md` | TOB残留本地builder修复基线，用户此前报告完成 |
| `remediation/enterprise-form-options-root-cause-remediation-v2.md` | f.options根因修复；用户此前确认Create/Edit可打开，保留回归 |
| `remediation/enterprise-customer-data-fetch-unification-v2.md` | customer_id查询/标准化/保存关系链；保留回归 |
| `remediation/enterprise-empty-option-removal-v1.md` | 仅移除字面“（空）”选项，placeholder为请选择，真实空值规则保留 |
| `remediation/enterprise-home-route-blocker-repair-v1.md` | 首页真实点击导航修复基线，用户此前报告完成 |
| `investigation/enterprise-form-progress-legacy-parity-survey-v2.md` | 用户此前报告已完成，底栏、进展结构及主题/内容映射的本地事实输入 |
| `investigation/enterprise-form-scroll-progress-survey-v1.md` | SUPERSEDED；仅历史调查背景 |
| `investigation/enterprise-runtime-implementation-survey-v1.md` | 历史运行链调查规范；当前代码状态仍需核实 |
| `investigation/enterprise-excel-v0.1-v0.2-diff-survey-v1.md` | 未确认差异只读；两项确认增量与行业选项按专属Authority生效 |
| `remediation/mox-4-group-render-chain-repair-v1.md` | 历史MOX四组断链修复及回归基线 |
| `remediation/mox-end-to-end-canonical-convergence-v1.md` | 历史canonical收敛背景；旧数量依当前业务Authority更新 |
| `remediation/non-mox-modules-mox-reference-alignment-v1.md` | 历史四模块对齐；实施报告PASS曾被审查推翻 |
| `remediation/non-mox-alignment-independent-review-findings-remediation-v2.md` | 历史7个阻塞修复基线，不限制完整审查范围 |
| `remediation/non-mox-shared-form-renderer-convergence-v1.md` | SUPERSEDED BY FIVE-MODULE V3 |
| `reviews/non-mox-alignment-independent-rereview-v2.md` | SUPERSEDED BY FULL RERUN V3；不得仅复核7项 |
| `integration/parallel-module-integration-plan-v1.md` | 历史模块worktree集成规则，不替代当前master专项 |
| `integration/local-worktree-layout-v1.md` | 历史worktree布局；当前路径以实际Git和本轮报告为准 |
| `reviews/authority-consistency-audit-2026-09-07.md` | 历史文档对账快照，不是当前候选验收结论 |

## 3. 合并修复中不得回退的已确认业务规则

### 3.1 字段与分组

模块字段分别由自己的当前Canonical Authority定义，不因master旧实现而恢复已废弃业务字段，也不把MOX字段复制到其他模块。
MOX新增/编辑四组：客户信息 / 无线格局 / 微波格局 / 作战情况；其余四模块三组：客户信息 / 业务格局 / 作战情况。全部由Contract驱动共享实际renderer，不接受只共享外壳、私有完整HTML builder或本地第二套schema。

确认Excel增量仅删除“整体空间（肥肉/瘦肉/骨头）”分类，整体空间金额/跳数及其他未删除字段保留；大企名称为“大企（油气矿、广电、交通）”。当前40/33/24/27/25是业务身份总数，mode字段按visibility派生，不能直接当SQLite列数。
其他未确认V0.2差异不得趁冲突修复自行纳入；已确认增量不能以旧冻结说明阻塞。

### 3.2 Customer与options

Field Contract/fieldDef是type/control/editor等静态metadata唯一Authority；runtime model只承载动态值、options和状态。不能恢复以不存在的f.type判断select而让options缺失的路径。
Customer真实ID必须贯穿query、API、normalization、候选选择与业务customer_id；不以名称关联，不恢复私有重复查询或吞异常空数组。

### 3.3 Progress

Progress History为唯一持久化事实源，battleProgress为最新/当前投影。新增页、编辑页、独立进展弹窗都须验证实际写链。
新增/编辑保留相同的只读最新摘要、可展开新增入口、主题和内容两个可编辑输入；只读摘要不意味着整个进展区域只读。命名调整不改变行为，不能恢复业务表text双写/fallback。双滚动为用户此前确认可接受，不趁本轮重新改造。
此前四模块双写及按本地报告最小建议修复的具体实现/验收，以相应本地提交和报告核实，不能继承旧索引的“待报告”或旧PASS代替当前证据。

### 3.4 Heatmap、Metric与首页

Heatmap/Metric字段身份使用canonical key，label仅展示；统计与点击筛选使用同一条件，既有业务口径不因合并重写。
首页按V4及第18节：目标/实时并列，实时单一M$后缀，三卡与空间拓展布局不重叠，指定桌面对齐/等高、企业专项标题蓝色，ISP&大企实时汇总ISP/电力/大企，导航按已确认子页。不得恢复旧首页占位实时金额或错误跳转。

### 3.5 数据库与测试

已执行历史SQL不可编辑、删改、重编号、重排；不可修改账本/checksum掩盖失败。历史阶段用历史预期，完整生产链按当前最终结构；新库与旧库升级均验证数据保留与CRUD。
本轮可恢复有双方代码事实支撑、被合并漏掉/重复的既有迁移登记和接线；新的生产迁移设计/版本碰撞单列阻塞，不借“修测试”越权。
47个失败必须逐项恢复、分组归因并核验，不全当过期schema断言；不以build通过代替后端语法/启动，也不拿业务字段数替代物理列集合。

## 4. 当前路径与执行方式

```text
原业务工作树：D:\BattleMap\battle-map（原rebase保护）
失败候选预期：D:\BattleMap\battle-map-master-integration（核对后只读保留）
新纯代码候选默认：D:\BattleMap\battle-map-master-code-only-v1（独立新分支）
指导文档镜像：D:\BattleMap\BattleMapenterprise-authority
本地产物：D:\BattleMap\local-reports\enterprise-master-remediation-v1\
前轮合并报告：D:\BattleMap\local-reports\enterprise-master-merge-report.md
前轮候选审查：D:\BattleMap\local-reports\enterprise-master-merge-candidate-review.md
```

目录/分支已经存在时不覆盖，按专项核实版本和用途；本轮一个写Agent只操作新的隔离候选。原工作树与master引用不移动，不能通过update-ref/worktree强制参数绕过rebase占用。
业务根Excel继续留本地；需要证据时从实际文件系统定位并记录hash，不要求入Git。数据库验证使用隔离库，不能拿原工作树旧服务或真实业务库证明新候选。

## 5. 当前推进顺序

1. 云端发布当前两份integration规范，本地更新Authority。
2. 实施者核对原rebase、来源/master/失败候选SHA、备份与最新完整审查，建立文件scope/失败矩阵。
3. 根据docs是否已入祖先选择合法候选模式；含docs历史则从固定master准备新的纯代码净增量分支，保留原历史而不纳入交付祖先。
4. 修复冲突标记背后的实际语义，修复集成接线及有证据的测试/fixture问题；完整schema/后端/五模块/主线回归。
5. 只在隔离交付分支提交代码，最终提交树再次核验；docs TREE/INDEX/HISTORY均证明，产物留本地。
6. 新Agent按integration/enterprise-master-candidate-independent-review-v1.md对同一新SHA完整复审；旧finding只是回归集，同时主动发现新问题。
7. 复审PASS后再明确master落地方式；CODE_ONLY模式必须如实说明拓扑，不称原feature已祖先合并。本轮不移动master、不push。
8. 后续另行处理原rebase收尾、发布与标签；不得用当前失败候选提前交付。

## 6. 状态与历史维护

当前状态集中在本索引第0节；模块规范定义目标，本地报告记录对应HEAD的事实。三者不能互相代替。
先前表单/首页/增量/Progress进度属于历史阶段，其代码与报告保留；当前合并缺陷不意味着重新开始这些业务建设，也不证明这些业务在候选已正确保留。
实施者只能声明IMPLEMENTED/PARTIAL/BLOCKED，独立审查决定候选是否通过；只有后续真实master引用到位才可声明本地主线合入。文档标签不代表VERIFIED。
每个新候选需完整重跑约定集成审查范围，不仅复核已知冲突标记或47个失败。报告PASS必须关联真实提交blob、生产调用链和验证日志。
本轮文档留本地/隔离worktree/不移动master规则优先于旧阶段提交报告和直接merge提示词；业务语义冲突或版本无法核实则记录具体BLOCKED，不猜测、不丢成果。
