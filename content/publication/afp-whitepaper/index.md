---
title: "AFP / SafeLoop Whitepaper Archive (2025 Concept Edition)"
authors:
  - CHING HUI KAI
date: 2025-09-09
publication_types: ["report"]
featured: true
links:
  - name: Current Specification
    url: /specification/
  - name: Evaluation Status
    url: /evaluations/
  - name: Failure Cases
    url: /failure-cases/
  - name: GitHub
    url: https://github.com/huikai79/afp-framework-site
---

## Status

**Historical concept edition · Superseded as a current reference.** The 2025 whitepaper records AFP's earlier prompt-governance and antifragility framing. It is retained for provenance and version history. It is not the current AFP specification and must not be cited as evidence that AFP has been empirically proven superior.

For current claims, scope boundaries, evaluation rules, and benchmark status, use the [AFP Specification](/specification/), [Evaluations](/evaluations/), and [Failure Cases](/failure-cases/) pages.

## Annotated historical reading guide

The original 2025 PDF remains unmodified. This page supplies the current context that the original artifact itself did not contain.

| 2025 wording or framing | Current interpretation |
|---|---|
| "solve drift and hallucination" | Historical design intent. AFP does not guarantee factual correctness by itself. |
| "self-correcting system" | Revision is not proof of correctness; current AFP requires explicit validation and re-testing. |
| "stronger through use" / antifragility | Naming and a research hypothesis unless supported by reproducible evidence. |
| mandatory non-prediction labels for future questions | Not a current universal conformance rule. Evidence, uncertainty, and task-appropriate validation govern the answer. |
| "significantly improve compliance" | Not a current empirical claim. Compliance still requires domain controls, qualified review, and applicable external rules. |
| GPT-4/5 vs Thinking Mode vs AFP Mode | Historical benchmark framing. The current public pilot uses controlled treatment groups and has not yet published benchmark scores. |

## Original artifact handling

The original PDF is preserved unchanged in the repository for provenance. It is no longer promoted as the primary download because the artifact predates the current Historical/Superseded status labeling. Direct access to, or search indexing of, the original file does not promote its historical wording to a current AFP claim.

The original Chinese PDF also has a known compatibility defect: some PDF renderers fail to display its CJK glyphs correctly. Until a corrected archival binary can be published without overwriting the original, the HTML archive page is the safe reader-facing entry point.

## 2026 agentic extension under evaluation

The current text-only pilot is not a proxy for full agent safety. Future evaluation should separately test context trust, tool/action authorization, persistent state or memory integrity, execution evidence, and recovery/rollback. These are evaluation directions, not current AFP conformance requirements and not evidence that agent safety has been proven.
