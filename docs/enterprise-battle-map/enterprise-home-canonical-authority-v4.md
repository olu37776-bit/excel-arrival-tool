# 企业作战地图：企业首页 Canonical Authority V4

**状态：CURRENT FINAL AUTHORITY**  
**文档分支：`enterprise-battle-map-authority`**  
**本地实施分支：`feature/enterprise-battle-map`**  
**适用范围：企业首页导航、页面结构、视觉布局、目标占位、实时汇总、空间拓展、汇总 API、测试与审查**  
**取代：企业首页 V1/V2/V3，V4 为当前完整首页 Authority**  
**本轮依据：目标/实时横向并列、实时金额补M$、空间拓展按MOX与ISP卡片中线限定边界并与上排等高、企业专项标题使用其他专项一致蓝色**

---

## 0. 最新执行状态

此前首页/字段修复为用户报告完成，旧审查结论按对应HEAD保留。本次用户要求目标/实时横向并列、现有实时金额补M$单位，并明确空间拓展不要太窄：左边缘对齐上排MOX卡片横向中心位置、右边缘对齐ISP&大企卡片横向中心位置，整体位于TOB下方居中，高度与上排卡片一致。
“企业专项”标题同时改为与其他“xx专项”标题一致的蓝色，复用实际共享颜色样式。当前按第18节进行展示修正，下面相关正文已同步；云端未读取当前页面或本地代码，实际实现以本地证据为准。本次不重建汇总API、数据库或统计公式。实施后按快照准备V1精确本地提交，固定新候选；联合复核第9/11节核验版本及新增展示要求。

## 1. 当前确认结论

1. 企业首页当前阶段暂不建设 Heatmap。
2. 首页顶部包含企业专项。
3. 企业专项下方显示 MOX、TOB、ISP&大企三个并列模块。
4. 每个模块只显示目标、实时，两组在卡内横向并列，目标在左、实时在右。
5. 目标暂时使用占位值：`xx M$`。
6. 当前不显示、不计算“达成率”。
7. 当前不显示进度条。
8. 实时必须绑定真实数据库汇总，数值后显示 `M$`，不能继续使用 `xx` 或只有无单位数字。
9. 空间拓展在三卡下方居中，桌面左/右边缘分别对齐MOX/ISP&大企卡片的水平中心位置，高度与上排一致，保留真实汇总和三指标。
10. 首页不得增加未确认指标。
11. 企业专项与三卡区必须有明确垂直间距，三卡之间、三卡与空间拓展之间均不得重叠。
12. MOX、TOB、ISP&大企及空间拓展的卡片和数字样式复用全局首页“骨干场景 / 企业场景 / 单域自治”的当前成熟机制。
13. 全局首页“企业场景”点击进入企业首页；企业首页 MOX/TOB/ISP&大企卡片分别进入 MOX/TOB/ISP 页面。

---

## 2. 页面身份与导航

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

- 不存在独立“总览”菜单；
- 点击一级“企业”进入企业首页；
- 点击“ISP&大企”父项进入 ISP 页面，不得返回企业首页；
- “企业专项”和“空间拓展”是页面内容，不是导航项；
- 当前首页不包含 Heatmap、明细表格、新增或编辑入口。

点击映射：

| 实际入口 | 目标页面 |
|---|---|
| 全局首页“企业场景”卡片 | 企业首页 |
| 一级“企业”菜单 | 企业首页 |
| 企业首页 MOX 卡片 | MOX 子页 |
| 企业首页 TOB 卡片 | TOB 子页 |
| 企业首页 ISP&大企 卡片 | ISP 子页（沿用该父项的既有导航规则） |

本地 Agent 必须从当前 router/route registry 确认真实 route name/path，复用项目导航机制并在报告记录精确映射；不得猜测 URL、新建重复企业首页或错误跳回全局首页。卡片主体及其目标/实时数字区域均可触发同一跳转，键盘可聚焦并能按项目既有可访问交互触发。不额外为企业专项或空间拓展创造未经确认的跳转目标。

---

## 3. 页面结构

企业首页从上到下固定为：

```text
企业专项
→ MOX / TOB / ISP&大企 三个并列模块
→ 空间拓展
```

当前阶段不渲染首页 Heatmap，也不保留 Heatmap 空白占位。

---

## 4. 企业专项

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
- 保留现有专项内容结构，复用成熟专项组件；与下方三卡区通过正常布局流和共享 spacing token 分隔；
- 保持标题和定义文案内容；“企业专项”标题文字使用与项目其他“xx专项”标题相同的蓝色，不继续使用当前白色；
- 先定位真实参照专项标题及其共享class/token，复用同一颜色来源和主题规则，不凭印象硬编码一个近似蓝；只调整标题颜色，不批量给整块定义文案或其他卡片文字染色；
- 不另建第二套专项视觉组件；
- 文案保持原文，不改写、不缩写；
- `1.2亿$`只是企业专项定义文案的一部分，不用于计算或分摊三个模块目标。

---

## 5. 三个并列模块

企业专项下方固定显示：

```text
MOX ｜ TOB ｜ ISP&大企
```

每个模块内部为两个横向并列的指标组：左侧 `目标：xx M$`，右侧 `实时：真实汇总值 M$`。两组的标签、金额行分别对齐，不能将整个目标组占一行、整个实时组放下一行。

### 5.1 目标

当前目标未取得正式数值，统一显示占位：

```text
xx M$
```

要求：

- 目标不从数据库计算；
- 目标不从企业专项中的 `1.2亿$`拆分；
- 不显示“待确认”替换该占位，除非用户后续明确修改；
- 三个目标占位可以集中维护，不能散落多份；
- 后续需求人给出真实目标时，再发布新 Authority 更新目标值。

### 5.2 实时

实时必须由数据库真实数据聚合，不得显示 `xx`或随机值。数字后显示与目标一致的 `M$` 单位，由共享显示层提供且只出现一次；0金额也显示 `0 M$`（小数格式沿用项目规范）。

统一业务金额字段（各模块 canonical key 与 DB 列须通过正式 Contract 映射）：

```text
已下单金额（$M）
```

MOX：

```text
MOX实时 = SUM(MOX.已下单金额（$M）)
```

TOB：

```text
TOB实时 = SUM(TOB.已下单金额（$M）)
```

ISP&大企：

```text
ISP&大企实时
= SUM(ISP.已下单金额（$M）)
+ SUM(电力.已下单金额（$M）)
+ SUM(大企.已下单金额（$M）)
```

其中“大企”对应实际业务表：

```text
大企（油气矿、广电、交通）
```

### 5.3 聚合边界

- TOB/ISP/电力/大企当前金额 canonical key 为 `orderedAmountMusd`；MOX 由本地当前正式 Contract 核实精确 key，不能以中文 label 作为运行身份。
- 实时只统计“已下单金额（$M）”，不得误用“26年订货空间”“整体空间”“已下单数量”或目标值。
- 汇总各模块在现有权限/软删除等数据有效性规则下的全部适用记录；不额外引入未确认的年份、月份、项目状态或“已孵化”条件。空间拓展的条件不得套到实时金额上。
- 每条业务记录只计一次，不能因联接 Customer/Progress 历史表造成倍增；跨模块不按客户名自行去重。
- 既有单位为 M$，不再次除以一百万。先按数值求和，再使用项目统一 formatter 展示。

### 5.4 明确禁止

当前首页三个模块中不得出现：

- 达成率；
- 进度条；
- 趋势；
- 同比或环比；
- 排名；
- 用户未确认的任何额外指标。

---

## 6. 三个模块视觉规则

- 桌面宽度下三列等宽并列；
- 三张卡片高度和视觉层级一致；
- 模块标题、目标、实时文字居中；
- 视觉唯一参照为**全局首页**现有“骨干场景 / 企业场景 / 单域自治”场景卡及其数字展示，不再以“骨干子页面顶部统计卡”作本轮参照；
- 优先直接复用其共享卡片/数值组件和样式 token；如果当前嵌在全局首页，最小提取中性共享展示组件，保持全局首页现有行为和外观；不能复制多份 CSS 或为企业卡片另建近似样式；
- 复用卡片边框/背景/圆角/内边距、标题/数值/单位字号层级及交互态，不复制其业务指标、公式或布局语义；
- 目标和实时在同一卡内横向两列并列，目标左、实时右，两组标签与数值行对齐，不拆成两张卡或上下两整行；
- 数值与M$单位相邻，不让单位独自掉行；三个模块的单位位置、字号层级与目标一致；
- 实时数值可以使用比目标稍高的视觉权重，但不得新增业务含义；
- 通过合理内边距、字号层级和卡片高度解决页面空、散、丑的问题；
- 不通过添加未确认指标填充页面。

间距和防重叠：
- 用 grid/flex 正常文档流、gap、padding/min-height 和自然换行解决企业专项、三卡、空间拓展之间的间距；不使用负 margin、绝对定位或固定高度补丁把问题移到其他宽度。
- 企业专项文案换行后能够自然撑高，下方三卡不覆盖文案；数字或单位变长也不得互相遮挡。
- 三卡桌面等宽，小窗口可按项目既有断点将卡片换行；卡内目标/实时仍用横向两组排布，适配内边距与字号，不退回上下两整行。金额及单位不得溢出、遮挡或裁掉。
- 具体间距值依据全局首页现有 token 与本地渲染效果确定，并在实施报告中记录，不新增无依据的设计体系。

---

## 7. 空间拓展

三个模块下方显示一个水平居中的空间拓展卡片：

```text
空间拓展
可参与总空间：真实值 M$
总项目：真实值 个
已落地：真实值 个
```

常规桌面上排三卡并列时，空间拓展的**左边缘对齐MOX卡片横向中心位置，右边缘对齐ISP&大企卡片横向中心位置**，即边缘落在这两张卡片各自的中间，而非卡片内侧边缘。整体在TOB下方居中，不缩成单张卡片那么窄。
宽度和左右位置由同一上排网格的卡片宽度/gap派生，不写死截图像素或直接用忽略gap的百分比。保留与三卡区的垂直间隔。
空间拓展高度增加至与上排三卡一致，复用同一高度/内边距规则或共享min-height，并以真实渲染尺寸核对；不通过裁切、负margin或绝对定位补丁凑尺寸。
三个指标在卡内横向并列、居中，保持原名称、单位和共享数字样式。窄窗口上排三卡换行后，空间拓展按可用容器宽度居中自适应，不硬套跨行卡片的中线坐标；指标可自然换行并撑高，不能裁切或溢出。

这里更改展示样式，不把“可参与总空间”改为已下单金额，不把项目数改为金额。

汇总范围固定为：

```text
MOX + TOB + ISP + 电力 + 大企
```

每一行是一条独立项目/机会记录，项目数量按记录数统计，不按客户去重。

### 7.1 可参与总空间

用户已确认：可参与总空间使用 `整体空间（M$）`求和。

筛选条件沿用子模块已确认规则：

```text
空间洞察 = 已孵化
AND
项目状态 = 跟踪
```

公式：

```text
可参与总空间
= SUM(
    整体空间（M$）
    WHERE 空间洞察 = 已孵化
      AND 项目状态 = 跟踪
  )
```

不得使用：

- 已按 Excel 确认增量删除的 `整体空间`分类值（肥肉/瘦肉/骨头）；
- `整体空间（跳）`；
- `26年订货空间（$M）`；
- `已下单金额（$M）`。

### 7.2 总项目

```text
总项目 = COUNT(项目状态 = 跟踪)
```

范围为五个业务模块全部记录。

### 7.3 已落地

```text
已落地
= COUNT(
    空间洞察 = 已孵化
    AND 项目状态 = 跟踪
  )
```

因此：

- 总项目是所有“跟踪”项目数；
- 已落地是“跟踪”项目中同时标记“已孵化”的记录数；
- 可参与总空间和已落地使用同一记录集合，前者求金额，后者计数。

---

## 8. 金额与空值规则

- 数据库和 API canonical 金额单位统一为 M$；
- `NULL`和空值按 0 参与 SUM；
- 非法非数值值不得字符串拼接，应排除并产生可诊断校验信息；
- UI只做格式化展示，不把格式化字符串写回数据库；
- 目标与实时金额均用M$后缀且只显示一次，现有值已是M$，本次不乘除一百万或改变精度；
- 空间拓展可参与总空间继续用M$，总项目/已落地继续用“个”，不能给数量也加金额单位；
- 金额小数位使用当前项目已有统一 formatter；当前文档不新增新的精度规则。

---

## 9. 首页汇总 Contract

推荐集中维护：

```text
src/enterprise/home/contracts/enterprise-home-contract.js
```

至少定义：

```js
{
  targetPlaceholders,
  realtimeMetrics,
  expansionMetrics,
  formatterIds
}
```

概念示例：

```js
export const ENTERPRISE_HOME_CONTRACT = Object.freeze({
  targetPlaceholders: {
    mox: 'xx M$',
    tob: 'xx M$',
    ispAndLargeEnterprise: 'xx M$'
  },
  realtimeMetrics: {
    mox: 'home.realtime.mox',
    tob: 'home.realtime.tob',
    ispAndLargeEnterprise: 'home.realtime.ispAndLargeEnterprise'
  },
  expansionMetrics: {
    availableSpace: 'home.expansion.availableSpace',
    totalProjects: 'home.expansion.totalProjects',
    landed: 'home.expansion.landed'
  }
})
```

Vue 页面不得自行重复维护 SUM/COUNT/WHERE 条件。

---

## 10. 汇总 API

企业首页不得为了显示六个真实汇总值加载五张完整明细。

推荐：

```text
GET /api/enterprise/home-summary
```

响应只返回真实聚合值：

```json
{
  "realtime": {
    "mox": 0,
    "tob": 0,
    "ispAndLargeEnterprise": 0
  },
  "expansion": {
    "availableSpace": 0,
    "totalProjects": 0,
    "landed": 0
  }
}
```

目标占位无需作为数据库聚合结果返回。

要求：

- 聚合优先由 API / `database.js` / SQLite 完成；
- 使用各模块 canonical DB 列，不以中文 label 拼 SQL；
- 不返回五张表完整记录；
- 不在前端拉取五份明细后聚合；
- 一个模块表不存在或尚未完成时，必须返回可诊断错误或按明确兼容规则处理，不得伪造成功结果；
- API 失败时页面显示明确错误状态，不退回 `xx`作为实时值；也不得用 0 伪装失败。
- 从全局首页或子页返回企业首页时，按既有数据生命周期重新获取/有效失效刷新；在子页更新已下单金额后返回首页，必须显示新汇总。无需另建轮询或推送系统。
- 保持现有认证与数据权限，不因新增汇总接口扩大数据可见范围。

---

## 11. Heatmap 当前状态

```text
ENTERPRISE_HOME_HEATMAP = DEFERRED
```

要求：

- 当前首页不渲染 Heatmap；
- 不请求 Heatmap API；
- 不留空白 Heatmap 占位；
- 不生成随机或假数据；
- 子页面 Heatmap 与共享 Heatmap 结构不受影响；
- 后续恢复首页 Heatmap 时必须发布新版本 Authority。

---

## 12. 页面状态

### 加载

- 企业专项立即显示；
- 三个模块的实时和空间拓展真实值使用统一 loading/skeleton；
- 目标始终显示 `xx M$`；
- 数据返回后只替换实时和空间拓展值。

### 空数据

数据库真实聚合为0时金额显示0 M$（精度沿用formatter），项目数量显示0个，不得与目标占位混淆。

### 错误

汇总 API 失败时：

- 企业专项和页面结构仍保留；
- 实时与空间拓展显示“数据加载失败”或当前统一错误态；
- 保留可诊断错误；
- 不用随机数、旧缓存或 `xx`冒充实时数据。

---

## 13. 自动测试门禁

至少覆盖：

1. 点击企业进入企业首页；
2. 无独立总览菜单；
3. ISP&大企进入 ISP；
4. 企业专项内容与位置正确，标题颜色与实际其他专项标题共用蓝色样式来源；
5. MOX、TOB、ISP&大企三卡并列且顺序正确；
6. 每张卡只含横向并列的目标和实时，两组标签/数值行分别对齐；
7. 不存在达成率和进度条；
8. 三个目标显示 `xx M$`，三个实时金额有且仅有一个M$后缀，0金额也带单位；
9. MOX实时等于MOX已下单金额（$M）之和；
10. TOB实时等于TOB已下单金额（$M）之和；
11. ISP&大企实时等于ISP+电力+大企已下单金额（$M）之和；
12. 可参与总空间按已孵化AND跟踪记录的整体空间（M$）求和；
13. 总项目只统计跟踪记录；
14. 已落地统计已孵化AND跟踪记录；
15. 项目数量按记录数，不按客户去重；
16. 首页不加载五张完整明细；
17. 加载、0值、失败状态正确；
18. 当前不渲染或请求首页Heatmap；
19. 全量Vitest和build通过。
20. 全局首页企业场景卡片（含其数字区域）进入真实企业首页；MOX/TOB/ISP&大企三卡进入约定子页。
21. 企业专项、三卡和空间拓展在桌面与窄窗口下不重叠、长金额及单位不遮挡；桌面空间拓展左/右边缘分别对齐MOX/ISP&大企卡片横向中心位置，在TOB下方居中且与上排等高。
22. 三卡/空间拓展真实页面使用与全局首页场景卡一致的共享展示组件/token，数字层级一致；全局首页其他场景外观和路由无回归。
23. 使用五模块金额不相同的隔离 fixture 验证真实汇总 API 和 DB 映射，包含小数、0、NULL、多条记录/历史关系，识别错误字段、漏模块、倍增及单位重复换算。
24. 子页金额变更后返回首页，真实汇总更新；加载和失败不冒充0或占位实时金额。

人工视觉验收由用户执行。

---

## 14. 当前实施范围

本次仅允许：
- “企业专项”标题颜色复用其他专项标题的蓝色；
- 企业首页目标/实时卡内横向布局；
- 实时金额M$后缀及必要共享展示适配；
- 空间拓展按MOX/ISP&大企卡片横向中心位置限定左右边界、居中、等高及响应式间距；
- 实际需要的中性共享样式/展示参数；
- 直接相关测试、视觉证据和实施文档。

既有汇总Contract/API、数据库、统计公式、字段契约、权限、路由目标和刷新机制保持。读取这些实现只用于确认绑定和回归，不据第16节历史范围重新建设。
不新增Heatmap、达成率、进度条、目标推算、明细表或其他指标；不改SQL、Excel或真实业务数据。发现已有真实功能问题记录证据，按对应既有任务处理，不借展示调整扩大修改范围。

---

## 15. 完成标准

只有以下全部满足才可完成：

- 首页页面结构和样式符合本Authority，“企业专项”标题蓝色与其他专项一致；
- 三张卡只显示横向并列的目标与实时，目标在左、实时在右；
- 目标为 `xx M$`，实时金额使用相同M$后缀且不重复换算；
- 空间拓展桌面边界对齐MOX/ISP&大企卡片各自横向中心位置、居中且与上排等高；
- 实时与空间拓展绑定真实聚合；
- 页面不存在达成率、进度条和未确认指标；
- 页面不存在首页 Heatmap 和无意义空白占位；
- 汇总 API 不加载完整明细；
- 自动测试和 build 通过；
- 独立审查通过；
- 用户人工验收通过。

---

## 16. 首页 V4 原始实施步骤、边界和产物（保留实施基线）

原跳转修复的WRITE_SCOPE、计划和实施报告见 `remediation/enterprise-home-route-blocker-repair-v1.md`。本节保留历史实施基线；当前展示修正按第18节执行，不继承本节原始API/DB建设范围，不重复已完成建设。

用户已反馈前轮核对完成并人工检查“基本没什么问题”，本轮进入上述具体首页调整。该反馈不等于本文件的新需求已经实现，也不能把历史审查结果改写为已验证本轮新 HEAD。

固定环境：
- 代码目录：D:\BattleMap\battle-map
- 代码分支：feature/enterprise-battle-map
- Authority：D:\BattleMap\BattleMapenterprise-authority
- 更新：git -C "D:\BattleMap\BattleMapenterprise-authority" pull --ff-only origin enterprise-battle-map-authority

### 16.1 先恢复现状

记录 BASE_HEAD、AUTHORITY_HEAD 和工作树状态，保留既有变更，只有一个写 Agent；不 reset/rebase/clean。读取本 V4、共享架构 V5、五模块当前金额与空间字段/Metric Contract，以及最新本地完整独立审查报告。

定位并记录：
- 全局首页“骨干场景 / 企业场景 / 单域自治”实际卡片和数字组件、style token、事件入口；
- 企业首页企业专项、三卡、空间拓展真实布局、实际金额绑定和 placeholder 来源；
- 现有汇总 Contract、API、database.js、五模块 canonical key→DB列及单位；
- 现有 router、真实目标页面和导航行为；
- 重叠的实际原因及需要修改的最小共享展示边界。

本轮无需重新实施此前已经正确的共享表单/其他操作链；核实并保留即可。不要把旧索引的“企业首页最后建设/DEFERRED”当成本轮阻塞，用户当前已明确授权首页工作，V4 的当前范围优先。

### 16.2 先计划，后直接实施

计划写到：
docs/enterprise/implementation/enterprise-home-polish-v4-plan.md

内容至少包括真实文件/函数位置、路由映射表、金额与空间汇总映射表、共享样式来源、布局修复、精确 WRITE_SCOPE、验证步骤。
按本 V4 完成自检后直接实施，无需用户再批准普通实现选择。

实施顺序：
1. 复用全局场景卡展示机制，修复布局间距和重叠；
2. 接通或修正现有服务端汇总，保留目标占位，实时及空间拓展显示真实值；
3. 修正全局企业场景入口和三张子模块卡片跳转；
4. 检查加载/空数据/错误/返回刷新；
5. 完成验证与同步文档。

空间拓展第7节规则继续有效，不因本轮样式要求变更其公式。业务字段实际缺失或 Contract 冲突时记录具体证据，不临时猜字段、单位或新计算规则；其余独立调整继续。

### 16.3 验证与交付

对这轮新增金额聚合、API和路由做有意义的自动测试，消费真实生产实现。间距和数字样式使用本地运行页面视觉检查，保留修复前后截图和检查窗口尺寸；有现成浏览器测试能力时可补布局边界检查，不为纯样式写大量实现镜像测试或引入新测试框架。
必要回归包括全局首页其他场景导航与展示、企业首页汇总/路由、被修改共享组件的现有消费者。运行项目既有 full Vitest、build和已有 lint/typecheck，记录命令、退出码；DB测试用隔离数据，不修改用户真实业务数据。

报告写到：
docs/enterprise/implementation/enterprise-home-polish-v4-report.md
证据目录：
docs/enterprise/implementation/evidence/enterprise-home-polish-v4/<BASE_HEAD>/

报告记录实际路由、五模块金额字段/DB单位映射、样式共享来源、截图、样例聚合对照、测试和剩余问题。同名产物属于旧执行时先保留历史副本。
仅提交本轮明确拥有的代码、测试、计划/报告和证据，避免 git add 全仓；不 push/merge。报告SHA自引用按现有 IMPLEMENTATION_HEAD + 最终 docs-only 提交规则记录。

实施者仅声明 IMPLEMENTED，不改写历史独立审查结论。下一步针对新 HEAD 进行本 V4 首页范围的独立核验及受影响回归，再由用户人工确认页面；如修改触及已有共享业务机制，按实际影响扩大到对应既有门禁。无需为只读到的所有模块重做无关重构。

最终短回执：
RESULT=COMPLETE/PARTIAL/BLOCKED
STATUS=IMPLEMENTED
BASE_HEAD=
IMPLEMENTATION_HEAD=
FINAL_HEAD=
SECTION_SPACING=PASS/FAIL/NOT_CHECKED
GLOBAL_SCENE_STYLE_REUSE=PASS/FAIL
REALTIME_ORDERED_AMOUNT_SUM=PASS/FAIL/NOT_RUN
EXPANSION_SUMMARY=PASS/FAIL/NOT_RUN
GLOBAL_ENTERPRISE_SCENE_ROUTE=PASS/FAIL/NOT_RUN
MODULE_CARD_ROUTES=PASS/FAIL/NOT_RUN
LOADING_ZERO_ERROR_REFRESH=PASS/FAIL/NOT_RUN
FULL_TESTS=PASS/FAIL/NOT_RUN
BUILD=PASS/FAIL/NOT_RUN
REPORT_PATH=
BLOCKERS=NONE或具体项
NEXT=HOME_V4_INDEPENDENT_REVIEW/CONTINUE_IMPLEMENTATION

无需上传本地代码、报告或业务数据。

---

## 17. V4 实施后独立核验与人工验收

用户已报告首页跳转修复完成，当前联合独立复核入口及报告路径以第0节所引 V1 为准；以下为继续适用的首页核验要求，旧单任务报告保留历史。新独立 Agent 负责本节；实施报告的 PASS 不是审查事实。此次只审查本轮首页范围与实际受影响消费者，不机械重跑无关五模块整改。

### 17.1 输入和固定状态

在第16节固定目录更新 Authority 并记录 AUTHORITY_HEAD。读取本V4全部要求、本地 enterprise-home-polish-v4-plan.md、enterprise-home-polish-v4-report.md、对应证据、当前真实代码及必要字段/Metric Contract。
核对 feature/enterprise-battle-map、工作树状态、BASE_HEAD/IMPLEMENTATION_HEAD/FINAL_HEAD，固定新的 REVIEWED_HEAD。报告提交与实现提交不同时确认 docs-only 差异。
受审代码/配置/测试必须已提交且无并发写入；识别并保留已知报告产物，不覆盖其他修改。审查期间不修改生产代码、测试、Migration、业务数据或Authority，不提交、不push。
若Authority拉取失败，核实实际文件版本和缺少的要求；不能把网络失败当业务缺陷，也不能把未知版本称为最新。缺失内容无法取得时只标记对应证据缺口，继续可完成项。

### 17.2 核验顺序

1. 布局与样式：真实企业首页专项文案自然撑高，与三卡、空间拓展有间隔；桌面与窄窗口、长数字/换行文案不重叠。确认三卡及空间拓展消费全局首页场景卡/数字的实际共享组件或token，非仅复制近似CSS。核查全局其他场景未回归。
2. 金额：从真实首页请求追到API与数据库，独立核实“已下单金额”canonical key/DB列及M$单位；MOX、TOB分别求和，ISP&大企等于ISP+电力+大企。以非零且各模块不同的隔离测试数据或已有可信fixture核对，不以全部0证明正确。排查错字段、遗漏、join倍增、重复单位换算和未授权过滤。
3. 空间拓展：严格执行第7节的整体空间求和、跟踪项目数和已孵化AND跟踪计数，不能误用已下单金额。
4. 路由：通过真实点击和当前router核实全局企业场景→企业首页；MOX→MOX、TOB→TOB、ISP&大企→ISP；数字区域点击同目标，键盘操作及返回导航正常。不凭字符串搜索或未被页面调用的helper作结论。
5. 页面状态：目标可为xx M$，实时不为xx/随机值；加载、0、失败有区分，API失败不伪装0；子页金额变更后返回首页汇总更新。不得读取五份完整明细在前端求和。
6. 证据与测试：重新运行本轮金额/API/路由测试及被修改共享组件的受影响回归，检查测试是否验证真实实现。核对实施阶段full Vitest/build及已有lint/typecheck的命令、退出码和对应代码快照；证据完整且对应同一实现时无需仅因报告提交或本次只读审查重复全量。缺失、失败、源码变化或实际影响无法排除时，再重跑必要范围。保留作出取舍的依据。

使用项目现有浏览器能力观察实际页面，并保存截图/尺寸。无法进行视觉检查时标记 VISUAL_CHECK=NOT_RUN，转入明确的人工检查项；不能声称布局已验证。用户最终视觉确认仍单独记账。测试/API写入只使用隔离数据，不修改真实业务库。

### 17.3 报告与判定

单独进行首页审查时的报告路径（本轮联合复核改用其专属报告，原报告保留）：
D:\BattleMap\battle-map\docs\enterprise\reviews\enterprise-home-v4-independent-review.md
证据：
D:\BattleMap\battle-map\docs\enterprise\reviews\evidence\enterprise-home-v4\<REVIEWED_HEAD>\

已有报告先原样保存至 reviews/history/enterprise-home-v4-independent-review-before-<REVIEWED_HEAD>.md，同名不同内容不得覆盖。
报告包含版本/HEAD、需求逐项矩阵、实际共享组件来源、金额/空间字段和汇总对照、路由表、页面截图/尺寸、测试日志、未运行项及finding。
每个finding记录ID、严重度、实际位置/生产路径、违反的V4条款、复现证据、影响及修复方向。审查中不修复，发现一项缺陷后继续其他独立检查。
结束复核HEAD和受审文件稳定；只允许上述报告/证据变更和已识别的临时输出。

判定：
- PASS：本轮必需核验完成，无blocking finding，受审HEAD/代码稳定；人工最终确认仍PENDING。
- FAIL：确认违反本V4的阻塞实现/测试缺陷，NEXT=HOME_V4_REMEDIATION。
- PARTIAL：必要证据/执行条件缺失，明确缺项，NEXT=COMPLETE_HOME_V4_REVIEW。仅最终人工视觉确认未进行，不把已完成的独立技术核验判失败。

最终短回执：
RESULT=PASS/FAIL/PARTIAL
REVIEWED_HEAD=
AUTHORITY_HEAD=
SPACING_AND_STYLE=PASS/FAIL/NOT_RUN
REALTIME_ORDERED_AMOUNT=PASS/FAIL/NOT_RUN
EXPANSION_METRICS=PASS/FAIL/NOT_RUN
ROUTES=PASS/FAIL/NOT_RUN
LOADING_ZERO_ERROR_REFRESH=PASS/FAIL/NOT_RUN
AFFECTED_REGRESSION=PASS/FAIL/NOT_RUN
FULL_TEST_BUILD_EVIDENCE=VALID/INVALID/MISSING
HEAD_AND_SOURCE_UNCHANGED=YES/NO
BLOCKING_FINDINGS=NONE或ID
REMAINING_CHECKS=NONE或具体项
REPORT_PATH=
MANUAL_ACCEPTANCE=PENDING
NEXT=USER_MANUAL_ACCEPTANCE/HOME_V4_REMEDIATION/COMPLETE_HOME_V4_REVIEW

### 17.4 用户人工确认

独立核验完成后，让用户在实际页面确认：
- 企业专项、三卡和空间拓展的间距、数字样式；
- 目标/实时横向并列，目标占位与实时金额均带M$且无重复换算；
- 空间拓展左右边界对齐MOX/ISP&大企卡片横向中心，桌面居中且与上排等高；
- 全局企业场景和三卡点击跳转；
- 返回首页后金额刷新。

人工确认结果记录到同一报告，不替用户声称通过。用户确认无问题后首页V4完成，再按Authority推进剩余业务需求；不自动假设Excel V0.2调查或首页外任务已完成。

---

## 18. 本次卡内并列、M$单位、空间拓展尺寸及专项标题颜色修正

### 18.1 输入、范围与本地产物

先更新：
git -C "D:\BattleMap\BattleMapenterprise-authority" pull --ff-only origin enterprise-battle-map-authority

在Authority的docs/enterprise-battle-map下读取authority-index.md、本文件第0/4—8/14/18节、integration/enterprise-review-snapshot-preparation-v1.md及联合独立复核第9/11节。
在D:\BattleMap\battle-map读取适用AGENTS.md与最近报告，记录BASE_HEAD、AUTHORITY_HEAD、分支/工作树及实际运行来源；先盘点未提交改动，保留既有选项/行业/迁移任务进度，不并发改变受审快照。

固定本地产物：
- docs/enterprise/implementation/enterprise-home-card-layout-unit-v1-plan.md
- docs/enterprise/implementation/enterprise-home-card-layout-unit-v1-report.md
- docs/enterprise/implementation/evidence/enterprise-home-card-layout-unit-v1/<BASE_HEAD>/

先定位企业首页实际卡片、指标布局、formatter/单位接线、空间拓展容器、全局场景共享组件和CSS token，以及其他实际“xx专项”标题的蓝色class/token。记录问题入口及改动前的视口/截图，写最小文件级WRITE_SCOPE，按第14节直接实施。

### 18.2 实施与验证

1. 三卡内部目标在左、实时在右，两组横向并列；不改为两张卡，也不保留上下两整行。
2. 实时沿用现有数值，仅在共享显示层呈现M$后缀且只出现一次。核实formatter是否已含单位，避免重复；保留原精度，不乘除一百万，不改API数值类型。
3. 空间拓展左/右边缘分别对齐上排MOX/ISP&大企卡片各自横向中心位置，整体在TOB下方居中，不缩成单卡宽；常规桌面高度与上排一致。复用现有共享尺寸/内边距，保留三指标与项目计数单位；窄屏按内容自适应，避免硬裁切。
4. “企业专项”标题复用其他“xx专项”标题的现有蓝色class/token，核对同一主题下真实计算颜色一致；标题/定义文案内容及其他文本颜色保持。普通点击卡片及两组数字仍到原子页；企业专项、三卡、空间拓展的间距及共享全局场景外观保持正常。
5. 用实际页面记录桌面与窄窗口的截图/尺寸，同时记录专项标题参照及颜色来源：确认两组并排、金额单位、空间拓展左右边缘与上排卡片横向中心的对齐/居中/高度；用0、小数及代表性长金额确认无重复单位、换算或溢出。使用隔离fixture/测试数据，不改真实业务库。
6. 运行实际受影响展示/formatter/路由回归与项目必要build。纯CSS不新增实现镜像测试或测试框架；可复用同一最终实现的有效汇总/DB证据，不机械重跑所有历史模块测试。共享展示组件被改时核验其真实消费者，保留global首页原布局/行为。
7. 未能观察真实页面则记录VISUAL_CHECK=NOT_RUN，不能仅凭类名/静态模板判断布局通过。代码核验和用户最终视觉确认分别记录。

### 18.3 提交与交接

报告记录真实文件/共享组件、专项标题参照及蓝色来源、布局和单位改动、使用的宽度/高度规则、截图及视口、相关测试命令/退出码、复用证据与剩余问题。旧同名报告保留历史。
按快照准备V1精确本地提交本次实现/测试/必要文档，固定包含本次改动的新REVIEW_CANDIDATE_HEAD和REVIEW_WORKTREE；不全量add、不reset/clean、不push。旧候选及已知finding保留，独立复核不在脏代码上继续。
实施只声明IMPLEMENTED/PARTIAL/BLOCKED，新会话按联合复核第9/11节独立核验。

短回执：
RESULT=
IMPLEMENTATION_HEAD=
REVIEW_CANDIDATE_HEAD=
REVIEW_WORKTREE=
ENTERPRISE_SPECIAL_TITLE_BLUE_MATCH=
TARGET_REALTIME_SIDE_BY_SIDE=
REALTIME_MUSD_UNIT_ONCE=
EXPANSION_EDGES_AT_MOX_ISP_CENTERS_AND_EQUAL_HEIGHT=
VISUAL_CHECK=
AFFECTED_TESTS_AND_BUILD=
REPORT_PATH=
REMAINING=
