#!/usr/bin/env python3
"""Synthesise the narration for each film (record-narrated-demo skill).

    python3 demo/synth.py            # every film in demo/films.json
    python3 demo/synth.py order      # one film

Voice: Kokoro `bm_george` (British English), the catalogue voice; not a per-film choice.
Every line is mastered with a two-pass loudnorm to I=-18.6 LUFS, TP=-1.5 dBTP,
resampled to 48 kHz stereo, and VERIFIED PER LINE (exists, > 0.5 s, duration read
back with ffprobe). A total-duration check is not enough: TTS has failed by
producing 0 of 12 or 10 of 12 lines with exit code 0.

Writes demo/voice/<film>/<NN>-<beat>.wav and demo/voice/<film>/durations.json,
which the walkthrough uses to hold each beat for voice + reading tail.
"""
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
FILMS = json.load(open(os.path.join(ROOT, 'films.json'), encoding='utf-8'))


def ffprobe_duration(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                          '-of', 'default=nw=1:nk=1', path], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def loudnorm(src, dst, target='I=-18.6:TP=-1.5:LRA=11'):
    """Two-pass loudnorm: measure, then feed the measured values back."""
    probe = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', src, '-af',
                            f'loudnorm={target}:print_format=json', '-f', 'null', '-'],
                           capture_output=True, text=True, check=True).stderr
    m = json.loads(probe[probe.rindex('{'):probe.rindex('}') + 1])
    second = (f"loudnorm={target}:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
              f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:"
              f"offset={m['target_offset']}:linear=true")
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', src, '-af', second,
                    '-ar', '48000', '-ac', '2', dst], check=True)


def main(names):
    import numpy as np
    import soundfile as sf
    from kokoro import KPipeline
    pipe = KPipeline(lang_code='b')                         # British English
    for name in names:
        film = FILMS[name]
        out = os.path.join(ROOT, 'voice', name)
        os.makedirs(out, exist_ok=True)
        durations = {}
        for n, (beat, line) in enumerate(film['lines'].items(), start=1):
            raw = os.path.join(out, f'{n:02d}-{beat}.raw.wav')
            wav = os.path.join(out, f'{n:02d}-{beat}.wav')
            chunks = []
            for c in pipe(line, voice='bm_george', speed=1.0):
                a = c.audio if hasattr(c, 'audio') else c[2]     # newer: Result objects; older: (gs, ps, audio)
                chunks.append(a.numpy() if hasattr(a, 'numpy') else np.asarray(a))
            audio = np.concatenate(chunks)
            sf.write(raw, audio, 24000)                     # Kokoro emits 24 kHz mono
            loudnorm(raw, wav)
            os.remove(raw)
            d = ffprobe_duration(wav)
            if d < 0.5:
                raise SystemExit(f'{name}/{beat}: voice line is {d:.2f}s — synthesis failed')
            durations[beat] = round(d, 3)
            print(f'  {name}/{n:02d}-{beat}: {d:.2f}s')
        if len(durations) != len(film['lines']):
            raise SystemExit(f'{name}: {len(durations)} of {len(film["lines"])} lines synthesised')
        json.dump(durations, open(os.path.join(out, 'durations.json'), 'w'), indent=1)
        print(f'{name}: {len(durations)} lines, {sum(durations.values()):.1f}s of voice')


if __name__ == '__main__':
    main(sys.argv[1:] or list(FILMS))
