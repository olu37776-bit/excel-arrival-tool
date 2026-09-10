# 企业作战地图 Authority 文档索引

**状态：CURRENT AUTHORITY INDEX**  
**指导文档仓库：olu37776-bit/excel-arrival-tool / enterprise-battle-map-authority**  
**业务代码：D:\BattleMap\battle-map；目标主线：master**  
**Authority镜像：D:\BattleMap\BattleMapenterprise-authority**

## 0. 当前任务：用户手动处理集成后，对整个 BattleMap 项目做完整独立 Review

用户最新决定合并问题改由本人手动处理，现在要求全面审查整个项目。当前不再让本地Agent执行上一轮失败候选修复或重复合并，不以旧remediation已完成作为本轮审查前提。

**当前唯一执行入口：`../project-review/battle-map-full-project-independent-review-v1.md`**

本地绝对路径：
```text
D:\BattleMap\BattleMapenterprise-authority\docs\project-review\battle-map-full-project-independent-review-v1.md
```

本轮是整个BattleMap应用的Review，不只是企业模块、主线受影响diff、renderer或历史finding。必须先从实际代码枚举全部业务模块、前端路由、后端API、数据表、初始化/迁移、测试和运行/交付入口，再逐项覆盖。非企业模块依据自己的业务需求核验，不强制套用企业Canonical架构。

前轮用户报告的三类问题继续作为必查回归：
- server.js及server/db/database.js的候选提交曾残留原始冲突标记；
- docs/enterprise/的50+文件可能违反本地docs不提交、不上传规则；
- build报告通过但测试报告47个失败，涉及MOX Schema。

上述是前轮转述，不证明当前手动结果仍有这些问题，也不表示它们已经关闭。当前master引用、工作树、提交/快照、进行中的Git操作及实际运行版本必须重新核实。云端未访问本地最新源码、完整日志和真实数据库，不声明全项目PASS。

```text
CURRENT_TASK=BATTLEMAP_FULL_PROJECT_INDEPENDENT_REVIEW_V1
SCOPE=ENTIRE_BATTLEMAP_PROJECT_NOT_ONLY_ENTERPRISE
MANUAL_INTEGRATION=USER_TAKING_OVER_ACTUAL_RESULT_TO_VERIFY
PREVIOUS_CANDIDATE_REVIEW=USER_REPORTED_FAIL_HISTORICAL
PREVIOUS_CONFLICT_MARKERS=MANDATORY_REGRESSION_NOT_ASSUMED_OPEN_OR_CLOSED
PREVIOUS_DOCS_CONFLICT=MANDATORY_REGRESSION
PREVIOUS_47_FAILURES=RECOVER_AND_RETEST_ACTUAL_CASES
CURRENT_MASTER_OR_SNAPSHOT=LOCAL_VERIFICATION_REQUIRED
CODE_REPAIR_OR_GIT_MUTATION=NOT_AUTHORIZED_IN_THIS_REVIEW
LOCAL_REPORTS=OUTSIDE_CODE_REPOSITORY
NEXT=REVIEW_FINDINGS_AND_FULL_COVERAGE_RECEIPT
```

独立审查只读代码；允许按新规范建立隔离核验worktree/输入快照、运行测试与自建测试库、写仓库外证据。不得提交、修复、push、处理rebase、移动master或操作tag。发现问题只给最小修复建议，不现场修代码。

## 1. 文档治理与业务交付分离

GitHub指导文档继续由云端维护在独立Authority分支，本地Agent先拉取再执行。指导文档仓库不是待交付的BattleMap业务源码仓库。
业务代码库本次本地docs、实施/审查报告、Excel与真实DB不提交、不上传；master原有文档保留，不误删。用户此前关闭的文档合并请求不重开。

本轮所有本地审查清单、报告、日志、必要复现脚本、截图和隔离测试资料写到：
```text
D:\BattleMap\local-reports\battle-map-full-review-v1\<短SHA或SNAPSHOT_ID>\run-001\
```
目录重复则按规范增加run编号，旧证据保留。具体产物结构与短回执在当前Review第13—15节。
旧文档中的docs/enterprise/...是历史证据入口，允许读取；其“新报告加入代码提交”条款在本轮不适用。不复制整个Authority镜像到业务代码库。

docs最终tree与新增可达历史分别核验；归档标签不是排除或验收证据。若用户手动操作已经改变拓扑，记录实际结果，不沿用此前普通merge/净增量候选的假设，不替用户重写历史。旧失败候选/rebase/备份只读保留；本轮不再自动新建纯代码交付分支。

## 2. 正式 Authority 与执行入口

表内除当前全项目Review外的实施规范仅提供适用业务目标、历史事实和验证规则；阅读它们不授权在只读审查中执行修改步骤。

| 文档 | 用途与状态 |
|---|---|
| `../project-review/battle-map-full-project-independent-review-v1.md` | **CURRENT执行**：全项目清单、18类完整审查、固定提交/快照、全部模块、后端/DB/安全/测试/交付、旧finding与新问题 |
| `integration/enterprise-master-candidate-failure-remediation-v1.md` | 前轮候选修复规范，用户改为手动处理；**非当前执行任务**，仅历史/回归依据 |
| `integration/enterprise-master-candidate-independent-review-v1.md` | 原候选审查范围，当前由全项目Review扩大覆盖；集成/文档/Schema规则继续参考，不限审查边界 |
| `enterprise-contract-architecture-v5.md` | 企业端到端canonical、共享机制、API/DB、Progress单一事实源的长期架构 |
| `architecture/enterprise-runtime-field-options-contract-v1.md` | fieldDef静态metadata与动态options唯一来源、错误边界 |
| `mox-canonical-authority-v6.md` | 当前MOX业务目标，已同步确认增量；40个业务身份，不是物理列数 |
| `tob-canonical-authority-v2.md` | 当前TOB业务目标，已同步确认增量；33个业务身份 |
| `isp-canonical-authority-v2.md` | 当前ISP业务目标，已同步删除分类与行业选项；24个业务身份 |
| `power-canonical-authority-v2.md` | 当前电力业务目标，已同步删除分类与行业选项；27个业务身份 |
| `large-enterprise-canonical-authority-v2.md` | 当前大企业务目标，已同步确认增量；25个业务身份 |
| `enterprise-excel-confirmed-delta-v1.md` | 仅删除指定分类字段、更新大企名称；用户此前报告完成，当前核对实际代码 |
| `enterprise-industry-options-authority-v1.md` | ISP/电力/大企已确认行业选项，保持既有授权与实际进度 |
| `enterprise-home-canonical-authority-v4.md` | 当前完整首页目标，第18节展示/布局/单位/标题；旧DEFERRED阶段不再覆盖已授权首页目标 |
| `remediation/enterprise-migration-schema-test-alignment-v1.md` | 历史SQL不可改、按版本测试、真实完整链和物理列集合；本轮仅按其规则审查，不实施 |
| `remediation/enterprise-confirmed-delta-test-expectation-alignment-v1.md` | 区分过期预期、fixture、真实回归；禁止削弱测试 |
| `integration/enterprise-review-snapshot-preparation-v1.md` | 固定可运行版本与证据的既有规则；本轮版本/只读/报告边界按全项目Review，不代用户提交 |
| `reviews/non-mox-modules-mox-reference-independent-review-v1.md` | 原完整企业机制审查基线，当前整体纳入企业范围，不只看已知finding |
| `reviews/non-mox-full-independent-review-rerun-v3.md` | 新HEAD完整范围重审，历史finding额外回归，主动发现新问题 |
| `reviews/enterprise-progress-single-source-independent-review-v1.md` | 五模块Progress三入口、主题/内容、父记录、历史保留、最新投影、无双写 |
| `reviews/enterprise-home-and-excel-delta-independent-review-v1.md` | 首页/确认字段增量联合核验；旧证据不能代替当前SHA |
| `reviews/mox-end-to-end-canonical-independent-review-v1.md` | MOX既有审查规范；旧PASS不延伸到当前版本 |
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
| `integration/parallel-module-integration-plan-v1.md` | 历史模块worktree集成规则，不授权当前继续合并 |
| `integration/local-worktree-layout-v1.md` | 历史worktree布局；当前路径以实际Git和本轮报告为准 |
| `reviews/authority-consistency-audit-2026-09-07.md` | 历史文档对账快照，不是当前版本验收结论 |

## 3. 已确认企业业务规则继续有效

### 3.1 字段与分组

模块字段分别由自己的当前Canonical Authority定义，不因master旧实现而恢复已废弃字段，也不把MOX字段复制到其他模块。
MOX新增/编辑四组：客户信息 / 无线格局 / 微波格局 / 作战情况；其余四模块三组：客户信息 / 业务格局 / 作战情况。全部由Contract驱动共享实际renderer，不接受只共享外壳、私有完整HTML builder或本地第二套schema。

确认Excel增量仅删除“整体空间（肥肉/瘦肉/骨头）”分类，整体空间金额/跳数及其他未删除字段保留；大企名称为“大企（油气矿、广电、交通）”。当前40/33/24/27/25是业务身份总数，mode字段按visibility派生，不能直接当SQLite列数。
未确认V0.2差异不在审查中实施；已确认增量不能以旧冻结说明阻塞。非企业模块按各自需求与实际Contract审查，不把本节变成全项目业务字段清单。

### 3.2 Customer与options

Field Contract/fieldDef是type/control/editor等静态metadata唯一Authority；runtime model只承载动态值、options和状态。不能恢复以不存在的f.type判断select而让options缺失的路径。
Customer真实ID必须贯穿query、API、normalization、候选选择与业务customer_id；不以名称关联，不恢复私有重复查询或吞异常空数组。

### 3.3 Progress

Progress History为唯一持久化事实源，battleProgress为最新/当前投影。新增页、编辑页、独立进展弹窗都须验证实际写链。
新增/编辑保留相同的只读最新摘要、可展开新增入口、主题和内容两个可编辑输入；只读摘要不意味着整个进展区域只读。命名调整不改变行为，不能恢复业务表text双写/fallback。双滚动为用户此前确认可接受，不按审查者偏好重构。
此前双写与最小修复建议的具体完成状态，以本地当前代码/提交和报告核实，不能继承旧索引的待报告或旧PASS。

### 3.4 Heatmap、Metric与首页

企业Heatmap/Metric字段身份使用canonical key，label仅展示；统计与点击筛选使用同一条件，既有业务口径不因集成重写。
首页按V4及第18节：目标/实时并列，实时单一M$后缀，三卡与空间拓展布局不重叠，指定桌面对齐/等高、企业专项标题蓝色，ISP&大企实时汇总ISP/电力/大企，导航按已确认子页。不得恢复旧首页占位实时金额或错误跳转。
全局首页及非企业模块的统计/图表同样纳入全项目清单，但按它们自己的业务依据核验。

### 3.5 数据库与测试

已执行历史SQL不可编辑、删改、重编号、重排，不可改账本/checksum掩盖失败。历史阶段用历史预期，完整生产链按当前最终结构；新库与旧库升级验证数据保留、物理结构与CRUD。
前轮47个失败须从原日志逐项追溯并核验当前结果，不全当过期schema断言；不以build通过代替后端语法/启动，不拿业务字段数替代物理列集合。当前新增失败另行登记，原日志缺失不得编造关闭数。
本轮Review只诊断，任何有证据的生产接线/测试修复也不在审查中实施。

## 4. 当前路径与版本边界

```text
业务根：D:\BattleMap\battle-map
目标主线：master
指导文档镜像：D:\BattleMap\BattleMapenterprise-authority
当前Review：docs\project-review\battle-map-full-project-independent-review-v1.md（相对Authority镜像）
本地产物：D:\BattleMap\local-reports\battle-map-full-review-v1\
前轮合并报告：D:\BattleMap\local-reports\enterprise-master-merge-report.md
前轮候选审查：D:\BattleMap\local-reports\enterprise-master-merge-candidate-review.md
前轮修复产物：D:\BattleMap\local-reports\enterprise-master-remediation-v1\（若实际存在，仅历史证据）
```

当前真实手动结果以Git状态、差异和用户实际运行目录核实，不默认旧候选目录就是目标。已提交用固定SHA隔离审查；手动修改未提交时，不代提交、不忽略修改去审旧HEAD，可按全项目Review建立hash固定快照继续诊断，但不能宣称master提交已验证。
原rebase/merge状态若仍存在则保留，具体完整性缺口如实报告。隔离测试不操作真实业务DB，不连旧服务冒充新版本，不将源码/报告上传。

## 5. 当前推进顺序

1. 本地更新Authority，读取全项目Review规范；不再执行上一轮失败候选修复。
2. 核实当前master、实际手动结果和操作状态，固定正式SHA或明确诊断快照。
3. 建立全项目模块/路由/API/数据与测试清单，不能只列企业模块。
4. 优先检查冲突标记、后端解析/隔离启动、Schema与原47失败，再完成全项目18类Review范围。
5. 所有旧finding回归，主动发现新问题；每项覆盖、失败与证据缺口分别记录，不在审查中修复。
6. 输出仓库外唯一综合报告和第15节短回执，区分代码可用性、docs交付策略、版本完整性和人工验收。
7. 用户据具体findings决定下一步定向修复或验收；本轮不合并、不提交、不push、不操作tag或原rebase。

## 6. 状态与历史维护

当前状态集中在本索引第0节；模块规范定义目标，本地报告记录对应HEAD/快照事实，三者不能互相替代。
历史已授权建设及其证据保留，不因为扩大审查而重新实施。旧PASS不自动延伸到手动集成后的代码；没有新的证据也不将历史已关闭问题直接标当前OPEN。
全项目Review不等于把企业规则推广为所有模块强制架构。完整范围、已知回归、主动发现新finding和真实测试覆盖同时满足才可形成结论。
指导文档继续在独立GitHub分支维护；本地docs不提交/上传是业务代码交付限制，不是停用Authority流程。旧规范中继续合并、提交报告、执行修复的安排在本轮不适用。
