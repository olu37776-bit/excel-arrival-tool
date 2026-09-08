# 企业表单两处重新调查 V2：底栏按钮、作战进展及其存储

**状态：CURRENT / 重新只读调查，不现场修复**
**代码根：D:\BattleMap\battle-map / feature/enterprise-battle-map**
**参照：本地BattleMap主分支MOX、TOB页面**
**本版已撤销“新增与编辑的进展结构不同”的错误前提；旧报告保留历史**

## 1. 最新准确要求

调查范围只有两块：
1. 底部固定栏的“取消／保存”按钮及样式。
2. 作战进展区域的功能、样式，以及该区域对应的数据库读写映射。

**新增页和编辑页的进展UI结构都一样：**

| 顺序 | 控件 | 行为 |
|---|---|---|
| 1 | 最新作战进展 | 只读展示当前/最新记录 |
| 2 | 新增作战进展按钮 | 点击后在当前表单内展开编辑区 |
| 3 | 作战进展主题 | 可编辑输入 |
| 4 | 作战进展内容 | 可编辑输入 |

两个可编辑输入是主题与内容，不能把整个区域做成readonly，也不能以独立历史/新增弹窗替代此按钮和展开区。
新建尚无历史记录时可按既有方式显示空摘要，不因此删除上述UI结构。相同UI结构不代表新增业务记录与编辑已有记录的ID、草稿、提交时机必须相同：这些生命周期分别查清，不凭空重写。
只给原有“进展”UI文案加“作战”，保留最新/新增等限定词，不重复加前缀；canonical key、用户正文、历史数据和字段总数不因改名改变。

底部取消/保存栏按主分支原实现保持固定可见及原按钮样式。双滚动用户确认原本如此且可接受，不再调查消除。其他表单区域、字体、布局、字段、首页任务都不在本轮范围。

新增页、编辑页和独立“新增进展”弹窗必须纳入同一对照：四处原有名称（最新进展、新增进展、进展主题、进展内容）只做“作战”命名调整，其他原有功能、样式和交互不随改名变化。三入口的主题/内容语义、校验、payload、存储归属、父记录关联与保存后回显应一致；新增业务记录尚无ID等必要生命周期差异单独说明，不强行统一提交时机，也不把独立弹窗外壳套进表单。当前仅调查并报告差异，不执行改名或修复。

## 2. 输入与现场固定

先更新：
git -C "D:\BattleMap\BattleMapenterprise-authority" pull --ff-only origin enterprise-battle-map-authority

读取Authority目录docs/enterprise-battle-map下：
- authority-index.md、本文件；
- enterprise-contract-architecture-v5.md第7节；
- remediation/five-module-shared-form-renderer-convergence-v3.md第6/10节；
- 实际涉及模块的进展字段契约。

读取代码根AGENTS.md、旧V1调查报告及已有V2报告：
docs/enterprise/investigations/enterprise-form-scroll-progress-survey-v1-report.md
docs/enterprise/investigations/enterprise-form-progress-legacy-parity-survey-v2-report.md

新一轮如已有同名V2报告，先保存至docs/enterprise/investigations/history/下带原观察HEAD及唯一后缀的历史文件，再写当前报告；不覆盖旧证据，也不沿用错误前提。
记录AUTHORITY_HEAD、本地主分支完整SHA、当前BASE_HEAD、相关未提交diff/hash、实际服务/构建目录、数据库实际路径与当前schema/迁移版本、浏览器视口和缩放。当前工作树未提交不阻塞调查，但不能把其结果冒称固定HEAD独立验证。

使用D:\BattleMap\battle-map应用仓库的主分支MOX/TOB，主分支名称按真实ref核对；不是云端excel-arrival-tool文档仓库main。用git show/git ls-tree等读取主分支源码、样式及数据处理，不切换/覆盖当前树，不把main文件复制回生产代码。
可直接使用本地指定主分支；无需为调查强制联网更新。不猜测远程最新版本。读取当前页面时确保同一运行链无并发代码修改。

## 3. 两块UI对照

分别检查MOX/TOB主分支与当前的Create/Edit，再核对其他三模块共享接线，形成五模块×Create/Edit矩阵。每项验证同一四段进展结构，不再以模式不同为缺控件的理由。

底栏：
- 旧/新footer组件、slot、定位、滚动前后可见性、取消/保存按钮样式；
- 只查该区域，不调整其他字段或消除滚动条。

作战进展：
- readonly最新摘要、新增按钮、展开状态、主题/内容两个可编辑控件是否实际存在；
- 旧/新组件、fieldDef/controlId/editorId、projection、registry、特殊editor、props/model/slot/事件；
- 定位按钮/控件被删、readonly误派发、条件/绑定/事件丢失等实际原因，不能只描述“现在只读”就判正确；
- 最新展示读取什么字段，是否只有正文而主题被遗漏；对照主分支真实映射，不能把主题解释成弹窗标题栏；
- 读取新增/编辑草稿、取消、保存和重新打开处理；不向真实库提交测试记录。

同视口/主题取截图、DOM和两块区域computed style；旧环境不能安全运行时用源码/CSS和已有截图作部分对照，明确未实测项，不启动会自动改库的旧程序。

## 4. 数据库必须给出具体事实

本项属于进展区域的端到端调查，不是新增第三项数据库改造任务。
不要只写“使用History”就结束。分别记录主分支代码声明、当前代码声明与当前实际数据库事实，缺少旧运行库时不能把旧SQL当成已核验旧实库。

建立准确映射表：
按新增页、编辑页、独立新增进展弹窗三个入口分别列行，比较真实当前数据与主分支实现，不用一个入口的结论替代另外两个。
UI控件/摘要 → 前端model key → API路径/方法及payload key → handler/adapter → 实际表名/列名 → 父记录关联 → 最新进展读取规则。

至少回答：
1. 进展主题、进展内容各自的真实key和物理列是什么，是否独立存储；当前是否只保存内容、丢主题或拼成单个文本。
2. 记录写入进展历史表、模块业务表还是两处；读/写各自是谁负责，存在多个入口是否实际复用同一操作，有无双写/兜底/数据丢失。
3. 进展如何关联MOX/TOB/其他模块及具体业务记录：真实主键/外键或模块标识映射，是否缺ID/误绑。
4. Create尚无业务ID时主题/内容先放哪里，业务创建成功后何时写History；失败/取消是否可能留下孤立或提前保存的进展。
5. Edit展开新增进展后，保存是追加记录还是覆盖旧记录；空草稿、不展开、只改其他字段、重复提交分别走什么分支；根据真实代码描述，不预先规定答案。
6. 主题/内容的空值、必填、默认值和字段类型是否前后端/实库一致；UI可编辑却未进入payload或列缺失时明确断点。
7. 独立新增进展弹窗使用哪组主题/内容控件、校验、请求和持久化操作；与两页是否同源，取消是否未写入、提交是否追加且关联正确，保存后两页最新摘要/历史如何刷新。只追源码和只读事实，不实际提交。
8. 最新摘要具体按何种时间/排序/ID规则选取记录，读回是否包含主题与内容；保存后如何刷新，不能猜“最新=最大ID”。

只读连接实际数据库，核验相关schema、列/约束/关联及已执行迁移登记；按需要读取最少量、脱敏的关系/空值/记录证据，不导出整库或正文。不得通过应用初始化/自动迁移来“查看数据库”，不得绕过只读访问限制或修改锁/迁移账本。
区分SCHEMA_OBSERVED、SOURCE_PATH_TRACED和SAVE_ROUNDTRIP_NOT_RUN：本轮不能声称已执行真实保存验证。读取受限就报告具体缺口，仍完成源码映射；不把无法验证当成已通过。

既有目标仍是Progress History单一持久化事实源，表单内编辑和独立弹窗均可作为入口。不能为恢复UI复制业务表第二份progress文本、改SQL/历史迁移、增加模块业务字段或清洗历史数据。

## 5. 报告与停止点

当前报告：
docs/enterprise/investigations/enterprise-form-progress-legacy-parity-survey-v2-report.md

本轮证据使用不覆盖旧证据的目录：
docs/enterprise/investigations/evidence/enterprise-form-progress-legacy-parity-survey-v2/<BASE_HEAD>/<RUN_ID>/

报告包括两块旧新对照、Create/Edit相同结构检查矩阵、主题/内容完整数据库映射、新增与编辑各自保存生命周期、根因证据/假设、旧报告需纠正的判断、最小建议修复文件范围及验证点。
只写本调查报告/证据及其历史归档。生产代码、CSS、测试、SQL、Excel、真实数据和其他报告不动，不commit/push，不自动修复。

回执：
RESULT=INVESTIGATED/PARTIAL/BLOCKED
MAIN_REFERENCE_SHA=
OBSERVED_CURRENT_HEAD_AND_DIRTY_STATE=
FOOTER_BUTTON_STYLE_DIFF=
CREATE_AND_EDIT_COMMON_PROGRESS_STRUCTURE=
THREE_ENTRY_CONSISTENCY_MATRIX=
SUBJECT_CONTENT_UI_API_DB_MAPPING=
ACTUAL_DB_PATH_AND_SCHEMA_VERSION=
CREATE_SAVE_LIFECYCLE=
EDIT_SAVE_LIFECYCLE=
LATEST_PROGRESS_READ_RULE=
PERSISTENCE_OWNERSHIP_AND_GAPS=
ROOT_CAUSE_EVIDENCE=
REPORT_PATH=
UNRESOLVED=
NEXT=DEFINE_TARGETED_RESTORATION/COMPLETE_SPECIFIC_INVESTIGATION
