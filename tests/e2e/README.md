# Browser tests

These tests need only the preinstalled `playwright` library, not a test runner.
Run them against the app on `http://localhost:8080`, or set `APP_URL` for another address:

```bash
./mxcli run --local --detach -p GitPizza.mpr --constant Simulation.ResetOnStartup=true
node tests/e2e/journeys.js     # user journeys (acceptance scenarios, worked examples)
node tests/e2e/visual.js       # pixel comparison against the prototype
```

| Suite | What it proves |
|---|---|
| `journeys.js` | J1 order → pay → confirmation → tracking ($47.24). J2 coupon `GITHUB_STUDENT`, Example B ($26.58). J3 declined `VISA_0002`, then a retry with Apple Pay. J4 lookup of an unknown order. J5 the 404 page with no technical names. J6 connection loss: banner, blocked action, recovery. J7 phone layout with no horizontal scroll. |
| `visual.js` | The first viewport of SCR-01/02/03/10/40/41 at 1440×900 and 390×844, compared with `reference/` (the prototype). The budget is the share of differing pixels per screen. Shots and red diff images go to `out/`. |

Every test opens a fresh browser context and logs out at the end. Each context is a new
guest session, and the trial runtime caps how many sessions can be open at once.

## Why the visual budget is not zero

The comparison is strict: a pixel differs when any colour channel differs by more than 32.
Some differences remain on purpose:

- **Live data.** The home KPIs, the oven and courier state, and clocks change all the time.
- **Prototype-only elements.** The `PROTOTYPE` badge. Also the phone cart bar on an empty
  cart: the prototype's script hides it, but a CSS rule overrides `hidden`.
- **Story requirements the prototype lacks.** The dietary filter chips (US-033, BR-MENU-20)
  are hidden for the comparison only.

To refresh the references after a prototype change, serve the prototype package and run
`PROTO_URL=http://localhost:8765/08-prototype/customer node tests/e2e/capture-reference.js`.
