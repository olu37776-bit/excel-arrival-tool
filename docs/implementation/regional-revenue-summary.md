# 地区收入汇总与明细（Issue #38）

权威需求：[Issue #38](https://github.com/olu37776-bit/excel-arrival-tool/issues/38)。基线main `0d226b7e8a462904555bc47a0001dfaba6898d7b`，不使用冻结重构分支。

## 字段与范围

新增RPD地区收入汇总、CPD地区收入汇总两张可见工作表。初始统计月份由GUI/CLI `--report-month YYYY-MM`输入，默认本机当月；参数无效时在读取源文件前报错。生成后直接编辑各汇总页C4:G4合并区域中的年月（C4），两口径可独立调整，无需重新运行工具。

| 列 | 规则 |
|---|---|
| 地区部 | 基表region；空地区单列“（地区未填写）” |
| 1—上月累计 | 同一年1月至上月的最终收入预测之和；1月为前期累计（无）且为0 |
| 当月订未发/发未收/交未验 | 最终年月等于统计月，最终分段精确匹配 |
| 当月其他 | 当月的所有剩余最终分段，包含自由人工值、0、False或空白 |
| 当月小计 | 当月四类之和，不包含累计 |
| 末行小计 | 对应列全部地区合计；右下角仅当月 |

RPD/CPD分别使用final_revenue_month_rpd/cpd。共同使用final_revenue_segment和final_revenue_forecast；不重新分配金额，不修改基表事实。金额按Decimal两位小数，明确0和负数纳入。跨年、未来月份、月份空白/待修正、金额空白/无效的记录不纳入，并在汇总页通过公式显示当前所选年月的未纳入条数。

## Excel交互

两张汇总是真实OOXML透视表，具有缓存记录、透视字段、源范围及enableDrill。双击数值在Excel中新建匹配明细表；每格明细包含原基表40字段及汇总地区、汇总项目、基表行号。

修改基表黄色人工字段后：Ctrl+Alt+F9完成公式重算，再选择“数据→全部刷新”。月份位于订未发到小计五列上方，黄色C4:G4直接填写YYYY-MM。B5前期累计标题用公式引用C4；1月显示前期累计（无）。基表最终列继续受保护，两张透视表不保护，允许原生查看明细。

## 实施结构与守恒

- services/regional_summary.py：纯投影及Decimal汇总，不依赖Excel。
- adapters/regional_pivot.py：源单元格公式、原生缓存、透视结构、初始显示与样式。
- 两口径共享一个隐藏源_summary_source及同一份缓存；前40列通过公式引用基表（源中原地区列标为“原始地区部”，分组列名为“地区部”），4个辅助字段用于地区、汇总项目、基表行号及RPD/CPD口径。每张透视以原生报表筛选器固定默认口径。
- 每条基表记录保留两条源投影：分类记录，以及仅当月有效的小计记录。其余投影归入隐藏的“未纳入汇总”项。每口径2N行、合计4N行，另有6条被口径筛选永久排除的结构占位确保编辑月份或金额后刷新无需重建源范围。
- 每个可见汇总列有互斥的汇总项目筛选，同一格的基表行号唯一。最后一列为显式当月小计桶；禁用跨列grand total，保留底部grand total并命名“小计”。避免把累计和当月加总，也避免六个条件金额字段透视导致Show Details混入整地区记录。
- 辅助源不是事实表，不能直接总计所有源记录。用户应使用基表或可见汇总列。原基表保持40列不变，metadata不将辅助字段加入人工继承集合。
- 初始值由Python计算且与缓存一致；saveData开启，refreshOnLoad关闭，避免未完成公式重算时抢先刷新。用户按重算→刷新顺序更新。共享同一个缓存ID及对象，避免openpyxl多缓存写入时records关系重定向风险；保存重读两轮保持两口径明细各自正确。
- 最大基表262142行（4N+6辅助源受Excel行数上限约束），超出时给出明确错误。

不依赖Excel COM、宏、动态数组或新增用户安装项。openpyxl低层OOXML对象封装在单一adapter中，不宣称其高层支持创建透视。

## 验证

纯规则测试使用独立字面量预期，覆盖两口径、各列及小计、月份边界、异常/空白、0/负数、空地区、空工作簿。保存重读两轮，逐格检查缓存明细唯一性及金额与初始显示相符。

Linux门禁使用真实LibreOffice UNO API：打开生成xlsx、编辑人工月份/金额/分段、calculateAll、原生pivot.refresh、原生getDrillDownData，逐格验证明细ID和金额，再清空人工字段重新验证。未安装引擎时REQUIRE_FORMULA_ENGINE=1硬失败。Windows继续执行全量测试、构建及EXE smoke。

真实Windows桌面Excel交互需本地复核；自动验证不能冒充Excel实机验证。仅使用虚构测试数据。

参考：[Excel查看透视明细](https://support.microsoft.com/en-us/excel/expand-collapse-or-show-details-in-a-pivottable-or-pivotchart)、[openpyxl透视支持边界](https://openpyxl.readthedocs.io/en/stable/pivot.html)、[LibreOffice原生明细API](https://api.libreoffice.org/docs/idl/ref/interfacecom_1_1sun_1_1star_1_1sheet_1_1XDataPilotTable2.html)。

## 办公软件兼容边界

Excel工作簿底部单元格和标准OOXML grandTotalCaption均明确为“小计”。实际LibreOffice导入会忽略该自定义标题并用英文环境的Total Result。独立引擎验证记录原始标题，仅将末行该已知标签映射后比较金额与明细；不改工作簿、不跳过金额/明细断言，也不将LibreOffice标签行为冒充Excel结果。Microsoft定义见https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.spreadsheet.pivottabledefinition.grandtotalcaption 。

## 表内月份与稳定布局

可见表头为地区部、动态累计、订未发、发未收、交未验、其他、小计。月份仅在五个当月列上方显示。原生pivot使用稳定的前期累计/订未发/发未收/交未验/其他/小计成员；原生报表筛选区隐藏在第6/7行，原生两行表头隐藏在第8/9行，可见第5行表头位于pivot范围之外，因此刷新不会覆盖月份输入或累计公式。第10行开始的金额及底部小计仍是原生透视数据区，可直接双击。

源分类公式按每个口径汇总页的C4选择年份和月份，不硬编码9月或1—8月。6条__SCHEMA__口径记录只保留成员集合，避免切到无数据期间后透视列消失；RPD/CPD筛选均排除它们，金额为空，且不得进入任何格的明细。测试逐格验证这一边界。工作簿内年月有输入校验；粘贴绕过校验形成非法值时显示修正提示且不输出伪统计。
