# Git Pizza MxDev Lite — Delivery notes

Times in this file are UTC.

## 1. Summary

| Key | Value |
|---|---|
| Delivery date | 2026-11-19 |
| Package version used (00-README section 10) | lite-v1.2 (`package-lite/` of the handover repository) |
| Studio Pro version (exact) | 11.16.1 (MxBuild and runtime 11.16.1 from the Mendix CDN; the build number is not recorded by the command-line tools used, and Studio Pro itself was not used) |
| Git commit of the delivery (hash) | Model and app: `64b0e35`. The `RUN/` files are added in the commit after it, which changes nothing else. |
| Work started / finished | 2026-11-19 06:55 / 2026-11-19 15:45 (UTC) |
| Duration of the work (hours, from the journal) | 8.8 h wall-clock in one continuous session, no recorded pauses. The app with all stories, tests and quality gates was done at 10:46 (3.9 h); the rest was follow-up work asked for afterwards (videos, module split, reports, overview deck, these files). |
| Stories done / partial / no (from self-assessment.json) | 109 / 2 / 0 |
| Deviations (count per type) | NOT_IMPLEMENTED 0 · PARTIAL 3 · CHANGED 5 · INTERPRETATION 3 |
| Known issues (count) | 5 |
| `mx check` errors / warnings | 0 / 53 |
| Guest session inactivity timeout after all tabs are closed (LITE-SES-04, NFR-09.9) | 10 minutes (Mendix default session timeout) |

## 2. Platform and components

### 2.1 Marketplace modules and widgets

| Name | Version | Purpose in this app | Free of charge (yes/no) |
|---|---|---|---|
| Atlas_Core | 4.1.3 | Base layouts and the Atlas UI framework that the Git Pizza theme restyles | yes |
| Atlas_Web_Content | 4.1.0 | Atlas building blocks and page templates (comes with a new app; not used by the storefront pages) | yes |
| DataWidgets | 3.5.0 | Pluggable data widgets of the Mendix platform | yes |
| NanoflowCommons | 6.0.0 | Standard nanoflow actions (comes with a new app) | yes |
| WebActions | 2.11.0 | Standard browser actions (comes with a new app) | yes |
| Administration | 4.3.2 | Account management for the built-in administrator (comes with a new app; no guest access) | yes |
| FeedbackModule | 4.0.2 | Mendix feedback widget (comes with a new app; not placed on any page) | yes |

### 2.2 Custom code

| Kind (Java action / JavaScript action / custom widget / SCSS / other) | Name | Purpose |
|---|---|---|
| Java action | `Simulation.JA_Sleep` | Waits 1.5 s inside the queued simulation clock, so the clock ticks more often than a scheduled event can (minimum 1 minute) |
| JavaScript action | `Shop.JS_LivePoller` | Refreshes the live parts of SCR-01, SCR-05, SCR-08, SCR-09 and the sidebar every 2 s; shows `CONNECTION_LOST //` after two failed refreshes and blocks actions while offline (US-287); remembers the last session for the session-expiry toast (US-286); opens SCR-41 instead of the platform's error dialog (US-289) |
| JavaScript action | `Shop.JS_CopyText` | Copies the order hash or tracking link to the clipboard (SCR-08, SCR-09) |
| JavaScript action | `Shop.JS_Print` | Prints the receipt (US-167) |
| JavaScript action | `Shop.JS_RetryLast` | `RETRY_DEPLOYMENT` on SCR-41 repeats the page load that failed (US-282) |
| JavaScript action | `Shop.JS_ExpandTrace` | Expands the stack-trace block on SCR-41 |
| SCSS | `theme/web/_gitpizza-proto.scss`, `_gitpizza-app.scss`, `_gitpizza-screens.scss`, `_mxcli-gitpizza.scss` | The prototype's CSS and design tokens, ported into the Mendix theme and scoped to `.gp-app` |
| Other | `theme/web/mxcli-fonts/` | JetBrains Mono, Geist and Material Symbols, served from the app (no font CDN) |
| Other | `tools/seed/gen_seed.py` | Generates the seed microflows (`Simulation.SEED_*`) from `09-demo-data/*.json`; not part of the running app |

### 2.3 Security

| Item | Value |
|---|---|
| Security level | Production (strict mode on; demo users off) |
| User roles | `Anonymous` (guests: module roles `Shop.Guest`, `Catalog.Guest`, `Core.Guest`, `Fulfilment.Guest`); `Administrator` for the built-in admin user only, holding the same Guest roles |
| Built-in administrator | User name `MxAdmin`; its demo password is set in the project's app security settings (Studio Pro: App > Security > Administrator). It protects nothing outside this demo. |
| Anonymous users enabled | yes |
| Pages and microflows reachable for `Anonymous` | Every storefront page (SCR-01 – SCR-10, SCR-13, SCR-16, SCR-40, SCR-41) and the `ACT_` page actions behind them. Data access is row-scoped by XPath: a guest reads and changes only their own cart and checkout form, reads only orders granted to their session (`Fulfilment.OrderAccess`: placed, looked up or opened by tracking link, LITE-SES-03) and only customer-visible log lines of those orders; the catalog and the public store settings are read-only for everyone. Simulated orders, couriers, ovens, simulation settings and simulated customers are not readable by guests (LITE-SEC-02, LITE-SEC-05). Data sources check that the object asked for belongs to the caller or is published. |

### 2.4 Third-party runtime requests (NFR-13.7)

| Domain | Purpose |
|---|---|
| none | Fonts, icons, product photos, illustrations and the map image are served by the app itself; no payment, map or analytics service is called |

## 3. How the main mechanisms work (short)

| Mechanism | Description (2–5 sentences each) |
|---|---|
| Simulator (tick mechanism and interval, how timer progress is stored for BR-ORD-21, speed factor from the constant, recovery after restart) — see NFR-07/NFR-08 "Implementation latitude" | The clock is a chain of queued background tasks on the task queue `Simulation.SimulationClock`: `SIM_ClockRun` waits 1.5 s, runs one tick (`SIM_Tick`: payment, kitchen, couriers, pickup, traffic, housekeeping) and queues itself again, so each tick is its own transaction. A minutely scheduled event (`SE_ClockWatchdog`) restarts the chain if no tick happened for 15 s, also after a restart. Every running timer stores its anchor time and the fraction already done (`Order.TimerAnchorAt`, `Order.TimerProgress`, `Courier.TripProgress`, `SimulationSettings.TrafficProgress`), so a change of speed factor only scales the remaining part (BR-ORD-21, LITE-CFG-02). The speed factor comes from the constant `Simulation.SpeedFactor` at start; durations use `eff(x) = max(1, ceil(x / factor))`. |
| Live refresh of SCR-01, SCR-08, SCR-09 and the sidebar (interval, technique, what is kept on refresh per NFR-07.4) | The JavaScript action `Shop.JS_LivePoller` clicks each page's hidden refresh container every 2 s, which re-runs only that block's data source on the server (BR-ORD-20: within 5 s). Inputs, scroll position, open drawers and the selected tab are not re-rendered, so they are kept. |
| Guest sessions, cart and order access (LITE-SES-01 – LITE-SES-05) | Every visitor is a Mendix anonymous user with its own session; the cart belongs to that user. Placing, looking up or opening an order by its tracking link creates an `OrderAccess` row for the session, and every order query is constrained to those rows. The tracking link `/p/track/{token}` works in any browser; lookup (SCR-10) is limited to 5 misses per 10 minutes per session (A-24). The client keeps the session alive while a tab is open; the timeout is 10 minutes after all tabs are closed. |
| Home page KPIs without guest access to other orders (LITE-SEC-02) | A data-source microflow counts orders, pipeline times, kitchen load and couriers on the server, as the system, and returns only the numbers in a non-persistent `Shop.HomeView`. Guests get no read access to other orders. |
| Seed, reset at start, scheduled reset at 04:00, housekeeping | `Simulation.ASU_Startup` writes the `CONFIG` line, applies the speed factor, and resets the demo when `ResetOnStartup` is true, or loads the seed when the database is empty (`initial-seed`). The reset (`SUB_Reset`) deletes all orders and reloads catalog, settings and the seed orders from the generated `SEED_*` microflows (BR-DEMO-03, A-33). The scheduled event `SE_DailyReset` runs every day at 04:00 America/Los_Angeles (A-42). Housekeeping runs from the clock every 15 minutes and removes finished simulated orders older than 24 hours (A-16). |
| Server log lines (log node, where each line is written) | Log node `Simulation`, level INFO: `CONFIG` (and the WARN for an invalid speed) in `ASU_Startup`; `RESET start/end` in `SUB_Reset`; `ORDER <n> <FROM> -> <TO> by <actor>` in the single status-transition microflow every status change goes through, `NEW -> PAYMENT_PENDING` at creation; `COURIER` in the courier status microflow; `SPAWN` in the traffic generator. No contact data, addresses or tokens are logged. Incidents of SCR-41 are logged at ERROR on node `GitPizza`. |
| Price calculation | `Fulfilment.SUB_Price_Compute` computes subtotal, discount (coupon rules, minimum and maximum, delivery-only coupons), delivery fee (free from $40.00 or by `FREE_DISPATCH`), tax 8.625 % on subtotal minus discount, tip on subtotal minus discount for delivery only, and total, rounding half-up to cents at each step (BR-PRICE-05 – BR-PRICE-14). Line prices (size, crust, cheese, extras) are computed by `Shop.SUB_Line_Recalculate`. Both are covered by 16 microflow tests on the worked examples (`tests/pricing.test.mdl`). |

## 4. Mapping of the information model

### 4.1 Objects

Every object of `04-information-model/information-model.md`, in its order.

| Package object | App name (Module.Entity) | Notes (split, merged, not persisted, not implemented) |
|---|---|---|
| Guest and session (section 2) | `System.User` (anonymous) and `System.Session` | No own entity; the guest is the Mendix anonymous user |
| Category | `Catalog.Category` | |
| Product | `Catalog.Product` | Badges as four booleans (`HasBadgeClassic` …) instead of a set of `ProductBadge`; optional `CaffeineMg` for drinks (A-19) |
| ProductSize | `Catalog.ProductSize` | |
| Ingredient | `Catalog.Ingredient` | |
| RecipeItem | `Catalog.RecipeItem` | |
| Option | `Catalog.Option` | |
| Cart | `Shop.Cart` | Also holds the guest's home carousel position and menu filter state (live-refresh technique) |
| CartLine | `Shop.CartLine` | Allergens as a reference set to `Catalog.Allergen` |
| Order | `Fulfilment.Order` | Timer anchor and progress stored on the order (BR-ORD-21) |
| OrderLine | `Fulfilment.OrderLine` | |
| OrderLineModifier | `Fulfilment.OrderLineModifier` | |
| PaymentAttempt | `Fulfilment.PaymentAttempt` | |
| OrderStatusChange | `Fulfilment.OrderStatusChange` | |
| OrderLogEntry | `Fulfilment.OrderLogEntry` | Adds `TimeText`, the store-time timestamp formatted on the server (BR-DATA-05) |
| Courier | `Fulfilment.Courier` | |
| Oven | `Fulfilment.Oven` | |
| DeliveryZone | `Fulfilment.DeliveryZone` | |
| Coupon | `Fulfilment.Coupon` | |
| StoreSettings | `Core.StoreSettings` | Singleton |
| SimulationSettings | `Core.SimulationSettings` | Singleton; `SpeedFactor` stored as the integer 1/2/5/10 (DEV-04) |
| SimulationEvent | `Fulfilment.SimulationEvent` | |
| (app only) | `Catalog.Allergen` | The 14 EU allergens as rows, to implement `Set<Allergen>` as a reference set (allowed by section 9) |
| (app only) | `Fulfilment.OrderAccess` | Which session may open which order (LITE-SES-03) |
| (app only) | `Shop.CheckoutForm`, `Shop.LookupAttempt` | Checkout inputs per guest; failed lookups for the limit of A-24 |
| (app only) | `Core.Toast`, `Simulation.SimCustomer` | Toast messages per session; fictional customers for simulated orders |
| (app only, not persisted) | `Fulfilment.PriceResult`, `Shop.HomeView`, `Shop.MenuView`, `Shop.Choice`, `Shop.TrackView`, `Shop.LookupForm`, `Shop.ErrorView` | Results and view models of pages |

### 4.2 Enumerations

| Package enumeration | App name | Notes |
|---|---|---|
| ProductKind | `Catalog.ProductKind` | |
| ProductStatus | `Catalog.ProductStatus` | |
| ProductBadge | — | Four booleans on `Catalog.Product` (DEV-05) |
| SizeCode | `Catalog.SizeCode` | |
| SpiceLevel | `Catalog.SpiceLevel` | |
| Allergen (EU 14) | `Catalog.Allergen` (entity) | Rows instead of an enumeration, see 4.1 |
| OptionGroup | `Catalog.OptionGroup` | |
| PriceClass | `Catalog.PriceClass` | |
| RecipeRole | `Catalog.RecipeRole` | |
| CouponState | `Fulfilment.CouponState` | |
| DiscountType | `Fulfilment.DiscountType` | |
| OrderType | `Fulfilment.OrderType` | |
| OrderSource | `Fulfilment.OrderSource` | |
| OrderStatus | `Fulfilment.OrderStatus` | |
| PaymentStatus | `Fulfilment.PaymentStatus` | |
| PaymentMethod | `Fulfilment.PaymentMethod` | |
| TestCard | `Fulfilment.TestCard` | |
| PaymentAttemptStatus | `Fulfilment.PaymentAttemptStatus` | |
| PaymentFailureCode | `Fulfilment.PaymentFailureCode` | |
| FeeWaiver | `Fulfilment.FeeWaiver` | |
| TipOption | `Fulfilment.TipOption` | |
| ModifierType | `Fulfilment.ModifierType` | |
| ActorType | `Fulfilment.ActorType` | |
| LogLevel | `Fulfilment.LogLevel` | |
| CourierStatus | `Fulfilment.CourierStatus` | |
| VehicleType | `Fulfilment.VehicleType` | |
| OvenStatus | `Fulfilment.OvenStatus` | |
| IntakeStatus | — | Not stored: the only value in Lite is `OPEN` (DEV-05) |
| SpeedFactor | — | Integer `SimulationSettings.SpeedFactor` (DEV-04) |
| SimulationEventType | `Fulfilment.SimulationEventType` | |
| (app only) | `Core.ToastLevel`, `Shop.StageState` | Toast styling; state of a pipeline step on SCR-08/SCR-09 |

## 5. Deviations

Everything the app does differently from the package, including every Should not implemented and every Could implemented or not.

| ID | Type | Package reference | Package says | App does | Reason | Affected tests |
|---|---|---|---|---|---|---|
| DEV-01 | PARTIAL | US-097 (Could), SCR-06 | Delivery preview map with store and destination markers and the distance (e.g. `2.8 mi`) | Shows the store marker, and a destination marker only for an in-zone ZIP; no distance text, and the destination pin has one fixed position instead of one per zone | Could story; the rest of checkout came first | TCs of US-097 |
| DEV-02 | PARTIAL | US-288 | Busy states on buttons and protection against double submits | A second payment retry or rollback is refused on the server (the second tab gets a toast), so nothing is paid or refunded twice; buttons show no busy state of their own | Server-side guard first; the client busy state was not built | TCs of US-288 |
| DEV-03 | PARTIAL | A-91, `07-design-system/accessibility.md` | Blink and pulse animations run in bursts of at most 5 s (WCAG 2.2.2) | The cursor blink and live-dot pulse run continuously; they stop only when the browser asks for reduced motion | Found while writing these notes; not fixed yet | accessibility checks of animations |
| DEV-04 | CHANGED | LITE-CFG-02, information model 7.6 and 9 | `SimulationSettings.speedFactor` is the enumeration `X1`/`X2`/`X5`/`X10` | Stored as the integer 1, 2, 5 or 10, the value of the constant | The constant is an integer; one representation avoids conversion. Behaviour is the same | none |
| DEV-05 | CHANGED | Information model 3.2 and 9 | Enumerations `ProductBadge` and `IntakeStatus` | Badges are four booleans on the product; intake status is not stored because Lite has only `OPEN` (A-08) | Simpler model; behaviour the same | none |
| DEV-06 | CHANGED | deliverables.md G.3 | One commit per story with `US-xxx: <title>` | Stories that share pages or microflows were committed together with all their IDs in the message; seven stories built inside another story are listed in `Notes:` commits; later work (tests, quality, module split) is committed by area | Stories were built in groups by screen | none |
| DEV-07 | CHANGED | deliverables.md section 3 and section 7 | `RUN/journal.md` written while working; `RUN/` files delivered with the app | The journal was reconstructed at the end from the commit history, `FINDINGS.md` and the project brain; the `RUN/` files were written after the app was finished | The delivery files were missed until the end (see `FINDINGS.md`) | completeness check |
| DEV-08 | CHANGED | NFR-01, deliverables.md G.2 | Project built and opened with Studio Pro 11.16.1 | Built with MxBuild 11.16.1 and the 11.16.1 runtime through mxcli; the model was edited with mxcli (MDL scripts in `mdlsource/`), not in Studio Pro. `mx check`: 0 errors | Tooling of this delivery | none (the project version is 11.16.1) |
| DEV-09 | INTERPRETATION | US-033 (Could), SCR-02 | The story asks for dietary quick filters; the prototype of SCR-02 has none | Built as filter chips above the menu list: Vegetarian, Vegan, Spicy, and Show all | The story wins over the prototype | visual comparison of SCR-02 (chips hidden there) |
| DEV-10 | INTERPRETATION | BR-DATA-05, SIM-07 | All times in store time America/Los_Angeles | The runtime's default time zone is America/Los_Angeles; order-log times are formatted on the server and stored as text, because dates formatted in the browser follow the browser's zone | Store time for every visitor | SCR-09 log timestamps |
| DEV-11 | INTERPRETATION | SIM-09, NFR-07 | Clock tick at most every 2 s | A self-requeueing task-queue chain with a 1.5 s wait, plus a minutely watchdog; Mendix scheduled events cannot run more often than once a minute | Platform limit | none |

Should and Could stories:

| Story | Priority | Built |
|---|---|---|
| US-033 Dietary quick filter | Could | yes (DEV-09) |
| US-034 Menu loading state | Should | yes |
| US-052 Price breakdown | Should | yes |
| US-053 Phone layout with sticky price bar | Should | yes |
| US-093 Pickup details | Should | yes |
| US-097 Delivery preview map | Could | partly (DEV-01) |
| US-136 Lookup abuse protection | Should | yes |
| US-167 Print the receipt | Should | yes |

## 6. Known issues

| ID | Severity (Blocker/Major/Minor/Cosmetic) | Description | Steps to reproduce | Workaround | Affected tests |
|---|---|---|---|---|---|
| KI-01 | Major | `RUN/start.ps1` and `RUN/stop.ps1` were not run on Windows PowerShell 5.1 by the contractor. The commands they run (`mxcli run --local --setup/--detach --db-type hsqldb`, `mxcli run stop`) were run and checked on Linux with the same arguments | Run `RUN/start.ps1 -SpeedFactor 10 -ResetOnStartup $true` on Windows | Run the commands in `RUN/operations.md` section 1 by hand | all, if the scripts fail |
| KI-02 | Minor | `RUN/start.ps1` downloads the rolling `nightly` mxcli release when no `mxcli.exe` is present; a later nightly may behave differently from the one used (nightly-20261118) | Fresh clone without `mxcli.exe` | Put a known `mxcli.exe` in the repository root or set `MXCLI` | all |
| KI-03 | Minor | The local runtime has no licence, so it limits concurrent sessions ("The current licence does not allow more users to sign in"). Each browser context is a new anonymous session | Open many separate browser sessions at once | Log out (`mx.logout()`) or close sessions after each test; restart with `RUN/stop.ps1` + `RUN/start.ps1` | browser tests that open many sessions |
| KI-04 | Cosmetic | `assets/illustrations/no-results.png` does not exist (A-14); the no-results state of SCR-02 shows a broken image instead of the placeholder block | Search the menu for `zzz` | none; the text works alone | visual checks of SCR-02 no-results |
| KI-05 | Cosmetic | `mx check` reports 53 warnings, mostly empty validation templates in the Marketplace Administration module (CW0263) and `CW9509` on the tracking-link microflow `Shop.ACT_Track_Token` | `mx check GitPizza.mpr --warnings` | none needed | none |

## 7. Contradictions and gaps found in the package

| # | Documents involved | Contradiction or gap | Interpretation chosen |
|---|---|---|---|
| 1 | US-033, `08-prototype/customer/SCR-02-menu.html` | The story requires dietary quick filters; the prototype has none | Built as the story says (DEV-09) |
| 2 | Information model 7.6 and 9, `10-simulations/lite-configuration.md` section 1 | `speedFactor` is an enumeration `X1`…`X10`, the constant is an integer | Integer everywhere (DEV-04) |
| 3 | BR-DATA-05, SIM-07 | Store time is required, but a Mendix client formats dates in the browser's zone | Server-formatted log times (DEV-10) |
| 4 | SIM-09, NFR-07 | A tick at most every 2 s; the platform's scheduled events run at most once a minute (a gap, not a contradiction) | Queued clock chain (DEV-11) |
| 5 | `07-design-system/tokens.md`, A-91 | Tokens mark blink and pulse as infinite; A-91 limits them to 5-s bursts | A-91 applies; not yet built (DEV-03) |

## 8. Assumptions

| Assumption (A-xx) | Built as stated (yes/no) | Notes |
|---|---|---|
| A-01 | yes | Store, address and 8 ZIP zones from the seed |
| A-02 | yes | Tax 8.625 % on subtotal minus discount; tested (`tests/pricing.test.mdl`) |
| A-03 | yes | Fee $3.99, free from $40.00, minimum $15.00; tested |
| A-04 | yes | Durations in seconds, scaled by the speed factor |
| A-05 | yes | Tip for delivery only, default 15 %; tested |
| A-06 | yes | Card with five test cards, Apple Pay, Google Pay; no card fields; journeys J1, J3 |
| A-07 | yes | No dine-in |
| A-08 | yes | Always open; no intake pause |
| A-11 | yes | One shared dataset; carts per session |
| A-12 | yes | Traffic always on; `SPAWN` lines in the server log |
| A-14 | no | All product photos present; the missing `no-results.png` shows a broken image instead of the placeholder (KI-04) |
| A-15 | yes | `--font-body` is Geist, the rest JetBrains Mono (vendored fonts) |
| A-16 | yes | Housekeeping every 15 min removes finished simulated orders older than 24 h |
| A-17 | yes | Cancel and rollback only in `QUEUED` (and `PAYMENT_FAILED`); journey J11 |
| A-19 | yes | `CaffeineMg` on products, shown for drinks |
| A-20 | yes | Cart shows fee and tax as "calculated at checkout" |
| A-21 | yes | A new checkout form starts with Card and `VISA_4242` (`Shop.SUB_Checkout_Current`) |
| A-22 | yes | Payment sheet can be closed in the failure state; resumed from SCR-09 |
| A-23 | yes | Session order access via `OrderAccess`; tracking link in any browser |
| A-24 | yes | 5 failed lookups per 10 minutes per session |
| A-31 | yes | Seed dates relative to the reset time; see `RUN/operations.md` section 5 |
| A-33 | yes | A reset reloads the seed orders |
| A-34 | yes | Descriptions, version tags and alt texts of sides, drinks and desserts come from `09-demo-data/menu-items.json` through the seed |
| A-42 | yes | `SE_DailyReset` at 04:00 America/Los_Angeles |
| A-52 | n/a | Measurement condition for the tests; local performance runs are in `docs/reports/performance.html` |
| A-53 | yes | Session kept alive while a tab is open; 10-minute timeout afterwards |
| A-55 | n/a | Thresholds of the acceptance tests |
| A-61 | yes | No header "Execute Order" button |
| A-73 | yes | Real KPIs: deploys today, average pipeline time, kitchen load, couriers on duty |
| A-74 | yes | Confirmation says the oven is assigned when baking starts |
| A-80 | yes | 30-item limit enforced in the cart |
| A-90 | yes | `#6e6e6e` kept for log timestamps and comments |
| A-91 | no | Animations are continuous (DEV-03) |

## Additional notes

### Triggering an unexpected error (US-282 AC2)

1. Start the app with fault injection on, for example
   `./mxcli run --local --detach -p GitPizza.mpr --constant Shop.FaultInjection=true`.
2. Open `/p/fault`. Its data source fails with an unhandled error.
3. The platform's default error dialog is suppressed. The guest is sent to SCR-41 (`/p/error`),
   which shows `ERROR 500 // SEG_FAULT` and `INCIDENT_ID: ERR-yyyyMMdd-HHmmss-XXXX`.
4. The same ID is written to the server log on node `GitPizza` at ERROR level:
   `INCIDENT ERR-… : unexpected error page shown to …`, after the stack trace of the failure.
5. `RETRY_DEPLOYMENT` repeats the page load that failed. `RETURN_TO_MAIN` opens SCR-01.

With `Shop.FaultInjection` off (the default), `/p/fault` only says that fault injection is off.

### Sessions and connection loss (LITE-SES-04, US-286, US-287)

- While a tab of the app is open and online, the client keeps the session alive, and the 2-second
  live poller also keeps it in use. A session expires 10 minutes after all tabs are closed or offline.
- A guest who comes back in a new session after a non-empty cart was lost sees the toast "Your
  session expired. Your manifest was cleared." (TXT-ERR-20). The browser remembers the last
  session ID and cart count in `localStorage`. Orders stay reachable through the tracking link or
  the lookup (SCR-10).
- After two failed refreshes in a row the `CONNECTION_LOST //` banner is shown (TXT-NAV-30); on
  success it hides and TXT-NAV-31 is shown. While offline, every button or link press is stopped
  before it reaches the server and an error toast (TXT-ERR-19) is shown.
