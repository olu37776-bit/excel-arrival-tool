# 首页修复与 Excel 确认增量：联合独立复核 V1

**状态：CURRENT REVIEW AUTHORITY / 最新迁移Schema测试残留待定向修复；完成后固定新HEAD复核**  
**依据：2026-09-08 用户报告“首页和那个删除字段都完成了”**  
**代码工作树：D:\BattleMap\battle-map / feature/enterprise-battle-map**

## 1. 目标与角色

在同一固定新 HEAD 上独立核实首页跳转修复、原首页审查 findings、Excel 两项变更及实际受影响消费者，避免分别通过却在最终组合中回归。
用户报告完成不是独立验证通过；大企改名、工作簿实际输出和字段完整收敛仍须逐项核对，不能据用户简短回执推定每项已有证据。
本轮是独立审查，不再次实施。不得修改生产代码、测试、Migration、原始或输出 Excel、真实业务数据库或 Authority；不提交、不 push/merge，不替实施者修复 finding。

本文件规定本轮统一入口、报告与结论，优先于首页 V4 第17节原先的单任务报告路径；业务规则和必要核验要求仍沿用 V4、Excel 增量及五份当前模块契约。

## 2. 恢复输入并固定状态

先更新 Authority：
git -C "D:\BattleMap\BattleMapenterprise-authority" pull --ff-only origin enterprise-battle-map-authority

在 Authority 的 docs/enterprise-battle-map 下读取：
- authority-index.md、本文件；
- enterprise-home-canonical-authority-v4.md；
- remediation/enterprise-home-route-blocker-repair-v1.md；
- enterprise-excel-confirmed-delta-v1.md；
- 五份当前模块 Authority、共享架构 V5；只按真实改动继续读取相关机制规范。

在 D:\BattleMap\battle-map 读取：
- docs/enterprise/reviews/enterprise-home-v4-independent-review.md 及历史 findings/证据；
- docs/enterprise/implementation/enterprise-home-polish-v4-plan.md 和 enterprise-home-polish-v4-report.md；
- docs/enterprise/implementation/enterprise-home-route-repair-v1-plan.md 和 enterprise-home-route-repair-v1-report.md；
- docs/enterprise/implementation/enterprise-test-expectation-alignment-v1-plan.md、enterprise-test-expectation-alignment-v1-report.md 及其失败矩阵/证据；
- 最新迁移Schema专项的 docs/enterprise/implementation/enterprise-migration-schema-test-alignment-v1-plan.md、enterprise-migration-schema-test-alignment-v1-report.md 及失败矩阵/证据；
- Excel 计划/实施报告若已存在则读取作为辅助；缺少单独报告不阻塞，直接读取下面规定的本地根目录工作簿。

报告变更路径时先在本地用 rg 找到真实文件并核对内容/HEAD，不要求用户上传。某报告缺失时先尝试实际代码、文件与测试直接核验；只有无法获取完成具体检查所需的事实时才记录对应 EVIDENCE_GAP。
用户明确工作簿就在根目录且无需入 Git：先检查 D:\BattleMap\battle-map 根目录，必要时检查已知资料根 D:\BattleMap 的直属 Excel。用文件系统枚举，包括 Git ignored/untracked 文件，不得只执行 git ls-files 后宣称不存在。排除 Excel 锁文件，按名称、版本及真实 sheet/表头识别用户的当前文件，记录绝对路径和 SHA-256。存在多个无法区分的候选时列出具体冲突，不能凭最新修改时间猜测。

记录 AUTHORITY_HEAD、两项 IMPLEMENTATION_HEAD、旧 REVIEWED_HEAD、当前 REVIEWED_HEAD、工作树状态以及运行服务的代码目录/版本。确认两项实现均包含在受审 HEAD 中，识别 docs-only 后续提交。
受审生产代码/测试须已提交且无并发修改；若未提交，不由审查者提交或清理，完成可做的预检查并标记固定版本证据缺口。
工作簿无需 Git 跟踪、Git 历史、单独输出副本或独立 Excel 实施报告。对实际选定的当前文件记录并复核 SHA-256 即可固定核验对象；现有旧输入/备份可补充历史对照，不是当前文件检查前置。Authority 拉取失败不能称最新；记录实际本地版本及缺项，继续有依据的部分。

## 3. 首页与历史 findings

逐项恢复原报告 findings，包括未在用户摘要中提到的条目；建立原 finding → 修复提交 → 当前生产路径 → 新证据的闭环矩阵，不能直接复制实施者的 CLOSED/PASS。
首页其他已通过项目若有可信证据且相关实现未变，可说明影响分析后复用；已修改或缺证项重新执行。

真实浏览器普通点击必须覆盖：

| 入口 | 目标 |
|---|---|
| 全局首页“企业场景”卡片及数字区域 | 企业首页 |
| 一级“企业”菜单 | 企业首页 |
| 企业首页 MOX 卡片及目标/实时区域 | MOX 子页 |
| 企业首页 TOB 卡片及目标/实时区域 | TOB 子页 |
| 企业首页 ISP&大企卡片及目标/实时区域 | ISP 子页 |

使用当前真实首页组件、实际导航机制、router/guard/redirect 和最终渲染页面验证，记录实际 URL/route identity 与目标页面特征。
不能只断言 mock router.push 被调用，不能直接调用 handler、手动导航到目标或强制点击绕过遮挡来证明入口正确。
检查键盘激活、返回导航、控制台错误和被修改共享卡片的其他入口。无浏览器能力须记 NOT_RUN，不把此次真实跳转必检项判为 PASS。

沿首页 V4 核查实际影响：
- 企业专项/三卡/空间拓展不重叠，保留全局场景卡及数字的共享样式；
- 目标可占位，实时由各模块“已下单金额”真实汇总；ISP&大企包含 ISP+电力+大企；
- 可参与总空间继续按已孵化 AND 跟踪的整体空间金额求和，其他空间指标按 V4 原公式；
- 加载、0、失败可区分，返回首页刷新有效，不因字段删除或表名变化丢模块、错列、倍增或重复换算单位。

## 4. 根目录 Excel 实物核验

本轮以用户指出的根目录当前工作簿、当前字段契约和应用行为为核验对象，不要求重建 Excel 的历史编辑过程，也不要求补造单独实施报告。
只读打开真实文件，逐表记录实际 sheet 名、完整表头、相关验证/数值字段、必要结构和解析结果：

1. 每个业务表不再包含“整体空间（肥肉/瘦肉/骨头）”分类字段；不能只隐藏、清空或删除选项。不得误判整体空间金额/跳数为被删字段。
2. 大企 sheet 名为“大企（油气矿、广电、交通）”，没有额外创建交通模块。
3. 按当前已确认完整字段集合核对其余字段及相对顺序，特别是整体空间金额、跳数、已下单金额。核对数据与列对应及实际受影响的公式/验证/合并表头引用有效，不读取报告文字代替实物检查。
4. 工作簿可正常读取/打开，审查中不保存改写，不修改 Git ignore 或强制添加到 Git，也不要求重生成一个文件来满足报告格式。
5. 若已有旧版本/备份，可按字段身份对照剩余数据和引用；没有旧版本时仅注明“历史编辑差异未核实”，不把这一点单独升级为当前核验阻塞，也不得声称已证明全部历史单元格从未改变。已发现的数据错位/损坏仍是实际问题，应用迁移的数据保留测试仍须执行。

必要证据直接写入联合报告：真实路径、SHA-256、读取方式、每表字段/名称结论、与当前契约及应用的映射、实际发现问题。
只有真实文件无法定位/读取、多个候选无法识别或内容不符合当前需求，才记录相应的定位/证据缺口或实际缺陷。仅“未入 Git”“没有独立 Excel 实施报告”不是失败条件。
原报告受旧文档前置条件影响的 finding 保留历史；新复核记录用户澄清与实物证据，重新判断适用性，不能直接把未核验的工作簿标 PASS。

## 5. 应用端字段与联合回归

按当前五份模块规范逐项核查最终字段集合：

| MOX | TOB | ISP | 电力 | 大企 |
|---:|---:|---:|---:|---:|
| 40 | 33 | 24 | 27 | 25 |

这只是总业务身份数，不是DB物理列数；Create/Edit 可见或可编辑字段仍由 Contract visibility/mode 派生。不能靠数量正确掩盖错删、遗漏或替换字段。
TOB/ISP/电力/大企被删除分类身份原为 overallSpaceTier，MOX 精确 key 以本地真实契约映射确认。

核验：
- Field Contract、Table、Create/Edit、选项/校验、筛选、Heatmap 引用、导入导出、API、database.js 和实际持久化消费者对同一最终字段集合一致；
- 已删除字段无活动读取/写入/别名兜底；历史迁移、审查报告、一次性删除脚本中的字样不等于活动残留；
- Create/Edit 仍通过真实共享渲染器，不因删字段回退本地完整表单构建器；不能仅凭出现 .map() 就断定违规；
- 大企改名只影响已授权的 sheet 名及直接对应完整名称，既有模块 ID、客户主键、路由 identity 未重建；
- 如改动 DB，检查新库与升级库一致、迁移登记/事务/重复执行安全、其他数据保留。仅在隔离临时库或受控测试副本运行迁移和写入测试，不修改真实业务库或工作簿；
- 隔离数据完成五模块创建/编辑/保存/重读，以及必要的导入导出回归，验证剩余数值字段未错位；
- 通过不同模块非零金额和不同分类状态的隔离样例核验首页汇总，证明字段删除后金额、空间公式、模块范围不变。

测试必须消费真实生产路径，不复制实现建立自证断言。运行本轮路由、字段契约/消费者、相关迁移与联合回归。核对完整测试、build及已有 lint/typecheck 的日志、退出码和对应实现；同一最终实现的有效证据可复用，缺失、代码改变或影响无法排除则重跑必要范围。不得用修改前的全量 PASS 覆盖修改后的缺口，也不机械重建无关测试框架。

## 5.1 本轮出现的既有测试失败

此前用户报告测试修复完成，最新又报告三个迁移/DB测试残留，云端尚未读取本地日志。先按迁移Schema专项V1定向实施，之后按第8节复核；第7节与下面分类规则继续有效。审查者按 `remediation/enterprise-confirmed-delta-test-expectation-alignment-v1.md` 第3节记录逐项分类：过期预期、真实生产回归、测试/fixture缺陷、环境/证据缺口或未分类。
先完成可执行独立检查并保存报告，不现场改测试。旧数、旧名称或旧字段字样并不天然错误，例如升级前 fixture 应保持旧结构；反之，已确认过期的活动门禁也不能仅标“预期失败”就当作通过。
已证实必需测试资产与当前契约不一致、阻碍有效验证时，记录阻塞的测试问题；保持 FAIL 的事实归属，不能称为生产缺陷或忽略失败给整体 PASS。只有必要执行条件/证据不足而未确认缺陷时才使用 PARTIAL。
审查者复核实施者的分类及每项修改，不现场维护测试。若还有残留，则保留新 finding 和证据，审查结束后由实施者按该规范处理；本轮未完成项不能自动 PASS。

## 6. 报告、证据及退出判定

唯一当前联合报告：
D:\BattleMap\battle-map\docs\enterprise\reviews\enterprise-home-and-excel-delta-independent-review.md

证据：
D:\BattleMap\battle-map\docs\enterprise\reviews\evidence\enterprise-home-and-excel-delta\<REVIEWED_HEAD>\

若同名联合报告存在，先保留为：
docs/enterprise/reviews/history/enterprise-home-and-excel-delta-independent-review-before-<REVIEWED_HEAD>.md
同名归档内容不同则使用唯一后缀，不能覆盖。原首页独立报告保留旧结论，联合报告引用它并给出新 HEAD 下的 closure；不制造两份竞争的当前结论。

报告须包含版本/hash、逐项需求矩阵、finding 闭环、实际路由、当前 workbook 实物字段清单、应用数据保留依据、测试/浏览器证据、复用证据的影响分析、未运行项及下一步；历史 workbook 差异仅在有旧文件时补充。
每个新 finding 有 ID、严重度、实际位置/生产路径、违反条款、复现证据、影响和修复方向。发现阻塞继续其余独立检查，不现场修复。
结束复核受审代码 HEAD、工作树及 workbook hash 稳定；只允许本报告/证据和已识别的隔离测试临时输出变化。

判定：
- PASS：上述必检范围完成，无阻塞，新 HEAD 与实际工作簿证据稳定；人工最终验收仍单独待确认。
- FAIL：有已证实阻塞，列出准确 finding 和归属，转定向修复。
- PARTIAL：未证实缺陷但必要环境/输入/证据不足，列具体缺项。纯环境限制不得伪装代码缺陷；缺必需真实点击证据不得整体 PASS。
- 用户“完成了”不等于本轮人工验收完成，也不能据此称整个企业模块最终 VERIFIED。

短回执：
RESULT=PASS/FAIL/PARTIAL
REVIEWED_HEAD=
AUTHORITY_HEAD=
HOME_ROUTE_REPAIR=PASS/FAIL/NOT_RUN
ORIGINAL_FINDINGS_CLOSURE=
EXCEL_FIELD_REMOVAL=PASS/FAIL/NOT_RUN
REMAINING_FIELDS_AND_DATA_ALIGNMENT=PASS/FAIL/NOT_RUN
HISTORICAL_WORKBOOK_DIFF=VERIFIED/NOT_ASSESSED
LARGE_SHEET_NAME=PASS/FAIL/NOT_RUN
FIVE_MODULE_CONTRACT_AND_CONSUMERS=PASS/FAIL/NOT_RUN
HOME_SUMMARY_REGRESSION=PASS/FAIL/NOT_RUN
MIGRATION_AND_DATA_SAFETY=PASS/FAIL/NOT_APPLICABLE/NOT_RUN
TEST_FAILURE_CLOSURE=PASS/FAIL/NOT_RUN
TEST_ASSERTION_STRENGTH=PASS/FAIL/NOT_RUN
TEST_BUILD_EVIDENCE=VALID/INVALID/MISSING
HEAD_AND_WORKBOOK_STABLE=YES/NO
BLOCKING_FINDINGS=
REMAINING_CHECKS=
REPORT_PATH=
MANUAL_ACCEPTANCE=PENDING
NEXT=USER_MANUAL_ACCEPTANCE/TARGETED_REMEDIATION/COMPLETE_REVIEW

PASS 后由用户在实际页面与根目录 Excel 做简短人工验收，再更新联合报告中的人工结果并按当前 Authority 恢复其他待办；不自动启动新业务建设。

## 7. 测试残留修复完成后的本轮复核

用户报告“修复好了”，当前只记录 IMPLEMENTED_REPORTED，不预判修改仅涉及测试，也不预判所有旧失败已经消失。

1. 读取第2节新增的测试预期对齐计划、实施报告与实际差异，关联原联合报告、失败用例和旧/新 HEAD。本轮继续使用第6节唯一联合报告及证据目录，先归档旧结论，不另建竞争的最终报告。
2. 逐项核对旧失败分类和修改依据：过期预期须确实违反已确认的新契约；仍有效断言失败须通过真实实现修正。不能把未分类失败写成已解决，不能只依据实施报告的总通过数。
3. 审查测试 diff：确认字段精确集合/顺序/分组、数值字段保留、sheet 名和路由要求仍有有效验证；没有为本轮通过而新增 skip/only、吞异常、宽松替代精确断言或无审查刷新快照。废止用例的替代覆盖需可追溯。
4. 检查预期独立性，不能把被测结果重新当成 expected；原升级 fixture 保留旧结构/旧字段，迁移测试仍真正验证从旧到新及其他数据保留。既有负向用例和实际生产路径验证不能被空输入或全零样例架空。
5. 重新执行原失败用例和修改测试对应的受影响回归；核验原完整测试命令、build及现有必要门禁在同一最终代码/测试快照上的有效日志。已有完整、可信、对应同一实现的证据可以复用；缺失、失败、版本不符或修改影响未覆盖时补跑必要范围，不因重复审查而机械重跑所有历史任务。
6. 根目录 workbook 按第4节直接只读核对，包括 ignored/untracked 文件，记录真实路径/hash。无需入Git、单独Excel实施报告或重建历史编辑过程；实际内容不能仅靠修复报告自报。
7. 首页真实点击、五模块字段消费者、金额/空间汇总及迁移按第3—5节与实际差异核验。既有证据必须能对应当前实现及实物，不能用旧失败版本的 PASS 覆盖新 HEAD；若本次仅测试变化，明确哪些已有功能证据仍有效，避免无关重复工作。
8. 结束确认代码 HEAD、受审代码/测试及 workbook hash 稳定。逐项给出旧 finding 的关闭、仍失败或经用户澄清不适用的理由；不改写旧报告的事实，不把未读取文件标为通过。

结论仍按第6节 PASS/FAIL/PARTIAL。PASS 后才交用户简短人工验收：首页入口跳转与金额显示、五模块页面无被删分类字段、根目录大企表名含交通；本轮完成后再恢复其余真实待办。

## 8. 最新历史迁移与Schema测试修复后的复核

本节对应 `remediation/enterprise-migration-schema-test-alignment-v1.md`，实施者完成专项后再开始。只读核验，不修改测试、SQL或生产代码。

1. 用实际文件路径关联用户报告的ISP迁移、完整链、电力/大企DB三个失败，核对起始/截止迁移版本及分类。用户拼写不是重命名测试的依据。
2. 确认本轮历史SQL内容、排序/版本、生产runner/登记均未改变，没有伪造迁移账本/测试专属删列；既有其他任务差异单独归属。
3. 历史单步/前缀用对应版本schema预期，保留旧输入字段和数据；不能拿最新schema要求每个历史阶段，也不能通过改用例名删掉原有完整升级覆盖。
4. 全链真实调用当前生产迁移路径并达到最新登记版本；空库与真实旧结构升级的最终schema一致、旧分类列删除、其他数据/金额/跳数/关联保留。若生产完整终态仍残留旧列，保持PRODUCTION_MIGRATION_GAP finding，不能接受错误终态让测试通过。
5. 电力/大企等DB断言精确比较经版本和持久化契约确认的独立物理列集合，保留适用类型/约束等门禁；业务字段数不等于物理列数，expected不能从实际PRAGMA结果自生成。
6. 复查三个定向测试、受影响迁移/DB测试和原完整命令的当前证据，按第7节核验断言强度与build。未受影响的首页/Excel可信证据可复用；工作簿仍本地只读且不要求Git/单独报告。
7. 沿用第6节唯一联合报告和结论规则，不另建竞争结论。行业选项V1保留为独立已授权任务，只有相关改动确已进入受审HEAD时才按其实际影响核验，不推定已完成。
