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
- **Mendix:** 11.16.1. MDL scripts are `mdl 1` (each starts with `mdl 1;`) and live
  in `mdlsource/`.
