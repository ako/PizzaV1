---
milestone: "M2 — Pay and track"
---

# Slice: 09-customer-profile

<!-- mxcli-brain -->

Requirements for this slice. Anchors point FORWARD, at what the slice
will build — an anchor that does not resolve yet means not built, not
stale. `mxcli brain plan` counts them against the model.

## US-166 Order detail and receipt (git show <hash>)

Anchors: `@Shop.ACT_Receipt_Open`, `@Shop.Receipt` · id `f56681` · 2026-11-19

As a guest, I want to open the full detail of my order, so that I can see exactly what I ordered and paid. (Git Pizza MxDev Lite user story US-166, EP-09.)

## US-167 Print the receipt

Anchors: `@Shop.JS_Print`, `@Shop.NF_Print`, `@Shop.Receipt` · id `17fbc5` · 2026-11-19

As a guest who needs a receipt for expenses, I want to print it, so that I can hand it in. (Git Pizza MxDev Lite user story US-167, EP-09.)
