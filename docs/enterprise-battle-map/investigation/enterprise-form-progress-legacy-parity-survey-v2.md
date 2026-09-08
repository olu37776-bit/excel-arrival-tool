# 企业表单两处对照调查 V2：底栏按钮、作战进展

**状态：CURRENT / 只读调查，不现场修复**
**工作树：D:\BattleMap\battle-map / feature/enterprise-battle-map**
**基线：本地BattleMap主分支MOX、TOB的对应新增页和编辑页**
**取代：enterprise-form-scroll-progress-survey-v1.md的当前调查口径；旧报告保留**

## 1. 只有两块范围

| 区域 | 对照目标 |
|---|---|
| 底部操作栏 | 保留主分支对应页面固定可见的底栏，以及取消/保存按钮的位置、字体、颜色、尺寸、间距和样式；不重新设计保存/取消逻辑 |
| 作战进展区域 | 保留主分支对应页面的原功能、控件、展开行为和样式，只把可见“进展”文案加上“作战” |

**新增页与编辑页原本不同，必须分开对照，不要求改成一样。** 以主分支同模块、同模式的真实实现为准，不把编辑页的摘要/历史展示或展开区硬套到新增页，也不以新增页替代编辑页。
用户描述的“最新摘要→新增按钮→展开主题/内容”须在原本具备该交互的对应页面完整保留；不能以当前readonly摘要加独立历史弹窗替代原表单内编辑。摘要本身只读不代表整个进展区域只读。
双滚动用户确认旧版就有且可接受，不再调查消除。其他字段、其他表单区域、整体布局和样式均不在本次范围；不要借这两点再做全表单改造。

命名仅限实际UI文案，保留原限定词：

| 原文案（实际存在时） | 目标文案 |
|---|---|
| 进展 | 作战进展 |
| 最新进展 | 最新作战进展 |
| 新增进展 | 新增作战进展 |
| 进展主题 | 作战进展主题 |
| 进展内容 | 作战进展内容 |
| 进展历史 | 作战进展历史 |

已含“作战进展”的文案不重复加前缀。不修改canonical key、API/数据库身份、用户正文、历史数据、字段数或保存语义，不全仓替换字符串。

## 2. 直接读取指定主分支

更新：
git -C "D:\BattleMap\BattleMapenterprise-authority" pull --ff-only origin enterprise-battle-map-authority

读取Authority目录docs/enterprise-battle-map下的authority-index.md、本文件，以及共享架构V5第7节、五模块共享表单V3第6/10节和实际字段契约。
读取代码根AGENTS.md与旧调查报告：
docs/enterprise/investigations/enterprise-form-scroll-progress-survey-v1-report.md

准确参照是**D:\BattleMap\battle-map应用仓库的主分支MOX/TOB**，不是云端excel-arrival-tool文档仓库main，也不是当前独立进展弹窗。
核实本地主分支ref（优先main，以实际仓库为准）并记录完整SHA；用git show/git ls-tree等只读方式读取其MOX/TOB页面、底栏、进展组件、样式和相关处理，再对照当前feature分支。用rg恢复实际路径，不切换或覆盖当前工作树，不把main文件复制回生产代码。
本地指定基线即可开始，不要求先联网更新；origin/main如可见只说明已知缓存状态，不称最新远程。不漫无目的寻找其他旧版本。
记录当前HEAD、相关未提交diff/hash、运行目录/构建来源、视口/缩放。允许调查当前未提交现场，不要求先commit；同一运行链不得并发写入。
基线ref/页面确实不可取得时报告准确缺项；不能用不相干页面凑对照。

## 3. 分模式建立证据

先分别对照主分支与当前的MOX Create、MOX Edit、TOB Create、TOB Edit，再核查其他三模块相应模式的共享实现。其他模块保持其独立业务字段/分组，不复制MOX字段结构。
每项记录：模块/模式、主分支实现与行为、当前对应实现、差异、源码/组件/样式来源和证据。

底栏：
- 核对footer容器/slot、固定可见行为、取消/保存按钮及其计算样式；同视口滚动前后取证。
- 仅识别本区域样式或接线丢失，不改其他字段字体/布局，不清除内外滚动条。

作战进展：
- 对照同模式原有摘要、按钮、展开状态、主题/内容控件、只读/可编辑差异、样式及取消/保存行为。
- 追踪当前fieldDef/controlId/editorId、runtime投影、registry、特殊editor、props/slot/事件，定位能力丢失而非仅记录“现在readonly”。
- 按主分支实际逻辑读取新增记录尚无业务ID、编辑既有记录时的草稿/提交时机；本次不重新设计两种模式。
- 只读追踪主题/内容到Progress History及latest投影，区分准确代码事实与未执行的保存往返。不向真实库写测试记录。
- 旧报告中“当前只有readonly和独立弹窗”的观察可保留，但不能据此认定与旧交互等价。主分支对照确定的误判在新报告纠正，不覆盖旧证据。

Progress History仍是唯一持久化事实源；表单内编辑与独立弹窗可以共用进展操作。保留旧交互不等于恢复双写、复制五套旧表单或把整个独立dialog嵌进表单。
旧/新环境如可安全观察则用同视口截图/DOM和computed style；旧环境无法运行就明确视觉证据缺口。不得启动会改真实库的旧应用，不注入CSS试改。

## 4. 产物与停止点

唯一新调查报告：
docs/enterprise/investigations/enterprise-form-progress-legacy-parity-survey-v2-report.md

证据：
docs/enterprise/investigations/evidence/enterprise-form-progress-legacy-parity-survey-v2/<BASE_HEAD>/

报告包含基线/当前版本、分模块分模式矩阵、两块区域旧新对照、根因证据/假设、原报告需纠正的判断、建议恢复文件范围与验证点。能定位变化提交/hunk则记录，不把额外历史追踪当完成对照前置。
只写本调查报告/证据；同名产物保留历史。生产代码、CSS、测试、SQL、Excel、真实数据和其他报告不动，不提交、不push，不自动进入修复。

回执：
RESULT=INVESTIGATED/PARTIAL/BLOCKED
MAIN_REFERENCE_SHA=
OBSERVED_CURRENT_HEAD_AND_DIRTY_STATE=
FOOTER_BUTTON_STYLE_DIFF=
PROGRESS_CREATE_MODE_DIFF=
PROGRESS_EDIT_MODE_DIFF=
MODE_DIFFERENCES_PRESERVED_IN_PROPOSAL=
ROOT_CAUSE_EVIDENCE=
PROPOSED_TWO_AREA_RESTORE_SCOPE=
REPORT_PATH=
UNRESOLVED=
NEXT=DEFINE_TARGETED_RESTORATION/COMPLETE_SPECIFIC_COMPARISON
