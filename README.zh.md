[English](README.md)

# 反脆弱提示框架（AFP）· SafeLoop

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

AFP／SafeLoop 是持續發展中的開放框架，目標是讓重要或可重複使用的 AI 工作流程更容易被檢查、挑戰、驗證、修正與重新測試。

## 目前公開規格

**假設 → 證據 → 反證 → 決策 → 驗證 → 修正**

SafeLoop 是包在這套流程外的回饋迴路：**產出 → 檢查 → 挑戰 → 驗證 → 修正 → 重新測試**。

AFP 本身不保證事實一定正確、安全、符合法規，也不代表已證明模型表現會更好。高風險或專業領域仍需要相應的領域控制與合格真人覆核。

## 目前證據狀態

- 公開規格：working specification。
- 失敗案例：已公開初始 taxonomy；可重現案例仍在建立。
- 評估：Pilot Protocol v0.1 已公開。
- Benchmark 分數：尚未公布。

在有可重現比較支持以前，不應把 AFP 描述成已經實證優於其他方法。

## Repository 結構

- `content/specification/` — 目前公開規格。
- `content/evaluations/` — 評估設計、protocol 與 pilot 狀態。
- `content/failure-cases/` — 失敗分類與後續可重現案例。
- `benchmarks/afp-v0.1/` — 固定的 pilot pack 與 raw-output runner。
- `system-prompts/` 與 2025 提示頁 — 歷史 Prompt 治理版本，不是目前完整規格。
- `static/uploads/` — 歷史白皮書 PDF；2025 PDF 屬概念版典藏。

## 可重現性

Benchmark 的 validate 模式不會呼叫模型 API。Live 模式必須手動啟動、明確指定模型，並使用 repository secret；產生的 raw output 仍需後續評分，不能單靠生成結果宣稱 benchmark 成效。

## 如何參與

可透過 GitHub Issue 或 Pull Request 審查公開 protocol、重現 benchmark pack、提出可重現失敗案例，或改善文件與實作。請勿在公開討論中張貼密碼、金鑰或敏感個人資料。

## 授權

AFP 自有文字與文件採 Creative Commons Attribution 4.0 International（CC BY 4.0）授權；第三方軟體與模板元件仍依各自授權條款。
