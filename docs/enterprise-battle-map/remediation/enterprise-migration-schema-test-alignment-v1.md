# 企业历史迁移与 Schema 测试定向对齐 V1

**状态：CURRENT / 用户报告剩余测试失败，待本地定向修复**  
**代码：D:\BattleMap\battle-map / feature/enterprise-battle-map**  
**范围：指定迁移/数据库测试及直接相关测试 helper、fixture、预期和本轮报告；不修改 SQL 或生产迁移接线**

## 1. 当前问题与不可变边界

用户报告此前测试修复完成，但历史 SQL 仍包含已删除的“整体空间（肥肉/瘦肉/骨头）”分类字段，以下测试仍失败。用户明确：这些是已执行的历史迁移，不应修改；本轮更新相关测试。
云端未读取本地代码/失败日志，以下是处置规范，不是已确认根因或已通过结论。

| 用户指出的测试 | 本地必须核对的重点 |
|---|---|
| isp-migration.test.js | 实际运行哪个迁移阶段；期望是否错误使用最新 schema 对比历史阶段 |
| kox-migration-chhain.test.js（用户原拼写） | 用 rg 定位真实文件名，不据拼写新建/重命名测试；核实所谓完整链是否遗漏已注册后续迁移 |
| power-large-db.test.js | 实际库版本、物理列身份与旧硬编码列数；不得拿业务字段数直接替代数据库列数 |

不修改、删除、重排、重编号已执行 SQL，不更改其校验和机制或迁移账本以绕过校验。历史字段字样本身不是活动残留。
本轮也不新增 SQL、修改生产 migration runner/登记/初始化代码；若发现需要生产修复，保留有效失败，记录证据及建议后续范围，不借更新测试悄悄改变生产结构。
行业选项 V1仍已授权，完成状态未收到回执；保留其已有修改与报告，不在本轮重复实施或撤回。

## 2. 输入、真实路径与 WRITE_SCOPE

先更新 Authority：

git -C "D:\BattleMap\BattleMapenterprise-authority" pull --ff-only origin enterprise-battle-map-authority

读取 Authority：
- authority-index.md、本文件；
- remediation/enterprise-confirmed-delta-test-expectation-alignment-v1.md；
- enterprise-excel-confirmed-delta-v1.md、enterprise-contract-architecture-v5.md；
- 实际受影响模块当前契约及联合独立复核 V1 第8节。

在代码工作树读取最近联合审查报告、测试对齐实施报告、失败日志、package scripts、真实测试文件、SQL 历史、生产 runner/登记和当前 DB 映射。先用 rg --files 与 rg 恢复真实路径，不假定用户测试名完全准确。Excel不属于本次修改范围；不要求入Git或另补Excel实施报告。

记录 AUTHORITY_HEAD、BASE_HEAD、实际代码分支、工作树状态与旧 REVIEWED_HEAD；保护用户/其他任务改动，不 reset/rebase/clean，不切换到不相关的默认分支。同一工作树只允许一个写者，受审快照读取结束后再修改。
Authority 更新失败记录真实本地 SHA，不能声称最新；因权限/受保护流程受阻时停止相关操作并报告。

固定本地产物：
- docs/enterprise/implementation/enterprise-migration-schema-test-alignment-v1-plan.md
- docs/enterprise/implementation/enterprise-migration-schema-test-alignment-v1-report.md
- docs/enterprise/implementation/evidence/enterprise-migration-schema-test-alignment-v1/<BASE_HEAD>/

计划可简短，但先列具体测试/helper/fixture 文件级 WRITE_SCOPE，再实施。矩阵逐项包含：真实测试路径/用例、旧失败、数据库起始版本、迁移截止版本、预期与实际差异、分类、修复依据。已有报告保留历史，不改写原独立结论。

## 3. 按迁移阶段建立正确预期

### 3.1 历史单步或前缀迁移

测试明确只执行到旧版本 Vn 时，应验证 Vn 的历史结构。该阶段仍有旧分类列可能完全正确，不能要求旧 SQL 直接产生最终新结构。
保留该版本的独立 schema 预期、旧字段和样例数据，清晰标注版本/测试目的；不能让“历史预期”无版本地成为当前业务契约。
原来承诺验证完整升级的用例不得改名为“历史测试”后删除最终升级覆盖。

### 3.2 完整生产迁移链

真正的全链测试必须覆盖当前生产实际登记并执行的全部迁移，优先调用实际生产 runner；核对版本顺序、迁移账本和最新目标。不得只更新测试中一份仍然截断的手写清单，却继续称“完整链”。

先区分：
1. 生产链已有正确后续删除迁移，测试只跑旧 SQL/旧前缀：修正测试搭建，接入现有完整生产路径，再验证最终结构。
2. 真实生产完整链最终仍残留分类列：这是 PRODUCTION_MIGRATION_GAP（归属真实生产回归），不是可通过接受旧列解决的过期断言。本轮报告缺失/未登记/接线等实际证据，保持终态门禁失败，提出后续增量迁移或生产接线修复建议；不修改历史 SQL，也不在本轮越界实现生产修复。
3. 日志或运行环境不足以判断：标记证据/环境缺口，继续可完成检查，不能推定属于第1种。

最终结构目标不变：被删除分类字段不属于当前有效持久化结构；overallSpaceHops、overallSpaceMusd 及其他未删除字段保留。精确 DB 列名按本地 canonical→持久化映射核实，MOX旧分类 key不得猜测。

至少保留两条有实质覆盖的路径：空库经真实生产初始化/迁移达到最新版；包含旧分类和非零剩余字段样例的历史库经真实升级达到最新版。比较二者最终相关 schema，验证其他数据、客户关系及金额/跳数未损坏。
不得用测试专属 DROP COLUMN、人工改库或伪造迁移账本替生产迁移完成删除；不得把旧 fixture 预先改成最新结构使升级成为空操作。

### 3.3 物理列数与业务字段数

MOX40、TOB33、ISP24、电力27、大企25 是业务身份总数，不是 SQLite 物理列数。
逐表区分实际持久化字段、customer_id等关联列、技术列与仅查询投影/计算字段。不要将全部 canonical 字段直接当成数据库列。

用经迁移版本和当前持久化契约核实的独立预期列名集合做精确比较，并保留已有类型、空值、默认值、主键、外键、索引等适用断言。列顺序只有现有机制确实依赖时才作为额外要求，不让集合比较掩盖已有顺序契约。
若仍保留列数断言，预期数量可取该独立预期集合长度；不能取实际 PRAGMA 输出长度再与自己比较，不能只随实际错误结果改数字，不能改为“至少若干列”或部分包含。
历史 DB 测试按相应历史版本集合，当前 DB 测试按最终物理结构，两者分开命名并显示版本。

## 4. 修复与验证门禁

- 分类沿用通用测试对齐 V1；将版本错配、测试链截断、硬编码列数分别定位，不笼统称所有失败都是预期失败。
- 历史 SQL、历史 fixture、一次性迁移中出现旧字段允许存在；检查活动残留时按具体路径/用途区分，不全局豁免 SQL，也不全仓删除旧字段字样。
- 不能新增 skip/only、吞异常、删终态覆盖、宽松替换精确集合或无审查刷新全部快照；不从被测输出生成 expected。
- 在隔离临时数据库运行测试，绝不操作真实业务库、修改根目录工作簿或上传业务数据。
- 执行前后记录受涉及的历史 SQL 清单/差异或hash，证明本轮未改动；既有脏改动单独标注，不能替别人回滚。
- 先运行三个真实失败文件及必要用例，再运行直接受影响迁移/DB测试，最后运行原先暴露这些失败的完整测试命令，记录可复制命令、退出码和日志。
- 核验同一最终实现的 build/既有必要门禁。可信且覆盖同一最终实现的证据可复用；不得拿修改前的失败/通过记录代替当前测试证据。不新增无关全仓重构或测试框架。
- 无法闭环的生产迁移问题、其他失败、未运行项各自记录。已知必需门禁失败不得声明整体通过。

只提交本轮拥有的测试/helper/fixture与报告，不 push/merge；不提交 workbook/业务数据。实施者只声明 IMPLEMENTED/PARTIAL/BLOCKED，不自行 VERIFIED。
后续固定新 HEAD，按联合复核 V1 第8节独立检查断言强度、迁移历史不变与真实终态；旧首页/Excel未受影响且有效的证据可复用，不因这次测试修复重做已完成业务。

## 5. 短回执

RESULT=IMPLEMENTED/PARTIAL/BLOCKED
AUTHORITY_HEAD=
BASE_HEAD=
IMPLEMENTATION_HEAD=
ACTUAL_TEST_PATHS=
HISTORICAL_SQL_UNCHANGED=
HISTORICAL_STAGE_EXPECTATIONS=
FULL_PRODUCTION_CHAIN_TERMINAL_SCHEMA=
EXACT_PHYSICAL_COLUMN_SETS=
UPGRADE_DATA_PRESERVATION=
TARGETED_AND_ORIGINAL_FULL_TESTS=
BUILD_EVIDENCE=
PRODUCTION_MIGRATION_GAPS=
REPORT_PATH=
REMAINING=
NEXT=INDEPENDENT_REVIEW/TARGETED_PRODUCTION_FIX_REQUIRED/CONTINUE_TEST_REMEDIATION
