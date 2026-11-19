---
milestone: "M1 — Browse and order"
---

# Slice: 05-checkout

<!-- mxcli-brain -->

Requirements for this slice. Anchors point FORWARD, at what the slice
will build — an anchor that does not resolve yet means not built, not
stale. `mxcli brain plan` counts them against the model.

## US-081 Choose delivery or pickup

Anchors: `@Shop.ACT_Checkout_Type`, `@Shop.SUB_Checkout_Type` · id `53e40b` · 2026-11-19

As a guest, I want to choose delivery or pickup, so that I get my pizza the way that suits me. (Git Pizza MxDev Lite user story US-081, EP-05.)

## US-082 Enter a delivery address (.env variables)

Anchors: `@Shop.Checkout`, `@Shop.SUB_Checkout_Compute` · id `4ec814` · 2026-11-19

As a guest, I want to enter my delivery address in clear fields, so that the courier finds me. (Git Pizza MxDev Lite user story US-082, EP-05.)

## US-083 Delivery-zone check

Anchors: `@Shop.ACT_Checkout_Pickup`, `@Shop.SUB_Checkout_Compute`, `@Shop.SUB_Checkout_Pickup` · id `c14a4f` · 2026-11-19

As a guest, I want to know immediately whether the store delivers to my ZIP code, so that I do not complete a form for nothing. (Git Pizza MxDev Lite user story US-083, EP-05.)

## US-085 Contact details

Anchors: `@Shop.Checkout`, `@Core.SUB_FormatPhone` · id `40e006` · 2026-11-19

As a guest, I want to give my name, email and phone, so that the store and courier can reach me and I can look up my order later. (Git Pizza MxDev Lite user story US-085, EP-05.)

## US-086 Courier tip

Anchors: `@Shop.ACT_Checkout_Tip`, `@Shop.SUB_Checkout_Compute`, `@Shop.SUB_Checkout_Tip` · id `509ab6` · 2026-11-19

As a guest ordering delivery, I want to add a tip for the courier, so that I can reward good service. (Git Pizza MxDev Lite user story US-086, EP-05.)

## US-087 Order summary and total

Anchors: `@Shop.SUB_Checkout_Compute` · id `955b2d` · 2026-11-19

As a guest, I want to see a complete breakdown of what I will pay before I place the order, so that there are no surprises. (Git Pizza MxDev Lite user story US-087, EP-05.)

## US-088 Delivery fee

Anchors: `@Shop.SUB_Checkout_Compute` · id `405be3` · 2026-11-19

As a guest, I want to see when delivery is free and why, so that I can decide whether to add more or use a coupon. (Git Pizza MxDev Lite user story US-088, EP-05.)

## US-089 Minimum delivery order

Anchors: `@Shop.SUB_Checkout_Compute` · id `a3d93b` · 2026-11-19

As the store, I want delivery orders to reach a minimum subtotal, so that small orders are picked up instead. (Git Pizza MxDev Lite user story US-089, EP-05.)

## US-091 Place the order (Execute Order --force)

Anchors: `@Shop.ACT_Checkout_Place`, `@Shop.SUB_Checkout_Place` · id `e7a74e` · 2026-11-19

As a guest, I want to place the order with one button once everything is valid, so that the kitchen starts as soon as my payment is through. (Git Pizza MxDev Lite user story US-091, EP-05.)

## US-092 Empty-cart redirect

Anchors: `@Shop.Checkout`, `@Shop.CheckoutForm.IsEmptyCart` · id `926382` · 2026-11-19

As a guest, I want to be sent back to the menu if I open checkout with an empty cart, so that I never see a broken checkout. (Git Pizza MxDev Lite user story US-092, EP-05.)

## US-093 Pickup details

Anchors: `@Shop.SUB_Checkout_Compute` · id `fb616b` · 2026-11-19

As a guest ordering pickup, I want to see where and roughly when I can collect my order, so that I can plan my walk to the store. (Git Pizza MxDev Lite user story US-093, EP-05.)

## US-094 Coupon re-check for the order type

Anchors: `@Shop.SUB_Checkout_Compute` · id `fb1dee` · 2026-11-19

As a guest, I want the coupon to be checked again when I choose delivery or pickup, so that I see the real discount before paying. (Git Pizza MxDev Lite user story US-094, EP-05.)

## US-095 Item became unavailable during checkout

Anchors: `@Shop.SUB_Checkout_Place`, `@Shop.SUB_Line_Recalculate` · id `34df5f` · 2026-11-19

As a guest, I want to be told if something in my order sold out while I was checking out, so that I am not charged for food the kitchen cannot make. (Git Pizza MxDev Lite user story US-095, EP-05.)

## US-097 Delivery preview map

Anchors: `@Shop.Checkout`, `@Fulfilment.DeliveryZone` · id `86ff90` · 2026-11-19

As a guest, I want a small map preview of the route from the store to my ZIP code, so that I feel the delivery is real. (Git Pizza MxDev Lite user story US-097, EP-05.)
