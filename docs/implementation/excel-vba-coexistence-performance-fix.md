# Issue #52：Excel结果工作簿与其他工作簿VBA脚本共存性能修复

- 状态：`READY_FOR_IMPLEMENTATION`；用户现场根因尚待实机对照，不等于已修复。
- 日期：2026-09-09。
- 仓库：`olu37776-bit/excel-arrival-tool`。
- 目标：在当前 `main` 上最小修复；`refactor/revenue-allocation-v1`继续冻结。
- 调查代码基线：`158b9f56a1a75b11d423ec670d0e8b7c810366ec`，v0.11.3代码线。
- 问题：[Issue #52](https://github.com/olu37776-bit/excel-arrival-tool/issues/52)。
- 最终验证报告：`docs/reviews/excel-vba-coexistence-performance-verification.md`。

本文件是该修复的直接实施入口。不新增架构方案、子阶段计划或额外业务字段。先完成确定的小范围修复和对照验证，再根据测量决定是否继续精简透视辅助数据；不要一开始重建整个收入工具。

## 1. 已确认现象与未确认事项

用户确认：工具生成的结果表打开时，运行操作另一个工作簿的VBA脚本后，Excel卡住；不打开工具结果时，同一脚本正常。**不是仅按Alt+F11打开编辑器时卡住。**

尚未取得原脚本、问题工作簿、准确EXE版本、Excel版本/位数、PID和耗时数据。同一Excel实例是首要复现场景，实际进程关系需要记录。不能把代码风险直接写成唯一根因，也不能宣称已经复现死锁。

需要区分：持续计算导致界面暂不响应、内存压力、真正挂起/退出、脚本误操作活动工作簿。与#47的上期透视缓存读取异常不是同一个已证实故障；与#45的实时计算问题有关联，但不得因此顺带关闭#45/#47。

## 2. 代码事实

### 2.1 强制全量重算设置

[excel_writer.py（调查基线）](https://github.com/olu37776-bit/excel-arrival-tool/blob/158b9f56a1a75b11d423ec670d0e8b7c810366ec/src/revenue_tool/adapters/excel_writer.py)创建工作簿时写入：

```python
CalcProperties(
    calcMode="auto",
    fullCalcOnLoad=True,
    forceFullCalc=True,
    calcOnSave=True,
)
```

正常自动计算、打开时首次全量计算、每次强制全量重算是不同机制。微软说明，`ForceFullCalculation=True`会关闭智能重算，并可使每次重算涉及所有打开工作簿的全部公式；其影响可能持续到Excel重启。[官方依据A/B见末节]

因此，即使宏操作另一个工作簿，也可能触发本结果的大量额外计算。这是高优先级解释，不是现场复现结论。

### 2.2 透视辅助公式规模

[regional_pivot.py](https://github.com/olu37776-bit/excel-arrival-tool/blob/158b9f56a1a75b11d423ec670d0e8b7c810366ec/src/revenue_tool/adapters/regional_pivot.py)和[regional_summary.py](https://github.com/olu37776-bit/excel-arrival-tool/blob/158b9f56a1a75b11d423ec670d0e8b7c810366ec/src/revenue_tool/services/regional_summary.py)构造：

- 两张原生透视：`RPD地区收入汇总`、`CPD地区收入汇总`；
- 一个隐藏源表：`_summary_source`；
- 一条基表记录对应RPD分类、RPD小计、CPD分类、CPD小计四条辅助记录；
- 每条辅助记录引用所有基表列，再生成地区、月份、汇总项目三个公式。

设业务行数为N、基表列数为C、有效月份数为M。存在有效月份、正常生成透视时，当前实现：

```text
辅助数据记录数 = 4N + 5M
辅助公式数     = 4N × (C + 3)
基表最终公式数 = 4N
当前C=40，总公式数约176N
N=10,000时约1,760,000个公式
```

5M是静态布局种子记录，不是额外业务收入。上述为代码推导，不是用户文件实测；空表或无有效月份的分支不适用这个数量。

公式数量不是唯一性能指标：还应测公式文本总长度、引用数量、依赖重建、缓存体积及Excel内存。尤其两个最终月份公式含重复的文本解析表达式，不能仅凭公式格数评价优化。

### 2.3 没有证据证明透视刷新死循环

当前两张透视共用缓存，设置为`refreshOnLoad=False`、`backgroundQuery=False`。不能把隐藏源表重算与原生透视刷新混为一谈。

[formula_cache.py](https://github.com/olu37776-bit/excel-arrival-tool/blob/158b9f56a1a75b11d423ec670d0e8b7c810366ec/src/revenue_tool/adapters/formula_cache.py)目前给基表最终公式补初始缓存，但不等于整个隐藏源表都有完整缓存。不能为了缩短打开时间，一并关闭必要的首次计算而交付空白/过期数据。

## 3. 修复必须保留的业务能力

- 四个最终字段仍是实时公式。用户修改人工类别、月份、金额后，在自动计算模式下立即更新，无需重新运行EXE或手动F9。
- 保留人工值优先、空白回退、0/False不丢失、负数金额、月份简写和跨年归一化的现行规则。
- 保留基表字段、顺序、源数据计算、金额承载、人工继承、异常和三张辅助清单的既有语义。
- 保留两张原生透视、按实际月份横向排列、订未发/发未收/交未验/其他/小计、地区小计和双击金额查看明细。
- 保留用户编辑、筛选、排序、移动列及自行创建透视的能力；不增加保护限制。
- 保留现有“最终公式先更新，用户刷新透视后汇总更新”的流程，不添加每次键入自动刷新透视。
- 输入中的用户透视不需要继承，但本工具自己生成的两张汇总仍需保留；继续执行只读输入与同页透视区域隔离。

禁止以永久手动计算、删除最终公式、删除透视表、锁死基表、引入VBA事件或宏工作簿、要求修改用户原脚本，作为本问题的默认修复。

## 4. 优先实施：取消强制全量重算

### 4.1 最小代码修改

首先只修改创建输出工作簿的计算策略，建议明确写：

```python
CalcProperties(
    calcMode="auto",
    fullCalcOnLoad=True,
    forceFullCalc=False,
    calcOnSave=True,
)
```

第一轮保留`fullCalcOnLoad=True`保障初次打开计算，保留正常自动计算和保存计算；只取消`forceFullCalc=True`，便于单独确认这一变量的影响。不要同时改动业务公式和透视布局后就声称找到了唯一根因。

必须检查最终ZIP内`xl/workbook.xml`的`calcPr`，而非只断言Python对象属性。还要检查Excel打开及保存后没有被其他保存路径重新写成强制全算。

### 4.2 不改变用户整个Excel会话

输出文件保留自动计算意图，但程序不得后台控制用户现有Excel进程、修改其他工作簿属性或通过宏切换全局设置。Excel实际计算模式受同实例其他文件及打开顺序影响，验收必须记录`Application.Calculation`，不能因为XML写了auto就假定实机始终auto。[官方依据B]

不新增`CalculateFull`/`CalculateFullRebuild`来“保障实时”。正常依赖计算才是实时更新的路径。

### 4.3 先验证最小修复，再决定继续优化

先生成仅取消强制全算的版本，与原版做第7节对照。如果已经解决宏共存问题且实时公式、透视刷新正确，本轮可以按最小补丁收口，不为追求减少每一个公式扩大重构。

如果仍明显卡顿，则进入第5节测量与针对性优化。修改代码和执行验证无需再创建下一阶段文档。

## 5. 辅助公式精简：由测量驱动，不能制造旧数据

### 5.1 先输出机器可读规模数据

新增`tests/test_excel_calculation_policy.py`和`tests/test_workbook_formula_footprint.py`或复用同职责测试，统计最终生成文件：

```text
业务N / 有效月份M / 基表C
各Sheet实际行列数、公式数、公式文本总长度
_summary_source公式数
透视数量、缓存数量、recordCount及XML字节数
输出文件字节数、生成耗时
```

分别覆盖空数据、无有效月份、1,000行、10,000行；更大规模按已知业务规模及机器资源选取，不能把Excel行数上限当成可接受性能上限。大样本可作为单独基准而非每次单元测试都跑。

当前基线正常路径应能核验176N公式；优化后固定新的公式预算和实际值，避免后续又恢复四倍全字段复制。不能只测压缩文件大小。

### 5.2 可采用的优化方向

优先减少重复表达式、重复合法月份检查和无必要的全字段公式复制；如果要采用原生小计代替业务行复制，必须先证明分类、小计、筛选及双击明细行为等价。保留共用缓存，不因拆表重复建立大缓存。

只允许将**不会因用户允许的编辑而变化**的信息写成静态值。不能直接把辅助表所有非黄色字段都静态化：基表允许排序、移动行列及业务编辑，物理行号不是跨编辑稳定身份。

任何静态化方案都须通过：编辑某合同 → 排序 → 刷新 → 双击明细，检查合同号、供应中心、类别、月份、金额仍属于同一条记录。不能出现“新金额配旧合同信息”。也不能让小计人为复制的金额误进分类统计。

如尚无可证明等价的精简方式，保留现有结构、记录剩余规模风险，不删除功能冒充优化成功。若最小修复仍未通过，则Issue保持待修状态。

### 5.3 不引入新的计算负担

- 不为每次输入增加透视自动刷新、外部链接、事件监听或VBA。
- 不用OFFSET/INDIRECT等易变引用替代现有行内引用；不把有限数据范围改成整列/整表扫描。
- 不靠反复要求用户清缓存或重装Excel处理可由输出结构修复的问题。
- 不关闭首次计算来掩盖无缓存公式；如后续优化`fullCalcOnLoad`，必须单独证明全工作簿首开、刷新前后及保存重开的值正确。

## 6. 实施范围

允许直接修改的核心文件：

```text
src/revenue_tool/adapters/excel_writer.py
src/revenue_tool/adapters/regional_pivot.py（仅有测量依据时）
src/revenue_tool/adapters/final_revenue_formulas.py（仅等价表达式优化）
src/revenue_tool/adapters/formula_cache.py（仅必要的缓存/保存一致性）
```

相关既有测试可同步调整，并新增上述计算策略/规模测试。需要Windows辅助诊断时统一放在：

```text
scripts/benchmark_excel_vba_coexistence.bas
```

该脚本只用于本地验收，不嵌入输出xlsx。已有构建工作流仅为接入新增自动测试作必要调整，不扩展依赖、换GUI、改领域数据模型或变更业务规则。需要结构优化而确实触及`regional_summary.py`时，必须说明纯表示层等价性，不能改金额/分类口径。

实施者同步当前相关使用说明和本文件状态，最终证据只汇总到：

```text
docs/reviews/excel-vba-coexistence-performance-verification.md
```

## 7. Windows Excel同实例对照

### 7.1 必须隔离实验组

同一台机器、同一Excel版本/位数、相同加载项、相同脚本和源数据；每组从全新的Excel会话开始。测试仅操作副本。正常保存退出，不强制终止用户已有Excel进程。

| 组 | 打开的文件 | 目的 |
|---|---|---|
| A | 宏目标工作簿，不打开工具结果 | 宏自身基线 |
| B | 宏目标 + 原实现生成结果 | 复现原性能风险 |
| C | 宏目标 + 仅关闭forceFullCalc的新生成结果 | 隔离计算策略的影响 |
| D | 宏目标 + 最终修复结果 | 综合验证；无进一步优化时可与C相同 |

B/C/D中的宏与结果必须在**同一个Excel实例**。不能给D另开独立进程而称为修复。原版带强制计算设置的文件不得同时出现在C/D；微软文档提示该设置影响可持续到重启。[官方依据A]

记录打开顺序；至少覆盖“先目标后结果”和“先结果后目标”。等初次计算结束后再计宏耗时，将文件打开/初算与脚本执行分开。手动计算组仅为可选诊断，不用于最终通过。

### 7.2 测量项目

记录Excel版本/位数、PID、EXE或代码版本、N/M、文件大小、计算模式、目标及结果的ForceFullCalculation属性、脚本版本或本地哈希。

至少分开记录：打开到首次计算完成、宏运行、编辑一个人工值到最终字段更新、透视刷新、保存重开；记录进程内存峰值和卡顿时CPU/计算状态。每组重复至少3次，分别报告首轮与重复轮耗时，使用中位数对比，不能挑最快一次。

修复目标是普通编辑/普通计算触发的宏不再因本结果被迫反复全量计算，原正常脚本能完成。主动要求全部工作簿`CalculateFull`的脚本天然会计算新增结果，不能承诺其耗时与A完全相同；应单独报告这类工作负载。

### 7.3 无法提供实际宏时

不阻塞代码修复和自动测试。实施者可提供受控诊断宏：显式创建临时目标工作簿，仅对该对象的小范围单元格逐格写值、再做批量写值；只在独立测试副本中操作。

诊断宏必须限定Workbook/Worksheet/Range，不能用未限定的ActiveWorkbook、Cells或遍历并保存所有工作簿。计时主体不切换为手动、不全局禁用事件来掩盖共存问题；另设主动Application.Calculate的诊断场景并单列结果。

不要求用户开放“信任对VBA工程对象模型的访问”，不自动降低宏安全设置。没有原脚本复测只能证明受控场景，报告保留`PENDING_LOCAL_EXCEL_VALIDATION`，不能称为现场故障已解决。

如关闭强制全算后仍卡住，再核对原宏是否显式CalculateFull/CalculateFullRebuild、切换计算模式、遍历Workbooks/PivotCaches、针对错误ActiveWorkbook刷新，或触发加载项的Application级事件。不要未读脚本就归咎用户宏。

## 8. 正确性回归

### 自动及文件结构

- 最终xlsx不含`forceFullCalc="1"`或等价true值，calcMode保持auto；保存缓存路径不重新打开强制全算。
- 四个最终列仍为公式，初始缓存正确，原人工类型、空白、0、False、负数、清空回退与月份归一化不变。
- 两个原生透视、共用缓存和刷新设置保持合理；缓存记录数、关系、索引和工作表范围一致，无修复提示或孤立关系。
- 空数据/无有效月份、跨年、多中心、无要货、历史上期人工字段、分组透视输入、同页透视隔离和空Sheet读取回归通过。
- 比较业务值而不是XLSX二进制完全相同；允许变化的是计算设置和证明等价的表示结构。

### Microsoft Excel实机

- 自动模式下，修改黄色字段后，在任何F9、CalculateFull或透视刷新之前读取四个最终字段，必须已更新。
- 透视可继续由用户主动刷新；分别核对RPD、CPD每月每分类、地区/全表小计与Python预期值。
- 分类金额及小计均能双击Show Details；明细金额求和等于点击金额，不混入另一口径、种子行或重复小计副本。
- 修改后排序/筛选/移动列、刷新并保存重开，明细与合同/供应中心不串行。
- 用打包EXE生成的文件重复关键测试，不能只测开发环境生成物。

全量命令沿用仓库实际环境并记录退出码：

```bash
PYTHONPATH=src python -m unittest discover -s tests
python -m compileall -q src tests
git diff --check
python -m pip wheel . --no-deps --wheel-dir <临时目录>/wheel
```

复用仓库已有文件结构和公式测试。OpenXML结构检查、公式结构断言或其他计算引擎通过，均不能替代Microsoft Excel与VBA同实例性能验收。没有桌面Excel的执行环境如实跳过该项，不能伪造通过。

## 9. 旧结果与交付

新EXE不会自动修复已生成的旧xlsx；旧文件里的计算属性、公式和透视辅助数据仍然存在。

默认使用新版本、相同源数据重新生成一个新结果；需要继承人工值时选择旧结果作为上一次结果输入，保持读取只读、不继承用户自建透视、不覆盖原文件。不以删除用户透视、宏或原文件作为恢复步骤。

若单独提供旧文件修复工具，需要另行明确授权和备份策略；本次不批量改写历史工作簿。测试/交付通知提醒用户保存后重新启动Excel，避免旧会话残留强制计算影响。

## 10. 报告与关闭条件

最终报告包含：基线/最终提交、实际修改、最小修复与进一步优化各自效果、公式规模对比、全量命令与结果、A/B/C/D数据、Excel及EXE版本、业务值/实时公式/透视/Show Details回归、尚未覆盖的真实环境。

结论必须分开：

```text
代码及结构验证：PASS / FAIL
受控Excel同实例验证：PASS / FAIL / NOT_RUN
用户原脚本场景：PASS / FAIL / PENDING_LOCAL_EXCEL_VALIDATION
```

能直接完成的代码、测试、构建先完成，不等待新的Phase审批。只改了一行配置或只有结构测试通过，可以声明已实施，不能声明用户卡顿已验证修复。未完成用户同条件复测时保持#52开放，不将未验证假设写成根因定论。

## 11. 官方依据

A. [Workbook.ForceFullCalculation](https://learn.microsoft.com/en-us/office/vba/api/excel.workbook.forcefullcalculation)：强制计算忽略依赖；设置影响可能持续至Excel重启。

B. [Excel计算性能](https://learn.microsoft.com/en-us/office/vba/excel/concepts/excel-performance/excel-improving-calculation-performance)：智能重算、ForceFullCalculation、应用级计算选项、打开顺序及性能测量。注意文中What-If Data Table不是PivotTable，不能套用其倍率给本工具透视表。

C. [Application.Calculate](https://learn.microsoft.com/en-us/office/vba/api/excel.application.calculate)：应用、工作表和指定范围计算作用域不同，诊断宏应记录实际调用。

上述来源核对日期为2026-09-09。它们支持风险机制，不替代用户现场复现证据。
