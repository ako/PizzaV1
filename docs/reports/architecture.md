# Architecture

Module layers, coupling, bounded contexts and cycles · GitPizza · generated 2026-11-19 09:57 · mxcli nightly-20261118-9d764483c

| | |
|---|---|
| app modules | 2 — 8 outside |
| layers | 1 |
| domain cycles | 0 — 0 modules; 0 with navigation counted |
| clusters | 11 |
| unused documents | 3 — 0 to verify |

## Layered module map

Each app module on the layer its domain dependencies put it on: arrows point from a module to what it uses, thicker for more references. Red dashed arrows close a cycle. Fill shows cohesion.

Layer 0: Shop, Simulation

## Module health

Purpose is the module's documentation (`alter module <Name> set documentation '…'`). Low cohesion is flagged only where nothing explains it. A shell, an admin UI or an adapter is low-cohesion by design; annotate `module:<Name>` to explain another.

| Module | Purpose | Layer | Documents | Internal refs | Outbound | Inbound | Cohesion | Fan-in | Fan-out | Role / note |
|---|---|---|---|---|---|---|---|---|---|---|
| Shop | Git Pizza MxDev guest ordering: catalog, cart, checkout, simulated payment, order tracking and the system pages. | 0 | 465 | 12693 | 9 | 0 | 100% | 0 | 0 |  |
| Simulation | Demo simulation: clock, kitchen, ovens, couriers, payments, traffic and the daily demo reset (SIM-01 … SIM-08). | 0 | 2 | 0 | 0 | 0 | n/a | 0 | 0 |  |

## Coupling matrix (domain)

Rows use columns. Modules are in layer order, highest first, so a layered design is a triangle above the diagonal; a filled cell below it is a dependency upward — part of a cycle.

| uses → | Shop | Simulation |
|---|---|---|
| Shop |  |  |
| Simulation |  |  |

## Navigation dependencies

Menus, layouts and page links between app modules. Counted as dependencies they put 0 modules in cycles; that is how screens are wired, not how the domain is layered.

_(none)_

## Cycles

Each cycle with the exact edges that close it. A cycle is real when both directions carry domain meaning; it is accidental when one direction is a helper that belongs on the other side.

No domain cycles between app modules.

## Bounded contexts

Clusters of tightly connected documents, against the modules they come from. A module spread over several clusters may hold more than one context; a cluster spanning modules may be one context split across them.

| Cluster | Key | Size | Shop | Simulation | Note |
|---|---|---|---|---|---|
| Shop · Cart | `cluster:Shop.Cart` | 121 | 121 |  | label derived — name it |
| Shop · Order | `cluster:Shop.Order` | 66 | 66 |  | label derived — name it |
| Shop · Product | `cluster:Shop.Product` | 59 | 59 |  | label derived — name it |
| Shop · TrackView | `cluster:Shop.TrackView` | 51 | 51 |  | label derived — name it |
| Shop · OrderStatusChange | `cluster:Shop.OrderStatusChange` | 50 | 50 |  | label derived — name it |
| Shop · OrderLogEntry | `cluster:Shop.OrderLogEntry` | 48 | 48 |  | label derived — name it |
| Shop · OrderAccess | `cluster:Shop.OrderAccess` | 19 | 19 |  | label derived — name it |
| Shop · MenuView | `cluster:Shop.MenuView` | 16 | 16 |  | label derived — name it |
| Shop · Option | `cluster:Shop.Option` | 14 | 14 |  | label derived — name it |
| Shop · HomeView | `cluster:Shop.HomeView` | 7 | 7 |  | label derived — name it |
| Shop · ErrorView | `cluster:Shop.ErrorView` | 3 | 3 |  | label derived — name it |

3 cluster(s) of fewer than three documents not shown.

## God nodes, bridges and entity hotspots

God nodes are what the most references hang on; bridges sit on the most shortest paths between other elements (betweenness) and are where a split would cut; hotspots are entities used by the most flows.

**God nodes**

| Element | Type | Module | In | Out | Betweenness |
|---|---|---|---|---|---|
| `Shop.OrderLogEntry` | ENTITY | Shop | 961 | 7 | 0.0 |
| `Shop.SEED_Catalog` | MICROFLOW | Shop | 1 | 837 | 6.0 |
| `Shop.OrderStatusChange` | ENTITY | Shop | 501 | 7 | 0.0 |
| `Shop.Order` | ENTITY | Shop | 421 | 10 | 0.0 |
| `Shop.OrderLineModifier` | ENTITY | Shop | 382 | 8 | 0.0 |
| `Shop.Product` | ENTITY | Shop | 251 | 5 | 0.0 |
| `Shop.OrderLine` | ENTITY | Shop | 244 | 7 | 0.0 |
| `Shop.Option` | ENTITY | Shop | 140 | 3 | 0.0 |
| `Shop.Ingredient` | ENTITY | Shop | 132 | 9 | 0.0 |
| `Shop.SUB_Track_Fill` | MICROFLOW | Shop | 9 | 128 | 155.7 |
| `Shop.PaymentAttempt` | ENTITY | Shop | 124 | 9 | 0.0 |
| `Shop.RecipeItem` | ENTITY | Shop | 112 | 5 | 0.0 |
| `Shop.CartLine` | ENTITY | Shop | 106 | 3 | 0.0 |
| `Shop.ProductSize` | ENTITY | Shop | 100 | 5 | 0.0 |
| `Shop.DS_Config_Choices` | MICROFLOW | Shop | 1 | 87 | 0.0 |

**Bridges**

| Element | Type | Module | In | Out | Betweenness |
|---|---|---|---|---|---|
| `Shop.SUB_Line_Recalculate` | MICROFLOW | Shop | 12 | 62 | 1110.6 |
| `Shop.SUB_Cart_Recalculate` | MICROFLOW | Shop | 13 | 47 | 952.5 |
| `Shop.SEED_Orders` | MICROFLOW | Shop | 1 | 46 | 571.9 |
| `Shop.SUB_Reset` | MICROFLOW | Shop | 3 | 62 | 473.9 |
| `Shop.SUB_Checkout_Recalculate` | MICROFLOW | Shop | 5 | 5 | 297.0 |
| `Shop.SIM_Tick` | MICROFLOW | Shop | 1 | 10 | 262.1 |
| `Shop.SUB_Traffic_Spawn` | MICROFLOW | Shop | 1 | 49 | 193.2 |
| `Shop.SIM_ClockRun` | MICROFLOW | Shop | 4 | 3 | 190.1 |
| `Shop.ACT_Nav_Cart` | MICROFLOW | Shop | 10 | 3 | 175.0 |
| `Shop.SUB_Track_Fill` | MICROFLOW | Shop | 9 | 128 | 155.7 |
| `Shop.SIM_Traffic` | MICROFLOW | Shop | 1 | 12 | 152.2 |
| `Shop.SUB_Product_Add` | MICROFLOW | Shop | 1 | 12 | 148.0 |
| `Shop.SUB_Order_Place` | MICROFLOW | Shop | 2 | 85 | 141.2 |
| `Shop.SUB_Cart_AddLine` | MICROFLOW | Shop | 2 | 37 | 122.2 |
| `Shop.SUB_Price_Compute` | MICROFLOW | Shop | 3 | 27 | 115.0 |

**Entity hotspots**

| Entity | Used by flows | From modules |
|---|---|---|
| `Shop.Order` | 218 | Shop |
| `Shop.Product` | 66 | Shop |
| `Shop.PaymentAttempt` | 54 | Shop |
| `Shop.OrderLine` | 49 | Shop |
| `Shop.OrderLineModifier` | 47 | Shop |
| `Shop.OrderLogEntry` | 47 | Shop |
| `Shop.OrderStatusChange` | 47 | Shop |
| `Shop.Oven` | 41 | Shop |
| `Shop.DeliveryZone` | 37 | Shop |
| `Shop.CartLine` | 34 | Shop |
| `Shop.Cart` | 28 | Shop |
| `Shop.Courier` | 28 | Shop |
| `Shop.TrackView` | 18 | Shop |
| `Shop.CheckoutForm` | 16 | Shop |
| `Shop.MenuView` | 14 | Shop |

## Outside the app

References between app modules and Marketplace or platform modules. These are dependencies to keep upgradeable, not part of the app's layering.

| From | To | References | Kinds |
|---|---|---|---|
| Shop | System | 9 | associate, member, retrieve |

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

