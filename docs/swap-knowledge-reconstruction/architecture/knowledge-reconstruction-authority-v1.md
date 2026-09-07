# Swap / GBrain Knowledge Reconstruction Authority V1

> **状态：CURRENT**  
> **适用范围：** Swap / Microwave 知识库重建支线  
> **入口：** `docs/swap-knowledge-reconstruction/authority-index.md`

## 1. 目标

以 GBrain 为本地知识运行层，重建高质量、可追溯、可持续更新的 Swap 项目知识与 Microwave 领域知识。

长期目标不是“生成大量 Wiki”，而是让本地 Agent 面对真实需求时能够快速恢复：

- 当前业务语义；
- 设备 / 版本 / 单板 / 槽位 / 端口 / Feature / MML 关系；
- Swap 的配置输入、解析、转换、扩展与 GET→SET 处理架构；
- 典型新版本、新设备、新单板、新 Feature 适配的影响路径；
- 重要结论的真实 Evidence 与未知项。

## 2. 物理边界

### 2.1 正式 Knowledge Repo

- `D:\gbrain-knowledge\microwave-kb\`
  - Microwave Domain Knowledge
  - 独立 Git Repository
  - 独立 GBrain Source：`microwave-kb`

- `D:\gbrain-knowledge\swap-kb\`
  - Swap Project Knowledge
  - 独立 Git Repository
  - 独立 GBrain Source：`swap-kb`

Markdown + Git history 是正式长期知识资产；GBrain/PGLite 是检索与运行层，不直接作为唯一知识 Authority。

### 2.2 Raw Sources

`D:\swap-knowledge-sources\`

用于保存原始资料，包括但不限于：

- MML 手册 / 参数资料；
- Feature 配置资料；
- Device / Version / Board / Port 资料；
- Excel；
- Requirement / Design；
- Sample；
- Legacy Wiki；
- 后续新增产品资料。

Raw Source 不能因为“被导入”就自动升级成 Current Truth。

### 2.3 本地治理 / Evidence

Swap 本地仓库中的：

`.ai-local/knowledge/reconstruction/`

用于保存 Survey、Review、Remediation、Baseline、Batch、Evidence Map、Query Validation、Knowledge Gap 等本地执行治理产物。

这些文件不是正式 Brain Knowledge Page。

### 2.4 GitHub Authority Carrier

远程 Authority 维护在：

`olu37776-bit/excel-arrival-tool`

目录：

`docs/swap-knowledge-reconstruction/`

该目录只承担本支线远程 Authority，不改变 Excel 工具自身产品/代码 Authority。

## 3. Knowledge Boundary

### 3.1 `microwave-kb`

负责“正确的 Microwave 设备与配置世界是什么”。

长期对象包括但不限于：

- Device / Product Family；
- Version；
- Controller / Board；
- Slot / Port / Interface；
- Capability；
- Feature（如 XPIC、EPLA、CCIC 等）；
- MML Command / Parameter / Value；
- Applicability / Constraint；
- Hardware / Feature / MML 的真实关系。

Device、Board、Port、Feature、MML 高度关联，当前不拆成多个 GBrain Source。

### 3.2 `swap-kb`

负责“Swap 如何理解、校验、转换并生成这些配置”。

长期对象包括但不限于：

- Project Context；
- 用户业务场景（SCC / IF / Data / CCIC 等）；
- XPIC 等业务能力在 Swap 中的使用；
- Source Configuration；
- NCE 采集日志 → GET MML；
- Device DB → MML Normalization；
- legacy C++ parser / Java supplemental parser；
- 前端初始化配置聚合阶段；
- `SwapParam`；
- `SwapService#doTransfer`；
- `AbstractTransfer` / `*Module`；
- Module txt relevant-MML 声明；
- Device-specific specialization / XML applicability；
- Migration / Extension / Expansion；
- Module result merge；
- JNI / C++ / `cfg.ini` GET→SET；
- Verification / Change Impact / Project Decision。

同一领域 Truth 只保留一个 Primary Home；`swap-kb` 不复制 `microwave-kb` 已经拥有的完整领域 Current Truth。

## 4. 已知核心业务基线

### 4.1 源配置入口

当前至少存在两类源配置：

1. NCE 采集日志：主要包含设备 GET MML 现网配置；
2. Device DB：专有配置格式，需要先解析 / 规范化为 MML。

Device DB → MML 历史上存在 C++ parser（通常通过 `.so` / `.dll` 使用），Swap Java 侧存在补充解析能力；其真实覆盖、协作、合并、优先级必须以当前源码 / 配置 / 测试 Evidence 为准，禁止凭历史描述推断。

两类输入在统一 Source MML 语义层汇合后进入公共后续转换链。

### 4.2 用户与 Processing Architecture

前端用户主要感知 SCC / IF / Data / CCIC 等配置区域；XPIC 是重要 Feature / 可选能力，并存在扩容场景。IF 还存在配置复用等能力。

前端表格数据及其他输入会聚合到 `SwapParam`，各 Processing Module 读取该共享上下文并结合相关 GET MML 做校验、耦合判断、参数修改或配置扩展。

`Feature ≠ Processing Module`  
`Frontend Scenario ≠ Processing Module`  
`MML ≠ Processing Module`

Module txt 表示该 Module 需要接收 / 关注的相关 GET MML，不自动表示 unique ownership。同一 GET MML 可以被多个 Module 读取。

### 4.3 输出链

Processing Module 主要承担业务语义层面的配置读取、校验、参数迁移与配置新增 / 扩展；模块结果由 `SwapService#doTransfer` 等当前实现路径合并。

最终 GET-form → SET-form 的格式转换由 JNI / C++ / `cfg.ini` 映射层完成；不得无 Evidence 地把普通 Module 描述成最终 SET formatter。

## 5. Source Authority

不同事实类型采用不同第一事实源：

| 事实类型 | 第一事实源 |
|---|---|
| 当前 Swap 如何实现 | 当前源码 / 配置 |
| 实际运行行为 | Test / E2E / Runtime Evidence |
| Device / Version / Board / Port capability | 正式设备资料 / Excel / 产品资料 |
| MML Command / Parameter / Value 语义 | 正式 MML 手册 / 配置指南 |
| Microwave Feature 领域语义 | 正式 Feature / 产品资料 |
| Requirement intent | Requirement / Design |
| 旧 LLM Wiki | clue only |

当 Source 冲突或证据不足时：

- 不得猜测；
- 不得用较弱 Evidence 覆盖较强 Authority；
- 记录 Conflict / Knowledge Gap；
- 必要时返回 `NEED_USER_CONFIRMATION` 或 `BLOCKED_BY_AUTHORITY`。

## 6. 语言与术语

正式 `microwave-kb` / `swap-kb` 以中文为主。

以下保持原始 canonical form：

- Java class / method / field；
- package；
- config / XML key；
- MML Command / Parameter；
- Device / Board 型号；
- Feature 缩写。

同一实体维护 canonical name + aliases。前端叫法、代码叫法、产品资料叫法不一致时，建立 alias / mapping，不重复创建实体。

## 7. Knowledge Construction Convention

后续 Agent 必须优先读取本地已验证的：

`.ai-local/knowledge/reconstruction/conventions/v1/`

原则包括：

- Brain-first；
- 已有 Primary Page 优先 UPDATE；
- 真正新的长期对象才 CREATE；
- Current Truth 的强度不得超过 Evidence；
- Raw Source 不复制进 Knowledge Repo；
- 页面不是普通源码翻译；
- Unknown / Gap 不允许用猜测填满；
- 更新 Current Truth 时保留 Timeline / Evidence；
- Query Validation 是每批知识建设的必要验收之一。

如 Convention 与 CURRENT GitHub Authority 冲突，以 CURRENT GitHub Authority 为准，并记录冲突等待 Authority 更新，不得静默改写规则。

## 8. Reconstruction / Verification 角色分离

### Reconstruction / Remediation Agent

可以：

- 调查本地源码 / 配置 / Raw Sources；
- 修改正式 Knowledge Repo；
- 更新 Evidence / Query Validation / Implementation Report；
- commit Knowledge Repo。

只能声明：`IMPLEMENTED` / `REMEDIATED`。

### Independent Verification Agent

必须：

- 固定 REVIEWED_HEAD；
- 默认只读；
- 重新读取 CURRENT Authority；
- 独立检查 Knowledge Page、真实 Source、Evidence 和查询结果；
- 回归旧 Findings；
- 主动寻找新的阻塞 Finding。

只有 Independent Verification 可以声明：`VERIFIED`。

新 HEAD 必须重新证明，旧 HEAD 的 PASS 不自动继承。

## 9. Evidence 规则

实施报告中的 `PASS`、`0 findings`、`canonical`、`covered`、`shared` 等结论必须可以映射到真实 Evidence。

推荐使用：

- `CODE_EVIDENCE=`
- `SOURCE_EVIDENCE=`
- `TEST_EVIDENCE=`
- `QUERY_EVIDENCE=`
- `GIT_EVIDENCE=`
- `GBRAIN_EVIDENCE=`

报告与真实代码 / Source / Independent Review 冲突时，以真实 Evidence 与 Independent Review 为准。

## 10. 阶段推进

复杂 Batch 的长期设计必须先成为 GitHub CURRENT Task Authority，再由本地 Agent 拉取执行。

正常顺序：

`Authority → Reconstruction → commit → Independent Review → Remediation (if needed) → new HEAD → Independent Verification → Baseline Update → next task`

聊天提示词只负责：

- 拉取 Authority；
- 指向 CURRENT Task；
- 要求严格执行；
- 返回短回执。

## 11. 当前阶段

当前阶段以 `authority-index.md` 为准。

在 Local State Reconciliation 完成前，不假设 Batch #2 / Batch #3 已经最终 VERIFIED，不开始下一批知识建设。
