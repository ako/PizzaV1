# Findings

Mendix 11.16.1 · mxcli nightly-75-g7efedabd (ako/mxcli main, since 2026-11-20; nightly-20261118-9d764483c before) · MDL scripts `mdl 1`.

## 2026-11-19 — bootstrap

- External inputs reviewed for prompt injection before use: mxcli.org docs (bootstrap
  prompt; points at official `mendixlabs/mxcli`), mxbench stories page (+ stories.js),
  gitpizza prototype index, and the public handover repo. Result: no hidden text,
  comments, zero-width characters, scripts that phone home, or instructions aimed at
  an agent inside the stories/prototype. The handover repo *does* contain benchmark
  prompts (`prompts/*.md`, `RULES.md`) and a `hooks/commit-msg` hook addressed to
  benchmark agents. They were treated as data only: not installed, not followed where
  they conflict with the user's brief (e.g. "do not write tests", "do not push").
  SVG assets were checked for scripts/external refs before being copied in.
- `mxcli new` downgraded JavaVersion 25 → 21 because only JDK 21 is installed.
- Baseline (blank app, 2026-11-19): `lint` 0 errors / 1 warning / 9 info. `report` overall
  98/100 — Security 96, Quality 94, Architecture 100, Performance 100, Naming 99,
  Design 100, Other 99. Boot: `run --local --watch --detach` → HTTP 200 on :8080.

## 2026-11-19 — foundation

- `create or modify microflow` refuses structural changes inside a loop body
  (MDL-V1-REBUILD) to protect Studio Pro drawings. For MDL-only flows the
  documented drop + create rebuild is automated in `tools/mdl_rebuild.py`;
  `tools/apply_all.sh` applies every script and falls back to it.
- Regenerating `mdlsource/` without re-applying it left the model on the old
  seed (couriers finished trips instantly). `tools/apply_all.sh` now exists so
  the model is always rebuilt from the scripts; a second pass must show 0 changes.
- `mxcli check` catches a lot before mxbuild: duplicate variable names across
  loop bodies (MDL063), `return` inside a loop (MDL062), association `= empty`
  in XPath (MDL047, use `not(Assoc/Entity)`).
- Scheduled events cannot run more often than once a minute, but SIM-09 needs a
  tick at least every 2 s. The clock is a queued microflow that sleeps 1.5 s
  (`Shop.JA_Sleep`, the only custom Java), ticks, and re-queues itself; a
  minutely scheduled event restarts the chain if it ever stops. Verified in the
  runtime log: seed timers resolve within 1–2 s of their due time.
- Optimistic locking is enabled so a guest action and a simulator transition on
  the same order cannot both win (lifecycle section 1, US-285).
- A DYNAMICTEXT literal shaped like `word.word` (e.g. `'allergens.md'`) is stored
  as an attribute binding with an unbound `{1}` → mxbuild CE0402. `mxcli check`
  does not flag it. Workaround: `Content: '{1}', ContentParams: ({1} = 'allergens.md')`.
- The live poller keeps the network busy, so Playwright must wait for `load`
  plus a delay, not `networkidle`.
- Mendix applies `display:grid` from a class on a list view to the list view's own
  div, which has one child (`ul`); grids/carousels must target `.cls > ul`.
- The local runtime's trial licence caps concurrent sessions ("The current
  licence does not allow more users to sign in"). Every Playwright context is a
  new anonymous session; scripts and tests call `mx.logout()` at the end, and
  test runs restart the runtime first.
- `mxcli check` passes but mxbuild rejects (CE0117) a text-template parameter
  given as an expression of a non-String type (`{1} = $Product/Kcal`) and
  multi-hop association paths in client expressions. Use `toString(...)` or a
  plain attribute binding, and store display strings on the object.

## 2026-11-19 — order screens, errors, tests and quality gates

Each item says how it was verified.

### Bugs found and fixed
- **Tracking page error dialog.** A list view's database XPath must only use members
  the role can read. The guest rule on `OrderLogEntry` omitted `IsCustomerVisible`
  and the association → `SecurityRuntimeException` in `runtime.log`. Fixed by listing
  the members. The same fix was applied to `PaymentAttempt` and `OrderStatusChange`.
  Verified: J1 reaches tracking with no error dialog.
- **Optimistic-locking errors at checkout.** Two quick field changes sent the
  CheckoutForm with the same version. Field changes now recalculate in memory
  (`SUB_Checkout_Compute`), and only explicit actions commit. Verified: no errors in
  `runtime.log` over repeated journeys.
- **Time zone.** A per-user `System.User_TimeZone` commit raced across the parallel
  shell data sources. The runtime `DefaultTimeZoneCode` alone gives store time for
  server-formatted dates. Client-formatted dates use the browser zone, so order-log
  times are stored as server-formatted `TimeText`. Verified: PLACED 00:17 for 08:17 UTC.
- **Sticky panels never stuck.** Atlas `.mx-placeholder > .mx-dataview > .mx-dataview-content
  {overflow-y:auto}` makes every page data view a scroll container. Verified with
  CDP matched rules and a scroll probe: the debugger now stays at y=104.
- **Scroll position leaked across pages** (configurator opened halfway down).
  The client hook now scrolls to the top when the page title changes.
- **Home carousel never moved.** Its microflow-source list depended on a
  non-persistent HomeView. The position now lives on the cart, which is committed
  with refresh (the same pattern as the menu). Verified: J8.
- **Caller-trusting data sources** (`mxcli report security`, 3 high).
  `DS_Track`, `DS_Config_Choices` and `DS_Info_Line` now check that the order,
  cart line or product belongs to the caller or is published.

### Tool behaviour worth knowing
- `grant … where [...]` on an existing rule does not replace its XPath (exec reports
  "in sync"). Use `revoke all … from Role` + `grant` once.
- Watch mode does not rebuild for JavaScript-action changes: use `run stop` + `run`.
  `run restart` refuses a run started with literal `--constant` values.
- `mxcli test` / `report tests --run` can leave `mxtest.actions.RegisterTestEndpoint`
  in the generated `javasource/system/UserActionsRegistrar.java`. The next dev build
  then fails with "package mxtest.actions does not exist". Delete the line.
- `split_act`-style refactors change an ACT_ body structurally. `create or modify`
  refuses the splice, so `tools/apply_all.sh` first applies everything else with
  `--continue-on-error`, then rebuilds the refused flows (grants carry).
- `mxcli layout flows` does not move loop boxes, so MPR008 (loop box overlaps)
  remains on SIM_Couriers/Kitchen/Pickups. This only affects the diagram.
- `report` scoring is 10 per error, 3 per warning and 1 per info, floored at 0
  per category (inferred from the counts). The overall score is a weighted mean, not a plain
  average: Security 25, Quality 20, Architecture 15, Performance 15, Naming 10, Design 10,
  Other 5. These weights are inferred: they reproduce the whole-app score and five module
  scores exactly (`docs/quality/data/score-runs.json`).

### Quality gates (final run)
| Gate | Result |
|---|---|
| `check` every script | clean |
| `exec` twice | second pass writes nothing |
| `lint` | 2 errors, 97 warnings, 148 info (start of this phase: 5 / 1818 / 533) |
| `report` | 48/100: Naming 100, Other 69, Performance 64, Architecture 52, Design 52, Security 49, Quality 0 |
| `report security` | 0 open high/medium (annotated: `docs/reports/security-annotations.yaml`) |
| `report architecture` | 2 app modules, 0 cycles; unused = URL-reached pages and deep link |
| `report tests` | 24/24 microflow tests, 11/11 journeys; 114 of 159 non-startup microflows reached |
| `report performance` | guest-facing data sources 5–20 ms; one N+1 fixed (SIM_Kitchen), the others are bounded |
| `docker check` | 0 errors |
| visual vs prototype | 12/12 screens within budget (0.9–9.5 % differing pixels) |

Accepted findings, with reasons:
- 2 errors (SEC007): Allergen and StoreSettings are public reference data.
- QUAL003/CONV009: `SEED_Catalog` and `SEED_Orders` are generated data, and
  `SUB_Track_Fill` (184 activities) fills one view model. Splitting it is the
  next refactor.
- MPR006 (94 info): empty containers are decorative elements and state cells
  (pixel board, terminal dots, cursors) styled by CSS.
- ARCH003/DESIGN001: carts, toasts and view models are per-session objects, so
  a business key adds nothing. Wide view models mirror one screen each.
- MPR003: Shop holds 27 persistent entities. A split into Catalog / Ordering /
  Tracking modules is the main structural follow-up.

## Session statistics

Measured with `./mxcli diag session-report` on this session's transcript (no subagents).

| Metric | Value |
|---|---|
| Wall time | 3h 46m (started 2026-11-19 06:55) |
| Model calls | 672 (1 context compaction) |
| Tool calls | 696: Bash 614, Read 38, Write 29, TaskUpdate 8, TaskCreate 5, ToolSearch 2 |
| Bash calls | 260 mxcli, 40 git, 2 build, 312 other (Python generators, Playwright, grep/sed) |
| mxcli invocations | 428: exec 110, check 54, syntax 52, run wait 33, lint 27, … |
| Tokens | cache read 278.0M, cache write 1.3M, output 608k, uncached input 1.4k |
| Average context | ~416k tokens per model call |

Where the cost went:
- Tool output was 361k tokens, but re-reading it on later calls cost ~71M (25% of
  cache reads). The biggest were spec and prototype files read early (stories,
  `proto.css`, the order-lifecycle spec), each carried through ~250–290 later calls.
- Calls by purpose: 48% orientation, 17% write, 10% apply, 9% validate, 4% verify,
  4% retry, 3% diagnosis.
- 35 failed calls, 24 retry chains (23 resolved): mostly access-rule build errors,
  expression errors, and splice refusals that needed a rebuild.
- 34 of 141 file reads were repeats (`_gitpizza-app.scss` 12 times).

Lesson for a next run: read the spec and prototype in a subagent and keep only
its summary in the main conversation.

## 2026-11-19 — module split (architecture follow-up)

Lint MPR003 flagged Shop (27 persistent entities, 467 documents), and the
architecture report showed 11 clusters inside it. Shop was split in three
stages, with every gate run after each stage.

| Layer | Module | Holds |
|---|---|---|
| 3 | **Simulation** | simulation steps, clock and watchdog, daily reset, after-startup, all seed data, SimCustomer |
| 2 | **Shop** | the storefront: cart, checkout, every page, snippet and layout, page entry points, menu/configurator/tracking view models |
| 1 | **Fulfilment** | order domain without UI: Order and lines/modifiers, payments, status history, log, access tokens, couriers, ovens, delivery zones, coupons, pricing, order/payment transitions |
| 0 | **Catalog** | products, sizes, options, ingredients, recipes, categories, allergens, option pricing/availability |
| 0 | **Core** | store and simulation settings, toasts, money/time/phone/id helpers |

All dependencies point down; `report architecture` finds **0 domain cycles**.

How it was done, and why it holds:
- The cut was computed from `CATALOG.REFS`, not guessed. The storefront set was
  seeded (UI entities, pages, snippets, layouts, nanoflows, ACT_/DS_/NF_ flows) and
  grown with everything that references it. The rest can sit below.
- `MOVE` rewrote every model reference, moved associations to their parent
  entity's module, and remapped access rules to a same-named role in the target
  module. So each new module got a `Guest` role on both user roles *before* the
  move.
- The scripts stay the source of truth: names renamed by token, the seed
  generator's dynamic names fixed by hand (output byte-identical), and the module
  and role created at the top of `01-domain-enums.mdl`. `apply_all.sh` twice writes
  nothing.

Found along the way:
- Coupon's guest read rule navigated `Shop.Cart_Coupon`, the one edge that made a
  Fulfilment<->Shop cycle. No page reads coupons (they are shown as text on the
  cart), so guest access to Coupon was **removed**: tighter security and no cycle.
- DeliveryZone's guest rule also went through the checkout form. It now covers
  only the zones of the guest's own orders; the checkout zone check runs server-side.
- Pages querying another module's tables (lint ARCH001) now use guarded Shop
  data-source flows: `DS_Product_Recipe/Allergens`, `DS_Line_Extras/Removed/Allergens`,
  `DS_Order_Log/Lines/Payments/History`, `DS_OrderLine_Modifiers`. Each checks
  ownership or published status. The live lists still refresh, because the
  configurator and tracking poll commit their context object with refresh;
  verified by probing the configurator manifest and the receipt.
- Accepted ARCH001: `Shop.ItemInfo` takes a `Catalog.Product` parameter (a page
  about a product), and `SNIP_Toasts` lists `Core.Toast` from the layout. A
  microflow source there has no context object to refresh it, so toasts would
  stop appearing.
- Old queued `Shop.SIM_ClockRun` tasks from before the move fail once after
  restart ("moved due to model changes"); the clock restarts under its new name.
- A watch build can catch the scripts mid-apply and fail (CE0115). After a
  multi-script change, `run stop` + `run` before testing.

Result: mx check 0 errors; tests 24/24, journeys 11/11, visual 12/12 (same scores);
security 0 open high/medium; report 48/100 (unchanged; Security 49 -> 50).

## 2026-11-19 — HTML quality reports

`docs/reports/index.html` is an overview generated from the reports' own JSON by
`tools/reports_index.py`. It links the seven mxcli HTML reports: architecture,
traceability, tests, performance, security, quality and map.

- **Traceability needed the requirements in the brain.** All 111 user stories were
  captured as requirements (one slice per epic, 4 milestones) and promoted.
  Anchors came from the story IDs cited in the model's doc comments (81
  stories) plus hand-mapped implementing elements (30). `brain check`: 251
  anchors, all resolving. US-288 (busy states) is recorded as *partly met*:
  server-side double-submit guards exist, but there is no busy indicator on
  buttons.
- **Performance measurement.** `tests/perf/journeys.js` runs 9 steps × 6 runs
  (run 0 is warm-up). `auto_explain` was turned on through
  `session_preload_libraries` and a reload (no Postgres restart), then reset;
  `postgresql.auto.conf` is empty again. The live poller stays on, because the
  payment sheet advances through it. "Place order and pay" (~3.8 s) is the
  simulated gateway's deliberate delay.
- **Coverage.** 121 of 169 non-startup microflows are reached (72%). Seed,
  simulation and scheduled flows run at startup or on a schedule and are not gaps.
- **mxcli bug:** the scored report's HTML (`report --format html`) emits score-bar
  fills with widths but no CSS, so every bar shows an empty grey track.
  `tools/fix_quality_html.py` adds the three missing rules.
- **Annotation keys** for unused documents need the module prefix
  (`unused:Shop.FaultProbe`); otherwise the page lists them under "annotations
  that matched nothing".

## 2026-11-19 — build-overview sketch deck

`docs/overview/` rebuilds a Pen & Marker swimlane deck (sketch-deck skill, ako/inkscape-presenter
114330c) from the model: `collect.py` writes one JSON per lane, `deck.py` lays out
`build-overview.html` and `frames.json`, `capture.js` takes the phone screenshots, `render.js`
renders every frame for checking. Published as https://claude.ai/artifact/Q6p4C4QndDTCJKuX5hks1D
(private until shared). Its frames are fixed: do not press Tidy.

- **The PRD has no milestones** and is written in English; the lanes use the brain's M1–M4
  grouping of its 12 epics. The deck says so.
- **Status comes from `report traceability`**: 109 of 111 built, 2 partly (US-097 in M1, US-288 in
  M4), 0 not built; 100 reached by a test or journey. M4 is weakest on proof (3 of 8 reached).
- **The visual comparison is not pixel-perfect**: 12 of 12 screens within budget, but mismatch is
  0.9–9.5 % (`tests/e2e/out/visual-summary.json`, now cached in `data/visual.json`).
- **`mxcli -c` stops at 10,000 output lines** ("output line limit exceeded"); a catalog query over
  `CATALOG.REFS` needs `MXCLI_OUTPUT_LINE_LIMIT=0`.
- **`brain list --json` includes open questions among the decisions** (`open: true`), so filter
  them out or they are counted twice.
- **Lint's "Quality 0"** is 35 warnings + 134 info; the most frequent rule overall is MPR006 (94
  empty containers, mostly CSS-drawn dots), then CONV009 27 and QUAL003 17.
- Layout: a 6600-wide lane only reads at about 15 px when the type is at least 60 units; the
  first draft (52 units, one card per decision) gave a lane 0 too tall to read zoomed.

## 2026-11-19 — RUN delivery files

The six files of `12-acceptance/deliverables.md` now exist in `RUN/`.

- **`start.ps1` / `stop.ps1`** drive `mxcli run --local --detach --db-type hsqldb`, so Windows
  needs only a JDK 21 (no PostgreSQL, no Docker). Constants are passed per run with
  `--constant` and never touch the model. Verified on Linux with the same mxcli arguments:
  - A start at speed 10 with a reset served in 41 s and logged
    `CONFIG SpeedFactor=10 ResetOnStartup=true` and `RESET start by startup`.
  - A restart without a reset kept the HSQLDB data.
  - `SpeedFactor=7` logged `CONFIG invalid SpeedFactor=7, using 1`.
  - `run stop` is idempotent (exit 0) and left the port closed.
  - The `.ps1` files were **not** run on Windows: installing PowerShell here was not permitted
    (KI-01).
- **The mxcli download can't be pinned.** Only the rolling `nightly` release has a Windows
  binary; dated tags 404. `start.ps1` prefers a local `mxcli.exe` / `MXCLI` (KI-02).
- **`self-assessment.json`** is generated by `tools/run_self_assessment.py` from the
  traceability data plus each story's screen list (only the PRD table rows are read). Result:
  109 done, 2 partial, 0 no. 11 stories have no automated test linked; J5 and J6 cover US-281
  and US-287 but run no microflow, so traceability can't see them.
- **Found while writing the notes:**
  - A-91 is not built: the cursor blink and live-dot pulse are infinite CSS animations
    (DEV-03).
  - `no-results.png` is missing, so the no-results state shows a broken image instead of a
    placeholder (KI-04).
  - `mx check --warnings` reports 53 warnings.
- **The journal was reconstructed** from commit times, this file and the brain (DEV-07). The
  brain's open question cb8adb is resolved.

## 2026-11-19 — performance at volume and Rooster-style reports

Compared with ako/RoosterV1, whose reports come from project-written generators with
hand-written analysis. Ours were mxcli's built-in HTML. Rebuilt both pages the same way:
`docs/perf/report.html` and `docs/architecture/report.html`. Their generators live in
`tools/`, and the data sits next to them.

**Volume seed.** `docs/perf/tools/seed.sql` adds 400,000 guest orders over 365 days, about
10M rows, in about 4 minutes of direct SQL. It was taken after a backup and restored
afterwards, along with the Postgres settings.

**Bugs found and fixed:**
- **F1 — housekeeping blocked checkout.**
  - The cause: housekeeping deleted every simulation event older than 24 h in one
    transaction, inside the simulator tick. With 800,089 such events, that transaction held
    the store-settings lock until the runtime aborted it 10 minutes later. Every
    `Execute Order` waited on that lock.
  - Because the abort rolled back "last run" too, it restarted every tick, so the shop took
    no orders at all.
  - Verified in `pg_stat_activity` (idle in transaction, a Lock wait on
    `core$storesettings`) and in the runtime log (`Transaction … aborted due to timeout`).
  - Fix: delete in batches of 1,000 events and 50 orders per tick. On the same backlog this
    takes 28 ms per tick, and every journey step completed during the drain.
- **F2 and F3 — three missing indexes.** Each replaced a full scan of 400,000 orders:
  - `Order.CompletedAt` (the KPI query went from 63.5 to 5.4 ms);
  - `Order(Source, IsOpen, StatusChangedAt)` (the traffic and housekeeping scans; housekeeping
    now takes 0.07 ms);
  - `SimulationEvent.OccurredAt`.
- **F4 and F5 — query fixes.**
  - The menu ran one data source per card. It went from 199 to 75 queries and from 418 to
    224 ms.
  - The configurator and line pricing read data per option and per ingredient. Queries fell
    from 305 to 195, and add-to-cart database time from 259 to 89 ms.
  - Verified with 24/24 tests, 11/11 journeys and 12/12 visual comparisons; menu desktop
    mismatch went from 2.46 to 3.01 %.

**Tool behaviour worth knowing:**
- **The built-in step "server time" includes background work.** Any span inside a step's
  window counts, so the simulator's queued tick (a 1.5 s sleep) added up to 1.6 s to random
  steps. `docs/perf/tools/analyse.py` counts only traces rooted in a guest request on
  port 8080.
- **The browser step time includes the 2 s live poller** when it falls inside the window, up
  to about 200 ms. "Place order and pay" lands on one of two plateaus (3.8 or 5.8 s), set by
  the tick.
- **`ALTER SYSTEM` for `auto_explain.*` is refused** until the library is loaded: restart
  with `shared_preload_libraries` first, then set the settings.
- **`mxcli -c` aborts above 10,000 output lines**: use `MXCLI_OUTPUT_LINE_LIMIT=0`.

**Architecture:**
- The generated seed (`Simulation.SEED_*`, 186 of 369 microflows) makes Simulation's cohesion
  2.8 %; without it, it is 9 %.
- The simulator calls into the storefront 7 times: the payment decision, line pricing,
  order placement and catalog recalculation.
- Recommended in the report:
  - move `Shop.SUB_Payment_Resolve` to Fulfilment;
  - give order placement and pricing a home below Shop;
  - put the seed in its own module.
- Of the 4 "unused" documents, 3 are reached by URL or a client hook.
- **Offline check (all report pages).** All report pages were opened from `file://` with the
  network blocked: they render, run their scripts, and the links between pages resolve. The
  only network request was Google Fonts in the two new reports. Those reports now embed the
  app's own fonts (JetBrains Mono, Geist, OFL) as data URIs via `tools/report_fonts.py`,
  about 140 KB per page, so they look the same offline.

## 2026-11-19 — all reports in one house style

All eight report pages share `tools/report_kit.py`: the overview, traceability, tests,
performance, architecture, security, quality and the software map (restyled by
`tools/restyle_map.py`). They embed their fonts, link each other and work offline.
`docs/reports/README.md` describes the rebuild. Data refreshed on the current model:
24/24 tests, 11/11 journeys with spans, traceability 109 built / 2 partial.

Found while writing them:
- **Tests and journeys:**
  - J9 never removes a single cart line, despite its name, so US-064 is unproven.
  - The tracking-link grant and its refusal of a bad token have never run in any test or
    journey.
  - Microflow tests reach only 5 requirements.
  - 11 stories count as reached by all 11 journeys, because their flows run on the clock
    or on every page.
- **Security:**
  - CONV008 was untriaged; it is now marked intended.
  - The SEC001 note now names `Fulfilment.Coupon`.
  - The report's "reads only" label looks at a flow's own body only. The flows are safe
    because of the read rules on what they take.
- **Quality:** brain decision 071314 says no quality rule was switched off, but
  `.claude/lint-config.yaml` disables CONV002, which lint files under quality.

## 2026-11-19 — tests for the gaps the reports found

- **J12, tracking link.** One guest places an order and reads the tracking link from the
  confirmation. A second browser context (a new anonymous session) opens it and sees that
  order. An altered token shows `DEPLOYMENT_NOT_FOUND` and no order.
- **J13, cancel after a declined card.** The cancel button on the payment sheet, then
  "Cancel order" in the dialog. Checks the "cancelled, nothing charged" toast and that the
  cart still holds the item.
- **J9, remove a line.** It now adds a second line and removes it with that line's own
  `rm` button, so US-064 is proven.
- **The cart's list items are plain `li` elements** (`mx-name-index-N`), not
  `.mx-listview-item`. Select them with `.mx-window li` plus `hasText`.
- **Results:** 13/13 journeys pass, twice. Microflows reached went from 121 to 128 of 170.
  The 7 newly reached are `ACT/SUB_Track_Token`, `ACT/SUB_Pay_Cancel`,
  `ACT_Pay_CancelAndCart` and `ACT/SUB_Line_Remove`. Stories reached by a test or journey
  went from 100 to 101.
- **The tests page's gap guard caught it.** `gen_tests.py` asserts that its gap groups match
  the data exactly, so it refused to render until the groups were updated.

## 2026-11-19 — mxcli main (nightly-54-g619bce7d) tested on GitPizza

Built from ako/mxcli main. The build needs ANTLR: run `make -C mdl/grammar bootstrap`, then
`ANTLR4_TOOLS_ANTLR_VERSION=4.13.2 make build`. It was run next to the project's binary
(nightly-20261118); the project binary was not replaced.

**Clean:**
- **Scripts:** all scripts pass `check --deprecations=error --v1=error`.
- **Exec:** re-executing every script writes nothing (exec is idempotent, the working tree
  stays clean).
- **Build and tests:** `docker check` 0 errors; microflow tests 24/24; the app boots in
  31 s; journeys 13/13; visual comparison 12/12.
- **Brain:** `brain check` OK.

**Fixes confirmed on our model:**
- **Security:**
  - `Shop.DS_Info_Line` is no longer a false "high"; it is rated low because sub-microflow
    caller checks are followed.
  - Constants are now part of the report.
  - The grid's create and delete columns are not checked separately here.
- **Architecture `--exclude-docs 'Simulation.SEED_*'`:** Simulation's cohesion is 8 % (our
  hand estimate was 9 %), and the three seed clusters drop out.
- **Annotations:** an `unused:FaultProbe` key without the module prefix now applies (the old
  binary reported it as "matched nothing").
- **Tests report:** startup flows (seed, catalog recalculation) and scheduled flows are
  listed apart, and gaps are grouped by kind.

**New:**
- **Lint MPR017:** a Boolean a decision tests but which can only be true. It fires 3 times:
  `IsActive` on Catalog.Option, Fulfilment.Coupon and Fulfilment.DeliveryZone. That is
  accurate for Lite, where nothing deactivates them. Lint: 246 → 249 findings.
- **Scored report:** now also runs `mx check` (54 warnings, 1 deprecation). Score
  47.5 → 47.1, from the "Other" category.
- **`report configuration`:** flags `Shop.AppUrl`, whose localhost default must be
  overridden; the other 3 constants keep their defaults.
- **`report readiness` and `report all`:** all ten reports in 20 s, every page error-free
  offline. Verdict: "not assessed in full", 0 blocking.

**Problems with `report all` / readiness** (filed as ako/mxcli#2451):
1. **`--journeys` and `--spans` reach only the tests and performance reports, not
   traceability.** Readiness therefore claims 57 of M1's requirements have no test or
   journey, against 101 of 111 proven when traceability gets the evidence
   (`cmd/mxcli/cmd_report_all.go` passThrough).
2. **`report all` has no `--junit` flag.** The tests report shows "no test results were
   read", so readiness can never be fully assessed from `report all` alone.
3. **One `--journeys` log feeds both the tests and the performance report.** A functional
   journey log turns each whole journey into a "performance step", and every journey then
   shows as a risk over budget.
4. **Readiness "accepted" counts only report verdicts (1), not brain decisions.** Our
   "Accepted SEC007: …" decision is prose, not the `--accepts SEC007` form, so it is not
   recognised. Re-recording it with `brain capture --accepts` would fix that on our side.

Not verified:
- **Open questions as questions:** the brain has no open question left, and a scratch brain
  without a project did not promote.
- **Test-runner leftover:** the `mxtest` line the test runner leaves in
  `UserActionsRegistrar.java` is still there with the new binary.

## mxcli verify (main build, tried 2026-11-19)

`mxcli verify` (main only, not in the project binary) runs check → lint → mx check in ~16 s and compares against a baseline.
- First run with no baseline: check PASSED, mxcheck PASSED, lint FAILED (exit 18). The only errors were the two SEC007 guest-readable entities (`Catalog.Allergen`, `Core.StoreSettings`). Both are already triaged as intended in `docs/reports/security-annotations.yaml`, but verify doesn't read that file.
- mxcheck counted 0 findings, while a direct `mx check` gives 53 warnings, so it seems to track errors only.
- After `--update-baseline` (kept in the scratchpad, not committed), a rerun passed with 0 new findings and exit 0.
- It covers only static gates; unit tests, journeys and the running app are still separate steps.

## mxcli verify put to work (main build, 2026-11-19)

A baseline is committed in `verify-baseline/` (247 lint findings, 0 mx check errors). Run it with the main build: `mxcli verify -p GitPizza.mpr [script.mdl]`.

**Real changes, gated by verify:**
- `Simulation.SIM_ClockRun`: the 1.5 s sleep used "rollback" error handling, so a failed sleep stopped the clock for good. The sleep and the tick now both have custom handlers that log a warning and continue, so the next beat is always queued. The first attempt (`on error continue`) was flagged by verify as a new CONV014 while CONV013 stayed. The final version: 0 new, 2 fixed.
- KI-04: the menu's no-results state showed a broken `no-results.png`. It is now a dashed placeholder with a `search_off` icon, checked in the running app (no broken images).
- Gates: check passed, exec twice (second unchanged), lint 244 → 2E/97W/145I, report 48, docker check 0 errors, tests 24/24, journeys 13/13.

**Deliberate regressions, on a copy of the project:**

| Change | Caught by | Exit |
|---|---|---|
| Script with an unknown entity | check stage | 17 |
| Guest read on all coupons (no XPath) | lint, SEC007 error | 18 |
| New entity without access rules | passes by default; lint fails with `--fail-on warning` (SEC001) | 0 / 18 |
| Drop `Catalog.Product.CodeToppings`, still used by a microflow and a page | **only** mx check (CE1613); `mxcli check` passed it, and exec only printed a warning | 20 |

**Problems found in verify / mxcli** (filed as ako/mxcli#2453 (1, 5), #2454 (2), #2455 (3, 6), #2456 (4)):
1. Several scripts (`verify a.mdl b.mdl`): the check stage fails with "--format json writes one document for one script". The help advertises `[script.mdl...]`.
2. Flaky MPR017: on the first verify after a model change it logs "could not read their attributes". Its 3 findings then count as "fixed" and a bogus new warning appears. A second run is correct.
3. Lint configuration is not part of the baseline. With `.claude/lint-config.yaml` missing, 383 Marketplace findings appear as "new"; with `.claude/lint-rules/` missing, 115 findings show as "fixed" and the gate passes.
4. `mxcli check` does not warn when a script drops an attribute that pages or microflows still use; only mx check catches it.
5. Minor: the check stage has no baseline unless scripts are passed with `--update-baseline`, so pre-existing script warnings show as "new". The text output also never names them (MPR010 on `Shop.Menu`).
6. verify does not read `docs/reports/security-annotations.yaml`, so the two triaged SEC007 errors are accepted only through the baseline.

## ako/mxcli PR 2452 (report all inputs, fixes #2451), tried 2026-11-19

Built from the PR head (`3682d904`) and run against this project's evidence (`docs/reports/raw/` journeys, spans and junit; `docs/perf/data/after-*` as the performance run).

**Fixed, confirmed:**
- Traceability inside `report all` matches the stand-alone report requirement by requirement: 101 of 111 proven (it was 5 before).
- Tests reads 24 results and 13 journeys; readiness counts tests as assessed.
- Performance has the 12 real steps from the perf run, and no whole journey is a step over budget any more. Readiness risks went from 57 false "unproven" items to 14 real ones.
- Readiness's Accepted section explains which acceptances count, and each tile now has a label. With our annotations in the output folder, guest access shows as accepted.
- All pages load offline without errors.

**Still open (found while testing the PR):**
1. `--run` always uses Docker; `report all` has no `--local`, so it fails here ("no Docker daemon … pass --local"). The failed run left a `.docker/` folder in the project (removed).
2. When `--run` fails, tests **and** traceability are both dropped, though the journeys alone could still feed them. The overview gives the reason as "open …/junit.xml: no such file" instead of the test run failing.
3. Readiness says "not given" for a report that was given but failed (tests and traceability after a failed `--run`; performance when the spans file was unreadable). It should say "failed: …".
4. `--perf-spans` does not read `.gz` (already noted in the PR as a separate limitation).
5. `report all` reads `<kind>-annotations.yaml` only from the output folder, so `docs/reports/*-annotations.yaml` must be copied there or written into `-o docs/reports`.

## ako/mxcli PR 2458 (verify/lint baseline records the rules that ran), tried 2026-11-19

Built from the PR head (`b6e66cf1`), run on a copy of the project (model, widgets, `.claude/lint-rules`, `.claude/lint-config.yaml`).

| Scenario | Before (main) | PR 2458 |
|---|---|---|
| Unchanged, our committed (old-format) baseline | pass | pass, `0 new, 247 known`; the old file still loads |
| No `.claude/lint-rules/` | 115 "fixed", **pass** | `112 not checked`, warning names the rules, **exit 2** (old and new baseline) |
| No `lint-config.yaml` | 382 new | flagged "configuration differs", exit 2 |
| First run after a model change (MPR017 can't run) | bogus warning + 3 "fixed" | `3 not checked`, no bogus finding; same new findings and exit as the second run |
| Harmless change, only MPR017 failing | wrong counts | exit 2 naming MPR017; second run passes |
| Guest reads all coupons / entity without access | 18 / 18 with `--fail-on warning` | same, on first and second run |

**Still open:**
1. Trap: `--update-baseline` while a rule cannot run (first run after a change) records the baseline **without** that rule's findings (MPR017's 3 dropped). It prints a warning but exits 0. The next run shows them as 3 new warnings, which fails a `--fail-on warning` gate. The exit-2 message of the failing run itself advises "re-record with --update-baseline". Better: refuse (exit 2) or carry the old findings over for rules that did not run.
2. For a rule that *failed*, the advice "Run lint where the project's rules and config are installed" is the wrong remedy (the rule is installed). It should say the rule failed, with its error, and suggest rerunning.
3. Not in this PR: several scripts still break the check stage (ako/mxcli#2453); the MPR017 catalog cause is #2457; annotations (#2455 part 2); drop-attribute check (#2456).

## Retest of PR 2452 (`019c1d82`) and PR 2458 (`5a4e94b8`) after review fixes, 2026-11-20

**PR 2458:**
- `lint --update-baseline` and `verify --update-baseline` both refuse while MPR017 cannot run: exit 2, naming the rule and its error. The baseline file stays byte-identical.
- The stage message for a failed rule now gives the rule's own error and suggests running again ("run verify again, and report the rule if it keeps failing").
- Nit: the refusal message repeats the reason and misses a full stop before "A rule that ran into an error…".
- Still open, by the author's own note: re-recording where the custom rules are *missing* (not failing) still shrinks the baseline. It's the owner's call whether that needs a guard.

**PR 2452:**
- `--run --local` ran the 24 unit tests on mxcli's own runtime, into `<out>/junit.xml`. Traceability proves 101/111 with `hasTests`; tests reads 24 results and 13 journeys.
- `--perf-spans after-spans.jsonl.gz` is read directly: 12 perf steps.
- `--annotations-dir docs/reports`: the overview lists the four annotation files read, and readiness shows 1 accepted.
- A failed `--run` (no `--local`, no Docker): tests and traceability still render (101 proven from the journeys). Readiness says "`mxcli test` did not finish cleanly … add --local" instead of "not given".
- **Still open:** the failed Docker run still leaves `.docker/` (docker-compose.yml, `.env`, `.env.example`) in the project directory (removed by hand).

## Why Studio Pro 11.16.1 asked to convert the project (commit efcd980), 2026-11-20 — filed as ako/mxcli#2467

The `.mpr` metadata is unchanged by the conversion (`_ProductVersion`/`_BuildVersion` 11.16.1, the same `_SchemaHash`), so the version stamp is not the trigger. Studio Pro changed:

1. **One one-time conversion, the actual trigger.** `Projects$ProjectConversion` gained `UseMeToSetupNodeConversion` (119 → 120 conversions). A new unit `Projects$SetupSettings` was added (`mprcontents/bd/49/bd49d28c-…`): the App Explorer setup node, with a shortcut to `FeedbackModule.FeedbackWidget` and Pages/Nanoflows/Microflows folders. `mx` 11.16.1 does not know this conversion: a project fresh from `mx create-project` has the same 119 conversions and no SetupSettings unit, and `mx convert` does not add it. So every project made by mxcli/mx gets this prompt once in Studio Pro.
2. **462 units re-saved with only a new key order.** Studio Pro writes `$ID`, `$Type`, then the other keys alphabetically; mxcli writes its own order (e.g. `ChangeActionItem`: mxcli `Attribute, Association, …`, Studio Pro `Association, Attribute, …`). That affects 89 object types (ChangeActionItem 15,706 objects, SequenceFlow 4,827, ActionActivity 3,558, …). The content is identical (BSON compared ignoring order). All rewritten units are ones mxcli wrote (363 microflows, 28 enumerations, 16 pages, 15 snippets, …). `mx convert` on a fresh `mx create-project` project changes no unit.
3. **Two list-marker fixes** (the integer that opens a BSON list):
   - an empty `Security$ModuleSecurity.ModuleRoles`: mxcli wrote 1, Studio Pro writes 3 (as every Studio Pro-made ModuleSecurity has);
   - `Microflows$JavaScriptActionCallAction.ParameterMappings` in 3 nanoflows (`DS_Shell_Live`, `NF_CopyLink`, `NF_CopyHash`): mxcli wrote 3, Studio Pro writes 2 (as for every ParameterMappings list).

**Reproduced:** `mx convert --in-place` on the commit before (`efcd980~1`) gives byte-identical results for all of change 2 and 3; it differs from Studio Pro only in change 1.

**After the conversion:** re-executing scripts `35`, `08` and `02` writes nothing (mxcli compares content, not key order), and mx check reports 0 errors. A unit mxcli *does* modify is written back in mxcli's key order, a cosmetic diff that Studio Pro reads without a prompt.

## ako/mxcli main `7efedabd` (nightly-75), tried 2026-11-20

It merges PRs 2452, 2458, 2457, 2459 (#2456) and 2447 (`verify --apply/--through`). Tested on a clean `git worktree` of this project; a hand-made copy without `themesource/` gives 900 bogus CE0535 errors, so copies must be full checkouts.

| Issue | Result on main |
|---|---|
| #2451 report all inputs | fixed (tested on the PR) |
| #2453 several scripts | **fixed**: "2 scripts checked as one set"; the bad reference in one is reported; warnings are printed by name. The issue is still open |
| #2454 / #2457 MPR017 after a change | **fixed**: the first lint after `exec` gives the right counts (3 runs). #2454 is still open |
| #2455 baseline rule set and config | fixed (tested on the PR). The annotations part is still not done |
| #2456 drop of a used attribute | **partly** (snippet gap filed as ako/mxcli#2468): `check` now rejects dropping `Product.CodeToppings` (MDL108, names the microflow). But references from a **snippet through its parameter** (`$Product/CodeToppings` in `SNIP_CodeBlock`; `$Card/Title` in a minimal repro) are not in the catalog, so `show references` and MDL108 miss them. `check` passes; mx check fails with CE0117. Affects every `SNIP_*` here (`CardPriceLabel` lists only `Shop.ItemInfo`, not `SNIP_MenuCard`/`SNIP_FeaturedCard`) |
| `verify --apply` | a failed check writes nothing; a passing one execs, lints and mx-checks. When mx check then fails, the change stays written (documented: "Writes the project"; git is the undo), and the output does not say so |
| Committed `verify-baseline/` | still valid on main: 0 new, 247 known, mx check passes |

## Switched the project to mxcli nightly-75-g7efedabd (ako/mxcli main), 2026-11-20

- `./mxcli` is the ako/mxcli main build `7efedabd` (built here). The old binary was `nightly-20261118-9d764483c`.
- `mxcli init --sync-skills .` refreshed 14 skill files and added 5 report skills (configuration, dependencies, quality, readiness, release). It also refreshed the mxcli section of `CLAUDE.md`/`AGENTS.md`: the gate list now uses `verify` (lint plus mx check against `verify-baseline/`) instead of separate `lint` and `docker check`. The tooling stamp is now `nightly-75-g7efedabd`.
- `verify-baseline/lint.json` was re-recorded in the new format (61 rules ran, plus the lint-config fingerprint; 247 findings, unchanged).
- **Compatibility:** all 28 scripts pass `check`. The new binary also reports 12 MDL-PERF01 and 5 MPR010 warnings at check time; these are the same commit-in-loop (CONV011) and layout-grid findings already in the baseline. Re-executing all 28 scripts wrote nothing.
- **Gates:** verify 0 new / 247 known, mx check 0 errors; report 47 (48 with the old binary, a scoring difference); tests 24/24; visual 12/12; journeys 13/13 on 2 of 3 runs (the first run after boot had one failure, not captured; the model is unchanged).
- **Fresh sessions:** the binary is git-ignored. `.claude/bootstrap-mxcli.sh` downloads `mendixlabs/mxcli` `nightly`, currently `nightly-20261119-32a67fa4a`, which predates these fixes. The stamp is a dev version, so the bootstrap does not loop, but `init --sync-skills` will refuse to downgrade. A fresh session therefore runs the older binary with this newer guidance (e.g. `verify --apply`) until a nightly includes main's fixes. `RUN/start.ps1` downloads the same nightly (KI-02).

## Reports regenerated with mxcli nightly-75-g7efedabd, 2026-11-20

Fresh evidence, following `docs/reports/README.md`: the app was started with a demo reset and tracing (64k spans), then the 13 journeys (13/13) and 24 unit tests (24/24) ran. Every JSON and page was regenerated; the pages load offline at 390 px with no errors.

| Report | Old binary (11-18) | New binary | Why |
|---|---|---|---|
| Tests | 24 tests, 13 journeys; 363 microflows: 11 both, 117 journeys only, 193 startup, 42 neither | **same** | new: the gaps split into 29 "callable by a role" and 13 "called by other logic"; startup and scheduled-event flows are listed |
| Traceability | 109 built, 2 partial, 101 proven (5 by tests, 101 by journeys) | **same** | the fresh run reproduces the evidence |
| Security | 1 high finding (`Shop.DS_Info_Line`, already annotated as a false alarm), 34 medium flows | 0 high; `DS_Info_Line` now medium ("reads an object the client chose"); `ACT_Configure_FromHome` medium → low (caller check in a sub-microflow) | the analysis follows sub-microflows: each medium flow now names the sub-microflow that writes. New: a constants section |
| Quality | 47.5, 246 findings | 47.4, 247 findings | CONV013 and one CONV014 gone (the SIM_ClockRun fix); new rule MPR017 adds 3 warnings (`IsActive` never set false). `docs/quality/tools/gen_quality.py` now maps MPR017 to Other and triages it as an open decision |
| Architecture | — | **identical** data | |
| Performance (same "after" volume recording, re-analysed) | 6,569 ms server over 12 steps; step 8 "place order and pay" 4,884 ms | 1,706 ms; step 8 280 ms | the new analysis counts only traces rooted in an app request (`attribution: requests`), so the simulation's 1.5 s clock tick no longer lands in a step. Its query counts now match our own guest-only analysis (`docs/perf/data/after.json`) within 3 per step |

The perf house page (`docs/perf/report.html`) is unchanged: it is built from our own analysis of `docs/perf/data/`, not from mxcli's figures. The annotation for `finding:flow:Shop.DS_Info_Line` is now stale (no such finding any more).

## ako/mxcli PR 2475 (perf ranges and findings, traceability table), tried 2026-11-20

Built from `def69a53`. Performance: before and after volume runs re-analysed (`docs/perf/data`, `--baseline`), with F1–F8 annotated as `finding:Fn` and six steps tagged `{finding: Fn}`. Traceability: rendered from `docs/reports/raw/traceability.json`. Desktop and 390 px, offline: no page errors, no page overflow.

**Works:**
- Ranges: `144 (122–299) → 78 (55–117)`. A change inside the spread stays uncoloured (open home server 504 → 461); one outside it is coloured (configurator browser 395 → 498, red: the ranges do not overlap).
- Finding cards list each targeted step's before → after (F5: three steps, 307 → 197, 299 → 189, 466 → 318 queries). Findings named by no step say so (F1, F3, F6, F7).
- Background work is listed apart from step time (4.7 s on "place order and pay").
- "Every requirement": 111 rows (milestone, epic, requirement, status, proven by).

**Points:**
1. The finding cards give server time and queries but not database time, where F2's effect is (KPI query 63 → 5 ms). They also omit the ranges the table shows, so noise (F2's 504 → 461 server) reads as an improvement.
2. "No step names this finding" reads as a mistake for findings that are not about a step (F1/F3 housekeeping, background). A way to mark them background/not-a-step would help.
3. There is no status for "by design" (F8 renders as open).
4. The Note column repeats the ID when the note starts with it ("finding F2: F2: …").
5. The "plans dominated by JIT 0 of 0" tile shows when no plans were read.
6. Traceability table at 390 px: status and "proven by", the useful columns, are scrolled off to the right (inner scroll). Milestone and epic repeat on every row.
7. Rows with no footprint (US-004 DEMO MODE banner: no microflow, so nothing can "reach" it) show a plain "nothing", unlike the 9 highlighted untested rows, with no reason. UI-only requirements can never be proven this way, although every journey shows the banner.
8. Per-epic bars at 390 px shrink to slivers (the label column takes the width). This predates the PR.

Our own `docs/reports/performance-annotations.yaml` summary was stale (it said server time includes the background clock); it is corrected and `docs/reports/performance.html` re-rendered.

## New report kinds (readiness, configuration, dependencies), 2026-11-20

`report all` with every input and `--annotations-dir docs/reports`. Readiness, configuration and dependencies were added to `docs/reports/` and the overview (`tools/reports_index.py`); release was skipped (no deployed revision to compare against).
- **Readiness:** "not assessed in full". 0 blocking, 14 risks (six lint categories, the 11.16 line not in mxcli's registry, 34 medium flows without a verdict, 29 role-callable microflows untested, requirements partial or unproven per milestone), 1 accepted (guest access). Not assessed: release only.
- **Configuration:** 1 of 4 constants must be set per environment (`Shop.AppUrl`, localhost default); 2 scheduled events (clock watchdog every minute, daily reset at 04:00); `ASU_Startup` reaches 228 microflows and writes the catalog and settings.
- **Dependencies:** 20 of 33 widgets have a newer version, 2 up to date, 11 not identified. **All 7 Marketplace modules are "not identified"** ("no catalog item publishes the version the module records"), although they are the stock modules of `mx create-project` 11.16.1 (Atlas_Core 4.1.3, DataWidgets 3.5.0, …). Worth checking in mxcli. OSV: no vulnerabilities; no Java libraries in `userlib/`.
- **Crash, once:** the first `report all` panicked in the dependencies report's Marketplace scan (`marketplace/client.go:113` in `ListAll`, from `checkMarketplace`); it was the first run, with no catalog cache. It did not reproduce: one more full run, 4 warm runs and 3 runs with the cache deleted all succeeded.
