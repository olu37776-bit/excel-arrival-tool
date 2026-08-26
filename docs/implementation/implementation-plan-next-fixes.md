# 下一轮集中修复实施计划

- 文档 ID：`IMPLEMENTATION-PLAN-NEXT-FIXES`
- 状态：`READY_FOR_IMPLEMENTATION`
- 日期：`2026-08-26`
- 实施基线：仓库最新`main`
- 当前开放Issue：`#13`、`#17`
- 回归参考Issue：`#6`、`#9`、`#10`、`#11`

## 1. 目标

基于当前已完成的代码继续修复两项最新业务变化：

1. 无要货合同的`有要货 ↔ 不要货`状态必须稳定进入RPD/CPD跨期变化清单；
2. `是否解锁备货`从原始Y/N拼接改为`未解锁/部分解锁/已解锁`三态。

本轮不是重新实现此前全部功能。已关闭的Issue #6/#9/#10/#11作为回归约束，不能因本轮修改而退化。

## 2. 权威输入

实施前必须读取：

1. `docs/requirements-baseline.md`
2. `docs/source-schema.md`
3. `docs/output-schema.md` 1.3或更高
4. `docs/comparison-output.md` 0.5或更高
5. `docs/decisions/DR-001-manual-adjustment-fields.md`
6. `docs/decisions/DR-002-amount-arrival-segment-normalization.md`
7. `docs/decisions/DR-003-monthly-order-source-optional.md`
8. `docs/decisions/DR-004-country-filter-and-transit-diagnostics.md`
9. `docs/decisions/DR-005-retain-contract-without-demand-detail.md`
10. `docs/decisions/DR-006-no-demand-cross-period-visibility.md`
11. `docs/decisions/DR-007-stock-unlock-three-state-output.md`
12. Issue #13、#17

优先级：

```text
DR-007 / DR-006 / DR-005
> output-schema / comparison-output
> 较旧基线文字
> 当前代码与测试
```

## 3. 当前实现差异

### 3.1 不要货跨期变化

当前比较器已排除本期`CONTRACT_ONLY_NO_DEMAND`占位行，再按精确业务键比较月份。

该实现存在两个问题：

- 上期真实中心月份为空、本期变为不要货时，无法发现状态变化；
- 上期不要货、本期恢复真实中心但本期月份为空时，也无法发现状态变化。

必须增加合同级状态转换比较。

### 3.2 是否解锁备货

当前计算逻辑收集`stock_control_flag`后使用分隔符拼接，可能输出：

```text
Y|Y|N
```

该输出已废止，需要替换为三态聚合。

## 4. WRITE_SCOPE

允许修改：

- `config/default.json`
- `src/revenue_tool/config.py`
- `src/revenue_tool/domain/models.py`
- `src/revenue_tool/adapters/excel_reader.py`
- `src/revenue_tool/adapters/excel_writer.py`
- `src/revenue_tool/services/calculation.py`
- `src/revenue_tool/services/comparison.py`
- `src/revenue_tool/services/normalization.py`
- 相关测试和虚构fixture
- `README.md`中确有必要的用户说明
- `docs/reviews/implementation-verification-next-fixes.md`

如需新增小型领域类型、状态恢复器或聚合策略文件，可以新增。

不得修改已确认业务规则，不得提交真实业务Excel或真实业务数据。

## 5. 实施项A：不要货状态跨期可见

### 5.1 状态恢复

本期行已有显式`row_kind`。

上期结果读取必须恢复每行状态：

- 新格式：读取隐藏系统数据中的`row_kind`或等价状态；
- 旧格式兼容：`履行供应中心为空 + 收入分段类别=不要货`时识别为`CONTRACT_ONLY_NO_DEMAND`。

新生成结果必须持久化显式状态，不能继续只靠旧格式推断。

### 5.2 合同级状态比较

比较器先按合同聚合：

```text
HAS_DEMAND = 存在DEMAND_CENTER行
NO_DEMAND = 存在CONTRACT_ONLY_NO_DEMAND行
```

同一期同合同同时出现两种状态时，记录内部状态冲突异常，不静默选择。

### 5.3 变为不要货

```text
上期HAS_DEMAND + 本期NO_DEMAND
```

RPD和CPD清单均对每个上期真实中心输出：

- 变化方向=`变为不要货`；
- 上期月份允许为空；
- 本期月份为空；
- 变化月数为空。

### 5.4 恢复要货

```text
上期NO_DEMAND + 本期HAS_DEMAND
```

两张清单均对每个本期真实中心输出：

- 变化方向=`恢复要货`；
- 上期月份为空；
- 本期月份允许为空；
- 变化月数为空。

### 5.5 防重复

状态变化优先于普通新增/取消。

已由`变为不要货/恢复要货`覆盖的中心键，不再输出普通新增或取消。

两期均不要货不输出。无要货占位行继续排除在供应提拉清单之外。

## 6. 实施项B：是否解锁备货三态

按同一合同+履行供应中心，在完全重复明细去除后收集有效Y/N：

```text
无有效值 → 空
有效集合={Y} → 未解锁
有效集合={N} → 已解锁
有效集合={Y,N} → 部分解锁
```

要求：

- 空白/VALUE忽略；
- 非空非法标识记录异常并排除；
- 同行备货/发货总控标识不一致异常继续保留；
- 最终状态仅由备货总控标识决定；
- 无要货占位行为空；
- 删除/废弃`stock_flag_delimiter`及拼接代码；
- 中文三态文案集中定义，不散落在Writer或GUI。

## 7. 自动测试

### 7.1 不要货跨期

至少覆盖：

- 上期真实中心月份有值、本期不要货；
- 上期真实中心月份为空、本期不要货；
- 上期多中心、本期不要货；
- 上期不要货、本期真实中心月份有值；
- 上期不要货、本期真实中心月份为空；
- 两期均不要货；
- 状态变化不重复普通新增/取消；
- 旧结果兼容识别；
- 新结果显式状态可恢复；
- 无要货占位行不进入供应提拉清单。

### 7.2 解锁备货

至少覆盖：

- 单个Y、多个Y；
- 单个N、多个N；
- Y/N混合及不同顺序；
- 完全重复行；
- 全空；
- 空白/VALUE；
- 有效值与非法值混合；
- 无要货占位行；
- 最终Excel不再出现Y|N拼接。

### 7.3 全量回归

运行项目全部测试，不只跑新增测试。

重点回归：

- 当月订货文件可选；
- Sheet2/Sheet3字段定位；
- 七国结转；
- 海运周期异常分型；
- Excel筛选输出；
- 金额Decimal精度；
- 货未发完和到货日期；
- 三个人工字段继承。

## 8. 验证与Issue状态

- Issue #13：只有基表不要货、收入分段显式状态、RPD/CPD状态变化和测试全部通过后才可关闭；
- Issue #17：只有三态输出、配置清理和测试通过后才可关闭；
- 已关闭Issue #6/#9/#10/#11不得在本轮重新出现回归。

## 9. 产物

实施会话必须：

1. 从最新main创建独立分支；
2. 完成代码、配置和测试；
3. 创建代码PR；
4. 新增：

```text
docs/reviews/implementation-verification-next-fixes.md
```

验证报告至少包含：

- 修改文件；
- 规则到代码映射；
- 测试命令和结果；
- Issue #13/#17验收证据；
- 已关闭Issue回归结果；
- 仍需本地Excel验证的事项。

## 10. 完成标准

只有同时满足以下条件才可声明完成：

- `变为不要货/恢复要货`在RPD和CPD清单稳定可见，月份为空也不漏；
- 不产生重复普通新增/取消；
- 上期状态可可靠恢复；
- 三态解锁输出完全替代Y/N拼接；
- 全量自动测试通过；
- 验证报告已提交；
- PR说明包含实施摘要、测试结果和剩余风险。
