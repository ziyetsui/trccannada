# Textbook access implementation plan

**Goal:** Deploy the selected encrypted HTML access gate at the existing Pages URL.
**Architecture:** StatiCrypt 3.5.4 encrypts a privately maintained standalone course page. The publication script publishes only the encrypted HTML and required images. Credentials stay outside the repository.
**Tech Stack:** Node.js, StatiCrypt, Python, Playwright, GitHub Pages.
**Spec:** docs/superpowers/specs/2026-11-04-textbooks-access-design.md

## Constraints and review focus

- No plaintext course JSON, Markdown, templates, builders or credentials in the current published textbook tree.
- Preserve deep links, mobile usability, original progress and download behavior.
- Remember-device is optional and limited to seven days; logout must clear access.
- Failed encryption and missing or weak codes must leave publication untouched.
- Shared images and already-public Git history remain public; no history rewriting.

## Tasks

- [x] Preserve the full editable edition privately, generate a strong local code, add failing access-gate browser and publishing tests.
- [x] Add a pinned StatiCrypt dependency, Chinese template and a fail-closed publish script accepting a private source directory and environment password. Remove current plaintext textbook artifacts after successfully encrypting.
- [x] Run the gate integration tests and existing source/build/browser checks against the private edition; inspect the exact public diff and scan for raw course content and credentials.
- [x] Commit and push the authorized publishing branch; wait for Pages deployment and repeat browser and raw-path checks against the live URL. Deliver the access code and private-source maintenance instructions.
