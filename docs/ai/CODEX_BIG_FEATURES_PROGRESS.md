# Codex big features progress — 2026-09-29

This is the resumable handoff for the four owner-requested panel features.
Update it after every meaningful step. Status values are `TODO`,
`IN-PROGRESS`, or `DONE`.

## Feature checklist

### 1. Graphical creator Mini App khatm creation — DONE

- Goal: `GET /creator/khatms/new` graphical form and
  `POST /creator/khatms/create` using `create_and_launch_khatm`.
- Must cover: creator authorization, CSRF, verified phone, FREE plan cap,
  wallet balance, admin-configured creation price, clear Persian errors,
  fa/ar/en i18n, route and template tests.
- Touched files: `src/khatmsaz/web/app.py`,
  `src/khatmsaz/web/templates/creator_khatm_new.html`,
  `creator_dashboard.html`, `creator_khatms.html`, `src/khatmsaz/i18n/__init__.py`,
  `tests/test_panel_redesign.py`, `tests/test_admin_template_render.py`, project
  state/changelog, and this file.
- Completed: Graphify query; role/CSRF/verified-phone checks; card-based form;
  Quran/Salawat/Dua/La'an mapping; active category validation; optional localized
  automatic title; count/visibility/edition inputs; authoritative plan price;
  shared workflow/wallet/cap handling; localized errors; dashboard/list links;
  route + render + i18n tests.
- Validation: non-integration suite **174 passed, 86 deselected**; all **27**
  Jinja templates compiled; focused panel/i18n tests **13 passed**.
- Remaining before delivery gate: commit/push and Graphify update. Once those
  pass, no required feature-1 work remains.
- Follow-up: web custom free-text La'an authoring is not in this minimal version;
  curated active La'an categories work. The bot wizard remains available for
  the custom-text case.
- Exact next step: commit/push feature 1, update Graphify, then mark its delivery
  gate complete here.

### 2. Real FREE → PRO purchase — TODO

- Goal: wallet-funded permanent PRO upgrade at admin-configured PRO price;
  creator UI shows only FREE/PRO while BASIC remains backend-compatible.
- Touched files: none.
- Open decisions: exact PRO price and entitlements are owner/admin data, not
  code constants; current requested behavior is permanent because no expiry
  model exists.
- Next step after feature 1: inspect PlanDefinition, wallet purchase APIs,
  invoices and creator wallet route/template using Graphify.

### 3. Configurable panel logo — TODO

- Goal: admin-editable `panel_logo_url` via system settings; both admin and
  creator headers render it with the current «خ» fallback.
- Touched files: none.
- Open decision/follow-up: changing the real Telegram/Bale bot profile photo is
  explicitly outside this first version.
- Next step after feature 2: inspect system settings and common template
  context injection.

### 4. Reliable modern Persian panel font — TODO

- Goal: one stable modern Persian webfont with `font-display: swap` and robust
  system/Tahoma fallbacks in both base templates, without layout changes.
- Touched files: none.
- Open decision: final font preference remains owner-reviewable after live
  rendering; initial implementation will use a stable modern Persian font.
- Next step after feature 3: inspect both base templates and shared CSS/font
  configuration, then make the smallest consistent change.

## Cross-feature validation and delivery log

- Required after each feature: `python -m pytest -m "not integration"`, route
  tests, template render/compile, PROJECT_STATE + CHANGELOG update, commit and
  push to `main`, then Graphify update.
- No new migration is planned unless current schema proves insufficient.
- Current working tree before feature work: clean; `main == origin/main` at
  commit `5a0a587`.
