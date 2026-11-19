---
milestone: "M2 — Pay and track"
---

# Slice: 06-simulated-payment

<!-- mxcli-brain -->

Requirements for this slice. Anchors point FORWARD, at what the slice
will build — an anchor that does not resolve yet means not built, not
stale. `mxcli brain plan` counts them against the model.

## US-101 Choose a payment method and demo test card

Anchors: `@Shop.ACT_Checkout_Pay`, `@Shop.SNIP_PaymentChoice`, `@Shop.SUB_Checkout_Pay` · id `674aab` · 2026-11-19

As a guest, I want to choose how I pay — and, in this demo, which outcome I want to see — without typing any card data, so that I can try success and failure safely. (Git Pizza MxDev Lite user story US-101, EP-06.)

## US-102 Payment processing sheet

Anchors: `@Shop.PaymentSheet`, `@Shop.SUB_Track_Fill` · id `97ac05` · 2026-11-19

As a guest, I want to see that my payment is being processed, so that I wait instead of pressing the button again. (Git Pizza MxDev Lite user story US-102, EP-06.)

## US-103 Successful payment

Anchors: `@Shop.ACT_Pay_Refresh`, `@Shop.PaymentSheet`, `@Shop.SUB_Pay_Refresh`, `@Shop.SUB_Track_Fill` · id `f635a6` · 2026-11-19

As a guest, I want a successful payment to send my order straight to the kitchen, so that baking starts right away. (Git Pizza MxDev Lite user story US-103, EP-06.)

## US-104 Declined card or insufficient funds

Anchors: `@Shop.PaymentSheet`, `@Shop.SUB_Track_Fill` · id `ce323d` · 2026-11-19

As a guest, I want a clear reason when my payment fails, so that I can pick another way to pay. (Git Pizza MxDev Lite user story US-104, EP-06.)

## US-105 Gateway timeout

Anchors: `@Shop.PaymentSheet`, `@Shop.SUB_Track_Fill` · id `49311b` · 2026-11-19

As a demo viewer, I want to see what happens when the payment gateway does not answer, so that the demo shows a realistic technical failure. (Git Pizza MxDev Lite user story US-105, EP-06.)

## US-106 Retry payment with another method

Anchors: `@Shop.ACT_Pay_Retry`, `@Shop.PaymentSheet`, `@Shop.SUB_Pay_Retry`, `@Shop.SUB_Track_Fill` · id `ff52e1` · 2026-11-19

As a guest whose payment failed, I want to retry with another card or wallet, so that I can still get my pizza. (Git Pizza MxDev Lite user story US-106, EP-06.)

## US-107 Third failure rolls the order back

Anchors: `@Shop.ACT_Pay_ToCart`, `@Shop.PaymentSheet`, `@Shop.SUB_Track_Fill` · id `a7fee5` · 2026-11-19

As the store, I want an order to be rolled back after three failed payments, so that unpaid orders do not pile up. (Git Pizza MxDev Lite user story US-107, EP-06.)

## US-108 Cancel the order before payment

Anchors: `@Shop.ACT_Pay_Cancel`, `@Shop.ACT_Pay_CancelAndCart`, `@Shop.PaymentSheet`, `@Shop.SUB_Pay_Cancel`, `@Shop.SUB_Track_Fill` · id `72aded` · 2026-11-19

As a guest whose payment failed, I want to cancel the order, so that I can change my cart or stop. (Git Pizza MxDev Lite user story US-108, EP-06.)

## US-109 Abandoned failed payment expires

Anchors: `@Shop.SUB_Track_Fill` · id `ff6670` · 2026-11-19

As the store, I want a failed payment that nobody retries to expire, so that the order list stays clean. (Git Pizza MxDev Lite user story US-109, EP-06.)

## US-110 Order confirmation (DEPLOYMENT SUCCESSFUL // 200 OK)

Anchors: `@Shop.AppUrl`, `@Shop.Confirmation`, `@Shop.JS_CopyText`, `@Shop.NF_CopyHash`, `@Shop.NF_CopyLink`, `@Shop.SUB_Track_Fill` · id `329f49` · 2026-11-19

As a guest, I want a satisfying confirmation with my order reference and ETA, so that I know the order is in and how to follow it. (Git Pizza MxDev Lite user story US-110, EP-06.)

## US-111 Simulated refund on cancellation

Anchors: `@Fulfilment.SUB_Order_Refund` · id `5b0193` · 2026-11-19

As a guest whose paid order was cancelled, I want to see that my money was refunded, so that I trust the shop. (Git Pizza MxDev Lite user story US-111, EP-06.)

## US-112 Random payment failure rate

Anchors: `@Simulation.SIM_Payments`, `@Shop.SUB_Payment_Resolve` · id `afaea9` · 2026-11-19

As the simulator, I want the outcome of a payment to depend only on the chosen test card, so that every run of the demo and of the acceptance tests gives the same result. (Git Pizza MxDev Lite user story US-112, EP-06.)

## US-113 Retry or cancel from the tracking page

Anchors: `@Shop.ACT_Pay_Retry`, `@Shop.ACT_Track_RetryOpen`, `@Shop.SUB_Pay_Retry` · id `70fb35` · 2026-11-19

As a guest who closed the payment sheet, I want to finish or cancel a failed payment from the tracking page, so that I am never stuck. (Git Pizza MxDev Lite user story US-113, EP-06.)

## US-114 Simulated customers pay through the same gateway

Anchors: `@Simulation.SIM_Payments`, `@Simulation.SUB_Traffic_Spawn` · id `bdcc79` · 2026-11-19

As a guest watching the demo, I want simulated orders to go through the same payment simulation as mine, so that the kitchen queue, the couriers and the home page KPIs show realistic activity. (Git Pizza MxDev Lite user story US-114, EP-06.)
