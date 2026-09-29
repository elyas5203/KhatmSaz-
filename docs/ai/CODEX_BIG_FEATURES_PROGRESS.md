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
- Delivery gate: committed and pushed to `main` as `208eb86`; Graphify updated
  successfully to **3751 nodes / 13469 edges / 247 communities**. No required
  feature-1 work remains.
- Follow-up: web custom free-text La'an authoring is not in this minimal version;
  curated active La'an categories work. The bot wizard remains available for
  the custom-text case.
- Exact next step: start feature 2 with a Graphify query for wallet purchase,
  PlanDefinition PRO pricing, invoice kinds and the creator wallet route.

### 2. Real FREE → PRO purchase — DONE

- Goal: wallet-funded permanent PRO upgrade at admin-configured PRO price;
  creator UI shows only FREE/PRO while BASIC remains backend-compatible.
- Touched files: `modules/plan/repository.py`, `modules/plan/service.py`,
  `web/app.py`, `web/templates/creator_wallet.html`, `i18n/__init__.py`,
  `tests/test_pro_plan_purchase.py`, panel/template tests, DECISIONS, INDEX,
  PROJECT_STATE, CHANGELOG, and this file.
- Completed: database-priced/enable-gated purchase, wallet PURCHASE invoice,
  per-user transaction lock, FREE→PRO mutation, no-repeat charge, audit event,
  wallet UI button/status/top-up link, FREE/PRO-only presentation with legacy
  BASIC compatibility, fa/ar/en strings, route/service/template tests.
- Focused validation: **15 passed**.
- Open decisions: exact PRO price and entitlements are owner/admin data, not
  code constants; current requested behavior is permanent because no expiry
  model exists.
- Validation: non-integration suite **178 passed, 86 deselected**; focused
  validation **15 passed**.
- Template compilation: **27 templates passed**.
- Delivery gate: committed and pushed to `main` as `46dbe3b`; Graphify updated
  successfully to **3765 nodes / 13522 edges / 237 communities**.
- Exact next step: complete feature 3 validation and delivery.

### 3. Configurable panel logo — DONE

- Goal: admin-editable `panel_logo_url` via system settings; both admin and
  creator headers render it with the current «خ» fallback.
- Touched files: `modules/system_settings/service.py`, `web/app.py`,
  `web/templates/operations.html`, `base.html`, `creator_base.html`, focused
  route/template/setting tests, project state/changelog, and this file.
- Completed: whitelisted `panel_logo_url`; HTTP(S)/length validation; admin
  operations form with CSRF and audit event; shared request context; image in
  both admin/creator headers with the existing «خ» fallback.
- Focused validation: **15 passed**.
- Open decision/follow-up: changing the real Telegram/Bale bot profile photo is
  explicitly outside this first version.
- Validation: non-integration suite **184 passed, 86 deselected**; all **27**
  templates compiled; focused validation **15 passed**.
- Delivery gate: committed and pushed to `main` as `89aafad`; Graphify updated
  successfully to **3775 nodes / 13557 edges / 257 communities**.
- Exact next step: complete feature 4 validation and delivery.

### 4. Reliable modern Persian panel font — IN-PROGRESS

- Goal: one stable modern Persian webfont with `font-display: swap` and robust
  system/Tahoma fallbacks in both base templates, without layout changes.
- Touched files: `web/templates/base.html`, `creator_base.html`, template
  regression tests, project state/changelog, and this file.
- Completed: both panel shells load pinned Fontsource Estedad 5.3.0 weights
  from jsDelivr; Tailwind uses Estedad with system-ui/Tahoma/sans-serif
  fallbacks. Fontsource CSS provides `font-display: swap`.
- Open decision: final font preference remains owner-reviewable after live
  rendering; initial implementation will use a stable modern Persian font.
- Remaining: focused/full validation, commit/push, and Graphify update.
- Exact next step: finish the feature-4 delivery gate and final audit.

## Cross-feature validation and delivery log

- Required after each feature: `python -m pytest -m "not integration"`, route
  tests, template render/compile, PROJECT_STATE + CHANGELOG update, commit and
  push to `main`, then Graphify update.
- No new migration is planned unless current schema proves insufficient.
- Current working tree before feature work: clean; `main == origin/main` at
  commit `5a0a587`.
