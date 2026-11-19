# Security review

What protects the data, what does not, and what to fix · GitPizza · generated 2026-11-19 10:25 · mxcli nightly-20261118-9d764483c

| | |
|---|---|
| open high findings | 0 |
| open medium findings | 0 |
| client-callable flows | 35 — 33 to triage |
| security level | Production |

## Findings

Most severe first. Record a status per finding with `--annotations` (`open`, `fixed`, `accepted`, with a note); a fixed finding that comes back is shown open again.

| Severity | Finding | Fix | Status | Key |
|---|---|---|---|---|
| high | Caller-trusting flow `Shop.DS_Info_Line` — Changes an object the client chose, with entity access off: no access rule stops a substituted id. Callable by Administrator, Anonymous. | Derive the acting user or object in the microflow (`$currentUser`, a retrieve constrained by `[%CurrentUser%]`), or turn on entity access and constrain the parameter's entity. | fixed: takes only a product: refuses any product that is not PUBLISHED; the draft line is created in the caller's own cart via SUB_Cart_Current ([%CurrentUser%]); the report detects caller checks by name only | `finding:flow:Shop.DS_Info_Line` |
| info | Anonymous (guest) access is on — Anonymous users get role `Anonymous`. Everything that role may read and call is public. | Check the anonymous role's grid column and callable flows below. | intended: the shop has no sign-in: every visitor is an anonymous guest (LITE-SES-01) | `finding:setting:guest-access` |

Controls that hold:

- Security is at Production level: entity access rules are enforced.
- Strict mode is on: the client API is limited to what pages request.
- Demo users are disabled.
- 21 of 23 persistent app entities have an XPath constraint on every role's read access.
- 2 client-callable flow(s) check the caller in their own body.

## Who can read what

User role × persistent app entity. R read, W write; then the widest read: own rows, via user, filtered, or all (no constraint). `all` is right for reference data and admin roles and wrong almost anywhere else.

| Entity | Administrator | Anonymous |
|---|---|---|
| `Shop.Allergen` | R all | R all |
| `Shop.Cart` | RW via user | RW via user |
| `Shop.CartLine` | R via user | R via user |
| `Shop.Category` | R filtered | R filtered |
| `Shop.CheckoutForm` | RW via user | RW via user |
| `Shop.Coupon` | R via user | R via user |
| `Shop.Courier` | R via user | R via user |
| `Shop.DeliveryZone` | R via user | R via user |
| `Shop.Ingredient` | R filtered | R filtered |
| `Shop.Option` | R filtered | R filtered |
| `Shop.Order` | R via user | R via user |
| `Shop.OrderAccess` | R via user | R via user |
| `Shop.OrderLine` | R via user | R via user |
| `Shop.OrderLineModifier` | R via user | R via user |
| `Shop.OrderLogEntry` | R via user | R via user |
| `Shop.OrderStatusChange` | R via user | R via user |
| `Shop.Oven` | R via user | R via user |
| `Shop.PaymentAttempt` | R via user | R via user |
| `Shop.Product` | R filtered | R filtered |
| `Shop.ProductSize` | R filtered | R filtered |
| `Shop.RecipeItem` | R filtered | R filtered |
| `Shop.StoreSettings` | R all | R all |
| `Shop.Toast` | R via user | R via user |

**Access-rule constraints**

| Entity | XPath | Class | Module roles |
|---|---|---|---|
| `Shop.Cart` | `[Shop.Cart_Owner = '[%CurrentUser%]']` | via user | Shop.Guest |
| `Shop.CartLine` | `[Shop.CartLine_Cart/Shop.Cart/Shop.Cart_Owner = '[%CurrentUser%]']` | via user | Shop.Guest |
| `Shop.Category` | `[Shop.Product_Category/Shop.Product/ProductStatus = 'PUBLISHED']` | filtered | Shop.Guest |
| `Shop.CheckoutForm` | `[Shop.CheckoutForm_Owner = '[%CurrentUser%]']` | via user | Shop.Guest |
| `Shop.Coupon` | `[Shop.Cart_Coupon/Shop.Cart/Shop.Cart_Owner = '[%CurrentUser%]']` | via user | Shop.Guest |
| `Shop.Courier` | `[Shop.Order_Courier/Shop.Order/Shop.OrderAccess_Order/Shop.OrderAccess/Shop.OrderAccess_User = '[%CurrentUser%]']` | via user | Shop.Guest |
| `Shop.DeliveryZone` | `[   Shop.CheckoutForm_Zone/Shop.CheckoutForm/Shop.CheckoutForm_Owner = '[%CurrentUser%]'   or Shop.Order_Zone/Shop.Order/Shop.OrderAccess_Order/Shop.OrderAccess/Shop.OrderAccess_User = '[%CurrentUser%]' ]` | via user | Shop.Guest |
| `Shop.Ingredient` | `[   Shop.RecipeItem_Ingredient/Shop.RecipeItem/Shop.RecipeItem_Product/Shop.Product/ProductStatus = 'PUBLISHED'   or Shop.Option_Ingredient/Shop.Option/IsActive = true ]` | filtered | Shop.Guest |
| `Shop.Option` | `[IsActive = true]` | filtered | Shop.Guest |
| `Shop.Order` | `[Shop.OrderAccess_Order/Shop.OrderAccess/Shop.OrderAccess_User = '[%CurrentUser%]']` | via user | Shop.Guest |
| `Shop.OrderAccess` | `[Shop.OrderAccess_User = '[%CurrentUser%]']` | via user | Shop.Guest |
| `Shop.OrderLine` | `[Shop.OrderLine_Order/Shop.Order/Shop.OrderAccess_Order/Shop.OrderAccess/Shop.OrderAccess_User = '[%CurrentUser%]']` | via user | Shop.Guest |
| `Shop.OrderLineModifier` | `[Shop.OrderLineModifier_OrderLine/Shop.OrderLine/Shop.OrderLine_Order/Shop.Order/Shop.OrderAccess_Order/Shop.OrderAccess/Shop.OrderAccess_User = '[%CurrentUser%]']` | via user | Shop.Guest |
| `Shop.OrderLogEntry` | `[   IsCustomerVisible = true   and Shop.OrderLogEntry_Order/Shop.Order/Shop.OrderAccess_Order/Shop.OrderAccess/Shop.OrderAccess_User = '[%CurrentUser%]' ]` | via user | Shop.Guest |
| `Shop.OrderStatusChange` | `[Shop.OrderStatusChange_Order/Shop.Order/Shop.OrderAccess_Order/Shop.OrderAccess/Shop.OrderAccess_User = '[%CurrentUser%]']` | via user | Shop.Guest |
| `Shop.Oven` | `[Shop.Order_Oven/Shop.Order/Shop.OrderAccess_Order/Shop.OrderAccess/Shop.OrderAccess_User = '[%CurrentUser%]']` | via user | Shop.Guest |
| `Shop.PaymentAttempt` | `[Shop.PaymentAttempt_Order/Shop.Order/Shop.OrderAccess_Order/Shop.OrderAccess/Shop.OrderAccess_User = '[%CurrentUser%]']` | via user | Shop.Guest |
| `Shop.Product` | `[ProductStatus = 'PUBLISHED']` | filtered | Shop.Guest |
| `Shop.ProductSize` | `[Shop.ProductSize_Product/Shop.Product/ProductStatus = 'PUBLISHED']` | filtered | Shop.Guest |
| `Shop.RecipeItem` | `[Shop.RecipeItem_Product/Shop.Product/ProductStatus = 'PUBLISHED']` | filtered | Shop.Guest |
| `Shop.Toast` | `[Shop.Toast_Owner = '[%CurrentUser%]']` | via user | Shop.Guest |

## Client-callable flows

Microflows a user role may call that take a persistent object. The page passes the object as a plain id, so the question is what stops a caller substituting another one: a check in the flow's own body, or access rules on the parameter's entity.

| Microflow | Roles | Object parameters | Entity access | Risk | Triage | Verdict |
|---|---|---|---|---|---|---|
| `Shop.ACT_Cart_Checkout` | Administrator, Anonymous | `$Cart: Object:Shop.Cart` | off | medium | reads an object the client chose, with entity access off | `flow:Shop.ACT_Cart_Checkout` |
| `Shop.ACT_Cart_Clear` | Administrator, Anonymous | `$Cart: Object:Shop.Cart` | off | medium | reads an object the client chose, with entity access off | `flow:Shop.ACT_Cart_Clear` |
| `Shop.ACT_Cart_Edit` | Administrator, Anonymous | `$Line: Object:Shop.CartLine` | off | medium | reads an object the client chose, with entity access off | `flow:Shop.ACT_Cart_Edit` |
| `Shop.ACT_Checkout_Changed` | Administrator, Anonymous | `$Form: Object:Shop.CheckoutForm` | off | medium | reads an object the client chose, with entity access off | `flow:Shop.ACT_Checkout_Changed` |
| `Shop.ACT_Checkout_Pay` | Administrator, Anonymous | `$Form: Object:Shop.CheckoutForm` | off | medium | reads an object the client chose, with entity access off | `flow:Shop.ACT_Checkout_Pay` |
| `Shop.ACT_Checkout_Pickup` | Administrator, Anonymous | `$Form: Object:Shop.CheckoutForm` | off | medium | reads an object the client chose, with entity access off | `flow:Shop.ACT_Checkout_Pickup` |
| `Shop.ACT_Checkout_Place` | Administrator, Anonymous | `$Form: Object:Shop.CheckoutForm` | off | medium | reads an object the client chose, with entity access off | `flow:Shop.ACT_Checkout_Place` |
| `Shop.ACT_Checkout_Tip` | Administrator, Anonymous | `$Form: Object:Shop.CheckoutForm` | off | medium | reads an object the client chose, with entity access off | `flow:Shop.ACT_Checkout_Tip` |
| `Shop.ACT_Checkout_Type` | Administrator, Anonymous | `$Form: Object:Shop.CheckoutForm` | off | medium | reads an object the client chose, with entity access off | `flow:Shop.ACT_Checkout_Type` |
| `Shop.ACT_Config_Back` | Administrator, Anonymous | `$Line: Object:Shop.CartLine` | off | medium | reads an object the client chose, with entity access off | `flow:Shop.ACT_Config_Back` |
| `Shop.ACT_Config_Commit` | Administrator, Anonymous | `$Line: Object:Shop.CartLine` | off | medium | reads an object the client chose, with entity access off | `flow:Shop.ACT_Config_Commit` |
| `Shop.ACT_Config_Qty` | Administrator, Anonymous | `$Line: Object:Shop.CartLine` | off | medium | reads an object the client chose, with entity access off | `flow:Shop.ACT_Config_Qty` |
| `Shop.ACT_Configure_Edit` | Administrator, Anonymous | `$Line: Object:Shop.CartLine` | off | medium | reads an object the client chose, with entity access off | `flow:Shop.ACT_Configure_Edit` |
| `Shop.ACT_Configure_FromHome` | Administrator, Anonymous | `$Product: Object:Shop.Product` | off | medium | reads an object the client chose, with entity access off | `flow:Shop.ACT_Configure_FromHome` |
| `Shop.ACT_Configure_Open` | Administrator, Anonymous | `$Product: Object:Shop.Product` | off | medium | reads an object the client chose, with entity access off | `flow:Shop.ACT_Configure_Open` |
| `Shop.ACT_Coupon_Apply` | Administrator, Anonymous | `$Cart: Object:Shop.Cart` | off | medium | reads an object the client chose, with entity access off | `flow:Shop.ACT_Coupon_Apply` |
| `Shop.ACT_Coupon_Remove` | Administrator, Anonymous | `$Cart: Object:Shop.Cart` | off | medium | reads an object the client chose, with entity access off | `flow:Shop.ACT_Coupon_Remove` |
| `Shop.ACT_Info_Add` | Administrator, Anonymous | `$Line: Object:Shop.CartLine` | off | medium | reads an object the client chose, with entity access off | `flow:Shop.ACT_Info_Add` |
| `Shop.ACT_Line_Decrease` | Administrator, Anonymous | `$Line: Object:Shop.CartLine` | off | medium | reads an object the client chose, with entity access off | `flow:Shop.ACT_Line_Decrease` |
| `Shop.ACT_Line_Increase` | Administrator, Anonymous | `$Line: Object:Shop.CartLine` | off | medium | reads an object the client chose, with entity access off | `flow:Shop.ACT_Line_Increase` |
| `Shop.ACT_Line_Remove` | Administrator, Anonymous | `$Line: Object:Shop.CartLine` | off | medium | reads an object the client chose, with entity access off | `flow:Shop.ACT_Line_Remove` |
| `Shop.ACT_Nav_Search` | Administrator, Anonymous | `$Cart: Object:Shop.Cart` | off | medium | reads an object the client chose, with entity access off | `flow:Shop.ACT_Nav_Search` |
| `Shop.ACT_Product_Add` | Administrator, Anonymous | `$Product: Object:Shop.Product` | off | medium | reads an object the client chose, with entity access off | `flow:Shop.ACT_Product_Add` |
| `Shop.ACT_Product_Info` | Administrator, Anonymous | `$Product: Object:Shop.Product` | off | medium | reads an object the client chose, with entity access off | `flow:Shop.ACT_Product_Info` |
| `Shop.ACT_Product_QuickAdd` | Administrator, Anonymous | `$Product: Object:Shop.Product` | off | medium | reads an object the client chose, with entity access off | `flow:Shop.ACT_Product_QuickAdd` |
| `Shop.ACT_Receipt_Open` | Administrator, Anonymous | `$TheOrder: Object:Shop.Order` | off | medium | reads an object the client chose, with entity access off | `flow:Shop.ACT_Receipt_Open` |
| `Shop.ACT_Shell_Refresh` | Administrator, Anonymous | `$Cart: Object:Shop.Cart` | off | medium | reads an object the client chose, with entity access off | `flow:Shop.ACT_Shell_Refresh` |
| `Shop.ACT_Toast_Close` | Administrator, Anonymous | `$Toast: Object:Shop.Toast` | off | medium | reads an object the client chose, with entity access off | `flow:Shop.ACT_Toast_Close` |
| `Shop.ACT_Track_Open` | Administrator, Anonymous | `$TheOrder: Object:Shop.Order` | off | medium | reads an object the client chose, with entity access off | `flow:Shop.ACT_Track_Open` |
| `Shop.ACT_Track_RetryOpen` | Administrator, Anonymous | `$TheOrder: Object:Shop.Order` | off | medium | reads an object the client chose, with entity access off | `flow:Shop.ACT_Track_RetryOpen` |
| `Shop.DS_Config_Choices` | Administrator, Anonymous | `$Line: Object:Shop.CartLine` | off | ok | checks the caller in its own body ($currentUser / [%CurrentUser%]) |  |
| `Shop.DS_Home_Featured` | Administrator, Anonymous | `$Cart: Object:Shop.Cart` | off | medium | reads an object the client chose, with entity access off | `flow:Shop.DS_Home_Featured` |
| `Shop.DS_Info_Line` | Administrator, Anonymous | `$Product: Object:Shop.Product` | off | high | changes an object the client chose, with entity access off: no access rule stops a substituted id | `flow:Shop.DS_Info_Line` |
| `Shop.DS_Menu_Products` | Administrator, Anonymous | `$Cart: Object:Shop.Cart` | off | medium | reads an object the client chose, with entity access off | `flow:Shop.DS_Menu_Products` |
| `Shop.DS_Track` | Administrator, Anonymous | `$TheOrder: Object:Shop.Order` | off | ok | checks the caller in its own body ($currentUser / [%CurrentUser%]) |  |

## Lint security rules

Each security rule with a verdict: `intended` (the design wants it), `accepted` (a known risk), or `real` (to fix). Annotate `rule:<ID>`. The scored report counts these findings; this table explains them.

| Rule | Severity | Findings | Examples | Verdict |
|---|---|---|---|---|
| CONV007 | info | 2 | Shop.Shop.Allergen: Entity 'Shop.Allergen' has unconstrained READ access for role 'Shop.Guest' - all rows are accessible · Shop.Shop.StoreSettings: Entity 'Shop.StoreSettings' has unconstrained READ access for role 'Shop.Guest' - all rows are accessible | accepted: same two public reference entities |
| CONV008 | info | 1 | ProjectSecurity: Module role 'Shop.Guest' is mapped to 2 user roles: Administrator, Anonymous. Each module role should map to exactly one user role. | unreviewed |
| SEC001 | warning | 4 | Shop.LookupAttempt: Persistent entity 'Shop.LookupAttempt' has no access rules · Shop.SimCustomer: Persistent entity 'Shop.SimCustomer' has no access rules · Shop.SimulationEvent: Persistent entity 'Shop.SimulationEvent' has no access rules | intended: LookupAttempt, SimCustomer, SimulationEvent, SimulationSettings are server-only; no access rule = no client access |
| SEC004 | warning | 1 | ProjectSecurity: Guest access is enabled. Review entity access rules granted to the anonymous user role - any unconstrained READ exposes data to unauthenticated users (DIVD-2022-00019). | intended: guest app; every guest read is row-scoped except public catalog reference data (Allergen, StoreSettings display fields) |
| SEC006 | warning | 1 | Shop.Shop.SimCustomer: Entity 'Shop.SimCustomer' has PII-sounding attributes (Email) but no access rules. | intended: SimCustomer (simulated people) is server-only, no client access |
| SEC007 | error | 2 | Shop.Shop.Allergen: Entity 'Shop.Allergen' is readable by anonymous users (via role 'Shop.Guest') with no XPath constraint — all rows exposed to unauthenticated users. (DIVD-2022-00019) · Shop.Shop.StoreSettings: Entity 'Shop.StoreSettings' is readable by anonymous users (via role 'Shop.Guest') with no XPath constraint — all rows exposed to unauthenticated users. (DIVD-2022-00019) | accepted: Allergen (public allergen list on the notice) and StoreSettings (store name, address, phone, prices) are public by design |
| SEC010 | info | 10 | Shop.Cart_Drawer: List view 'lvLines' on page Shop.Cart_Drawer lists Shop.CartLine, which user roles 'Administrator', 'Anonymous' may read only through an XPath-constrained rule — it renders just the rows the constraint allows · Shop.Checkout: List view 'lvSum' on page Shop.Checkout lists Shop.CartLine, which user roles 'Administrator', 'Anonymous' may read only through an XPath-constrained rule — it renders just the rows the constraint allows · Shop.Configurator: List view 'lvDeps' on page Shop.Configurator lists Shop.Option, which user roles 'Administrator', 'Anonymous' may read only through an XPath-constrained rule — it renders just the rows the constraint allows | intended: list views show only the rows the guest's XPath allows: own cart, own orders |

## How this was measured

- A review of the model, read from the mxcli catalog (`refresh catalog full` and `source`) and the project security settings. Nothing ran against the app.
- Who can read what: each user role's module roles (`CATALOG.ROLE_MAPPINGS`) joined to entity access rules (`CATALOG.PERMISSIONS`). A rule's XPath is classified as own rows (`[System.owner = '[%CurrentUser%]']`), via user (any other path to the current user), filtered (a constraint not about the user) or all (no constraint); a cell shows the widest.
- Client-callable flows: microflows granted to a user role that take a persistent object or list. A flow checks its caller when its body (`CATALOG.SOURCE`) uses `$currentUser` or `[%CurrentUser%]`.
- Unsafe defaults: string constants whose default (or a committed configuration value) looks like key material — base64 of 16/24/32/64 bytes, a 128/192/256-bit hex string, a PEM block — or that are named like a secret; boolean constants named like test switches that default to `true`; the security level, demo users, guest access, strict mode and password policy.
- Lint security rules are grouped per rule with a verdict slot, so the score is explained rather than alarming.

## What this does not cover

- This is a model review, not a penetration test. Hosting (HTTPS, headers, TLS), Marketplace module vulnerabilities, rate limiting and the deployment's own constant values are not covered.
- Object parameters versus association values: an object parameter is a plain id, so a caller can substitute any object it may read; a forged association value is rejected by the runtime ("Hash is invalid"), and with strict mode `mx.data.get` is refused. Only the first is flagged here — confirm a flagged flow before fixing it.
- A caller check is detected by name (`$currentUser`); a check through a sub-microflow or a Java action is not seen, and such a flow is shown as trusting its caller.
- Access through Java actions, OQL datasets, published services' own authentication and nanoflows is not analysed.
- Demo accounts: dropping a demo user from the model does not delete its account from an existing database, and the runtime does not reactivate a deactivated demo account. Check each environment's database.

