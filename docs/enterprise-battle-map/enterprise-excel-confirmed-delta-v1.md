# 新版 Excel 两项已确认变更 V1

**状态：CURRENT / 用户已确认，待本地实施**  
**文档分支：enterprise-battle-map-authority**

## 1. 本轮准确含义及优先级

用户要求：“整体空间……这个字段全部删除，每个表都是”，并再次纠正：“是删除整体空间这个字段”。

1. 每个业务工作表中的“整体空间”字段整列删除，包含表头、列内数据、该字段的下拉验证和字段定义。不能仅删“肥肉/瘦肉/骨头”三个选项、清空数据或隐藏列。三个取值用于准确识别被删除字段。用户再次限定：“整体空间 肥肉／瘦肉／骨头，其他不要动”。因此只删除这个分类字段，其他字段、数据和业务规则保持不变；尤其“整体空间（M$）”、跳数等独立数值字段不在删除范围。
2. 大企工作表名称改为“大企（油气矿、广电、交通）”，增加“交通”。

本文件对以上两点优先于既有模块 Authority、Excel V0.2 字段冻结说明及历史固定字段数量断言。其余 V0.2 差异仍需逐项调查，不因本轮自动获准。旧报告保留为旧 HEAD 的证据。首页 V4 已由用户报告存在跳转阻塞，按 authority-index.md 和首页跳转修复 V1 处理；本任务不能将首页改记为 PASS。

## 2. 本地输入与实施顺序

Authority checkout：D:\BattleMap\BattleMapenterprise-authority  
代码：D:\BattleMap\battle-map（feature/enterprise-battle-map）  
Excel 从 D:\BattleMap 中按既有调查报告定位用户所说的新版基表；优先恢复已确认输入路径，不能凭修改时间猜多个候选中的一个。

1. 读取本文件、authority-index.md、既有 V0.1/V0.2 调查及本地报告，核对实际 workbook、sheet、字段定义和代码 HEAD。
2. 记录输入路径、文件 hash、sheet 清单、删除字段位置、原表名及依赖引用，写最小实施计划。
3. 原始工作簿先备份，再修改明确命名的输出副本；报告准确给出原件、备份及输出路径。如果新版已完成某项，验证后记为已满足，不重复删除相邻列。
4. 对每个业务 sheet 核查“整体空间”字段；存在则整列删除，不存在则记录。多行/合并表头按实际字段身份判断，不能用包含“整体空间”的字符串批量删除其他列或整个分组。若命中不唯一，先定位具体冲突，继续可确定的工作。
5. 大企 sheet 改用上述名称，并修正真实受影响的公式、名称、验证范围及导入/导出映射。检查列删除后的公式和范围移动、合并表头、表格范围、筛选、冻结及格式。
6. 重新打开输出文件核对各 sheet 的最终字段、数据对应关系和公式引用；保留宏等源文件功能，不能静默降级格式或丢失功能。新增“交通”仅修改已要求的表名，不额外创建交通 sheet 或业务模块。

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
- 所有业务 sheet 的字段整列删除、相邻数据完整、新表名、公式/验证引用有效；
- 五模块真实表格及共享 Create/Edit 中不再出现该字段，保存/重读正常；
- 当前契约、API、导入导出和实际受影响消费者一致，无 active legacy alias；
- 如有迁移，新库/升级库的最终结构一致，其他业务数据保持正确；
- 首页受影响指标及大企入口无回归。

根据实际改动运行必要测试和项目既有构建门禁；测试验证真实生产路径，不以文本搜索代替功能证据。纯 Excel 修改不机械重跑无关代码测试；代码发生修改则使用对应新实现的证据。不得将本轮实现自测称为独立审查通过。

本地计划：
docs/enterprise/implementation/enterprise-excel-confirmed-delta-v1-plan.md

本地报告：
docs/enterprise/implementation/enterprise-excel-confirmed-delta-v1-report.md

报告记录 AUTHORITY_HEAD、BASE_HEAD、实现提交、workbook 输入/输出及 hash、每表前后字段清单、canonical/DB/消费者映射、修改范围、验证结果和未完成项。保留已有报告历史。工作簿及业务数据留在本地，不提交到 GitHub。

最终简短回执：
RESULT=IMPLEMENTED/PARTIAL/BLOCKED
AUTHORITY_HEAD=
IMPLEMENTATION_HEAD=
WORKBOOK_OUTPUT=
ALL_SHEETS_OVERALL_SPACE_FIELD_REMOVED=
LARGE_SHEET_NAME=
APPLICATION_CONTRACT_CONVERGENCE=
VALIDATION=
REPORT_PATH=
REMAINING=
