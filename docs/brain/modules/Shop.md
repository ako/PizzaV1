# Shop

<!-- mxcli-brain -->

Decisions anchored to the Shop module. Loaded when Shop is in play,
not otherwise.

## Module split: Shop was cut into Simulation -> Shop -> Fulfilment -> Catalog + Core, computed from the model's reference graph; 0 domain cycles (report architecture). Lint MPR003 flagged 27 entities in one module.

Anchors: `@Shop`, `@Fulfilment`, `@Catalog`, `@Core`, `@Simulation` · id `04c414` · 2026-11-19

## Security: every visitor is the anonymous user role (no sign-in, no demo users, per the PRD); the built-in Administrator holds the same Guest module roles instead of unconstrained reads on every entity.

Anchors: `@Shop.Guest`, `@Fulfilment.Guest`, `@Catalog.Guest`, `@Core.Guest` · id `1b8578` · 2026-11-19

## Theme: the prototype's CSS is ported into the Mendix theme scoped to .gp-app, with hand-written adapters for Mendix DOM (list views, pop-ups, data views); Atlas data-view overflow neutralised so sticky panels work.

Anchors: `@Shop.Layout_Guest`, `@Shop.Layout_Minimal` · id `e95c42` · 2026-11-19

## Lint conventions: the project's own prefixes (NF_, SIM_, SE_, SEED_, ASU_), SNIP_ snippets and screen-named pages are declared in .claude/lint-config.yaml; no security, quality or performance rule was switched off.

Anchors: `@Shop` · id `071314` · 2026-11-19

## US-121..US-137 live updates: a JavaScript poller clicks each page's hidden refresh container every 2 s (BR-ORD-20: within 5 s); the same hook shows CONNECTION_LOST after two failures.

Anchors: `@Shop.JS_LivePoller`, `@Shop.DS_Shell_Live` · id `2be98e` · 2026-11-19

## US-083..US-094 checkout: field changes recalculate in memory and only explicit actions commit, after quick typing caused optimistic-locking conflicts.

Anchors: `@Shop.SUB_Checkout_Compute`, `@Shop.SUB_Checkout_Recalculate` · id `e77a06` · 2026-11-19

## US-022 carousel: the position lives on the guest's cart, because a list fed by a microflow only refreshes when a persistent context object is committed.

Anchors: `@Shop.SUB_Home_Carousel`, `@Shop.DS_Home_Featured` · id `a1bb79` · 2026-11-19

## US-033 dietary filter chips are built although the prototype lacks them (the story requires them); hidden only in the visual comparison.

Anchors: `@Shop.ACT_Menu_Filter` · id `a6e68d` · 2026-11-19

## US-034 loading state: skeleton cards drawn by CSS on the empty list the client renders while loading.

Anchors: `@Shop.Menu` · id `2bfb84` · 2026-11-19

## US-282 / US-289: the platform's error dialog is replaced by a client hook that opens SCR-41 with an incident id that DS_Error also writes to the server log; an opt-in constant FaultInjection triggers it for the acceptance test.

Anchors: `@Shop.DS_Error`, `@Shop.FaultInjection`, `@Shop.UnexpectedError` · id `5ae203` · 2026-11-19

## US-286 session expiry: the browser remembers the last session id and cart count; a new session after a non-empty cart was lost shows TXT-ERR-20. Session timeout is the Mendix default of 10 minutes (stated in RUN/delivery-notes.md).

Anchors: `@Shop.JS_LivePoller` · id `f52927` · 2026-11-19

## Pages read other modules' data through guarded data-source flows (own cart / own orders / published only) instead of database queries (lint ARCH001); accepted where a page is about one product (ItemInfo) and for the toast list, which has no context object to refresh it.

Anchors: `@Shop.DS_Order_Log`, `@Shop.DS_Product_Recipe`, `@Shop.SNIP_Toasts`, `@Shop.ItemInfo` · id `2d759f` · 2026-11-19

## Page actions: every ACT_ flow only delegates to a SUB_ with the logic (lint CONV010), keeping the permission boundary thin.

Anchors: `@Shop.ACT_Checkout_Place`, `@Shop.SUB_Checkout_Place` · id `c7be68` · 2026-11-19

## US-097 partly met: the checkout map shows the store marker and a destination marker only for an in-zone ZIP, but no distance text (e.g. 2.8 mi) and the destination pin has a fixed position rather than one per zone.

Anchors: `@Shop.Checkout` · id `13ee26` · 2026-11-19

Partly meets requirement `86ff90`: no distance label; fixed destination pin

## Commits deviate from the PRD convention 'US-xxx: <title>' per story: stories that share documents were committed together, with all their ids in the message (Notes: commits list stories built inside another).

Anchors: `@Shop` · id `fad15d` · 2026-11-19

## PRD delivery files not produced yet: RUN/journal.md, RUN/self-assessment.json, RUN/operations.md, RUN/start.ps1 and RUN/stop.ps1 (00-README section 8). RUN/delivery-notes.md exists but lacks the Marketplace module list and the object-name mapping.

Anchors: `@Shop` · id `cb8adb` · 2026-11-19 · OPEN
