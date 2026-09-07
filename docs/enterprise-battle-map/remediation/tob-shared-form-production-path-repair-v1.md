# TOB 真实共享表单渲染路径修复 V1

**状态：CURRENT TARGETED REMEDIATION AUTHORITY**
**代码工作树：D:\BattleMap\battle-map**
**代码分支：feature/enterprise-battle-map**
**Authority 镜像：D:\BattleMap\BattleMapenterprise-authority**

## 1. 当前问题和目标

用户转述最新独立审查：TOB 仍未迁入共享表单渲染器，仍使用本地 .map() 构建器。具体 finding ID、文件、函数、Create/Edit 受影响范围和其他阻塞项，以本地最新审查报告与代码为准；本文件不虚构细节。

本轮优先完成 TOB 真实生产路径迁移，并补足此前未能识别该缺陷的验证。既有 V3 共享目标不变，不能因后续其他操作收敛而遗漏新增/编辑入口。

.map() 是合法迭代方法，本身不是架构问题。禁止的是模块本地维护完整 Form Shell / Group / Field DOM、VNode、HTML字符串或控件分发形成第二套表单结构。不得把 .map() 换成 for、v-for 或另一个 helper 名称就宣称修复，也不得建立“出现 .map() 即失败”的门禁。

## 2. 必读输入

Authority 根目录下 docs/enterprise-battle-map/：
- authority-index.md
- enterprise-contract-architecture-v5.md
- architecture/enterprise-runtime-field-options-contract-v1.md
- tob-canonical-authority-v2.md
- remediation/five-module-shared-form-renderer-convergence-v3.md
- remediation/tob-shared-form-production-path-repair-v1.md
- remediation/five-module-shared-operation-convergence-v1.md
- reviews/non-mox-modules-mox-reference-independent-review-v1.md
- reviews/non-mox-full-independent-review-rerun-v3.md

代码工作树下：
- docs/enterprise/reviews/non-mox-modules-mox-reference-independent-review.md 及证据；
- docs/enterprise/remediations/five-module-shared-form-renderer-convergence-report-v3.md；
- docs/enterprise/remediations/five-module-shared-operation-convergence-plan-v1.md；
- docs/enterprise/remediations/five-module-shared-operation-convergence-report-v1.md；
- docs/enterprise/remediations/five-module-shared-operation-convergence-findings-v1.md；
- 相关 AGENTS.md、真实 TOB 页面、共享 renderer、Contract/Projection/runtime、测试与 package.json。

## 3. 恢复代码和 finding

更新 Authority 镜像，记录 AUTHORITY_HEAD。核对代码分支、BASE_HEAD、git status 和报告 REVIEWED_HEAD；无并发写入，不 reset/rebase/clean。若代码较报告变化，核对差异并重新定位缺陷，不套用旧行号。

保留上轮未提交的审查报告/证据；这些已知只读产物不应被误判为未完成生产修改。其他来源不明的代码修改不得覆盖或代替提交。

恢复全部未关闭 findings，保留原 ID。以 TOB renderer finding 为首个修复组；报告中其他可执行 blocking findings 按共享操作链 V1 继续处理，不因只修 TOB 就声明全轮 COMPLETE。

将原始报告逐字保存到：
docs/enterprise/remediations/evidence/tob-shared-form-repair/<BASE_HEAD>/input-review.md

若报告和当前代码不一致，保存复现证据并标记 REVIEW_REQUIRED，不擅自撤销 finding。

## 4. 修改前调查和具体计划

分别从用户真实动作恢复 TOB Create 与 Edit 两条链：
route/page → action/button → dialog state → Field Contract → Projection →
Runtime Field/Options → 实际 shell → group → field/control → 最终 render tree。

至少记录入口、函数/组件和代码位置，并标明本地 .map()：
- 输入是什么；
- 输出是字段数据、共享组件绑定，还是完整本地表单节点/HTML；
- 返回结果由哪个真实页面消费；
- Create/Edit 是否共用它，是否还有替代入口/旧组件；
- 是否仅 import 共享组件但实际绕开；
- shared shell 的 body 是否仍由本地完整构建。

再查当前其他模块使用的真实共享 renderer，确定本轮要接入的唯一 shell/group/field/registry。不能仅凭 MOX 曾 PASS 推断其实现正确。

先写：
docs/enterprise/remediations/tob-shared-form-production-path-plan-v1.md

内容包括原 finding、BASE_HEAD、两条 BEFORE 路径、目标 AFTER 路径、精确 WRITE_SCOPE、删除的本地构建器与消费者、保留的薄 adapter、验证命令、验收条件及其他未关闭 findings 的处理顺序。
计划符合既有 Authority 后直接实施，不停在规划要求用户重复批准。

## 5. 实施要求

TOB Create 与 Edit 最终必须为：
TOB Field Contract → shared Projection → shared Runtime Field Model/Options →
已有唯一 shared Form Shell → shared Group Renderer → shared Field Renderer/Registry →
actual Vue render tree。

模块只保留 identity、mode、model、runtime fields、提交/结果适配和必要的最小扩展绑定。不得：
- 搬迁本地 builder 到 shared 目录而保持独立完整实现；
- 为 TOB 新增完整 template branch；
- 共享 shell 但保留本地 group/field DOM；
- 把 TOB 本地 HTML 通过 slot/字符串原样塞入共享 shell；
- 复制 MOX 字段或表单模板；
- 保留旧入口在特定条件下 fallback。

接入真实共享路径后，确认无活动消费者才删除旧本地 builder、重复 group/section schema、控件分发和过期测试假设。合法的数据 .map()、共享 renderer 内部迭代和薄组件绑定可保留。

保持 TOB Canonical Authority V2：34 个业务字段为总体基线，各 Table/Create/Edit 视图按 Contract visibility/mode 派生 expected keys。不能强行在每个表单显示全部34字段。
保持客户信息、业务格局、作战情况三组；字段顺序、control/editor、只读规则、动态 options、customer_id、Progress特殊入口和提交生命周期不回退。
不改变业务字段集合、Metric/Heatmap口径、Customer/Progress数据模型、Excel V0.2或首页，不无证据重写其他四模块。

## 6. 必须补上的验证

先建立或修正有判别力的 TOB 回归测试，再修改生产实现；证明测试针对旧本地 builder 会失败，对修复后的共享链通过。可使用修复前快照/隔离临时实验，不覆盖用户工作树。已有可信测试可直接复用。

测试必须从真实 TOB 页面/路由和实际 Create/Edit action 出发，挂载真实共享 shell/group/field renderer；只 mock 外部系统边界，不 mock/stub 掉待证明的 renderer。
同时证明：
- 两个实际表单都经过同一现有共享 renderer，具有正确字段/分组和行为；
- 新增、编辑、取消、关闭后重开、提交后刷新等实际生命周期正常；
- select options、customer_id、Edit只读字段、Progress editor 等既有能力保留；
- 所有活动 TOB 表单入口已迁移，旧 builder 无消费者；
- 测试不是直接调用一个生产页面不用的 helper。

检查前次为什么漏检：未覆盖真实入口、只验 import/props、mock 掉 renderer、扫描范围漏项、错误解释“共享”等。结论必须有代码/测试证据，不预设具体原因。修正对应门禁，不能只补报告。

静态/架构门禁与运行测试互相补充：扫描真实 TOB 生产入口及其传递调用，核实模块本地完整表单构建器为0；输出分类证据，不按 .map() 文本数量判定。

先跑 TOB Create/Edit、共享 renderer 和直接相关回归；再跑五模块 Create/Edit、共享操作链相关回归、enterprise suite、full Vitest、build、已有 lint/typecheck。重叠测试可一次运行提供证据，不重复跑无新增风险的相同套件。
测试数据库使用隔离副本，日志保存实际命令、退出码与结果；未运行记 NOT_RUN，不降低断言或删除测试制造通过。

## 7. 产物与提交

计划：
docs/enterprise/remediations/tob-shared-form-production-path-plan-v1.md
实施报告：
docs/enterprise/remediations/tob-shared-form-production-path-report-v1.md
证据：
docs/enterprise/remediations/evidence/tob-shared-form-repair/<BASE_HEAD>/
同时更新：
docs/enterprise/remediations/five-module-shared-operation-convergence-findings-v1.md

报告记录两条 BEFORE/AFTER 路径、共享组件身份、删除路径、保留的合法 .map() 分类、漏检根因及门禁补强、全部验证与剩余 findings。
既有同名产物属于不同 BASE_HEAD 时，先逐字归档到当前证据目录 prior-artifacts/，不覆盖历史证据。

不改写独立审查的历史 FAIL/PASS。更新当前实施记录时保留先前声明和其被新 finding 推翻的事实，附 superseded/corrected 说明，不能抹去矛盾。

核对 WRITE_SCOPE，只 stage 本轮拥有的修改。本地提交代码、测试与同步文档，不 push/merge。
按共享操作链 V1 规则记录 IMPLEMENTATION_HEAD 和真实 FINAL_HEAD，报告补写 SHA 的后续提交只能含文档/证据。
finding 状态只能由实施者标为 IMPLEMENTED_PENDING_REVIEW 等，不自行声明 CLOSED/VERIFIED。

## 8. 验收与下一步

以下必须同时成立：
TOB_CREATE_USES_SHARED_RENDERER=PASS
TOB_EDIT_USES_SHARED_RENDERER=PASS
TOB_LOCAL_FULL_FORM_BUILDERS=0
OLD_TOB_FORM_CONSUMERS=0
TOB_FIELD_GROUP_CONFORMANCE=PASS
PRODUCTION_PATH_TESTS=PASS
REGRESSION_GATE_DETECTS_LOCAL_BUILDER=PASS
FIVE_MODULE_CREATE_EDIT_REGRESSION=PASS
SHARED_OPERATION_REGRESSION=PASS
FULL_TESTS=PASS
BUILD=PASS

任何 PASS/0 必须引用实际代码和测试/扫描证据。若仅 TOB 修完而其他报告 blocker 未解决，整体 RESULT=PARTIAL，列出剩余项；继续完成其他可执行组。
本轮实施完成后对新 HEAD 完整重跑 Review V1 + Full Rerun V3（含共享操作链），并读取本 TOB 修复报告检查上述门禁与测试漏检修复。禁止直接人工验收。

最终简短回执：
RESULT=COMPLETE/PARTIAL/BLOCKED
STATUS=IMPLEMENTED
BASE_HEAD=
IMPLEMENTATION_HEAD=
FINAL_HEAD=
TOB_CREATE_USES_SHARED_RENDERER=PASS/FAIL/NOT_RUN
TOB_EDIT_USES_SHARED_RENDERER=PASS/FAIL/NOT_RUN
TOB_LOCAL_FULL_FORM_BUILDERS=
OLD_TOB_FORM_CONSUMERS=
REGRESSION_GATE_DETECTS_LOCAL_BUILDER=PASS/FAIL/NOT_RUN
FIVE_MODULE_CREATE_EDIT_REGRESSION=PASS/FAIL/NOT_RUN
SHARED_OPERATION_REGRESSION=PASS/FAIL/NOT_RUN
FULL_TESTS=PASS/FAIL/NOT_RUN
BUILD=PASS/FAIL/NOT_RUN
FINDINGS_IMPLEMENTED=x/N
REMAINING_FINDINGS=NONE或ID
REPORT_PATH=
NEXT=FULL_INDEPENDENT_REVIEW_RERUN_V3/CONTINUE_REMEDIATION/AUTHORITY_DECISION

用户只需复制短回执，不要求上传本地报告或代码。
