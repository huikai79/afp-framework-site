---
# Keep title empty to use site title
title: ""
date: 2025-09-09
type: landing

design:
  spacing: "6rem"

sections:
  # ⓪ Compact Banner / Announcement (hero-compact)
  - block: hero
    content:
      title: "📢 Pre-registered Chapter Released"
      text: "**Chapter 5: Experiments & Evaluation (Planned Draft)** is now public. Feedback and collaboration are welcome."
      buttons:
        - text: View Chapter
          url: /publication/#ch5
    design:
      min_height: "28vh"         # 关键：不再全屏
      background:
        color: light
      spacing:
        padding: ["0.75rem","0","0.75rem","0"]

  # ① Executive Summary（以 Biography 块承载）
  - block: resume-biography-3
    content:
      username: admin           # 读取 content/authors/admin/_index.md
      text: ""                  # 正文在作者档里写
      button:
        text: Download Whitepaper
        url: /uploads/afp-whitepaper.pdf   # PDF 放 static/uploads/afp-whitepaper.pdf
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

  # ② Publications（展示白皮书和后续条目）
  - block: collection
    content:
      title: Publications
      text: ""
      filters:
        folders: ["publication"]   # 只抓 publication 类型
        featured_only: false
    design:
      view: citation               # 学术引用风
      columns: 1
---
