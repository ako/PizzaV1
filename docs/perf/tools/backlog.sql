-- Housekeeping backlog for finding F1: simulation events for a year of orders (2 per order, ~800,000),
-- as after housekeeping has been off or failing. Run after seed.sql, with the app stopped.
--   psql -h 127.0.0.1 -U mendix -d gitpizza -f docs/perf/tools/backlog.sql
\set ON_ERROR_STOP on
set synchronous_commit = off;
insert into "fulfilment$simulationevent" (id, occurredat, eventtype, message, "fulfilment$simulationevent_order", mxobjectversion)
select ((select ei.short_id::bigint from mendixsystem$entityidentifier ei join mendixsystem$entity e on e.id = ei.id
         where e.entity_name = 'Fulfilment.SimulationEvent') << 48) | ((11000000 + o.ordernumber * 2 + k) << 7) | ((o.ordernumber * 2 + k) % 128),
  o.placedat + (k * 10 || ' minutes')::interval, (array['STAGE_ADVANCED','DELIVERY_COMPLETED'])[k + 1],
  'MX-' || o.ordernumber || ' ' || (array['advanced','completed'])[k + 1], o.id, 1
from "fulfilment$order" o cross join generate_series(0, 1) k
where o.ordernumber > 100000 and o.placedat <= now() - interval '24 hours';
analyze "fulfilment$simulationevent";
select count(*) as simulation_events from "fulfilment$simulationevent";
