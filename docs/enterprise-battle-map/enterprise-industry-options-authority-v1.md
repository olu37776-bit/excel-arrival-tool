# 企业行业字段选项 Authority V1

**状态：CURRENT / 用户已确认，待本地实施**  
**范围：ISP、电力、大企现有 industry 字段的选项；不新增字段**  
**代码：D:\BattleMap\battle-map / feature/enterprise-battle-map**

## 1. 已确认选项

| 模块 | 行业可选项（按顺序） |
|---|---|
| ISP | ISP |
| 电力 | 电力 |
| 大企 | 油气矿、广电、交通 |

大企的“油气矿”是一个选项，不拆成油、气、矿；“交通”是第三个选项，不另建交通字段或模块。
不增加“其他”“大企”“ISP&大企”等业务选项。现有空值/必填及筛选“全部”等交互规则保持：占位或清除筛选不是新的行业业务值。本轮不新增默认选择规则，也不将已有数据批量改成唯一可选值。
如果已有持久化使用稳定 code，保留其既有身份，明确展示选项与 code 的映射；不因改选项重命名 canonical key 或制造长期别名。

本次行业枚举依据用户最新明确要求，优先于旧 Excel 验证列表、数据库 distinct 值或旧测试预期。根目录工作簿可只读核对，但无需等待修改 Excel 或提供额外报告才能调整应用选项。

## 2. 当前任务与本地输入

更新：
git -C "D:\BattleMap\BattleMapenterprise-authority" pull --ff-only origin enterprise-battle-map-authority

Authority 目录下读取：
- docs/enterprise-battle-map/authority-index.md、本文件；
- 三模块当前 Canonical Authority；
- architecture/enterprise-runtime-field-options-contract-v1.md；
- 真实行业 fieldDef、options provider/optionSet、Create/Edit、客户级联及校验消费者。

此前测试修复后用户最新又报告三个迁移/DB测试残留，当前优先级按authority-index.md：用户又报告未提交改动导致复核版本不稳定，先按快照准备V1盘点和固定实际候选，迁移Schema残留按其专项处理；本行业任务仍已授权，完成状态待回执，保留已有改动，不因测试修复重复实施或撤回。前轮独立复核尚无通过回执，不据新需求标记其 PASS。如果旧审查仍在读取同一工作树，先保留该次报告并结束读取，再由实施者写入；保留旧 REVIEWED_HEAD，不让新代码混入正在核验的快照。
记录 AUTHORITY_HEAD、BASE_HEAD、工作树状态和真实作用文件，保留既有修改，不 reset/rebase/clean。更新失败记录实际版本，不声称最新。

本地固定产物：
- 计划：docs/enterprise/implementation/enterprise-industry-options-v1-plan.md
- 实施报告：docs/enterprise/implementation/enterprise-industry-options-v1-report.md
- 证据：docs/enterprise/implementation/evidence/enterprise-industry-options-v1/<BASE_HEAD>/

计划先列出准确 WRITE_SCOPE、行业来源、值/标签映射、选项与读写消费者及验证方法，再直接实施。

## 3. 通过当前契约和共享机制实现

三模块均使用现有 industry 身份，仍位于客户信息组，order=6。字段总数仍为 ISP24、电力27、大企25，其他字段和顺序不变；MOX/TOB不增加行业字段。

1. 各模块行业选项归各自 Field Contract 或明确绑定的 optionSet 管理；共享渲染器/Options Provider 消费该契约。不要在 Vue 页面再维护一份业务数组，或复制完整表单。
2. 核实实际行业选择入口，包括现有新增、编辑中的可选控件、行业筛选和客户级联使用点。适用于行业输入的候选集合严格为第1节对应模块集合，不同模块切换时不串用缓存或其他模块候选。
3. 既有客户选择可能依赖 industry，应沿用现有客户查询/级联和 customer_id 关联，不为了减少选项另建客户模型或全局硬编码客户行业。客户无匹配时使用现有空状态，不制造候选或改关联。
4. 原有编辑只读字段继续只读，本轮不把“客户信息全部只读”改成可编辑。可编辑入口按新选项工作，只读展示按已有真实值读取，不通过改显示文字掩盖历史数据。
5. 与 industry 有关的既有输入校验、API可写入口和导入校验按实际接线与新选项一致；只读/非可写投影不新增写接口或数据库列。
6. 新提交的行业值按合法选项处理；历史越界值若存在，保留数据并记录其来源与影响，不自动改写客户主数据，不把旧值偷偷补回可选列表。不要因未知历史分类自行设计迁移；确需额外业务映射时报告具体值和冲突，继续可完成部分。
7. 当前根目录 Excel 如仍含旧候选，只记录来源差异，用户已确认的新选项优先；本轮不编辑 workbook，不要求入 Git 或单独 Excel 实施报告。

只修改行业选项及其真实直接消费者，不扩展地区部、代表处、客户类别、方案、应用场景等其他选项；首页路由/金额、删除整体空间分类字段及其他既有规则保持。

## 4. 验证与测试同步

本次修改同时维护相关既有测试预期，不留下一轮才处理的已知过期断言。

必要验证：
- ISP的实际可选行业恰为ISP，电力恰为电力，大企按序为油气矿/广电/交通；不是仅验证某个选项存在。
- 用实际模块契约和生产Runtime Options/共享表单初始化验证候选；不要只测独立常量。
- 模块切换、表单重开和现有客户级联后仍不混用选项，options始终符合共享契约，无 iterable 错误。
- 现有可写入口选择合法行业后保存/重读正确；不合法新输入按现有错误机制拒绝。只读编辑入口仍只读，customer_id不被意外改写。
- 相关筛选/导入消费者按实际存在范围回归；“全部”等清除筛选状态不被写成行业值。
- 字段数量、分组/order和其他字段内容保持；历史数据不被批量改写。

测试使用隔离数据，不修改真实业务库或Excel。运行针对性选项/客户级联/相关消费者测试和当前项目必要构建门禁；扩大测试仅针对实际影响，可信且对应同一最终实现的证据可以复用。不为此新增整套测试框架。
若发现有效断言失败，修正实际实现；不能新增skip、放宽集合断言或无审查批量更新快照。

## 5. 报告与完成状态

报告记录三模块真实选项定义来源、生产调用链、code/label映射、可编辑/只读行为、受影响消费者、旧数据差异、测试命令/退出码、剩余问题和实现提交。
仅提交本轮拥有的代码、测试、计划/报告与必要证据，不push/merge。实施者只声明 IMPLEMENTED。
完成后按 `integration/enterprise-review-snapshot-preparation-v1.md` 将已授权实现及必要依赖本地提交，准确记录本任务是否包含于候选；独立检查先核对实际候选版本再检查本范围；前轮联合复核已验证且此次未受影响的结果保留其对应版本证据，受影响部分重新证明，不把旧PASS直接扩为新HEAD全量结论。

短回执：
RESULT=IMPLEMENTED/PARTIAL/BLOCKED
AUTHORITY_HEAD=
IMPLEMENTATION_HEAD=
ISP_INDUSTRY_OPTIONS=
POWER_INDUSTRY_OPTIONS=
LARGE_INDUSTRY_OPTIONS=
SHARED_RUNTIME_AND_CUSTOMER_RELATION=
READONLY_AND_EXISTING_DATA_PRESERVED=
TESTS_AND_BUILD=
REPORT_PATH=
REMAINING=
NEXT=INDEPENDENT_REVIEW/CONTINUE_IMPLEMENTATION
