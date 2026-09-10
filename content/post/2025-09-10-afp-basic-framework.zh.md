---
title: "AFP System Prompt：2025 基礎版（歷史版本）"
date: 2025-09-10
summary: "AFP 早期以 Prompt 治理為中心的基礎版提示；保留作版本紀錄。"
tags: ["AFP", "SafeLoop", "System Prompt"]
categories: ["Prompt Engineering"]
---

> **版本狀態：歷史版本。** 本頁保留 2025 年 AFP 以 Prompt 治理為中心的基礎版提示，方便追溯框架演變。它不是 2026 年 AFP／SafeLoop 的完整現行規格，也不代表已經過 benchmark 證明優於其他提示方法。

目前規格請閱讀：[AFP 規格](/zh/specification/)；目前實證狀態請閱讀：[評估](/zh/evaluations/)。

## 2025 基礎版的核心結構

當時版本主要要求：

- 回答以安全與可查證事實為優先；資訊不足時標示假設與驗證方式。
- 以「理解 → 執行 → 檢查」形成簡化迴路。
- 將事實與較具探索性的類比、創意或替代路徑分開處理。
- 在輸出前檢查是否離題、缺乏證據或無法執行。

這些概念後來演變為目前較明確的六段工作流程：

**假設 → 證據 → 反證 → 決策 → 驗證 → 修正**

## 歷史下載

以下檔案保留作版本紀錄，內容可能與目前規格不同：

- [Basic Framework](/downloads/afp-basic.md)
- [Advanced Framework](/downloads/afp-advanced.md)
- [Mother Framework](/downloads/afp-master.md)

若要評估 AFP 目前是否有效，請以公開 evaluation protocol、benchmark 狀態與可重現結果為準，不以這些歷史提示文字本身作為成效證據。
