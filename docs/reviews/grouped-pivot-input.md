# v0.11.1 分组透视输入读取修复（Issue #47）

用户报告：上期文件读取报Nested.from_tree() missing 1 required positional argument: node；双击原工作簿图标闪现后消失。两者尚不能认定同因。

## 已复现的读取故障

openpyxl 3.1.5中FieldGroup.discretePr使用NestedInteger作为NestedSequence的expected_type，反序列化时把实例方法当作类方法调用。普通load_workbook会解析不参与业务继承的透视缓存。构造含fieldGroup/discretePr的XLSX，可经完整load_workbook重现完全相同异常。未收到用户实际文件，不能确认其具体XML结构。

改为data_only=True、read_only=True、keep_links=False导入，只读取单元格和元数据。继承和源数据仍按原字段契约校验，原文件不保存、不覆盖，不删用户透视。只读是程序导入方式，与生成工作簿的编辑权限无关；输出继续可编辑。业务行单次流式遍历，元数据窄表一次读取，避免逐行随机访问造成反复解析。缺少dimension或错误A1:A1范围时重新计算范围；日期/格式/False/0保留。

## 验证范围

新增真实XLSX分组缓存重现、上期继承和源文件读取、原文件SHA256不变、单元格类型/格式及dimension、损坏ZIP明确失败。打包EXE的smoke也加入分组缓存读取及False/0继承，不再只验证新生成文件可回读。等待完整测试和发布证据。

## 尚未确认的问题

用户补充Excel图标短暂闪现后消失，未看到工作簿窗口。该现象可能是启动或文件打开过程退出，不能只按文件关联/缓存损坏判断。需要实际原始XLSX、Excel版本，以及单独启动Excel后通过文件→打开是否仍退出的结果。Microsoft SDK结构验证与LibreOffice测试无法替代Microsoft Excel桌面验收；本issue保留开放。
