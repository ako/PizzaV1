# Findings

Mendix 11.16.1 · mxcli nightly-20261118-9d764483c · MDL scripts `mdl 1`.

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
