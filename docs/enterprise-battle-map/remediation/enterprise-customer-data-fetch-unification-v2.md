# 企业作战地图：客户数据获取统一修复 V2

**状态：CURRENT REMEDIATION AUTHORITY**  
**取代：`enterprise-customer-data-fetch-unification-v1.md`**  
**代码工作树：`D:\BattleMap\battle-map`**  
**代码分支：`feature/enterprise-battle-map`**  
**适用模块：MOX、TOB、ISP、电力、大企**

---

## 1. 已证实根因

当前“获取客户数据失败”已定位到真实数据库查询链。

旧 SQL：

```sql
SELECT region, office, country, customer FROM customers
```

该查询没有返回 `customer_id`。

企业业务记录的客户关联以 `customer_id` 为唯一关系标识，因此前端即使能够拿到地区部、代表处、国家和客户名称，也无法完成后续唯一客户关联。TOB、ISP、电力、大企新增链在依赖 `customer_id` 时进入失败路径，最终被 UI 统一表现为“获取客户数据失败”。

根因分类：

```text
IMPLEMENTATION_NONCONFORMANCE
+ TEST_GAP
```

不是新的业务需求，也不是 Customer Relation 架构需要重做。

---

## 2. 当前正确链路

客户查询的最小正确数据契约必须包含能够建立唯一关系的技术键：

```text
customers table
→ customer_id
→ region
→ office / representativeOffice
→ country
→ customer / customerName
→ 模块所需其他客户主数据字段
```

实际 SQL 可以根据当前表列名和 API normalization 做别名，但必须保证最终标准化响应包含真实 `customer_id`。

目标链路：

```text
Create Dialog
→ shared customer query
→ customer API
→ database.js customer query
→ customers
→ response normalization
→ customer_id + customer display fields
→ unique customer selection
→ business record.customer_id
```

任何模块不得通过客户名称代替 `customer_id` 建立关系。

---

## 3. 修复原则

1. 客户查询必须返回 `customer_id`；
2. API 标准化响应必须保留 `customer_id`，不得在映射层丢失；
3. 前端标准化模型必须保留 `customer_id`，不得只保留显示字段；
4. 地区部/代表处/国家/名称只用于显示和筛选，不替代关系主键；
5. 最终选中的客户必须能够唯一映射到一个真实 `customer_id`；
6. 同名客户不得默认取第一条；
7. 查询成功但 `customer_id` 缺失必须视为数据契约错误，而不是当成空结果；
8. 不允许通过静态 fallback、临时生成 ID、客户名称拼接等方式绕过问题。

---

## 4. 五模块统一要求

MOX、TOB、ISP、电力、大企必须共享同一权威客户查询链或同一标准化 customer API。

模块差异只体现在各自 Field Contract 的显示字段：

- MOX：地区部、代表处、国家、客户ID、客户名称、客户类别；
- TOB：地区部、代表处、国家、客户ID、客户名称；
- ISP / 电力 / 大企：地区部、代表处、国家、客户ID、客户名称、行业。

不得因为 UI 字段不同而复制五套客户 SQL 或五套 customer fetch。

---

## 5. 必须验证的真实调用链

实施/复核 Agent 必须逐层确认：

```text
页面打开新增
→ 调用哪个 client/composable/service
→ HTTP method + endpoint
→ server route
→ database.js function
→ 实际 SQL
→ SQL result columns
→ API response shape
→ frontend normalization
→ customer candidate model
→ selected customer_id
→ create payload.customer_id
```

每一层都要能指出真实文件、函数和字段名。

重点检查是否存在第二处丢失 `customer_id`：

- SQL SELECT 已包含，但 API serializer 丢失；
- API response 已包含，但前端 map 丢失；
- 候选对象存在，但表单选择逻辑未保存；
- create payload 未携带；
- server 写入前重新映射时丢失。

不能只因为 SQL 已修就宣布整条链通过。

---

## 6. 数据库与 API 门禁

### 6.1 SQL / database.js

客户列表/候选查询返回列必须包含真实客户主键。

测试必须直接验证 query result 中存在：

```text
customer_id
```

并验证非空、类型合法、与 customers 表真实主键一致。

### 6.2 API

成功响应中的每个可选择客户必须包含 `customer_id`。

如果数据库结果缺失 `customer_id`，API 不得静默返回“正常客户对象”；应使测试失败并返回可诊断错误。

### 6.3 Create payload

最终创建 MOX/TOB/ISP/电力/大企业务记录时，必须使用选择出的 `customer_id`。

服务端必须再次验证该 `customer_id` 在客户主表存在。

---

## 7. 回归测试硬门禁

这次故障能够进入人工验收，说明旧测试没有验证完整 customer relation contract。必须补齐以下测试。

### 7.1 database.js 查询测试

直接执行客户查询并断言：

- 结果包含 `customer_id`；
- `customer_id` 不是 undefined/null；
- region/office/country/customer 显示字段仍存在；
- 查询真实 customer row 时 ID 与数据库一致。

测试不得只断言“返回数组长度 > 0”。

### 7.2 API response contract 测试

断言标准化客户对象至少包含：

```text
customerId / customer_id（按当前 API canonical 规范）
region
representativeOffice/office
country
customerName/customer
```

关键要求是 API 的 canonical customer ID 映射可追溯到数据库真实 `customer_id`。

### 7.3 五模块新增初始化测试

MOX、TOB、ISP、电力、大企分别验证：

1. 打开新增会调用统一客户查询；
2. 查询返回候选；
3. 候选包含真实客户 ID；
4. 地区部/代表处筛选后仍保留该 ID；
5. 选择客户后表单模型拥有 `customer_id`；
6. create payload 携带正确 `customer_id`。

### 7.4 负向测试

必须覆盖：

- SQL/API 客户对象缺 `customer_id` → FAIL；
- customer_id 不存在 → 服务端拒绝保存；
- 同名客户两个不同 customer_id → 不得自动取第一条；
- API 500/404 → 与“无匹配客户”区分；
- response normalization 不得丢 ID。

---

## 8. 与 Field Contract 的关系

`customerId` 是各模块 Canonical Field Contract 中的客户关系字段，但其来源是 customer relation，不是业务表重复列。

正确关系：

```text
Field Contract.customerId
→ runtime.source = customer-relation
→ customer API canonical ID
→ customers.customer_id
→ business_table.customer_id FK/relationship
```

不得把“SQL 返回显示字段但不返回 customer_id”视为满足 Field Contract。

Contract Validator / Conformance 测试后续应能够验证：任何 `runtime.source = customer-relation` 且需要唯一关系的字段，都有可达的真实关系键。

---

## 9. WRITE_SCOPE

允许修改：

- 共享 customer SQL / database.js customer query；
- customer API / normalization；
- shared customer client/composable/service；
- 五模块新增客户选择接入；
- customer relation 直接相关测试；
- remediation report。

禁止修改：

- 各模块业务字段集合；
- Section/group 规则；
- Metric / Heatmap；
- 企业首页；
- 与客户关系无关的 Migration；
- 非企业模块。

---

## 10. 完成标准

只有以下全部满足才能标记 COMPLETE：

1. 实际客户 SQL 返回 `customer_id`；
2. API 不丢 `customer_id`；
3. 前端 normalization 不丢 `customer_id`；
4. 五模块新增均能获得客户候选；
5. 五模块均能唯一获得真实 `customer_id`；
6. create payload 使用该 ID；
7. 服务端验证客户存在；
8. 同名客户不会自动取第一条；
9. database/API/五模块/负向测试覆盖上述事实；
10. 全量 Vitest 和 build 通过。

---

## 11. 实施报告

继续使用：

```text
docs/enterprise/remediations/customer-data-fetch-unification-report.md
```

报告必须明确记录真实根因：

```text
ROOT_CAUSE=customer query SELECT omitted customer_id
```

并记录修复后的实际 SQL 或等价 query projection、API response 字段、五模块验证结果及测试结果。

最终短回执：

```text
ENTERPRISE CUSTOMER FETCH REMEDIATION
RESULT=COMPLETE/PARTIAL/BLOCKED
ROOT_CAUSE=customer query SELECT omitted customer_id
DB_QUERY_RETURNS_CUSTOMER_ID=PASS/FAIL
API_PRESERVES_CUSTOMER_ID=PASS/FAIL
FRONTEND_PRESERVES_CUSTOMER_ID=PASS/FAIL
MOX=PASS/FAIL
TOB=PASS/FAIL
ISP=PASS/FAIL
POWER=PASS/FAIL
LARGE_ENTERPRISE=PASS/FAIL
UNIQUE_MATCH=PASS/FAIL
NEGATIVE_TESTS=PASS/FAIL
FULL_TESTS=PASS/FAIL
BUILD=PASS/FAIL
BLOCKERS=NONE或内容
NEXT=RESUME_ENTERPRISE_REVIEW
```
