# Tests

What the tests check, whether they passed, and which microflows they reach · GitPizza · generated 2026-11-19 10:19 · mxcli nightly-20261118-9d764483c

| | |
|---|---|
| microflow tests passed | 24/24 — 52 checks |
| journeys passed | 11/11 — 0 checks |
| microflows reached | 32% — 114 of 352 |
| startup or scheduled only | 193 |
| reached by neither | 45 |

## Microflow coverage per module

Each app microflow in one category: reached by both layers, by microflow tests only, by journeys only, run only at startup or on a schedule (not a gap), or by neither.

> **Note:** Database state for the journeys: fresh demo reset

| Module | Microflows | Both | Tests only | Journeys only | Startup / scheduled | Neither | Reached |
|---|---|---|---|---|---|---|---|
| Shop | 352 | 10 | 0 | 104 | 193 | 45 | 32% |
| All app modules | 352 | 10 | 0 | 104 | 193 | 45 | 32% |

## Microflow tests

| Test | Status | Checks | Calls | Reaches | Note |
|---|---|---|---|---|---|
| Money with thousands separator and two decimals | passed | 1 | `Shop.SUB_Money` | 1 |  |
| Negative money uses a true minus sign | passed | 1 | `Shop.SUB_Money` | 1 |  |
| Timer text mm:ss | passed | 1 | `Shop.SUB_MmSs` | 1 |  |
| Negative seconds clamp to 00:00 | passed | 1 | `Shop.SUB_MmSs` | 1 |  |
| Phone with spaces is normalised | passed | 1 | `Shop.SUB_FormatPhone` | 1 |  |
| Phone with country code +1 is normalised | passed | 1 | `Shop.SUB_FormatPhone` | 1 |  |
| Phone with letters is rejected | passed | 1 | `Shop.SUB_FormatPhone` | 1 |  |
| Phone with too few digits is rejected | passed | 1 | `Shop.SUB_FormatPhone` | 1 |  |
| Example A: delivery over the free-delivery threshold, tip 15 % | passed | 4 | `Shop.SUB_Price_Compute` | 3 |  |
| Example A20: tip 20 % | passed | 2 | `Shop.SUB_Price_Compute` | 3 |  |
| Example A0: no tip | passed | 1 | `Shop.SUB_Price_Compute` | 3 |  |
| Example B: GITHUB_STUDENT 15 % on delivery under the threshold | passed | 5 | `Shop.SUB_Price_Compute` | 3 |  |
| Example D: pickup has no fee and no tip | passed | 3 | `Shop.SUB_Price_Compute` | 3 |  |
| P1: percentage discount rounded half-up (4.425 to 4.43) | passed | 2 | `Shop.SUB_Price_Compute` | 3 |  |
| P2: FREE_DISPATCH waives the delivery fee | passed | 3 | `Shop.SUB_Price_Compute` | 3 |  |
| P2-pickup: a delivery-only coupon is not applied to pickup | passed | 3 | `Shop.SUB_Price_Compute` | 3 |  |
| P3: below the coupon minimum names the missing amount | passed | 3 | `Shop.SUB_Price_Compute` | 3 |  |
| P4: percentage discount capped at the coupon maximum | passed | 4 | `Shop.SUB_Price_Compute` | 3 |  |
| P10: pickup under the delivery minimum | passed | 2 | `Shop.SUB_Price_Compute` | 3 |  |
| P11: tax rounded half-up (1.7457 to 1.75) | passed | 1 | `Shop.SUB_Price_Compute` | 3 |  |
| P6: vegan cheese surcharge, allergens GLUTEN and TREE_NUTS, vegan | passed | 4 | `Shop.SUB_Line_ApplyDefaults`, `Shop.SUB_Line_Recalculate` | 6 |  |
| P7: stuffed crust makes a vegetarian pizza non-vegan | passed | 4 | `Shop.SUB_Line_ApplyDefaults`, `Shop.SUB_Line_Recalculate` | 6 |  |
| P8: gluten-free crust on Small removes GLUTEN | passed | 2 | `Shop.SUB_Line_ApplyDefaults`, `Shop.SUB_Line_Recalculate` | 6 |  |
| Example C: Boolean Pepperoni Large fully configured | passed | 1 | `Shop.SUB_Line_ApplyDefaults`, `Shop.SUB_Line_Recalculate` | 6 |  |

## Browser journeys

What each journey checks is taken from the journey script's own check messages, not written from its name — prose written from a name drifts from what the script verifies. Annotate `journey:<name>` to add context.

| Journey | Status | Checks | Microflows run | What it checks |
|---|---|---|---|---|
| J1 order, pay and track (example: Root Pizza + Binary BBQ, delivery, tip 15 %) | passed | 0 | 59 |  |
| J2 coupon GITHUB_STUDENT on example B (Root Pizza M + Garlic Knot Loop) gives $26.58 | passed | 0 | 48 |  |
| J3 declined card VISA_0002, then retry with Apple Pay succeeds (scenario: Example B, G2) | passed | 0 | 66 |  |
| J4 order lookup rejects an unknown order without revealing which field was wrong | passed | 0 | 34 |  |
| J5 unknown URL shows ERROR 404 // CRUST_NOT_FOUND with RETURN_TO_MAIN | passed | 0 | 18 |  |
| J6 connection loss shows the CONNECTION_LOST banner and blocks actions with a toast | passed | 0 | 25 |  |
| J8 home: featured carousel pages and Configure opens the configurator | passed | 0 | 41 |  |
| J9 configure Inferno Payload Large + cherry tomatoes = $25.00, then cart quantity, remove and clear | passed | 0 | 50 |  |
| J10 menu grep and dietary filters (US-027, US-033) | passed | 0 | 29 |  |
| J11 pickup removes fee and tip; rollback while QUEUED refunds (US-086, US-129) | passed | 0 | 67 |  |
| J7 phone: bottom navigation and menu cards render at 390 px | passed | 0 | 24 |  |

## Gaps

Microflows no test and no journey reaches, by module. Not every gap deserves a test: give each group a verdict with `--annotations` (e.g. `needs a test`, `admin only`, `dead — remove`).

| Module | Microflows reached by neither | Verdict | Key |
|---|---|---|---|
| Shop | `Shop.ACT_Cart_Checkout`, `Shop.ACT_Cart_Edit`, `Shop.ACT_Cart_ToMenu`, `Shop.ACT_Checkout_Pickup`, `Shop.ACT_Config_Back`, `Shop.ACT_Config_Qty`, `Shop.ACT_Configure_Edit`, `Shop.ACT_Coupon_Remove`, `Shop.ACT_Info_Add`, `Shop.ACT_Line_Remove`, `Shop.ACT_Menu_ClearSearch`, `Shop.ACT_Menu_ShowAll`, `Shop.ACT_Nav_Home`, `Shop.ACT_Nav_Menu`, `Shop.ACT_Nav_Search`, `Shop.ACT_Nav_Track`, `Shop.ACT_Pay_Cancel`, `Shop.ACT_Pay_CancelAndCart`, `Shop.ACT_Pay_ToCart`, `Shop.ACT_Product_Info`, `Shop.ACT_Receipt_Open`, `Shop.ACT_Toast_Close`, `Shop.ACT_Toast_Copied`, `Shop.ACT_Track_OpenView`, `Shop.ACT_Track_RetryOpen`, `Shop.ACT_Track_Token`, `Shop.DS_Error`, `Shop.DS_FaultProbe`, `Shop.DS_Info_Line`, `Shop.SUB_Checkout_Pickup`, `Shop.SUB_Config_Back`, `Shop.SUB_Config_Qty`, `Shop.SUB_Configure_Edit`, `Shop.SUB_Coupon_Remove`, `Shop.SUB_Info_Add`, `Shop.SUB_Line_Remove`, `Shop.SUB_Menu_ClearSearch`, `Shop.SUB_Menu_ShowAll`, `Shop.SUB_Nav_Menu`, `Shop.SUB_Nav_Search`, `Shop.SUB_Nav_Track`, `Shop.SUB_Pay_Cancel`, `Shop.SUB_Toast_Close`, `Shop.SUB_Track_OpenView`, `Shop.SUB_Track_Token` | accepted: remaining gaps are UI-state actions (toast close, copy, receipt open), the opt-in fault probe and secondary navigation; logic with rules (pricing, coupons, line configuration) is covered by microflow tests | `gap:Shop` |

## How this was measured

- Microflow test results and per-test assertion counts come from `mxcli test --junit` (the `assertions` property), run by this command with `--run` or read from `--junit`.
- Static reach: the microflows each `.test.mdl`/`.test.md` test calls (`call microflow` and its setups), plus everything those call in turn through the catalog's `call` references.
- Runtime reach: with `--journeys`, every `Microflow <name>` span that starts inside a journey's time window counts as executed by that journey. This is measured, not estimated — the app was running with `run --local --trace-otlp` into the span collector.
- "Startup or scheduled" is the after-startup, before-shutdown and health-check microflows and every scheduled event's microflow, with what they call. Those run without a test and are not counted as gaps.
- The app is the project's own modules; Marketplace modules, `System` and `MxTest` are outside.

## What this does not cover

- Static reach overstates: a microflow that a test enters may have branches no test takes. "Reached" means entered, not exercised.
- Nanoflows and page logic are not counted. A page whose data source is a database query runs no microflow, so journeys cannot be seen to reach it through spans.
- Microflows called from Java actions are invisible to the call graph (ako/mxcli#1819), so static reach misses them; runtime reach does not.
- Entity event handlers a test triggers by committing are not followed statically.
- Journeys consume seed data. A run on a database earlier runs used can stop on its own precondition; the database state is stated above when the journey log records it.

