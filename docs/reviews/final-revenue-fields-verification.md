# Issue #36 最终收入字段验证

## 基线与范围

- 实施基线：main `ffb0e00c560eb5dda56275e14c795a5ab58dd878`。
- 修复分支：`fix/issue-36`；最终提交由本报告所在PR的提交记录确定（不写自引用SHA）。
- 依据：Issue #36正文及实时更新补充、`manual-revenue-month-normalization.md`；未读取或修改冻结重构分支。
- 版本预置0.8.7，避免未来合并后覆盖已发布的0.8.6；本次不合并、不发布正式Release。README下载仍指向实际已发布版本。

## 实施结果

新增`final_revenue_segment`、`final_revenue_month_rpd`、`final_revenue_month_cpd`、`final_revenue_forecast`。40列顺序由配置及校验器固定，原自动列位置不变，尾部严格采用Issue顺序。

`services/final_revenue.py`在人工值继承后独立计算最终值；`adapters/final_revenue_formulas.py`生成同一优先级的无宏同行Excel公式。人工实际值优先、业务空白回退；不引用是否手工调整预测。保留0/False，金额ROUND_HALF_UP两位小数，Excel侧ROUND保持一致。VALUE错误标记按空白处理。

月份实时支持9/09/9月/09月/9月份/10/10月/YYYY-M/YYYY-MM，两个口径对称；参考同口径优先、另一口径回退、前后一年唯一最近月份。无参考、半年并列显示补全年份提示；非法值显示可操作修正提示。Python完整归一化（含日期、Sep-26等）不变；Excel实时最小语法之外的写法建议改填YYYY-MM。输入无效时，不输出伪月份；下次读取保留既有异常和空白回退规则。

Excel开启auto/fullCalcOnLoad/forceFullCalc；最终列非黄色，月份`@`、金额`#,##0.00`。基表无密码保护，黄色单元格解锁，最终公式锁定；普通AutoFilter保留，不使用Structured Table。移动列、整表排序或受Excel保护限制的“数据→清除”操作需先“审阅→撤销工作表保护”；这项取舍落实Issue明确的最终列不可编辑要求，不隐藏操作限制。透视表需用户手动刷新。

上期读取跳过全部最终字段，不读取它们的缓存或被人为改写的值；metadata保留四个字段ID。32/35/36列结果兼容，40列无缓存、列移动、显示名变更、插入非关键列仍继承真正人工值。跨月变化继续比较自动月份，供应提拉、日期、收入分段、深供金额承载、GUI流程不变。

## 修改文件

- `config/default.json`、`src/revenue_tool/config.py`：40列字段契约。
- `src/revenue_tool/services/final_revenue.py`、`calculation.py`：内部最终值计算。
- `src/revenue_tool/adapters/final_revenue_formulas.py`、`excel_writer.py`：实时公式、格式、保护与自动重算。
- `src/revenue_tool/adapters/excel_reader.py`：最终字段不继承。
- `tests/test_final_revenue.py`、`test_manual_revenue_forecast.py`、`test_pipeline.py`：新验收与旧格式回归。
- `.github/workflows/build-windows-exe.yml`：PR全量测试、独立公式重算、Windows EXE smoke；PR不发布Release。
- `pyproject.toml`、`src/revenue_tool/__init__.py`：预置0.8.7。
- `docs/output-schema.md`、`docs/requirements-baseline.md`、`docs/decisions/DR-001-manual-adjustment-fields.md`及本报告：同步规则与验证。

## 验证证据

新增5个测试方法，独立LibreOffice重算362组虚构输入，分别编辑和清空四个人工源字段，逐项比较4个最终值：共2,896次Python/公式结果比较。含两个口径12个参考月份×12个人工月份、跨年、并列、无参考、回退、金额正负和0、分段0/False、业务空白、非法值、半年边界。布尔输入fixture使用General格式，防止LibreOffice导入数值格式时预先把布尔转为数字；不是忽略差异。

实际xlsx往返覆盖旧36列、新40列无公式缓存、新最终值被改写、旧32/35列、metadata显示名变更和列移动；明确0/False保留，原始人工值继承正确，跨月变化不因最终列变化而增加。

在仓库根目录执行：

```bash
PYTHONPATH=src REQUIRE_FORMULA_ENGINE=1 python -m unittest discover -s tests
python -m compileall -q src tests
git diff --check
python -m pip wheel . --no-deps --wheel-dir /tmp/issue36-wheel.6SbDDZ/wheel
python -m pip wheel . --no-deps --no-build-isolation --no-index --wheel-dir /tmp/issue36-wheel.6SbDDZ/wheel
PYTHONPATH=src python -m revenue_tool.gui --smoke-test
```

本地结果：全量116项通过（包含真实公式引擎测试，无跳过），compileall、diff check、wheel与GUI smoke通过。`REQUIRE_FORMULA_ENGINE=1`确保缺少独立重算引擎时失败，不静默跳过。Windows构建环境可跳过独立LibreOffice测试，由并行Linux作业强制承担该门禁。

标准wheel命令在改版本号前通过；最终0.8.7重建时依赖联网授权取消，因此使用已安装构建依赖执行上述无网络命令成功，未绕过授权。最终wheel SHA-256：`ed34e4df6727704d54fa47998db223dd1bbc69d2af5199872a555e6f98319871`。PR Linux作业仍执行标准隔离构建命令。

GitHub Actions和Windows EXE：提交后由PR运行Linux全量/重算与Windows全量/EXE smoke；运行链接与最终状态在PR验证记录更新，未运行前不视为通过。测试Artifact带版本及提交SHA，不冒充正式发布。

## 门禁与待实机验证

- 本地代码/工作簿自动验证：PASS。
- PR CI及Windows EXE smoke：以PR检查记录为准。
- Windows桌面Excel实时编辑、工作表保护交互、撤销保护后的筛选清除及透视刷新：PENDING_LOCAL_EXCEL_VALIDATION。LibreOffice重算不能冒充Windows桌面Excel验收。
- 真实业务源文件需本地复核。本次只使用虚构fixture，不上传真实业务数据。
- 未修改或合并冻结的收入分配重构分支；未实现额外月度汇总、金额分配或GUI重构。
