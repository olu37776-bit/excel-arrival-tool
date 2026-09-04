# 企业作战地图：MOX 新增/编辑 Field Contract 运行时完整性审查 V1

**状态：CURRENT REVIEW AUTHORITY**  
**审查对象：MOX 新增与编辑弹窗的字段完整性及 Field Contract 实际运行时接入**  
**代码目录：`D:\BattleMap\battle-map`**  
**本地 Authority：`D:\BattleMap\BattleMapenterprise-authority`**  
**当前业务 Authority：`mox-canonical-authority-v4.md`**  
**审查性质：只读定位，不实施 remediation**

---

## 1. 本轮只回答的问题

本轮只回答两个问题：

1. `src/config/enterprise/mox-field-contract.js` 是否真的成为 MOX 新增和编辑的唯一字段来源；
2. 当前新增/编辑是否遗漏了 Contract / Authority 要求展示的字段，遗漏发生在哪一层。

本轮暂不重新决定 MOX Section 最终是 3 个还是 4 个，也不做视觉样式修复。Section 命名/数量由用户后续单独确认后再更新 Authority。

---

## 2. Authority 基线

MOX 当前 Canonical Authority 定义 41 个封闭业务字段，order 为 1—41。

Field Contract 必须为每个字段定义至少：

- `key`
- `label`
- `section`
- `order`
- `ui.table`
- `ui.create`
- `ui.edit`
- `runtime`
- `validation`
- `behavior`

新增和编辑不得各自维护另一份完整字段数组。

正确链路应为：

```text
mox-field-contract.js
→ field-projections.js
→ create projection / edit projection
→ 新增弹窗 / 编辑弹窗
→ control registry / special editor
```

不是：

```text
Contract文件存在
+ 新增自己一套fields
+ 编辑自己一套fields
```

---

## 3. 第一层：Contract 本体完整性

审查 `src/config/enterprise/mox-field-contract.js`：

1. 是否正好包含 41 个 canonical business keys；
2. key 唯一；
3. order 是否连续 1—41；
4. 是否仍缺少 Authority 中任一字段；
5. 是否存在 Authority 外业务字段；
6. 每个字段是否有明确 `ui.create.visible` 与 `ui.edit.visible`；
7. 所有应该进入新增/编辑的字段是否被错误标为 `visible:false`；
8. `battleProgress` 是否仍通过特殊 `editorId` / behavior 接入；
9. 两组重名字段是否保持不同 canonical key；
10. 客户类别是否允许新增和编辑。

产出：

```text
CONTRACT_FIELD_COUNT=
CONTRACT_KEYS_MISSING=
CONTRACT_EXTRA_KEYS=
CREATE_VISIBLE_COUNT=
EDIT_VISIBLE_COUNT=
CREATE_FALSE_UNEXPECTED=
EDIT_FALSE_UNEXPECTED=
```

---

## 4. 第二层：Projection 是否真实使用 Contract

审查 `field-projections.js` 及 MOX 调用链。

必须确认：

- create projection 直接从当前 MOX Field Contract 生成；
- edit projection 直接从当前 MOX Field Contract 生成；
- projection 不维护第二份字段白名单；
- projection 不使用旧 `mox-field-schema.js`；
- projection 不按旧字段名过滤；
- projection 不因 section/group 名称变化静默丢字段；
- projection 排序来自 `order`；
- `visible/editable/controlId`来自 Contract，而不是组件硬编码覆盖。

重点查找：

- `.filter(...)` 中写死 key 列表；
- `CREATE_FIELDS` / `EDIT_FIELDS` / `businessFields` / `customerFields` 等完整数组；
- 旧 `业务信息` 分组映射；
- hard-coded exclude list；
- `if (field.section === ...)` 导致未识别 section 被直接丢弃。

产出：

```text
CREATE_PROJECTION_SOURCE=CONTRACT/HARDCODED/MIXED
EDIT_PROJECTION_SOURCE=CONTRACT/HARDCODED/MIXED
SECONDARY_FIELD_ARRAYS=数量+路径
PROJECTION_DROPPED_KEYS=字段列表
```

---

## 5. 第三层：新增弹窗实际字段集合

从新增弹窗真实运行时代码恢复其最终渲染字段集合，不只读测试。

对比：

```text
ExpectedCreateKeys
= Contract 中 ui.create.visible=true 的 key 集合

ActualCreateKeys
= 新增弹窗最终实际渲染的 key 集合
```

必须计算：

```text
MissingCreateKeys = ExpectedCreateKeys - ActualCreateKeys
ExtraCreateKeys = ActualCreateKeys - ExpectedCreateKeys
```

同时记录每个 missing key 的丢失层：

- Contract 本体缺失；
- Contract visible 配置错误；
- Projection 丢失；
- Section renderer 丢失；
- control registry 无 renderer；
- 模板未消费 projection；
- 其他明确根因。

客户数据 API 当前是否能打开弹窗不是本轮字段审查的替代条件。即使初始化失败，也必须静态恢复完整字段渲染链。

---

## 6. 第四层：编辑弹窗实际字段集合

同样计算：

```text
ExpectedEditKeys
= Contract 中 ui.edit.visible=true 的 key 集合

ActualEditKeys
= 编辑弹窗最终实际渲染的 key 集合

MissingEditKeys = ExpectedEditKeys - ActualEditKeys
ExtraEditKeys = ActualEditKeys - ExpectedEditKeys
```

特别核验：

- 客户类别存在且按 Authority 可编辑；
- 其他客户信息权限符合 Contract；
- `battleProgress`存在并使用特殊编辑器；
- 作战情况末尾字段没有因为特殊 editor 被漏掉；
- 业务格局的无线/微波字段没有因为分组映射漏一部分。

---

## 7. 第五层：测试是否真的能防止漏字段

检查当前 MOX form tests。

有效测试必须直接从真实 Contract 和真实 projection 得出期望值，至少断言：

```text
Set(createProjection.keys) === Set(contract where ui.create.visible)
Set(editProjection.keys) === Set(contract where ui.edit.visible)
```

并验证：

- 顺序一致；
- 无 extra；
- 无 missing；
- 特殊 editor 可解析；
- 不复制一份 41 字段数组到测试中自证；
- 不只检查字段数量而忽略具体 key。

如果当前测试全部通过但人工仍发现漏字段，必须解释测试为什么没有捕获该缺陷。

---

## 8. Field Contract 是否“起作用”的判定

结果只能按以下分类：

### EFFECTIVE

同时满足：

- Contract 是唯一字段 Authority；
- create/edit projection 均直接由 Contract 派生；
- 组件不维护第二份完整字段清单；
- ExpectedCreateKeys = ActualCreateKeys；
- ExpectedEditKeys = ActualEditKeys；
- 测试能够阻止未来漏字段。

### PARTIALLY_EFFECTIVE

典型情况：

- Contract 存在且部分页面消费；
- 但 create/edit 仍有 hard-coded filter、旧 schema 或 section mapping；
- 或 Contract 的 visible 配置导致字段遗漏；
- 或测试不能验证完整投影。

### NOT_EFFECTIVE

典型情况：

- 新增/编辑仍主要维护自己的字段数组；
- Contract 只是文档化配置，没有真正驱动渲染；
- 旧 schema/config仍是实际运行时 Authority。

---

## 9. Finding 分级

### BLOCKING

- 新增或编辑漏任何当前 Authority 要求显示的字段；
- 新增/编辑不由唯一 Contract 派生；
- 存在第二份活动完整字段 Authority；
- `battleProgress`或关键客户字段因 projection/renderer 缺失无法出现；
- 测试通过但完全无法检测字段漏失。

### HIGH

- Contract 本体完整但 visible/editable 配置错误；
- Section renderer 会静默丢弃未知 section；
- 测试仅按数量断言、未比较 key 集合；
- create/edit 使用两套近似但不完全相同的 projection 逻辑。

---

## 10. 审查产物

写入：

```text
docs/enterprise/reviews/mox-create-edit-contract-runtime-audit.md
```

本轮只读，不修改生产代码和测试。

最终短回执：

```text
MOX FORM CONTRACT RUNTIME AUDIT
RESULT=EFFECTIVE/PARTIALLY_EFFECTIVE/NOT_EFFECTIVE
REVIEWED_HEAD=SHA
CONTRACT_FIELD_COUNT=
CREATE_VISIBLE_COUNT=
EDIT_VISIBLE_COUNT=
ACTUAL_CREATE_COUNT=
ACTUAL_EDIT_COUNT=
MISSING_CREATE_KEYS=
MISSING_EDIT_KEYS=
EXTRA_CREATE_KEYS=
EXTRA_EDIT_KEYS=
CREATE_PROJECTION_SOURCE=CONTRACT/HARDCODED/MIXED
EDIT_PROJECTION_SOURCE=CONTRACT/HARDCODED/MIXED
SECONDARY_FIELD_ARRAYS=
OLD_SCHEMA_ACTIVE=YES/NO
BATTLE_PROGRESS_CREATE=PASS/FAIL
BATTLE_PROGRESS_EDIT=PASS/FAIL
TEST_GAP=NONE/描述
BLOCKING_FINDINGS=
HIGH_FINDINGS=
CODE_CHANGED=NO
NEXT_GATE=MOX_FORM_REMEDIATION/CONTINUE_REVIEW
```
