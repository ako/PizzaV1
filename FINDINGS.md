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
