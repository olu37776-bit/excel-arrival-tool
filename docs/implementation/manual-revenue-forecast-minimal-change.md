# 基表收入预测最小改动实施说明

- 文档 ID：`MANUAL-REVENUE-FORECAST-MINIMAL-CHANGE`
- 状态：`IMPLEMENTED`
- 日期：`2026-08-27`
- 仓库：`olu37776-bit/excel-arrival-tool`
- 实施分支：`main`
- 本次修正基线：`29243a621eb3985b296d2849b0be73f48b4fced7`
- 修正规则：Issue #26、Issue #27

> `refactor/revenue-allocation-v1` 暂时冻结，仅保留历史，不作为本次实施依据。本次直接在现有 `main` 稳定实现上做最小修改，不再引入 RevenueAllocationCandidate、PreviousRunState、Posting、月度汇总新工作簿或双任务 GUI。

---

## 1. 本次目标

保持现有“合同号 + 履行供应中心”基表和五张业务 Sheet，只完成五项变化：

1. 新增三个金额字段：
   - `收入预测`
   - `调整月份（按RPD）`
   - `调整月份（按CPD）`
2. `收入预测`由系统按最终展示的`遗留量 + 当月新订货`计算。
3. 多履行供应中心合同的`遗留量`、`当月新订货`和`收入预测`只在“深供”行显示，其他供应中心行显示0，避免金额重复汇总。
4. 两个人工金额字段`调整月份（按RPD）/调整月份（按CPD）`首次为空，后续从上一次结果继承。
5. 取消`备货总控标识`与`发货总控标识`不同步异常，即停止生成`CONTROL_FLAG_MISMATCH`。

除此之外，现有字段、日期计算、收入年月、收入分段、跨月变化、异常处理和 GUI 主流程均不改变。

---

## 2. 新增三个字段

新增稳定字段 ID：

```text
revenue_forecast
manual_revenue_forecast_rpd
manual_revenue_forecast_cpd
```

显示名称：

```text
收入预测
调整月份（按RPD）
调整月份（按CPD）
```

`收入预测`是系统计算金额；`调整月份（按RPD）/调整月份（按CPD）`沿用原两个手工调整收入预测字段的数据类型和人工金额语义。Issue #27只修改显示名称，不改变稳定字段ID或业务规则。

### 2.1 收入预测

`收入预测`按当前结果行最终展示金额计算：

```text
收入预测 = 遗留量 + 当月新订货
```

系统写入Decimal两位小数结果，不写Excel公式，不使用上期人工值覆盖。

### 2.2 调整月份（按RPD）

首次为空，用户手工填写，后续继承。

不根据`收入预测`或`收入年月（按RPD）`自动生成。

### 2.3 调整月份（按CPD）

首次为空，用户手工填写，后续继承。

不根据`收入预测`或`收入年月（按CPD）`自动生成。

### 2.4 空白与0

两个手工调整字段必须区分：

```text
空白 → None，表示未填写
0 / 0.00 → Decimal("0.00")，表示用户明确填写0
```

不得使用 truthy/falsy 判断人工金额。

---

## 3. 基表字段顺序

现有32列调整为35列，冻结顺序如下：

```text
1  合同号
2  遗留量
3  当月新订货
4  收入预测
5  BG
6  地区部
7  国家
8  结转类型
9  客户群
10 项目名称
11 贸易术语
12 履行供应中心
13 多个供应中心发货
14 是否解锁备货
15 分批发货
16 海运周期
17 ATA
18 ASD
19 RPD
20 多次要货
21 最晚ASD
22 最晚RPD
23 货未发完
24 CPD
25 分批供应
26 到货日期（按RPD）
27 到货日期（按CPD）
28 收入年月（按RPD）
29 收入年月（按CPD）
30 收入分段类别
31 是否手工调整预测
32 调整月份（按RPD）
33 调整月份（按CPD）
34 调整金额
35 调整备注
```

即：

- `收入预测`插在`当月新订货`之后；
- 两个人工金额字段插在`是否手工调整预测`之后；
- 其他原字段相对顺序保持不变。

---

## 4. 人工字段继承

现有继承业务键继续使用：

```text
合同号 + 履行供应中心
```

无要货占位行继续使用：

```text
合同号 + 空履行供应中心
```

人工字段继承集合扩展为：

```text
manual_adjust_flag
manual_revenue_forecast_rpd
manual_revenue_forecast_cpd
manual_revenue_month
adjustment_note
```

首次没有上期结果时，五个人工字段全部为空；`收入预测`正常自动计算。

旧32列结果作为上一次结果时：

- 原`是否手工调整收入月份 / 手工调整收入月份 / 调整备注`通过稳定字段ID或旧显示名别名继续正常继承；
- 旧32列结果不存在的两个新人工金额字段保持空白；
- `收入预测`根据本期遗留量和当月新订货重新计算；
- 缺少新增字段不得导致整个上一次结果不可用；
- RPD/CPD跨期比较继续按现有规则执行。

输入解析必须把`调整月份（按RPD）/调整月份（按CPD）`按原有人工金额类型处理：

- 正数、负数、0均支持；
- 空白保持`None`；
- 非空且无法解析的人工金额不得静默变0，应记录明确的上期字段/金额异常并按空白处理。

---

## 5. 多供应中心合同的金额展示规则

### 5.1 目的

现有实现会把合同级：

```text
遗留量
当月新订货
收入预测
```

复制到同一合同的每个履行供应中心行，直接汇总会重复。

本次只修改**基表展示金额**，不改变合同原始金额事实和收入分段计算。

### 5.2 单供应中心

合同只有一个有效履行供应中心时：

```text
遗留量 = 合同真实遗留量
当月新订货 = 合同真实当月新订货
收入预测 = 遗留量 + 当月新订货
```

### 5.3 多供应中心

同一合同存在多个有效履行供应中心时：

```text
履行供应中心规范化后精确等于“深供”
→ 该行保留完整合同金额
→ 收入预测 = 遗留量 + 当月新订货

其他供应中心行
→ 遗留量 = 0.00
→ 当月新订货 = 0.00
→ 收入预测 = 0.00
```

“深供”使用现有文本规范化规则后做精确匹配，不使用模糊相似度。

### 5.4 重要边界：展示金额不得影响收入分段

当前`收入分段类别`会使用合同真实`遗留量 / 当月新订货`判断`未录入订货 / 订未发`等状态。

因此实现必须先使用合同真实金额完成所有业务计算，再在最终构建BaseRow展示值时执行多中心金额归零。

禁止出现：

```text
非深供行因为展示金额被置0
→ 被错误判为“未录入订货”
```

也就是说：

```text
业务计算金额 ≠ 多中心场景下的展示金额
```

金额归零只影响以下用户可见字段：

```text
legacy_amount
monthly_new_order
revenue_forecast
```

不反向影响日期、到货日期、收入年月、收入分段或其他计算。

### 5.5 多中心但不存在“深供”

为避免合同金额静默消失，本次采用安全行为：

```text
多供应中心，但没有任何中心规范化后精确等于“深供”
→ 不执行金额归零
→ 保持现有各中心重复展示
→ 记录异常 MULTI_CENTER_DEEP_SUPPLY_NOT_FOUND
```

异常信息至少包含：

- 合同号；
- 实际履行供应中心集合；
- 原因：多中心合同未找到“深供”金额承载行，因此未做金额归零。

禁止在未找到“深供”时任选第一行承载金额，因为这会制造未经业务确认的新规则。

### 5.6 无要货合同

`CONTRACT_ONLY_NO_DEMAND`占位行只有一行，继续正常显示完整：

```text
遗留量
当月新订货
收入预测
```

不应用“深供”规则。

---

## 6. 取消 CONTROL_FLAG_MISMATCH

现有`DataQualityAnalyzer._log_control_flag_risks()`会在同一要货明细行：

```text
备货总控标识 != 发货总控标识
```

时生成：

```text
CONTROL_FLAG_MISMATCH
```

本次正式取消该异常。

实施后：

- 不再调用或删除该同步性检查；
- 异常清单不得再出现`CONTROL_FLAG_MISMATCH`；
- 不因为两个标识不同产生任何替代异常。

`是否解锁备货`规则不变，仍然只根据：

```text
备货总控标识
```

按现有三态聚合：

```text
无有效Y/N → 空
全部Y → 未解锁
全部N → 已解锁
Y/N混合 → 部分解锁
```

`发货总控标识`仍可以继续被源字段读取，但不再与备货标识做同步性异常校验。

非法枚举值等现有字段级异常不因本次取消同步性检查而取消。

---

## 7. 变化表和供应提拉表

本次不新增这三个金额字段到：

```text
RPD跨月变化
CPD跨月变化
供应需要提拉诉求清单粗表
```

这些表的字段契约保持现状。

但因为`遗留量 / 当月新订货`在多中心合同中只在深供行展示，为保持跨月变化和供应提拉金额口径与基表一致：

- 这些派生表如果直接消费BaseRow展示金额，则自然沿用深供规则；
- 不允许在派生表重新恢复合同级金额到非深供行；
- 不改变现有变化方向、月份差和不要货状态逻辑。

---

## 8. 配置修改

修改`config/default.json`：

1. `output.base_columns`加入三个字段并保持第3节顺序；
2. 三个字段仅是输出字段，不加入四类源文件`fields`；
3. 其他Sheet字段契约保持不变。

修改`src/revenue_tool/config.py`：

- `expected_base_ids`从32个更新为35个；
- 更新错误文字，不再写死“基表32个稳定字段”；
- 不改变其他源字段和Sheet契约。

metadata仍沿用当前schema 3即可，因为`_tool_meta`已经按`config.base_columns`写出稳定字段ID和显示名。

不为本次最小改动升级复杂metadata版本。

---

## 9. Writer修改

`ExcelOutputAdapter`：

### 9.1 金额格式

`amount_fields`扩展为：

```text
legacy_amount
monthly_new_order
revenue_forecast
manual_revenue_forecast_rpd
manual_revenue_forecast_cpd
```

### 9.2 黄色可编辑字段

`editable_fields`扩展为：

```text
manual_adjust_flag
manual_revenue_forecast_rpd
manual_revenue_forecast_cpd
manual_revenue_month
adjustment_note
```

保留现有AutoFilter、冻结首行和非人工字段斑马纹规则。

---

## 10. Reader和计算服务修改

### 10.1 `ExcelInputAdapter.read_previous()`

必须能够读取并继承`调整月份（按RPD）/调整月份（按CPD）`；上期`收入预测`不参与继承。

`_parse_previous_value()`：

将：

```text
manual_revenue_forecast_rpd
manual_revenue_forecast_cpd
```

按人工金额解析，但空白保持`None`，不能像源`legacy_amount/monthly_new_order`那样空白转0。

### 10.2 `RevenueEngine`

`_manual_values()`扩展为五个人工字段，不包含`revenue_forecast`。

多中心金额展示规则建议在合同中心分组确定后实现：

1. 保留`contract_values`中的真实合同金额；
2. 使用真实金额完成`_revenue_segment()`；
3. 确定多中心是否存在精确“深供”行；
4. 创建BaseRow时为非深供行覆盖显示：
   - `legacy_amount = ZERO_AMOUNT`
   - `monthly_new_order = ZERO_AMOUNT`
   - `revenue_forecast = ZERO_AMOUNT`
5. 其他行按最终展示的`legacy_amount + monthly_new_order`计算`revenue_forecast`；
6. 不修改收入分段使用的真实合同金额，避免影响同合同其他中心和业务计算。

无要货占位分支不修改金额。

### 10.3 `DataQualityAnalyzer`

移除：

```text
_log_control_flag_risks()
```

或至少停止从`analyze()`调用它。

测试必须证明不再生成`CONTROL_FLAG_MISMATCH`。

---

## 11. 不允许的实现

本次禁止：

- 恢复`refactor/revenue-allocation-v1`复杂模型；
- 新建合同金额事实Sheet；
- 新建收入分配Sheet；
- 新建RPD/CPD月度收入汇总Sheet；
- candidate ID / projection fingerprint；
- PreviousRunState；
- Posting；
- 新桌面双任务入口；
- 给`收入预测`写Excel公式；
- 从上期结果继承或人工覆盖`收入预测`；
- 根据人工预测金额改变收入年月；
- 根据展示归零后的金额重新计算收入分段；
- 多中心没有深供时擅自选择其他供应中心承载合同金额；
- 继续产生`CONTROL_FLAG_MISMATCH`或等价替代异常。

---

## 12. 必须新增/修改的测试

至少覆盖：

### 12.1 字段契约

- 基表35列表头和固定顺序；
- `收入预测`首次自动等于遗留量与当月新订货之和；
- `收入预测`不是黄色可编辑字段；
- `调整月份（按RPD）/调整月份（按CPD）`首次为空且黄色可编辑；
- 三个新增字段金额格式为两位小数；
- metadata包含三个新增稳定字段ID。

### 12.2 人工字段继承

- 上期`收入预测`不继承，本期重新计算；
- RPD人工预测继承；
- CPD人工预测继承；
- 正数、负数、明确0；
- 空白仍为空；
- 旧32列结果仍可作为previous；
- 旧结果缺新三列时不使跨期比较失效；
- 原三个人工月份字段继续回归通过。

### 12.3 深供金额规则

构造同一合同至少两个供应中心：

```text
深供
其他中心
```

验证：

- 深供行保留真实遗留量；
- 深供行保留真实当月新订货；
- 深供行收入预测等于两列之和；
- 其他中心三列均为0；
- 收入分段仍按真实合同金额计算；
- 单中心合同金额不变；
- 无要货占位金额不变。

再覆盖：

```text
多中心但无深供
```

验证：

- 不执行归零；
- 各行保持现有金额；
- 生成`MULTI_CENTER_DEEP_SUPPLY_NOT_FOUND`；
- 不丢失合同金额。

### 12.4 取消同步异常

构造：

```text
备货总控标识=Y
发货总控标识=N
```

以及反向组合。

验证：

- 异常清单不含`CONTROL_FLAG_MISMATCH`；
- `是否解锁备货`仍按备货总控标识正确聚合；
- 非法备货/发货枚举值的现有字段级异常仍按原规则处理。

### 12.5 全量回归

必须保证既有：

- 当月订货可选；
- 自动Sheet定位；
- 空白/VALUE；
- 海运周期；
- 七国；
- 不要货占位；
- 不要货跨期变化；
- 备货三态；
- RPD/CPD变化；
- 供应提拉；
- AutoFilter；
- GUI smoke

全部继续通过。

---

## 13. 建议WRITE_SCOPE

允许修改：

```text
config/default.json
src/revenue_tool/config.py
src/revenue_tool/services/calculation.py
src/revenue_tool/services/data_quality.py
src/revenue_tool/adapters/excel_reader.py
src/revenue_tool/adapters/excel_writer.py
相关tests/*
必要的实施验证文档
```

除非测试证明必要，不修改GUI和pipeline接口。

禁止引入新的领域架构层。

---

## 14. 验证命令

至少执行：

```text
PYTHONPATH=src python -m unittest discover -s tests
PYTHONPATH=src python -m compileall -q src tests
git diff --check
python -m pip wheel . --no-deps --wheel-dir <临时目录>/wheel
```

如有Windows构建工作流，继续执行GUI EXE smoke，但本次不需要新增复杂发布流程。

---

## 15. 完成标准

只有同时满足以下条件才能声明完成：

```text
基表=35列且顺序正确
收入预测自动等于最终展示的遗留量与当月新订货之和
收入预测不可编辑且不继承上期值
`调整月份（按RPD）/调整月份（按CPD）`首次为空并正确继承
明确0不会丢失
多中心+深供时只有深供行保留遗留量、当月新订货和收入预测
非深供行展示0但收入分段不受影响
多中心无深供时不丢金额并有明确异常
CONTROL_FLAG_MISMATCH完全停止生成
是否解锁备货三态保持正确
旧32列previous兼容
RPD/CPD跨期比较保持正确
全部测试通过
```

本次完成后即可直接生成新的测试EXE做真实数据和Windows Excel验收，不再启动收入分配架构重构。
