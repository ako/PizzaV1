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
- **Modules** (layered, no cycles; see `FINDINGS.md`): `PizzaChat` (the pizza assistant) and `Simulation` (simulation, reset,
  seed) → `Shop` (storefront: cart, checkout, pages) → `Fulfilment` (orders, payments,
  couriers, pricing) → `Catalog` (products and options) and `Core` (settings, toasts,
  helpers).
- **Mendix:** 11.16.1. MDL scripts are `mdl 1` (each starts with `mdl 1;`) and live
  in `mdlsource/`.

## Pizza chat (optional)

A pizza assistant on every page (floating chat button, bottom right): it searches the
menu, explains diets and allergens, checks delivery to a ZIP code and follows the
guest's own orders, answering with cards: products with an Add to cart button, the
live cart with Checkout, a delivery map and an order card with its timeline and map.
The assistant only reads and proposes; the guest presses the buttons. Built like
`ako/ChatV2` (Agents Kit, Conversational UI, an Agent Editor agent on Mendix Cloud
GenAI, the `PizzaChatText` card widget in `widgets-src/PizzaChat`). See
`docs/brain/modules/PizzaChat.md` and `mdlsource/50`–`52`.

It needs a Mendix Cloud GenAI text key in `GENAI_TEXT_KEY` and an encryption key; both
are passed per run, never stored in the model:

```bash
python3 -c "import secrets,string; print(''.join(secrets.choice(string.ascii_letters+string.digits) for _ in range(32)), end='')" > .mxcli/encryption.key
./mxcli run --local --detach --ensure-db -p GitPizza.mpr --constant Encryption.EncryptionKey=@file:.mxcli/encryption.key --constant PizzaChat.MxGenAIKey=@env:GENAI_TEXT_KEY
```

Open the app on **http://localhost:8080** (not 127.0.0.1: Conversational UI's streaming
picks its session cookie by host name). Without the key the app runs as usual and the
chat answers that the assistant is not available.

### Studio Pro on your laptop

The project has a **pgdev** configuration (App > Settings > Configurations) for running
from Studio Pro against a local PostgreSQL: `localhost:5438`, database `pizzadb`, user
`postgres`, app on http://localhost:8083. Make it the active configuration and run locally.

For the pizza chat, set two constants on its **Constants** tab: `PizzaChat.MxGenAIKey`
(your Mendix Cloud GenAI text key) and `Encryption.EncryptionKey` (any 32 letters or
digits, the same every run). They are **private values**: Studio Pro keeps them on your
machine, not in the project, so they never reach git. Without them the app runs and the
chat says the assistant is not available.

## Quality reports

Open [`docs/reports/index.html`](docs/reports/index.html) for the overview. Every report has
its own page in one shared look:
- [traceability](docs/traceability/report.html)
- [tests and coverage](docs/testing/report.html)
- [performance under load](docs/perf/report.html)
- [architecture](docs/architecture/report.html)
- [security](docs/security/report.html)
- [quality score](docs/quality/report.html)
- [software map](docs/reports/map.html)

The pages work offline. Each also has mxcli's built-in rendering next to the index.
[`docs/reports/README.md`](docs/reports/README.md) explains how to rebuild them.

## Build overview

A sketched swimlane board of how the app was built from the PRD: lane 0 for crosscutting work,
then one lane per milestone (M1–M4), each with PRD, decisions, model, proof and status, plus a
summary. It is rebuilt from the model by [`docs/overview/`](docs/overview/collect.py) and
published as a private sketch deck: https://claude.ai/artifact/Q6p4C4QndDTCJKuX5hks1D.

## Journey videos

Narrated walkthroughs of the two main guest journeys, recorded against the running
app, filmed at desktop size (1920×1080) and on an iPhone profile. The voice plays
over silence, with no background bed. The order film runs about 2½ minutes and also
shows the delivery map and the pizza assistant; the declined-card film runs about
100 seconds. The scripts that rebuild them are in [`demo/`](demo/README.md).

| Journey | Desktop | Phone |
|---|---|---|
| **Sam orders a pizza**: home → menu → configure Inferno Payload (Large + cherry tomatoes, $25.00) → cart → checkout with the route map → pay → confirmation → live tracking on the map → asking the pizza assistant "Where is my order?" and getting an order card | [order-desktop.mp4](demo/films/order-desktop.mp4) | [order-phone.mp4](demo/films/order-phone.mp4) |
| **A declined card**: Binary BBQ → checkout with the test card the bank declines → retry with Apple Pay → confirmation → order log showing both attempts | [declined-desktop.mp4](demo/films/declined-desktop.mp4) | [declined-phone.mp4](demo/films/declined-phone.mp4) |
