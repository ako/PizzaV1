# Git Pizza MxDev Lite — Operations

Times in this file are store time (America/Los_Angeles) unless marked UTC.

## 1. Build, start and stop locally

**Local runtime.** The app runs on the standalone Mendix 11.16.1 runtime, built with MxBuild 11.16.1.
Both are driven by mxcli (`mxcli run --local`, from `mendixlabs/mxcli`). The database is the
runtime's built-in HSQLDB file database, so there is no database server and no Docker.
Studio Pro is not needed to build or run the app.

**Prerequisites (Windows):**

- Windows PowerShell 5.1.
- A JDK 21, with `java.exe` on `PATH` or `JAVA_HOME` set. The project's Java version is 21.
- Internet access on the first run. `mxcli.exe` is downloaded once to `.mxcli-bin\` unless it is
  already in the repository root, on `PATH`, or named by `MXCLI`. MxBuild and the runtime are
  downloaded once to `%USERPROFILE%\.mxcli\mxbuild\11.16.1\`.
- Free ports 8080 (app), 8090 (runtime admin API, loopback only) and 6543 (MxBuild build server, loopback only).

**Commands, from the repository root of a fresh clone:**

```powershell
RUN/start.ps1 -SpeedFactor 10 -ResetOnStartup $true    # build, start, print the base URL
RUN/stop.ps1                                           # stop everything start.ps1 started
```

| Script | Parameters | Exit code | Duration |
|---|---|---|---|
| `RUN/start.ps1` | `-SpeedFactor <n>` (default 1), `-ResetOnStartup $true\|$false` (default `$false`), optional `-Port <n>` (default 8080) | 0 when the app answers HTTP at the base URL (the URL is printed); 1 with a message on stderr when it cannot be built or started | First run: downloads (a few minutes, depending on the connection) plus build and start. Later runs: about 40–60 s; measured 41 s on a Linux host with warm caches |
| `RUN/stop.ps1` | optional `-Port <n>` | 0 when nothing is left running (also when nothing was running); 1 when the port still answers | a few seconds |

What `start.ps1` does:

1. Finds or downloads `mxcli.exe` and checks for Java.
2. Stops a previous run (`mxcli run stop`).
3. Prepares MxBuild and the runtime (`mxcli run --local --setup --db-type hsqldb`).
4. Builds the project and starts the runtime in the background with the constants for this run:
   `mxcli run --local --detach --db-type hsqldb --app-port 8080 --constant Simulation.SpeedFactor=<n> --constant Simulation.ResetOnStartup=<true|false> --constant Shop.AppUrl=http://localhost:8080/`.
   This returns once the app serves.
5. Checks that `http://localhost:8080/` answers 200, prints the base URL and exits 0.

`stop.ps1` runs `mxcli run stop`, which stops the runtime and the MxBuild build server using
the process ids in `.mxcli\run-state.json`. It then checks that the port no longer answers.

**Base URL:** `http://localhost:8080`. The app listens on 127.0.0.1 only.

**Database:** HSQLDB files under `deployment\data\database\hsqldb\`. They are kept between runs,
and `deployment/` is not committed. To start with an empty database (NFR-16.1), run
`RUN/stop.ps1`, delete `deployment\data\database`, and start again. The app then loads the seed
by itself and logs `RESET start by initial-seed`. Alternatively, start with
`-ResetOnStartup $true`, which restores the seed in the existing database.

**The same commands on Linux or macOS** (as used during development):

```bash
./mxcli run --local --detach --db-type hsqldb -p GitPizza.mpr --constant Simulation.SpeedFactor=10 --constant Simulation.ResetOnStartup=true
```

```bash
./mxcli run stop -p GitPizza.mpr
```

## 2. Constants

| Constant | Default in the project | Set by the scripts |
|---|---|---|
| `Simulation.SpeedFactor` | `1` | `-SpeedFactor` |
| `Simulation.ResetOnStartup` | `false` | `-ResetOnStartup` |
| `Shop.AppUrl` | `http://localhost:8080/` | `http://localhost:<Port>/`; it is the base of the tracking link |
| `Shop.FaultInjection` | `false` | not set; `true` only to trigger SCR-41 by hand (`RUN/delivery-notes.md`, Additional notes) |

The scripts pass the values as runtime constant overrides for this run only (`mxcli --constant`).
They never change the model or the project's configuration (NFR-18.6).

The values take effect at start (LITE-CFG-01). The after-startup microflow
`Simulation.ASU_Startup` reads them, writes the `CONFIG` line, stores the speed factor in
`Core.SimulationSettings.SpeedFactor`, and resets the demo before the simulator clock starts
when `ResetOnStartup` is true. A speed factor other than 1, 2, 5 or 10 is logged at WARN as
`CONFIG invalid SpeedFactor=<value>, using 1`, and 1 is used.

## 3. Server log

While the app runs, the runtime log is written to `.mxcli\runtime.log` in the repository.
mxcli's own output (build, start, stop) goes to `.mxcli\run.log`. Each file is appended to
across runs.

Line format: `yyyy-MM-dd HH:mm:ss.SSS LEVEL - <log node>: <message>`. The timestamp is the
host's clock (UTC on the development host), not store time. Examples from a run at speed factor 10:

```text
2026-11-19 15:31:41.430 INFO - Simulation: CONFIG SpeedFactor=10 ResetOnStartup=true
2026-11-19 15:31:41.445 INFO - Simulation: RESET start by startup
2026-11-19 15:31:44.334 INFO - Simulation: RESET end orders=0 duration=3s
2026-11-19 15:33:52.844 INFO - Simulation: ORDER MX-1048 NEW -> PAYMENT_PENDING by sim/traffic
2026-11-19 15:32:07.061 INFO - Simulation: ORDER MX-1044 QA_CHECK -> READY_FOR_PICKUP by sim/kitchen-auto
2026-11-19 15:32:07.107 INFO - Simulation: COURIER CU-01 AVAILABLE -> TO_STORE order=MX-1038
2026-11-19 15:32:07.088 INFO - Simulation: COURIER CU-01 RETURNING -> AVAILABLE
2026-11-19 15:33:52.848 INFO - Simulation: SPAWN MX-1048 PICKUP COUNTER items=1
2026-11-19 15:36:27.128 WARNING - Simulation: CONFIG invalid SpeedFactor=7, using 1
```

These are the lines of LITE-CFG-04 – LITE-CFG-07, on log node `Simulation` at INFO. The runtime
spells the WARN level as `WARNING`. An unexpected error shown on SCR-41 is logged at ERROR on
node `GitPizza` with its incident ID.

## 4. Screen URLs

Page URLs are relative to the base URL. Mendix serves page URLs under `/p/`.

| Screen | URL path | Notes |
|---|---|---|
| SCR-01 Home | `/` or `/p/home` | |
| SCR-02 Menu | `/p/menu` | |
| SCR-03 Pizza configurator | no own URL | Reached from `Configure` on a pizza card (SCR-01, SCR-02) |
| SCR-04 Item info | no own URL | Reached from `module.info` on a product card |
| SCR-05 Cart | no own URL | Drawer opened from the cart button in the header or tab bar |
| SCR-06 Checkout | `/p/checkout` | Also reached from the cart and the Terminal Debugger panel (A-61) |
| SCR-07 Payment sheet | no own URL | Opened by `Execute Order --force` on SCR-06 |
| SCR-08 Order confirmation | no own URL | Shown after a successful payment |
| SCR-09 Order tracking | `/p/track/{trackingToken}` | The guest's tracking link (`Shop.AppUrl` + `p/track/` + token). It is also reached from SCR-08 and SCR-10 |
| SCR-10 Track order lookup | `/p/track` | An invalid or altered tracking link shows `/p/track-invalid` |
| SCR-13 Order receipt | no own URL | Opened by the receipt button on SCR-08 and SCR-09; there is no separate receipt link |
| SCR-16 Customer shell | n/a | Header, sidebar, tab bar and footer around every screen |
| SCR-40 Not found | `/p/not-found` | Also shown for every unknown URL |
| SCR-41 Unexpected error | `/p/error` | Shown instead of the platform's error dialog. To trigger a real one, start with `Shop.FaultInjection=true` and open `/p/fault` |

## 5. Reset and test window

- **Start with `ResetOnStartup = true`.** Before the simulator clock starts, the app deletes all
  orders, reloads the catalog, the settings and the seed orders, and logs `RESET start by startup`
  and `RESET end orders=<n> duration=<s>s`. On an empty database this took 3 s; with about 50
  orders, 5 s.
- **Start with `ResetOnStartup = false`.** The database is kept. Only an empty database is seeded
  (`RESET start by initial-seed`).
- **Scheduled reset.** Every day at 04:00 store time, the scheduled event
  `Simulation.SE_DailyReset` (A-42) logs `RESET start by scheduled`. Open sessions get the toast
  "The demo data was reset by the system." on their next refresh. A test running across 04:00
  loses its orders; the log line `RESET start by scheduled` shows when that happened.
- **Test window.** Run tests between 02:00 and 24:00 store time (A-31). After a reset just after
  midnight, some seed orders fall on the previous date and are not counted as "today" in the
  home KPIs.

## 6. Images and brand files

Static files are served from `theme/web/assets/` under the URL `/assets/`:

| Kind | Folder | File name |
|---|---|---|
| Product photo | `theme/web/assets/products/` | The `imageFile` name in `09-demo-data/` (for example `pz-01-root-pizza.jpg`) |
| Brand file | `theme/web/assets/brand/` | As in `assets/brand/` (for example `logo-horizontal.svg`) |
| Illustration | `theme/web/assets/illustrations/` | As in `assets/illustrations/` (for example `no-results.png`, which is still missing) |

To add or replace a file:

1. Copy it into the folder with the exact file name.
2. Run `RUN/stop.ps1`, then `RUN/start.ps1 -ResetOnStartup $true`. The build copies the theme
   folder, and the reset reloads the product data.

A product whose photo was not available when the seed was generated has an empty `ImageFile`.
For a new photo of such a product:

1. Set `imageAvailable` in the package JSON.
2. Regenerate the seed with `python3 tools/seed/gen_seed.py`.
3. Apply it with `tools/apply_all.sh`, using mxcli on Linux, macOS or WSL.
4. Restart with `-ResetOnStartup $true`.

## 7. Known operational limits

- **Concurrent sessions.** The runtime runs without a licence, which limits concurrent sessions.
  Test scripts should log out (`mx.logout()`) or close each browser context after use, or restart
  the app between suites (`RUN/delivery-notes.md` KI-03).
- **Disk.** The cached MxBuild and runtime take 1.6 GB under `%USERPROFILE%\.mxcli\`. Memory use was
  not measured.
- **Only one run per working copy.** A second `start.ps1` first stops the running one.
- **Simulator start.** The first tick runs a few seconds after start. The watchdog restarts the
  clock within a minute if it ever stops.
- **Untested on Windows.** The scripts were not run on Windows by the contractor
  (`RUN/delivery-notes.md` KI-01).
