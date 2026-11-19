---
milestone: "M1 — Browse and order"
---

# Slice: 04-cart-coupons

<!-- mxcli-brain -->

Requirements for this slice. Anchors point FORWARD, at what the slice
will build — an anchor that does not resolve yet means not built, not
stale. `mxcli brain plan` counts them against the model.

## US-061 Review the cart (MANIFEST.LOCK)

Anchors: `@Shop.ACT_Nav_Cart` · id `96be5c` · 2026-11-19

As a guest, I want to see every item in my cart with its configuration and price, so that I can check my order before paying. (Git Pizza MxDev Lite user story US-061, EP-04.)

## US-062 Empty cart state

Anchors: `@Shop.ACT_Cart_ToMenu` · id `7e7074` · 2026-11-19

As a guest, I want a helpful empty cart, so that I know what to do next. (Git Pizza MxDev Lite user story US-062, EP-04.)

## US-063 Change the quantity of a line

Anchors: `@Shop.ACT_Line_Decrease`, `@Shop.ACT_Line_Increase`, `@Shop.SUB_Line_Decrease`, `@Shop.SUB_Line_Increase` · id `977de4` · 2026-11-19

As a guest, I want to change how many of an item I order, so that I do not have to add it again. (Git Pizza MxDev Lite user story US-063, EP-04.)

## US-064 Remove a line (rm)

Anchors: `@Shop.ACT_Line_Remove`, `@Shop.SUB_Line_Remove` · id `838c34` · 2026-11-19

As a guest, I want to remove an item, so that I only pay for what I want. (Git Pizza MxDev Lite user story US-064, EP-04.)

## US-065 Clear the cart (rm -rf)

Anchors: `@Shop.ACT_Cart_Clear`, `@Shop.SUB_Cart_Clear` · id `8ea340` · 2026-11-19

As a guest, I want to empty the cart in one action, so that I can start over. (Git Pizza MxDev Lite user story US-065, EP-04.)

## US-066 Apply a coupon

Anchors: `@Shop.ACT_Coupon_Apply`, `@Shop.SUB_Coupon_Apply` · id `b76fbc` · 2026-11-19

As a guest, I want to enter a coupon code, so that I get the discount I am entitled to. (Git Pizza MxDev Lite user story US-066, EP-04.)

## US-067 Coupon validation messages

Anchors: `@Fulfilment.SUB_Coupon_Evaluate`, `@Shop.SUB_Coupon_Apply` · id `28aee2` · 2026-11-19

As a guest, I want a precise reason when a coupon does not work, so that I know whether I can fix it. (Git Pizza MxDev Lite user story US-067, EP-04.)

## US-068 Remove or replace the coupon

Anchors: `@Shop.ACT_Coupon_Remove`, `@Shop.SUB_Coupon_Remove` · id `34798b` · 2026-11-19

As a guest, I want to remove a coupon or try another, so that I can use the best one. (Git Pizza MxDev Lite user story US-068, EP-04.)

## US-069 Totals in the cart

Anchors: `@Shop.SUB_Cart_Recalculate`, `@Shop.Cart_Drawer` · id `7f8332` · 2026-11-19

As a guest, I want to see the running totals in the cart, so that I know roughly what I will pay. (Git Pizza MxDev Lite user story US-069, EP-04.)

## US-070 Delivery minimum and free-delivery hints

Anchors: `@Shop.SUB_Cart_Recalculate` · id `a644fe` · 2026-11-19

As a guest, I want to know whether my cart reaches the delivery minimum and free delivery, so that I can adjust it before checkout. (Git Pizza MxDev Lite user story US-070, EP-04.)

## US-071 Unavailable lines in the cart

Anchors: `@Shop.SUB_Cart_Recalculate` · id `01ff8e` · 2026-11-19

As a guest, I want to be told when an item in my cart has become unavailable, so that I can fix my order before paying. (Git Pizza MxDev Lite user story US-071, EP-04.)

## US-072 Cart persistence in the guest session

Anchors: `@Shop.SUB_Cart_Current`, `@Shop.Cart` · id `b95de0` · 2026-11-19

As a guest, I want my cart to survive page reloads and navigation in my browser session, so that I never lose items while I order. (Git Pizza MxDev Lite user story US-072, EP-04.)

## US-073 Proceed to checkout

Anchors: `@Shop.ACT_Cart_Checkout`, `@Shop.SUB_Cart_Recalculate` · id `cd0e26` · 2026-11-19

As a guest, I want to go from the cart to checkout, so that I can place my order. (Git Pizza MxDev Lite user story US-073, EP-04.)
