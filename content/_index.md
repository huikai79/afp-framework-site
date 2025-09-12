---
# Keep title empty to use site title
title: ""
date: 2025-09-09
type: landing

design:
  spacing: "6rem"

sections:

  # —— 新增 Banner Block 开始
  - block: hero
    id: banner-chapter5
    content:
      title: "第5章实验与评估（计划稿）已公开"
      subtitle: "预注册章节发布中，欢迎反馈与合作"
      cta:
        label: "查看计划中章节"
        url: /publication/whitepaper/chapter5   # 或者你第五章的实际路径
    design:
      css_class: highlight
      background:
        image:
          filename: banner-background.jpg   # 可选，放个背景图
        gradient_start: '#ff8c00'
        gradient_end: '#ff4500'
      text_color_light: true
  # —— 新增 Banner Block 结束

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
