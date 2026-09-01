# 人工调整月份输入归一化实施验证

- 文档 ID：`MANUAL-REVENUE-MONTH-NORMALIZATION-VERIFICATION`
- 验证日期：`2026-09-01`
- 实施基线：`34014aae4dc94dbdb8cff45676f203c8f771f627`
- 最终代码实施提交：`b080b7bad96b212b5f02f400fdb8e1a7a5d3bbb6`
- 实施依据：`docs/implementation/manual-revenue-month-normalization.md`
- 结论：`PASS`

## 1. 修改文件

- `src/revenue_tool/services/normalization.py`
- `src/revenue_tool/adapters/excel_reader.py`
- `tests/test_normalization.py`
- `tests/test_manual_revenue_forecast.py`
- `docs/reviews/manual-revenue-month-normalization-verification.md`

未修改 Writer、自动到货日期、自动收入年月、收入分段、跨月变化、供应提拉、基表字段配置或 GUI。冻结分支 `refactor/revenue-allocation-v1` 未作为输入。

## 2. 归一化实现

新增独立纯函数 `normalize_manual_revenue_month()` 和结构化结果 `ManualMonthNormalizationResult`。结果状态为：

- `BLANK`：业务空白，结果为 `None`，不报异常；
- `NORMALIZED`：成功归一化为 `YYYY-MM`；
- `YEAR_REQUIRED`：仅有月份但年份无法唯一确定；
- `INVALID`：非空输入无法形成合法单一月份。

支持并已验证：

- 年月：`2026-09`、`2026-9`、`2026/9`、`2026.9`、`2026年9月`、`202609`；
- Unicode：`２０２６ 年 ９ 月`；
- 完整日期文本及 Python/Excel `date`、`datetime`；
- 英文旧格式：`Sep-26`、`Sep-2026`，使用程序内固定英文月份映射；
- 仅月份：`9`、`09`、`9月`、`09月`、`9月份`及整数数值；
- 数值年月：`202609`、`202609.0`。

新输出仍由现有 Writer 写为 `YYYY-MM`文本，单元格格式保持`@`，未出现`Sep-26`。

## 3. 最近年份和参考口径

RPD人工月份按“自动RPD月份优先、自动CPD月份回退”选择参考；CPD执行对称规则。只填写月份时，仅比较参考年份前一年、本年和后一年三个候选的月份距离，并且只接受唯一最近候选。

验证结果：

- `2026-12 + 1月 → 2027-01`；
- `2026-01 + 12月 → 2025-12`；
- `2026-11 + 2月 → 2027-02`；
- 同口径参考可用时不使用另一口径；同口径不可用时正确回退。

`2026-03 + 9月`存在六个月距离并列，结果为空并生成`MANUAL_MONTH_YEAR_REQUIRED`。两个自动月份都为空且只填写月份时同样不猜年份。完整年月不需要参考月份。

## 4. 空白、无效输入和异常

空单元格、空白字符、`(空白)`、`VALUE`、`#VALUE`和`#VALUE!`均按空白处理，不报异常。

`0月`、`13月`、非法年月、非法完整日期、范围文本、任意字符和非整数数值生成`INVALID_PREVIOUS_MANUAL_MONTH`。提示包含可填写示例、年份补全说明、合同号、履行供应中心、字段ID、原始值以及两套自动参考月份。

成功归一化不生成信息性异常。`MANUAL_MONTH_YEAR_REQUIRED`与真正无效输入保持独立。

## 5. 顺序无关读取

`ExcelInputAdapter.read_previous()`现在按以下阶段处理每行：

1. 依据稳定字段ID/显示名匹配结果缓存所有单元格；
2. 先解析合同号、履行供应中心及两套自动收入年月；
3. 使用已解析的自动月份归一化两个人工月份；
4. 解析其他人工字段并构造`PreviousData/BaseRow`。

因此人工月份解析不依赖Excel列顺序或配置遍历顺序。

## 6. Excel往返验证

自动化测试和独立工作簿检查均完成：

```text
生成结果
→ 将上期自动月份设置为RPD=2026-06、CPD=2026-07
→ 用户填写RPD=9月、CPD=数值10
→ 保存为上一次结果
→ 重新运行生产pipeline
→ 新结果继承为RPD=2026-09、CPD=2026-10
```

同时验证：

- 移动人工月份列到表尾；
- 插入非关键列；
- metadata字段ID对应的显示名变化；
- 删除metadata后的旧显示名别名；
- 输出单元格继续为黄色可编辑区域，格式为`@`；
- 36列基表字段数量、名称和顺序不变；
- 5个可见Sheet可以独立解析和渲染；
- 工作簿公式错误扫描为0。

## 7. 全量验证

```text
PYTHONPATH=src python -m unittest discover -s tests
```

结果：`109/109 PASS`。

```text
PYTHONPATH=src python -m compileall -q src tests
```

结果：`PASS`。

```text
git diff --check
```

结果：`PASS`。

```text
python -m pip wheel . --no-deps --wheel-dir <临时目录>/wheel
```

结果：`PASS`，生成`excel_arrival_tool-0.8.4-py3-none-any.whl`。

全量回归覆盖自动收入年月、跨月变化、`REVENUE_MONTH_ONE_SIDE_MISSING`、旧32/35列结果和现行36列结果继承。

## 8. 剩余风险

- 未在实施文档中列出的任意本地化日期文本不会被猜测，按无效输入提示用户填写标准年月；这是受控边界。
- 普通数值不会按Excel日期序列猜测；只有工作簿读取后明确表现为日期/日期时间的单元格才按日期处理，避免把编号误判为月份。
- 仍建议用真实业务上期结果补充桌面Excel人工验收，但不存在已知代码阻塞项。

## 9. Gate结论

`PASS`。文档规定的输入兼容、唯一最近年份、歧义保护、异常分类、列顺序独立、旧结果兼容、文本输出和全量验证均已满足。
