# v0.11.0 验证记录

需求 #44：所有实际年月横向排列、仅两张汇总、删除前期累计及GUI年月选项。#45：用户Excel人工填写后未更新，尚缺实际文件，保持待复核。

PR #46，首个提交 d3b7a2df9b1e524d62d71cf74d06169b1afa22eb。

- 本地126项测试通过，3项因本地无Tk显示/UNO跳过。
- PR工作流34081636727：Linux任务101617885484，126项测试全部通过，无跳过，135.502秒。包括无需F9/calculateAll的四个最终字段自动编辑检查，以及五阶段、两种口径、所有月份/地区/类别/小计的原生金额和Show Details检查；覆盖新增2027-03月份。
- Microsoft Open XML SDK任务101617885320：edge-cases.xlsx、empty.xlsx、pipeline.xlsx均0错误。
- PR Windows任务101618366080：126项测试通过（2项仅Linux引擎测试跳过），130.016秒。PyInstaller EXE构建、生成XLSX/公式缓存检查、真实Tk窗口smoke均通过。
- PR #46已合并：e94ae7b44cb97784bd8a59d90082d9df5c6d4668。正式发布工作流34082016871：Microsoft SDK任务101618970281通过；Linux任务101618970421共126项测试全通过、无跳过，159.921秒。Windows任务101619520902：126项测试通过（2项仅Linux引擎检查跳过），95.300秒；EXE构建、真实GUI与工作簿smoke通过。
- v0.11.0于2026-09-07 04:14:54 UTC正式发布。EXE大小12,839,908字节，SHA256：24e191f61d772069e5cb1e691ba578c3278bb9a284d325532b21e8c788110d71。
- [下载EXE](https://github.com/olu37776-bit/excel-arrival-tool/releases/download/v0.11.0/ExcelRevenueTool-v0.11.0.exe)。

原生计算引擎为LibreOffice；没有用户问题文件，也没有Microsoft Excel桌面实机验收，不宣称#45根因已确认。基表四个最终公式保留，增加calcOnSave与清晰输入/刷新说明。
