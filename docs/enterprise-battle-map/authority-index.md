# 企业作战地图 Authority 文档索引

**状态：CURRENT AUTHORITY INDEX**  
**文档分支：`enterprise-battle-map-authority`**  
**本地实施分支：`feature/enterprise-battle-map`**

---

## 1. 当前正式 Authority

| 顺序 | 文档 | 用途 | 当前门禁 |
|---:|---|---|---|
| 1 | `enterprise-contract-architecture-v3.md` | `src/config/enterprise`目录、Field/Metric Contract、三个同级Section、Projection、Validator、数据库和测试治理 | 所有企业任务必读 |
| 2 | `mox-canonical-authority-v4.md` | MOX 41字段、三个Section、客户类别、进展、V34、UI/API/DB、统计与筛选 | 当前MOX唯一业务Authority |
| 3 | `remediation/mox-post-manual-review-remediation-v1.md` | 当前人工审查后定向修复WRITE_SCOPE | 当前实施必读 |
| 4 | `tob-canonical-authority-v2.md` | TOB字段和页面目标 | MOX VERIFIED后实施 |
| 5 | `isp-canonical-authority-v2.md` | ISP字段和页面目标 | MOX VERIFIED后实施 |
| 6 | `power-canonical-authority-v2.md` | 电力字段和页面目标 | MOX VERIFIED后实施 |
| 7 | `large-enterprise-canonical-authority-v2.md` | 大企字段和页面目标 | MOX VERIFIED后实施 |
| 8 | `enterprise-home-canonical-authority-v2.md` | 企业首页历史设计 | DEFERRED；当前不得实施数据口径，等待后续新版本 |

当前执行范围只包括 MOX V4 修复。不得开始 TOB、ISP、电力、大企或企业首页最终数据绑定。

---

## 2. 已被取代或暂停使用的文档

以下文件仅保留历史记录，不再作为当前实施或审查 Authority：

- `enterprise-contract-architecture-v1.md`
- `enterprise-contract-architecture-v2.md`
- `mox-canonical-authority-v3.md`
- `tob-canonical-authority-v1.md`
- `isp-canonical-authority-v1.md`
- `power-canonical-authority-v1.md`
- `large-enterprise-canonical-authority-v1.md`
- `enterprise-home-canonical-authority-v1.md`
- 任何与 MOX V4 冲突的本地字段清单、Schema、Contract、WRITE_SCOPE和Review结论

`enterprise-home-canonical-authority-v2.md`当前也不得用于实施首页统计口径。首页将在最后阶段重新发布当前版本。

本地 Agent 不得同时读取新旧版本后自行折中。

---

## 3. 本地 Agent 必读规则

任何 MOX 任务开始前必须依次读取：

1. `enterprise-contract-architecture-v3.md`；
2. `mox-canonical-authority-v4.md`；
3. 当前 remediation 或 review 规范；
4. 本地“企业作战地图基表”的 MOX Sheet；
5. 当前真实代码、API、`database.js`、SQLite和测试。

规则：

- GitHub当前 Authority 定义目标；
- Excel核实列、Row2、Row3和Data Validation；
- 当前代码和数据库只用于判断差距；
- 本地旧文档不得创造需求；
- 表格、新增、编辑必须消费同一 Field Contract；
- 统计与点击筛选必须消费同一 Metric Contract 条件；
- 代码、测试、自动验证和状态更新必须同轮完成；
- 实施完成后停止，由新Agent独立审查；
- 人工页面验收由用户执行。

---

## 4. 当前代码目录规则

企业领域 Contract 配置位于：

```text
src/config/enterprise/
```

不得继续使用 `src/enterprise` 或 `src/features` 作为活动 Contract Authority目录。

组件、页面、API和数据库实现仍保留在项目现有职责目录；本规则只约束 Field/Metric Contract、Projection、Validator、Metric Engine和option sets。

---

## 5. 表单 Section 规则

MOX新增和编辑使用三个同级Section：

```text
客户信息 ｜ 业务格局 ｜ 作战情况
```

无线与微波字段均属于“业务格局”，按MOX Field Contract顺序连续展示。不得再显示旧“客户信息/业务信息”二分结构，也不得渲染四个顶级Section。

TOB、ISP、电力和大企后续同样使用：

```text
客户信息 ｜ 业务格局 ｜ 作战情况
```

具体字段由各模块Authority决定。

---

## 6. 当前MOX关键修复门禁

当前MOX必须先完成：

- Contract迁移到`src/config/enterprise`；
- 清除重复Schema和旧活动引用；
- 41字段、顺序和三个Section正确；
- 客户类别在新增/编辑可选：空值、核心NA、战略NA；
- 点击新增不再报“获取客户数据失败”；
- 作战进展复用TOB当前有效特殊交互；
- V34 SQL、`database.js`注册、`_migrations`和最终Schema正确；
- Authority外旧字段、企业模块死代码和过期测试完成收敛；
- 九个统计和点击筛选无回归；
- 测试和build通过。

完成后进入MOX V4独立审查；未通过前不得推广到其他模块。

---

## 7. 页面结构与Heatmap

业务子页面统一：

```text
模块专项
→ 三个并列统计大模块
→ 当前模块Heatmap
→ 新增 / 表格 / 编辑
```

三个统计大模块：空间洞察、当年项目、空间拓展。每个模块内部显示指标，不得一个指标一张顶级卡。

企业首页最终汇总与Heatmap当前均延后，等待独立的新版企业首页Authority；当前MOX修复不得顺带建设。

---

## 8. 推荐推进顺序

```text
MOX V4定向修复
→ 自动验证
→ 独立审查
→ 用户人工验收
→ MOX VERIFIED / REFERENCE_IMPLEMENTATION_V1
→ 发布MOX参考实现文档
→ TOB
→ ISP
→ 电力
→ 大企
→ 企业首页最终建设
→ 企业模块最终技术债复核
```

---

## 9. Raw地址

总索引：

```text
https://raw.githubusercontent.com/olu37776-bit/excel-arrival-tool/enterprise-battle-map-authority/docs/enterprise-battle-map/authority-index.md
```

共享架构V3：

```text
https://raw.githubusercontent.com/olu37776-bit/excel-arrival-tool/enterprise-battle-map-authority/docs/enterprise-battle-map/enterprise-contract-architecture-v3.md
```

MOX V4：

```text
https://raw.githubusercontent.com/olu37776-bit/excel-arrival-tool/enterprise-battle-map-authority/docs/enterprise-battle-map/mox-canonical-authority-v4.md
```

当前MOX修复计划：

```text
https://raw.githubusercontent.com/olu37776-bit/excel-arrival-tool/enterprise-battle-map-authority/docs/enterprise-battle-map/remediation/mox-post-manual-review-remediation-v1.md
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

---

## 10. 文档维护规则

- 业务和架构修正由该Authority分支统一维护；
- 本地实施分支不再维护第二套长期设计Authority；
- 新版本发布后旧版本自动superseded；
- 字段变更必须同步字段表、Contract、Validator、数据库门禁和测试标准；
- 实施状态和审查证据可以留在本地，但不得覆盖GitHub目标设计；
- MOX页面全面确认后发布`mox-reference-implementation-v1.md`，供其他模块复用机制。
