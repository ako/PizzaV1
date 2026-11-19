# Delivery notes — Git Pizza MxDev

## Running the app

```bash
./mxcli setup mxbuild -p GitPizza.mpr
./mxcli run --local --watch --detach -p GitPizza.mpr
```

The app serves at `http://localhost:8080/`. Guests are anonymous Mendix users;
there is no sign-in (LITE-SES-01).

| Constant | Default | Purpose |
|---|---|---|
| `Simulation.SpeedFactor` | `1` | Speeds up the kitchen, oven and courier simulation |
| `Simulation.ResetOnStartup` | `false` | Resets the demo data when the app starts (SIM-08) |
| `Shop.AppUrl` | `http://localhost:8080/` | Base URL used for tracking links |
| `Shop.FaultInjection` | `false` | Turns on the fault probe below. Keep it `false` in production |

## Triggering an unexpected error (US-282 AC2)

1. Start the app with fault injection on:
   `./mxcli run --local --detach -p GitPizza.mpr --constant Shop.FaultInjection=true`
2. Open `http://localhost:8080/p/fault`. Its data source fails with an
   unhandled error.
3. The platform's default error dialog is suppressed. The guest is sent to
   SCR-41 (`/p/error`), which shows `ERROR 500 // SEG_FAULT` and
   `INCIDENT_ID: ERR-yyyyMMdd-HHmmss-XXXX`.
4. The same ID is written to the application log on node `GitPizza` at ERROR
   level: `INCIDENT ERR-… : unexpected error page shown to …`. The technical
   stack trace of the failure is in the log just before that line.
5. `RETRY_DEPLOYMENT` repeats the page load that failed. `RETURN_TO_MAIN`
   opens SCR-01.

With `Shop.FaultInjection` off, `/p/fault` only says that fault injection is
off.

## Sessions (LITE-SES-04, US-286)

- The session timeout is the Mendix default of **10 minutes** of inactivity.
- While a tab of the app is open and online, the client keeps the session
  alive, and the 2-second live poller also keeps it in use. So a session only
  expires after all tabs have been closed (or have been offline) for 10 minutes.
- When a guest comes back in a new session after a non-empty cart was lost,
  the toast "Your session expired. Your manifest was cleared." (TXT-ERR-20) is
  shown. The browser remembers the last session ID and cart count in
  `localStorage`. Orders stay reachable through the tracking link or ORDER_LOOKUP.

## Connection loss (US-287)

- The live poller checks the server every 2 seconds. After two failures in a
  row, the `CONNECTION_LOST //` banner is shown (TXT-NAV-30). The poller keeps
  retrying every 2 seconds. On success the banner hides and the toast TXT-NAV-31
  is shown.
- While offline, any button or link press is stopped before it reaches the
  server. An error toast (TXT-ERR-19) is shown, so the action is neither lost
  silently nor sent twice later.

## Time zone

All dates are shown in store time, America/Los_Angeles (BR-DATA-05). This uses
the runtime's default time zone. Order-log timestamps are formatted on the
server.
