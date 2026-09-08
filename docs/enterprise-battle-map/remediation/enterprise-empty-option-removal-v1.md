# 企业下拉选项“（空）”修正 V1

**状态：CURRENT / 已授权待本地实施**
**代码：D:\BattleMap\battle-map / feature/enterprise-battle-map**

## 1. 最终需求

检查MOX、TOB、ISP、电力、大企所有字段选择入口，只处理实际显示字面文字“（空）”的选项。核实确有同义半角“(空)”时同样处理。
删除该可选项及其生成来源；受影响控件未选择时显示灰色、不可选择的“请选择”占位。已有合法值正常回显，不默认选中第一项，“请选择”不写入业务数据。

**本次不是空值清理。** null、undefined、空字符串、数据库NULL和原未填写状态继续按原契约处理。不得按value为空过滤候选，不改变必填/可空规则，不清洗历史数据。
用户确认MOX客户类别当前没有该选项：检查记录未命中，保持原实现及合法空值测试。其他未命中控件也不改。

仅识别实际option显示标签，不能模糊删除包含“空”字的正常名称。“全部”“无”“其他”、正常选项与只读空值展示保持原语义。

## 2. 输入与范围

先更新：
git -C "D:\BattleMap\BattleMapenterprise-authority" pull --ff-only origin enterprise-battle-map-authority

读取该目录的docs/enterprise-battle-map下：
- authority-index.md、本文件；
- architecture/enterprise-runtime-field-options-contract-v1.md；
- 实际命中字段的模块契约；
- integration/enterprise-review-snapshot-preparation-v1.md。

读取代码根适用AGENTS.md和最近实施/审查报告，记录AUTHORITY_HEAD、BASE_HEAD、分支及未提交改动归属。
用rg和实际页面定位“（空）”选项：模块、field key、入口、显示label、底层value/类型、静态/动态来源、共享调用链。检查新增/编辑、实际表格编辑、字段筛选等选择入口；不预设每个模块都存在问题。
先写简短命中/未命中清单和精确文件级WRITE_SCOPE，再实施。

允许修改实际生成该文字选项的optionSet、provider、共享控件/适配器及直接相关测试。优先修真实来源，不能逐页面复制清理逻辑或新建本地完整表单。
不改SQL/迁移、Excel、真实业务库及无关枚举/字段。行业选项和既有迁移测试任务保持其实际进度，不重做、不自动标完成。

## 3. 实施规则

1. 区分显示label与底层value。即使某项label为“（空）”、value为空，移除该UI项也不代表删除字段空值合法性。
2. 不用filter(Boolean)，不按value真假值/null/空串全局过滤。保留合法0、false及其他真实选项的类型、身份、顺序。
3. 核对静态配置、动态候选和控件注入，避免级联、异步刷新或表单重开重新补入“（空）”。若合法业务值被错误formatter显示为该文字，按现有契约修正标签映射，不误删合法业务值。
4. 使用现有placeholder机制显示“请选择”；原生select如需disabled显示option，仅作不可选择提示。清除保持原无值语义，已有值不被重置。
5. 保持客户级联/customer_id、编辑只读、nullable/required及Runtime错误边界。不能把API失败或undefined options吞成成功空列表。
6. 若历史记录确实保存字符串“（空）”，记录其影响，不批量改写；编辑其他字段不能隐式清空它，也不为历史值重新添加可选项。需要额外数据处理时报告具体问题。
7. 本轮无并发写入/审查。旧候选保留，本次提交后固定新候选，不把未提交修复交给旧HEAD核验。

## 4. 验证

- 所有实际命中入口的菜单不再提供“（空）”；五模块检查清单包含真实命中及未命中结果。
- 受影响控件无值显示不可选“请选择”，已有值正常回显、不默认首项、不把占位文字保存。
- 真正空值、原必填/可空行为及其他正常选项保留；MOX客户类别未命中时不改，不删除其合法空值测试。
- 真实共享生产路径经级联、刷新、模块切换和重开后不重新注入；客户关系及错误边界无回归。
- 只调整要求渲染字面“（空）”的过期测试预期；保留空值fixture、精确候选集合，不skip或放宽断言。
- 执行实际受影响测试及必要构建门禁，真实打开命中下拉核验选项/placeholder。可信且对应同一最终实现的证据可复用，未执行项如实记录；不以搜索或helper测试代替UI证据。

## 5. 本地产物与交接

固定路径：
- docs/enterprise/implementation/enterprise-empty-option-removal-v1-plan.md
- docs/enterprise/implementation/enterprise-empty-option-removal-v1-report.md
- docs/enterprise/implementation/evidence/enterprise-empty-option-removal-v1/<BASE_HEAD>/

报告记录命中/未命中、来源与修改、测试/界面证据、命令/退出码、剩余问题。
按快照准备V1精确本地提交代码/测试和必要报告，保留无关改动，不全量add，不reset/clean，不push；本地commit无需网络。
返回准确REVIEW_CANDIDATE_HEAD和REVIEW_WORKTREE，供新会话按联合复核第9/10节核验。实施者仅声明IMPLEMENTED/PARTIAL/BLOCKED，不自行VERIFIED。

回执：
RESULT=
IMPLEMENTATION_HEAD=
REVIEW_CANDIDATE_HEAD=
REVIEW_WORKTREE=
MATCHED_OPTIONS_REMOVED=
UNMATCHED_CONTROLS_PRESERVED=
PLACEHOLDER_AND_REAL_NULL_VALUES=
TESTS_BUILD_AND_UI_EVIDENCE=
REPORT_PATH=
REMAINING=
