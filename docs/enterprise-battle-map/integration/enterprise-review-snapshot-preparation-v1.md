# 企业模块独立复核前：未提交改动收口与固定版本 V1

**状态：CURRENT / 用户报告前轮因大量未提交改动无法固定HEAD，待本地处理**  
**执行者：实施 Agent；独立审查者不代为提交**  
**代码：D:\BattleMap\battle-map / feature/enterprise-battle-map**

## 1. 目的与当前边界

用户反馈前轮独立复核无法在稳定HEAD完成核验。先由实施者核对并提交已授权企业任务的实际实现，形成能还原、能运行的受审版本，再交独立复核。
云端未读取本地状态及完整报告，不预判具体未提交文件或原报告整体结论；原审查中的真实缺陷继续保留。固定版本缺口本身不等于新增功能缺陷。

本地git commit不需要联网或先push。代码不必上传GitHub才能独立核验；Authority文档拉取与本地代码提交是两个仓库操作。
本次允许盘点、必要的文档/证据同步、精确暂存与本地提交既有已授权实现；不是新功能或无边界代码修复。
三个迁移/DB测试若仍未完成，继续依其专项V1完成该范围，再固定候选；若已有完成证据不重复修复。行业选项按实际进度登记，不能因没有云端回执假定未做、重做或自动标完成。
后续字面“（空）”选项修正按 `remediation/enterprise-empty-option-removal-v1.md` 单独授权实施；本次只删实际显示该文字的选项，真实空值及未命中控件保持。已有候选保留，新修正完成并提交后再固定新候选，不能混入正在核验的旧快照。

最新首页展示修正按enterprise-home-canonical-authority-v4.md第18节实施：目标/实时并列、实时M$后缀、空间拓展左右边缘对齐MOX/ISP卡片横向中心并等高，企业专项标题复用其他专项的蓝色。本次只将其实际已授权展示改动及直接测试纳入候选，不因整理提交修改统计/SQL或重复既有任务；新候选交联合复核第9/11节。

## 2. 恢复事实与产物

先更新：
git -C "D:\BattleMap\BattleMapenterprise-authority" pull --ff-only origin enterprise-battle-map-authority

读取该Authority目录的docs/enterprise-battle-map下：
- authority-index.md、本文件；
- reviews/enterprise-home-and-excel-delta-independent-review-v1.md；
- remediation/enterprise-migration-schema-test-alignment-v1.md；
- 每项实际待提交改动对应的既有实施规范、计划与报告。

代码根读取适用AGENTS.md/仓库规则及最近联合复核报告。确认其他写Agent和原复核均已结束读取/修改；保存旧结论，不边审边改。

在原工作树执行只读盘点：
git -C "D:\BattleMap\battle-map" rev-parse --show-toplevel
git -C "D:\BattleMap\battle-map" branch --show-current
git -C "D:\BattleMap\battle-map" rev-parse HEAD
git -C "D:\BattleMap\battle-map" status --short --untracked-files=all
git -C "D:\BattleMap\battle-map" diff --name-status
git -C "D:\BattleMap\battle-map" diff --cached --name-status
git -C "D:\BattleMap\battle-map" ls-files --others --exclude-standard

这些命令只定位变化；还须逐项读取实际diff、暂存内容与未跟踪源码内容，用rg定位引用和依赖，不凭文件名判断归属。确认真实项目分支，不在不相关仓库/默认分支操作，不初始化替代仓库。
记录AUTHORITY_HEAD、BASE_HEAD、旧REVIEWED_HEAD、分支、工作树路径和正在运行的服务版本。Authority拉取失败如实记录实际SHA，不称最新。

本地固定产物：
- docs/enterprise/implementation/enterprise-review-snapshot-preparation-v1-plan.md
- docs/enterprise/implementation/enterprise-review-snapshot-preparation-v1-report.md
- docs/enterprise/implementation/evidence/enterprise-review-snapshot-preparation-v1/<BASE_HEAD>/

计划包含文件/必要hunk级归属、需求/报告依据、暂存状态、依赖、待提交/排除决定、验证依据和精确WRITE_SCOPE。同名报告保留历史，旧独立报告只引用不改写。
报告可引用已有失败矩阵和验证日志，不另造一套竞争的业务Authority。

## 3. 改动归属与完整提交

| 改动类别 | 处置 |
|---|---|
| 既有已授权企业实现且内容/归属明确 | 核对后纳入本地提交，包括本次Agent接手前已完成的相关代码，不要求必须由当前Agent编写 |
| 新增源码、测试helper/fixture、实际需要的配置/依赖接线 | 与依赖它们的实现一起纳入，不能只提交修改文件而漏掉未跟踪依赖；按仓库规则处理lock/必要生成物 |
| 三个迁移/DB测试仍有残留 | 按其既有专项范围修复并记录；不得改已执行历史SQL或扩大生产迁移权限 |
| 行业选项等独立已授权任务 | 已完成且影响同一受审运行链时核对后纳入，并明确复核范围；未完成部分保持真实状态，避免以脏代码污染候选 |
| 其他任务或归属无法确认的改动 | 原样保留，记录具体位置和冲突；不能为了干净全量提交、删除、回滚或冒领 |
| 根目录Excel、真实业务DB、日志/构建缓存及本地运行资料 | 不作为代码提交前置；Excel用路径及SHA-256固定，运行资料记录必要版本信息，不提交业务数据 |
| 旧/当前审查报告与证据 | 保留历史和HEAD归属；本次准备报告可提交，独立审查中新产物允许留工作树，不需为其不断重开审查 |

共享文件混合多项已授权且不可分离的改动，可组成一个明确说明依赖的完整提交；不能为形式拆分制造不可运行版本。混有未授权或不明归属hunk时，先隔离处理，不整文件夹带。
已有暂存区不等于本轮可提交清单。若有无关暂存内容，不直接git commit；用可核验的隔离工作树或临时索引等方式保留原暂存意图。无法安全分离的具体项记录阻塞，继续可完成的盘点与准备，不猜测权限。

按已核对路径/hunk暂存，检查git diff --cached的完整内容与范围，再执行本地commit。由实际文件清单生成并在报告记录准确git add/commit命令；不要使用git add .、git add -A或git commit -a笼统打包。
既有规则要求的commit hook正常执行，不用--no-verify或修改规则绕过。身份/钩子/权限失败记录真实原因，继续可做项，不伪造成功。
不push/merge，不reset/rebase/clean，不强制checkout/批量restore或全量stash清场。已执行历史SQL不追改；若发现其本来已被改动，记录相对历史的差异和归属，不静默提交或替别人回滚。

## 4. 固定真正用于运行的版本

仅有一个HEAD字符串不足以证明正在测试该版本。提交后核对：
- 所有受审源码、测试、fixture、配置/构建接线等可执行依赖已进入候选提交；暂存/未暂存或未跟踪文件没有覆盖受审实现。
- 候选包含本次声称完成的全部修复，需求/旧finding/实际提交有映射；剩余已知失败单独记录。
- 测试与启动使用候选的源码和配置，记录实际目录、服务实例/构建来源及HEAD；不用旧服务、旧dist或原脏工作树来证明新提交。
- Excel仍在本地根目录，不修改或强制加入Git；记录准确路径及SHA-256，与代码版本分开固定。
- 不要求整个git status绝对为空。报告/证据、工作簿及已证明不影响受审运行的其他文件可列明排除；影响无法排除的未提交源码不能靠声明“范围外”忽略。

若原工作树留有其他可执行改动或持续开发，优先从已完成的候选提交建立独立detached review worktree。默认位置为D:\BattleMap\battle-map-enterprise-review-<短SHA>，已存在则核对版本/用途后选唯一新路径，不覆盖。
准备者可创建该工作树、按已有项目流程准备依赖/隔离测试配置，并记录实际路径；不手动把原脏源码、旧构建或真实业务库复制进去。完整提交缺依赖时回到实施阶段补齐；不能在review worktree私下补丁后宣称它等于HEAD。
独立工作树中的测试数据用隔离库/fixture；本地原Excel可按明确绝对路径只读核对，无需复制入Git。依赖安装/构建如改动受审lock/生成源码，按既有规范处理后重新固定，不把改后的运行冒充原版本。

先固定实现提交，再保存与其对应的验证证据/准备报告；允许随后单独docs-only提交。报告区分IMPLEMENTATION_HEAD和最终REVIEW_CANDIDATE_HEAD。
最终候选SHA在交接回执记录即可，不为让报告包含自身commit SHA而循环amend/提交。审查者固定收到的准确候选SHA，检查docs-only差异与实现等价性。

## 5. 验证与交接

按实际改动运行必要测试，优先复用同一实现的可信日志；迁移残留按专项V1验证，其他范围按对应规范。若隔离候选与原验证环境不能证明等价，补跑具体必要范围，避免机械重跑所有历史建设。
验证失败如实记录，不通过提交操作把FAIL改PASS。提交可固定一个仍有已知缺陷的版本，但不能把它宣称“全部修复完成”；稳定版本与功能通过分别判定。

最终检查候选HEAD、运行源码/配置和Excel hash稳定，列出剩余工作树文件及影响依据。保留新问题和旧finding，不改写原报告。
交接：
- SNAPSHOT_READY=YES：候选能完整还原并用于规定核验，受审源码不依赖未提交改动；不代表测试通过或独立VERIFIED。
- SNAPSHOT_READY=NO：明确缺失源码/依赖、混合改动或运行版本等具体缺口，报告已完成部分，不能仅写“工作树脏”。
- 已知真实生产/测试失败继续按既定范围处理；稳定候选也可交审查确认残余，但必须显式声明未关闭项，不能期待整体PASS。
- 独立复核在新会话按联合规范第9节检查版本、第7/8节及实际业务范围核验，只写报告/证据，不提交或修复代码。审查期间不改候选；需要修改则先结束该次审查。

短回执：
RESULT=PREPARED/PARTIAL/BLOCKED
AUTHORITY_HEAD=
BASE_HEAD=
IMPLEMENTATION_COMMITS=
IMPLEMENTATION_HEAD=
REVIEW_CANDIDATE_HEAD=
REVIEW_WORKTREE=
IN_SCOPE_UNCOMMITTED_EXECUTABLE_CHANGES=
EXCLUDED_LOCAL_FILES_AND_REASON=
WORKBOOK_PATH=
WORKBOOK_SHA256=
VALIDATION_EVIDENCE=
KNOWN_OPEN_FINDINGS=
SNAPSHOT_READY=YES/NO
REPORT_PATH=
NEXT=INDEPENDENT_REVIEW/CONTINUE_AUTHORIZED_REMEDIATION/RESOLVE_SPECIFIC_SNAPSHOT_GAP
