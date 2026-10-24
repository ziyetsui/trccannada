# Oxford visual memory implementation plan

**Goal:** Illustrate all 163 Oxford take-off examples and automatically display the correct image in study and recall.

**Architecture:** An editable illustration manifest binds stable lesson/example IDs to sentence memories and local image assets. A Python validator enriches examples at build time. The existing pronunciation component displays the image and preserves text/audio fallback.

**Tech Stack:** Python standard library, GPTProto native async API, existing vanilla JavaScript, Playwright.

**Spec:** `learning-library/docs/research/visual-memory-design.md`

## Constraints

Adults learning from zero. Only take-off is illustrated in this delivery. All 163 examples require independent assets; no generic image reused to claim coverage. No API credentials in project. No one-view retention promise. Preserve existing pronunciation and course content. API task IDs persisted before polling; unknown submission state is never automatically resubmitted.

## Review focus

- Sentence edits must fail rather than silently reuse stale visual mnemonics.
- Missing, corrupt or external assets must fail the build.
- Missing runtime images must leave existing text and audio usable.
- Small screens and dark mode must remain readable with no overflow.
- Recall must not leak the French answer through picture captions or accessible image labels.

## Tasks

- [x] Write research/design and create `scripts/content/sentence-illustrations.json` from the 163 authorized source memories. Save exact prompts and generation provenance.
- [x] Implement resumable GPTProto generation in `scripts/generate_illustrations.py`; perform and inspect the first image, then process remaining examples with bounded concurrency. Raw responses and task state stay outside the repo.
- [x] Write failing tests in `tests/test_illustrations.py` for coverage, stale text, missing/invalid asset and unsafe paths. Add `scripts/illustrations.py`, integrate into `build_site.py`, and make those tests pass.
- [x] Extend `web/pronunciation.js` and `web/style.css` to display a lazy loaded image in study and recall with a graceful error fallback and answer-free recall labels.
- [x] Rebuild; run relevant existing unit/browser checks and new desktop/mobile/dark/recall/error checks. Inspect per-lesson contact sheets, record issues and fixes. Publication follows the checks; deployed coverage is the final release gate.

## Execution notes

User explicitly requested research → scheme → image generation → automatic insertion, then narrowed the scope to Oxford 起飞. Execute in this session on a fresh clone and feature branch; no additional design approval gate is needed under the session's autonomy instructions. Keep the original published branch intact until validated changes are ready.
