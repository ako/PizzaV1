# Mendix Best Practices Report

**Project:** GitPizza  
**Date:** 2026-11-19 10:26:32  
**Overall Score:** ████░░░░░░ 48/100

## Summary

| Metric | Count |
|--------|-------|
| Errors | 2 |
| Warnings | 96 |
| Info | 148 |
| **Total** | **246** |

## Category Scores

| Category | Score | Errors | Warnings | Info |
|----------|-------|--------|----------|------|
| Security | ████░░░░░░ 49 | 2 | 6 | 13 |
| Quality | ░░░░░░░░░░ 0 | 0 | 36 | 134 |
| Architecture | █████░░░░░ 52 | 0 | 16 | 0 |
| Performance | ██████░░░░ 64 | 0 | 12 | 0 |
| Naming | ██████████ 100 | 0 | 0 | 0 |
| Design | █████░░░░░ 52 | 0 | 16 | 0 |
| Other | ██████░░░░ 69 | 0 | 10 | 1 |

## Recommendations

### Security

- Intended if the list is meant to be row-scoped; otherwise grant an unconstrained READ to a module role those user roles hold
- GRANT <Role> ON Shop.LookupAttempt (READ *)
- Add an XPath constraint to limit which rows 'Shop.Guest' can READ on 'Allergen'
- Add an XPath constraint to the access rule for 'Shop.Guest', or remove the grant if this data should not be public.
- Review the user role assignments for 'Shop.Guest' and ensure a 1:1 mapping

### Quality

- Remove the container, or give it the content it was meant to hold
- Extract logical sections into SUB_ microflows to keep each under 15 activities
- Extract logical sections into SUB_ microflows. This improves readability, testability, and reusability.
- Break down complex logic into sub-microflows. Extract decision branches into separate SUB_ microflows.
- Replace entity validation rules with a VAL_Allergen microflow for explicit, testable validation

### Architecture

- Add an attribute like 'CartCode or ExternalID' with UNIQUE and NOT NULL constraints. Example: Code: String(50) NOT NULL UNIQUE

### Performance

- Move the commit outside the loop, or collect objects in a list and commit once after the loop

### Design

- Extract related attributes into separate entities with associations, or use entity generalization.
- Set error handling to 'Custom with rollback' and add an error handler flow

### Other

- Wrap dataview 'dvCart' in `layoutgrid { row { column (desktopwidth: autofill) { … } } }`
- Widen the gap: the @position x values of the loop and '(unnamed)' must differ by more than half of both widths (1065px here). Or drop the @position annotations around the loop and let the layout place it.
- Describing this microflow does not round-trip. Edit it in Studio Pro, or restructure so each branch reaches the decision's merge without passing through another branch's path. The condition can usually be folded into one decision instead (e.g. `not(a) or b`).

## Detailed Findings

| Rule | Severity | Location | Message |
|------|----------|----------|--------|
| MPR003 | warning | Shop.DomainModel | Module 'Shop' has 27 persistent entities (max 15). Consider splitting into smaller modules. |
| MPR006 | info | Shop.SNIP_HomeActiveOrder | CONTAINER 'apPoll' in Shop.SNIP_HomeActiveOrder is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.SNIP_Stepper | CONTAINER 'fill' in Shop.SNIP_Stepper is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Configurator | CONTAINER 'ltDot' in Shop.Configurator is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Configurator | CONTAINER 'd1' in Shop.Configurator is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Configurator | CONTAINER 'd2' in Shop.Configurator is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Configurator | CONTAINER 'd3' in Shop.Configurator is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Configurator | CONTAINER 'upDiv' in Shop.Configurator is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Home | CONTAINER 'glow1' in Shop.Home is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Home | CONTAINER 'glow2' in Shop.Home is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Home | CONTAINER 'envDot' in Shop.Home is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Home | CONTAINER 'dot1' in Shop.Home is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Home | CONTAINER 'dot2' in Shop.Home is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Home | CONTAINER 'dot3' in Shop.Home is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Home | CONTAINER 'tCursor' in Shop.Home is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Home | CONTAINER 'kpi1Dot' in Shop.Home is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Home | CONTAINER 'px0' in Shop.Home is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Home | CONTAINER 'px1' in Shop.Home is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Home | CONTAINER 'px2' in Shop.Home is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Home | CONTAINER 'px3' in Shop.Home is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Home | CONTAINER 'px4' in Shop.Home is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Home | CONTAINER 'px5' in Shop.Home is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Home | CONTAINER 'px6' in Shop.Home is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Home | CONTAINER 'px7' in Shop.Home is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Home | CONTAINER 'px8' in Shop.Home is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Home | CONTAINER 'px9' in Shop.Home is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Home | CONTAINER 'px10' in Shop.Home is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Home | CONTAINER 'px11' in Shop.Home is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Home | CONTAINER 'px12' in Shop.Home is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Home | CONTAINER 'px13' in Shop.Home is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Home | CONTAINER 'px14' in Shop.Home is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Home | CONTAINER 'px15' in Shop.Home is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Home | CONTAINER 'px16' in Shop.Home is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Home | CONTAINER 'px17' in Shop.Home is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Home | CONTAINER 'px18' in Shop.Home is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Home | CONTAINER 'px19' in Shop.Home is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Home | CONTAINER 'px20' in Shop.Home is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Home | CONTAINER 'px21' in Shop.Home is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Home | CONTAINER 'px22' in Shop.Home is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Home | CONTAINER 'px23' in Shop.Home is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Home | CONTAINER 'px24' in Shop.Home is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Home | CONTAINER 'px25' in Shop.Home is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Home | CONTAINER 'px26' in Shop.Home is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Home | CONTAINER 'px27' in Shop.Home is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Home | CONTAINER 'px28' in Shop.Home is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Home | CONTAINER 'px29' in Shop.Home is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Home | CONTAINER 'px30' in Shop.Home is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Home | CONTAINER 'px31' in Shop.Home is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Home | CONTAINER 'px32' in Shop.Home is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Home | CONTAINER 'px33' in Shop.Home is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Home | CONTAINER 'px34' in Shop.Home is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Home | CONTAINER 'px35' in Shop.Home is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Home | CONTAINER 'px36' in Shop.Home is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Home | CONTAINER 'px37' in Shop.Home is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Home | CONTAINER 'px38' in Shop.Home is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Home | CONTAINER 'px39' in Shop.Home is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Home | CONTAINER 'pb1' in Shop.Home is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Home | CONTAINER 'pb2' in Shop.Home is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Home | CONTAINER 'pb3' in Shop.Home is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Home | CONTAINER 'pb4' in Shop.Home is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Home | CONTAINER 'pb5' in Shop.Home is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Home | CONTAINER 'liveHome' in Shop.Home is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Menu | CONTAINER 'de2c' in Shop.Menu is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Menu | CONTAINER 'menuPoll' in Shop.Menu is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Checkout | CONTAINER 'md1' in Shop.Checkout is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Checkout | CONTAINER 'md2' in Shop.Checkout is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Checkout | CONTAINER 'md3' in Shop.Checkout is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.UnexpectedError | CONTAINER 'titleC' in Shop.UnexpectedError is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.UnexpectedError | CONTAINER 'td1' in Shop.UnexpectedError is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.UnexpectedError | CONTAINER 'td2' in Shop.UnexpectedError is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.UnexpectedError | CONTAINER 'td3' in Shop.UnexpectedError is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Confirmation | CONTAINER 'cd1' in Shop.Confirmation is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Confirmation | CONTAINER 'cd2' in Shop.Confirmation is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Confirmation | CONTAINER 'cd3' in Shop.Confirmation is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Confirmation | CONTAINER 'hkDot' in Shop.Confirmation is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Confirmation | CONTAINER 'sDot' in Shop.Confirmation is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Confirmation | CONTAINER 'confPoll' in Shop.Confirmation is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.NotFound | CONTAINER 'titleC' in Shop.NotFound is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.NotFound | CONTAINER 'td1' in Shop.NotFound is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.NotFound | CONTAINER 'td2' in Shop.NotFound is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.NotFound | CONTAINER 'td3' in Shop.NotFound is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Tracking | CONTAINER 'thLiveDot' in Shop.Tracking is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Tracking | CONTAINER 'dFill' in Shop.Tracking is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Tracking | CONTAINER 'l1' in Shop.Tracking is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Tracking | CONTAINER 'l2' in Shop.Tracking is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Tracking | CONTAINER 'l3' in Shop.Tracking is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Tracking | CONTAINER 'prC' in Shop.Tracking is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Tracking | CONTAINER 'route' in Shop.Tracking is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.Tracking | CONTAINER 'trkPoll' in Shop.Tracking is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.SNIP_Header | CONTAINER 'shellPoll' in Shop.SNIP_Header is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.PaymentSheet | CONTAINER 'progressBar' in Shop.PaymentSheet is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.PaymentSheet | CONTAINER 'ld1' in Shop.PaymentSheet is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.PaymentSheet | CONTAINER 'ld2' in Shop.PaymentSheet is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.PaymentSheet | CONTAINER 'ld3' in Shop.PaymentSheet is empty — valid and it renders, but probably unintended |
| MPR006 | info | Shop.PaymentSheet | CONTAINER 'payPoll' in Shop.PaymentSheet is empty — valid and it renders, but probably unintended |
| MPR010 | warning | Shop.Cart_Drawer | DataView 'dvCart' contains input fields but is not inside a layout grid — label and input widths only render correctly inside a layoutgrid |
| MPR010 | warning | Shop.Checkout | DataView 'dvForm' contains input fields but is not inside a layout grid — label and input widths only render correctly inside a layoutgrid |
| MPR010 | warning | Shop.Menu | DataView 'dvTabs' contains input fields but is not inside a layout grid — label and input widths only render correctly inside a layoutgrid |
| MPR010 | warning | Shop.TrackLookup | DataView 'dvLookup' contains input fields but is not inside a layout grid — label and input widths only render correctly inside a layoutgrid |
| MPR010 | warning | Shop.SNIP_Header | DataView 'dvHeader' contains input fields but is not inside a layout grid — label and input widths only render correctly inside a layoutgrid |
| SEC001 | warning | Shop.LookupAttempt | Persistent entity 'Shop.LookupAttempt' has no access rules |
| SEC001 | warning | Shop.SimCustomer | Persistent entity 'Shop.SimCustomer' has no access rules |
| SEC001 | warning | Shop.SimulationEvent | Persistent entity 'Shop.SimulationEvent' has no access rules |
| SEC001 | warning | Shop.SimulationSettings | Persistent entity 'Shop.SimulationSettings' has no access rules |
| SEC010 | info | Shop.Cart_Drawer | List view 'lvLines' on page Shop.Cart_Drawer lists Shop.CartLine, which user roles 'Administrator', 'Anonymous' may read only through an XPath-constrained rule — it renders just the rows the constraint allows |
| SEC010 | info | Shop.Checkout | List view 'lvSum' on page Shop.Checkout lists Shop.CartLine, which user roles 'Administrator', 'Anonymous' may read only through an XPath-constrained rule — it renders just the rows the constraint allows |
| SEC010 | info | Shop.Configurator | List view 'lvDeps' on page Shop.Configurator lists Shop.Option, which user roles 'Administrator', 'Anonymous' may read only through an XPath-constrained rule — it renders just the rows the constraint allows |
| SEC010 | info | Shop.Configurator | List view 'lvUnl' on page Shop.Configurator lists Shop.Ingredient, which user roles 'Administrator', 'Anonymous' may read only through an XPath-constrained rule — it renders just the rows the constraint allows |
| SEC010 | info | Shop.Menu | List view 'lvDbg' on page Shop.Menu lists Shop.CartLine, which user roles 'Administrator', 'Anonymous' may read only through an XPath-constrained rule — it renders just the rows the constraint allows |
| SEC010 | info | Shop.Receipt | List view 'lvAttempts' on page Shop.Receipt lists Shop.PaymentAttempt, which user roles 'Administrator', 'Anonymous' may read only through an XPath-constrained rule — it renders just the rows the constraint allows |
| SEC010 | info | Shop.Receipt | List view 'lvHist' on page Shop.Receipt lists Shop.OrderStatusChange, which user roles 'Administrator', 'Anonymous' may read only through an XPath-constrained rule — it renders just the rows the constraint allows |
| SEC010 | info | Shop.Receipt | List view 'lvMods' on page Shop.Receipt lists Shop.OrderLineModifier, which user roles 'Administrator', 'Anonymous' may read only through an XPath-constrained rule — it renders just the rows the constraint allows |
| SEC010 | info | Shop.Receipt | List view 'lvRLines' on page Shop.Receipt lists Shop.OrderLine, which user roles 'Administrator', 'Anonymous' may read only through an XPath-constrained rule — it renders just the rows the constraint allows |
| SEC010 | info | Shop.Tracking | List view 'lvLines' on page Shop.Tracking lists Shop.OrderLine, which user roles 'Administrator', 'Anonymous' may read only through an XPath-constrained rule — it renders just the rows the constraint allows |
| MPR008 | warning | Shop.SIM_Couriers | The box of loop '(loop)' (1305,2975, 2010x310) overlaps '(unnamed)' (360,2975) in microflow 'Shop.SIM_Couriers'. A loop's box grows with its body, so a gap sized for an ordinary activity is not enough. |
| MPR008 | warning | Shop.SIM_Kitchen | The box of loop '(loop)' (1715,1900, 2350x760) overlaps '(unnamed)' (520,1900) in microflow 'Shop.SIM_Kitchen'. A loop's box grows with its body, so a gap sized for an ordinary activity is not enough. |
| MPR008 | warning | Shop.SIM_Kitchen | The box of loop '(loop)' (1715,1900, 2350x760) overlaps '(unnamed)' (680,1900) in microflow 'Shop.SIM_Kitchen'. A loop's box grows with its body, so a gap sized for an ordinary activity is not enough. |
| MPR008 | warning | Shop.SIM_Kitchen | The box of loop '(loop)' (1715,1900, 2350x760) overlaps '(end)' (2830,1900) in microflow 'Shop.SIM_Kitchen'. A loop's box grows with its body, so a gap sized for an ordinary activity is not enough. |
| MPR008 | warning | Shop.SIM_Pickups | The box of loop '(loop)' (1065,200, 1370x310) overlaps '(unnamed)' (360,200) in microflow 'Shop.SIM_Pickups'. A loop's box grows with its body, so a gap sized for an ordinary activity is not enough. |
| CONV011 | warning | Shop.SIM_Couriers | Microflow 'Shop.SIM_Couriers' has a Change object action with Commit enabled inside a loop. This causes N+1 database operations. |
| CONV011 | warning | Shop.SIM_Couriers | Microflow 'Shop.SIM_Couriers' has a Change object action with Commit enabled inside a loop. This causes N+1 database operations. |
| CONV011 | warning | Shop.SIM_Couriers | Microflow 'Shop.SIM_Couriers' has a Create object action with Commit enabled inside a loop. This causes N+1 database operations. |
| CONV011 | warning | Shop.SIM_Couriers | Microflow 'Shop.SIM_Couriers' has a Change object action with Commit enabled inside a loop. This causes N+1 database operations. |
| CONV011 | warning | Shop.SIM_Couriers | Microflow 'Shop.SIM_Couriers' has a Create object action with Commit enabled inside a loop. This causes N+1 database operations. |
| CONV011 | warning | Shop.SIM_Couriers | Microflow 'Shop.SIM_Couriers' has a Change object action with Commit enabled inside a loop. This causes N+1 database operations. |
| CONV011 | warning | Shop.SIM_Couriers | Microflow 'Shop.SIM_Couriers' has a Create object action with Commit enabled inside a loop. This causes N+1 database operations. |
| CONV011 | warning | Shop.SIM_Kitchen | Microflow 'Shop.SIM_Kitchen' has a Change object action with Commit enabled inside a loop. This causes N+1 database operations. |
| CONV011 | warning | Shop.SIM_Kitchen | Microflow 'Shop.SIM_Kitchen' has a Change object action with Commit enabled inside a loop. This causes N+1 database operations. |
| CONV011 | warning | Shop.SIM_Pickups | Microflow 'Shop.SIM_Pickups' has a Create object action with Commit enabled inside a loop. This causes N+1 database operations. |
| CONV011 | warning | Shop.SUB_Cart_Recalculate | Microflow 'Shop.SUB_Cart_Recalculate' has a Change object action with Commit enabled inside a loop. This causes N+1 database operations. |
| CONV011 | warning | Shop.SUB_Order_Place | Microflow 'Shop.SUB_Order_Place' has a Create object action with Commit enabled inside a loop. This causes N+1 database operations. |
| CONV013 | warning | Shop.SIM_ClockRun | Java action call in 'Shop.SIM_ClockRun' uses 'Rollback' error handling instead of Custom. |
| CONV014 | warning | Shop.SIM_ClockRun | Activity '(unnamed activity)' in 'Shop.SIM_ClockRun' uses 'Continue' error handling, which silently swallows errors. |
| CONV014 | warning | Shop.SIM_Tick | Activity '(unnamed activity)' in 'Shop.SIM_Tick' uses 'Continue' error handling, which silently swallows errors. |
| CONV014 | warning | Shop.SIM_Tick | Activity '(unnamed activity)' in 'Shop.SIM_Tick' uses 'Continue' error handling, which silently swallows errors. |
| CONV014 | warning | Shop.SIM_Tick | Activity '(unnamed activity)' in 'Shop.SIM_Tick' uses 'Continue' error handling, which silently swallows errors. |
| CONV014 | warning | Shop.SIM_Tick | Activity '(unnamed activity)' in 'Shop.SIM_Tick' uses 'Continue' error handling, which silently swallows errors. |
| CONV014 | warning | Shop.SIM_Tick | Activity '(unnamed activity)' in 'Shop.SIM_Tick' uses 'Continue' error handling, which silently swallows errors. |
| CONV014 | warning | Shop.SIM_Tick | Activity '(unnamed activity)' in 'Shop.SIM_Tick' uses 'Continue' error handling, which silently swallows errors. |
| MDL-FLOW01 | info | Shop.SIM_Housekeeping | 'Shop.SIM_Housekeeping': 2 branches of a decision at (680, 200) rejoin at one shared point before the decision's own merge, so the block cannot be nested. DESCRIBE renders it as nested IFs and drops the path that enters the shared part early — the described flow is not the flow you drew [recombinable, overlap 13 node(s)] |
| CONV007 | info | Shop.Allergen | Entity 'Shop.Allergen' has unconstrained READ access for role 'Shop.Guest' - all rows are accessible |
| CONV007 | info | Shop.StoreSettings | Entity 'Shop.StoreSettings' has unconstrained READ access for role 'Shop.Guest' - all rows are accessible |
| CONV008 | info | ProjectSecurity | Module role 'Shop.Guest' is mapped to 2 user roles: Administrator, Anonymous. Each module role should map to exactly one user role. |
| CONV009 | info | Shop.DS_Config_Choices | Microflow 'DS_Config_Choices' has 61 activities (convention max: 15). Split into sub-microflows. |
| CONV009 | info | Shop.DS_Menu_Products | Microflow 'DS_Menu_Products' has 19 activities (convention max: 15). Split into sub-microflows. |
| CONV009 | info | Shop.SEED_Catalog | Microflow 'SEED_Catalog' has 376 activities (convention max: 15). Split into sub-microflows. |
| CONV009 | info | Shop.SEED_Order_1017_Lines | Microflow 'SEED_Order_1017_Lines' has 19 activities (convention max: 15). Split into sub-microflows. |
| CONV009 | info | Shop.SEED_Order_1022_Log | Microflow 'SEED_Order_1022_Log' has 19 activities (convention max: 15). Split into sub-microflows. |
| CONV009 | info | Shop.SEED_Order_1026_Log | Microflow 'SEED_Order_1026_Log' has 16 activities (convention max: 15). Split into sub-microflows. |
| CONV009 | info | Shop.SEED_Orders | Microflow 'SEED_Orders' has 46 activities (convention max: 15). Split into sub-microflows. |
| CONV009 | info | Shop.SUB_Cart_AddLine | Microflow 'SUB_Cart_AddLine' has 33 activities (convention max: 15). Split into sub-microflows. |
| CONV009 | info | Shop.SUB_Cart_Recalculate | Microflow 'SUB_Cart_Recalculate' has 37 activities (convention max: 15). Split into sub-microflows. |
| CONV009 | info | Shop.SUB_Checkout_Compute | Microflow 'SUB_Checkout_Compute' has 51 activities (convention max: 15). Split into sub-microflows. |
| CONV009 | info | Shop.SUB_Checkout_Place | Microflow 'SUB_Checkout_Place' has 70 activities (convention max: 15). Split into sub-microflows. |
| CONV009 | info | Shop.SUB_Config_Choose | Microflow 'SUB_Config_Choose' has 38 activities (convention max: 15). Split into sub-microflows. |
| CONV009 | info | Shop.SUB_Config_Commit | Microflow 'SUB_Config_Commit' has 35 activities (convention max: 15). Split into sub-microflows. |
| CONV009 | info | Shop.SUB_Coupon_Evaluate | Microflow 'SUB_Coupon_Evaluate' has 18 activities (convention max: 15). Split into sub-microflows. |
| CONV009 | info | Shop.SUB_Home_Refresh | Microflow 'SUB_Home_Refresh' has 33 activities (convention max: 15). Split into sub-microflows. |
| CONV009 | info | Shop.SUB_Line_Recalculate | Microflow 'SUB_Line_Recalculate' has 60 activities (convention max: 15). Split into sub-microflows. |
| CONV009 | info | Shop.SUB_Lookup | Microflow 'SUB_Lookup' has 17 activities (convention max: 15). Split into sub-microflows. |
| CONV009 | info | Shop.SUB_Menu_Refresh | Microflow 'SUB_Menu_Refresh' has 33 activities (convention max: 15). Split into sub-microflows. |
| CONV009 | info | Shop.SUB_OrderLine_SnapshotModifiers | Microflow 'SUB_OrderLine_SnapshotModifiers' has 22 activities (convention max: 15). Split into sub-microflows. |
| CONV009 | info | Shop.SUB_Order_Place | Microflow 'SUB_Order_Place' has 25 activities (convention max: 15). Split into sub-microflows. |
| CONV009 | info | Shop.SUB_Order_TimerBase | Microflow 'SUB_Order_TimerBase' has 23 activities (convention max: 15). Split into sub-microflows. |
| CONV009 | info | Shop.SUB_Payment_Resolve | Microflow 'SUB_Payment_Resolve' has 40 activities (convention max: 15). Split into sub-microflows. |
| CONV009 | info | Shop.SUB_Price_Compute | Microflow 'SUB_Price_Compute' has 35 activities (convention max: 15). Split into sub-microflows. |
| CONV009 | info | Shop.SUB_Product_Recalculate | Microflow 'SUB_Product_Recalculate' has 50 activities (convention max: 15). Split into sub-microflows. |
| CONV009 | info | Shop.SUB_Reset | Microflow 'SUB_Reset' has 59 activities (convention max: 15). Split into sub-microflows. |
| CONV009 | info | Shop.SUB_Track_Fill | Microflow 'SUB_Track_Fill' has 184 activities (convention max: 15). Split into sub-microflows. |
| CONV009 | info | Shop.SUB_Traffic_Spawn | Microflow 'SUB_Traffic_Spawn' has 22 activities (convention max: 15). Split into sub-microflows. |
| CONV015 | info | Shop.Allergen | Entity 'Shop.Allergen' has 2 validation rule(s). Use VAL_ microflows for validation logic instead. |
| CONV015 | info | Shop.Category | Entity 'Shop.Category' has 2 validation rule(s). Use VAL_ microflows for validation logic instead. |
| CONV015 | info | Shop.Coupon | Entity 'Shop.Coupon' has 2 validation rule(s). Use VAL_ microflows for validation logic instead. |
| CONV015 | info | Shop.Courier | Entity 'Shop.Courier' has 2 validation rule(s). Use VAL_ microflows for validation logic instead. |
| CONV015 | info | Shop.DeliveryZone | Entity 'Shop.DeliveryZone' has 2 validation rule(s). Use VAL_ microflows for validation logic instead. |
| CONV015 | info | Shop.Ingredient | Entity 'Shop.Ingredient' has 2 validation rule(s). Use VAL_ microflows for validation logic instead. |
| CONV015 | info | Shop.Option | Entity 'Shop.Option' has 2 validation rule(s). Use VAL_ microflows for validation logic instead. |
| CONV015 | info | Shop.Order | Entity 'Shop.Order' has 2 validation rule(s). Use VAL_ microflows for validation logic instead. |
| CONV015 | info | Shop.Oven | Entity 'Shop.Oven' has 2 validation rule(s). Use VAL_ microflows for validation logic instead. |
| CONV015 | info | Shop.Product | Entity 'Shop.Product' has 2 validation rule(s). Use VAL_ microflows for validation logic instead. |
| CONV015 | info | Shop.SimCustomer | Entity 'Shop.SimCustomer' has 2 validation rule(s). Use VAL_ microflows for validation logic instead. |
| DESIGN001 | warning | Shop.Cart | Entity 'Cart' has 28 attributes (max: 10). Consider splitting into smaller entities. |
| DESIGN001 | warning | Shop.CartLine | Entity 'CartLine' has 21 attributes (max: 10). Consider splitting into smaller entities. |
| DESIGN001 | warning | Shop.CheckoutForm | Entity 'CheckoutForm' has 46 attributes (max: 10). Consider splitting into smaller entities. |
| DESIGN001 | warning | Shop.Choice | Entity 'Choice' has 11 attributes (max: 10). Consider splitting into smaller entities. |
| DESIGN001 | warning | Shop.Courier | Entity 'Courier' has 12 attributes (max: 10). Consider splitting into smaller entities. |
| DESIGN001 | warning | Shop.HomeView | Entity 'HomeView' has 17 attributes (max: 10). Consider splitting into smaller entities. |
| DESIGN001 | warning | Shop.Option | Entity 'Option' has 16 attributes (max: 10). Consider splitting into smaller entities. |
| DESIGN001 | warning | Shop.Order | Entity 'Order' has 51 attributes (max: 10). Consider splitting into smaller entities. |
| DESIGN001 | warning | Shop.OrderLine | Entity 'OrderLine' has 15 attributes (max: 10). Consider splitting into smaller entities. |
| DESIGN001 | warning | Shop.PaymentAttempt | Entity 'PaymentAttempt' has 12 attributes (max: 10). Consider splitting into smaller entities. |
| DESIGN001 | warning | Shop.Product | Entity 'Product' has 45 attributes (max: 10). Consider splitting into smaller entities. |
| DESIGN001 | warning | Shop.SimCustomer | Entity 'SimCustomer' has 12 attributes (max: 10). Consider splitting into smaller entities. |
| DESIGN001 | warning | Shop.SimulationSettings | Entity 'SimulationSettings' has 24 attributes (max: 10). Consider splitting into smaller entities. |
| DESIGN001 | warning | Shop.StoreSettings | Entity 'StoreSettings' has 11 attributes (max: 10). Consider splitting into smaller entities. |
| DESIGN001 | warning | Shop.TrackView | Entity 'TrackView' has 64 attributes (max: 10). Consider splitting into smaller entities. |
| ARCH003 | warning | Shop.Cart | Entity 'Cart' has no business key. Add a UNIQUE NOT NULL attribute for cross-system identification. |
| ARCH003 | warning | Shop.CartLine | Entity 'CartLine' has no business key. Add a UNIQUE NOT NULL attribute for cross-system identification. |
| ARCH003 | warning | Shop.CheckoutForm | Entity 'CheckoutForm' has no business key. Add a UNIQUE NOT NULL attribute for cross-system identification. |
| ARCH003 | warning | Shop.LookupAttempt | Entity 'LookupAttempt' has no business key. Add a UNIQUE NOT NULL attribute for cross-system identification. |
| ARCH003 | warning | Shop.OrderAccess | Entity 'OrderAccess' has no business key. Add a UNIQUE NOT NULL attribute for cross-system identification. |
| ARCH003 | warning | Shop.OrderLine | Entity 'OrderLine' has no business key. Add a UNIQUE NOT NULL attribute for cross-system identification. |
| ARCH003 | warning | Shop.OrderLineModifier | Entity 'OrderLineModifier' has no business key. Add a UNIQUE NOT NULL attribute for cross-system identification. |
| ARCH003 | warning | Shop.OrderLogEntry | Entity 'OrderLogEntry' has no business key. Add a UNIQUE NOT NULL attribute for cross-system identification. |
| ARCH003 | warning | Shop.OrderStatusChange | Entity 'OrderStatusChange' has no business key. Add a UNIQUE NOT NULL attribute for cross-system identification. |
| ARCH003 | warning | Shop.PaymentAttempt | Entity 'PaymentAttempt' has no business key. Add a UNIQUE NOT NULL attribute for cross-system identification. |
| ARCH003 | warning | Shop.ProductSize | Entity 'ProductSize' has no business key. Add a UNIQUE NOT NULL attribute for cross-system identification. |
| ARCH003 | warning | Shop.RecipeItem | Entity 'RecipeItem' has no business key. Add a UNIQUE NOT NULL attribute for cross-system identification. |
| ARCH003 | warning | Shop.SimulationEvent | Entity 'SimulationEvent' has no business key. Add a UNIQUE NOT NULL attribute for cross-system identification. |
| ARCH003 | warning | Shop.SimulationSettings | Entity 'SimulationSettings' has no business key. Add a UNIQUE NOT NULL attribute for cross-system identification. |
| ARCH003 | warning | Shop.StoreSettings | Entity 'StoreSettings' has no business key. Add a UNIQUE NOT NULL attribute for cross-system identification. |
| ARCH003 | warning | Shop.Toast | Entity 'Toast' has no business key. Add a UNIQUE NOT NULL attribute for cross-system identification. |
| QUAL003 | warning | Shop.DS_Config_Choices | Microflow 'DS_Config_Choices' has 61 activities (max: 25). Consider splitting into smaller microflows. |
| QUAL003 | warning | Shop.SEED_Catalog | Microflow 'SEED_Catalog' has 376 activities (max: 25). Consider splitting into smaller microflows. |
| QUAL003 | warning | Shop.SEED_Orders | Microflow 'SEED_Orders' has 46 activities (max: 25). Consider splitting into smaller microflows. |
| QUAL003 | warning | Shop.SUB_Cart_AddLine | Microflow 'SUB_Cart_AddLine' has 33 activities (max: 25). Consider splitting into smaller microflows. |
| QUAL003 | warning | Shop.SUB_Cart_Recalculate | Microflow 'SUB_Cart_Recalculate' has 37 activities (max: 25). Consider splitting into smaller microflows. |
| QUAL003 | warning | Shop.SUB_Checkout_Compute | Microflow 'SUB_Checkout_Compute' has 51 activities (max: 25). Consider splitting into smaller microflows. |
| QUAL003 | warning | Shop.SUB_Checkout_Place | Microflow 'SUB_Checkout_Place' has 70 activities (max: 25). Consider splitting into smaller microflows. |
| QUAL003 | warning | Shop.SUB_Config_Choose | Microflow 'SUB_Config_Choose' has 38 activities (max: 25). Consider splitting into smaller microflows. |
| QUAL003 | warning | Shop.SUB_Config_Commit | Microflow 'SUB_Config_Commit' has 35 activities (max: 25). Consider splitting into smaller microflows. |
| QUAL003 | warning | Shop.SUB_Home_Refresh | Microflow 'SUB_Home_Refresh' has 33 activities (max: 25). Consider splitting into smaller microflows. |
| QUAL003 | warning | Shop.SUB_Line_Recalculate | Microflow 'SUB_Line_Recalculate' has 60 activities (max: 25). Consider splitting into smaller microflows. |
| QUAL003 | warning | Shop.SUB_Menu_Refresh | Microflow 'SUB_Menu_Refresh' has 33 activities (max: 25). Consider splitting into smaller microflows. |
| QUAL003 | warning | Shop.SUB_Payment_Resolve | Microflow 'SUB_Payment_Resolve' has 40 activities (max: 25). Consider splitting into smaller microflows. |
| QUAL003 | warning | Shop.SUB_Price_Compute | Microflow 'SUB_Price_Compute' has 35 activities (max: 25). Consider splitting into smaller microflows. |
| QUAL003 | warning | Shop.SUB_Product_Recalculate | Microflow 'SUB_Product_Recalculate' has 50 activities (max: 25). Consider splitting into smaller microflows. |
| QUAL003 | warning | Shop.SUB_Reset | Microflow 'SUB_Reset' has 59 activities (max: 25). Consider splitting into smaller microflows. |
| QUAL003 | warning | Shop.SUB_Track_Fill | Microflow 'SUB_Track_Fill' has 184 activities (max: 25). Consider splitting into smaller microflows. |
| QUAL001 | warning | Shop.DS_Config_Choices | Microflow 'DS_Config_Choices' has complexity 21 (max: 10). Consider splitting into smaller microflows. |
| QUAL001 | warning | Shop.SIM_Couriers | Microflow 'SIM_Couriers' has complexity 17 (max: 10). Consider splitting into smaller microflows. |
| QUAL001 | warning | Shop.SIM_Kitchen | Microflow 'SIM_Kitchen' has complexity 13 (max: 10). Consider splitting into smaller microflows. |
| QUAL001 | warning | Shop.SUB_Cart_Recalculate | Microflow 'SUB_Cart_Recalculate' has complexity 14 (max: 10). Consider splitting into smaller microflows. |
| QUAL001 | warning | Shop.SUB_Checkout_Place | Microflow 'SUB_Checkout_Place' has complexity 16 (max: 10). Consider splitting into smaller microflows. |
| QUAL001 | warning | Shop.SUB_Config_Choose | Microflow 'SUB_Config_Choose' has complexity 14 (max: 10). Consider splitting into smaller microflows. |
| QUAL001 | warning | Shop.SUB_Line_Recalculate | Microflow 'SUB_Line_Recalculate' has complexity 19 (max: 10). Consider splitting into smaller microflows. |
| QUAL001 | warning | Shop.SUB_Order_TimerBase | Microflow 'SUB_Order_TimerBase' has complexity 11 (max: 10). Consider splitting into smaller microflows. |
| QUAL001 | warning | Shop.SUB_Price_Compute | Microflow 'SUB_Price_Compute' has complexity 12 (max: 10). Consider splitting into smaller microflows. |
| QUAL001 | warning | Shop.SUB_Product_Recalculate | Microflow 'SUB_Product_Recalculate' has complexity 12 (max: 10). Consider splitting into smaller microflows. |
| QUAL001 | warning | Shop.SUB_Track_Fill | Microflow 'SUB_Track_Fill' has complexity 38 (max: 10). Consider splitting into smaller microflows. |
| QUAL004 | info | Shop.FaultProbe | Page 'FaultProbe' is not shown from any microflow. |
| QUAL004 | info | Shop.UnexpectedError | Page 'UnexpectedError' is not shown from any microflow. |
| SEC004 | warning | ProjectSecurity | Guest access is enabled. Review entity access rules granted to the anonymous user role - any unconstrained READ exposes data to unauthenticated users (DIVD-2022-00019). |
| SEC006 | warning | Shop.SimCustomer | Entity 'Shop.SimCustomer' has PII-sounding attributes (Email) but no access rules. |
| SEC007 | error | Shop.Allergen | Entity 'Shop.Allergen' is readable by anonymous users (via role 'Shop.Guest') with no XPath constraint — all rows exposed to unauthenticated users. (DIVD-2022-00019) |
| SEC007 | error | Shop.StoreSettings | Entity 'Shop.StoreSettings' is readable by anonymous users (via role 'Shop.Guest') with no XPath constraint — all rows exposed to unauthenticated users. (DIVD-2022-00019) |

