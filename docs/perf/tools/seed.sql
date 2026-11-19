-- Volume seed for the performance report: one year of a busy Git Pizza store.
--   psql -h 127.0.0.1 -U mendix -d gitpizza -f docs/perf/tools/seed.sql     (app stopped; back up first)
--
-- Direct SQL per the demo-data / report-performance skills: id = short_id << 48 | seq << 7 | (seq % 128),
-- every seeded seq is >= 10,000,000 so it cannot meet a sequence the runtime hands out; the
-- entities' object_sequence is moved past the seeded range at the end. Dates are relative to now().
--
-- Shape (about 10M rows):
--   400,000 guest orders over the past 365 days (~1,100 a day, so about as many today), all finished:
--     delivered 60 %, picked up 33 %, cancelled 7 %; 1-4 lines each, modifiers on pizza lines;
--     6 status changes, 8 log lines, 1-2 payment attempts, 1 session grant each; 2 simulation events
--     for the last 24 h only (housekeeping's steady state; docs/perf/tools/backlog.sql adds a year's backlog)
--   150,000 abandoned guest carts from the past 90 days with 2 lines each (their sessions are gone)
--   200,000 expired toasts and 50,000 lookup attempts
-- Simulated (SIMULATOR) orders are not seeded: housekeeping deletes finished ones after 24 h (A-16).
-- One order is known for the lookup step: MX-200000 with perf.lookup@example.com.
\set ON_ERROR_STOP on
\timing on
set synchronous_commit = off;

create temp table sid as
select e.entity_name as n, ei.short_id::bigint as s
from mendixsystem$entityidentifier ei join mendixsystem$entity e on e.id = ei.id;
create or replace function pg_temp.s(n text) returns bigint language sql stable as $$ select s from sid where sid.n = $1 $$;
create or replace function pg_temp.mkid(short bigint, seq bigint) returns bigint language sql immutable
  as $$ select (short << 48) | (seq << 7) | (seq % 128) $$;

create temp table p as select 10000000::bigint as base, 400000 as n_ord, 150000 as n_cart, now()::timestamp as t0;

-- products with their default (or first) size price
create temp table prod as
select row_number() over (order by p.code) - 1 as i, p.id, p.code, p.name, p.kind, p.modulekey,
  coalesce((select s.price from "catalog$productsize" s where s."catalog$productsize_product" = p.id order by s.isdefault desc, s.sortorder limit 1), 4.99) as price,
  (select s.id from "catalog$productsize" s where s."catalog$productsize_product" = p.id order by s.isdefault desc, s.sortorder limit 1) as size_id
from "catalog$product" p;
create temp table zone as select row_number() over (order by zip) - 1 as i, id, zip from "fulfilment$deliveryzone";
create temp table oven as select row_number() over (order by code) - 1 as i, id from "fulfilment$oven";
create temp table cour as select row_number() over (order by code) - 1 as i, id from "fulfilment$courier" where code <> 'CU-05';

-- ---------------------------------------------------------------- orders
create temp table o as
select g, pg_temp.mkid(pg_temp.s('Fulfilment.Order'), (select base from p) + g) as id,
  100000 + g as nr,
  case when g % 100 < 60 then 'DELIVERY' else 'PICKUP' end as otype,
  case when g % 100 >= 93 then 'CANCELLED' when g % 100 < 60 then 'DELIVERED' else 'PICKED_UP' end as st,
  1 + (g % 4) as n_lines,
  (select t0 from p) - ((g % 365) || ' days')::interval - (((g * 7919) % 43200) || ' seconds')::interval - interval '10 minutes' as placed
from generate_series(1::bigint, (select n_ord from p)) g;
alter table o add primary key (g);

insert into "fulfilment$order" (id, ordernumber, commithash, trackingtoken, source, ordertype, orderstatus, statuschangedat,
  payment, contactname, contactemail, contactphone, addressline1, addressline2, city, statecode, zip, deliverynotes,
  distancemiles, couponcode, subtotal, discountamount, deliveryfee, taxratepercent, taxamount, tip, tipamount, total,
  placedat, paidat, queuedat, bakingstartedat, qastartedat, readyat, dispatchedat, completedat, cancelledat,
  routeprogresspercent, timerprogress, timeranchorat, isqasliceddone, isqaextrasdone, isqasealeddone, remakecount,
  ispriority, cancelreason, cancelledby, pizzacount, itemcount, isopen, paymentlabel,
  "fulfilment$order_oven", "fulfilment$order_courier", "fulfilment$order_zone", mxobjectversion)
select o.id, o.nr, substr(md5('c' || o.g), 1, 7), md5('t' || o.g) || substr(md5('u' || o.g), 1, 8), 'GUEST', o.otype, o.st,
  o.placed + interval '25 minutes',
  case when o.st = 'CANCELLED' then 'REFUNDED' else 'PAID' end,
  case when o.g = 100000 then 'Perf Lookup' else (array['Sam Rivera','Jordan Lee','Alex Kim','Priya Shah','Chris Doe','Maria Lopez'])[1 + o.g % 6] end,
  case when o.g = 100000 then 'perf.lookup@example.com' else 'guest' || (o.g % 60000) || '@example.com' end,
  '(415) 555-' || lpad((o.g % 10000)::text, 4, '0'),
  case when o.otype = 'DELIVERY' then (o.g % 900 + 10) || ' Mission Street' else '' end, '', 'San Francisco', 'CA',
  case when o.otype = 'DELIVERY' then z.zip else '' end, '',
  case when o.otype = 'DELIVERY' then 1 + (o.g % 30) / 10.0 else 0 end, '',
  20 + (o.g % 40), 0, case when o.otype = 'DELIVERY' and 20 + (o.g % 40) < 40 then 3.99 else 0 end,
  8.625, round((20 + (o.g % 40)) * 0.08625, 2),
  case when o.otype = 'DELIVERY' then 'FIFTEEN' else 'NONE' end,
  case when o.otype = 'DELIVERY' then round((20 + (o.g % 40)) * 0.15, 2) else 0 end,
  round((20 + (o.g % 40)) * 1.08625 + case when o.otype = 'DELIVERY' then (20 + (o.g % 40)) * 0.15 + 3.99 else 0 end, 2),
  o.placed, o.placed + interval '3 seconds', o.placed + interval '3 seconds',
  case when o.st <> 'CANCELLED' then o.placed + interval '4 minutes' end,
  case when o.st <> 'CANCELLED' then o.placed + interval '10 minutes' end,
  case when o.st <> 'CANCELLED' then o.placed + interval '12 minutes' end,
  case when o.st = 'DELIVERED' then o.placed + interval '14 minutes' end,
  case when o.st <> 'CANCELLED' then o.placed + interval '25 minutes' end,
  case when o.st = 'CANCELLED' then o.placed + interval '2 minutes' end,
  case when o.st = 'DELIVERED' then 100 else 0 end, 0, o.placed + interval '25 minutes',
  o.st <> 'CANCELLED', o.st <> 'CANCELLED', o.st <> 'CANCELLED', 0, false,
  case when o.st = 'CANCELLED' then 'Cancelled by the guest' end, case when o.st = 'CANCELLED' then 'GUEST' end,
  greatest(1, o.n_lines - 1), o.n_lines, false, 'Visa •••• 4242',
  case when o.st <> 'CANCELLED' then (select id from oven where i = o.g % 2) end,
  case when o.st = 'DELIVERED' then (select id from cour where i = o.g % 4) end,
  case when o.otype = 'DELIVERY' then z.id end, 1
from o join zone z on z.i = o.g % (select count(*) from zone);

-- ---------------------------------------------------------------- lines and modifiers
create temp table l as
select row_number() over (order by o.g, k) as g, o.g as og, o.id as oid, k, pr.*
from o cross join lateral generate_series(1, o.n_lines) k
join prod pr on pr.i = (o.g * 3 + k * 7) % (select count(*) from prod);
insert into "fulfilment$orderline" (id, productcode, productname, realworldname, modulekey, kind, size, sizelabel, quantity,
  unitprice, linetotal, allergentext, isvegetarian, isvegan, configtext, sortorder, "fulfilment$orderline_order",
  "fulfilment$orderline_product", mxobjectversion)
select pg_temp.mkid(pg_temp.s('Fulfilment.OrderLine'), (select base from p) + l.g), l.code, l.name, l.name, l.modulekey, l.kind,
  case when l.kind = 'PIZZA' then 'MEDIUM' else 'REGULAR' end, case when l.kind = 'PIZZA' then 'Medium 12"' else 'Regular' end,
  1, l.price, l.price, 'Cereals containing gluten, Milk', l.og % 3 = 0, false, '', l.k, l.oid, l.id, 1
from l;

insert into "fulfilment$orderlinemodifier" (id, modifiertype, optionkey, name, price, isdefault, sortorder,
  "fulfilment$orderlinemodifier_orderline", mxobjectversion)
select pg_temp.mkid(pg_temp.s('Fulfilment.OrderLineModifier'), (select base from p) + l.g * 2 + m),
  (array['CRUST','SAUCE'])[m + 1], (array['CR-01','SA-01'])[m + 1], (array['Classic crust','Tomato sauce'])[m + 1], 0, true, m + 1,
  pg_temp.mkid(pg_temp.s('Fulfilment.OrderLine'), (select base from p) + l.g), 1
from l cross join generate_series(0, 1) m where l.kind = 'PIZZA';

-- ---------------------------------------------------------------- history: status changes, log, payments, events, access
insert into "fulfilment$orderstatuschange" (id, fromstatus, tostatus, changedat, actor, actorname, reason, seq,
  "fulfilment$orderstatuschange_order", mxobjectversion)
select pg_temp.mkid(pg_temp.s('Fulfilment.OrderStatusChange'), (select base from p) + o.g * 8 + k),
  (array['NEW','PAYMENT_PENDING','QUEUED','BAKING','QA_CHECK','READY_FOR_DISPATCH'])[k],
  (array['PAYMENT_PENDING','QUEUED','BAKING','QA_CHECK','READY_FOR_DISPATCH', o.st])[k],
  o.placed + (k * 4 || ' minutes')::interval, case when k <= 2 then 'GUEST' else 'SIMULATOR' end,
  case when k <= 2 then 'guest' else 'sim/kitchen-auto' end, '', k, o.id, 1
from o cross join generate_series(1, 6) k;

insert into "fulfilment$orderlogentry" (id, loggedat, level, tag, message, iscustomervisible, seq,
  "fulfilment$orderlogentry_order", mxobjectversion, timetext)
select pg_temp.mkid(pg_temp.s('Fulfilment.OrderLogEntry'), (select base from p) + o.g * 8 + k),
  o.placed + (k * 3 || ' minutes')::interval, 'INFO',
  (array['INIT','PAY','QUEUE','BAKE','QA','READY','COURIER','DONE'])[k],
  'Order MX-' || o.nr || ' ' || (array['staged','paid','queued','baking','quality check','ready','on its way','done'])[k],
  k <> 4, k, o.id, 1, to_char(o.placed + (k * 3 || ' minutes')::interval, 'HH24:MI:SS')
from o cross join generate_series(1, 8) k;

insert into "fulfilment$paymentattempt" (id, attemptnumber, method, card, amount, attemptstatus, failurecode, transactionid,
  startedat, finishedat, refundedat, refundid, methodlabel, "fulfilment$paymentattempt_order", mxobjectversion)
select pg_temp.mkid(pg_temp.s('Fulfilment.PaymentAttempt'), (select base from p) + o.g * 2 + a), a + 1, 'CARD',
  case when a = 0 and o.g % 10 = 0 then 'VISA_0002' else 'VISA_4242' end, 30,
  case when a = 0 and o.g % 10 = 0 then 'FAILED' when o.st = 'CANCELLED' then 'REFUNDED' else 'SUCCEEDED' end,
  case when a = 0 and o.g % 10 = 0 then 'DECLINED' end, 'txn_sim_' || substr(md5('p' || o.g || a), 1, 12),
  o.placed, o.placed + interval '3 seconds', case when o.st = 'CANCELLED' then o.placed + interval '2 minutes' end, '',
  'Visa •••• 4242', o.id, 1
from o cross join generate_series(0, 1) a where a = 0 or o.g % 10 = 0;

insert into "fulfilment$simulationevent" (id, occurredat, eventtype, message, "fulfilment$simulationevent_order", mxobjectversion)
select pg_temp.mkid(pg_temp.s('Fulfilment.SimulationEvent'), (select base from p) + o.g * 2 + e),
  o.placed + (e * 10 || ' minutes')::interval, (array['STAGE_ADVANCED','DELIVERY_COMPLETED'])[e + 1],
  'MX-' || o.nr || ' ' || (array['advanced','completed'])[e + 1], o.id, 1
from o cross join generate_series(0, 1) e
where o.placed > (select t0 from p) - interval '24 hours';   -- steady state: housekeeping keeps 24 h (backlog.sql adds the rest)

insert into "fulfilment$orderaccess" (id, grantedat, "fulfilment$orderaccess_order", mxobjectversion)
select pg_temp.mkid(pg_temp.s('Fulfilment.OrderAccess'), (select base from p) + o.g), o.placed, o.id, 1 from o;

-- ---------------------------------------------------------------- abandoned carts, toasts, lookups
insert into "shop$cart" (id, couponinput, couponstate, itemcount, subtotal, discountpreview, hasunavailable, hasonlydrinks,
  updatedat, isfiltervegetarian, isfiltervegan, isfilterspicy, total, isfreeunlocked, carouselstart, mxobjectversion)
select pg_temp.mkid(pg_temp.s('Shop.Cart'), (select base from p) + g), '', 'NONE', 2, 30, 0, false, false,
  (select t0 from p) - ((g % 90) || ' days')::interval - ((g % 1440) || ' minutes')::interval, false, false, false, 30, false, 0, 1
from generate_series(1, (select n_cart from p)) g;

insert into "shop$cartline" (id, quantity, unitprice, linetotal, isvegetarian, isvegan, isavailable, configurationkey, configtext,
  createdat, isdraft, extrascount, "shop$cartline_cart", "shop$cartline_product", "shop$cartline_size", mxobjectversion)
select pg_temp.mkid(pg_temp.s('Shop.CartLine'), (select base from p) + g * 2 + k), 1, pr.price, pr.price, false, false, true,
  pr.code || '|' || k, '', (select t0 from p) - ((g % 90) || ' days')::interval, false, 0,
  pg_temp.mkid(pg_temp.s('Shop.Cart'), (select base from p) + g), pr.id, pr.size_id, 1
from generate_series(1, (select n_cart from p)) g cross join generate_series(0, 1) k
join prod pr on pr.i = (g + k * 5) % (select count(*) from prod);

insert into "core$toast" (id, message, level, createdat, expiresat, shouldshowcartaction, mxobjectversion)
select pg_temp.mkid(pg_temp.s('Core.Toast'), (select base from p) + g), 'Added to your manifest.', 'SUCCESS',
  (select t0 from p) - ((g % 365) || ' days')::interval, (select t0 from p) - ((g % 365) || ' days')::interval + interval '5 seconds', false, 1
from generate_series(1, 200000) g;

insert into "shop$lookupattempt" (id, attemptedat, mxobjectversion)
select pg_temp.mkid(pg_temp.s('Shop.LookupAttempt'), (select base from p) + g), (select t0 from p) - ((g % 365) || ' days')::interval, 1
from generate_series(1, 50000) g;

-- ---------------------------------------------------------------- keep the runtime's sequences clear of the seed
update mendixsystem$entityidentifier set object_sequence = greatest(object_sequence, 20000000)
where id in (select id from mendixsystem$entity where entity_name in ('Fulfilment.Order','Fulfilment.OrderLine',
  'Fulfilment.OrderLineModifier','Fulfilment.OrderStatusChange','Fulfilment.OrderLogEntry','Fulfilment.PaymentAttempt',
  'Fulfilment.SimulationEvent','Fulfilment.OrderAccess','Shop.Cart','Shop.CartLine','Core.Toast','Shop.LookupAttempt'));

analyze;

select 'orders' as what, count(*) from "fulfilment$order"
union all select 'orders today (UTC date)', count(*) from "fulfilment$order" where placedat >= date_trunc('day', now())
union all select 'order lines', count(*) from "fulfilment$orderline"
union all select 'log entries', count(*) from "fulfilment$orderlogentry"
union all select 'status changes', count(*) from "fulfilment$orderstatuschange"
union all select 'carts', count(*) from "shop$cart"
union all select 'cart lines', count(*) from "shop$cartline";
