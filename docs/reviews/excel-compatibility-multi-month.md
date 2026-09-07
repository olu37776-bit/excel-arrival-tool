# Excel文件兼容性、多月汇总及GUI（Issue #42）

## 用户反馈与复现

v0.9.1输出被Microsoft Excel提示修复；基表保护阻止用户自行透视；原GUI月份仅支持手输一个月份。
首次Microsoft Open XML SDK 3.0.1 / Office2019校验（工作流34078506994，任务101609181623）确认：

- pivotTableDefinition存在不允许的r:id属性，两个透视表各一处。
- pivotField/items/item的t=grand不符合该位置约束，两个透视表各一处。grand只能留在行总计定义。
- 默认及自定义字体子元素顺序被SDK拒绝，三处。
- 旧边界数据、空表及完整流水线输出均有7个错误；原先LibreOffice和openpyxl回归未发现这些错误。

## 修复边界

保存出口移除非法透视属性、调整字体元素顺序；字段成员不再插入grand项，底部总计继续由rowItems定义。
原有公式计算值缓存、透视关系、金额与明细均保留；不以删除透视表解决文件修复问题。
基表工作表保护关闭，用户可直接创建自己的透视表。黄色人工输入提示保留。

GUI改为年份下拉/可输入、12个月勾选，默认本机当月，支持本月/全年/清空。一次最多12个月，选项排序去重。
多月输出按YYYY-MM命名各自RPD/CPD汇总，每月单独cacheId及源范围，月内两口径共享缓存。
汇总页C4提供当年12个月下拉，跨年可手输完整YYYY-MM并确认提示；重新计算与刷新方式不变。
GUI生成转为后台线程，通过队列向主线程返回；生成时禁止重复执行，进度动画不伪装为百分比。
文件、月份和保存分组；底部开始生成、打开结果/文件夹固定可见，表单支持滚动。

## 验证

首次修复提交fd4b7989cab1926a4c66af36fc808e7955b6a238的Microsoft SDK任务101610956305：
edge-cases.xlsx、empty.xlsx、multi-month.xlsx、pipeline.xlsx均为0个错误。
后续发布必须再次通过SDK、完整规则/公式回归、原生多月刷新与逐金额明细检查、GUI窗口及后台任务测试、Windows EXE自检。

多月原生测试覆盖两个阶段四张表：仅修改8月RPD汇总的选择，逐格核对金额和合同明细，其他三张表必须完全一致。
GUI测试实际创建Tk窗口，检查默认与多选、操作按钮可见、后台执行期间事件循环响应、禁止重复执行、成功后恢复控件。

## 证据限制

Microsoft Open XML SDK检查结构与语义约束，不是桌面Microsoft Excel。
Linux真实重算/原生透视使用LibreOffice；Windows验证对象是生成工具和文件读回。
用户实际报错工作簿、Excel版本和修复日志尚未提供，桌面Excel打开不再提示修复仍需实机确认；不能把这些自动检查描述为Excel实机验证。

参考：[Microsoft PivotTableDefinition](https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.spreadsheet.pivottabledefinition?view=openxml-3.0.1)、[Microsoft Font](https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.spreadsheet.font?view=openxml-3.0.1)。
