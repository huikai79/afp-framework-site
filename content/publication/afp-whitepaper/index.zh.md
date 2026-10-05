---
title: "AFP／SafeLoop 白皮書典藏（2025 概念版）"
authors:
  - 莊輝愷
date: 2025-09-09
publication_types: ["report"]
featured: true
links:
  - name: 目前規格
    url: /zh/specification/
  - name: 評估狀態
    url: /zh/evaluations/
  - name: 失敗案例
    url: /zh/failure-cases/
  - name: GitHub
    url: https://github.com/huikai79/afp-framework-site
---

## 文件狀態

**歷史概念版本 · 已被現行規格取代。** 2025 白皮書記錄 AFP 較早期以 Prompt 治理與「反脆弱」為中心的定位，目前保留作 provenance 與版本紀錄。它不是現行規格，也不能作為 AFP 已實證優於其他方法的證據。

目前對外主張、適用邊界、評估規則與 benchmark 狀態，請以[目前規格](/zh/specification/)、[評估](/zh/evaluations/)與[失敗案例](/zh/failure-cases/)頁面為準。

## 歷史典藏導讀

2025 原始 PDF 保持不變。本頁補上原始 artifact 當時沒有的現行版本脈絡。

| 2025 措辭／框架 | 目前解讀 |
|---|---|
| 「解決長對話漂移與幻覺」 | 屬歷史設計意圖。AFP 本身不保證事實正確。 |
| 「自我校正系統」 | 自行修正不等於正確；現行 AFP 要求明確驗證與重新測試。 |
| 「越用越強韌」／反脆弱 | 目前屬名稱與研究假說；未有可重現證據前，不作效果主張。 |
| 未來問題一律強制掛「非預測」標籤 | 不是現行通用 conformance 規則；應依證據、不確定性與任務風險處理。 |
| 「顯著提升合規性」 | 不是現行實證主張；合規仍需領域控制、合格人工覆核與適用的外部規則。 |
| GPT-4/5 vs Thinking Mode vs AFP Mode | 屬歷史 benchmark 框架；目前公開 Pilot 已改採受控 treatment，比較結果尚未正式發布。 |

## 原始 artifact 的處理方式

2025 原始 PDF 保持不變並留在 repository，以保存 provenance。由於原件製作時尚未包含現在的 Historical／Superseded 身分標示，本站不再把它作為主要下載入口。即使搜尋引擎或直接網址仍能找到原始檔，也不代表其中歷史主張恢復為現行 AFP 主張。

〔已知限制〕原始中文 PDF 在部分 PDF renderer 會出現 CJK 字形缺失。在能以不覆寫原件的方式發布 corrected archival binary 前，本 HTML 典藏頁是面向讀者的安全入口。

## 2026 Agentic 延伸：目前屬待評估範圍

目前文字層 Pilot 不能代替完整 Agent 安全證據。後續評估應分開測試 context trust、tool／action authorization、持久狀態或 memory integrity、execution evidence，以及 recovery／rollback。這些目前是評估方向，不是已生效的 AFP conformance requirement，也不是「已證明 Agent 安全」的證據。
