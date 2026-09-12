---
title: AFP Benchmark Protocol v0.1
type: page
url: /zh/evaluations/protocol/
summary: AFP 與基線進行公平比較的公開文字層 pilot protocol。
---

## 目的

這個 pilot 不預設 AFP 比較好，而是先建立可被檢查與重現的比較契約。

核心問題是：**在相同模型與相同可見輸入下，AFP 是否能降低可觀察的可靠性失敗，而且改善幅度足以合理化額外結構？**

## 測試邊界

Protocol v0.1 只測文字層。它不測即時網路搜尋、檔案操作、外部 Agent 行動、生產環境流量或端到端安全，因此不能把這個 pilot 的結果宣稱成完整 Agent 能力證明。

## 四組比較

1. **A · Model only** — 不加入額外治理結構。
2. **B · General instructions** — 一般任務／Custom Instructions。
3. **C · AFP** — 在相同任務上使用 AFP 工作流程。
4. **D · AFP + governance controls** — AFP 加上明確 evidence gate、覆核條件與必要的 regression check。

比較時應盡可能固定 **模型、任務、工具、證據集合與評估日期**。

## 先驗證有效性，再評品質

每次 run 先分類，避免把供應商或測試設計問題算成模型失敗。公開狀態包含 `MODEL_PASS`、`MODEL_FAIL`、`PROVIDER_BLOCK`、`INFRA_ERROR`、`INVALID_TEST` 與 `GRADER_DISPUTE`。

模型品質通過率只以 `MODEL_PASS` 與 `MODEL_FAIL` 計算；其他狀態必須另外保留並公開。

## 最低報告要求

依情況保留任務／rubric 分數、嚴重或致命失敗、重複執行變異、高信心但缺乏支持的主張、遺漏反證、工具呼叫、token 使用、完成時間、raw output、grader 理由與排除案例。

## 可重現性

固定的 machine-readable pilot pack 與 runner 位於公開 repository 的 `benchmarks/afp-v0.1/`。Validate 模式不呼叫模型 API；Live 模式必須手動啟動，而且 raw output 在完成評分與 validity check 前不能被當成 benchmark 結論。

[查看 GitHub benchmark 檔案](https://github.com/huikai79/afp-framework-site/tree/main/benchmarks/afp-v0.1)

## 目前狀態

**Protocol 已公開；benchmark 分數尚未公布。** 負面、混合、爭議與被排除的結果，應與正面結果一起保留。
