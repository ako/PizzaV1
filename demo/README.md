# Narrated journey films

These films are made with the `record-narrated-demo` skill
(`.claude/skills/record-narrated-demo`). They **explain** the guest journeys and gate
nothing; the verdicts live in `tests/e2e/journeys.js`, which walks the same paths
(J1, J3, J9).

| Film | Story | Desktop (1920×1080) | Phone (iPhone profile) |
|---|---|---|---|
| Sam orders a pizza | home → menu → configure Inferno Payload Large + cherry tomatoes ($25.00) → cart → checkout → pay → confirmation → live tracking | `films/order-desktop.mp4` (102 s, 60 % voice) | `films/order-phone.mp4` (101 s, 61 %) |
| A declined card | Binary BBQ → checkout with the declining test card → declined → Apple Pay retry → confirmation → order log with both attempts | `films/declined-desktop.mp4` (101 s, 57 %) | `films/declined-phone.mp4` (99 s, 58 %) |

## Rebuild

```bash
./mxcli run --local --detach -p GitPizza.mpr --constant Simulation.ResetOnStartup=true
python3 demo/synth.py                      # voice: Kokoro bm_george, -18.6 LUFS / -1.5 dBTP, 48 kHz
node demo/walkthrough.js order desktop     # record a take (order|declined × desktop|phone)
node demo/assemble.js order desktop        # clock map, contact sheet, voice + bed, mp4
```

- `films.json` holds the narration: one line per beat, used for both the caption and
  the voice. It names the persona and avoids platform vocabulary.
- `walkthrough.js` holds each beat for the line's measured length plus a 1.4 s
  reading tail, and asserts the state each beat is about. A take with a beat that
  did not hold throws and is re-recorded, never cut. Clicks are paced and guarded
  against the error dialog (`take.js`).
- `assemble.js` maps the recorder's clock to the video's (offset + scale, measured at
  about 1.008–1.012), writes `out/<film>-<device>/contact.png` (one frame per beat, to
  check by looking), places each voice line at its beat, adds a −30 LUFS pad bed,
  and reports the voice density.
- Desktop takes use CSS `zoom` 1.333, so the app lays out at the prototype's 1440 px
  in a sharp 1920×1080 frame. Phone takes use a real iPhone user agent
  (`isMobile`, `hasTouch`, DPR 3).
- **Phone deviation:** the overlay's caption-band rules describe the 1920×1080 film
  frame, so on the 430×932 phone the plate is sized for the phone (150 px, 17 px
  text) and `checkOverlay` runs non-strict. The plate is otherwise the same: flat,
  same ground, hairline and app font. The phone's fixed tab bar is lifted above the
  plate, so every tab the walk taps stays visible.
- `take.goto()` waits for `networkidle`. The app's 2-second live poller sometimes
  leaves no quiet gap, which shows as a first-load timeout; just re-run the take.

Raw takes (`out/`) and voice files (`voice/**/*.wav`) are regenerated and not committed.
