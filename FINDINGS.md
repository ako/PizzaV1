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
