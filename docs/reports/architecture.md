# Architecture

Module layers, coupling, bounded contexts and cycles · GitPizza · generated 2026-11-19 12:36 · mxcli nightly-20261118-9d764483c

| | |
|---|---|
| app modules | 5 — 8 outside |
| layers | 4 |
| domain cycles | 0 — 0 modules; 0 with navigation counted |
| clusters | 10 |
| unused documents | 3 — 0 to verify |

## Layered module map

Each app module on the layer its domain dependencies put it on: arrows point from a module to what it uses, thicker for more references. Red dashed arrows close a cycle. Fill shows cohesion.

Layer 3: Simulation  
Layer 2: Shop  
Layer 1: Fulfilment  
Layer 0: Catalog, Core

## Module health

Purpose is the module's documentation (`alter module <Name> set documentation '…'`). Low cohesion is flagged only where nothing explains it. A shell, an admin UI or an adapter is low-cohesion by design; annotate `module:<Name>` to explain another.

| Module | Purpose | Layer | Documents | Internal refs | Outbound | Inbound | Cohesion | Fan-in | Fan-out | Role / note |
|---|---|---|---|---|---|---|---|---|---|---|
| Simulation | Demo simulation: clock, kitchen, ovens, couriers, payments, traffic and the daily demo reset (SIM-01 … SIM-08). | 3 | 211 | 286 | 10021 | 0 | 3% | 0 | 4 |  |
| Shop | Git Pizza MxDev guest ordering: catalog, cart, checkout, simulated payment, order tracking and the system pages. | 2 | 195 | 1270 | 834 | 16 | 60% | 1 | 3 |  |
| Fulfilment | The order domain without UI: orders and their lines, payments, status history and log, couriers, ovens, delivery zones, coupons, pricing and the order transitions. | 1 | 43 | 268 | 10 | 9257 | 96% | 2 | 2 |  |
| Catalog | Product catalog: pizzas, sides, drinks and desserts with sizes, options, recipes, ingredients and allergens (the menu's data). | 0 | 17 | 66 | 0 | 1313 | 100% | 3 | 0 |  |
| Core | Shared foundation: store and simulation settings, guest toasts, and the money, time, phone and id helpers every module uses. | 0 | 11 | 19 | 1 | 271 | 95% | 3 | 0 |  |

## Coupling matrix (domain)

Rows use columns. Modules are in layer order, highest first, so a layered design is a triangle above the diagonal; a filled cell below it is a dependency upward — part of a cycle.

| uses → | Simulation | Shop | Fulfilment | Catalog | Core |
|---|---|---|---|---|---|
| Simulation |  | 16 | 8823 | 1038 | 141 |
| Shop |  |  | 434 | 272 | 125 |
| Fulfilment |  |  |  | 3 | 5 |
| Catalog |  |  |  |  |  |
| Core |  |  |  |  |  |

## Navigation dependencies

Menus, layouts and page links between app modules. Counted as dependencies they put 0 modules in cycles; that is how screens are wired, not how the domain is layered.

_(none)_

## Cycles

Each cycle with the exact edges that close it. A cycle is real when both directions carry domain meaning; it is accidental when one direction is a helper that belongs on the other side.

No domain cycles between app modules.

## Bounded contexts

Clusters of tightly connected documents, against the modules they come from. A module spread over several clusters may hold more than one context; a cluster spanning modules may be one context split across them.

| Cluster | Key | Size | Simulation | Shop | Fulfilment | Catalog | Core | Note |
|---|---|---|---|---|---|---|---|---|
| Shop · CartLine | `cluster:Shop.CartLine` | 90 | 1 | 75 |  | 11 | 3 | label derived — name it |
| Simulation · Order | `cluster:Fulfilment.Order` | 86 | 55 | 10 | 19 |  | 2 | label derived — name it |
| Simulation · Product | `cluster:Catalog.Product` | 61 | 46 | 9 | 5 | 1 |  | label derived — name it |
| Shop · Cart | `cluster:Shop.Cart` | 52 |  | 46 | 3 |  | 3 | label derived — name it |
| Simulation · OrderStatusChange | `cluster:Fulfilment.OrderStatusChange` | 52 | 46 | 2 | 4 |  |  | label derived — name it |
| Simulation · OrderLogEntry | `cluster:Fulfilment.OrderLogEntry` | 49 | 46 | 1 | 2 |  |  | label derived — name it |
| Shop · TrackView | `cluster:Shop.TrackView` | 47 | 7 | 34 | 4 |  | 2 | label derived — name it |
| Catalog | `cluster:Catalog.Option` | 21 | 4 | 6 | 2 | 8 | 1 |  |
| Shop · SE_DailyReset | `cluster:Simulation.SE_DailyReset` | 4 | 2 | 2 |  |  |  | label derived — name it |
| Shop · ErrorView | `cluster:Shop.ErrorView` | 3 |  | 3 |  |  |  | label derived — name it |

Modules that may hold more than one context:

- `Simulation` has at least a fifth of its clustered documents in each of 4 clusters
- `Shop` has at least a fifth of its clustered documents in each of 2 clusters
- `Catalog` has at least a fifth of its clustered documents in each of 2 clusters
- `Core` has at least a fifth of its clustered documents in each of 2 clusters

3 cluster(s) of fewer than three documents not shown.

## God nodes, bridges and entity hotspots

God nodes are what the most references hang on; bridges sit on the most shortest paths between other elements (betweenness) and are where a split would cut; hotspots are entities used by the most flows.

**God nodes**

| Element | Type | Module | In | Out | Betweenness |
|---|---|---|---|---|---|
| `Fulfilment.OrderLogEntry` | ENTITY | Fulfilment | 962 | 7 | 0.0 |
| `Simulation.SEED_Catalog` | MICROFLOW | Simulation | 1 | 837 | 6.0 |
| `Fulfilment.OrderStatusChange` | ENTITY | Fulfilment | 502 | 7 | 0.0 |
| `Fulfilment.Order` | ENTITY | Fulfilment | 430 | 10 | 0.0 |
| `Fulfilment.OrderLineModifier` | ENTITY | Fulfilment | 383 | 8 | 0.0 |
| `Catalog.Product` | ENTITY | Catalog | 255 | 5 | 0.0 |
| `Fulfilment.OrderLine` | ENTITY | Fulfilment | 246 | 7 | 0.0 |
| `Catalog.Option` | ENTITY | Catalog | 141 | 3 | 0.0 |
| `Catalog.Ingredient` | ENTITY | Catalog | 133 | 9 | 0.0 |
| `Shop.SUB_Track_Fill` | MICROFLOW | Shop | 9 | 128 | 155.7 |
| `Fulfilment.PaymentAttempt` | ENTITY | Fulfilment | 125 | 9 | 0.0 |
| `Catalog.RecipeItem` | ENTITY | Catalog | 113 | 5 | 0.0 |
| `Shop.CartLine` | ENTITY | Shop | 112 | 3 | 0.0 |
| `Catalog.ProductSize` | ENTITY | Catalog | 100 | 5 | 0.0 |
| `Shop.DS_Config_Choices` | MICROFLOW | Shop | 1 | 87 | 0.0 |

**Bridges**

| Element | Type | Module | In | Out | Betweenness |
|---|---|---|---|---|---|
| `Shop.SUB_Line_Recalculate` | MICROFLOW | Shop | 12 | 62 | 1110.6 |
| `Shop.SUB_Cart_Recalculate` | MICROFLOW | Shop | 13 | 47 | 952.5 |
| `Simulation.SEED_Orders` | MICROFLOW | Simulation | 1 | 46 | 571.9 |
| `Simulation.SUB_Reset` | MICROFLOW | Simulation | 3 | 62 | 473.9 |
| `Shop.SUB_Checkout_Recalculate` | MICROFLOW | Shop | 5 | 5 | 297.0 |
| `Simulation.SIM_Tick` | MICROFLOW | Simulation | 1 | 10 | 262.1 |
| `Simulation.SUB_Traffic_Spawn` | MICROFLOW | Simulation | 1 | 49 | 193.2 |
| `Simulation.SIM_ClockRun` | MICROFLOW | Simulation | 4 | 3 | 190.1 |
| `Shop.ACT_Nav_Cart` | MICROFLOW | Shop | 10 | 3 | 175.0 |
| `Shop.SUB_Track_Fill` | MICROFLOW | Shop | 9 | 128 | 155.7 |
| `Simulation.SIM_Traffic` | MICROFLOW | Simulation | 1 | 12 | 152.2 |
| `Shop.SUB_Product_Add` | MICROFLOW | Shop | 1 | 12 | 148.0 |
| `Shop.SUB_Order_Place` | MICROFLOW | Shop | 2 | 85 | 141.2 |
| `Shop.SUB_Cart_AddLine` | MICROFLOW | Shop | 2 | 37 | 122.2 |
| `Fulfilment.SUB_Price_Compute` | MICROFLOW | Fulfilment | 3 | 27 | 115.0 |

**Entity hotspots**

| Entity | Used by flows | From modules |
|---|---|---|
| `Fulfilment.Order` | 223 | Fulfilment,Simulation,Shop |
| `Catalog.Product` | 68 | Shop,Simulation |
| `Fulfilment.PaymentAttempt` | 55 | Fulfilment,Shop,Simulation |
| `Fulfilment.OrderLine` | 51 | Shop,Simulation |
| `Fulfilment.OrderLineModifier` | 48 | Shop,Simulation |
| `Fulfilment.OrderLogEntry` | 48 | Fulfilment,Simulation,Shop |
| `Fulfilment.OrderStatusChange` | 48 | Fulfilment,Simulation,Shop |
| `Fulfilment.Oven` | 41 | Simulation,Shop |
| `Fulfilment.DeliveryZone` | 37 | Simulation,Shop |
| `Shop.CartLine` | 37 | Shop,Simulation |
| `Shop.Cart` | 33 | Shop,Simulation |
| `Fulfilment.Courier` | 28 | Simulation,Shop |
| `Shop.TrackView` | 18 | Shop |
| `Shop.CheckoutForm` | 16 | Shop,Simulation |
| `Shop.MenuView` | 14 | Shop |

## Outside the app

References between app modules and Marketplace or platform modules. These are dependencies to keep upgradeable, not part of the app's layering.

| From | To | References | Kinds |
|---|---|---|---|
| Shop | System | 3 | associate |
| Simulation | System | 3 | member, retrieve |
| Fulfilment | System | 2 | associate |
| Core | System | 1 | associate |

## Unused documents

Documents of a kind that should be referenced if used, with no inbound reference. "verify" means the graph cannot see the way it may be used; check before deleting. Annotate `unused:<Name>`.

| Document | Type | Verdict | Why |
|---|---|---|---|
| `Shop.ACT_Track_Token` | MICROFLOW | unused |  |
| `Shop.FaultProbe` | PAGE | unused |  |
| `Shop.UnexpectedError` | PAGE | unused |  |

## How this was measured

- Every number is read from the mxcli catalog (`refresh catalog full`, plus the `communities` pass for clusters, layers and centrality). Each section is a query over `CATALOG.REFS` or a `CATALOG.GRAPH_*` view and can be re-run by hand.
- The app is the project's own modules: Marketplace modules, `System` and the test runner's `MxTest` are outside unless `--include-marketplace` or `--modules` says otherwise. Their edges from app modules are listed under "Outside the app".
- Domain dependencies are every reference kind except screen wiring (`layout`, `show_page`, `menu_item`, `home_page`, `widget`, `snippet_call`). The map, layers, matrix and cycles use domain edges only; navigation is reported separately.
- A module's layer is the longest path from it down the condensed domain graph to a module with no dependencies; modules in a cycle share a layer.
- Cohesion is internal references divided by internal plus outbound references, over every kind.
- Clusters are Leiden communities over the structural kinds (`CATALOG.GRAPH_ANALYSIS_SCOPE`), restricted to app modules; clusters smaller than three documents are counted, not shown.

## What this does not cover

- References made from Java actions are not in the graph (ako/mxcli#1819): a microflow called only from Java reads as unused, and a dependency through Java is invisible.
- A name in a string — a constant's value, a `call microflow` by name, a URL — is not a reference. Such documents are marked "verify", never "used".
- Layers and cycles are about module dependencies, not runtime behaviour: a cycle closed by one reference is as much a cycle as one closed by a hundred.
- Cluster labels are derived (dominant module, then most central member); they are not names. Name them with `--annotations`.

## Annotations that matched nothing

These keys are in the annotations file but name nothing on this page. The item was renamed, fixed or removed — update or drop the entry.

- `unused:ACT_Track_Token`
- `unused:FaultProbe`
- `unused:UnexpectedError`

