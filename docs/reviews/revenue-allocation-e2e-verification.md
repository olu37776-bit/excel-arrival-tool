# 收入分配重构端到端实施验证报告

- 日期：2026-08-27
- 仓库：`olu37776-bit/excel-arrival-tool`
- 分支：`refactor/revenue-allocation-v1`
- Draft PR：`#25`
- 实施基线：`85cc86a5f9f33710940746c4c1ab8a4dcbef530c`
- 最终 E2E 实施提交（生产代码、测试、配置和 workflow）：`09b2319b3b17b708af60d31e1929c254b363852f`
- GitHub Actions：`https://github.com/olu37776-bit/excel-arrival-tool/actions/runs/33053288511`

## 1. E2E范围和结论

本次将已经通过 Gate 的 Phase 1 领域链和 Phase 2 冻结契约直接接入生产 `run_pipeline`，完成：

```text
源数据
→ ContractFinancialFact
→ DemandRecord
→ FulfillmentProjection
→ RevenueAllocationCandidate
→ RevenueAllocationDecision
→ ContractAllocationSummary
→ MonthlyRevenuePosting
→ RPD/CPD月度汇总与待处理收入
→ 新工作簿
→ 用户填写金额/备注并保存
→ PreviousResultReader重新导入
→ 精确继承、变化诊断和重新汇总
```

E2E Gate：**PASS**。

## 2. 领域模型和服务边界

保留并正式用于生产链：

- `ContractFinancialFact`：一合同一条，唯一权威金额事实；`revenue_forecast = legacy_amount + monthly_new_order`。
- `DemandRecord`：去重后的要货证据；不包含合同金额或人工分配金额。
- `FulfillmentProjection`：合同号 + 履行供应中心；沿用 Phase 1 日期、运输周期、到货日期、收入年月、收入分段和备货三态规则。
- `CONTRACT_ONLY_NO_DEMAND`：保留履行占位，但不生成虚构分配候选。

新增并接入：

- `RevenueAllocationCandidate`
- `ManualAllocationSnapshot`
- `PreviousRunMetadata`
- `PreviousContractState`
- `PreviousCandidateState`
- `PreviousRunState`
- `OrphanedPreviousAllocation`
- `RevenueAllocationDecision`
- `ContractAllocationSummary`
- `PendingRevenueRow`
- `MonthlyRevenuePosting`
- `MonthlyRevenueSummaryRow`

主要服务：

- `AllocationCandidateBuilder`
- `CandidateHistoryService`
- `AllocationService`
- `MonthlyRevenueService`
- `PreviousResultReader`
- `RevenueDatasetBuilder`

旧 `RevenueEngine / BaseRow / PreviousData / LegacyProjectionAdapter` 未删除，继续用于 v0.8 兼容、跨期适配和 Phase 1 Golden；不再作为新工作簿金额主数据流。

## 3. candidate ID v1和projection fingerprint v1

candidate ID v1严格使用冻结算法：

```text
payload = [
  "1",
  normalize_text(contract_no),
  normalize_lookup(supply_center),
  normalize_text(row_kind).upper()
]

canonical_json = json.dumps(
  payload,
  ensure_ascii=False,
  separators=(",", ":")
)

allocation_candidate_id
= "RAC-v1-" + sha256(canonical_json UTF-8).hexdigest()
```

固定测试向量：

```text
["1","C001","sc-a","DEMAND_CENTER"]
→ RAC-v1-adadc699ea166aac0e020e8640d57a9a6e843fd59e454b6143d6be9109d1bf77
```

projection fingerprint使用独立、固定字段集合和`sort_keys=True` canonical JSON；固定测试向量为：

```text
FP-v1-ff8e0014d505880bb6ca23663bad2e3ba53948c6c63657d0a9f578d79b09fd4f
```

测试证明：日期和履行内容变化改变 fingerprint 但不改变candidate ID；`demand_record_id`、源行摘要、源文件/Sheet/行号、合同金额和人工金额不进入candidate ID或fingerprint。

## 4. PreviousRunState和历史继承

新格式使用 metadata schema `4`，保存：

- `schema_version`
- `run_id`
- `rules_version`
- `candidate_id_version`
- `projection_fingerprint_version`
- 金额精度
- 数据集与Sheet映射
- 字段ID与显示名
- `row_kind`
- 源文件SHA-256指纹
- UTC生成时间

`PreviousResultReader`与源数据读取器解耦。读取时按 `_tool_meta` 的稳定字段ID和当期工作簿显示名定位，因此支持列移动、插入非关键列和配置显示名变化。

历史规则验证：

- ID精确命中：继承手工金额和备注，保留明确数值0，记录`inherited_from_run_id`。
- 指纹变化：保留金额，`PROJECTION_CHANGED`、`projection_changed=Y`、`review_required=Y`。
- 合同预测变化：保留金额，不按比例调整，`CONTRACT_REVENUE_FORECAST_CHANGED`、`review_required=Y`。
- 新候选：`CANDIDATE_ADDED`，不做模糊金额迁移。
- 消失候选：`CANDIDATE_REMOVED`。
- 消失且上期金额状态为`VALUE`（包括0）：生成`ORPHANED_PREVIOUS_ALLOCATION`并进入待处理收入；金额和备注不迁移到其他中心。
- v0.8 schema 2/3：恢复旧FulfillmentProjection和跨期比较；金额状态为`UNAVAILABLE`，不转换旧三个人工月份字段。

## 5. 分配、部分分配和待处理规则

人工金额使用`UNAVAILABLE / BLANK / VALUE`三态，所有判断均显式检查状态，不使用truthy/falsy。

最终金额优先级：

```text
有效手工金额
→ 手工金额

否则存在自动金额
→ 自动金额

否则
→ 未分配
```

自动全额分配仅用于：合同预测非0、唯一正常候选、分段不是“需判断/不要货”。多候选合同没有平均分配、按记录数分配或尾差自动补齐。

验证覆盖：

- 空白和明确0；
- 正数和负数；
- 自动完整分配；
- 手工覆盖自动金额；
- 部分分配；
- 分配超额；
- 混合方向错误；
- 无要货合同；
- orphaned历史金额。

分配超额记录`ALLOCATION_EXCEEDS_FORECAST`，不截断、不修改任何候选，该合同不进入正式月度汇总。

## 6. MonthlyRevenuePosting和两套汇总

每个有`final_allocated_amount`的候选生成RPD和CPD两条Posting，两条记录引用同一金额；RPD和CPD不相加为业务总收入。

正式归月只允许“订未发”和“发未收”。需判断、不要货、分配超额、缺少当前口径月份、未分配、orphaned历史金额和无法归月的数据进入待处理。

如果一个口径月份为空，该口径进入待归月；另一口径有效时仍正常归月。

RPD/CPD月度汇总共同字段为：

1. 收入年月
2. BG
3. 地区部
4. 国家
5. 结转类型
6. 客户群
7. 当月预测
8. 订未发
9. 发未收
10. 未录入订货（合同数）

“未录入订货”按去重合同数统计，不作为金额。

## 7. 金额守恒证据

单元、E2E往返和独立生成工作簿均验证：

```text
每合同：
allocated_amount + unallocated_amount = revenue_forecast

RPD：
RPD已归月 + RPD待归月 + unallocated_amount = revenue_forecast

CPD：
CPD已归月 + CPD待归月 + unallocated_amount = revenue_forecast

每张月度汇总行：
当月预测 = 订未发 + 发未收

全量：
合同收入预测合计
= RPD已归月 + RPD待归月 + 全量未分配
= CPD已归月 + CPD待归月 + 全量未分配
```

超额或方向错误不会静默修正；它们通过异常和待处理显式保留。

## 8. 新工作簿

可见Sheet顺序：

1. 合同收入预测
2. 收入分配
3. RPD月度收入汇总
4. CPD月度收入汇总
5. 待处理收入
6. 收入归月明细
7. 要货记录明细
8. RPD跨月变化
9. CPD跨月变化
10. 供应需要提拉诉求清单粗表
11. 异常清单

隐藏Sheet：

- `_fulfillment_projection`
- `_tool_meta`

“合同收入预测”一合同一行，是合同金额唯一允许直接求和的权威Sheet。

“收入分配”包含完整合同、履行、历史、分配、变化、异常和待处理上下文。仅“手工分配金额”和“分配备注”使用黄色底色并允许用户编辑。“合同收入预测（参考，不可直接汇总）”带表头批注，明确禁止直接求和。

所有可见Sheet冻结首行、使用普通区域AutoFilter、无Structured Table；金额两位小数，日期`yyyy-mm-dd`，收入年月为`YYYY-MM`文本。

## 9. Excel往返证据

自动测试执行了真实 `.xlsx` 往返：

```text
第一次生成
→ 在收入分配Sheet插入非关键列并移动关键列位置
→ 填写部分金额、明确0、负数、超额金额和备注
→ 保存
→ 作为上一次结果重新导入
→ 按metadata字段ID恢复
→ 精确继承金额、0和备注
→ 重算合同分配状态
→ 重建RPD/CPD Posting与月度汇总
→ 保留未分配差额
→ 生成变化和orphan诊断
```

显示名变化通过单独配置回归验证；关键列不依赖固定列号。

## 10. 辅助分析和Issue #20

RPD跨月变化、CPD跨月变化和供应提拉继续消费`FulfillmentProjection`的兼容视图，不消费合同金额重复行。三张表在国家后包含“结转类型”，继续支持提前、延后、新增、取消、变为不要货和恢复要货；无要货占位不进入供应提拉。

Phase 1 Golden继续通过。Issue #20仍按最终解析国家判断结转类型，精确差异测试保留，没有宽泛忽略规则。

## 11. GUI

保留单页Tkinter GUI，仅做必要更新：

- “上一次成功结果”改为“上一次结果 / 已分配结果（可选）”；
- 说明可选择已填写手工金额和备注的上一次结果；
- 完成摘要显示合同数、候选数、已分配/待分配金额、RPD/CPD归月金额、待处理数和异常数；
- 四类源文件选择保持不变；当月订货继续可选；输出不能覆盖源文件或上一次结果。

## 12. 测试和构建结果

本地全量验证：

```text
PYTHONPATH=src python -m unittest discover -s tests
→ Ran 114 tests ... OK

python -m compileall -q src tests
→ PASS

git diff --check
→ PASS

python -m pip wheel . --no-deps --wheel-dir <临时目录>/wheel
→ PASS
```

新增测试覆盖candidate ID固定向量、fingerprint固定向量、PreviousRunState、历史继承、部分分配、超额、负数、守恒、Posting、两套汇总、未录入订货合同数、新Sheet/字段、完整Excel往返、v0.8兼容、AutoFilter和GUI smoke。Phase 1 Golden与Issue #20回归继续通过。

独立工作簿检查：

- 11个可见Sheet和2个隐藏Sheet均可解析；
- 所有可见Sheet的`auto_filter.ref`与数据区域一致；
- 所有可见Sheet冻结`A2`；
- OOXML包内无`xl/tables/`；
- 公式错误扫描为0；
- 两个编辑列黄色底色正确；
- 合同金额参考列表头批注存在；
- 五个核心Sheet完成自动渲染复核；渲染环境缺少中文字体，只把该步骤计为结构和布局自动验证。

## 13. GitHub Actions和Windows EXE

GitHub Actions run `33053288511`：**PASS**。

步骤全部通过：

- Windows依赖安装；
- 全量114项测试；
- `compileall`；
- wheel构建；
- PyInstaller GUI EXE构建；
- Windows环境执行`ExcelRevenueTool.exe --smoke-test`；
- 分支Artifact和SHA-256文件上传；
- 分支专属prerelease发布。

分支专属测试EXE：

```text
https://github.com/olu37776-bit/excel-arrival-tool/releases/download/revenue-e2e-09b2319/ExcelRevenueTool-RevenueE2E.exe
```

- 文件大小：12,884,635 bytes
- SHA-256：`e6f498cab9ed1ae35578266adcf35a13dd1969b7d7b8dcca5284e81f57dd65ce`
- 该文件是`refactor/revenue-allocation-v1`分支测试包，不是main正式版本；没有合并PR或发布正式Release。

## 14. 待本地验收和剩余风险

待本地验收：

- 使用真实四源文件验证业务金额、字段值和实际数据规模；
- 在Windows桌面Excel中打开、填写、保存、重开并执行“数据→清除”；
- 用真实已分配结果执行一次跨期继承和月度汇总业务签字。

这些是本地真实数据/桌面Excel验收项，不是当前自动化Gate失败。当前无已知代码阻塞项。

## 15. E2E Gate

```text
领域边界：PASS
candidate ID v1：PASS
projection fingerprint v1：PASS
PreviousRunState与v0.8兼容：PASS
人工/自动/部分/超额分配：PASS
RPD/CPD Posting和月度汇总：PASS
金额守恒：PASS
新工作簿：PASS
Excel自动往返：PASS
辅助分析迁移：PASS
GUI smoke：PASS
本地114项测试：PASS
GitHub Actions全量测试：PASS
Windows EXE构建和smoke：PASS

E2E Gate：PASS
```
