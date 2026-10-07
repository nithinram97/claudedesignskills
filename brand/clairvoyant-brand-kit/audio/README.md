# Soundtrack: "Orb, leap and merge"

Original music and placeholder sound effects for the logo film
(`blender/clairvoyant_orb_leap_merge_v3.py`, 430 frames at 30 fps = 14.333 s).

Everything here is synthesized from scratch by `tools/make_orb_audio.py`: no samples,
no third-party recordings. **License: CC0-1.0 (public domain dedication).** Use, edit and
publish it freely, no attribution needed.

## Files

All files are **48 kHz / 24-bit stereo WAV**, exactly the length of the film, and start at
frame 1, so they line up in any editor without nudging.

| File | What it is |
|---|---|
| `clairvoyant_orb_merge_mix.wav` | Music and effects together. The Blender script loads this one. |
| `clairvoyant_orb_merge_music.wav` | Music stem |
| `clairvoyant_orb_merge_sfx.wav` | Sound-effects stem |
| `sfx/*.wav` | Each effect on its own (16 one-shots), peak -1 dBFS |
| `cue_sheet.csv` | Frame, time and file of every effect cue |

The two stems sum exactly to the mix: drop both in, set them to 0 dB, and you have the mix,
now with separate faders. The mix peaks at -1 dBFS and is about -14 LUFS (a typical online level).

## The music

120 bpm in C major, one chord per second, written to the beats:

| Frames | Beat | Music |
|---|---|---|
| 1–30 | Idle | Soft Cmaj7 pad |
| 31–203 | Chase and climb | Plucked arpeggios that climb in register as Orb climbs: C, C, Dm7, Em7, Fmaj7 |
| 204–224 | Psych up | Thins to one held G and a low pad |
| 225–243 | Leap and catch | Silence (only his breath), a click, 4 frames of nothing |
| 244–277 | Merge | Shimmering G pad and bells |
| 278–325 | Reveal | F → G build with an accelerating pulse under the riser |
| 326 | Stand locks in | Big C major hit |
| 345–430 | Title | Warm Cmaj9 bells, a sparkle on the tagline, fade out |

## Effects (placeholders)

Antenna twitch ticks, spark pop and zip, footsteps, bars rising, a marimba note per landing
(C, E, G, C), the jump "boing" and falling "wah", his breath on the leap, the catch click and
shimmer, the merge "shoop" and ping, the reveal riser, the stand "thoom", and a tuned tick per
wordmark letter. See `cue_sheet.csv` for exact frames. They're meant to time the cut, not
to be final: swap any one-shot for a designed sound at the same frame.

## Regenerate or change

```bash
tools/make_orb_audio.py                 # rewrites this folder
tools/make_orb_audio.py --seed 7        # different random detail in the noises
```

If you retime the film, change the `F_*` beat frames at the top of both the Blender script
and `tools/make_orb_audio.py`, then regenerate. Needs Python 3 and numpy.

## In Blender

The script finds `clairvoyant_orb_merge_mix.wav` automatically (next to your .blend, in an
`audio/` folder next to it, or in this folder) and adds it as a sound strip at frame 1. The MP4
is rendered with AAC audio. To use another file, set `AUDIO_FILE` near the top of the script.
