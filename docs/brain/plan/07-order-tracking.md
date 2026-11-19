---
milestone: "M2 — Pay and track"
---

# Slice: 07-order-tracking

<!-- mxcli-brain -->

Requirements for this slice. Anchors point FORWARD, at what the slice
will build — an anchor that does not resolve yet means not built, not
stale. `mxcli brain plan` counts them against the model.

## US-121 Open the tracking page

Anchors: `@Shop.ACT_Track_Token`, `@Shop.SUB_Track_Fill`, `@Shop.SUB_Track_Token` · id `691cee` · 2026-11-19

As a guest, I want to open the tracking page of my order from wherever I am, so that I can follow it at any time. (Git Pizza MxDev Lite user story US-121, EP-07.)

## US-122 Pipeline stepper

Anchors: `@Shop.SNIP_Stepper`, `@Shop.SUB_Track_Fill` · id `697ae4` · 2026-11-19

As a guest, I want to see my order as five pipeline stages, so that I understand at a glance how far it is. (Git Pizza MxDev Lite user story US-122, EP-07.)

## US-123 Live order log (bash — track.log)

Anchors: `@Shop.SNIP_OrderLog`, `@Shop.SUB_Track_Fill` · id `be55aa` · 2026-11-19

As a developer-customer, I want to watch my order's log like a build log, so that the wait is entertaining and transparent. (Git Pizza MxDev Lite user story US-123, EP-07.)

## US-124 Automatic refresh

Anchors: `@Shop.SUB_Track_Fill` · id `dfb800` · 2026-11-19

As a guest, I want the tracking page to update by itself, so that I never have to reload. (Git Pizza MxDev Lite user story US-124, EP-07.)

## US-125 ETA countdown

Anchors: `@Shop.SUB_Track_Fill` · id `2ef681` · 2026-11-19

As a hungry customer, I want a countdown to delivery or pickup, so that I know when to expect my pizza. (Git Pizza MxDev Lite user story US-125, EP-07.)

## US-126 Simulated map with the courier

Anchors: `@Shop.SUB_Track_Fill` · id `503ba6` · 2026-11-19

As a guest, I want to see the courier moving towards me on a map, so that delivery feels real and I can judge the remaining time. (Git Pizza MxDev Lite user story US-126, EP-07.)

## US-127 Courier and oven information

Anchors: `@Shop.SUB_Track_Fill` · id `3353ef` · 2026-11-19

As a guest, I want to know which oven bakes my pizza and which courier brings it, so that the process feels personal. (Git Pizza MxDev Lite user story US-127, EP-07.)

## US-128 Order summary and receipt link

Anchors: `@Shop.ACT_Receipt_Open`, `@Shop.SUB_Track_Fill` · id `152bc8` · 2026-11-19

As a guest, I want to see what I ordered and what I paid on the tracking page, so that I can check it at a glance. (Git Pizza MxDev Lite user story US-128, EP-07.)

## US-129 Roll back (cancel) a queued order

Anchors: `@Shop.ACT_Track_Rollback`, `@Shop.SUB_Track_Fill`, `@Shop.SUB_Track_Rollback` · id `2a87af` · 2026-11-19

As a guest, I want to cancel my order while the kitchen has not started it, so that I can change my mind and get my money back. (Git Pizza MxDev Lite user story US-129, EP-07.)

## US-130 Rollback rejected after baking starts

Anchors: `@Shop.SUB_Track_Fill` · id `55019e` · 2026-11-19

As the store, I want guests not to be able to cancel food that is already being made, so that we do not waste it. (Git Pizza MxDev Lite user story US-130, EP-07.)

## US-131 Cancelled order display

Anchors: `@Shop.SUB_Track_Fill` · id `87d99b` · 2026-11-19

As a guest, I want to understand why my order was cancelled and whether I was refunded, so that I know what happened to my money. (Git Pizza MxDev Lite user story US-131, EP-07.)

## US-132 Pickup tracking

Anchors: `@Shop.SUB_Track_Fill` · id `6547bc` · 2026-11-19

As a guest who chose pickup, I want to know exactly when to come to the store, so that my pizza is hot when I arrive. (Git Pizza MxDev Lite user story US-132, EP-07.)

## US-133 Look up an order by number and email

Anchors: `@Shop.ACT_Lookup`, `@Shop.LookupForm`, `@Shop.SUB_Lookup`, `@Shop.SUB_Track_Fill`, `@Shop.TrackLookup` · id `bf71ba` · 2026-11-19

As a guest who lost the tracking link, I want to find my order with its number and my email, so that I can still track it. (Git Pizza MxDev Lite user story US-133, EP-07.)

## US-134 Invalid tracking link

Anchors: `@Shop.ACT_Track_Token`, `@Shop.SUB_Track_Fill`, `@Shop.SUB_Track_Token`, `@Shop.TrackInvalid` · id `d58a51` · 2026-11-19

As a guest with a broken or outdated link, I want a clear message and a way forward, so that I am not left on an empty page. (Git Pizza MxDev Lite user story US-134, EP-07.)

## US-135 ./track.log navigation target

Anchors: `@Shop.ACT_Nav_Track`, `@Shop.SUB_Nav_Track`, `@Shop.SUB_Track_Fill` · id `bf9414` · 2026-11-19

As a guest, I want the "track" navigation item to take me straight to the most relevant order, so that I need no extra clicks. (Git Pizza MxDev Lite user story US-135, EP-07.)

## US-136 Lookup abuse protection

Anchors: `@Shop.ACT_Lookup`, `@Shop.LookupAttempt`, `@Shop.SUB_Lookup`, `@Shop.SUB_Track_Fill` · id `714236` · 2026-11-19

As the store, I want repeated failed lookups to be slowed down, so that nobody can guess other people's orders. (Git Pizza MxDev Lite user story US-136, EP-07.)

## US-137 Completed order view

Anchors: `@Shop.SUB_Track_Fill` · id `01e571` · 2026-11-19

As a guest whose pizza arrived, I want the tracking page to confirm completion and offer the receipt, so that the journey ends cleanly. (Git Pizza MxDev Lite user story US-137, EP-07.)
