# Performance

Where time goes in the main journeys at production volume · GitPizza · generated 2026-11-19 10:22 · mxcli nightly-20261118-9d764483c

| | |
|---|---|
| steps measured | 11 |
| server time, all steps | 161914 ms |
| database time | 4254 ms — 17607 queries |
| plans dominated by JIT | 0 — of 0 |

## Summary

Measured on the 11 browser journeys after a fresh demo reset (seed: 46 orders, 25 products). Server time per window includes the background simulation clock (Shop.SIM_ClockRun sleeps 1.5 s per tick in its task queue), not guest-facing work: the guest-facing data sources run in 5–20 ms (SUB_Track_Fill about 13 ms per call).

## Journey steps

Median of the warm runs per step.

> **Warning:** The journey log does not say what data the run used. Record the seed (volume, date) with a `{"meta":true,"database":"…"}` line; without it the numbers cannot be compared.

| Journey / step | Runs | Browser ms | Server ms | DB ms | Queries | Note |
|---|---|---|---|---|---|---|
| J1 order, pay and track (example: Root Pizza + Binary BBQ, delivery, tip 15 %) / J1 order, pay and track (example: Root Pizza + Binary BBQ, delivery, tip 15 %) | 1 (1 warm) | 20039 | 20395 | 589 | 2611 |  |
| J2 coupon GITHUB_STUDENT on example B (Root Pizza M + Garlic Knot Loop) gives $26.58 / J2 coupon GITHUB_STUDENT on example B (Root Pizza M + Garlic Knot Loop) gives $26.58 | 1 (1 warm) | 17211 | 17345 | 596 | 2114 |  |
| J3 declined card VISA_0002, then retry with Apple Pay succeeds (scenario: Example B, G2) / J3 declined card VISA_0002, then retry with Apple Pay succeeds (scenario: Example B, G2) | 1 (1 warm) | 30555 | 28209 | 608 | 2633 |  |
| J4 order lookup rejects an unknown order without revealing which field was wrong / J4 order lookup rejects an unknown order without revealing which field was wrong | 1 (1 warm) | 5227 | 6322 | 68 | 359 |  |
| J5 unknown URL shows ERROR 404 // CRUST_NOT_FOUND with RETURN_TO_MAIN / J5 unknown URL shows ERROR 404 // CRUST_NOT_FOUND with RETURN_TO_MAIN | 1 (1 warm) | 2679 | 1929 | 29 | 125 |  |
| J6 connection loss shows the CONNECTION_LOST banner and blocks actions with a toast / J6 connection loss shows the CONNECTION_LOST banner and blocks actions with a toast | 1 (1 warm) | 16527 | 16869 | 235 | 1167 |  |
| J8 home: featured carousel pages and Configure opens the configurator / J8 home: featured carousel pages and Configure opens the configurator | 1 (1 warm) | 8264 | 8096 | 186 | 758 |  |
| J9 configure Inferno Payload Large + cherry tomatoes = $25.00, then cart quantity, remove and clear / J9 configure Inferno Payload Large + cherry tomatoes = $25.00, then cart quantity, remove and clear | 1 (1 warm) | 19776 | 20334 | 911 | 3178 |  |
| J10 menu grep and dietary filters (US-027, US-033) / J10 menu grep and dietary filters (US-027, US-033) | 1 (1 warm) | 12825 | 12688 | 389 | 1473 |  |
| J11 pickup removes fee and tip; rollback while QUEUED refunds (US-086, US-129) / J11 pickup removes fee and tip; rollback while QUEUED refunds (US-086, US-129) | 1 (1 warm) | 25535 | 24837 | 561 | 2719 |  |
| J7 phone: bottom navigation and menu cards render at 390 px / J7 phone: bottom navigation and menu cards render at 390 px | 1 (1 warm) | 3724 | 4889 | 83 | 470 |  |

## Step: J1 order, pay and track (example: Root Pizza + Binary BBQ, delivery, tip 15 %) / J1 order, pay and track (example: Root Pizza + Binary BBQ, delivery, tip 15 %)

**Microflows (inclusive time)**

| Microflow | Calls | ms |
|---|---|---|
| `Shop.SIM_ClockRun` | 13 | 20000 |
| `Shop.SIM_Tick` | 13 | 454 |
| `Shop.SUB_Track_Fill` | 13 | 166 |
| `Shop.SIM_Couriers` | 13 | 144 |
| `Shop.SUB_Line_Recalculate` | 15 | 135 |
| `Shop.DS_Track` | 8 | 131 |
| `Shop.ACT_Product_QuickAdd` | 2 | 107 |
| `Shop.SUB_Cart_Recalculate` | 5 | 106 |

**Statements, most frequent first**

| SQL (literals replaced) | Count | ms |
|---|---|---|
| `SELECT "shop$simulationsettings"."id", "shop$simulationsettings"."speedfactor", "shop$simulationsettings"."paymentprocessing", "shop$simulationsettings"."paymenttimeout", "shop$simulationsettings"."paymentfailedtimeout"…` | 442 | 70 |
| `SELECT "shop$category"."id", "shop$category"."code", "shop$category"."filename", "shop$category"."displayname", "shop$category"."kind", "shop$category"."sortorder", "shop$category"."mxobjectversion" FROM "shop$category"…` | 200 | 30 |
| `SELECT "atj1Shop$Ingredient_Allergen"."shop$ingredientid" AS "parent", "atj1Shop$Ingredient_Allergen"."shop$allergenid" AS "child" FROM "shop$ingredient_allergen" "atj1Shop$Ingredient_Allergen" WHERE "atj1Shop$Ingredien…` | 140 | 12 |
| `SELECT "shop$ingredient"."id", "shop$ingredient"."code", "shop$ingredient"."name", "shop$ingredient"."isvegetarian", "shop$ingredient"."isvegan", "shop$ingredient"."isinstock", "shop$ingredient"."sortorder", "shop$ingre…` | 139 | 17 |
| `SELECT "shop$option"."id", "shop$option"."code", "shop$option"."optionkey", "shop$option"."name", "shop$option"."description", "shop$option"."optiongroup", "shop$option"."priceclass", "shop$option"."surcharge", "shop$op…` | 129 | 9.7 |
| `SELECT "shop$order"."id", "shop$order"."ordernumber", "shop$order"."commithash", "shop$order"."trackingtoken", "shop$order"."source", "shop$order"."ordertype", "shop$order"."orderstatus", "shop$order"."statuschangedat",…` | 75 | 13 |
| `SELECT "shop$courier"."id", "shop$courier"."code", "shop$courier"."name", "shop$courier"."nodehandle", "shop$courier"."vehicle", "shop$courier"."plate", "shop$courier"."phone", "shop$courier"."courierstatus", "shop$cour…` | 67 | 7.1 |
| `SELECT "shop$order"."id", "shop$order"."ordernumber", "shop$order"."commithash", "shop$order"."trackingtoken", "shop$order"."source", "shop$order"."ordertype", "shop$order"."orderstatus", "shop$order"."statuschangedat",…` | 65 | 10 |

## Step: J2 coupon GITHUB_STUDENT on example B (Root Pizza M + Garlic Knot Loop) gives $26.58 / J2 coupon GITHUB_STUDENT on example B (Root Pizza M + Garlic Knot Loop) gives $26.58

**Microflows (inclusive time)**

| Microflow | Calls | ms |
|---|---|---|
| `Shop.SIM_ClockRun` | 11 | 16863 |
| `Shop.SIM_Tick` | 11 | 333 |
| `Shop.DS_Menu_Products` | 18 | 183 |
| `Shop.SIM_Couriers` | 11 | 149 |
| `Shop.SUB_Cart_Recalculate` | 5 | 95 |
| `Shop.SIM_Kitchen` | 11 | 93 |
| `Shop.ACT_Product_QuickAdd` | 2 | 75 |
| `Shop.SUB_Line_Recalculate` | 13 | 75 |

**Statements, most frequent first**

| SQL (literals replaced) | Count | ms |
|---|---|---|
| `SELECT "shop$category"."id", "shop$category"."code", "shop$category"."filename", "shop$category"."displayname", "shop$category"."kind", "shop$category"."sortorder", "shop$category"."mxobjectversion" FROM "shop$category"…` | 450 | 66 |
| `SELECT "shop$simulationsettings"."id", "shop$simulationsettings"."speedfactor", "shop$simulationsettings"."paymentprocessing", "shop$simulationsettings"."paymenttimeout", "shop$simulationsettings"."paymentfailedtimeout"…` | 228 | 33 |
| `SELECT "system$autocommitentry"."id", "system$autocommitentry"."sessionid", "system$autocommitentry"."objectid", "system$autocommitentry"."createddate", "system$autocommitentry"."mxobjectversion" FROM "system$autocommit…` | 79 | 44 |
| `SELECT "shop$courier"."id", "shop$courier"."code", "shop$courier"."name", "shop$courier"."nodehandle", "shop$courier"."vehicle", "shop$courier"."plate", "shop$courier"."phone", "shop$courier"."courierstatus", "shop$cour…` | 68 | 7.7 |
| `SELECT "shop$ingredient"."id", "shop$ingredient"."code", "shop$ingredient"."name", "shop$ingredient"."isvegetarian", "shop$ingredient"."isvegan", "shop$ingredient"."isinstock", "shop$ingredient"."sortorder", "shop$ingre…` | 56 | 12 |
| `SELECT "atj1Shop$Ingredient_Allergen"."shop$ingredientid" AS "parent", "atj1Shop$Ingredient_Allergen"."shop$allergenid" AS "child" FROM "shop$ingredient_allergen" "atj1Shop$Ingredient_Allergen" WHERE "atj1Shop$Ingredien…` | 56 | 5.6 |
| `SELECT "shop$order"."id", "shop$order"."ordernumber", "shop$order"."commithash", "shop$order"."trackingtoken", "shop$order"."source", "shop$order"."ordertype", "shop$order"."orderstatus", "shop$order"."statuschangedat",…` | 55 | 10 |
| `SELECT "shop$cart"."id", "shop$cart"."couponinput", "shop$cart"."couponstate", "shop$cart"."couponmessage", "shop$cart"."couponfielderror", "shop$cart"."itemcount", "shop$cart"."subtotal", "shop$cart"."discountpreview",…` | 52 | 43 |

## Step: J3 declined card VISA_0002, then retry with Apple Pay succeeds (scenario: Example B, G2) / J3 declined card VISA_0002, then retry with Apple Pay succeeds (scenario: Example B, G2)

**Microflows (inclusive time)**

| Microflow | Calls | ms |
|---|---|---|
| `Shop.SIM_ClockRun` | 18 | 27520 |
| `Shop.SIM_Tick` | 18 | 459 |
| `Shop.SUB_Track_Fill` | 21 | 249 |
| `Shop.SIM_Couriers` | 18 | 211 |
| `Shop.ACT_Pay_Refresh` | 9 | 151 |
| `Shop.SUB_Pay_Refresh` | 9 | 149 |
| `Shop.DS_Track` | 11 | 148 |
| `Shop.ACT_Track_Refresh` | 9 | 144 |

**Statements, most frequent first**

| SQL (literals replaced) | Count | ms |
|---|---|---|
| `SELECT "shop$simulationsettings"."id", "shop$simulationsettings"."speedfactor", "shop$simulationsettings"."paymentprocessing", "shop$simulationsettings"."paymenttimeout", "shop$simulationsettings"."paymentfailedtimeout"…` | 616 | 94 |
| `SELECT "shop$courier"."id", "shop$courier"."code", "shop$courier"."name", "shop$courier"."nodehandle", "shop$courier"."vehicle", "shop$courier"."plate", "shop$courier"."phone", "shop$courier"."courierstatus", "shop$cour…` | 126 | 13 |
| `SELECT "shop$category"."id", "shop$category"."code", "shop$category"."filename", "shop$category"."displayname", "shop$category"."kind", "shop$category"."sortorder", "shop$category"."mxobjectversion" FROM "shop$category"…` | 125 | 14 |
| `SELECT "shop$order"."id", "shop$order"."ordernumber", "shop$order"."commithash", "shop$order"."trackingtoken", "shop$order"."source", "shop$order"."ordertype", "shop$order"."orderstatus", "shop$order"."statuschangedat",…` | 114 | 19 |
| `SELECT "shop$order"."id", "shop$order"."ordernumber", "shop$order"."commithash", "shop$order"."trackingtoken", "shop$order"."source", "shop$order"."ordertype", "shop$order"."orderstatus", "shop$order"."statuschangedat",…` | 90 | 12 |
| `UPDATE "shop$courier" SET "tripprogresspercent" = ?,"mxobjectversion" = ("mxobjectversion" + ?) WHERE "mxobjectversion" = ? AND "id" = ?` | 72 | 9.6 |
| `SELECT "system$autocommitentry"."id", "system$autocommitentry"."sessionid", "system$autocommitentry"."objectid", "system$autocommitentry"."createddate", "system$autocommitentry"."mxobjectversion" FROM "system$autocommit…` | 66 | 21 |
| `(SELECT * FROM (SELECT "T"."id", "T"."sequence", "T"."status", "T"."queueid", "T"."queuename", "T"."contexttype", "T"."contextdata", "T"."microflowname", "T"."useractionname", "T"."arguments", "T"."xasid", "T"."threadid…` | 57 | 24 |

## Step: J4 order lookup rejects an unknown order without revealing which field was wrong / J4 order lookup rejects an unknown order without revealing which field was wrong

**Microflows (inclusive time)**

| Microflow | Calls | ms |
|---|---|---|
| `Shop.SIM_ClockRun` | 4 | 6124 |
| `Shop.SIM_Tick` | 4 | 114 |
| `Shop.SIM_Couriers` | 4 | 51 |
| `Shop.SIM_Kitchen` | 4 | 22 |
| `Shop.SUB_Order_Progress` | 22 | 20 |
| `Shop.SUB_Timer_Progress` | 34 | 15 |
| `Shop.SIM_Pickups` | 4 | 14 |
| `Shop.SIM_Payments` | 4 | 14 |

**Statements, most frequent first**

| SQL (literals replaced) | Count | ms |
|---|---|---|
| `SELECT "shop$simulationsettings"."id", "shop$simulationsettings"."speedfactor", "shop$simulationsettings"."paymentprocessing", "shop$simulationsettings"."paymenttimeout", "shop$simulationsettings"."paymentfailedtimeout"…` | 72 | 9.3 |
| `SELECT "shop$courier"."id", "shop$courier"."code", "shop$courier"."name", "shop$courier"."nodehandle", "shop$courier"."vehicle", "shop$courier"."plate", "shop$courier"."phone", "shop$courier"."courierstatus", "shop$cour…` | 28 | 3.0 |
| `SELECT "shop$order"."id", "shop$order"."ordernumber", "shop$order"."commithash", "shop$order"."trackingtoken", "shop$order"."source", "shop$order"."ordertype", "shop$order"."orderstatus", "shop$order"."statuschangedat",…` | 20 | 4.3 |
| `SELECT "shop$order"."id", "shop$order"."ordernumber", "shop$order"."commithash", "shop$order"."trackingtoken", "shop$order"."source", "shop$order"."ordertype", "shop$order"."orderstatus", "shop$order"."statuschangedat",…` | 16 | 2.2 |
| `UPDATE "shop$courier" SET "tripprogresspercent" = ?,"mxobjectversion" = ("mxobjectversion" + ?) WHERE "mxobjectversion" = ? AND "id" = ?` | 16 | 2.0 |
| `(SELECT * FROM (SELECT "T"."id", "T"."sequence", "T"."status", "T"."queueid", "T"."queuename", "T"."contexttype", "T"."contextdata", "T"."microflowname", "T"."useractionname", "T"."arguments", "T"."xasid", "T"."threadid…` | 11 | 5.0 |
| `SELECT "system$autocommitentry"."id", "system$autocommitentry"."sessionid", "system$autocommitentry"."objectid", "system$autocommitentry"."createddate", "system$autocommitentry"."mxobjectversion" FROM "system$autocommit…` | 8 | 1.1 |
| `SELECT "shop$cart"."id", "shop$cart"."couponinput", "shop$cart"."couponstate", "shop$cart"."couponmessage", "shop$cart"."couponfielderror", "shop$cart"."itemcount", "shop$cart"."subtotal", "shop$cart"."discountpreview",…` | 5 | 1.8 |

## Step: J5 unknown URL shows ERROR 404 // CRUST_NOT_FOUND with RETURN_TO_MAIN / J5 unknown URL shows ERROR 404 // CRUST_NOT_FOUND with RETURN_TO_MAIN

**Microflows (inclusive time)**

| Microflow | Calls | ms |
|---|---|---|
| `Shop.SIM_ClockRun` | 1 | 1535 |
| `Shop.SIM_Tick` | 1 | 29 |
| `Shop.SIM_Couriers` | 1 | 18 |
| `Shop.SIM_Kitchen` | 1 | 4.7 |
| `Shop.SUB_Order_Progress` | 5 | 4.1 |
| `Shop.DS_Shell_Cart` | 1 | 3.7 |
| `Shop.SUB_Timer_Progress` | 8 | 3.4 |
| `Shop.SUB_Eff` | 9 | 3.4 |

**Statements, most frequent first**

| SQL (literals replaced) | Count | ms |
|---|---|---|
| `SELECT "shop$simulationsettings"."id", "shop$simulationsettings"."speedfactor", "shop$simulationsettings"."paymentprocessing", "shop$simulationsettings"."paymenttimeout", "shop$simulationsettings"."paymentfailedtimeout"…` | 18 | 2.0 |
| `SELECT "shop$courier"."id", "shop$courier"."code", "shop$courier"."name", "shop$courier"."nodehandle", "shop$courier"."vehicle", "shop$courier"."plate", "shop$courier"."phone", "shop$courier"."courierstatus", "shop$cour…` | 7 | 0.7 |
| `SELECT "shop$order"."id", "shop$order"."ordernumber", "shop$order"."commithash", "shop$order"."trackingtoken", "shop$order"."source", "shop$order"."ordertype", "shop$order"."orderstatus", "shop$order"."statuschangedat",…` | 5 | 0.6 |
| `SELECT "shop$order"."id", "shop$order"."ordernumber", "shop$order"."commithash", "shop$order"."trackingtoken", "shop$order"."source", "shop$order"."ordertype", "shop$order"."orderstatus", "shop$order"."statuschangedat",…` | 5 | 0.5 |
| `(SELECT * FROM (SELECT "T"."id", "T"."sequence", "T"."status", "T"."queueid", "T"."queuename", "T"."contexttype", "T"."contextdata", "T"."microflowname", "T"."useractionname", "T"."arguments", "T"."xasid", "T"."threadid…` | 4 | 1.4 |
| `UPDATE "shop$courier" SET "tripprogresspercent" = ?,"mxobjectversion" = ("mxobjectversion" + ?) WHERE "mxobjectversion" = ? AND "id" = ?` | 4 | 0.5 |
| `SELECT "system$autocommitentry"."id", "system$autocommitentry"."sessionid", "system$autocommitentry"."objectid", "system$autocommitentry"."createddate", "system$autocommitentry"."mxobjectversion" FROM "system$autocommit…` | 3 | 0.4 |
| `UPDATE "shop$courier" SET "courierstatus" = ?,"statuschangedat" = ?,"tripprogress" = ?,"tripanchorat" = ?,"tripseconds" = ?,"tripprogresspercent" = ?,"shop$courier_currentorder" = ?,"mxobjectversion" = ("mxobjectversion…` | 2 | 0.8 |

## Step: J6 connection loss shows the CONNECTION_LOST banner and blocks actions with a toast / J6 connection loss shows the CONNECTION_LOST banner and blocks actions with a toast

**Microflows (inclusive time)**

| Microflow | Calls | ms |
|---|---|---|
| `Shop.SIM_ClockRun` | 11 | 16794 |
| `Shop.SIM_Tick` | 11 | 272 |
| `Shop.SIM_Couriers` | 11 | 128 |
| `Shop.DS_Menu_Products` | 8 | 70 |
| `Shop.SIM_Kitchen` | 11 | 69 |
| `Shop.SUB_Order_Progress` | 55 | 51 |
| `Shop.SUB_Timer_Progress` | 88 | 40 |
| `Shop.SUB_Eff` | 89 | 36 |

**Statements, most frequent first**

| SQL (literals replaced) | Count | ms |
|---|---|---|
| `SELECT "shop$category"."id", "shop$category"."code", "shop$category"."filename", "shop$category"."displayname", "shop$category"."kind", "shop$category"."sortorder", "shop$category"."mxobjectversion" FROM "shop$category"…` | 200 | 23 |
| `SELECT "shop$simulationsettings"."id", "shop$simulationsettings"."speedfactor", "shop$simulationsettings"."paymentprocessing", "shop$simulationsettings"."paymenttimeout", "shop$simulationsettings"."paymentfailedtimeout"…` | 189 | 23 |
| `SELECT "shop$courier"."id", "shop$courier"."code", "shop$courier"."name", "shop$courier"."nodehandle", "shop$courier"."vehicle", "shop$courier"."plate", "shop$courier"."phone", "shop$courier"."courierstatus", "shop$cour…` | 66 | 8.5 |
| `SELECT "shop$order"."id", "shop$order"."ordernumber", "shop$order"."commithash", "shop$order"."trackingtoken", "shop$order"."source", "shop$order"."ordertype", "shop$order"."orderstatus", "shop$order"."statuschangedat",…` | 55 | 7.6 |
| `SELECT "shop$order"."id", "shop$order"."ordernumber", "shop$order"."commithash", "shop$order"."trackingtoken", "shop$order"."source", "shop$order"."ordertype", "shop$order"."orderstatus", "shop$order"."statuschangedat",…` | 44 | 7.3 |
| `UPDATE "shop$courier" SET "tripprogresspercent" = ?,"mxobjectversion" = ("mxobjectversion" + ?) WHERE "mxobjectversion" = ? AND "id" = ?` | 44 | 6.3 |
| `(SELECT * FROM (SELECT "T"."id", "T"."sequence", "T"."status", "T"."queueid", "T"."queuename", "T"."contexttype", "T"."contextdata", "T"."microflowname", "T"."useractionname", "T"."arguments", "T"."xasid", "T"."threadid…` | 34 | 17 |
| `SELECT "system$autocommitentry"."id", "system$autocommitentry"."sessionid", "system$autocommitentry"."objectid", "system$autocommitentry"."createddate", "system$autocommitentry"."mxobjectversion" FROM "system$autocommit…` | 31 | 12 |

## Step: J8 home: featured carousel pages and Configure opens the configurator / J8 home: featured carousel pages and Configure opens the configurator

**Microflows (inclusive time)**

| Microflow | Calls | ms |
|---|---|---|
| `Shop.SIM_ClockRun` | 5 | 7654 |
| `Shop.SIM_Tick` | 5 | 113 |
| `Shop.DS_Config_Choices` | 7 | 94 |
| `Shop.SIM_Couriers` | 5 | 58 |
| `Shop.SUB_Home_Refresh` | 3 | 37 |
| `Shop.ACT_Configure_FromHome` | 1 | 32 |
| `Shop.SUB_Option_AvailableFor` | 43 | 32 |
| `Shop.SUB_Configure_FromHome` | 1 | 31 |

**Statements, most frequent first**

| SQL (literals replaced) | Count | ms |
|---|---|---|
| `SELECT "shop$simulationsettings"."id", "shop$simulationsettings"."speedfactor", "shop$simulationsettings"."paymentprocessing", "shop$simulationsettings"."paymenttimeout", "shop$simulationsettings"."paymentfailedtimeout"…` | 85 | 9.2 |
| `SELECT "atj1Shop$Ingredient_Allergen"."shop$ingredientid" AS "parent", "atj1Shop$Ingredient_Allergen"."shop$allergenid" AS "child" FROM "shop$ingredient_allergen" "atj1Shop$Ingredient_Allergen" WHERE "atj1Shop$Ingredien…` | 63 | 13 |
| `SELECT "shop$ingredient"."id", "shop$ingredient"."code", "shop$ingredient"."name", "shop$ingredient"."isvegetarian", "shop$ingredient"."isvegan", "shop$ingredient"."isinstock", "shop$ingredient"."sortorder", "shop$ingre…` | 63 | 10 |
| `SELECT "shop$option"."id", "shop$option"."code", "shop$option"."optionkey", "shop$option"."name", "shop$option"."description", "shop$option"."optiongroup", "shop$option"."priceclass", "shop$option"."surcharge", "shop$op…` | 33 | 5.9 |
| `SELECT "shop$courier"."id", "shop$courier"."code", "shop$courier"."name", "shop$courier"."nodehandle", "shop$courier"."vehicle", "shop$courier"."plate", "shop$courier"."phone", "shop$courier"."courierstatus", "shop$cour…` | 30 | 3.7 |
| `SELECT "shop$order"."id", "shop$order"."ordernumber", "shop$order"."commithash", "shop$order"."trackingtoken", "shop$order"."source", "shop$order"."ordertype", "shop$order"."orderstatus", "shop$order"."statuschangedat",…` | 25 | 4.0 |
| `SELECT "atj2Shop$CartLine_Extra"."shop$cartlineid" AS "parent", "atj2Shop$CartLine_Extra"."shop$optionid" AS "child" FROM "shop$cartline_extra" "atj2Shop$CartLine_Extra" WHERE "atj2Shop$CartLine_Extra"."shop$cartlineid"…` | 20 | 10 |
| `SELECT "atj1Shop$CartLine_Allergen"."shop$cartlineid" AS "parent", "atj1Shop$CartLine_Allergen"."shop$allergenid" AS "child" FROM "shop$cartline_allergen" "atj1Shop$CartLine_Allergen" WHERE "atj1Shop$CartLine_Allergen".…` | 20 | 7.8 |

## Step: J9 configure Inferno Payload Large + cherry tomatoes = $25.00, then cart quantity, remove and clear / J9 configure Inferno Payload Large + cherry tomatoes = $25.00, then cart quantity, remove and clear

**Microflows (inclusive time)**

| Microflow | Calls | ms |
|---|---|---|
| `Shop.SIM_ClockRun` | 13 | 19828 |
| `Shop.DS_Config_Choices` | 21 | 486 |
| `Shop.SIM_Tick` | 13 | 308 |
| `Shop.DS_Menu_Products` | 20 | 247 |
| `Shop.SIM_Couriers` | 13 | 166 |
| `Shop.SUB_Option_AvailableFor` | 159 | 150 |
| `Shop.SUB_Line_Recalculate` | 10 | 104 |
| `Shop.SUB_Cart_Recalculate` | 5 | 64 |

**Statements, most frequent first**

| SQL (literals replaced) | Count | ms |
|---|---|---|
| `SELECT "shop$category"."id", "shop$category"."code", "shop$category"."filename", "shop$category"."displayname", "shop$category"."kind", "shop$category"."sortorder", "shop$category"."mxobjectversion" FROM "shop$category"…` | 500 | 87 |
| `SELECT "atj1Shop$Ingredient_Allergen"."shop$ingredientid" AS "parent", "atj1Shop$Ingredient_Allergen"."shop$allergenid" AS "child" FROM "shop$ingredient_allergen" "atj1Shop$Ingredient_Allergen" WHERE "atj1Shop$Ingredien…` | 299 | 64 |
| `SELECT "shop$ingredient"."id", "shop$ingredient"."code", "shop$ingredient"."name", "shop$ingredient"."isvegetarian", "shop$ingredient"."isvegan", "shop$ingredient"."isinstock", "shop$ingredient"."sortorder", "shop$ingre…` | 298 | 105 |
| `SELECT "shop$simulationsettings"."id", "shop$simulationsettings"."speedfactor", "shop$simulationsettings"."paymentprocessing", "shop$simulationsettings"."paymenttimeout", "shop$simulationsettings"."paymentfailedtimeout"…` | 229 | 29 |
| `SELECT "shop$option"."id", "shop$option"."code", "shop$option"."optionkey", "shop$option"."name", "shop$option"."description", "shop$option"."optiongroup", "shop$option"."priceclass", "shop$option"."surcharge", "shop$op…` | 155 | 32 |
| `SELECT "system$autocommitentry"."id", "system$autocommitentry"."sessionid", "system$autocommitentry"."objectid", "system$autocommitentry"."createddate", "system$autocommitentry"."mxobjectversion" FROM "system$autocommit…` | 98 | 52 |
| `SELECT "atj1Shop$CartLine_Allergen"."shop$cartlineid" AS "parent", "atj1Shop$CartLine_Allergen"."shop$allergenid" AS "child" FROM "shop$cartline_allergen" "atj1Shop$CartLine_Allergen" WHERE "atj1Shop$CartLine_Allergen".…` | 76 | 34 |
| `SELECT "atj2Shop$CartLine_Extra"."shop$cartlineid" AS "parent", "atj2Shop$CartLine_Extra"."shop$optionid" AS "child" FROM "shop$cartline_extra" "atj2Shop$CartLine_Extra" WHERE "atj2Shop$CartLine_Extra"."shop$cartlineid"…` | 76 | 31 |

## Step: J10 menu grep and dietary filters (US-027, US-033) / J10 menu grep and dietary filters (US-027, US-033)

**Microflows (inclusive time)**

| Microflow | Calls | ms |
|---|---|---|
| `Shop.SIM_ClockRun` | 8 | 12178 |
| `Shop.SIM_Tick` | 8 | 165 |
| `Shop.DS_Menu_Products` | 22 | 156 |
| `Shop.SIM_Couriers` | 8 | 76 |
| `Shop.SUB_Menu_Refresh` | 5 | 46 |
| `Shop.SIM_Kitchen` | 8 | 45 |
| `Shop.SUB_Order_Progress` | 48 | 33 |
| `Shop.ACT_Menu_Filter` | 2 | 21 |

**Statements, most frequent first**

| SQL (literals replaced) | Count | ms |
|---|---|---|
| `SELECT "shop$category"."id", "shop$category"."code", "shop$category"."filename", "shop$category"."displayname", "shop$category"."kind", "shop$category"."sortorder", "shop$category"."mxobjectversion" FROM "shop$category"…` | 450 | 48 |
| `SELECT "shop$simulationsettings"."id", "shop$simulationsettings"."speedfactor", "shop$simulationsettings"."paymentprocessing", "shop$simulationsettings"."paymenttimeout", "shop$simulationsettings"."paymentfailedtimeout"…` | 145 | 18 |
| `SELECT "system$autocommitentry"."id", "system$autocommitentry"."sessionid", "system$autocommitentry"."objectid", "system$autocommitentry"."createddate", "system$autocommitentry"."mxobjectversion" FROM "system$autocommit…` | 72 | 40 |
| `SELECT "shop$cart"."id", "shop$cart"."couponinput", "shop$cart"."couponstate", "shop$cart"."couponmessage", "shop$cart"."couponfielderror", "shop$cart"."itemcount", "shop$cart"."subtotal", "shop$cart"."discountpreview",…` | 41 | 13 |
| `SELECT "shop$order"."id", "shop$order"."ordernumber", "shop$order"."commithash", "shop$order"."trackingtoken", "shop$order"."source", "shop$order"."ordertype", "shop$order"."orderstatus", "shop$order"."statuschangedat",…` | 40 | 6.5 |
| `SELECT "shop$courier"."id", "shop$courier"."code", "shop$courier"."name", "shop$courier"."nodehandle", "shop$courier"."vehicle", "shop$courier"."plate", "shop$courier"."phone", "shop$courier"."courierstatus", "shop$cour…` | 40 | 3.7 |
| `SELECT "shop$product"."id", "shop$product"."code", "shop$product"."name", "shop$product"."modulekey", "shop$product"."realworldname", "shop$product"."shortdescription", "shop$product"."description", "shop$product"."vers…` | 33 | 42 |
| `SELECT "shop$recipeitem"."id", "shop$recipeitem"."role", "shop$recipeitem"."isremovable", "shop$recipeitem"."sortorder", "shop$recipeitem"."mxobjectversion", "shop$recipeitem"."shop$recipeitem_ingredient", "shop$recipei…` | 33 | 28 |

## Step: J11 pickup removes fee and tip; rollback while QUEUED refunds (US-086, US-129) / J11 pickup removes fee and tip; rollback while QUEUED refunds (US-086, US-129)

**Microflows (inclusive time)**

| Microflow | Calls | ms |
|---|---|---|
| `Shop.SIM_ClockRun` | 16 | 24533 |
| `Shop.SIM_Tick` | 16 | 494 |
| `Shop.SUB_Track_Fill` | 18 | 177 |
| `Shop.SIM_Couriers` | 16 | 173 |
| `Shop.DS_Track` | 10 | 117 |
| `Shop.SUB_Order_Progress` | 135 | 106 |
| `Shop.SIM_Traffic` | 16 | 104 |
| `Shop.SIM_Kitchen` | 16 | 102 |

**Statements, most frequent first**

| SQL (literals replaced) | Count | ms |
|---|---|---|
| `SELECT "shop$simulationsettings"."id", "shop$simulationsettings"."speedfactor", "shop$simulationsettings"."paymentprocessing", "shop$simulationsettings"."paymenttimeout", "shop$simulationsettings"."paymentfailedtimeout"…` | 534 | 73 |
| `SELECT "shop$category"."id", "shop$category"."code", "shop$category"."filename", "shop$category"."displayname", "shop$category"."kind", "shop$category"."sortorder", "shop$category"."mxobjectversion" FROM "shop$category"…` | 125 | 17 |
| `SELECT "atj1Shop$Ingredient_Allergen"."shop$ingredientid" AS "parent", "atj1Shop$Ingredient_Allergen"."shop$allergenid" AS "child" FROM "shop$ingredient_allergen" "atj1Shop$Ingredient_Allergen" WHERE "atj1Shop$Ingredien…` | 108 | 11 |
| `SELECT "shop$ingredient"."id", "shop$ingredient"."code", "shop$ingredient"."name", "shop$ingredient"."isvegetarian", "shop$ingredient"."isvegan", "shop$ingredient"."isinstock", "shop$ingredient"."sortorder", "shop$ingre…` | 108 | 8.4 |
| `SELECT "shop$option"."id", "shop$option"."code", "shop$option"."optionkey", "shop$option"."name", "shop$option"."description", "shop$option"."optiongroup", "shop$option"."priceclass", "shop$option"."surcharge", "shop$op…` | 96 | 13 |
| `SELECT "shop$order"."id", "shop$order"."ordernumber", "shop$order"."commithash", "shop$order"."trackingtoken", "shop$order"."source", "shop$order"."ordertype", "shop$order"."orderstatus", "shop$order"."statuschangedat",…` | 94 | 14 |
| `SELECT "shop$courier"."id", "shop$courier"."code", "shop$courier"."name", "shop$courier"."nodehandle", "shop$courier"."vehicle", "shop$courier"."plate", "shop$courier"."phone", "shop$courier"."courierstatus", "shop$cour…` | 84 | 7.2 |
| `SELECT "shop$order"."id", "shop$order"."ordernumber", "shop$order"."commithash", "shop$order"."trackingtoken", "shop$order"."source", "shop$order"."ordertype", "shop$order"."orderstatus", "shop$order"."statuschangedat",…` | 80 | 10 |

## Step: J7 phone: bottom navigation and menu cards render at 390 px / J7 phone: bottom navigation and menu cards render at 390 px

**Microflows (inclusive time)**

| Microflow | Calls | ms |
|---|---|---|
| `Shop.SIM_ClockRun` | 3 | 4571 |
| `Shop.SIM_Tick` | 3 | 65 |
| `Shop.SIM_Couriers` | 3 | 39 |
| `Shop.DS_Menu_Products` | 4 | 29 |
| `Shop.DS_Shell_Cart` | 3 | 15 |
| `Shop.SUB_Cart_Current` | 4 | 14 |
| `Shop.SUB_Order_Progress` | 18 | 13 |
| `Shop.DS_Menu` | 1 | 10 |

**Statements, most frequent first**

| SQL (literals replaced) | Count | ms |
|---|---|---|
| `SELECT "shop$category"."id", "shop$category"."code", "shop$category"."filename", "shop$category"."displayname", "shop$category"."kind", "shop$category"."sortorder", "shop$category"."mxobjectversion" FROM "shop$category"…` | 100 | 9.4 |
| `SELECT "shop$simulationsettings"."id", "shop$simulationsettings"."speedfactor", "shop$simulationsettings"."paymentprocessing", "shop$simulationsettings"."paymenttimeout", "shop$simulationsettings"."paymentfailedtimeout"…` | 51 | 5.8 |
| `SELECT "system$autocommitentry"."id", "system$autocommitentry"."sessionid", "system$autocommitentry"."objectid", "system$autocommitentry"."createddate", "system$autocommitentry"."mxobjectversion" FROM "system$autocommit…` | 23 | 4.6 |
| `SELECT "shop$courier"."id", "shop$courier"."code", "shop$courier"."name", "shop$courier"."nodehandle", "shop$courier"."vehicle", "shop$courier"."plate", "shop$courier"."phone", "shop$courier"."courierstatus", "shop$cour…` | 21 | 1.8 |
| `SELECT "shop$order"."id", "shop$order"."ordernumber", "shop$order"."commithash", "shop$order"."trackingtoken", "shop$order"."source", "shop$order"."ordertype", "shop$order"."orderstatus", "shop$order"."statuschangedat",…` | 15 | 1.6 |
| `SELECT "shop$ingredient"."id", "shop$ingredient"."code", "shop$ingredient"."name", "shop$ingredient"."isvegetarian", "shop$ingredient"."isvegan", "shop$ingredient"."isinstock", "shop$ingredient"."sortorder", "shop$ingre…` | 12 | 5.3 |
| `SELECT "shop$recipeitem"."id", "shop$recipeitem"."role", "shop$recipeitem"."isremovable", "shop$recipeitem"."sortorder", "shop$recipeitem"."mxobjectversion", "shop$recipeitem"."shop$recipeitem_ingredient", "shop$recipei…` | 12 | 4.6 |
| `SELECT "shop$product"."id", "shop$product"."code", "shop$product"."name", "shop$product"."modulekey", "shop$product"."realworldname", "shop$product"."shortdescription", "shop$product"."description", "shop$product"."vers…` | 12 | 4.1 |

## Query plans

No plans were given (`--plans <postgres log>` with auto_explain in JSON format).

_(none)_

## N+1 candidates in the model

Two N+1 shapes no index fixes, found in the model. Annotate `candidate:<Microflow>`.

| Shape | Where | Detail | Verdict |
|---|---|---|---|
| retrieve in loop | `Shop.DS_Config_Choices` | association retrieve of an entity inside a loop (depth 1): one query per iteration — about five per row by association, counting access checks | accepted: loops over the options of one pizza (at most ~30): bounded |
| retrieve in loop | `Shop.DS_Config_Choices` | association retrieve of an entity inside a loop (depth 1): one query per iteration — about five per row by association, counting access checks | accepted: loops over the options of one pizza (at most ~30): bounded |
| retrieve in loop | `Shop.SIM_Couriers` | association retrieve of an entity inside a loop (depth 1): one query per iteration — about five per row by association, counting access checks | accepted: background simulation over 5 couriers |
| retrieve in loop | `Shop.SIM_Couriers` | database retrieve of Shop.Courier inside a loop (depth 1): one query per iteration — about five per row by association, counting access checks | accepted: background simulation over 5 couriers |
| retrieve in loop | `Shop.SIM_Kitchen` | association retrieve of an entity inside a loop (depth 1): one query per iteration — about five per row by association, counting access checks | fixed: simulation settings and the bake timer are read once before the queue loop |
| retrieve in loop | `Shop.SIM_Kitchen` | database retrieve of Shop.SimulationSettings inside a loop (depth 1): one query per iteration — about five per row by association, counting access checks | fixed: simulation settings and the bake timer are read once before the queue loop |
| retrieve in loop | `Shop.SUB_Cart_Recalculate` | association retrieve of an entity inside a loop (depth 1): one query per iteration — about five per row by association, counting access checks | accepted: loops over cart lines, max 30 items per cart (BR-CART-03) |
| retrieve in loop | `Shop.SUB_Line_Recalculate` | association retrieve of an entity inside a loop (depth 1): one query per iteration — about five per row by association, counting access checks | accepted: loops over the chosen options and recipe of one line: bounded |
| retrieve in loop | `Shop.SUB_Line_Recalculate` | association retrieve of an entity inside a loop (depth 1): one query per iteration — about five per row by association, counting access checks | accepted: loops over the chosen options and recipe of one line: bounded |
| retrieve in loop | `Shop.SUB_Line_Recalculate` | association retrieve of an entity inside a loop (depth 1): one query per iteration — about five per row by association, counting access checks | accepted: loops over the chosen options and recipe of one line: bounded |
| retrieve in loop | `Shop.SUB_Line_Recalculate` | association retrieve of an entity inside a loop (depth 1): one query per iteration — about five per row by association, counting access checks | accepted: loops over the chosen options and recipe of one line: bounded |
| retrieve in loop | `Shop.SUB_Order_Place` | association retrieve of an entity inside a loop (depth 1): one query per iteration — about five per row by association, counting access checks | accepted: snapshot of the cart lines once per order (max 30) |
| retrieve in loop | `Shop.SUB_Order_Place` | association retrieve of an entity inside a loop (depth 1): one query per iteration — about five per row by association, counting access checks | accepted: snapshot of the cart lines once per order (max 30) |
| retrieve in loop | `Shop.SUB_Order_Place` | association retrieve of an entity inside a loop (depth 1): one query per iteration — about five per row by association, counting access checks | accepted: snapshot of the cart lines once per order (max 30) |
| retrieve in loop | `Shop.SUB_Oven_FirstFree` | database retrieve of Shop.Order inside a loop (depth 1): one query per iteration — about five per row by association, counting access checks | accepted: background simulation over 3 ovens |
| retrieve in loop | `Shop.SUB_Product_Recalculate` | association retrieve of an entity inside a loop (depth 1): one query per iteration — about five per row by association, counting access checks |  |
| retrieve in loop | `Shop.SUB_Toast_Broadcast` | association retrieve of an entity inside a loop (depth 1): one query per iteration — about five per row by association, counting access checks |  |

## Recommendations

- Before real volume: give the simulation its own scheduled cadence instead of a 1.5 s self-requeueing task, or switch it off outside demos.

## How this was measured

- Each journey step is the time window its journey log record gives: from the action until its last `/xas/` request answered and nothing new started for a short quiet period (the journey script decides). Every span that starts inside the window belongs to the step.
- Browser time is the record's `browserMs` (or the window length). Server time is the union of the step's root spans — concurrent requests are not counted twice. Database time and query count are the database spans (`db.system` / `db.statement`) in the window.
- Each step ran several times; the first run warms caches and the JIT and is not counted. Figures are the median of the warm runs; the flame chart and statements are from the run closest to the median.
- Plans come from Postgres `auto_explain` in JSON format (`--plans <postgres log>`), with the JIT block reported next to the plan.
- Before/after compares against `--baseline`, an earlier performance report of the same journeys on the same seed.

## What this does not cover

- Results are only as representative as the seed: volume, distribution and dates. Seed dates relative to today — a seed dated from a fixed day made a "revertible" list about 120× too long and led to a wrong conclusion until checked.
- A fair before/after needs the committed model as the "before", on the same seed: revert the change, restart and measure, rather than reuse an older run.
- Access rules steer plans: an index on a status column can go unused because the access-rule subquery drives from an association, and a Mendix index cannot include an association. Such a finding needs a model change, not another index.
- Spans show the runtime's work, not the browser's rendering; the difference between browser and server time is network and client.
- Static N+1 candidates are shapes, not measurements: confirm each in a step's query count before changing it.

