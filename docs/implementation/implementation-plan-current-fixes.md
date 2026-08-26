# 当前缺陷实施计划

- 文档 ID：`IMPLEMENTATION-PLAN-CURRENT-FIXES`
- 状态：`READY_FOR_IMPLEMENTATION`
- 日期：`2026-08-26`
- 实施基线：仓库 `main`
- 关联 Issue：`#6`、`#9`、`#10`、`#11`、`#13`

## 1. 任务目标

在一个独立实施分支中，对当前 Excel 到货与收入月份工具进行一次集中修复，使代码、配置、测试和用户可见结果符合最新需求与决策文档。

本阶段不是重新设计业务规则，也不是单纯修补某个结果单元格。需要修复源文件输入、Sheet定位、领域状态、收入分段、国家匹配、海运周期异常和Excel输出可用性之间的完整链路。

## 2. 权威输入及优先级

实施前必须读取：

1. `docs/requirements-baseline.md`
2. `docs/source-schema.md`
3. `docs/output-schema.md`
4. `docs/comparison-output.md`
5. `docs/decisions/DR-001-manual-adjustment-fields.md`
6. `docs/decisions/DR-002-amount-arrival-segment-normalization.md`
7. `docs/decisions/DR-003-monthly-order-source-optional.md`
8. `docs/decisions/DR-004-country-filter-and-transit-diagnostics.md`
9. `docs/decisions/DR-005-retain-contract-without-demand-detail.md`
10. Issue `#6`、`#9`、`#10`、`#11`、`#13`

优先级：

```text
业务方最新决策 / 编号更后的DR
> requirements/source/output/comparison基线中的旧描述
> 当前代码、配置和测试
```

特别说明：`DR-005`已明确取代“要货明细没有合同就记录异常并丢行”的旧规则。

## 3. 必须完成的功能范围

### 3.1 当月订货整个源文件可选

依据`DR-003`：

- GUI允许不选择当月订货文件；
- Application接口和`SourceFiles`允许`monthly_order=None`；
- 配置中仅`monthly_order.optional=true`；
- 未提供时不打开文件、不定位Sheet、不报异常；
- 合同全集使用遗留量∪要货明细；
- 所有正常行当月新订货为规范化数值0；
- BG跳过当月订货来源；
- 提供文件后按真实数据处理，不能把解析失败伪装成未提供。

### 3.2 四类源文件统一按字段契约定位业务Sheet

依据Issue #6：

- Sheet名只作优先提示；
- 扫描工作簿所有Sheet和候选表头行；
- 通过该业务角色的required fields识别；
- `Sheet1/Sheet2/Sheet3`等自动名称必须支持；
- 多候选产生`AMBIGUOUS_SHEET_ROLE`；
- 无候选产生包含实际Sheet列表和缺失字段的明确异常；
- 不得因第一个Sheet不匹配就放弃整个文件；
- 四类角色共享统一机制，不写当月订货特判。

### 3.3 七国结转类型可靠匹配

依据Issue #9和`DR-004`：

- 结转类型只使用遗留量自身国家；
- 七国名单不变；
- 建立国家identity规范化，至少处理NFKC、普通/全角空白、换行、制表符和常见零宽/格式控制字符；
- 合法别名只通过显式alias映射；
- 阿拉伯联合酋长国、沙特阿拉伯必须作为固定回归用例；
- 非七国不得误匹配。

### 3.4 Excel筛选后支持“数据→清除”

依据Issue #10和`DR-004`：

- 基表、RPD跨月变化、CPD跨月变化、供应需要提拉诉求清单粗表、异常清单均需支持；
- 任意单列或多列筛选后，Windows桌面版Excel的`数据→清除`可一次恢复全部行；
- 表头筛选下拉继续存在；
- 不能破坏冻结首行、样式、列顺序、日期/金额格式和人工列可编辑性；
- 是否保留Structured Table由实现决定，最终以桌面Excel行为验收。

### 3.5 海运周期异常必须可追溯

依据Issue #11和`DR-004`：

- FCA/FOB/EXW直接5天；
- 其他术语按国家+履行供应中心查表；
- 国家缺失：`TRANSIT_COUNTRY_MISSING`；
- 国家和中心存在但周期表无组合：`TRANSIT_NOT_FOUND`；
- 组合存在但周期为空/VALUE/无可用值：`TRANSIT_VALUE_UNAVAILABLE`；
- 非空非法周期：`INVALID_TRANSIT_DAYS`；
- 异常应带合同号、国家、履行供应中心、查找组合/原值和明确原因；
- 同一业务键同一根因不重复报噪声异常。

### 3.6 无要货明细合同保留，并显式分类为不要货

依据Issue #13和`DR-005`：

```text
合同进入全集
且要货明细中该合同匹配记录数=0
→ 生成一条合同占位行
→ 收入分段类别=不要货
```

必须实现：

- 内部显式状态，例如`row_kind=CONTRACT_ONLY_NO_DEMAND`；
- 业务键允许受控的合同号+空履行供应中心；
- 合同级字段正常填写；
- 履约字段、海运周期、日期、到货日期和收入年月为空；
- 多个供应中心发货、分批发货、多次要货、分批供应均为N；
- 不产生合同未找到、供应中心缺失或海运周期异常；
- 收入分段策略首先识别该显式状态并直接返回`不要货`；
- 不得仅依赖ATA/ASD/RPD/CPD全空的偶然结果；
- 即使遗留量或当月新订货非0，也仍为`不要货`；
- 要货明细存在合同但供应中心为空时，不套用该正常状态。

### 3.7 回归既有最新规则

修复不得破坏：

- 金额使用`Decimal(str(value))`、两位小数、`ROUND_HALF_UP`；
- 空白、`(空白)`、VALUE占位的既有安静规范化；
- 货未发完门控后的两套到货日期；
- 收入分段的`需判断/发未收/未录入订货/订未发/不要货`；
- 三个人工字段继承；
- RPD/CPD变化清单及供应差异清单。

## 4. 建议WRITE_SCOPE

允许修改：

- `config/default.json`
- `src/revenue_tool/config.py`
- `src/revenue_tool/gui.py`
- `src/revenue_tool/application/pipeline.py`
- `src/revenue_tool/domain/models.py`
- `src/revenue_tool/adapters/excel_reader.py`
- `src/revenue_tool/adapters/sheet_locator.py`
- `src/revenue_tool/adapters/excel_writer.py`
- `src/revenue_tool/services/normalization.py`
- `src/revenue_tool/services/calculation.py`
- `src/revenue_tool/services/comparison.py`
- 相关测试、虚构fixture、README使用说明
- 实施验证报告

如需新增小型领域类型、策略或适配器文件，可以新增，但不得引入Web服务、数据库或不必要框架。

不得提交真实业务Excel或真实业务数据。

## 5. 实施顺序

1. 审查当前main实现与上述文档/Issue差异；
2. 先修领域模型和输入契约：可选源、row_kind、SourceFiles；
3. 修Sheet定位和输入适配；
4. 修合同集合与无要货占位行；
5. 修收入分段显式优先规则；
6. 修国家identity和七国匹配；
7. 修海运周期异常分型；
8. 修Excel筛选输出行为；
9. 补全单元、集成和工作簿契约测试；
10. 运行全量测试，生成验证报告和PR。

不要把所有修复继续堆进一个大函数。输入识别、规范化、领域状态、分类策略、异常生成和写出行为应保持现有分层并进一步解耦。

## 6. 验证计划

### 6.1 自动测试

至少覆盖：

- 当月订货未选择/有效/错误文件；
- 业务Sheet位于Sheet2；
- 多候选Sheet和无匹配Sheet；
- 七国逐一匹配、空白/不可见字符、非七国；
- 普通运输周期命中、无组合、空周期、非法周期、国家缺失；
- 无要货明细且金额为0；
- 无要货明细且金额非0，仍为不要货；
- 有合同但供应中心为空，不误当不要货；
- 人工字段继承和空中心占位键；
- 占位行不进入三张变化/差异清单；
- 金额浮点精度边界和现有日期规则回归；
- 输出五个Sheet表头、列顺序、筛选范围和格式。

### 6.2 运行验证

执行项目定义的全部测试、静态检查和打包烟雾测试。不得只跑新增测试。

### 6.3 Windows Excel实机验证

Issue #10必须使用Windows桌面版Excel验证：

- 单列筛选；
- 多列筛选；
- `数据→清除`；
- 保存关闭后重新打开再验证。

若当前执行环境无法进行实机操作，自动测试不得冒充实机通过。PR中应明确标记`PENDING_LOCAL_EXCEL_VALIDATION`，并给出本地复验步骤。

## 7. 完成标准

只有同时满足以下条件才能声明实施完成：

- 所有范围代码已修改；
- Issue #6/#9/#10/#11/#13均有对应测试或验证证据；
- 全量自动测试通过；
- 代码与配置没有继续把当月订货强制为必选；
- 无要货占位行由显式领域状态驱动；
- 未关闭的本地Excel实机验证被明确列出；
- PR说明包含实现摘要、测试命令、结果、遗留风险和本地复验步骤。

## 8. 实施产物

实施会话应提交：

1. 一个实施分支；
2. 一个代码PR；
3. 代码、配置和测试；
4. `docs/reviews/implementation-verification-current-fixes.md`；
5. PR最终回执：已修复Issue、测试结果、未完成的实机验证、变更文件和已知风险。
