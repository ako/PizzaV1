---
milestone: "M1 — Browse and order"
---

# Slice: 02-menu-browsing

<!-- mxcli-brain -->

Requirements for this slice. Anchors point FORWARD, at what the slice
will build — an anchor that does not resolve yet means not built, not
stale. `mxcli brain plan` counts them against the model.

## US-021 Home hero and terminal intro

Anchors: `@Shop.Home`, `@Shop.DS_Home` · id `9e9b0c` · 2026-11-19

As a first-time guest, I want a striking landing page that explains the concept in one look, so that I understand what Git Pizza MxDev is and start ordering. (Git Pizza MxDev Lite user story US-021, EP-02.)

## US-022 Featured modules carousel

Anchors: `@Shop.DS_Home_Featured`, `@Shop.SNIP_FeaturedCard` · id `d232c9` · 2026-11-19

As a guest, I want to see the house favorites on the home page, so that I can pick a great pizza without browsing the whole menu. (Git Pizza MxDev Lite user story US-022, EP-02.)

## US-023 Live demo KPIs on the home page

Anchors: `@Shop.ACT_Home_Refresh`, `@Shop.SUB_Home_Refresh` · id `94fa95` · 2026-11-19

As a visitor watching the demo, I want a few live numbers about today's operation on the home page, so that I can see the simulated business is running. (Git Pizza MxDev Lite user story US-023, EP-02.)

## US-024 Live build status of my active order on the home page

Anchors: `@Shop.DS_Home_Active`, `@Shop.SNIP_HomeActiveOrder`, `@Shop.SUB_Track_Fill` · id `2c3985` · 2026-11-19

As a guest with an order in progress, I want to see its pipeline on the home page, so that I know its state without opening the tracking page. (Git Pizza MxDev Lite user story US-024, EP-02.)

## US-025 Category tabs and product cards

Anchors: `@Shop.ACT_Menu_Tab`, `@Shop.DS_Menu_Products`, `@Shop.SNIP_MenuCard`, `@Shop.SUB_Menu_Refresh`, `@Shop.SUB_Menu_Tab` · id `2c9ed9` · 2026-11-19

As a guest, I want to browse the menu by category with clear, appetizing cards, so that I can compare items and prices quickly. (Git Pizza MxDev Lite user story US-025, EP-02.)

## US-026 Ingredients shown as a code block

Anchors: `@Shop.DS_Product_Allergens`, `@Shop.DS_Product_Recipe`, `@Shop.SNIP_CodeBlock` · id `a16588` · 2026-11-19

As a developer-customer, I want each pizza's ingredients written as a small code snippet, so that the menu speaks my language while staying readable. (Git Pizza MxDev Lite user story US-026, EP-02.)

## US-027 Menu search (grep)

Anchors: `@Shop.ACT_Menu_ClearSearch`, `@Shop.ACT_Menu_Search`, `@Shop.ACT_Nav_Search`, `@Shop.SUB_Menu_ClearSearch`, `@Shop.SUB_Menu_Refresh`, `@Shop.SUB_Menu_Search`, `@Shop.SUB_Nav_Search`, `@Shop.SUB_Product_Recalculate` · id `0c432b` · 2026-11-19

As a guest, I want to search the whole menu by name, dish or ingredient, so that I find what I am craving fast. (Git Pizza MxDev Lite user story US-027, EP-02.)

## US-028 Quick add (+ import)

Anchors: `@Shop.ACT_Product_Add`, `@Shop.ACT_Product_QuickAdd`, `@Shop.SUB_Product_Add` · id `2fd490` · 2026-11-19

As a guest, I want to add an item with its default configuration in one click, so that ordering a favorite is fast. (Git Pizza MxDev Lite user story US-028, EP-02.)

## US-029 Item info for sides, drinks and desserts

Anchors: `@Shop.ACT_Info_Add`, `@Shop.ACT_Product_Add`, `@Shop.ACT_Product_Info`, `@Shop.DS_Info_Line`, `@Shop.ItemInfo`, `@Shop.SUB_Info_Add`, `@Shop.SUB_Product_Add` · id `94d068` · 2026-11-19

As a guest, I want to open the details of a side, drink or dessert, so that I can read its description, serving, allergens and calories before adding it. (Git Pizza MxDev Lite user story US-029, EP-02.)

## US-030 Allergen and nutrition info for pizzas

Anchors: `@Shop.ACT_Product_Info`, `@Shop.ItemInfo` · id `21e00f` · 2026-11-19

As a guest with a food allergy, I want to see a pizza's allergens, diet flags and calories before configuring it, so that I can choose safely. (Git Pizza MxDev Lite user story US-030, EP-02.)

## US-031 Sold-out products

Anchors: `@Catalog.Product.IsSoldOut`, `@Shop.SNIP_MenuCard` · id `d01be4` · 2026-11-19

As a guest, I want to see which items are sold out today, so that I do not try to order something the kitchen cannot make. (Git Pizza MxDev Lite user story US-031, EP-02.)

## US-032 Terminal Debugger cart panel (desktop menu)

Anchors: `@Shop.ACT_Menu_Refresh`, `@Shop.SUB_Menu_Refresh_Do` · id `bd9c55` · 2026-11-19

As a guest on desktop, I want a live cart summary next to the menu, so that I see what I have added without opening the cart. (Git Pizza MxDev Lite user story US-032, EP-02.)

## US-033 Dietary quick filter

Anchors: `@Shop.ACT_Menu_Filter`, `@Shop.SUB_Menu_Filter`, `@Shop.SUB_Menu_Refresh` · id `dcc2ac` · 2026-11-19

As a vegetarian or vegan guest, I want to filter the menu by diet, so that I only see items I can eat. (Git Pizza MxDev Lite user story US-033, EP-02.)

## US-034 Menu loading state

Anchors: `@Shop.Menu` · id `9ade69` · 2026-11-19

As a guest on a slow connection, I want to see that the menu is loading, so that I do not think the page is broken. (Git Pizza MxDev Lite user story US-034, EP-02.)
