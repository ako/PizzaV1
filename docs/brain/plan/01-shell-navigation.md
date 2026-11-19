---
milestone: "M1 — Browse and order"
---

# Slice: 01-shell-navigation

<!-- mxcli-brain -->

Requirements for this slice. Anchors point FORWARD, at what the slice
will build — an anchor that does not resolve yet means not built, not
stale. `mxcli brain plan` counts them against the model.

## US-001 Customer header and main navigation

Anchors: `@Shop.ACT_Nav_Checkout`, `@Shop.ACT_Nav_Search`, `@Shop.SNIP_Header`, `@Shop.SUB_Nav_Search` · id `7121c4` · 2026-11-19

As a guest, I want a persistent header with the main navigation, search and the cart button, so that I can reach every part of the shop from any page. (Git Pizza MxDev Lite user story US-001, EP-01.)

## US-002 Project Explorer sidebar (desktop)

Anchors: `@Shop.SNIP_Sidebar` · id `2b28e2` · 2026-11-19

As a guest on a desktop screen, I want an IDE-style file explorer on the left, so that I can jump to categories and my active order like files in a project. (Git Pizza MxDev Lite user story US-002, EP-01.)

## US-003 Phone bottom tab bar

Anchors: `@Shop.SNIP_BottomNav` · id `1aa7f8` · 2026-11-19

As a guest on a phone, I want a bottom tab bar, so that the main areas are reachable with my thumb. (Git Pizza MxDev Lite user story US-003, EP-01.)

## US-004 DEMO MODE banner

Anchors: `@Shop.SNIP_DemoBanner` · id `b0bd16` · 2026-11-19

As any visitor, I want to be told on every screen that this is a demo with simulated payment, kitchen and delivery, so that I never mistake it for a real shop. (Git Pizza MxDev Lite user story US-004, EP-01.)

## US-006 Official brand and logo only

Anchors: `@Shop.SNIP_Header`, `@Shop.Layout_Guest` · id `9f79cb` · 2026-11-19

As the owner, I want the app to use only the Git Pizza MxDev name and official logo, so that every contractor's result carries the same, correct brand. (Git Pizza MxDev Lite user story US-006, EP-01.)

## US-007 Storefront footer

Anchors: `@Shop.SNIP_Footer` · id `183b6e` · 2026-11-19

As a guest, I want a footer with the store's details and the allergen notice, so that I know who I am ordering from. (Git Pizza MxDev Lite user story US-007, EP-01.)

## US-010 Toast notifications

Anchors: `@Core.SUB_Toast`, `@Core.Toast`, `@Shop.SNIP_Toasts` · id `0a96ea` · 2026-11-19

As any user, I want short confirmations and error notices that do not block my work, so that I know my action worked or why it did not. (Git Pizza MxDev Lite user story US-010, EP-01.)

## US-011 Responsive layout switch

Anchors: `@Shop.Layout_Guest`, `@Shop.SNIP_BottomNav` · id `2c42ba` · 2026-11-19

As any user, I want the app to work at phone, tablet and desktop widths, so that I can use it on any device. (Git Pizza MxDev Lite user story US-011, EP-01.)

## US-012 Dev labels with plain meaning

Anchors: `@Fulfilment.OrderStatus`, `@Shop.SUB_Track_Fill` · id `f8b2d5` · 2026-11-19

As a visitor who is not a developer, I want every developer label to also tell me its plain meaning, so that I can use the shop without knowing git or CI/CD. (Git Pizza MxDev Lite user story US-012, EP-01.)
