# Fulfilment

<!-- mxcli-brain -->

Decisions anchored to the Fulfilment module. Loaded when Fulfilment is in play,
not otherwise.

## US-288 is partly met: a second payment retry or rollback is refused on the server (the second tab gets a toast), so no order is paid or refunded twice; buttons show no explicit busy state of their own.

Anchors: `@Fulfilment.SUB_Payment_Retry`, `@Shop.SUB_Track_Rollback` · id `9fafa3` · 2026-11-19

Partly meets requirement `58f3c6`: no explicit busy indicator on buttons; server-side guards only

## Security: guest read on Coupon removed (no page reads it; the code shows as text on the cart); DeliveryZone readable only for the guest's own orders. This also closed the one Fulfilment<->Shop cycle.

Anchors: `@Fulfilment.Coupon`, `@Fulfilment.DeliveryZone` · id `968fd2` · 2026-11-19

## Store time (BR-DATA-05): the runtime's default time zone America/Los_Angeles; order-log times are stored as server-formatted text because client-formatted dates follow the browser's zone.

Anchors: `@Fulfilment.OrderLogEntry.TimeText`, `@Fulfilment.SUB_Order_Log` · id `f2c8ab` · 2026-11-19

## Indexes from the volume test: Order.CompletedAt for the home KPIs, Order(Source, IsOpen, StatusChangedAt) for the traffic generator and housekeeping, SimulationEvent.OccurredAt for housekeeping; each replaced a full scan of 400,000 orders (docs/perf/report.html F2, F3).

Anchors: `@Fulfilment.Order`, `@Shop.SUB_Home_Refresh` · id `42a525` · 2026-11-19
