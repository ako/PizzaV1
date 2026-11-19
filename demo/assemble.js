// Assemble a recorded take into the finished film (record-narrated-demo, Stage 2).
//
//   node demo/assemble.js <film> <desktop|phone>
//
// 1. Clock map. The recorder's clock is not the video's: there is an OFFSET (recording
//    starts before the first screen settles; take.js records it) and a SCALE (the capture
//    drops frames while the page is busy, so the file plays back longer than the session).
//    Two anchors -> video_t = offset + B * mark_t, with B fitted from the file's real
//    duration. An implausible B is refused rather than cut.
// 2. Contact sheet: one frame from inside every beat, tiled, so the map is checked by
//    LOOKING (demo/out/<film>-<device>/contact.png) rather than trusted.
// 3. Sound: each voice line (demo/voice/<film>/, mastered to -18.6 LUFS by synth.py) is
//    placed at its beat's video time; a warm sustained pad sits under it at -30 LUFS.
//    The voice track is timed from the audio: walkthrough.js held each beat for the
//    line's measured length + a reading tail.
// 4. demo/films/<film>-<device>.mp4 (H.264 + AAC 48 kHz), and the voice density.
'use strict';
const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

const [film, device] = process.argv.slice(2);
const OUT = path.join(__dirname, 'out', `${film}-${device}`);
const meta = JSON.parse(fs.readFileSync(path.join(OUT, 'beats.json'), 'utf8'));
const FILMS = JSON.parse(fs.readFileSync(path.join(__dirname, 'films.json'), 'utf8'));
const voiceDir = path.join(__dirname, 'voice', film);
const durFile = path.join(voiceDir, 'durations.json');
const DUR = fs.existsSync(durFile) ? JSON.parse(fs.readFileSync(durFile, 'utf8')) : null;
const FINAL = path.join(__dirname, 'films');
fs.mkdirSync(FINAL, { recursive: true });

const run = (bin, args) => execFileSync(bin, args, { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] });
const probe = (file) => parseFloat(run('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'default=nw=1:nk=1', file]));

// webm from the recorder often has no duration header: remux once so ffprobe can read it.
const rawWebm = path.join(OUT, 'raw', meta.video);
const take = path.join(OUT, 'take.mp4');
run('ffmpeg', ['-y', '-loglevel', 'error', '-i', rawWebm, '-c:v', 'libx264', '-preset', 'slow', '-crf', '24',
  '-pix_fmt', 'yuv420p', '-vf', 'pad=ceil(iw/2)*2:ceil(ih/2)*2', '-an', take]);
const videoDur = probe(take);

const end = meta.beats.find((b) => b.name === 'end').t;
const B = (videoDur - meta.offset_s) / (end + meta.post_roll_s);
if (B < 0.9 || B > 1.3) throw new Error(`clock scale ${B.toFixed(3)} is implausible — refusing to cut this take`);
const vt = (t) => meta.offset_s + B * t;
console.log(`clock map: video_t = ${meta.offset_s.toFixed(3)} + ${B.toFixed(4)} x mark_t   (video ${videoDur.toFixed(2)}s)`);

// Contact sheet: one frame 2 s into every beat.
const says = meta.beats.filter((b) => b.name.startsWith('say:'));
const frames = says.map((b, i) => {
  const f = path.join(OUT, `beat-${String(i + 1).padStart(2, '0')}.png`);
  run('ffmpeg', ['-y', '-loglevel', 'error', '-ss', vt(b.t + 2.0).toFixed(3), '-i', take, '-frames:v', '1', '-vf', 'scale=480:-2', f]);
  return f;
});
const cols = 4;
const rows = Math.ceil(frames.length / cols);
const inputs = frames.flatMap((f) => ['-i', f]);
const layout = frames.map((_, i) => `${(i % cols) === 0 ? '0' : Array.from({ length: i % cols }, (__, k) => `w${k}`).join('+')}_${Math.floor(i / cols) === 0 ? '0' : Array.from({ length: Math.floor(i / cols) }, (__, k) => `h${k * cols}`).join('+')}`).join('|');
run('ffmpeg', ['-y', '-loglevel', 'error', ...inputs, '-filter_complex', `xstack=inputs=${frames.length}:layout=${layout}:fill=black`, path.join(OUT, 'contact.png')]);
frames.forEach((f) => fs.unlinkSync(f));
console.log(`contact sheet: ${path.join(OUT, 'contact.png')} (${frames.length} beats, ${rows}x${cols})`);

// Sound.
const finalFile = path.join(FINAL, `${film}-${device}.mp4`);
if (!DUR) {
  fs.copyFileSync(take, finalFile);
  console.log(`no voice track (demo/voice/${film}/durations.json missing): silent film with captions -> ${finalFile}`);
  process.exit(0);
}
const beatNames = Object.keys(FILMS[film].lines);
const voiceFiles = fs.readdirSync(voiceDir).filter((f) => f.endsWith('.wav')).sort();
if (voiceFiles.length !== beatNames.length) throw new Error(`${voiceFiles.length} voice files for ${beatNames.length} lines`);
const audioIn = [];
const placed = [];
let voiceTotal = 0;
beatNames.forEach((name, i) => {
  const mark = meta.beats.find((b) => b.name === `say:${name}`);
  if (!mark) throw new Error(`no mark for beat ${name}`);
  const file = path.join(voiceDir, voiceFiles[i]);
  if (!voiceFiles[i].includes(name)) throw new Error(`voice file ${voiceFiles[i]} does not match beat ${name}`);
  const d = probe(file);
  if (Math.abs(d - DUR[name]) > 0.05) throw new Error(`${name}: voice is ${d.toFixed(2)}s, durations.json says ${DUR[name]}`);
  voiceTotal += d;
  audioIn.push('-i', file);
  const at = Math.round((vt(mark.t) + 0.35) * 1000);   // the caption rises in ~0.35 s
  placed.push(`[${i + 1}:a]adelay=${at}|${at}[v${i}]`);
});
// The bed: a warm A-major pad, slow swell, no percussion, mastered to -30 LUFS.
const bedSrc = `aevalsrc='0.2*sin(2*PI*110*t)+0.15*sin(2*PI*164.81*t)+0.12*sin(2*PI*220*t)+0.08*sin(2*PI*277.18*t)` +
  `|0.2*sin(2*PI*110.4*t)+0.15*sin(2*PI*165.2*t)+0.12*sin(2*PI*220.6*t)+0.08*sin(2*PI*277.6*t)':s=48000:d=${videoDur.toFixed(2)}`;
const bed = path.join(OUT, 'bed.wav');
run('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'lavfi', '-i', bedSrc, '-af',
  `tremolo=f=0.1:d=0.35,lowpass=f=900,afade=t=in:d=3,afade=t=out:st=${Math.max(0, videoDur - 4).toFixed(2)}:d=4,loudnorm=I=-30:TP=-3:LRA=7`,
  '-ar', '48000', '-ac', '2', bed]);
const mix = `${placed.join(';')};${beatNames.map((_, i) => `[v${i}]`).join('')}[0:a]amix=inputs=${beatNames.length + 1}:normalize=0:duration=longest[a]`;
const audio = path.join(OUT, 'sound.wav');
run('ffmpeg', ['-y', '-loglevel', 'error', '-i', bed, ...audioIn, '-filter_complex', mix, '-map', '[a]', '-t', videoDur.toFixed(2), audio]);
run('ffmpeg', ['-y', '-loglevel', 'error', '-i', take, '-i', audio, '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
  '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-movflags', '+faststart', '-shortest', finalFile]);
const filmDur = probe(finalFile);
console.log(`film: ${finalFile}  ${filmDur.toFixed(1)}s, voice ${voiceTotal.toFixed(1)}s = ${(100 * voiceTotal / filmDur).toFixed(0)}% density`);
