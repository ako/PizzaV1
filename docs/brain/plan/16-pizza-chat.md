# Slice: 16-pizza-chat

<!-- mxcli-brain -->

Requirements for this slice. Anchors point FORWARD, at what the slice
will build — an anchor that does not resolve yet means not built, not
stale. `mxcli brain plan` counts them against the model.

## A guest can chat with a pizza assistant from a floating chat button on every page; the chat keeps its history while the guest moves between pages

Anchors: `@PizzaChat.SNIP_ChatLauncher`, `@PizzaChat.DS_Chat`, `@PizzaChat.PizzaAssistant` · id `78f7a8` · 2026-11-20

## The assistant searches the menu and explains products, diets and allergens from the catalog, and shows them as product cards with photo, price and an Add to cart button

Anchors: `@PizzaChat.Tool_SearchMenu`, `@PizzaChat.Tool_GetProduct`, `@PizzaChat.REST_GetProducts` · id `f327ab` · 2026-11-20

## The guest builds a cart from the chat: a card's Add to cart button adds the product's default configuration with the cart's own limits, and a cart card shows the live cart with a Checkout button; the assistant itself never changes the cart or pays

Anchors: `@PizzaChat.REST_PostAction`, `@PizzaChat.REST_GetCart`, `@PizzaChat.Tool_GetCart` · id `1dc981` · 2026-11-20

## The assistant checks a ZIP against the delivery zone and shows a map card with the store, the destination and the distance

Anchors: `@PizzaChat.Tool_CheckDelivery`, `@PizzaChat.REST_GetZone` · id `5dbf32` · 2026-11-20

## The assistant tracks the guest's own orders (placed in this session, or found by order number and checkout email with the lookup page's rules) and shows an order card with status, timeline, live map and the tracking link

Anchors: `@PizzaChat.Tool_MyOrders`, `@PizzaChat.Tool_GetOrder`, `@PizzaChat.Tool_FindOrder`, `@PizzaChat.REST_GetOrder` · id `4ea1a0` · 2026-11-20
