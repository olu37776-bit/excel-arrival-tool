# 企业新增/编辑双滚动与作战进展差异：只读调查 V1

**状态：SUPERSEDED / 历史调查口径保留，不再按本文件继续执行**
**当前入口：`investigation/enterprise-form-progress-legacy-parity-survey-v2.md`**
**代码根：D:\BattleMap\battle-map / feature/enterprise-battle-map**

用户最新已确认：双滚动原来就有且可接受；主分支MOX/TOB页面才是旧行为基线。当前范围只有底栏取消/保存按钮样式及进展区域，新增/编辑按主分支对应模式保留差异；其他表单区域不动，仅统一进展可见文案。下文为旧调查任务历史，不再以独立弹窗替代表单内编辑，也不继续调查消除双滚动。

## 1. 调查目标与边界（历史）

用户人工发现：
1. 新增/编辑窗口同时出现内外两条竖向滚动条，怀疑套了两层窗口。
2. 表单中的“作战进展”与以前不同，应参照现有“新增进展”独立弹窗的样式；该弹窗有标题和内容，不只是内容。

本轮确认复现范围、真实渲染/滚动链、进展组件与数据结构差异，输出根因证据和最小修复建议，不现场修复。
两条滚动条不自动证明双弹窗；textarea内部滚动也不自动等于表单重复滚动。区分实际结构后再下结论。
用户指定独立“新增进展”弹窗为参照；核实其中“标题”属于弹窗标题栏、字段标签还是进展记录业务标题，不能自行新增字段或把不同概念混用。

只允许写本轮调查报告和证据。生产代码、CSS、测试、SQL、Excel、业务数据库、其他实施/独立报告保持原样；不提交、不push、不merge，不reset/clean。既有首页/选项修复已授权，但不在本调查会话混做。

## 2. 更新与读取

先更新文档：
git -C "D:\BattleMap\BattleMapenterprise-authority" pull --ff-only origin enterprise-battle-map-authority

在该目录的docs/enterprise-battle-map下读取：
- authority-index.md、本文件；
- enterprise-contract-architecture-v5.md第3/7节；
- remediation/five-module-shared-form-renderer-convergence-v3.md第6/10/16节；
- remediation/tob-shared-form-production-path-repair-v1.md；
- 实际涉及模块的当前字段规范及最近本地实施/审查报告。

代码根读取适用AGENTS.md，用rg定位当前真实页面/组件/样式与报告，不猜测文件路径。
记录AUTHORITY_HEAD、BASE_HEAD、实际代码/运行目录、分支、工作树状态、浏览器视口和缩放。核对实际服务来自源码还是旧构建，不能拿另一个实例解释用户页面。
本轮是调查，不是固定HEAD独立验收：允许读取用户当前含未提交改动的运行现场，无需先提交才能调查。记录相关diff/文件hash和运行版本归属，不把工作树观察写成BASE_HEAD已验证。调查前后检查相关源文件稳定；若别的任务正在写同一运行链，先协调停止写入，无法稳定则注明受影响证据并完成其余可做项。
Authority拉取失败记录实际本地版本，不称最新。

## 3. 五模块复现清单

MOX、TOB、ISP、电力、大企分别检查Create与Edit入口，记录：
- 实际路由/按钮、组件、是否复现、滚动条位置/控制的区域；
- “作战进展”入口、实际编辑/只读形态、是否有标题与内容；
- 对应独立新增进展弹窗是否存在、实际组件和表现。

先在一个确实复现的模块完整取证，再按共享链判断其他模块并核对实际入口；未运行项写NOT_RUN，不能根据一次打开推定五模块全部相同。
在同一视口对比，必要时补一个较小高度窗口；记录缩放/视口，不凭截图大小猜CSS问题。原有长内容如可只读观察则使用；不为造样例写真实数据。
仅打开/关闭弹窗、滚动、查看DOM/计算样式和现有请求。不触发新增、保存、删除或自动保存。若打开页面会自动迁移/写库，改用既有隔离环境或记录该限制，不直接启动真实业务库迁移。

## 4. 内外滚动条：证据必须定位到节点和来源

对复现入口记录实际组件链及DOM祖先链：
页面/背景body → dialog/modal/teleport → shared Form Shell → body/group容器 → field/editor。
这是观察路径，不预设这些都应该存在或都是滚动容器。

逐一记录实际可滚动节点：
- DOM标识、所属组件/源码位置；
- computed overflow/overflow-y、height/max-height/min-height、padding及相关flex/grid约束；
- clientHeight、scrollHeight、scrollTop与可见滚动条位置；
- 滚动内外两侧分别移动什么，背景页面是否仍跟随滚动，标题/操作按钮是否在预期位置。

核查：
- 模块页面是否仍包一层dialog，shared shell内部又建立dialog；
- 单一dialog是否因外层body与内部表单都设置overflow/max-height而双滚；
- 背景body滚动锁定、teleport层级、祖先高度/flex子项min-height等是否参与；
- 滚动条是否实际来自textarea/富文本等字段内部，是否属于合理独立编辑区域；
- 两条滚动条是否同时控制同一表单内容，而非仅凭“都在右侧”判断。

将现象、源码规则、计算布局和滚动行为对应。只能确认静态可疑代码时标HYPOTHESIS，不写根因已证明。
建议可以指出应由哪层负责主表单滚动及哪些编辑器保留内部滚动，但本轮不改overflow、不隐藏滚动条、不删除容器、不注入CSS试改。

## 5. 作战进展：对照独立新增进展弹窗

并列比较同模块表单内进展区域和独立弹窗：
- 标题栏、进展业务标题输入（若有）、内容编辑器、标签/placeholder、只读/可编辑状态；
- 样式class/token、间距、边框、编辑器类型及可见控件；
- 实际组件、props/model、事件、注册editorId/controlId及shared registry派发；
- 是否直接复用内容编辑组件，是否只复制外观，是否退化成普通textarea；
- 若内嵌的是整个独立dialog而非内容组件，是否同时解释双层窗口/双滚；必须有真实组件/DOM证据，不能预先认定两问题同根因。

继续只读追踪标题和内容的真实身份：
字段契约 → runtime projection/editor binding → model/adapters → 现有Progress API → History实体/列 → latest/current展示。
精确key以本地代码为准，不假定弹窗标题就等于记录title字段。确认标题是控件未渲染、绑定/投影丢失、数据本来没有，还是只存在外壳标题。
只读检查既有保存处理、payload构造和测试/日志；本轮不实际写业务记录验证。没有写入证据时明确区分“静态路径已读”和“保存往返未执行”。

保持既有边界：Progress History为唯一持久化事实源，battleProgress为当前/最新投影或特殊editor入口。调查建议不得恢复业务表第二份progress文本、双写或长期fallback；不因希望复用弹窗样式而再嵌一整个modal。
如有对应旧截图、实施报告或可定位的git历史，核对变化引入的具体提交/未提交hunk；不能仅凭“以前不同”推定某次共享迁移是根因，也不为还原旧外观恢复已废止架构。缺少可信旧版本时如实记录，只比较当前两个真实入口。
找出既有测试为何未覆盖用户看到的差异；只记录缺口和建议验证点，不改测试。

## 6. 报告与退出

本地唯一调查报告：
docs/enterprise/investigations/enterprise-form-scroll-progress-survey-v1-report.md

证据目录：
docs/enterprise/investigations/evidence/enterprise-form-scroll-progress-survey-v1/<BASE_HEAD>/

同名旧报告保留历史副本；不覆盖现有独立审查结论。截图/DOM/计算样式和必要日志只保留证明问题所需内容，业务数据留本地，不要求上传。

报告必须包含：
- 运行版本、工作树差异归属、五模块Create/Edit复现矩阵；
- 双滚节点/组件链、滚动行为、样式来源及尺寸证据；
- 表单内与独立进展弹窗的标题/内容/样式/数据映射对照；
- 已证实事实、根因假设、未运行项分别列明；
- 两问题是否同根因及证据；
- 可供后续批准实施的最小修复方向、具体建议文件级WRITE_SCOPE、应保留行为及验证点。

只读调查完成不等于独立验收PASS；环境不足时尽量完成源码定位，报告具体缺项，不为了形成结论猜测。
完成后停止，不自动进入修复或新建生产/测试文件。

回执：
RESULT=INVESTIGATED/PARTIAL/BLOCKED
OBSERVED_BASE_HEAD=
RUNTIME_SOURCE_AND_DIRTY_STATE=
FORM_SCROLL_REPRODUCTION=
SCROLL_OWNERS_AND_CAUSE=
PROGRESS_TITLE_CONTENT_DIFFERENCE=
PROGRESS_COMPONENT_AND_DATA_MAPPING=
SAME_ROOT_CAUSE=YES/NO/UNCONFIRMED
REPORT_PATH=
EVIDENCE_PATH=
UNRESOLVED=
NEXT=DEFINE_TARGETED_REMEDIATION/COMPLETE_SPECIFIC_INVESTIGATION
