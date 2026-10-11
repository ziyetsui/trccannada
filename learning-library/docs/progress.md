# Execution ledger — plan: docs/implementation-plan.md

Design approved by user: “是的 继续”. Proceed with implementation in this session.

Ruling: No additional permission handoff — the user explicitly approved the written design and instructed continuation; routine implementation is authorized by the session and higher-priority autonomy instructions.
Ruling: Work directly in learning-library — this folder is a document workspace, not a standalone Git repository; avoid initializing or modifying the parent wiki's version-control structure.
Ruling: Merge repeated English objectives into 168 original French units across seven books, while retaining 505 numbered source-unit coverage records. This is permitted by the approved design and avoids invented one-to-one language equivalence; the risk is that the edited order differs from an English book's literal unit order, which the coverage ledger makes visible.
Ruling: General French from foundations with Canadian daily-life examples; no claim of a complete TEF/TCF preparation course, because the user did not choose an exam target.

Pre-flight: Authoring exports Markdown -> builder reads fixed section names and exercise delimiters -> browser consumes validated embedded JSON. All share stable lesson ids and source mapping ids.

Tasks 1–4: completed.

168 lessons, 531 examples, 336 in-lesson MCQs, 505 numbered source framework records. Study guide (20 diagnostic items), mixed review (35 items), reference tables and seven indexes complete.

Verification: source integrity passed for 7 books / 1,369 pages; six Python tests and 24 browser scenarios passed. French Markdown local links and document course-id references checked. Standalone HTML and ZIP archive verified; desktop/mobile screenshots inspected.

Fresh independent review: no critical findings. Corrected G36 infinitive example, delayed voice preference restoration, stop status, keyboard focus and prerequisite wording; rebuilt and reran applicable checks. Reviewer verdict: suitable for delivery as clearly labeled original edited draft, not teacher-certified phonetic/OCR accuracy.

Package includes source TOCs and their page assets, not full source books. Full source conversion remains local. No public deployment or message sent.

## 2026-10-11 新增两书

用户指定的40篇EPUB与Oxford131页PDF已加入同一离线书架。新增S01–S40、T01–T22，合计9册230课；新课283例句/146题，整体814例句/482题。来源全文独立保留，每课可打开对应原文与原题答案；错误另行提醒。分享包移除原书全文，保留新编课。详细检查见additional-verification.md及对应JSON。
