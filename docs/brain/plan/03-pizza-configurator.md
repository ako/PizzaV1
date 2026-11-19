---
milestone: "M1 — Browse and order"
---

# Slice: 03-pizza-configurator

<!-- mxcli-brain -->

Requirements for this slice. Anchors point FORWARD, at what the slice
will build — an anchor that does not resolve yet means not built, not
stale. `mxcli brain plan` counts them against the model.

## US-041 Open the configurator with the default configuration

Anchors: `@Shop.ACT_Configure_Open`, `@Shop.SUB_Configure_Open` · id `957b93` · 2026-11-19

As a guest, I want the configurator to open with the pizza exactly as listed on the menu, so that I only change what I care about. (Git Pizza MxDev Lite user story US-041, EP-03.)

## US-042 Choose the size (scale_factor)

Anchors: `@Shop.ACT_Config_Choose`, `@Shop.SUB_Config_Choose` · id `5e6184` · 2026-11-19

As a guest, I want to choose Small, Medium or Large, so that the pizza fits my appetite and the price updates at once. (Git Pizza MxDev Lite user story US-042, EP-03.)

## US-043 Choose the crust (core_kernel)

Anchors: `@Shop.ACT_Config_Choose`, `@Shop.SUB_Config_Choose` · id `bceb73` · 2026-11-19

As a guest, I want to choose the crust, including gluten-free and stuffed options, so that the base suits my taste or diet. (Git Pizza MxDev Lite user story US-043, EP-03.)

## US-044 Choose sauce and cheese (base_layer, cheese_driver)

Anchors: `@Shop.ACT_Config_Choose`, `@Shop.SUB_Config_Choose` · id `98f196` · 2026-11-19

As a guest, I want to change the sauce and the cheese, so that I can make a white pizza, a vegan pizza or a richer one. (Git Pizza MxDev Lite user story US-044, EP-03.)

## US-045 Add extra toppings (inject dependencies)

Anchors: `@Shop.ACT_Config_Choose`, `@Shop.SUB_Config_Choose` · id `90abe1` · 2026-11-19

As a guest, I want to add extra toppings up to the allowed number, so that I can build the pizza I want. (Git Pizza MxDev Lite user story US-045, EP-03.)

## US-046 Remove default ingredients (unlink)

Anchors: `@Shop.ACT_Config_Choose`, `@Shop.SUB_Config_Choose` · id `98868a` · 2026-11-19

As a guest, I want to remove ingredients I do not like, for free, so that the pizza is made the way I want. (Git Pizza MxDev Lite user story US-046, EP-03.)

## US-047 Live allergens and diet flags

Anchors: `@Shop.SUB_Line_Recalculate`, `@Shop.DS_Line_Allergens` · id `459b76` · 2026-11-19

As a guest with dietary needs, I want allergens and vegetarian/vegan flags to update with every change, so that I know exactly what I am ordering. (Git Pizza MxDev Lite user story US-047, EP-03.)

## US-048 Live manifest.json preview

Anchors: `@Shop.Configurator`, `@Shop.SUB_Line_Recalculate` · id `0fde4e` · 2026-11-19

As a developer-customer, I want to see my pizza as a live JSON manifest, so that the configuration feels like writing code and I can double-check every choice. (Git Pizza MxDev Lite user story US-048, EP-03.)

## US-049 Set quantity and add to cart (Build & Deploy)

Anchors: `@Shop.ACT_Config_Commit`, `@Shop.ACT_Config_Qty`, `@Shop.SUB_Config_Commit`, `@Shop.SUB_Config_Qty`, `@Shop.SUB_Config_Return` · id `596e9a` · 2026-11-19

As a guest, I want to add my configured pizza to the cart in the quantity I need, so that I can continue ordering. (Git Pizza MxDev Lite user story US-049, EP-03.)

## US-050 Edit a cart line in the configurator

Anchors: `@Shop.ACT_Cart_Edit`, `@Shop.ACT_Config_Back`, `@Shop.ACT_Config_Commit`, `@Shop.ACT_Configure_Edit`, `@Shop.SUB_Config_Back`, `@Shop.SUB_Config_Commit`, `@Shop.SUB_Configure_Edit` · id `629dee` · 2026-11-19

As a guest, I want to change a pizza that is already in my cart, so that I do not have to delete and rebuild it. (Git Pizza MxDev Lite user story US-050, EP-03.)

## US-051 Unavailable options and ingredients

Anchors: `@Shop.ACT_Config_Choose`, `@Shop.SUB_Config_Choose` · id `fe99a6` · 2026-11-19

As a guest, I want unavailable options to be visibly disabled, so that I never configure something the kitchen cannot make today. (Git Pizza MxDev Lite user story US-051, EP-03.)

## US-052 Price breakdown

Anchors: `@Shop.DS_Config_Choices` · id `4a26bb` · 2026-11-19

As a price-conscious customer, I want to see how the unit price is made up, so that I understand every surcharge. (Git Pizza MxDev Lite user story US-052, EP-03.)

## US-053 Phone layout with sticky price bar

Anchors: `@Shop.Configurator` · id `c62548` · 2026-11-19

As a guest on a phone, I want the price and the add button always in reach while I scroll through the options, so that I can finish quickly. (Git Pizza MxDev Lite user story US-053, EP-03.)
