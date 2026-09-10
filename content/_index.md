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
        text: Read the current AFP specification
        url: /specification/
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
      title: A reliability layer for AI workflows
      text: |
        AFP structures six things that increasingly matter once AI systems can search, call tools, use memory, and act across multiple steps:

        **Assumptions → Evidence → Counter-evidence → Decision → Validation → Revision**

        The framework is designed around inspectability: important claims should have a traceable basis, failure should be detectable, and revised outputs should be testable again.

        [Read the specification →](/specification/)

  - block: markdown
    id: evidence
    content:
      title: From claims to evidence
      text: |
        The current AFP public reference is evidence-first and organized around three surfaces:

        - **Specification** — what AFP currently requires.
        - **Evaluations** — how AFP should be compared against simpler baselines.
        - **Failure Cases** — concrete ways AI workflows fail and how the framework responds.

        **Current evidence status:** Pilot Protocol v0.1 is public; benchmark scores are not yet published.

        [Evaluation plan →](/evaluations/) · [Failure cases →](/failure-cases/)

  - block: collection
    content:
      title: Research & Publications
      text: "Public AFP documents and archived editions. Historical whitepapers are labeled separately from the current specification."
      filters:
        folders: ["publication"]
        featured_only: false
    design:
      view: citation
      columns: 1
---
