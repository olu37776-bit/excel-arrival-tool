# 首页修复与 Excel 确认增量：联合独立复核 V1

**状态：CURRENT INDEPENDENT REVIEW / IMPLEMENTED_REPORTED / PENDING_VERIFICATION**  
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
- docs/enterprise/implementation/enterprise-excel-confirmed-delta-v1-plan.md 和 enterprise-excel-confirmed-delta-v1-report.md。

报告变更路径时先在本地用 rg 找到真实文件并核对内容/HEAD，不要求用户上传。缺失输入应记录具体 EVIDENCE_GAP，继续其他可完成核验，不编造结果。
从报告定位真实 workbook 输入、备份、输出和相关 hash。不要凭文件修改时间在多个候选中猜测。

记录 AUTHORITY_HEAD、两项 IMPLEMENTATION_HEAD、旧 REVIEWED_HEAD、当前 REVIEWED_HEAD、工作树状态以及运行服务的代码目录/版本。确认两项实现均包含在受审 HEAD 中，识别 docs-only 后续提交。
受审生产代码/测试须已提交且无并发修改；若未提交，不由审查者提交或清理，完成可做的预检查并标记固定版本证据缺口。
Excel 不在 Git 内则固定输入/输出 SHA-256，审查前后校验。Authority 拉取失败不能称最新；记录实际本地版本及缺项，继续有依据的部分。

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

## 4. Excel 文件核验

只读输入/备份与输出，对所有业务 sheet 逐项比较：
1. 仅整列删除取值为“肥肉/瘦肉/骨头”的“整体空间”分类字段，包括字段表头、该列数据及对应验证；不能仅隐藏、清空或删除选项。
2. 大企 sheet 名为“大企（油气矿、广电、交通）”；未额外新增交通 sheet 或改变业务模块身份。
3. 其余字段、数据、相对顺序和业务含义保留，尤其整体空间金额、整体空间跳数、已下单金额。以字段身份对齐列删除前后数据，不用原列字母直接比较。
4. 公式/名称/验证、合并表头、表格范围和其他实际受影响引用有效；允许必要的引用位置移动，不允许语义改变、#REF! 或格式/宏静默丢失。
5. 输出可正常重新打开。原始工作簿和输出均不在审查中保存改写；不可取得旧输入/备份时明确无法证明“其他数据未变”的证据缺口。

记录每表前后字段与结构摘要、输入/输出 hash 和差异判定，不上传真实业务数据。

## 5. 应用端字段与联合回归

按当前五份模块规范逐项核查最终字段集合：

| MOX | TOB | ISP | 电力 | 大企 |
|---:|---:|---:|---:|---:|
| 40 | 33 | 24 | 27 | 25 |

这只是总业务身份数；Create/Edit 可见或可编辑字段仍由 Contract visibility/mode 派生。不能靠数量正确掩盖错删、遗漏或替换字段。
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

用户报告当前执行中存在多项旧测试预期失败，尚未由云端读取日志。审查者按 `remediation/enterprise-confirmed-delta-test-expectation-alignment-v1.md` 第3节记录逐项分类：过期预期、真实生产回归、测试/fixture缺陷、环境/证据缺口或未分类。
先完成可执行独立检查并保存报告，不现场改测试。旧数、旧名称或旧字段字样并不天然错误，例如升级前 fixture 应保持旧结构；反之，已确认过期的活动门禁也不能仅标“预期失败”就当作通过。
已证实必需测试资产与当前契约不一致、阻碍有效验证时，记录阻塞的测试问题；保持 FAIL 的事实归属，不能称为生产缺陷或忽略失败给整体 PASS。只有必要执行条件/证据不足而未确认缺陷时才使用 PARTIAL。
本轮审查只分类；保存报告并结束后由实施者维护测试。修改后新 HEAD 需复核断言强度与联合功能，具体任务见该规范。

## 6. 报告、证据及退出判定

唯一当前联合报告：
D:\BattleMap\battle-map\docs\enterprise\reviews\enterprise-home-and-excel-delta-independent-review.md

证据：
D:\BattleMap\battle-map\docs\enterprise\reviews\evidence\enterprise-home-and-excel-delta\<REVIEWED_HEAD>\

若同名联合报告存在，先保留为：
docs/enterprise/reviews/history/enterprise-home-and-excel-delta-independent-review-before-<REVIEWED_HEAD>.md
同名归档内容不同则使用唯一后缀，不能覆盖。原首页独立报告保留旧结论，联合报告引用它并给出新 HEAD 下的 closure；不制造两份竞争的当前结论。

报告须包含版本/hash、逐项需求矩阵、finding 闭环、实际路由、字段和 workbook 差异、数据保留依据、测试/浏览器证据、复用证据的影响分析、未运行项及下一步。
每个新 finding 有 ID、严重度、实际位置/生产路径、违反条款、复现证据、影响和修复方向。发现阻塞继续其余独立检查，不现场修复。
结束复核受审代码 HEAD、工作树及 workbook hash 稳定；只允许本报告/证据和已识别的隔离测试临时输出变化。

判定：
- PASS：上述必检范围完成，无阻塞，新 HEAD 与输出文件证据稳定；人工最终验收仍单独待确认。
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
OTHER_FIELDS_AND_DATA_PRESERVED=PASS/FAIL/NOT_RUN
LARGE_SHEET_NAME=PASS/FAIL/NOT_RUN
FIVE_MODULE_CONTRACT_AND_CONSUMERS=PASS/FAIL/NOT_RUN
HOME_SUMMARY_REGRESSION=PASS/FAIL/NOT_RUN
MIGRATION_AND_DATA_SAFETY=PASS/FAIL/NOT_APPLICABLE/NOT_RUN
TEST_BUILD_EVIDENCE=VALID/INVALID/MISSING
HEAD_AND_WORKBOOK_STABLE=YES/NO
BLOCKING_FINDINGS=
REMAINING_CHECKS=
REPORT_PATH=
MANUAL_ACCEPTANCE=PENDING
NEXT=USER_MANUAL_ACCEPTANCE/TARGETED_REMEDIATION/COMPLETE_REVIEW

PASS 后由用户在实际页面与输出 Excel 做简短人工验收，再更新联合报告中的人工结果并按当前 Authority 恢复其他待办；不自动启动新业务建设。
