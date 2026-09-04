# 企业作战地图基表 V0.1 → V0.2 差异调查 V1

**状态：CURRENT INVESTIGATION TASK**  
**本地目录：`D:\BattleMap`**  
**输入：企业作战地图基表 V0.1 与 V0.2 两个 Excel 工作簿**  
**性质：只读调查，不修改代码、不修改数据库、不修改 Authority 业务定义**

---

## 1. 目标

本轮只做版本差异恢复，回答：

> 企业作战地图基表 V0.2 相比 V0.1 到底发生了哪些变化，以及这些变化可能影响哪些企业模块 Contract / Runtime。

不要直接实施代码修改。先形成事实清单，再由设计/Authority 决定哪些变化属于：

```text
DISPLAY_ONLY
GROUP_OR_ORDER_CHANGE
OPTION_SET_CHANGE
FIELD_ADDED
FIELD_REMOVED
FIELD_RENAMED_SAME_SEMANTICS
FIELD_SEMANTICS_CHANGED
DATA_TYPE_OR_FORMAT_CHANGE
BUSINESS_DATA_ONLY
NEED_USER_CONFIRMATION
```

---

## 2. 输入文件定位

在 `D:\BattleMap` 下定位文件名包含：

```text
企业作战地图基表V0.1
企业作战地图基表V0.2
```

允许 `.xlsx` / `.xlsm` / `.xls` 等实际存在格式。

必须先返回实际完整文件名、绝对路径、文件大小、修改时间。

若任一版本存在多个候选文件，不得自行挑选，返回 `BLOCKED_MULTIPLE_CANDIDATES` 并列出候选。

不得修改原始工作簿。

---

## 3. 比较优先级

本次比较优先看 **Schema / Contract 变化**，业务数据行变化只做次级摘要。

优先级：

1. Sheet 新增 / 删除 / 重命名 / 顺序；
2. 每个业务 Sheet 的 Row2 分组；
3. Row3 字段 label；
4. 字段列新增 / 删除；
5. 字段重命名；
6. 字段顺序变化；
7. 字段 group 变化；
8. Data Validation / 下拉选项变化；
9. 单元格格式 / 数字格式 / 日期格式 / 百分比 / 金额单位变化；
10. 公式变化；
11. 合并单元格结构变化；
12. 冻结窗格、隐藏列等仅在影响解析或使用时记录；
13. 业务数据内容变化摘要。

不要把普通字体、颜色、边框等纯视觉格式变化当成 Contract change，除非它影响 Row2/Row3 识别或 Data Validation。

---

## 4. Sheet 级比较

输出：

```text
SHEETS_ADDED=
SHEETS_REMOVED=
SHEETS_RENAMED=
SHEETS_REORDERED=
```

对名称相同的 Sheet 继续字段级比较。

对疑似重命名 Sheet，可以根据字段集合高度相似提出 `POSSIBLE_RENAME`，但不得自动定论。

---

## 5. 字段级比较

每个业务 Sheet 建立 V0.1 和 V0.2 字段 inventory：

```text
column
row2Group
row3Label
validation
numberFormat
formulaPresence
mergedHeaderContext
```

然后输出差异：

### 5.1 新增字段

```text
ADDED
sheet=
column=
row2Group=
row3Label=
validation=
format=
```

### 5.2 删除字段

同样记录旧位置和属性。

### 5.3 重命名候选

不要只按列位置判断。

只有在下列证据较强时才标记：

```text
POSSIBLE_RENAME_SAME_SEMANTICS
```

例如：

- 相邻字段上下文一致；
- group 一致；
- 数据列值高度一致；
- validation 一致；
- 格式一致；
- 新旧 label 语义近似。

否则标记：

```text
NEED_USER_CONFIRMATION
```

绝不能把“删除一个字段 + 新增另一个字段”未经确认自动认定为同义改名。

### 5.4 顺序 / 分组变化

字段 identity 可暂以 `(Sheet + Row3 label)` 辅助比对，但最终报告必须注明 canonical key 需要由现有 Authority 映射，不得用中文 label 直接定义新的 canonical key。

---

## 6. Data Validation 比较

重点恢复固定下拉变化。

需要展开并标准化：

- 直接列表；
- 引用区域；
- named range；
- 跨 Sheet 引用。

输出 exact set：

```text
OPTION_SET_CHANGED
sheet=
field=
V0.1=[...]
V0.2=[...]
ADDED_OPTIONS=[...]
REMOVED_OPTIONS=[...]
```

顺序变化单独记录，不要误判为值域变化。

---

## 7. 数据类型 / 格式 / 公式变化

对字段记录：

```text
NUMBER_FORMAT_CHANGED
FORMULA_CHANGED
FORMULA_TO_VALUE
VALUE_TO_FORMULA
PERCENT_OR_CURRENCY_UNIT_CHANGED
DATE_FORMAT_CHANGED
```

如果只有展示格式变化但真实数值语义不变，标记 `DISPLAY_ONLY`。

如果可能改变运行时数据类型或单位，标记 `CONTRACT_IMPACT_POSSIBLE`。

---

## 8. 业务数据行变化

业务数据变化不是本轮主要目标，但需要给出摘要：

每个 Sheet：

```text
ROW_COUNT_V0.1=
ROW_COUNT_V0.2=
ROW_COUNT_DELTA=
```

如果能找到稳定业务主键（例如客户ID、合同号等，以 Sheet 实际字段为准），统计：

```text
ROWS_ADDED=
ROWS_REMOVED=
ROWS_CHANGED=
```

不要逐单元格打印全部业务数据差异；只对 Schema 变化判断有帮助时抽样。

如果没有可靠主键，不得用行号冒充业务 identity，标记 `NO_STABLE_ROW_KEY`。

---

## 9. 与现有 Enterprise Authority 对照

读取本地 Authority 镜像：

```text
D:\BattleMap\BattleMapenterprise-authority\docs\enterprise-battle-map\authority-index.md
```

并至少读取当前：

```text
enterprise-contract-architecture-v5.md
mox-canonical-authority-v6.md
tob-canonical-authority-v2.md
isp-canonical-authority-v2.md
power-canonical-authority-v2.md
large-enterprise-canonical-authority-v2.md
```

对每个 Excel Schema 变化，尝试映射到已有 canonical field。

输出：

```text
CURRENT_CANONICAL_MATCH=<key or NONE>
IMPACT=<NONE/LABEL/GROUP/ORDER/OPTION_SET/FIELD_CONTRACT/PERSISTENCE/METRIC/HEATMAP/UNKNOWN>
```

禁止直接修改 Authority。

如果 V0.2 中字段与当前 Authority 明显冲突，只记录事实，不自行选择 Excel 或旧 Authority 谁覆盖谁。

---

## 10. 报告

创建本地只读调查报告：

```text
D:\BattleMap\battle-map\docs\enterprise\investigations\enterprise-excel-v0.1-v0.2-diff-report.md
```

报告结构：

1. Input files；
2. Workbook-level summary；
3. Sheet-level changes；
4. Field-level changes；
5. Option-set changes；
6. Format/type/formula changes；
7. Business-data delta summary；
8. Current canonical mapping / impact；
9. NEED_USER_CONFIRMATION；
10. Recommended Authority changes（仅建议，不实施）。

重点给出一个汇总表：

| Module/Sheet | Change Type | V0.1 | V0.2 | Current Canonical Key | Impact | User Confirmation |
|---|---|---|---|---|---|---|

---

## 11. 禁止事项

- 不修改两个 Excel；
- 不修改生产代码；
- 不修改 SQLite；
- 不修改 Field Contract；
- 不新增 Migration；
- 不自动接受 V0.2 为最终 Authority；
- 不自动把 label rename 变成 canonical key rename；
- 不使用 Excel 行号作为业务主键；
- 不输出海量无意义单元格 diff。

---

## 12. 最终短回执

```text
ENTERPRISE EXCEL V0.1 -> V0.2 DIFF SURVEY
RESULT=COMPLETE/PARTIAL/BLOCKED
V01_FILE=
V02_FILE=
SHEETS_ADDED=
SHEETS_REMOVED=
FIELD_ADDED_COUNT=
FIELD_REMOVED_COUNT=
POSSIBLE_RENAME_COUNT=
GROUP_CHANGE_COUNT=
ORDER_CHANGE_COUNT=
OPTION_SET_CHANGE_COUNT=
FORMAT_TYPE_CHANGE_COUNT=
BUSINESS_DATA_CHANGE=YES/NO/UNKNOWN
CANONICAL_IMPACT_COUNT=
NEED_USER_CONFIRMATION_COUNT=
REPORT=
BLOCKERS=NONE或内容
NEXT=AUTHORITY_REVIEW
```
