# 企业作战地图 Authority 文档索引

**文档分支：`enterprise-battle-map-authority`**  
**本地实施分支：`feature/enterprise-battle-map`**

---

## 1. 当前正式 Authority

| 顺序 | 文档 | 用途 | 当前门禁 |
|---:|---|---|---|
| 1 | `enterprise-contract-architecture-v1.md` | 共享 Contract、Projection、Validator、Metric Engine、数据库治理和推广规则 | 所有模块必读 |
| 2 | `mox-canonical-authority-v3.md` | MOX 最终字段、V34、UI/API/DB、统计与筛选 | 当前正在建设/审查 |
| 3 | `tob-canonical-authority-v1.md` | TOB 最终字段与实施门禁 | MOX VERIFIED 后实施 |
| 4 | `isp-canonical-authority-v1.md` | ISP 最终字段与实施门禁 | MOX VERIFIED 后实施 |
| 5 | `power-canonical-authority-v1.md` | 电力最终字段与实施门禁 | MOX VERIFIED 后实施 |
| 6 | `large-enterprise-canonical-authority-v1.md` | 大企最终字段与实施门禁 | MOX VERIFIED 后实施 |

---

## 2. 本地 Agent 必读规则

任何模块任务开始前必须：

1. 读取 `enterprise-contract-architecture-v1.md`；
2. 只读取当前模块对应的 Canonical Authority；
3. 读取本地“企业作战地图基表”对应 Sheet 核实列、Row2、Row3、Data Validation；
4. 不再使用与当前 Authority 冲突的本地旧字段文档、旧 Schema 或旧 config；
5. 不把其他模块字段复制到当前模块；
6. 代码、测试、自动验证、状态文档必须同轮完成；
7. 实施完成后停止，由新 Agent 独立审查；
8. 人工页面验收由用户执行。

---

## 3. 推荐实施顺序

```text
MOX remediation / implementation
→ MOX independent review
→ 用户人工验收
→ MOX VERIFIED
→ TOB planning + implementation + review
→ ISP planning + implementation + review
→ 电力 planning + implementation + review
→ 大企 planning + implementation + review
→ 企业首页真实统计
→ Heatmap真实规则
→ 统一清理已登记死代码与技术债
```

禁止在 MOX 尚未 VERIFIED 时一次性实施其余四个模块。

---

## 4. Raw 地址

共享架构：

```text
https://raw.githubusercontent.com/olu37776-bit/excel-arrival-tool/enterprise-battle-map-authority/docs/enterprise-battle-map/enterprise-contract-architecture-v1.md
```

MOX：

```text
https://raw.githubusercontent.com/olu37776-bit/excel-arrival-tool/enterprise-battle-map-authority/docs/enterprise-battle-map/mox-canonical-authority-v3.md
```

TOB：

```text
https://raw.githubusercontent.com/olu37776-bit/excel-arrival-tool/enterprise-battle-map-authority/docs/enterprise-battle-map/tob-canonical-authority-v1.md
```

ISP：

```text
https://raw.githubusercontent.com/olu37776-bit/excel-arrival-tool/enterprise-battle-map-authority/docs/enterprise-battle-map/isp-canonical-authority-v1.md
```

电力：

```text
https://raw.githubusercontent.com/olu37776-bit/excel-arrival-tool/enterprise-battle-map-authority/docs/enterprise-battle-map/power-canonical-authority-v1.md
```

大企：

```text
https://raw.githubusercontent.com/olu37776-bit/excel-arrival-tool/enterprise-battle-map-authority/docs/enterprise-battle-map/large-enterprise-canonical-authority-v1.md
```

---

## 5. 文档维护规则

- 后续业务修正由该 Authority 分支更新；
- 不在本地复制出另一套长期需求 Authority；
- 变更字段时同步修改模块文档中的字段表、Contract规则、Validator门禁和测试门槛；
- 如新增文档版本，旧版本标记 superseded，不允许两份同时作为当前 Authority；
- 本地实施分支只记录实现状态、验证证据和独立 Review，不自行重写业务设计。
