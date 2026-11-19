# Simulation

<!-- mxcli-brain -->

Decisions anchored to the Simulation module. Loaded when Simulation is in play,
not otherwise.

## Demo data: generated from the PRD's 09-demo-data JSON by tools/seed/gen_seed.py into SEED_* flows (one per order, split into lines/history/log parts); the generator output is byte-identical after every refactor.

Anchors: `@Simulation.SEED_Catalog`, `@Simulation.SEED_Orders` · id `128ecd` · 2026-11-19

## Simulation clock: Mendix scheduled events run at most once a minute, so the clock is a task queue that sleeps 1.5 s, ticks and re-queues itself (SIM_ClockRun), guarded by a minutely watchdog (SE_ClockWatchdog).

Anchors: `@Simulation.SIM_ClockRun`, `@Simulation.SE_ClockWatchdog`, `@Simulation.SimulationClock` · id `1ee26b` · 2026-11-19

## Housekeeping deletes in bounded batches (1,000 events, 50 orders per tick, oldest first) and marks its run done only when a batch comes back short: deleting a backlog in one transaction inside the simulator tick held the store-settings lock for 10 minutes on a 400,000-order volume seed, blocked every checkout and was aborted by the runtime (docs/perf/report.html F1).

Anchors: `@Simulation.SIM_Housekeeping`, `@Fulfilment.SimulationEvent` · id `b327f8` · 2026-11-19
