---
milestone: "M3 — Simulated kitchen and couriers"
---

# Slice: 14-simulation-control

<!-- mxcli-brain -->

Requirements for this slice. Anchors point FORWARD, at what the slice
will build — an anchor that does not resolve yet means not built, not
stale. `mxcli brain plan` counts them against the model.

## US-265 Order traffic generator

Anchors: `@Simulation.SIM_Traffic`, `@Simulation.SUB_Traffic_Spawn` · id `51fbc1` · 2026-11-19

As a guest watching the demo, I want simulated customers to keep ordering, so that the kitchen, the couriers and the home page KPIs are always busy. (Git Pizza MxDev Lite user story US-265, EP-14.)

## US-270 Reset the demo

Anchors: `@Simulation.SUB_Toast_Broadcast` · id `e07c78` · 2026-11-19

As the owner, I want the demo data to be restored to the initial state automatically, so that every test run and every demo day starts from the same, complete dataset. (Git Pizza MxDev Lite user story US-270, EP-14.)

## US-271 Live log lines for every step

Anchors: `@Fulfilment.SUB_Order_Log`, `@Fulfilment.SUB_Order_Transition` · id `44dd09` · 2026-11-19

As a guest, I want every step of my order to be written to its log in terminal style, so that the pipeline is transparent. (Git Pizza MxDev Lite user story US-271, EP-14.)

## US-272 Simulated pickup arrival

Anchors: `@Simulation.SIM_Pickups` · id `8469a6` · 2026-11-19

As a guest who ordered pickup, I want a simulated customer arrival to complete pickup orders, so that pickup orders finish without anyone operating the store. (Git Pizza MxDev Lite user story US-272, EP-14.)

## US-273 Housekeeping of old simulated orders

Anchors: `@Simulation.SIM_Housekeeping` · id `65937a` · 2026-11-19

As the owner, I want old simulated orders to be removed automatically, so that a demo instance running for weeks stays fast and readable. (Git Pizza MxDev Lite user story US-273, EP-14.)
