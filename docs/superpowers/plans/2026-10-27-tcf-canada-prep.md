# TCF Canada Prep Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans to implement this plan in the current session.

**Goal:** Publish a reviewable TCF Canada preparation page and preserve the successful Oxford approach in reusable documentation.

**Architecture:** A static page beneath the existing learning library, using the current CSS theme and exact Oxford assets. A small independent script handles French device speech, theme and active recall; existing app behavior remains independent.

**Tech Stack:** HTML, CSS, JavaScript, Python build scripts and Playwright.

**Spec:** `docs/superpowers/specs/2026-10-27-tcf-canada-prep-design.md`

## Global Constraints

- Preserve the primary checkout; use `feat/tcf-canada-prep` from `origin/publish/website`.
- Keep source attribution and verification limits visible; no fabricated official questions or score guarantees.
- Reuse exact sentence/image bindings; French audio is device speech, not original exam audio.
- Work on mobile, in dark mode, with no French voice and with storage disabled.

## Review Focus

- Relative links under the GitHub Pages repository prefix.
- Rebuilding the learning library must preserve the new entry point.
- Recall must hide text answers and phonetic hints together.
- No French device voices must never fall back to English.
- Copied Oxford pictures must match their unchanged sentences and stable IDs.

### Task 1: Preserve learning practices and prompts

**Files:** `docs/french-learning-best-practices.md`, `docs/prompts/french-learning-task.md`.

- [x] Extract historical user requirements, separate them from implementation conclusions, and preserve concrete image revisions.
- [x] Write a reusable task prompt and image prompt schema, with source and acceptance requirements.

### Task 2: Add the preparation page and route

**Files:** `learning-library/tcf-canada/{index.html,prep.css,prep.js}`, `learning-library/web/template.html`, generated `learning-library/index.html`, README, `tests/test_tcf_prep.py`.

**Interfaces:** Uses existing CSS tokens, French voice API and Oxford asset manifest; produces static `/learning-library/tcf-canada/` plus a persistent library entry.

- [x] First run a failing browser test for the missing route.
- [x] Build the page, resource notes, three exact Oxford warm-up cards, recall and optional French speech.
- [x] Link from the source template, rebuild and verify existing course counts and asset binding.
- [x] Run preparation-page browser tests and the existing published-site smoke test.

### Task 3: Review and deliver

- [x] Review the full diff and verify source links, mobile layout and the actual generated page.
- [ ] Record verification, commit, push the feature branch and create a PR targeting `publish/website`.
- [ ] Attach the PR, open a local preview and report the preview and best-practice documents.
