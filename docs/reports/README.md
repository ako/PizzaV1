# Reports

`index.html` links every report page. All pages share one look (`tools/report_kit.py`),
embed their fonts and work offline. Each also has mxcli's built-in rendering of the same
data in this folder.

| Report | Page | Generator | Data |
|---|---|---|---|
| Traceability | `../traceability/report.html` | `../traceability/tools/gen_traceability.py` | `raw/traceability.json` |
| Tests and coverage | `../testing/report.html` | `../testing/tools/gen_tests.py` | `raw/tests.json`, `raw/junit.xml`, `raw/journeys.jsonl` |
| Performance under load | `../perf/report.html` | `../perf/tools/gen_report.py` | `../perf/data/` (see `../perf/README.md`) |
| Architecture | `../architecture/report.html` | `../architecture/tools/gen_arch.py` | `../architecture/arch.json` |
| Security | `../security/report.html` | `../security/tools/gen_security.py` | `raw/security.json`, `security-annotations.yaml` |
| Quality score | `../quality/report.html` | `../quality/tools/gen_quality.py` | `raw/quality.json` |
| Software map | `map.html` | `tools/restyle_map.py` after `mxcli report map` | the model |

## Refresh the data

1. Start the app with a fresh demo reset and tracing:

   ```bash
   ./mxcli run --local --detach -p GitPizza.mpr --trace-otlp http://127.0.0.1:4318 --constant Simulation.ResetOnStartup=true
   ```

2. Run the journeys while spans are collected:

   ```bash
   ./mxcli report tests -p GitPizza.mpr --journeys-cmd "node tests/e2e/journeys.js" -f json -o /tmp/t.json
   ```

   Then copy the collector's `journeys.jsonl` and `spans.jsonl` into `raw/`.
   `spans.jsonl` is gitignored.

3. Stop the app and run the microflow tests:

   ```bash
   ./mxcli test tests/ -p GitPizza.mpr --local --junit docs/reports/raw/junit.xml
   ```

   Afterwards, delete the `mxtest` line the test runner leaves in
   `javasource/system/UserActionsRegistrar.java`.

4. Write each report's JSON. `$EV` stands for
   `--junit raw/junit.xml --journeys raw/journeys.jsonl --spans raw/spans.jsonl`:
   - `./mxcli report tests -p GitPizza.mpr $EV -f json -o raw/tests.json`
   - `./mxcli report traceability -p GitPizza.mpr $EV -f json -o raw/traceability.json`
   - `./mxcli report security -p GitPizza.mpr -f json -o raw/security.json`
   - `./mxcli report -p GitPizza.mpr --format json -o raw/quality.json`
   - `./mxcli report architecture -p GitPizza.mpr -f json -o raw/architecture.json`

5. Render the pages:
   - each generator above;
   - `python3 ../architecture/tools/collect.py` first, for the architecture page;
   - `./mxcli report map -p GitPizza.mpr -o docs/reports/map.html`, then
     `python3 tools/restyle_map.py docs/reports/map.html`;
   - `python3 tools/reports_index.py` for the overview.

   The built-in renderings come from
   `./mxcli report <kind> --from raw/<kind>.json --annotations <kind>-annotations.yaml -o <kind>.html`.
