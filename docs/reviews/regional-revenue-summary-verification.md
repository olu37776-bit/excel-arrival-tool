# Issue #38 验证记录

状态：已合并并发布v0.9.0；PR及main的Linux/Windows自动验证全部通过，真实Windows桌面Excel验收边界保留。

## 实施结果

- 需求：[Issue #38](https://github.com/olu37776-bit/excel-arrival-tool/issues/38)，包含用户追加的“点击金额”及表内年月调整要求。
- PR：[#39](https://github.com/olu37776-bit/excel-arrival-tool/pull/39)。验证源码：`efdb6b186cca5c7afe5fd86559dc8eca6080de6c`。
- 合并main：`3619ffd0c961de8d58f0c3a934566acc435c4e36`。版本0.9.0。
- RPD/CPD各一张；C4:G4黄色区域位于订未发至小计五列上方，可以独立修改YYYY-MM。B5动态显示所选年份1月至上月累计，1月为0。
- 所有金额及底部/右侧小计均处于原生透视数据区，双击金额查看匹配明细；基表保持40列和原人工继承边界。

## 验证证据

- [PR完整验证](https://github.com/olu37776-bit/excel-arrival-tool/actions/runs/34075014637)：Linux与Windows均成功。
- [合并后验证与正式发布](https://github.com/olu37776-bit/excel-arrival-tool/actions/runs/34075254664)：Linux全量121项通过，无跳过；包括真实公式重算、原生透视刷新和Show Details。
- 原生办公引擎6个阶段：初始、人工月份/分段及负金额修改、明确0、清空人工字段、两口径切换至6月/12月、切换至1月/下一年。2口径×4行（含底部小计）×6金额列×6阶段，共288格金额及明细集合比较通过。结构占位不会进入明细，无重复业务条目。
- 字面量金额预期、跨年排除、0/负金额、空地区、自由分段、空工作簿、两轮xlsx保存重读、共享缓存的口径隔离与单格明细守恒通过。
- compileall、diff check、wheel通过。Windows EXE自检已扩展为实际生成并重新读取包含两张原生透视的工作簿，验证内置依赖与汇总金额。
- 本地PDF转换和文本抽取检查了两张汇总的列序、年月位置、累计标题和金额；预览环境缺少中文字体，未将其图片当作Windows中文渲染验收。

## 修复过程中发现并消除的问题

- 多缓存关系可能在openpyxl保存时指向同一records文件：改为一个共享缓存，以原生口径筛选隔离。
- 原生刷新总计方向与预写显示不一致：修正OOXML总计设置，底部保留、跨列总计关闭。
- 月份控件放入透视的报表筛选预留区会被刷新清除：移动到该范围外，内部筛选及表头行隐藏，外部动态表头保持稳定。
- 月份切到无数据区间可能导致类别列消失：增加被RPD/CPD口径严格排除的结构成员，维持固定列序。

## 验证边界

Windows桌面Excel和真实业务数据：PENDING_LOCAL_EXCEL_VALIDATION。LibreOffice导入忽略Excel的grandTotalCaption并改用Total Result，测试仅对其末行标签作明确映射，金额及明细断言全部保留。原始xlsx底部单元格和标准grandTotalCaption均明确为“小计”。不把独立引擎结果冒充Excel实机验证。

实现及使用边界见[实施文档](../implementation/regional-revenue-summary.md)。

## 正式发布完成（2026-09-07）

- main的Windows全量测试、EXE构建、实际EXE生成/读回工作簿自检、校验和及Release上传全部成功。
- [ExcelRevenueTool-v0.9.0.exe](https://github.com/olu37776-bit/excel-arrival-tool/releases/download/v0.9.0/ExcelRevenueTool-v0.9.0.exe)，12807998字节。
- SHA-256：`09061df3691838886311f9b9fcd923f19f379324976ad8735a8d58966487174c`。
- Issue #38关闭；README下载链接及使用说明已同步。
