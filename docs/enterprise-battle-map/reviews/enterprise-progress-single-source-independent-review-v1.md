# 作战进展单一存储及三入口一致性：独立审查 V1

**状态：CURRENT REVIEW AUTHORITY / 本地实施完成并固定候选后执行**
**代码根：D:\BattleMap\battle-map / feature/enterprise-battle-map**
**事实来源：用户报告调查发现除MOX外均双写，已安排本地Agent按报告最小建议修复；云端未读取本地报告，不声明已修复或已验证。**

## 1. 任务与输入

本轮沿用真实调查报告中的最小修复建议，不重开实施方案。独立审查修复差异、实际运行与数据证据，不修改生产代码、测试、SQL或真实业务库，不替实施者修复、不commit/push。
只有隔离临时库/明确的测试副本可用于保存、失败注入与迁移验证；只读审查不等于禁止这些必要测试写入。

先更新：
git -C "D:\BattleMap\BattleMapenterprise-authority" pull --ff-only origin enterprise-battle-map-authority

读取Authority的docs/enterprise-battle-map/authority-index.md、本文件、共享架构V5第7节、共享表单V3第10节和五份当前模块契约。读取代码根AGENTS.md及：
docs/enterprise/investigations/enterprise-form-progress-legacy-parity-survey-v2-report.md
从此报告恢复准确findings、建议文件/操作范围与数据结论，再读取本次实际diff、提交说明和已有实施报告/日志。不要要求重造一个特定名称的实施报告；现有可核验证据足够即可。
报告路径变化时用rg定位并核对内容；缺少报告先核对实际代码/测试/DB证据，完成可做检查，不冒称读过或忽略未闭环finding。

已知重点是TOB、ISP、电力、大企；MOX“无双写”仅为用户转述，仍须回归。逐项列出调查finding→最小建议→实际修改→新证据，范围外变化单列，不按“最小”二字豁免数据或UI缺陷。

## 2. 固定审查对象

记录AUTHORITY_HEAD、调查观察版本/dirty差异、修复前BASE_HEAD、IMPLEMENTATION_HEAD、REVIEWED_HEAD、实际review worktree和服务/构建来源。
先确认本地实施结束，同一代码/服务无并发写入。受审代码、测试及可执行依赖必须完整在固定候选中；按integration/enterprise-review-snapshot-preparation-v1.md核对，不由审查者替实施者提交或清理。
有相关未提交代码时可做预检查，但不得以干净HEAD名义给其PASS；返回准确未固定文件与运行来源缺口。不要求Excel、数据库或审查报告入Git，不要求联网拉最新代码或push。
新候选若为独立worktree，测试与浏览器必须指向该候选，不能仍用主工作树旧服务。

只读确定当前应用真实DB路径、schema/已执行迁移版本、是否已应用本次迁移。用一致性快照/项目现有备份机制建立隔离测试副本，不复制仍在写入的SQLite主文件后忽略WAL；不为取证启动会自动迁移真实库的应用。
分别标记代码修复、隔离升级验证、用户当前实库状态，不能以测试副本通过宣称实库已升级。

## 3. 双写是否在完整生产链消失

五模块按三入口建立矩阵：业务新增页、业务编辑页、独立新增进展弹窗。
每行记录真实UI/model→API方法/path/payload→operation/adapter→database.js/SQL→物理表列及业务关联。主题和内容须分别追踪，不能把业务主题当弹窗标题栏。

目标：
- Progress History为唯一持久化事实源；battleProgress保留canonical身份，作为latest投影/特殊编辑入口，不能因移除冗余物理列而删业务字段。
- 三入口消费同一共享进展操作与校验/持久化规则。模块保留独立contract与关系映射，不复制四套修补逻辑。
- 业务表的insert/update/upsert、通用序列化、ORM/DB默认赋值、trigger、批量/导入等实际存在的写入口，不再保存第二份进展文本。相关导入功能应走同一目标操作或明确拒绝不支持的输入，不能静默丢进展。
- 最新摘要、列表/详情、历史、相关导出/筛选等真实消费者从History投影读取，不保留业务文本fallback或旧alias活动兼容。
- 检查事件双触发、父表保存与进展保存分别追加、watcher/回调再写、重复请求等是否导致History本身插入两次。仅证明“没写业务表”还不够。
- SQL历史字样、一次性迁移代码、只读内存投影、废弃列存在本身不等于活动双写；分别报告活动写入、活动fallback、schema冗余和数据未迁移，不能靠rg命中直接判定。

用实际生产保存路径及数据库前后差异/SQL证据证明：每个有效新增动作只产生预期的一条History，主题/内容和父记录/module正确，既有历史不被覆盖，其他业务字段正常保存。不得仅mock History方法或断言调用次数替代落库证据。

## 4. 历史数据与迁移

按实际schema与数据比较business text和History，覆盖：仅业务表有值、仅History有值、两边一致、两边不同、空值、相同正文但不同主题/时间、关联异常。是否需要数据搬迁以事实决定，不先假定四模块均需新增SQL。
独有主题/内容与原有记录必须保留；两边不同不能简单取一侧覆盖另一侧。无可靠业务时间/主题时不能编造，无法安全解释的记录应明确阻塞对应收敛步骤。
去重必须有真实来源/关联依据，不能只凭正文相同误删不同事件；重复执行不得再次导入相同来源记录。不得把迁移执行时间伪装成历史业务时间，导致latest排序改变。
如果有物理schema变更：
- 已执行V*.sql内容、顺序和账本不可重写；使用当前项目正式增量版本与生产runner。
- 新库与升级库终态一致；生产完整迁移链确实执行新版本，失败回滚，重复启动/执行安全。
- 删除冗余列前已有独有数据保留与读写切换证据；不能把先删后丢数据解释成消除双写。
- 相关客户关系、索引/约束和其他数据保持；不能为修复进展删除额外字段。
- 历史阶段fixture/预期保留历史schema；最终schema断言来自明确契约，不取PRAGMA结果生成expected，不把MOX40/TOB33/ISP24/电力27/大企25业务身份数硬编码为物理列数。

核验现存实库实际状态及已有实施迁移证据。若仅代码/隔离库完成，明确LIVE_DB_STATUS与剩余步骤；审查者不代执行生产迁移。没有升级前数据/备份等依据时不能声称历史数据全部已保留。

## 5. 三入口与UI回归

以本地BattleMap应用主分支MOX/TOB的旧交互和调查证据为UI基线，不能把主分支旧双写复制回来。
新增页、编辑页均保留：只读最新摘要→可展开新增按钮→可编辑主题→可编辑内容；无历史的新建页面仍保留结构。
四处原名称仅做已确认“作战”命名调整，保留最新/新增限定词。独立新增进展弹窗与两页在主题/内容含义、校验、数据关联、保存结果与最新/历史回显上一致；弹窗外壳和新建父记录ID时机按既有生命周期处理。
核验：
1. Create父记录ID产生前草稿不写进展，保存失败不留下孤立进展；业务/进展组合失败不被当成完整成功，恢复或重试不重复创建。
2. Edit新增进展追加，原历史保留；仅改其他字段、无新增草稿、取消时不新增进展；部分输入按实际contract校验，不默认拼接或吞掉主题。
3. 独立弹窗新增后两页最新摘要与历史刷新正确；重新打开/刷新页面后仍读到同一记录。
4. 连点/重试和真实失败路径无重复History；如已有编辑历史能力，保留其与“新增一条”的明确区别。
5. 五模块保留真实共享表单渲染链，不回退本地完整builder；独立popup不能替代表单内按钮。
6. 底部固定取消/保存按钮按报告最小建议检查：若本次已修复则对照位置/样式/滚动可见性验收；若未纳入实施则列为原UI待办，不能宣称整体表单问题全部解决。双滚动用户接受，不因它判错，不扩展其他样式。

真实页面取三入口证据，并用隔离数据执行保存/取消/重开。无浏览器能力记NOT_RUN，不能用源码推断UI已通过。
MOX至少覆盖共享改动实际影响的三入口与持久化；其余四模块逐一证明，不能抽一个代替全部。

## 6. 验证与结论

复查实际测试diff，检查是否删断言/skip、只覆盖空值或mock、从被测结果生成expected来绿灯。针对真实保存、迁移、错误/重复提交和UI遗漏补齐应有证据；审查者不修改测试。
执行本次针对性测试、必要build和共享操作影响的既有门禁；五模块机制复核沿索引第7节的完整审查基线逐项记录执行或同一候选可信证据的复用依据。未受影响首页/Excel不机械重跑，不能用修改前PASS覆盖受影响链路。
每项结论关联具体代码、命令/退出码、数据库差异、截图与候选版本。已证实阻塞继续其他独立检查，不现场修复。

唯一专项报告：
docs/enterprise/reviews/enterprise-progress-single-source-independent-review-v1-report.md
证据：
docs/enterprise/reviews/evidence/enterprise-progress-single-source-v1/<REVIEWED_HEAD>/<RUN_ID>/
已有同名报告先归档到docs/enterprise/reviews/history/，带旧HEAD和唯一后缀；旧调查/联合报告不改写。联合复核引用本专项对应HEAD结论，不制造相互竞争的当前结论。
只写本报告、证据与历史归档，不提交。结束核对代码、运行版本稳定。

RESULT：
- PASS：本专项必检完成，无阻塞且证据稳定；仍单列真实库应用状态及原UI待办，不等于整个企业模块最终验收。
- FAIL：有实际双写/fallback、丢数据、三入口功能回归、契约或必要测试缺陷，给准确finding。
- PARTIAL：必要候选/实库/运行证据不足，不能由源码审查冒充已验证。
代码/隔离验证充分但实库未升级，可分别给子项PASS；整体实库修复完成状态不得给PASS。

回执：
RESULT=PASS/FAIL/PARTIAL
REVIEWED_HEAD=
RUNTIME_SOURCE_MATCHES_REVIEWED_HEAD=
FOUR_MODULE_DOUBLE_WRITE_CLOSURE=
MOX_REGRESSION=
THREE_ENTRY_CONSISTENCY=
HISTORY_DATA_PRESERVATION=
MIGRATION_CHAIN_AND_RETRY_SAFETY=
LIVE_DB_STATUS=
INLINE_PROGRESS_UI=
FOOTER_STATUS=
TEST_AND_BROWSER_EVIDENCE=
BLOCKING_FINDINGS=
REMAINING_ITEMS=
REPORT_PATH=
NEXT=TARGETED_REMEDIATION/COMPLETE_EVIDENCE/USER_MANUAL_ACCEPTANCE
