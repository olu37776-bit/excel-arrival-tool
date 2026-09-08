# 新版 Excel 两项已确认变更 V1

**状态：CURRENT / IMPLEMENTED_REPORTED / 待联合独立核验**  
**文档分支：enterprise-battle-map-authority**

## 1. 本轮准确含义及优先级

用户要求：“整体空间……这个字段全部删除，每个表都是”，并再次纠正：“是删除整体空间这个字段”。

1. 每个业务工作表中的“整体空间”字段整列删除，包含表头、列内数据、该字段的下拉验证和字段定义。不能仅删“肥肉/瘦肉/骨头”三个选项、清空数据或隐藏列。三个取值用于准确识别被删除字段。用户再次限定：“整体空间 肥肉／瘦肉／骨头，其他不要动”。因此只删除这个分类字段，其他字段、数据和业务规则保持不变；尤其“整体空间（M$）”、跳数等独立数值字段不在删除范围。
2. 大企工作表名称改为“大企（油气矿、广电、交通）”，增加“交通”。

本文件对以上两点优先于既有模块 Authority、Excel V0.2 字段冻结说明及历史固定字段数量断言。其余 V0.2 差异仍需逐项调查，不因本轮自动获准。旧报告保留为旧 HEAD 的证据。2026-09-08 用户报告首页和删除字段均完成。当前按 `reviews/enterprise-home-and-excel-delta-independent-review-v1.md` 核验输出、字段收敛、大企改名及首页回归，不再重复实施；具体完成事实以本地证据为准，不自行标 PASS。下面保留原实施流程供核对，不向审查者授予写入权限。

## 2. 本地文件与当前核验方式

Authority checkout：D:\BattleMap\BattleMapenterprise-authority
代码：D:\BattleMap\battle-map（feature/enterprise-battle-map）

用户最新明确：Excel 就在根目录，不需要进入 Git。先检查代码根 D:\BattleMap\battle-map，必要时检查既有资料根 D:\BattleMap 的直属工作簿。通过文件系统列举实际文件，包括 ignored/untracked 文件；排除锁文件，按文件名、版本、sheet 和表头确定当前基表，记录真实绝对路径与 SHA-256。多候选无法区分时报告具体冲突，不能猜测。

用户已报告改动完成，当前只读实际工作簿核对字段、名称及与应用契约的一致性，不要求重新实施改表，不要求单独输出文件、Git提交记录或单独 Excel 实施报告。
现有计划/报告/旧版本可作辅助事实；缺少它们时直接核验实物。没有历史副本时不声称核实了全部历史编辑差异；按联合复核 V1第4节记录可证明范围，不据此单独阻塞当前核验。
如果实物不符合两项已确认要求，记录准确 sheet/字段证据后按原范围修复，保留原文件和其他数据；不能为通过检查扩大删除范围或静默改写当前源表。
原有修改列/表名所需的公式、验证范围、合并表头及格式完整性继续要求有效，不能只看字段数。新增“交通”只改已要求表名，不新增交通 sheet/模块。

## 3. 项目中的对应字段收敛（仅限被删除字段）

本轮业务变更进入当前字段契约，不能只在 Excel 中删除、页面仍维护同一字段。

先以实际 Excel 和代码建立“整体空间”字段 → canonical key → DB 列 → 消费者映射。既有 TOB/ISP/电力/大企 Authority 的该分类字段均为 overallSpaceTier；MOX 的精确 canonical key 仍需从真实契约核实。此 key 仅作为一次性删除映射，不再属于最终有效字段。删除字段的当前定义及有效消费者，包括实际存在的表格、Create/Edit、校验、筛选、Heatmap、导入导出及 API 投影。最终不能通过隐藏 UI 或保留空选项冒充字段删除。

- 五份当前模块 Authority 已同步最终字段集合：MOX 40、TOB 33、ISP 24、电力27、大企25。仅删除一个分类字段，其后 order 前移一位，其他身份不变；Create/Edit 可见项仍按 visibility/mode 派生，不能把业务总数字段等同于视图可编辑数量。数量描述目标契约，实际完成情况按本地证据记录。
- 继续由共享表单渲染器消费模块契约；不为删字段引入模块本地表单构建器或兼容分支。
- 大企工作表名及直接对应的完整表名展示同步更新，不顺带改写其他页面文案；内部稳定模块 ID、客户主键及路由 identity 不因中文标题变化重建。
- 持久化结构如需调整，按现有迁移机制编写可验证迁移；在隔离的新库和升级副本中验证，不直接操作真实业务库。保留历史迁移文件，旧分类数据不得转换为其他字段数据。
- 检查首页金额/空间指标是否引用被删字段；按实际 canonical identity 确认影响，不因名称相近误改其他指标或金额列。发现真实依赖且缺少替代业务规则时，报告具体依赖，不能自行发明计算规则。

本轮不要求重新实现已有共享机制；仅修改上述两项涉及的真实链路。

## 4. 验证与报告

验证应覆盖：
- 根目录实际工作簿的全部业务 sheet 符合最终字段/名称要求，其他字段与数值列对应正确、公式/验证引用有效；
- 五模块真实表格及共享 Create/Edit 中不再出现该字段，保存/重读正常；
- 当前契约、API、导入导出和实际受影响消费者一致，无 active legacy alias；
- 如有迁移，新库/升级库的最终结构一致，其他业务数据保持正确；
- 首页受影响指标及大企入口无回归。

根据实际改动运行必要测试和项目既有构建门禁；测试验证真实生产路径，不以文本搜索代替功能证据。纯 Excel 修改不机械重跑无关代码测试；代码发生修改则使用对应新实现的证据。不得将本轮实现自测称为独立审查通过。

测试维护补充：本轮已报告多项既有测试失败，按 `remediation/enterprise-confirmed-delta-test-expectation-alignment-v1.md` 分类后对齐；旧升级输入保留旧结构，仍有效的金额/数据保留断言不能放宽。正在执行的独立审查不现场修改测试。

原实施计划路径（如存在则参考，不是实物核验前置）：
docs/enterprise/implementation/enterprise-excel-confirmed-delta-v1-plan.md

原独立 Excel 实施报告路径（可选，不要求补造）：
docs/enterprise/implementation/enterprise-excel-confirmed-delta-v1-report.md

当前直接将真实工作簿路径/hash、每表实际字段和名称、canonical/DB/消费者核对、验证结果及未完成项写入正在执行的修复报告或联合审查报告，无需另补一份 Excel 实施报告。已有旧报告保留历史；工作簿及业务数据留在本地，不提交到 GitHub。

最终简短回执：
RESULT=IMPLEMENTED/PARTIAL/BLOCKED
AUTHORITY_HEAD=
IMPLEMENTATION_HEAD=
WORKBOOK_PATH=
ALL_SHEETS_OVERALL_SPACE_FIELD_REMOVED=
LARGE_SHEET_NAME=
APPLICATION_CONTRACT_CONVERGENCE=
VALIDATION=
REPORT_PATH=
REMAINING=
