# 企业已确认需求变更：测试预期统一对齐 V1

**状态：CURRENT IMPLEMENTATION / 用户报告审查已结束并阻塞，执行测试残留修复**  
**代码：D:\BattleMap\battle-map / feature/enterprise-battle-map**  
**依据：联合审查报告测试残留；用户明确 Excel 在根目录且无需进 Git或单独实施报告**

## 1. 目的与角色边界

测试是当前契约的可执行约束，需求已经明确变化时，应同步修正过期预期、fixture 与必要快照。
用户报告“预期失败”尚不能证明所有失败都是旧断言问题；云端未读取失败日志。逐项依据当前 Authority、真实实现和测试意图分类，不按错误数量批量放行。
用户已报告审查结束，实施者现在读取报告并执行本文件；核实受审工作树无并发审查写入。处理测试残留，同时按最新实物核验规则读取根目录 Excel；原独立结论保留，后续由新审查重新评估。

## 2. 输入与固定产物

先执行：
git -C "D:\BattleMap\BattleMapenterprise-authority" pull --ff-only origin enterprise-battle-map-authority

读取 Authority 的 authority-index.md、本文件、当前五模块契约、enterprise-excel-confirmed-delta-v1.md、enterprise-home-canonical-authority-v4.md 及实际失败涉及的共享机制规范。
读取本地：
docs/enterprise/reviews/enterprise-home-and-excel-delta-independent-review.md
及已有实施记录、失败日志与命令/退出码；报告位置如有变化先用 rg 恢复实际路径。独立 Excel 实施报告不是前置，文件定位与检查按 enterprise-excel-confirmed-delta-v1.md 第2节直接执行。
确认当前代码分支、BASE_HEAD、旧 REVIEWED_HEAD、AUTHORITY_HEAD、工作树状态和运行/测试环境，保留其他变更，不 reset/rebase/clean。拉取失败记录真实版本，不称为最新。

固定产物：
- 计划与失败处置矩阵：docs/enterprise/implementation/enterprise-test-expectation-alignment-v1-plan.md
- 实施报告：docs/enterprise/implementation/enterprise-test-expectation-alignment-v1-report.md
- 证据：docs/enterprise/implementation/evidence/enterprise-test-expectation-alignment-v1/<BASE_HEAD>/

已有同名报告保留历史副本，原独立审查结论不得改写。把根目录 Excel 的真实路径、hash、每表字段/名称核对证据记录在本轮报告，不补造过去的修改过程。

## 3. 先分类再修改

每个失败记录：测试路径/用例名、命令与错误、原意、旧预期、当前要求、真实结果、相关生产链路、分类、依据及处理。

| 分类 | 判定依据 | 处理 |
|---|---|---|
| STALE_EXPECTATION | 旧预期明确违反已确认新契约，且实际实现符合新要求 | 修改相关预期/fixture/快照，保持原测试意图 |
| PRODUCTION_REGRESSION | 失败验证的是仍有效要求，实际实现违反该要求 | 保留有效断言，修复真实实现；不能把预期改成错误结果 |
| TEST_OR_FIXTURE_DEFECT | 测试搭建/数据/清理或硬编码位置与已明确新机制不符 | 修正真实测试问题，维持相同验证强度 |
| ENVIRONMENT_OR_EVIDENCE_GAP | 依赖、启动、服务版本、输入或日志不足，无法得出代码结论 | 处理可解决环境问题，明确缺项；不能改业务预期来绕过 |
| OBSOLETE_REVIEW_PREREQUISITE | 仅因 workbook 未入Git或独立Excel实施报告不存在而阻塞，且未尝试实物核验 | 按最新用户澄清直接读取根目录文件；报告其证据和旧finding适用性，不能未读就宣称通过 |
| UNCLASSIFIED | 缺少足够依据 | 继续调查并保留失败，不默认归为过期 |

一次失败可能涉及多项原因，分别记录。先复用现有日志；缺失或不能复现的项再运行对应测试。
范围内的真实回归沿已确认首页/Excel要求作必要修复，在 WRITE_SCOPE 中单列生产文件；超出已有业务要求的变化记录具体问题，不借测试维护扩大功能。

## 4. 已确认应对齐的变化

1. 五模块最终总业务字段数：MOX 40、TOB 33、ISP 24、电力27、大企25。测试必须同时验证精确身份集合、连续顺序、分组及剩余字段保留，不能只改总数。
2. 仅删除“整体空间（肥肉/瘦肉/骨头）”分类字段。TOB/ISP/电力/大企旧 key 为 overallSpaceTier，MOX 从实际契约核实。整体空间金额/跳数及其他字段的断言保留。
3. 当前有效枚举、表格、Create/Edit、API 投影和最终 schema 不应要求该分类字段继续存在。涉及删除列后的字段位置、表头/合并范围和导入导出数据，依据新字段映射调整，不能全仓替换数字或列索引。
4. 大企当前 sheet 名为“大企（油气矿、广电、交通）”；旧名称仍可作为旧输入/迁移 fixture，不为改名重建内部模块 ID 或路由。
5. 首页目标允许 xx M$，实时是已下单金额真实汇总；MOX与TOB各自统计，ISP&大企包含ISP+电力+大企。空间拓展原金额字段、筛选条件和计数保持不变。
6. 全局企业场景/一级企业进入企业首页；企业首页MOX/TOB/ISP&大企分别进入MOX/TOB/ISP。路由测试验证真实入口及目标，不只改 mock 调用参数。
7. Create/Edit 仍由共享渲染器消费模块契约。合法 .map() 不等于本地完整表单构建器；测试应针对实际生产链路，不按语法字样误判。

上述数量是总业务身份数，不等于表格/新增/编辑的可见或可编辑数量。视图期望按已确认 visibility/mode 规则推导，并独立检查业务集合与规则是否正确。

## 5. 必须保留的验证能力

- 已有迁移测试所用旧 schema/旧 Excel fixture 必须保留原字段与必要数据（不要求用户当前根目录工作簿具备 Git 历史）；验证迁移前存在、迁移后删除及其他字段数据保留。不能把旧输入也改成新 schema，让迁移测试退化为空操作。
- 保留已删除字段不再被活动接口接受/投影/持久化的必要负向断言，以及金额和跳数字段保存重读的回归。
- snapshot 更新必须逐项核对 diff 与需求对应，不整仓无审查刷新。
- 不能新增 skip/only、删除有价值用例、吞掉异常、将精确相等改成宽松包含，或降低门禁以消除本轮失败。目标已经废止的旧用例可有依据地替换，报告须说明新覆盖位置。
- 不把被测函数结果当作 expected；若生产与测试引用同一 Contract，可用于验证投影一致性，但还要有独立于该输出的需求断言，能检出契约自身错删/漏删或错名。
- 共享测试 fixture/helper 只统一重复的测试搭建；保留模块独立业务语义、差异样例及失败定位。不要为这次对齐新建另一套字段 Authority。
- 已有仍有效的客户关系、Progress、Metric公式、共享渲染和数据保留测试不因这两项需求变化降低要求。

## 6. 实施与验证

形成失败矩阵及实际文件级 WRITE_SCOPE 后直接实施：先修正同根因 fixture/helper，再逐项调整真正过期的预期；有效断言失败则修正实现。
使用隔离测试库与临时文件，不修改真实业务数据或用户原始/输出 workbook。
先运行对应失败用例，随后跑实际受影响模块/共享消费者，最后运行原先暴露本批失败的完整测试命令，确认没有把失败移到别处。若完整测试已在同一最终实现执行且日志可信，可复用，避免无依据重复。
运行或核验当前最终实现的 build 和项目已有必要门禁。修正测试后的旧 PASS 不自动变成当前 PASS，必须有当前代码/测试快照对应证据。
只更新与本次已确认需求或实际根因关联的测试，其他历史失败另行如实记录，不静默忽略；必需门禁仍失败时不能声明整体通过。

报告包含每项失败的分类、Authority依据、旧/新预期、修改文件、生产修复、测试覆盖去向、命令/退出码、剩余失败和最终实现提交。
仅提交本轮拥有的代码/测试/报告，不 push/merge。实施者声明 IMPLEMENTED，不能修改原独立报告为 VERIFIED。
完成后在新独立会话对固定新 HEAD 按联合复核 V1 重新核验，重点审查失败分类和断言是否仍能检出真实错误。

短回执：
RESULT=IMPLEMENTED/PARTIAL/BLOCKED
BASE_HEAD=
IMPLEMENTATION_HEAD=
STALE_EXPECTATIONS_FIXED=
PRODUCTION_REGRESSIONS_FIXED=
TEST_FIXTURE_DEFECTS_FIXED=
UNCLASSIFIED_FAILURES=
ROOT_WORKBOOK_PATH=
ROOT_WORKBOOK_SHA256=
WORKBOOK_ACTUAL_CONTENT_CHECK=
REGRESSION_AND_FULL_SUITE=
BUILD=
REPORT_PATH=
REMAINING=
NEXT=INDEPENDENT_REVIEW/CONTINUE_REMEDIATION
