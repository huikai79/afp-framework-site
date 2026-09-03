---
# Keep title empty to use site title
title: ""
date: 2026-09-03
type: landing

design:
  spacing: "6rem"

sections:
  # ① 2026 定位與 SafeLoop 核心說明
  - block: resume-biography-3
    content:
      username: admin
      text: ""
      button:
        text: 閱讀 AFP 白皮書
        url: /uploads/afp-whitepaper.zh.pdf
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

  # ② 公開研究與出版內容
  - block: collection
    content:
      title: 研究與出版
      text: "AFP 的公開文件、白皮書與後續研究成果。網站將逐步加入規格、評估與失敗案例。"
      filters:
        folders: ["publication"]
        featured_only: false
    design:
      view: citation
      columns: 1
---
