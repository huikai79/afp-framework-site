---
# Keep title empty to use site title
title: ""
date: 2025-09-09
type: landing

sections:
  # ⓪ Banner 提示区（新增）
  - block: hero
    content:
      title: "📢 预注册章节发布中"
      text: "《第5章：实验与评估（计划稿）》 已公开，欢迎反馈与合作。"
      button:
        text: 查看章节
        url: /publication/#ch5
    design:
      background:
        color: light
      spacing: "3rem"  

  # ① 执行概要（以 Biography 块承载）  
  - block: resume-biography-3
    content:
      username: admin           # 读取 content/authors/admin/_index.md
      text: ""                  # 正文在作者档里写
      button:
        text: 下载白皮书
        url: /uploads/afp-whitepaper.zh.pdf   # PDF 放 static/uploads/afp-whitepaper.zh.pdf
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

  # ② 出版物（展示白皮书和后续条目）
  - block: collection
    content:
      title: 出版物
      text: ""
      filters:
        folders: ["publication"]   # 只抓 publication 类型
        featured_only: false
    design:
      view: citation               # 学术引用风
      columns: 1
---
