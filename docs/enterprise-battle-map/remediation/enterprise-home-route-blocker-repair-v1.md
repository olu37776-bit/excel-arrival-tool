# 首页 V4 跳转阻塞定向修复 V1

**状态：CURRENT / USER_REPORTED_BLOCKER / 待本地修复**  
**完整业务基线：enterprise-home-canonical-authority-v4.md**

## 1. 已知事实与边界

用户报告：首页独立审查发现点击未跳转，与人工检查一致，详情已写入本地文档。
云端未读取本地报告或运行代码，因此不预设 finding ID、失败入口数量、根因或其余检查已通过。执行者必须先读最新报告，恢复准确事实。
首页尚未完成验收。先处理本轮首页阻塞；Excel 两项变更仍获授权，保留已完成工作，不重置、不混入首页修复提交，同一工作树只允许一个写入者。

## 2. 固定输入与产物

Authority：D:\BattleMap\BattleMapenterprise-authority
更新：
git -C "D:\BattleMap\BattleMapenterprise-authority" pull --ff-only origin enterprise-battle-map-authority

代码：D:\BattleMap\battle-map
分支：feature/enterprise-battle-map

必读：
- Authority 的 authority-index.md、本文件、enterprise-home-canonical-authority-v4.md。
- D:\BattleMap\battle-map\docs\enterprise\reviews\enterprise-home-v4-independent-review.md 及其证据。
- docs/enterprise/implementation/enterprise-home-polish-v4-plan.md 与 enterprise-home-polish-v4-report.md。
- 本地报告实际引用的文件、路由、组件与测试。

若报告改名，先在本地 docs/enterprise/reviews 中用 rg 定位并核对报告 HEAD/时间/内容，记录实际路径；不要求用户上传。找不到时明确报告缺失，仍可复现用户所述点击问题，不伪造审查明细。
记录 AUTHORITY_HEAD、BASE_HEAD、旧 REVIEWED_HEAD、工作树及当前运行服务对应的 checkout/代码版本。拉取失败不能称为最新；禁止 reset/rebase/clean 或覆盖 Excel 等既有修改。

本轮产物固定在代码仓库：
- 计划：docs/enterprise/implementation/enterprise-home-route-repair-v1-plan.md
- 实施报告：docs/enterprise/implementation/enterprise-home-route-repair-v1-report.md
- 证据：docs/enterprise/implementation/evidence/enterprise-home-route-repair-v1/<BASE_HEAD>/
已有同名报告先保存历史副本。

## 3. 从报告和真实点击定位

提取报告全部 finding、级别、复现与证据，建立 finding → 原因 → 修改 → 回归映射。优先修复跳转阻塞；报告中其他属于 V4 的明确阻塞也应闭环，不因为用户只摘要了一项便忽略。不扩展未授权业务需求。

根据 V4 核查全部入口：

| 入口 | 应到达页面 |
|---|---|
| 全局首页“企业场景”卡片 | 企业首页 |
| 一级“企业”菜单 | 企业首页 |
| 企业首页 MOX 卡片 | MOX 子页 |
| 企业首页 TOB 卡片 | TOB 子页 |
| 企业首页 ISP&大企卡片 | ISP 子页 |

先在真实页面复现报告失败入口，再追踪：
页面实际渲染组件 → 卡片主体/数字实际 DOM → 事件或链接 → 项目导航机制 → router registry/guard/redirect → 目标页面实际渲染。

核实点击绑定、组件事件传递、遮挡与 pointer-events、事件拦截、路由目标、重定向/守卫及懒加载。以上只是排查方向，不是预判根因。
尤其确认修改的是当前运行首页所使用的组件，不能只修改未使用的 helper、旧页面或另一份卡片定义。运行服务与已修改代码不一致时，先纠正启动目录/服务版本并复现，不以清缓存代替已确认代码缺陷的修复。

## 4. 修复范围

在计划列出真实文件级 WRITE_SCOPE 后直接实施。
复用既有 router/route registry 和共享卡片交互机制；必要时修复真正断开的事件转发或配置。不要猜 URL、创建重复企业首页、增加全局 DOM 点击补丁或吞掉导航错误。
卡片主体与目标/实时数字区域到达同一约定目标；键盘使用符合现有元素语义的激活方式。无需为企业专项或空间拓展新增跳转。
保持已有布局、样式、金额/空间公式、权限和其他场景导航。涉及共享组件时回归其实际受影响消费者。
本任务不重新修改 Excel、业务字段、数据库或已正确的表单机制。若报告另有必要但超出 V4 的变更，说明具体范围和依据，继续已授权修复。

## 5. 验证必须到达真实页面

1. 保存修复前复现证据；针对实际缺陷补充可在修复前失败、修复后通过的回归。
2. 使用实际页面组件和真实项目路由配置验证点击；只断言 mock router.push 被调用、路由字符串存在或孤立 helper 返回值正确，不能证明问题已解决。
3. 本地启动真实应用，以浏览器普通点击完成失败入口以及上表各项，核对 URL/route identity 和目标页面特征。卡片主体、数字区域均须验证，不能用强制点击绕过遮挡，也不能手动调用 handler/router 代替点击。
4. 核对键盘激活、浏览器返回、共享卡片其他消费者和控制台导航错误。记录启动命令、服务地址、代码版本、操作和截图/执行日志。
5. 运行相关路由/组件测试、受影响回归与项目构建；其他完整测试按变更影响和现有可信证据决定。测试证据对应修复后实现，旧实现的通过记录不能证明新代码。
6. 无浏览器能力则明确 REAL_BROWSER_NAVIGATION=NOT_RUN，保存可完成的证据并列出剩余检查；不能宣称真实跳转已验证或验收完成。

## 6. 报告与后续

报告包含：本地审查来源、全部 findings 的处置、根因、实际生产链路、精确路由映射、WRITE_SCOPE、修复前后证据、测试/构建、代码提交和未完成项。
原独立审查报告保持原结论与旧 HEAD；实施者只声明 IMPLEMENTED，不自行改为 VERIFIED。
仅提交本轮拥有的变更，不 push/merge；不能把其他任务未提交修改混入。
完成后对固定新 HEAD 做独立复核，沿用首页 V4 第17节，覆盖原 findings 和本次受影响范围；保留旧报告历史。独立复核后再由用户确认真实页面跳转。

短回执：
RESULT=IMPLEMENTED/PARTIAL/BLOCKED
AUTHORITY_HEAD=
BASE_HEAD=
IMPLEMENTATION_HEAD=
SOURCE_REVIEW_PATH=
FINDINGS_FIXED=
ROOT_CAUSE=
GLOBAL_ENTERPRISE_SCENE_ROUTE=PASS/FAIL/NOT_RUN
MODULE_CARD_ROUTES=PASS/FAIL/NOT_RUN
REAL_BROWSER_NAVIGATION=PASS/FAIL/NOT_RUN
REGRESSION_AND_BUILD=
REPORT_PATH=
REMAINING=
NEXT=INDEPENDENT_REVIEW/CONTINUE_REPAIR
