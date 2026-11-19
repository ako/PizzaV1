# Performance under load

`report.html`: two guest journeys measured on a volume seed of 400,000 orders (about 10M
rows), before and after the fixes this test led to. Findings are grouped by improvement
(F1–F8), with flame-chart pairs for the steps that changed and the most expensive
statements. The built-in rendering of the same data is `../reports/performance.html`.

## Reproduce

1. Back up the dev database: `pg_dump -Fc -h 127.0.0.1 -U mendix gitpizza > before-volume.dump`.
2. With the app stopped, run `psql -h 127.0.0.1 -U mendix -d gitpizza -f tools/seed.sql`
   (about 4 minutes). For finding F1, also run `tools/backlog.sql`, which adds a year of
   simulation events.
3. Instrument Postgres as superuser, recording each change so it can be reset:
   - `ALTER SYSTEM SET shared_preload_libraries = pg_stat_statements, auto_explain;`
   - restart the cluster;
   - set `auto_explain.log_min_duration = '20ms'`, `log_analyze`, `log_buffers` and
     `log_format = 'json'`;
   - `create extension pg_stat_statements`.
4. Start the app without a reset and with tracing:
   `./mxcli run --local --detach -p GitPizza.mpr --trace-otlp http://127.0.0.1:4318 --constant Simulation.ResetOnStartup=false`.
5. Measure:
   `./mxcli report performance -p GitPizza.mpr --journeys-cmd "node tests/perf/journeys.js" -f json -o data/<label>-raw.json`.
   Then copy the collector's `journeys.jsonl` to `data/<label>-journeys.jsonl` and its
   `spans.jsonl` to `data/<label>-spans.jsonl.gz` (gzipped). Save the top of
   `pg_stat_statements` as `data/<label>-statements.psv`.
6. Generate the data and the page:
   - `python3 tools/analyse.py data/before`, then `data/after` and `data/drain`. This
     keeps only the guest's own requests and flame charts.
   - `python3 tools/gen_report.py`
7. Restore: drop and recreate the database from the dump, `ALTER SYSTEM RESET` each setting,
   and restart Postgres.

"Before" is the committed model on the seed; "after" is the fixed model on the same seed.
Both start fresh. The incident facts of F1 (`data/f1-incident.json`) come from the runtime
log of the first volume run.
