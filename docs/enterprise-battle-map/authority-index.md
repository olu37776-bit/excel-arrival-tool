# 企业作战地图 Authority 文档索引

**状态：CURRENT AUTHORITY INDEX**  
**文档分支：`enterprise-battle-map-authority`**  
**本地实施分支：`feature/enterprise-battle-map`**

---

## 1. 当前正式 Authority

| 顺序 | 文档 | 用途 | 当前门禁 |
|---:|---|---|---|
| 1 | `enterprise-contract-architecture-v2.md` | 共享 Field/Metric/Heatmap Contract、同级表单 Section、Projection、Validator、数据库治理和推广规则 | 所有任务必读 |
| 2 | `mox-canonical-authority-v3.md` | MOX 最终字段、V34、UI/API/DB、统计与筛选 | 当前参考模块建设/审查 |
| 3 | `tob-canonical-authority-v2.md` | TOB 字段与“客户信息｜业务格局｜作战情况”设计 | MOX VERIFIED 后实施 |
| 4 | `isp-canonical-authority-v2.md` | ISP 字段与“客户信息｜业务格局｜作战情况”设计 | MOX VERIFIED 后实施 |
| 5 | `power-canonical-authority-v2.md` | 电力字段与“客户信息｜业务格局｜作战情况”设计 | MOX VERIFIED 后实施 |
| 6 | `large-enterprise-canonical-authority-v2.md` | 大企字段与“客户信息｜业务格局｜作战情况”设计 | MOX VERIFIED 后实施 |
| 7 | `enterprise-home-canonical-authority-v1.md` | 企业首页、企业专项、三个汇总模块、空间拓展和首页 Heatmap | 子模块稳定后实施 |

---

## 2. 已被取代的文档

以下文件仅保留历史记录，不再作为实施或审查 Authority：

- `enterprise-contract-architecture-v1.md`
- `tob-canonical-authority-v1.md`
- `isp-canonical-authority-v1.md`
- `power-canonical-authority-v1.md`
- `large-enterprise-canonical-authority-v1.md`

本地 Agent 不得同时读取 V1 与当前 V2 后自行折中。发生冲突时，只使用本索引列出的当前版本。

---

## 3. 本地 Agent 必读规则

任何任务开始前必须：

1. 先读取 `enterprise-contract-architecture-v2.md`；
2. 只读取当前模块对应的 Canonical Authority；
3. 读取本地“企业作战地图基表”对应 Sheet，核实列、Row2、Row3、Data Validation；
4. Excel用于核实当前 Authority 中字段来源，不得自行扩充 Authority 外字段；
5. 不使用与当前 Authority 冲突的本地旧文档、旧 Schema、旧 config；
6. 不把其他模块字段复制到当前模块；
7. 表格、新增、编辑必须消费同一模块 Field Contract；
8. 统计数值与点击筛选必须消费同一 Metric Contract 条件；
9. Heatmap 必须使用共享组件与当前页面 Heatmap Contract；
10. 代码、测试、自动验证、状态文档必须同轮完成；
11. 实施完成后停止，由新 Agent 独立审查；
12. 人工页面验收由用户执行。

---

## 4. 表单 Section 统一规则

### MOX

新增与编辑使用四个同级 Section：

```text
客户信息 ｜ 无线格局 ｜ 微波格局 ｜ 作战情况
```

### TOB、ISP、电力、大企

新增与编辑统一使用三个同级 Section：

```text
客户信息 ｜ 业务格局 ｜ 作战情况
```

Section 是同级区块，不是先后流程。具体字段由各模块 Field Contract 决定。

---

## 5. 页面与 Heatmap 统一规则

业务子页面统一结构：

```text
模块专项
→ 三个并列统计大模块
→ 当前模块 Heatmap
→ 新增 / 表格 / 编辑
```

企业首页统一结构：

```text
企业专项
→ MOX / TOB / ISP&大企 三个并列模块
→ 空间拓展
→ 企业首页 Heatmap
```

企业首页 Heatmap 位于空间拓展下方。其维度、聚合值、Tooltip和点击行为必须另行冻结；没有规则时不得生成假数据。

---

## 6. 推荐实施顺序

```text
MOX Contract与页面完成
→ 自动测试
→ 独立审查
→ 用户人工验收
→ MOX VERIFIED / REFERENCE_IMPLEMENTATION_V1
→ 提炼已验证共享内核
→ TOB
→ ISP
→ 电力
→ 大企
→ 冻结企业首页目标/实时与空间拓展汇总口径
→ 冻结企业首页Heatmap规则
→ 企业首页实施与审查
→ 统一清理登记的死代码和技术债
```

禁止在 MOX 尚未 VERIFIED 时一次性实施其余模块。

---

## 7. Raw 地址

总索引：

```text
https://raw.githubusercontent.com/olu37776-bit/excel-arrival-tool/enterprise-battle-map-authority/docs/enterprise-battle-map/authority-index.md
```

共享架构 V2：

```text
https://raw.githubusercontent.com/olu37776-bit/excel-arrival-tool/enterprise-battle-map-authority/docs/enterprise-battle-map/enterprise-contract-architecture-v2.md
```

MOX：

```text
https://raw.githubusercontent.com/olu37776-bit/excel-arrival-tool/enterprise-battle-map-authority/docs/enterprise-battle-map/mox-canonical-authority-v3.md
```

TOB V2：

```text
https://raw.githubusercontent.com/olu37776-bit/excel-arrival-tool/enterprise-battle-map-authority/docs/enterprise-battle-map/tob-canonical-authority-v2.md
```

ISP V2：

```text
https://raw.githubusercontent.com/olu37776-bit/excel-arrival-tool/enterprise-battle-map-authority/docs/enterprise-battle-map/isp-canonical-authority-v2.md
```

电力 V2：

```text
https://raw.githubusercontent.com/olu37776-bit/excel-arrival-tool/enterprise-battle-map-authority/docs/enterprise-battle-map/power-canonical-authority-v2.md
```

大企 V2：

```text
https://raw.githubusercontent.com/olu37776-bit/excel-arrival-tool/enterprise-battle-map-authority/docs/enterprise-battle-map/large-enterprise-canonical-authority-v2.md
```

企业首页：

```text
https://raw.githubusercontent.com/olu37776-bit/excel-arrival-tool/enterprise-battle-map-authority/docs/enterprise-battle-map/enterprise-home-canonical-authority-v1.md
```

---

## 8. 文档维护规则

- 后续业务修正由该 Authority 分支统一更新；
- 不在本地复制出另一套长期需求 Authority；
- 变更字段时同步修改字段表、Contract规则、Validator门禁和测试门槛；
- 新版本发布后，旧版本标记 superseded，不允许两份同时作为当前 Authority；
- 本地实施分支只记录实现状态、验证证据和独立 Review，不自行重写业务设计；
- MOX 页面全面确认后，新增 `mox-reference-implementation-v1.md`，作为其他模块实现机制的直接参考。
