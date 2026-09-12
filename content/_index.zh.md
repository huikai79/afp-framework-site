---
title: ""
date: 2026-09-10
type: landing

design:
  spacing: "6rem"

sections:
  - block: resume-biography-3
    content:
      username: admin
      text: ""
      button:
        text: 閱讀目前 AFP 規格
        url: /zh/specification/
    design:
      css_class: dark
      avatar:
        size: medium
        shape: circle
      background:
        image:
          filename: stacked-peaks.svg
          size: cover
          position: center
          parallax: false

  - block: markdown
    id: framework
    content:
      title: AI 工作流程的可靠性層
      text: |
        當 AI 可以搜尋、呼叫工具、使用記憶並執行多步驟任務後，AFP 把六個需要被檢查的環節放進同一條工作流程：

        **假設 → 證據 → 反證 → 決策 → 驗證 → 修正**

        核心要求是可檢查性：重要主張應能回到依據，失敗應能被發現，修正後的結果應能重新測試。

        [閱讀規格 →](/zh/specification/)

  - block: markdown
    id: evidence
    content:
      title: 從主張走向證據
      text: |
        AFP 目前採 evidence-first 的公開方式，網站以三個核心介面組織：

        - **規格** — AFP 目前實際要求什麼。
        - **評估** — 如何用相同模型、任務與工具比較 AFP 與較簡單的基線。
        - **失敗案例** — AI 工作流程具體如何失敗，以及 AFP 如何處理。

        **目前證據狀態：** Pilot Protocol v0.1 已公開；benchmark 分數尚未公布。

        [查看評估計畫 →](/zh/evaluations/) · [查看失敗案例 →](/zh/failure-cases/)

  - block: collection
    content:
      title: 研究與出版
      text: "AFP 的公開文件與歷史版本；舊白皮書會與目前規格明確區分。"
      filters:
        folders: ["publication"]
        featured_only: false
    design:
      view: citation
      columns: 1
---
