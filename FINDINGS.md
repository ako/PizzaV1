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
  per category (inferred from the counts).

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
