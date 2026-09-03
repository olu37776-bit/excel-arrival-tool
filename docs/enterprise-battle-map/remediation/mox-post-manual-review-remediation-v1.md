# MOX 人工审查后定向修复计划 V1

**状态：CURRENT IMPLEMENTATION PLAN**  
**唯一业务 Authority：`mox-canonical-authority-v4.md`**  
**共享架构 Authority：`enterprise-contract-architecture-v3.md`**  
**本地分支：`feature/enterprise-battle-map`**  
**实施后下一门禁：MOX V4 独立审查**

---

## 1. 修复原因

用户人工检查发现当前 MOX 仍存在以下阻塞：

1. Contract/Schema 被放在 `src/enterprise`，目标应位于 `src/config`；
2. 企业模块存在过期测试和死代码；
3. 点击 MOX“新增”仍报“获取客户数据失败”；
4. 编辑中“客户类别”不可选择，实际应支持空值、核心NA、战略NA；
5. 新增/编辑仍使用旧“客户信息 / 业务信息”结构，没有使用三个同级 Section；
6. “作战进展”已退化，未保持之前有效的特殊交互；当前 TOB 进展实现仍正常，应作为直接参考；
7. V34、数据库列和旧字段清理必须继续接受验证；
8. 当前不能把 MOX 作为后续模块参考实现。

本计划只处理上述问题及其直接依赖，不实施其他模块，不建设企业首页，不修改 Heatmap 业务规则。

---

## 2. WRITE_SCOPE

### 2.1 允许修改

- `src/enterprise` 下当前 MOX Contract/Schema 配置；
- `src/config` 下当前企业/MOX字段和 Metric 配置；
- 目标 `src/config/enterprise`契约目录；
- MOX 表格、新增、编辑的 Contract Projection 接入；
- MOX 客户数据 API 调用及直接服务端查询链；
- 客户类别控件及客户主数据更新链；
- MOX 作战进展控件/handler接入；
- MOX、企业契约和直接相关测试；
- 企业模块直接相关死代码；
- V34及其 `database.js`注册、CRUD、映射和Validation（仅发现未完成时）；
- `enterprise-status.md`的实现状态。

### 2.2 禁止修改

- TOB、ISP、电力、大企字段 Contract；
- 企业首页真实汇总；
- Heatmap真实业务规则；
- 非企业模块代码、测试和死代码；
- 与MOX无关的数据库表；
- 已确认的41字段、顺序、枚举和统计公式；
- 其他模块页面样式。

---

## 3. 实施顺序

必须按顺序完成。不得只修 UI 后跳过 Contract、测试或数据库验证。

### Step 1：冻结基线

执行并记录：

```text
git branch --show-current
git status --short
git log -1 --oneline
git diff --stat
```

确认当前分支为 `feature/enterprise-battle-map`，不得丢失现有修改。

完整读取：

1. `enterprise-contract-architecture-v3.md`；
2. `mox-canonical-authority-v4.md`；
3. 本计划；
4. 本地 MOX Sheet；
5. 当前 MOX Contract、UI、API、`database.js`、V34、SQLite Schema和测试；
6. 当前 TOB 作战进展实现，仅作为进展交互参考。

### Step 2：恢复当前契约拓扑

列出并检查：

- `src/enterprise`下所有企业 Contract/Schema 文件；
- `src/config`下所有 MOX Field/Metric/Schema 文件；
- 全部 import、require和动态引用；
- 表格、新增、编辑实际读取的字段来源；
- 测试引用的旧路径。

产出当前依赖图，确认哪一份配置是真正运行时 Authority。

### Step 3：迁移到 `src/config/enterprise`

最终活动文件必须位于：

```text
src/config/enterprise/
```

至少包括共享 Contract 支持、MOX Field Contract和MOX Metric Contract。

规则：

- 迁移所有调用方；
- 目标路径生效后删除 `src/enterprise`中的活动契约文件；
- 删除旧 `mox-field-schema.js`第二 Authority；
- 删除旧 `src/config`根目录中重复MOX配置；
- 不保留 re-export、fallback或新旧路径双轨；
- 页面组件只从最终路径导入。

### Step 4：三个同级 Section

新增和编辑必须只显示：

```text
客户信息 ｜ 业务格局 ｜ 作战情况
```

要求：

- 三个 Section 同级；
- 删除旧“业务信息”Section；
- 无线和微波字段均位于“业务格局”；
- 业务格局内仍按 Field Contract order 先无线后微波；
- 不新增“无线格局/微波格局”两个顶级 Section；
- 作战进展为作战情况最后一项；
- 表格继续按1—41顺序，不显示Section标题。

### Step 5：客户类别修复

MOX 客户类别：

```text
空值
核心NA
战略NA
```

实现要求：

- 新增中为可选下拉；
- 编辑中为可选下拉；
- 空值必须作为合法状态处理，不得强制转为任意非空枚举；
- 控件值、API值和客户表值一致；
- 不在MOX业务表新增重复客户类别列；
- 保存客户类别必须写入客户主数据权威字段；
- 其他客户信息在编辑中保持只读；
- 修改客户类别不得改变 `customer_id`。

若现有客户更新API不足，补齐最小、明确的客户主数据更新路径，并增加权限和错误处理测试。

### Step 6：修复“获取客户数据失败”

必须定位真实根因，不得隐藏错误。

验证链：

```text
点击新增
→ 弹窗初始化
→ 客户数据请求
→ API route
→ database.js客户查询
→ 客户表
```

检查 URL、method、参数、route注册、响应结构、SQL、字段名和异常处理。

修复后必须保证：

- 新增弹窗可初始化；
- 地区部/代表处联动可用；
- 客户候选可读；
- 选择后得到唯一 `customer_id`；
- API失败仍返回可诊断错误；
- 同名客户不得自动取第一条。

### Step 7：恢复作战进展特殊交互

当前 TOB 仍正常的作战进展实现是直接参考。

要求：

- 复用或抽取 TOB 当前有效的进展组件/handler；
- MOX Field Contract 的 `battleProgress`通过 `editorId`或当前等价机制接入；
- 用户可见名称为“作战进展”；
- 支持原有新增、追加、编辑、保存和回填；
- 不允许退化为普通input/textarea；
- 不复制第二套不同实现；
- 不继续使用 `latest_progress`作为活动字段。

若提炼共享进展组件，只允许调整MOX和TOB直接相关引用，并必须验证TOB无回归。

### Step 8：V34与最终数据库复核

复核而不是假定已完成：

- V34 SQL语法正确；
- V34注册在`database.js`实际Migration链；
- 事务、回滚和`_migrations`登记正确；
- 新建库与升级库MOX最终Schema一致；
- 41字段映射完整；
- `dpm`、`remark`、`service_interface`、`entered_amount`、`space_26`、`produce_owner`、`industry`、`latest_progress`、`phase_wireless`及其他Authority外旧业务列已删除；
- `database.js`不再有旧字段活动CRUD、映射或Validation；
- 不保留双写、fallback或旧API字段。

发现缺口时在本轮完成最小修复并同步Migration测试。

### Step 9：企业模块过期测试清理

仅处理企业模块及其直接依赖测试。

先将测试分类：

- KEEP：仍验证V4 Authority；
- REBUILD：测试目标有效但路径、Section、字段或Contract结构已变化；
- DELETE：只验证旧路径、旧Schema、旧字段、兼容层或已删除代码。

必须删除或重建：

- 断言 `src/enterprise`为契约目录的测试；
- 断言旧 `mox-field-schema.js`存在的测试；
- 断言“客户信息/业务信息”二分结构的测试；
- 断言客户类别编辑只读的测试；
- 断言旧进展普通输入或旧字段名的测试；
- 断言旧字段、fallback、双写或legacy compatibility的测试；
- 对已删除死代码的测试；
- 复制生产字段数组后验证复制品的测试。

新测试必须直接使用真实 Contract、Projection、API、Migration和Metric Engine。

### Step 10：企业模块死代码清理

范围只限：

- 企业契约配置；
- MOX页面/表格/表单旧字段配置；
- MOX客户数据旧请求链；
- MOX作战进展旧实现；
- 企业API和database.js旧字段分支；
- 企业测试；
- `src/enterprise`旧契约目录。

删除前建立 import/reference 清单。只有满足以下任一条件才删除：

- 无活动引用；
- 已被V4 Contract/Projection完整替代；
- 只服务已删除旧字段或旧需求。

不得扩展到非企业模块。

### Step 11：测试与自动验证

代码、测试、自动验证必须同轮完成。

至少验证：

- Contract最终路径；
- 41字段与1—41顺序；
- 三个Section；
- 表格/新增/编辑使用同一Contract；
- 客户类别空值/核心NA/战略NA；
- 客户数据成功和失败路径；
- `customer_id`匹配；
- 作战进展特殊交互；
- TOB进展无回归（如提炼共享组件）；
- V34注册、执行、回滚、幂等；
- 新建库/升级库最终Schema；
- 旧字段和旧路径无活动引用；
- 过期测试已删除或重建；
- 9个Metric与点击筛选无回归。

执行项目真实脚本：

- MOX Contract测试；
- MOX新增/编辑测试；
- 客户API/数据库测试；
- Migration测试；
- Metric测试；
- 企业模块测试；
- 全量Vitest；
- build；
- lint/typecheck（如配置）。

不执行人工页面检查，用户自行验收。

---

## 4. 完成标准

只有以下全部满足才可 `COMPLETE`：

1. Contract Authority位于`src/config/enterprise`；
2. `src/enterprise`无活动Contract/Schema；
3. 不存在重复MOX字段Authority；
4. 新增和编辑使用三个同级Section；
5. 客户类别在新增/编辑均可选择空值/核心NA/战略NA；
6. 点击新增不再报客户数据失败；
7. 作战进展恢复为TOB参考的特殊交互；
8. 41字段、顺序、API/DB映射正确；
9. V34和最终数据库Schema正确；
10. Authority外旧字段及活动引用为0；
11. 企业模块过期测试已删除或重建；
12. 企业模块相关死代码已清理；
13. 9个统计和点击筛选无回归；
14. 相关测试、全量测试和build通过；
15. 没有修改其他模块或其他业务域。

---

## 5. 实施回执

本地 Agent 最终只需返回：

```text
MOX V4 REMEDIATION COMPLETE/PARTIAL/BLOCKED
CONTRACT_PATH=路径
OLD_ENTERPRISE_CONTRACT_FILES=0或数量
DUPLICATE_AUTHORITIES=0或数量
SECTIONS=客户信息/业务格局/作战情况 或 FAIL
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
