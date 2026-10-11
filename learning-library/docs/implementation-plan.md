# French Learning Library Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Produce a complete original French curriculum adapted from the seven supplied frameworks, with editable Markdown and a self-contained learning website.

**Architecture:** Seven edited course books contain 168 original learning units; overlapping source units are explicitly merged. A numbered source-unit ledger maps all 505 source unit headings to French units and explains language-specific adaptations. Markdown lessons are the build input; a Python builder produces embedded-data HTML without network dependencies.

**Tech Stack:** Python 3.13, UTF-8 Markdown, HTML/CSS/vanilla JavaScript, browser Web Speech API; Playwright for browser verification.

**Spec:** ../research/02-french-curriculum-and-web-design.md (approved in conversation).

## Global Constraints

- 中文讲解、原创法语例句，每课加入幼儿比喻。
- Markdown 是真实源文件，含固定课号、级别、先修课和结构化练习。
- 原书转换库只放本地资料目录，不默认发布到公网。
- 没有法语声音时明确提示安装/启用系统法语声音，避免悄悄用英语读法语。
- 生成嵌入完整数据的独立 HTML，避免 file:// 下 fetch 本地 JSON 的限制。
- CEFR 标注是编写者的教学估计，不能冒充官方认证。

## Review Focus

- Source units whose English structure has no French equivalent need a stated replacement, not a false literal equivalence (Task 1 coverage check).
- Voices may arrive late or never arrive; select only French and show a usable unavailable state (Task 3 browser scenarios).
- Corrupt or blocked localStorage must preserve the current lesson and allow study (Task 3 browser scenarios).
- Accents, apostrophes and Chinese search terms must find lessons (Task 3 browser scenarios).
- Direct file opening, mobile layouts and keyboard interaction must work without a server (Task 3 browser scenarios).

### Task 1: Curriculum and provenance

Files: french/*/NN.md; french/coverage.json; french/coverage.md; scripts/author_curriculum.py; tests/test_library.py.
Interfaces: lesson ids G01–G42, E01–E28, A01–A24, P01–P20, M01–M15, F01–F15, I01–I24. Each lesson has metadata, objective, explanation, analogy, >=3 examples, >=2 MCQs with reasons, an application task, references and prerequisite ids.

- [x] Write tests for missing lesson sections, invalid correct choices, duplicate ids, missing source units and broken mapped targets; run before implementation and observe failure.
- [x] Author all seven course books; create 505 explicit numbered coverage records; retain source adaptation explanations and excerpt caveat.
- [x] Run content validation and inspect representative lessons, answer explanations and phonetic rules.

### Task 2: Reference and review material

Files: french/reference.md; french/study-guide.md; french/review.md; french/README.md.
Interfaces: Markdown documents directly embedded as reading panels; exercises remain in lesson records.

- [x] Add study routes, diagnostic questions, mixed review, grammar/pronunciation reference, glossary and searchable index.
- [x] Check all referenced lesson ids exist and public reference links are documented.

### Task 3: Website and build

Files: scripts/build_site.py; web/template.html; web/style.css; web/app.js; index.html; tests/browser_check.py.
Interfaces: build_site loads lessons from Markdown and exports a list with metadata, sections, examples and quiz records; window.LESSONS is the embedded payload. app renders with DOM textContent and safe element creation.

- [x] Implement Markdown parsing and schema validation; make Task 1 tests pass.
- [x] Build a responsive library dashboard and lesson flow with catalogue, search/filter, examples, practice/answers, related units and references.
- [x] Add voice selection, rate, cancel/stop and playback lifecycle feedback; include native missing-voice handling.
- [x] Add progress with a guarded storage adapter and restart-safe restoration.
- [x] Test search, navigation, quiz feedback, progress persistence, storage failure, delayed/no voices, correct language and file/mobile layouts.
- [x] Run build, source integrity checks, tests and browser checks; save verification report and screenshots.

### Task 4: Review and delivery

Files: docs/progress.md; docs/verification.md; README.md.

- [x] Obtain one fresh review of the finished curriculum and browser implementation, as required by executing-plans.
- [x] Fix substantive findings and run the appropriate checks again.
- [x] Update the main entry, package the French course with its independent HTML and source Markdown, and report exact completion and limitations.
