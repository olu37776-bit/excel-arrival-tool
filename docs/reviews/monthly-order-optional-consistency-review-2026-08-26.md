# 当月订货可选化一致性审查

- 审查 ID：`MONTHLY-ORDER-OPTIONAL-REVIEW-2026-08-26`
- 日期：`2026-08-26`
- 状态：`REVIEWED`
- 审查范围：
  - `docs/requirements-baseline.md` 0.6
  - `docs/source-schema.md` 0.9
  - `docs/output-schema.md` 1.2
  - `docs/decisions/DR-003-monthly-order-source-optional.md`

## 1. 结论

当月订货业务角色已经从“必选源文件”调整为“可选源文件”。

统一口径为：

```text
遗留量          必选
当月订货        可选
要货明细        必选
国家运输周期    必选
```

当月订货整个文件未提供属于正常业务状态，不报异常、不阻止运行。

## 2. 文件缺失时的统一结果

- `monthly_order`不读取；
- 不定位Sheet；
- 不匹配字段；
- 当月新订货=0；
- BG跳过当月订货来源；
- 合同全集=遗留量∪要货明细；
- 不产生缺少当月订货文件的异常。

## 3. 文件存在时的统一结果

- 使用统一SheetLocator扫描所有Sheet；
- 不依赖“当月订货”固定Sheet名；
- `Sheet2`、`Sheet3`等自动名称必须可识别；
- 合同全集恢复为遗留量∪当月订货∪要货明细；
- 合同无匹配时当月新订货=0且不报异常。

## 4. 关键边界

“文件未提供”和“文件已提供但无法识别”必须分开：

```text
未提供 → 正常，无异常
已提供但无业务Sheet/字段歧义 → 有异常证据
```

不能为了可选化而把损坏或错误文件静默吞掉。

## 5. 当前代码与文档的已知偏差

当前`main`代码仍存在以下偏差，后续独立会话需要修复：

1. GUI仍把当月订货放在required列表；
2. `run_pipeline(monthly_order_path)`仍是必填参数；
3. `SourceFiles`仍按四个Path处理；
4. `config/default.json`中`monthly_order.optional=false`；
5. `config.py`强制四个角色的optional都必须false；
6. 输入读取循环当前默认四个角色都有路径；
7. 源文件互斥校验需要忽略None；
8. 测试需要新增“整个文件未提供”场景。

## 6. 验收结论

```text
需求语义：已闭合
文档一致性：通过
代码一致性：未通过，待后续修复
是否修改代码：否
```
