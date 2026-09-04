# 企业作战地图：客户数据获取统一修复 V1

**状态：CURRENT REMEDIATION AUTHORITY**  
**代码工作树：`D:\BattleMap\battle-map`**  
**代码分支：`feature/enterprise-battle-map`**  
**适用模块：TOB、ISP、电力、大企；MOX 作为已工作的回归参考**  
**问题：点击“新增”时 TOB / ISP / 电力 / 大企均报“获取客户数据失败”**

---

## 1. 目标

本轮只解决企业模块新增弹窗的客户数据初始化链路，并将其收敛为一套可复用、可测试的共享机制。

目标状态：

```text
共享客户查询入口
→ 共享 API / service
→ database.js 客户主数据查询
→ 标准化响应
→ 各模块新增表单客户选择适配
→ 唯一 customer_id
```

MOX 当前新增能够正常获取客户数据，因此必须先恢复其真实工作链路，并将其作为行为参考。不得在不了解 MOX 工作方式的情况下为 TOB / ISP / 电力 / 大企另造四套客户查询逻辑。

本轮不修改各模块 Field Contract 字段集合，不修改 Section 设计，不修改统计、Heatmap 或企业首页。

---

## 2. 当前人工验收事实

用户已确认：

- MOX 新增目前能够正常进入客户数据流程；
- TOB 新增报“获取客户数据失败”；
- ISP 新增报“获取客户数据失败”；
- 电力新增报“获取客户数据失败”；
- 大企新增报“获取客户数据失败”。

因此本轮默认这是共享客户查询链或模块接入不一致问题，必须通过真实调用链证明根因，不能只改提示文案或 catch 后返回空数组。

---

## 3. Authority

实施时按以下顺序判断：

1. 本文件；
2. `enterprise-contract-architecture-v3.md` 中客户关系规则；
3. MOX 当前真实、已工作的客户查询代码；
4. 各模块当前 Create 表单接入代码；
5. 当前 server/API/database.js 客户查询实现；
6. 本地旧文档和旧实现仅作历史参考。

客户业务字段仍由各模块 Canonical Authority 决定，本文件不新增业务字段。

---

## 4. 必须先恢复真实调用链

在修改前逐层定位并记录：

```text
MOX 点击新增
→ create dialog 初始化
→ 客户数据 client / composable / service
→ HTTP method + URL + params
→ server route
→ service / database.js
→ 客户主表 SQL
→ response shape
→ 前端 normalization
→ 地区部 / 代表处 / 客户候选
→ 唯一 customer_id
```

然后分别恢复 TOB / ISP / 电力 / 大企当前调用链，与 MOX 对比。

必须明确根因属于哪一类：

- 错误 import；
- 调错 endpoint；
- route 未注册；
- method / params 不一致；
- response shape 不一致；
- 模块仍调用旧客户 API；
- 字段名 / SQL / customer table 映射错误；
- 共享 helper 未导出或引用错误；
- 错误处理把真实错误统一包装成“获取客户数据失败”；
- 其他可证实原因。

不得未定位根因就直接复制 MOX 文件。

---

## 5. 目标共享机制

### 5.1 共享能力

以下能力应只有一套：

- 客户列表 / 客户候选查询 client；
- 地区部、代表处等筛选所需的数据规范化；
- 客户唯一匹配；
- `customer_id` 提取；
- API 错误规范化；
- 必要的 server route / database customer query。

如果当前 MOX 已经使用共享能力，应直接让其他四个模块接入同一能力。

如果 MOX 当前仍有模块内私有实现，而该实现本质上是通用客户查询，则允许在本轮抽取为最小共享 service/helper，并迁移 MOX + TOB + ISP + 电力 + 大企共同使用。

禁止：

- 为五个模块各写一套 customer fetch；
- 为每个模块复制相同 HTTP 请求函数；
- 建立 `tobCustomerApi` / `ispCustomerApi` / `powerCustomerApi` 等内容相同的重复实现；
- 通过硬编码模块名改变客户查询业务语义；
- 使用假客户数据或静态 fallback 让弹窗“看起来能打开”。

### 5.2 模块差异只留在 UI Projection

共享的是客户主数据查询和唯一客户选择机制。

模块自己的客户展示字段仍按各自 Contract：

- MOX：地区部、代表处、国家、客户ID、客户名称、客户类别；
- TOB：地区部、代表处、国家、客户ID、客户名称；
- ISP / 电力 / 大企：地区部、代表处、国家、客户ID、客户名称、行业。

不得因为共享客户查询而把所有模块客户字段强行统一成同一 UI 字段集合。

---

## 6. 客户选择规则

所有模块新增必须满足：

1. 客户ID不能手工输入；
2. 地区部 / 代表处沿用当前已有联动方式；
3. 最终必须定位唯一客户并取得真实 `customer_id`；
4. 同名客户不得默认取第一条；
5. customer 主数据不存在时不得提交业务记录；
6. API / database.js 必须验证客户存在；
7. 客户查询失败时显示可诊断错误，不得静默转为空列表；
8. 查询成功但无匹配客户与查询本身失败必须区分。

本轮只修新增客户初始化和选择链，不扩大到未确认的客户主数据编辑需求。

---

## 7. 错误处理

当前用户看到统一文案“获取客户数据失败”。本轮修复后要求：

- UI 可以保留友好的用户提示；
- 开发日志 / 测试必须能得到真实 status、endpoint、error code 或后端 message；
- 不得在前端 `catch` 中吞掉真实错误；
- 404、500、响应格式错误、数据库异常必须可区分；
- 网络/API失败不能 fallback 成空数组并继续保存。

---

## 8. WRITE_SCOPE

允许修改：

- 企业共享客户查询 client / service / composable；
- MOX 当前客户查询实现，仅在抽取共享机制或回归所必需时；
- TOB / ISP / 电力 / 大企新增表单的客户数据接入；
- customer API route / service；
- `database.js` 中客户主数据查询的直接相关部分；
- 客户查询和新增初始化相关测试；
- 企业模块状态 / remediation evidence。

禁止修改：

- 五个模块 Field Contract 字段集合；
- MOX 当前字段完整性问题；
- 新增/编辑 Section 数量和样式；
- Metric Contract；
- Heatmap；
- 企业首页；
- V34—V38 业务字段 Migration，除非有证据证明客户查询本身依赖缺失且当前 Authority 已要求的客户技术列未正确创建；此时必须先记录 blocker，不能自行扩字段。

---

## 9. 测试门禁

本轮代码与测试必须同轮完成。

至少增加或修正以下自动验证：

### 共享客户查询

- 正常返回客户数据；
- response normalization 正确；
- API 非 2xx 可诊断；
- 错误响应不会伪装为空列表；
- 客户唯一匹配逻辑；
- 同名客户不会自动取第一条。

### MOX 回归

- MOX 新增客户数据仍正常加载；
- MOX 原有地区部 / 代表处联动不回归；
- MOX 能得到唯一 `customer_id`。

### TOB / ISP / 电力 / 大企

每个模块至少验证：

- 打开新增时客户查询成功；
- 不再进入“获取客户数据失败”异常路径；
- 能读取标准化客户候选；
- 最终选择得到 `customer_id`；
- 模块没有调用其他模块客户 API；
- 模块客户字段仍按自己的 Contract 展示。

### 联合验证

必须执行：

- customer API / database tests；
- MOX create 客户链回归测试；
- TOB create 测试；
- ISP create 测试；
- 电力 create 测试；
- 大企 create 测试；
- 企业模块测试；
- 全量 Vitest；
- build；
- lint/typecheck（如项目已有）。

不得通过删除失败测试或降低断言解决问题。

---

## 10. 完成标准

只有全部满足才能标记 COMPLETE：

1. TOB / ISP / 电力 / 大企新增不再因客户数据初始化失败而报错；
2. MOX 客户查询无回归；
3. 五个模块使用同一共享客户查询机制，或至少共享同一权威 API/service 且不存在重复请求实现；
4. 各模块仍按自己的客户字段 Contract 展示；
5. 唯一 `customer_id` 规则成立；
6. 同名客户不会默认取第一条；
7. 错误可诊断，不吞异常；
8. 相关测试、企业测试、全量 Vitest 和 build 通过；
9. 没有修改本轮禁止范围。

---

## 11. 实施产物

创建：

```text
docs/enterprise/remediations/customer-data-fetch-unification-report.md
```

报告至少记录：

- reviewed HEAD；
- root cause；
- 原 MOX 工作链；
- 最终共享链；
- changed files；
- 五模块接入情况；
- 测试结果；
- 未解决 blocker。

最终短回执：

```text
ENTERPRISE CUSTOMER FETCH REMEDIATION
RESULT=COMPLETE/PARTIAL/BLOCKED
ROOT_CAUSE=
SHARED_CUSTOMER_PATH=路径或说明
MOX=PASS/FAIL
TOB=PASS/FAIL
ISP=PASS/FAIL
POWER=PASS/FAIL
LARGE_ENTERPRISE=PASS/FAIL
CUSTOMER_ID_UNIQUE_MATCH=PASS/FAIL
DUPLICATE_CUSTOMER_FETCH_IMPLEMENTATIONS=0或数量
CUSTOMER_API_TESTS=PASS/FAIL
ENTERPRISE_TESTS=PASS/FAIL
FULL_TESTS=PASS/FAIL
BUILD=PASS/FAIL
OUT_OF_SCOPE_CHANGES=NO/YES
BLOCKERS=NONE或内容
NEXT=RESUME_ENTERPRISE_REVIEW
```
