# Fulfilment

<!-- mxcli-brain -->

Decisions anchored to the Fulfilment module. Loaded when Fulfilment is in play,
not otherwise.

## US-288 is partly met: a second payment retry or rollback is refused on the server (the second tab gets a toast), so no order is paid or refunded twice; buttons show no explicit busy state of their own.

Anchors: `@Fulfilment.SUB_Payment_Retry`, `@Shop.SUB_Track_Rollback` · id `9fafa3` · 2026-11-19

Partly meets requirement `58f3c6`: no explicit busy indicator on buttons; server-side guards only
