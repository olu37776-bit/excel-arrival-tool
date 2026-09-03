# 企业作战地图：ISP 并行实施计划 V1

**状态：CURRENT IMPLEMENTATION PLAN**  
**任务分支：`task/enterprise-isp`**  
**长期集成分支：`feature/enterprise-battle-map`**  
**Migration预留：`V36.sql`**  
**实施性质：现有页面最小重构 + 契约化收敛**

---

## 1. 必读 Authority

按顺序读取：

1. `enterprise-contract-architecture-v3.md`；
2. `parallel-module-execution-v1.md`；
3. `isp-canonical-authority-v2.md`；
4. 本地“企业作战地图基表”的 ISP Sheet；
5. 当前 MOX Contract/Projection/Metric实现，仅参考机制；
6. 当前 ISP 页面、表格、新增、编辑、Heatmap、API、`database.js`、SQLite和测试。

字段和页面业务以 ISP Authority 为准；目录、Contract形态、三个Section、数据库和测试治理以共享架构 V3 为准。

---

## 2. 分支与边界

从冻结的 `feature/enterprise-battle-map`同一 `BASE_HEAD`创建：

```text
task/enterprise-isp
```

使用独立 worktree/环境。不得在长期集成分支直接工作。

只处理 ISP。禁止修改 TOB、电力、大企、企业首页和 MOX 业务 Contract。

共享内核默认只读。确需修改共享文件时，必须记录原因并添加共享回归测试；架构级缺口返回 `SHARED_BLOCKER`。

---

## 3. 目标

将现有 ISP 页面收敛为：

```text
ISP专项
→ 空间洞察 / 当年项目 / 空间拓展三个并列统计模块
→ 现有ISP Heatmap
→ 新增 / 表格 / 编辑
```

新增与编辑使用三个同级 Section：

```text
客户信息 ｜ 业务格局 ｜ 作战情况
```

建立唯一：

```text
src/config/enterprise/isp-field-contract.js
src/config/enterprise/isp-metric-contract.js
```

表格、新增、编辑从 Field Contract 派生；统计与点击筛选从 Metric Contract 同一 `where`派生。

---

## 4. 现有实现处理

ISP 当前已有页面，应采用最小改动：

- 已正确页面壳、ISP专项、Heatmap、客户联动、CRUD和样式优先保留；
- 旧表格/新增/编辑字段数组迁移到 Contract 后删除；
- 目标外业务字段从 UI、活动 API 契约、`database.js`映射和最终 ISP Schema 删除；
- 只清理 ISP 与直接企业共享依赖中的过期测试和死代码；
- 不复制 MOX 具体字段；
- Heatmap规则未完全冻结时保留现有正确逻辑或安全空状态，不生成假数据。

---

## 5. 字段 Contract

字段集合、canonical key、顺序和规则以 `isp-canonical-authority-v2.md`为准，目标总数为 25。

每项必须写实：

- `key`、`label`、`section`、`order`；
- Excel Sheet、列、Row2、Row3、Validation；
- data type、unit；
- table/create/edit投影、权限和控件；
- API read/create/update字段；
- `database.js`映射；
- SQLite列和类型；
- Validation与特殊行为。

关键门禁：

- ISP有行业、无客户类别；
- `微波应用场景`固定为骨干汇聚微波互联、2B专线、基站回传；
- `解决方案`固定为licensed微波、unlicensed微波，不得拆出第三个“微波”；
- `现网微波链路数量（跳）`、`我司份额（%）`、`友商空间（跳）`类型和单位正确；
- `代表处是否有系统部`为是/否；
- `作战分类-是否重点项目`是一个字段，现有筛选使用 `focusProject`；
- `作战进展`固定最后并使用共享特殊进展编辑器；
- 目标外字段数量：table/create/edit均为0。

---

## 6. 客户关系

ISP业务记录保存 `customer_id`。

要求：

- 复用地区部、代表处等现有联动；
- 新增最终定位唯一客户并自动保存 `customer_id`；
- 客户ID不可手填；
- 同名客户不得取第一条；
- 编辑客户信息全部只读；
- 编辑业务字段不得改变 `customer_id`；
- API校验客户真实存在；
- 行业通过客户主数据关系读取，不在ISP业务表新增重复客户属性Authority。

如当前 ISP 缺少完整 `customer_id`链路，按共享架构补齐，不创建第二套客户模型。

---

## 7. 数据库与 V36

如当前 ISP Schema 已与目标完全一致，可记录 `MIGRATION_NOT_REQUIRED`；否则使用预留 `V36.sql`。

V36必须：

- 注册到 `database.js`真实Migration链；
- 成功后写 `_migrations`；
- 在事务中执行，失败回滚；
- 新建库与旧库升级后ISP Schema一致；
- 搬迁同义历史数据后删除旧列；
- 删除无Authority旧列；
- 同步CRUD、字段映射、Validation和API；
- 具备执行、回滚、幂等和最终Schema测试。

若 `V36.sql`已被占用，停止并返回 `MIGRATION_VERSION_CONFLICT`。

---

## 8. Metric与点击筛选

使用ISP Authority中的9项Metric：

- 已孵化、孵化中；
- 当年项目总项目数、已签单、推进中、高风险；
- 可参与总空间、空间拓展总项目、已落地。

要求：

- 同一 `where`同时用于统计和点击表格筛选；
- 当前不增加年份过滤；
- `annual.total`与`expansion.total`不同；
- 高风险使用“推进中 AND 高风险”；
- 可参与总空间对符合条件记录的 `overallSpaceMusd`求和；
- 九个指标全部可点击；
- 点击只改变表格，不让顶部统计错误重算；
- 三个大模块并列、文字居中，不拆成9张顶级卡。

---

## 9. 测试治理

代码与测试同轮完成。

必须覆盖：

1. 25字段、三个Section和精确顺序；
2. Excel Authority完整；
3. ISP有行业、无客户类别；
4. 应用场景和解决方案枚举；
5. 百分比读写口径；
6. table/create/edit真实消费同一 Contract；
7. 目标外字段为0；
8. customer_id新增保存、编辑不变、客户信息只读；
9. focusProject与重点项目筛选；
10. 作战进展特殊编辑器；
11. 代表处是否有系统部与一线接口人保存/回填；
12. 9个Metric及9个点击筛选；
13. ISP Heatmap无回归；
14. V36或`MIGRATION_NOT_REQUIRED`证据；
15. 新建库/升级库Schema；
16. ISP过期测试已删除或重建；
17. ISP死代码清理后无活动引用；
18. 全量Vitest、build、lint/typecheck（如配置）。

不得执行人工页面检查。

---

## 10. 实施报告与完成门槛

创建：

```text
docs/enterprise/implementations/isp-implementation-report.md
```

记录：BASE_HEAD、任务分支、changed files、共享文件修改、Field/Metric Contract、Excel字段核验、Migration、测试、build、阻塞和未完成项。

只有以下全部满足才可 `IMPLEMENTED_NOT_VERIFIED`：

- 25字段及三处Projection正确；
- API/DB映射完整；
- customer_id正确；
- 9个统计与点击筛选正确；
- Heatmap无回归；
- 测试和build通过；
- 没有修改其他模块；
- 已提交到 `task/enterprise-isp`；
- 未合并、未审查。

最终等待统一集成和统一独立审查。
