# MOX 人工审查后定向修复计划 V2

**状态：CURRENT IMPLEMENTATION PLAN**  
**取代：`mox-post-manual-review-remediation-v1.md`**  
**唯一业务 Authority：`mox-canonical-authority-v4.md`**  
**共享架构 Authority：`enterprise-contract-architecture-v3.md`**  
**本地实施分支：`feature/enterprise-battle-map`**  
**下一门禁：MOX V4 独立审查**

---

## 1. 当前人工审查结论

当前 MOX 不能进入独立审查，原因包括：

1. Contract/Schema 错放在 `src/enterprise`，最终应位于 `src/config/enterprise`；
2. 企业模块仍有重复配置、过期测试和死代码；
3. 点击 MOX“新增”立即报“获取客户数据失败”，导致新增界面当前无法人工查看；
4. 编辑界面仍未按目标 Contract 完成字段、Section、控件和顺序对齐；
5. 新增界面即使当前不可见，也必须在错误修复后完整对齐，不能只修到“可以打开”；
6. 客户类别当前不可选，目标为可选：空值、核心NA、战略NA；
7. 新增与编辑应使用三个同级 Section：客户信息、业务格局、作战情况；
8. 作战进展未继承原有特殊交互；当前 TOB 中仍正确工作的进展实现是直接参考；
9. V34、数据库最终列、旧字段清理及 `database.js` 注册仍需重新验证；
10. 当前实现尚不能作为其他模块参考模板。

本计划只处理 MOX 及企业模块直接依赖，不实施其他模块，不建设企业首页，不修改 Heatmap 业务规则。

---

## 2. 核心门禁：新增与编辑必须成对完成

新增和编辑不是两个可分开的后续任务，而是同一 Field Contract 的两个 Projection。

必须满足：

```text
MOX_FIELD_CONTRACT
├─ create projection
└─ edit projection
```

实施规则：

1. 先修复“获取客户数据失败”，使新增弹窗能够正常初始化；
2. 错误修复后，必须继续完成新增的全字段、Section、顺序、控件、枚举、保存和回填；
3. 同一轮同步完成编辑的全字段、Section、顺序、控件、权限、保存和回填；
4. 不允许只修改编辑，因为当前用户暂时只能看到编辑；
5. 不允许只让新增“能够打开”就宣布完成；
6. 新增与编辑必须由同一 Field Contract 派生，不得各自维护完整字段数组；
7. 新增和编辑中的同一字段必须使用同一 canonical key、label、section、control、API/DB映射；
8. 唯一允许的差异是明确的权限差异，例如客户字段在编辑中只读，但客户类别是本次明确例外；
9. `CREATE_ALIGNMENT`和`EDIT_ALIGNMENT`任一失败，本次 remediation 均不得标记 COMPLETE。

当前新建无法人工查看，不代表新建字段结构可以免审。必须通过自动测试和后续用户人工验收共同确认。

---

## 3. WRITE_SCOPE

### 3.1 允许修改

- `src/enterprise` 下当前 MOX Contract/Schema 配置；
- `src/config` 下企业/MOX旧字段和 Metric 配置；
- 目标 `src/config/enterprise` 契约目录；
- MOX Field Contract、Metric Contract、Projection、Validator；
- MOX 表格；
- MOX 新增弹窗全部字段、Section、控件、客户初始化、保存和回填；
- MOX 编辑弹窗全部字段、Section、控件、权限、保存和回填；
- MOX 客户数据请求、客户 API 及其 `database.js` 直接查询链；
- 客户类别客户主数据更新链；
- MOX 作战进展特殊 editor/handler 接入；
- MOX/企业契约直接相关测试；
- 企业模块直接相关重复配置、过期测试和死代码；
- V34及其 `database.js`注册、CRUD、映射和Validation（发现未完成时）；
- 本地状态与验证证据文档。

### 3.2 禁止修改

- TOB、ISP、电力、大企字段 Contract 或业务页面；
- 企业首页汇总；
- Heatmap 真实业务规则；
- 非企业模块代码、测试和死代码；
- 与 MOX 无关的数据库表；
- 已确认的 41 字段、顺序、枚举和 9 项统计公式；
- 其他模块页面样式。

---

## 4. Authority 与字段封闭集合

必须读取：

1. `enterprise-contract-architecture-v3.md`；
2. `mox-canonical-authority-v4.md`；
3. 本计划；
4. 本地“企业作战地图基表”的 MOX Sheet；
5. 当前 MOX Contract、UI、API、`database.js`、V34、SQLite Schema和测试；
6. 当前 TOB 作战进展实现，仅作为进展交互参考。

MOX 最终业务字段就是 V4 Authority 中的 41 项。除记录主键和明确必要技术列外：

- Authority 中存在：保留或建设；
- Authority 中不存在：从表格、新增、编辑、API活动契约、`database.js`活动映射和最终数据库 Schema 删除；
- 不因旧代码、旧数据库、旧测试或旧文档中存在某字段而保留；
- 不允许本地 Agent 自行增加第 42 个业务字段。

---

## 5. Contract 目录与单一 Authority

最终活动契约位于：

```text
src/config/enterprise/
```

必须完成：

1. 将 `src/enterprise` 中的活动 Field/Metric Contract、Projection、Validator 配置迁移到 `src/config/enterprise`；
2. 更新所有真实 import/require；
3. 删除旧 `mox-field-schema.js` 第二 Authority；
4. 删除 `src/config` 根目录或其他位置重复的 MOX字段/Metric配置；
5. 不保留 re-export、fallback 或新旧路径双轨；
6. 页面、API、数据库代码仍保留在项目现有职责目录，不因 Contract 迁移被整体移动。

删除前先建立 import/reference 清单；完成后活动 MOX Field Authority 和 Metric Authority 各只能有一份。

---

## 6. 新增与编辑的三个同级 Section

新增和编辑都必须只显示：

```text
客户信息 ｜ 业务格局 ｜ 作战情况
```

要求：

- 三个 Section 同级；
- 删除旧“客户信息 / 业务信息”二分结构；
- 不渲染“无线格局 / 微波格局”两个顶层 Section；
- 无线与微波字段都进入“业务格局”，并按 Field Contract order 先无线后微波；
- 作战进展属于“作战情况”且固定最后；
- 表格不显示 Section 标题，按 V4 Authority 1—41 展开；
- 新增和编辑不得在组件中另写完整字段顺序。

自动测试必须分别断言：

- `CREATE_SECTIONS = 客户信息/业务格局/作战情况`；
- `EDIT_SECTIONS = 客户信息/业务格局/作战情况`；
- 两者字段顺序均来自同一 Contract。

---

## 7. 新增弹窗完整修复

### 7.1 修复初始化错误

必须追踪真实链路：

```text
点击新增
→ 弹窗初始化
→ 客户数据请求
→ API route
→ database.js客户查询
→ 客户表
```

检查 URL、method、参数、route注册、响应结构、客户表字段、SQL和错误包装。

禁止仅隐藏“获取客户数据失败”。修复后 API 失败仍需返回可诊断信息。

### 7.2 错误修复后的完整新增对齐

弹窗能够打开后，还必须继续验证并修复：

- 41 项 Authority 中所有可新增字段完整；
- 三个 Section 正确；
- 字段顺序来自 Contract；
- 目标外字段为 0；
- 固定枚举控件正确；
- 数字、金额、百分比控件与格式正确；
- `customer_id` 自动匹配，不可手填；
- 地区部、代表处等当前客户联动保留；
- 同名客户不能取第一条；
- 客户类别可选择空值、核心NA、战略NA；
- 作战进展使用特殊 editor；
- 一线接口人存在；
- 保存后通过 API/DB 重新读取全部字段正确。

目标：

```text
EXTRA_CREATE_FIELDS=0
CREATE_ALIGNMENT=PASS
CREATE_PERSISTENCE=PASS
```

---

## 8. 编辑弹窗完整修复

编辑必须使用与新增相同的 Field Contract、三个 Section 和字段顺序。

客户信息规则：

- 地区部、代表处、国家、客户ID、客户名称保持只读；
- 客户类别是明确例外，在编辑中允许选择空值、核心NA、战略NA；
- 修改客户类别写入客户主数据表，不在 MOX 表创建重复列；
- 编辑其他业务字段不得改变 `customer_id`。

还必须保证：

- 41 项中的所有目标编辑字段完整；
- 目标外字段为 0；
- 枚举与新增一致；
- 作战进展使用特殊 editor；
- 一线接口人保存和回填正确；
- 保存后重新打开字段值正确。

目标：

```text
EXTRA_EDIT_FIELDS=0
EDIT_ALIGNMENT=PASS
EDIT_PERSISTENCE=PASS
```

---

## 9. 客户类别

MOX 客户类别固定合法状态：

```text
空值
核心NA
战略NA
```

要求：

- 新增可选；
- 编辑可选；
- 空值为合法状态；
- 前端、API、客户表字段和值域一致；
- 保存到客户主数据 Authority；
- 不在 MOX 业务表增加重复客户类别列；
- 不改变 `customer_id`；
- 增加新增、编辑、空值、非法值和保存回填测试。

---

## 10. 作战进展

当前 TOB 页面中仍正确工作的进展交互是直接参考。

MOX 必须：

- 用户可见名称为“作战进展”；
- 通过 `editorId`或现有等价机制接入有效特殊实现；
- 支持新增、追加、编辑、保存和回填；
- 不退化为普通 input/textarea；
- 不继续使用 `latest_progress`作为活动 canonical 字段；
- 不复制第二套不同进展组件。

如果抽取共享进展组件，只允许修改 MOX 和 TOB 的直接引用，并必须运行 TOB 回归测试。

---

## 11. V34 与数据库最终态

必须复核而非假定已完成：

- V34 SQL语法正确；
- V34在`database.js`实际Migration链中注册；
- Migration事务、失败回滚和`_migrations`登记正确；
- 重复启动不重复执行；
- 新建库与升级库MOX最终Schema一致；
- 41字段持久化映射完整；
- Authority外旧字段和`database.js`活动引用为0；
- 不保留双写、fallback或旧API字段。

已知应删除字段至少包括：

```text
dpm
remark
service_interface
entered_amount
space_26
produce_owner
industry
latest_progress
phase_wireless
```

其中 `entered_amount`与`latest_progress`只允许在一次性V34迁移中读取并搬迁到最终字段，完成后删除旧列和活动引用。

---

## 12. 过期测试与企业模块死代码

仅处理企业模块和直接依赖。

测试分类：

- KEEP：仍验证V4目标；
- REBUILD：目标有效，但路径、Section、字段或Contract结构已改变；
- DELETE：只验证旧目录、旧Schema、旧字段、旧兼容层或已删除死代码。

必须删除或重建：

- 断言`src/enterprise`为契约目录的测试；
- 断言旧`mox-field-schema.js`存在的测试；
- 断言“客户信息/业务信息”二分结构的测试；
- 断言客户类别只读的测试；
- 断言作战进展是普通输入的测试；
- 断言旧字段、fallback、双写或legacy兼容的测试；
- 只测试已删除代码的测试；
- 复制生产配置后测试复制品的伪测试。

死代码清理范围仅限：

- 企业契约配置；
- MOX表格/表单旧字段配置；
- MOX客户数据旧请求链；
- MOX进展旧实现；
- 企业API和`database.js`旧字段分支；
- 企业测试；
- `src/enterprise`旧契约目录。

不得扩展到非企业业务域。

---

## 13. 统计与筛选回归

9个 Metric 和点击筛选规则不得因本轮修复回归。

必须继续满足：

- 统计数值和点击筛选共用同一 `where`；
- 九个指标全部可点击；
- 点击后真实筛选下方表格；
- `annual.total`与`expansion.total`使用不同条件；
- 点击筛选不让顶部统计错误重算；
- 重点项目筛选使用 canonical `focusProject`。

---

## 14. 自动测试与验证

代码、测试、自动验证必须同轮完成。

至少运行：

- Contract路径和唯一Authority测试；
- 41字段、顺序和三个Section测试；
- 新增初始化成功/失败测试；
- 新增全字段、控件、保存和回填测试；
- 编辑全字段、权限、保存和回填测试；
- 客户类别空值/核心NA/战略NA测试；
- `customer_id`匹配测试；
- 作战进展特殊交互测试；
- 必要TOB进展回归测试；
- V34语法、注册、执行、回滚、幂等和最终Schema测试；
- 旧字段和旧路径无活动引用测试；
- 9个Metric与点击筛选回归测试；
- 企业模块测试；
- 全量Vitest；
- build；
- lint/typecheck（如配置）。

不执行人工页面检查，用户自行验收。

---

## 15. 完成标准

只有以下全部满足才可 `COMPLETE`：

1. Contract位于`src/config/enterprise`；
2. `src/enterprise`无活动Contract/Schema；
3. 重复Authority为0；
4. 新增能够正常打开；
5. 新增按三个Section完成全字段对齐；
6. 编辑按三个Section完成全字段对齐；
7. 新增/编辑均消费同一Field Contract；
8. 客户类别在新增和编辑均可选空值/核心NA/战略NA；
9. 作战进展恢复有效特殊交互；
10. 41字段、顺序、API/DB映射正确；
11. V34和最终数据库Schema正确；
12. Authority外旧字段、过期测试和企业死代码完成收敛；
13. 9个统计和点击筛选无回归；
14. 相关测试、全量测试和build通过；
15. 无其他模块或业务域越界修改。

---

## 16. 实施回执

```text
MOX V4 REMEDIATION COMPLETE/PARTIAL/BLOCKED
CONTRACT_PATH=路径
DUPLICATE_AUTHORITIES=0或数量
CREATE_DIALOG_OPEN=PASS/FAIL
CREATE_SECTIONS=客户信息/业务格局/作战情况 或 FAIL
CREATE_ALIGNMENT=PASS/PARTIAL/FAIL
CREATE_EXTRA_FIELDS=数量
CREATE_PERSISTENCE=PASS/PARTIAL/FAIL
EDIT_SECTIONS=客户信息/业务格局/作战情况 或 FAIL
EDIT_ALIGNMENT=PASS/PARTIAL/FAIL
EDIT_EXTRA_FIELDS=数量
EDIT_PERSISTENCE=PASS/PARTIAL/FAIL
CUSTOMER_CATEGORY=PASS/PARTIAL/FAIL
CUSTOMER_DATA_ERROR=FIXED/PARTIAL/FAIL
PROGRESS_EDITOR=PASS/PARTIAL/FAIL
V34=PASS/PARTIAL/FAIL
FINAL_DB_SCHEMA=PASS/PARTIAL/FAIL
OLD_RUNTIME_FIELDS=0或数量
OUTDATED_TESTS_DELETED=数量
OUTDATED_TESTS_REBUILT=数量
ENTERPRISE_DEAD_CODE_REMOVED=数量
METRIC_REGRESSION=NO/YES
MOX_TESTS=通过/失败
FULL_TESTS=通过/失败
BUILD=PASS/FAIL
OUT_OF_SCOPE_CHANGES=NO/YES
REVIEW_READY=YES/NO
NEXT=MOX_V4_INDEPENDENT_REVIEW
```
