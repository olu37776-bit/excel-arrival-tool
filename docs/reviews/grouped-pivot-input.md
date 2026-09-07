# v0.11.1 分组透视输入读取修复（Issue #47）

用户报告：上期文件读取报Nested.from_tree() missing 1 required positional argument: node；双击原工作簿图标闪现后消失。两者尚不能认定同因。

## 已复现的读取故障

openpyxl 3.1.5中FieldGroup.discretePr使用NestedInteger作为NestedSequence的expected_type，反序列化时把实例方法当作类方法调用。普通load_workbook会解析不参与业务继承的透视缓存。构造含fieldGroup/discretePr的XLSX，可经完整load_workbook重现完全相同异常。未收到用户实际文件，不能确认其具体XML结构。

改为data_only=True、read_only=True、keep_links=False导入，只读取单元格和元数据。继承和源数据仍按原字段契约校验，原文件不保存、不覆盖，不删用户透视。只读是程序导入方式，与生成工作簿的编辑权限无关；输出继续可编辑。业务行单次流式遍历，元数据窄表一次读取，避免逐行随机访问造成反复解析。缺少dimension或错误A1:A1范围时重新计算范围；日期/格式/False/0保留。

## 验证范围

新增真实XLSX分组缓存重现、上期继承和源文件读取、原文件SHA256不变、单元格类型/格式及dimension、损坏ZIP明确失败。打包EXE的smoke也加入分组缓存读取及False/0继承，不再只验证新生成文件可回读。新增4项专项回归本地通过，修正测试夹具的源路径索引后PR工作流34104261464中Linux任务101685531843完整130项测试通过，无跳过，117.745秒。Microsoft SDK任务101685531537通过。Windows任务101686341305共130项测试通过（2项Linux引擎测试跳过），93.028秒；EXE构建与包含分组透视读取的smoke通过。PR #48合并为2fbea89d1c26ac7d07031754cb5b9cdaa28cc2dd，正式发布工作流34104827669：Microsoft SDK任务101687333833通过；Linux任务101687334115共130项全通过、无跳过，145.308秒。Windows任务101688497777共130项通过（2项仅Linux引擎跳过），98.111秒；EXE构建、分组缓存读取、人工字段继承及GUI smoke通过。

v0.11.1于2026-09-07 09:20:11 UTC发布，EXE 12,843,409字节，SHA256：3b520afd0e2b3eafa6ca52fbc246bafb535077601f147eb87fef6e7e1f10861d。
[下载修复版EXE](https://github.com/olu37776-bit/excel-arrival-tool/releases/download/v0.11.1/ExcelRevenueTool-v0.11.1.exe)。

## 尚未确认的问题

用户补充Excel图标短暂闪现后消失，未看到工作簿窗口。该现象可能是启动或文件打开过程退出，不能只按文件关联/缓存损坏判断。需要实际原始XLSX、Excel版本，以及单独启动Excel后通过文件→打开是否仍退出的结果。Microsoft SDK结构验证与LibreOffice测试无法替代Microsoft Excel桌面验收；本issue保留开放。
