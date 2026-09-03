# 企业作战地图：企业首页 Canonical Authority V1

**状态：FINAL STRUCTURE AUTHORITY / DATA RULES OPEN**  
**文档分支：`enterprise-battle-map-authority`**  
**本地实施分支：`feature/enterprise-battle-map`**  
**适用范围：企业首页导航、页面结构、企业专项、汇总模块、空间拓展、Heatmap、数据接口与测试**

---

## 1. 页面身份与导航

企业首页是一级“企业”本身对应的页面，不是“总览”子菜单。

```text
企业  ← 点击后进入企业首页
├─ MOX
├─ TOB
└─ ISP&大企
   ├─ ISP
   ├─ 电力
   └─ 大企
```

硬约束：

1. 不存在独立“总览”菜单；
2. “企业专项”“空间拓展”“Heatmap”都不是导航项；
3. 点击一级“企业”进入企业首页；
4. 点击“ISP&大企”父项时进入 ISP，不得跳回企业首页；
5. 企业首页可以有独立根 route，但不能产生额外可见菜单项。

---

## 2. 企业首页最终结构

企业首页从上到下必须为：

```text
企业专项
→ MOX / TOB / ISP&大企 三个并列模块
→ 空间拓展
→ 企业首页 Heatmap
```

当前企业首页不包含明细表格、新增或编辑弹窗。

---

## 3. 企业专项

标题：

```text
企业专项
```

定义文案：

```text
聚焦四大客户群，加速方案补齐，形成PtP+PtMP整体解决方案优势，贡献1.2亿$
```

要求：

- 位于页面最上方；
- 复用 MOX专项 / TOB专项 / ISP专项 的成熟结构和样式；
- 只替换标题和定义文案；
- 不另建一套专项视觉体系；
- 文案不得被本地 Agent 改写或缩写。

---

## 4. 三个并列汇总模块

企业专项下方为三个同级模块：

```text
MOX ｜ TOB ｜ ISP&大企
```

每个模块内部显示：

```text
目标：xx M$
实时：xx M$
```

要求：

- 桌面宽度下横向三列；
- 三个模块宽度、高度和视觉层级一致；
- 标题、目标、实时文字居中；
- 参考“骨干”页面顶部统计模块；
- 不把目标和实时拆成独立顶级卡片；
- 未接真实数据时使用 `--` 或明确空状态，不得使用随机值或虚假 0。

目标/实时的数据字段、汇总范围、金额单位换算和 ISP&大企聚合方式当前均为 `OPEN`，本地 Agent 不得自行推断。

---

## 5. 空间拓展

三个汇总模块下方显示一个独立页面模块：

```text
空间拓展
- 可参与总空间：xx M$
- 总项目：xx个
- 已落地：xx个
```

要求：

- 位于三个汇总模块下方；
- 不是导航项；
- 标题和指标文字居中；
- 可复用业务子页面空间拓展卡片的视觉语言，但企业首页数据契约必须独立；
- 未冻结真实规则时显示空状态，不得拿单个子模块数据冒充企业汇总。

以下仍为 `OPEN`：参与模块范围、金额求和方式、项目去重方式、已落地条件，以及是否直接汇总各模块 Metric 结果。

---

## 6. 企业首页 Heatmap

企业首页必须包含 Heatmap，位置固定在空间拓展下方：

```text
企业专项
→ 三个汇总模块
→ 空间拓展
→ 企业首页 Heatmap
```

### 6.1 实现原则

- 复用共享 `HeatmapChart` 和 Heatmap Engine；
- 企业首页只维护独立 `enterprise-home-heatmap-contract.js`；
- 不在页面组件中硬编码维度、聚合字段、Tooltip 或颜色规则；
- 不复制各业务页面的 ECharts 初始化、resize 和 dispose 代码；
- ECharts 实例不放入 Pinia；
- 页面卸载时 dispose 并清理监听；
- 无规则或无数据时显示明确空状态，不生成随机热力数据。

### 6.2 Contract 逻辑格式

```js
{
  key: 'enterpriseHomeHeatmap',
  module: 'enterpriseHome',
  title: '企业热力图',
  source: { api, mode: 'aggregate-api' },
  dimensions: { x, y, geo },
  value: { field, aggregate, unit },
  tooltip: { fields, formatterId },
  interaction: { clickAction, navigationTarget, drilldownParams },
  emptyState
}
```

### 6.3 当前开放规则

以下仍为 `OPEN`：

- 地理热力图还是矩阵热力图；
- 地区部、代表处、国家、模块或其他维度；
- 项目数量、整体空间（M$）、已下单金额或其他聚合值；
- Tooltip 字段；
- 颜色区间；
- 点击后导航、钻取或无动作。

企业首页没有明细表格，因此不得照搬业务子页面“点击 Heatmap 筛选表格”的逻辑。

---

## 7. 数据与性能边界

企业首页只请求汇总与 Heatmap 所需数据：

```text
企业首页
├─ summary API：目标/实时 + 空间拓展
└─ heatmap API：企业首页Heatmap聚合数据
```

要求：

- 不一次加载五张完整明细；
- 聚合优先在 API/SQLite 完成；
- Summary 和 Heatmap 的加载、空状态、错误状态独立；
- 一个接口失败不应让整个页面完全不可用；
- 不用随机 fallback 数据掩盖接口错误；
- Contract 使用静态 `const` / `Object.freeze()`，不做 Pinia 深响应式；
- Heatmap 更新 option，不重复创建 ECharts 实例。

---

## 8. 自动测试门禁

企业首页建设时必须覆盖：

1. 点击“企业”进入企业首页；
2. 无独立“总览”菜单；
3. “ISP&大企”进入 ISP；
4. 企业专项位于最上方，文案完全正确；
5. MOX、TOB、ISP&大企三个模块同级并列；
6. 每个模块内部包含目标和实时；
7. 空间拓展位于三个模块下方；
8. 企业首页 Heatmap 位于空间拓展下方；
9. 企业专项、空间拓展、Heatmap 均不进入导航；
10. 页面不出现明细表格、新增和编辑入口；
11. Summary API 成功、空数据和失败状态；
12. Heatmap API 成功、空数据和失败状态；
13. Heatmap 初始化、更新、resize、dispose 和监听清理；
14. 页面不加载五张完整明细；
15. 未冻结规则不产生假默认值；
16. 企业首页 Heatmap 不绑定子页面表格筛选。

人工页面验收由用户执行。

---

## 9. 实施顺序与完成标准

```text
MOX VERIFIED / REFERENCE_IMPLEMENTATION_V1
→ TOB VERIFIED
→ ISP VERIFIED
→ 电力 VERIFIED
→ 大企 VERIFIED
→ 冻结企业首页目标/实时与空间拓展口径
→ 冻结企业首页Heatmap规则
→ 企业首页代码、测试、自动验证
→ 独立审查
→ 用户人工验收
```

企业首页只有在导航、企业专项、汇总数据、空间拓展、Heatmap、聚合 API、自动测试、独立审查和用户人工验收全部通过后，才能标记 VERIFIED。
