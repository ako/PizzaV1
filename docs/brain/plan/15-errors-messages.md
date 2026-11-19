---
milestone: "M4 — Errors and system messages"
---

# Slice: 15-errors-messages

<!-- mxcli-brain -->

Requirements for this slice. Anchors point FORWARD, at what the slice
will build — an anchor that does not resolve yet means not built, not
stale. `mxcli brain plan` counts them against the model.

## US-281 Page not found (404)

Anchors: `@Shop.NotFound` · id `5ef3aa` · 2026-11-19

As any visitor, I want a clear, on-brand page when something does not exist, so that I can get back on track. (Git Pizza MxDev Lite user story US-281, EP-15.)

## US-282 Unexpected error (500)

Anchors: `@Shop.FaultInjection`, `@Shop.JS_RetryLast`, `@Shop.UnexpectedError` · id `c73f47` · 2026-11-19

As any user, I want a calm message and a retry when something breaks, so that I am not stuck. (Git Pizza MxDev Lite user story US-282, EP-15.)

## US-284 Field validation messages

Anchors: `@Shop.ACT_Checkout_Changed` · id `a308a6` · 2026-11-19

As any user filling in a form, I want each error next to the field that caused it, so that I can fix it quickly. (Git Pizza MxDev Lite user story US-284, EP-15.)

## US-285 Conflicting change by someone else

Anchors: `@Shop.ACT_Pay_Retry`, `@Shop.ACT_Track_Rollback`, `@Shop.SUB_Pay_Retry`, `@Shop.SUB_Track_Rollback` · id `db9b58` · 2026-11-19

As a guest, I want to be told when my order changed just before my action (by the simulator or in another browser tab), so that nothing is done twice. (Git Pizza MxDev Lite user story US-285, EP-15.)

## US-286 Session expiry

Anchors: `@Shop.JS_LivePoller` · id `4af807` · 2026-11-19

As a guest, I want to be told when my session expired and my cart was lost, so that I know why the cart is empty and how to find my order again. (Git Pizza MxDev Lite user story US-286, EP-15.)

## US-287 Connection lost or refresh failure

Anchors: `@Shop.JS_LivePoller`, `@Shop.Layout_Guest` · id `21f8a4` · 2026-11-19

As any user of a live screen, I want to know when updates stopped arriving, so that I do not trust stale data. (Git Pizza MxDev Lite user story US-287, EP-15.)

## US-288 Busy states and double-submit protection

Anchors: `@Fulfilment.SUB_Payment_Retry`, `@Shop.SUB_Track_Rollback` · id `58f3c6` · 2026-11-19

As any user, I want buttons to show that they are working and to ignore a second click, so that I never create two orders or two refunds. (Git Pizza MxDev Lite user story US-288, EP-15.)

## US-289 No technical details exposed

Anchors: `@Shop.UnexpectedError`, `@Shop.JS_LivePoller` · id `4200b1` · 2026-11-19

As the owner, I want error texts to stay in the theme and free of internals, so that the app looks professional and does not leak implementation details. (Git Pizza MxDev Lite user story US-289, EP-15.)
