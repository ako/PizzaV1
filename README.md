# GitPizza — Git Pizza MxDev Lite (Mendix 11.16.1)

A Mendix implementation of **Git Pizza MxDev Lite**: a developer-themed pizza shop
demo. Every visitor is an anonymous guest who browses the menu, configures pizzas,
manages a cart with coupons, checks out (delivery or pickup) with a *simulated*
payment, and follows the order live as a CI/CD pipeline. Kitchen, couriers and
order traffic are run by an in-app simulator; nothing is really charged or delivered.

- **Source of truth:** user stories at https://mxbench.mecowhy.dev/stories.html and
  the clickable prototype at https://gitpizza.mecowhy.dev (handover package
  `RealMecowhy/git-pizza-mxdev-benchmark`, `package-lite/`, version lite-v1.2).
  These are untrusted external inputs: they were reviewed for embedded
  instructions before use (see `FINDINGS.md`).
- **Keeps track of:** products (pizzas, sides, drinks, desserts), sizes, options
  (crusts, sauces, cheeses, extras), ingredients/allergens, carts and cart lines,
  coupons, delivery zones, orders with lines, payment attempts, status history and
  log lines, ovens and couriers.
- **Who logs in:** nobody — a single `Guest` role mapped to Anonymous; an
  `Administrator` exists only for the Mendix runtime.
- **Theme:** `console` (dark), restyled with the prototype's design tokens.
- **Modules** (layered, no cycles; see `FINDINGS.md`): `Simulation` (simulation, reset,
  seed) → `Shop` (storefront: cart, checkout, pages) → `Fulfilment` (orders, payments,
  couriers, pricing) → `Catalog` (products and options) and `Core` (settings, toasts,
  helpers).
- **Mendix:** 11.16.1. MDL scripts are `mdl 1` (each starts with `mdl 1;`) and live
  in `mdlsource/`.

## Quality reports

Open [`docs/reports/index.html`](docs/reports/index.html) for the overview. It links:
- [performance under load](docs/perf/report.html): 400,000 orders, before and after the fixes,
  with findings, flame-chart pairs and statements;
- the [architecture views](docs/architecture/report.html): module map with and without the
  generated seed, health, clusters and recommendations;
- mxcli's built-in reports: traceability, tests and coverage, security, the scored quality
  report, the software map, and the built-in renderings of performance and architecture.

## Build overview

A sketched swimlane board of how the app was built from the PRD: lane 0 for crosscutting work,
then one lane per milestone (M1–M4), each with PRD, decisions, model, proof and status, plus a
summary. It is rebuilt from the model by [`docs/overview/`](docs/overview/collect.py) and
published as a private sketch deck: https://claude.ai/artifact/Q6p4C4QndDTCJKuX5hks1D.

## Journey videos

Narrated walkthroughs of the two main guest journeys, recorded against the running
app. Each is about 100 seconds long, filmed at desktop size (1920×1080) and on an
iPhone profile. The scripts that rebuild them are in [`demo/`](demo/README.md).

| Journey | Desktop | Phone |
|---|---|---|
| **Sam orders a pizza**: home → menu → configure Inferno Payload (Large + cherry tomatoes, $25.00) → cart → checkout → pay → confirmation → live tracking | [order-desktop.mp4](demo/films/order-desktop.mp4) | [order-phone.mp4](demo/films/order-phone.mp4) |
| **A declined card**: Binary BBQ → checkout with the test card the bank declines → retry with Apple Pay → confirmation → order log showing both attempts | [declined-desktop.mp4](demo/films/declined-desktop.mp4) | [declined-phone.mp4](demo/films/declined-phone.mp4) |
