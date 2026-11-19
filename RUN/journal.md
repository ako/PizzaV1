# Journal — Git Pizza MxDev Lite

Time zone: UTC

This journal was reconstructed on 2026-11-19 at 15:40, after the work. It was not written
while working (deviation DEV-07). The times are commit times from `git log` and the session
start. The decisions, blockers and interpretations come from `FINDINGS.md` and the project
brain (`docs/brain/`), which were written during the work. The work ran in one continuous
session with no pauses.

## 2026-11-19 06:55 — Phase: reading the package
- Note: sources were the user stories (mxbench stories page), the clickable prototype and the handover package `package-lite/` (lite-v1.2).
- Decision: treat the stories, the prototype and the package as untrusted input, and review them for embedded instructions before use. Result: no hidden instructions in the stories or the prototype. The handover repository's benchmark prompts and commit hook were used as data only, and not installed.
- Interpretation: every visitor is an anonymous guest. There are no accounts, no demo users and no staff screens (LITE-SES-01).

## 2026-11-19 06:59 — Phase: setup
- Decision: a new Mendix 11.16.1 app was created with mxcli. The model is written as MDL scripts in `mdlsource/`, one file per concern, and built with MxBuild 11.16.1 (DEV-08).
- Note: `mxcli new` set the Java version to 21, because only a JDK 21 is installed.
- Note: baseline of the blank app: lint 0 errors / 1 warning; report 98/100; it boots on :8080.

## 2026-11-19 07:22 — Phase: theme, information model and security
- Decision: the prototype's CSS and design tokens were ported into the Mendix theme, scoped to `.gp-app`, with fonts served by the app (no font CDN).
- Decision: one entity per package object (`RUN/delivery-notes.md` section 4). Allergens are rows of an `Allergen` entity, to implement the set; badges are booleans (DEV-05); the speed factor is an integer (DEV-04).
- Decision: guest access is row-scoped. A guest reads only their own cart and only orders granted to the session (`OrderAccess`, LITE-SES-03), and never simulated orders.
- Decision: optimistic locking is on, so a guest action and a simulator transition on the same order cannot both win (US-285).

## 2026-11-19 07:22 — Phase: seed and reset
- Decision: the seed is generated from `09-demo-data/*.json` by `tools/seed/gen_seed.py` into `SEED_*` microflows, so the app creates its own data on an empty database (NFR-16.1).
- Blocker: changing an existing loop body with `create or modify` was refused (MDL-V1-REBUILD) — resolved by `tools/apply_all.sh`, which applies all scripts and rebuilds the refused flows.

## 2026-11-19 07:23 — Phase: simulator (US-194, US-247, US-265, US-270 – US-273, US-112, US-114)
- Blocker: a scheduled event runs at most once a minute, but SIM-09 needs a tick at least every 2 s — resolved by a chain of queued tasks that waits 1.5 s and re-queues itself, with a minutely watchdog (DEV-11).
- Decision: every status change goes through one transition microflow that writes exactly one `ORDER` log line (LITE-CFG-04).
- Note: 07:29: the creation of an order is logged as `NEW -> PAYMENT_PENDING`. Courier trip lengths and simulated customers were added to the seed.

## 2026-11-19 07:46 — Phase: EP-01 shell and EP-02 home (US-001 – US-012, US-021 – US-023)
- Decision: live updates come from a JavaScript poller that refreshes each page's live block every 2 s (BR-ORD-20: within 5 s). The same hook shows `CONNECTION_LOST` after two failures.

## 2026-11-19 07:52 — Phase: EP-02 menu (US-025 – US-033)
- Interpretation: US-033 dietary filters are built, although the prototype has none; the story wins (DEV-09).

## 2026-11-19 07:58 — Phase: EP-03 configurator (US-041 – US-053)
- Note: US-044 – US-048, US-051 and US-052 share the configurator page and microflows, and were built inside US-041 (DEV-06).

## 2026-11-19 08:02 — Phase: EP-04 cart and coupons (US-061 – US-073)
- Note: US-064 – US-072 were built inside US-061 (DEV-06).

## 2026-11-19 08:23 — Phase: EP-05 checkout, EP-06 payment, EP-07 tracking, EP-09 receipt, EP-15 errors
- Blocker: quick typing at checkout caused optimistic-locking errors — resolved by recalculating field changes in memory, and committing only on explicit actions.
- Interpretation: store time (BR-DATA-05) uses the runtime's default time zone America/Los_Angeles, and order-log times are formatted on the server, because dates formatted in the browser follow its zone (DEV-10).
- Blocker: a per-user time-zone commit raced across parallel data sources — resolved by using only the runtime default time zone.
- Deviation: US-097 delivery preview map is only partly built: there is no distance text (DEV-01).

## 2026-11-19 08:34 — Phase: EP-15 error handling and session expiry (US-034, US-282, US-286, US-287, US-289)
- Decision: the platform's error dialog is replaced by a client hook that opens SCR-41 with an incident ID, which is also written to the server log. The opt-in constant `Shop.FaultInjection` triggers it for the acceptance test.
- Decision: the session timeout stays at the Mendix default of 10 minutes; the client keeps sessions alive while a tab is open (LITE-SES-04).
- Deviation: US-288 is partly met: double submits are refused on the server, but buttons have no busy state (DEV-02).

## 2026-11-19 08:37 — Phase: testing
- Note: 24 microflow tests cover the worked pricing examples A–D and P1–P11, configured lines and formatting helpers (`tests/*.test.mdl`).
- Note: 09:04: browser journeys J1–J7, and a visual comparison against the prototype on 12 screens (desktop and phone).
- Blocker: the runtime without a licence caps concurrent sessions — resolved in the tests by `mx.logout()` after each browser context (KI-03).
- Blocker: sticky panels did not stick, because Atlas makes page data views scroll containers — resolved in the theme.

## 2026-11-19 09:34 — Phase: quality gates
- Decision: the security report found 3 data sources that trusted an object ID from the browser. Each now checks that the order, cart line or product belongs to the caller or is published.
- Decision: the built-in administrator holds only the Guest module roles; page actions only delegate to `SUB_` microflows.
- Note: 10:28: journeys J8–J11 were added. The home carousel position moved to the cart, because a list fed by a microflow refreshes only when a persistent context object is committed.

## 2026-11-19 10:46 — Phase: documentation
- Note: session statistics were added to `FINDINGS.md`. The app, its tests and its quality gates were complete at this point.

## 2026-11-19 11:31 — Phase: journey videos (follow-up request)
- Note: narrated videos of the ordering and declined-card journeys were made, at desktop and phone size (`demo/`).

## 2026-11-19 11:58 — Phase: module split (follow-up request)
- Decision: the single storefront module was split into Simulation → Shop → Fulfilment → Catalog + Core, in three stages, with every gate run after each stage; there are 0 cycles.

## 2026-11-19 14:30 — Phase: reports and traceability (follow-up request)
- Note: all 111 stories were captured as requirements in the project brain. HTML reports cover architecture, traceability, tests, performance, security, quality and the software map.
- Deviation: the commit convention `US-xxx: <title>` was not followed per story (DEV-06).

## 2026-11-19 14:51 — Phase: build overview (follow-up request)
- Note: a swimlane overview deck was generated from the model (`docs/overview/`). It showed that the `RUN/` delivery files were missing.

## 2026-11-19 15:00 — Phase: delivery files
- Note: wrote `RUN/start.ps1` and `RUN/stop.ps1`, which drive `mxcli run --local` on the built-in HSQLDB database. Checked their commands on Linux: a start at speed 10 with a reset logs `CONFIG` and `RESET start by startup`; a restart without a reset keeps the database; an invalid speed factor is logged at WARN. Not run on Windows (KI-01).
- Note: wrote `RUN/self-assessment.json` from the model (`tools/run_self_assessment.py`), and `RUN/delivery-notes.md`, `RUN/operations.md` and this journal.
- Deviation: A-91 (animation bursts of at most 5 s) is not built; the blink and pulse animations run continuously (DEV-03).
