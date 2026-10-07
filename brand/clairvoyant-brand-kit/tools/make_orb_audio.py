#!/usr/bin/env python3
"""
Clairvoyant "Orb, leap and merge": music + sound effects generator.

Synthesizes an original music bed and placeholder sound effects timed to the
beats of blender/clairvoyant_orb_leap_merge_v3.py (430 frames @ 30 fps), and
writes high-quality, edit-ready files:

    audio/clairvoyant_orb_merge_mix.wav     music + sfx, the one Blender loads
    audio/clairvoyant_orb_merge_music.wav   music stem
    audio/clairvoyant_orb_merge_sfx.wav     sound-effects stem
    audio/sfx/*.wav                         every effect as a separate one-shot
    audio/cue_sheet.csv                     frame, time and name of every cue

All files are 48 kHz / 24-bit stereo WAV, the same length as the film, so the
stems line up at frame 1 in any editor. Everything is generated from scratch
by this script (no samples), released CC0-1.0.

Usage:
    ./make_orb_audio.py                     # writes ../audio next to this script
    ./make_orb_audio.py --out some/folder   # choose the output folder
    python3 make_orb_audio.py --seed 7      # different random details

Needs Python 3 and numpy.
"""

import argparse
import csv
import os
import sys

try:
    import numpy as np
except ImportError:
    sys.exit("This script needs numpy: pip install numpy")

SR = 48000
FPS = 30
FRAMES = 430
DUR = FRAMES / FPS                      # 14.333 s, exactly the film
N = int(round(DUR * SR))
TAU = 2 * np.pi

# Beat frames, mirrored from the Blender script (change both together)
F_POP, F_CHASE, F_CLIMB, F_SHORT, F_PSYCH = 31, 55, 97, 186, 204
F_LEAP, F_CATCH, F_MERGE, F_REVEAL, F_STAND, F_TITLE = 225, 241, 250, 278, 312, 345


def sec(frame):
    """Time in seconds of a frame (frame 1 = 0.0 s)."""
    return (frame - 1) / FPS


def hz(note):
    """Note name like 'C4', 'F#3', 'Bb5' to frequency."""
    names = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
    n = names[note[0]]
    rest = note[1:]
    if rest[0] in "#b":
        n += 1 if rest[0] == "#" else -1
        rest = rest[1:]
    midi = 12 * (int(rest) + 1) + n
    return 440.0 * 2 ** ((midi - 69) / 12)


# --------------------------------------------------------------------------
# Building blocks
# --------------------------------------------------------------------------
def tt(dur):
    return np.arange(int(dur * SR)) / SR


def env_adsr(n, a=0.005, d=0.0, s=1.0, r=0.05):
    e = np.full(n, s, dtype=float)
    na, nd, nr = int(a * SR), int(d * SR), int(r * SR)
    na = min(na, n)
    e[:na] = np.linspace(0, 1, na, endpoint=False) if na else e[:na]
    if nd:
        e[na:na + nd] = np.linspace(1, s, min(nd, max(0, n - na)))
    if nr and nr < n:
        e[-nr:] *= np.linspace(1, 0, nr) ** 2
    return e


def fft_filter(x, lo=None, hi=None, slope=4.0):
    """Zero-phase band filter with smooth (Butterworth-like) shoulders."""
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    g = np.ones_like(f)
    if lo:
        g *= 1 / np.sqrt(1 + (lo / np.maximum(f, 1e-3)) ** (2 * slope))
    if hi:
        g *= 1 / np.sqrt(1 + (f / hi) ** (2 * slope))
    return np.fft.irfft(X * g, len(x))


def sweep_noise(dur, f0, f1, q=1.2, rng=None, curve=1.0):
    """Noise through a band-pass whose centre glides from f0 to f1 (STFT)."""
    rng = rng or np.random.default_rng(0)
    n = int(dur * SR)
    x = rng.standard_normal(n + 4096)
    win, hop = 2048, 512
    w = np.hanning(win)
    out = np.zeros(len(x))
    norm = np.zeros(len(x))
    freqs = np.fft.rfftfreq(win, 1 / SR)
    lf = np.log(np.maximum(freqs, 1.0))
    for i, s in enumerate(range(0, len(x) - win, hop)):
        p = min(1.0, s / max(1, n)) ** curve
        fc = f0 * (f1 / f0) ** p
        g = np.exp(-0.5 * ((lf - np.log(fc)) / (0.35 * q)) ** 2)
        seg = np.fft.irfft(np.fft.rfft(x[s:s + win] * w) * g, win)
        out[s:s + win] += seg * w
        norm[s:s + win] += w * w
    out = out[:n] / np.maximum(norm[:n], 1e-6)
    return out / (np.max(np.abs(out)) + 1e-9)


def tone(freq, dur, partials=((1, 1.0),), decay=None, vib=0.0, vib_rate=5.5, glide=None):
    """Additive tone. partials = (ratio, amp[, decay]); glide = end frequency."""
    t = tt(dur)
    if glide:
        f_t = freq * (glide / freq) ** (t / dur)
    else:
        f_t = np.full_like(t, freq)
    if vib:
        f_t = f_t * (1 + vib * np.sin(TAU * vib_rate * t))
    phase = TAU * np.cumsum(f_t) / SR
    out = np.zeros_like(t)
    for p in partials:
        ratio, amp = p[0], p[1]
        d = p[2] if len(p) > 2 else decay
        part = amp * np.sin(phase * ratio)
        if d:
            part *= np.exp(-t * d)
        out += part
    return out


def marimba(freq, dur=1.2):
    x = tone(freq, dur, ((1, 1.0, 5.5), (3.93, 0.35, 16), (9.2, 0.12, 40), (2.0, 0.08, 9)))
    click = np.random.default_rng(int(freq)).standard_normal(len(x)) * np.exp(-tt(dur) * 400) * 0.15
    return (x + fft_filter(click, lo=1500)) * env_adsr(len(x), a=0.001, r=0.05)


def bell(freq, dur=2.5, bright=1.0):
    x = tone(freq, dur, ((1, 1.0, 1.6), (2.0, 0.45 * bright, 2.4), (2.76, 0.35 * bright, 3.5),
                         (5.40, 0.18 * bright, 6.0), (8.93, 0.08 * bright, 9.0)))
    return x * env_adsr(len(x), a=0.002, r=0.2)


def pluck(freq, dur=0.6, bright=1.0):
    parts = tuple((k, (0.9 ** k) * (1 if k == 1 else bright) / k ** 0.6, 3 + 2.2 * k) for k in range(1, 9))
    x = tone(freq, dur, parts)
    return x * env_adsr(len(x), a=0.002, r=0.08)


def pad(freqs, dur, a=0.6, r=0.8, bright=0.5, detune=0.004):
    t = tt(dur)
    out = np.zeros_like(t)
    for f in freqs:
        for dt in (-detune, 0, detune):
            ff = f * (1 + dt)
            for k, amp in ((1, 1.0), (2, 0.35 * bright), (3, 0.18 * bright), (4, 0.08 * bright)):
                out += amp * np.sin(TAU * ff * k * t + k * dt * 50)
    out *= (1 + 0.08 * np.sin(TAU * 0.25 * t))          # slow breathing
    out /= (3 * len(freqs))
    return out * env_adsr(len(t), a=a, r=r)


def boom(dur=1.8, f0=110, f1=38):
    t = tt(dur)
    f_t = f1 + (f0 - f1) * np.exp(-t * 14)
    body = np.sin(TAU * np.cumsum(f_t) / SR) * np.exp(-t * 2.6)
    knock = fft_filter(np.random.default_rng(3).standard_normal(len(t)), lo=200, hi=2500) * np.exp(-t * 60) * 0.35
    return (body + knock) * env_adsr(len(t), a=0.001, r=0.3)


def click(dur=0.05, f=3200):
    t = tt(dur)
    n = fft_filter(np.random.default_rng(5).standard_normal(len(t)), lo=2500) * np.exp(-t * 250)
    return (0.6 * n + 0.6 * np.sin(TAU * f * t) * np.exp(-t * 120)) * env_adsr(len(t), a=0.0005, r=0.005)


def tick(dur=0.03, f=5200, amp=1.0):
    t = tt(dur)
    return amp * np.sin(TAU * f * t) * np.exp(-t * 300)


def step(rng):
    t = tt(0.09)
    thud = np.sin(TAU * 150 * t * (1 - t * 2)) * np.exp(-t * 55)
    scuff = fft_filter(rng.standard_normal(len(t)), lo=300, hi=3000) * np.exp(-t * 90) * 0.25
    return (thud + scuff) * 0.8


# --------------------------------------------------------------------------
# Mixing helpers
# --------------------------------------------------------------------------
class Track:
    def __init__(self, n=N):
        self.buf = np.zeros((n, 2))

    def add(self, x, at, gain=1.0, pan=0.0):
        """Place mono x at time `at` seconds, equal-power pan -1..1."""
        i = int(round(at * SR))
        if i >= len(self.buf):
            return
        x = x[: len(self.buf) - i]
        lg, rg = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
        self.buf[i:i + len(x), 0] += x * gain * lg * np.sqrt(2)
        self.buf[i:i + len(x), 1] += x * gain * rg * np.sqrt(2)


def reverb(stereo, seconds=1.9, mix=0.25, seed=1, predelay=0.012):
    """Convolution reverb with a synthetic, decorrelated stereo tail."""
    rng = np.random.default_rng(seed)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    decay = np.exp(-t * 6.9 / seconds)
    out = np.zeros_like(stereo)
    pd = int(predelay * SR)
    for ch in range(2):
        ir = rng.standard_normal(n) * decay
        ir = fft_filter(ir, lo=180, hi=7000)            # darker, cleaner tail
        ir[:pd] = 0
        ir /= np.sqrt(np.sum(ir ** 2))
        L = len(stereo) + n
        size = 1 << (L - 1).bit_length()
        wet = np.fft.irfft(np.fft.rfft(stereo[:, ch], size) * np.fft.rfft(ir, size), size)[: len(stereo)]
        out[:, ch] = stereo[:, ch] * (1 - mix) + wet * mix * 2.0
    return out


def fades(stereo):
    x = stereo.copy()
    fade_in, fade_out = int(0.01 * SR), int(0.45 * SR)
    x[:fade_in] *= np.linspace(0, 1, fade_in)[:, None]
    x[-fade_out:] *= (np.linspace(1, 0, fade_out) ** 1.5)[:, None]
    return x


def master(stereo, peak_db=-1.0):
    """Remove DC, fades, linear peak-normalise to peak_db. Returns (audio, gain), so stems can share the gain."""
    x = fades(fft_filter_stereo(stereo, lo=18))
    gain = 10 ** (peak_db / 20) / (np.max(np.abs(x)) + 1e-9)
    return x * gain, gain


def fft_filter_stereo(stereo, **kw):
    return np.stack([fft_filter(stereo[:, c], **kw) for c in range(2)], axis=1)


def automate(stereo, points):
    """Volume automation: points = [(frame, dB), ...], linear in dB between points."""
    t = np.arange(len(stereo)) / SR
    fx = [sec(f) for f, _ in points]
    db = np.interp(t, fx, [d for _, d in points])
    return stereo * (10 ** (db / 20))[:, None]


def write_wav24(path, stereo):
    import wave
    data = np.clip(stereo, -1, 1 - 1 / 2 ** 23)
    ints = np.round(data * (2 ** 23)).astype("<i4")
    raw = ints.reshape(-1).view(np.uint8).reshape(-1, 4)[:, :3].tobytes()
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(3)
        w.setframerate(SR)
        w.writeframes(raw)


# --------------------------------------------------------------------------
# The score
# --------------------------------------------------------------------------
def build(seed):
    rng = np.random.default_rng(seed)
    music, sfx = Track(), Track()
    cues = []                                        # one-shot sfx for the cue sheet

    def cue(name, frame, x, gain=1.0, pan=0.0):
        sfx.add(x, sec(frame), gain, pan)
        cues.append((name, frame, x))

    # ---------------- MUSIC: 120 bpm, C major, one chord per second ------------
    beat = 0.5
    # idle: a soft pad under the twitching
    music.add(pad([hz("C3"), hz("G3"), hz("B3"), hz("E4")], 1.6, a=0.5, r=0.6, bright=0.3), 0.0, 0.22)

    # chase + climb: arpeggios that climb with Orb, one chord per second
    prog = [("C", ["C", "E", "G", "B"], 3), ("C", ["C", "E", "G", "D"], 3), ("D", ["D", "F", "A", "C"], 3),
            ("E", ["E", "G", "B", "D"], 3), ("F", ["F", "A", "C", "E"], 4)]
    t0 = sec(F_POP)
    for i, (root, tones, octv) in enumerate(prog):
        start = t0 + i * 1.0
        length = 1.0 if i < len(prog) - 1 else sec(F_PSYCH) - start
        music.add(pad([hz(f"{root}2"), hz(f"{tones[1]}3"), hz(f"{tones[2]}3")], length + 0.4, a=0.08, r=0.4, bright=0.6),
                  start, 0.20)
        music.add(pluck(hz(f"{root}2"), 0.9, bright=0.4), start, 0.42, -0.1)            # bass on the downbeat
        music.add(pluck(hz(f"{root}2"), 0.6, bright=0.4), start + beat, 0.28, -0.1)
        steps = int(round(length / (beat / 2)))
        for k in range(steps):                                            # 8th-note arpeggio, rising register
            note = tones[k % 4]
            o = octv + 1 + (1 if k >= 4 else 0) + (i // 3)
            pan = -0.35 + 0.7 * (k % 4) / 3
            music.add(pluck(hz(f"{note}{min(o, 6)}"), 0.45, bright=0.8), start + k * beat / 2, 0.16 + 0.02 * i, pan)
        if start >= sec(F_CHASE) - 0.01:                                  # soft hats once the chase starts
            for k in range(steps):
                if k % 2:
                    music.add(fft_filter(rng.standard_normal(int(0.04 * SR)), lo=7000) * np.exp(-tt(0.04) * 90),
                              start + k * beat / 2, 0.05, 0.3)

    # psych-up: everything thins to one held note
    t_ps = sec(F_PSYCH)
    held = tone(hz("G5"), sec(F_LEAP) - t_ps + 0.3, ((1, 1.0), (2, 0.15)), vib=0.004) * env_adsr(int((sec(F_LEAP) - t_ps + 0.3) * SR), a=0.3, r=0.35)
    music.add(held, t_ps, 0.13, 0.1)
    music.add(pad([hz("F2"), hz("C3")], sec(F_LEAP) - t_ps, a=0.2, r=0.5, bright=0.2), t_ps, 0.14)
    # leap: silence (only his breath, in sfx)

    # after the catch: a shimmering pad that rises into the merge
    t_c = sec(F_CATCH) + 4 / FPS
    music.add(pad([hz("G3"), hz("D4"), hz("A4"), hz("C5")], sec(F_REVEAL) - t_c + 0.3, a=0.25, r=0.5, bright=0.7), t_c, 0.20)
    for k, n in enumerate(["G5", "D6", "A5", "C6", "E6", "G6"]):
        music.add(bell(hz(n), 1.6, bright=0.6), t_c + 0.12 * k, 0.07, -0.5 + 0.2 * k)

    # reveal: F -> G build under the riser, then C lands on the stand
    t_r = sec(F_REVEAL)
    t_boom = sec(F_STAND + 14)
    music.add(pad([hz("F2"), hz("A3"), hz("C4"), hz("E4")], (t_boom - t_r) / 2 + 0.2, a=0.3, r=0.3, bright=0.7), t_r, 0.22)
    music.add(pad([hz("G2"), hz("B3"), hz("D4"), hz("F4")], (t_boom - t_r) / 2 + 0.05, a=0.1, r=0.1, bright=0.9),
              t_r + (t_boom - t_r) / 2, 0.26)
    for k in range(int((t_boom - t_r) / (beat / 2))):                     # accelerating pulse into the hit
        music.add(pluck(hz("G3") if k % 2 else hz("G2"), 0.25, bright=0.6), t_r + k * beat / 2, 0.10 + 0.012 * k)

    # the stand locks in: big C major
    music.add(pad([hz("C2"), hz("G2"), hz("E3"), hz("C4"), hz("G4")], DUR - t_boom, a=0.02, r=1.2, bright=0.8), t_boom, 0.30)
    music.add(bell(hz("C6"), 3.0), t_boom, 0.16, 0.2)
    music.add(bell(hz("G5"), 3.0), t_boom + 0.03, 0.12, -0.2)

    # title: warm Cmaj9 bells
    t_t = sec(F_TITLE)
    for k, n in enumerate(["C4", "G4", "B4", "D5", "E5"]):
        music.add(bell(hz(n), 3.0, bright=0.5), t_t + 0.05 * k, 0.12, -0.4 + 0.2 * k)
    music.add(bell(hz("G6"), 2.0, bright=0.4), sec(F_TITLE + 46), 0.08, 0.3)          # tagline sparkle

    # ---------------- SFX -----------------------------------------------------------
    for f in (14, 24):
        cue("antenna_twitch", f, tick(0.04, 4200) + 0.5 * tick(0.04, 6100), 0.35, 0.15)
    pop = tone(900, 0.12, ((1, 1.0), (2, 0.3)), glide=180, decay=18) * env_adsr(int(0.12 * SR), a=0.001, r=0.02)
    cue("spark_pop", F_POP, pop, 0.8, 0.1)
    cue("spark_zip", F_POP, sweep_noise(0.9, 900, 5000, q=0.8, rng=rng) * env_adsr(int(0.9 * SR), a=0.05, r=0.5) *
        np.exp(-tt(0.9) * 2), 0.28, 0.5)
    for i in range(5):                                                        # chase footsteps
        cue("footstep", F_CHASE + 2 + i * 7 + 7, step(rng), 0.45, -0.2 + 0.08 * i)
    for f in (77, 97, 117, 133):                                              # bars rise out of the floor
        cue("bar_rise", f, boom(0.5, 160, 70) * 0.6 + sweep_noise(0.5, 300, 1200, rng=rng) * 0.15 * np.exp(-tt(0.5) * 6), 0.4)
    for f, n in ((F_CLIMB + 14, "C5"), (F_CLIMB + 34, "E5"), (F_CLIMB + 54, "G5"), (F_CLIMB + 78, "C6")):
        cue("landing_marimba", f, marimba(hz(n)), 0.5, 0.1)                 # each landing climbs the scale
    boing = tone(220, 0.5, ((1, 1.0), (2, 0.25)), glide=520, vib=0.06, vib_rate=14, decay=4) * env_adsr(int(0.5 * SR), a=0.003, r=0.1)
    cue("jump_boing", F_SHORT, boing, 0.45)
    wah = tone(392, 0.6, ((1, 1.0), (2, 0.5), (3, 0.3), (4, 0.15)), glide=262, vib=0.02, vib_rate=6, decay=2.5)
    cue("fall_short_wah", F_SHORT + 16, fft_filter(wah, hi=2500) * env_adsr(len(wah), a=0.02, r=0.15), 0.32, -0.1)
    breath_len = sec(F_CATCH) - sec(F_LEAP)
    br = sweep_noise(breath_len, 500, 1400, q=1.4, rng=rng) * env_adsr(int(breath_len * SR), a=0.25, r=0.15)
    cue("leap_breath", F_LEAP, br, 0.18)
    cue("catch_click", F_CATCH, click(), 0.9, 0.2)
    sh_len = 1.0
    shimmer = sum(bell(hz(n), sh_len, bright=1.0) * 0.25 for n in ("E6", "G6", "B6", "D7"))
    cue("catch_shimmer", F_CATCH + 4, shimmer, 0.35, 0.25)
    shoop_len = sec(F_MERGE + 22) - sec(F_MERGE)
    shoop = tone(320, shoop_len, ((1, 1.0), (2, 0.3), (3, 0.1)), glide=1250) * env_adsr(int(shoop_len * SR), a=0.2, r=0.08)
    cue("merge_shoop", F_MERGE, shoop + 0.2 * sweep_noise(shoop_len, 800, 6000, rng=rng), 0.3)
    cue("merge_ping", F_MERGE + 22, bell(hz("C7"), 2.0, bright=0.7), 0.4, 0.3)
    rise_len = t_boom - t_r
    riser = sweep_noise(rise_len, 250, 9000, q=1.0, rng=rng, curve=1.6) * (np.linspace(0, 1, int(rise_len * SR)) ** 2)
    cue("reveal_riser", F_REVEAL, riser, 0.4)
    cue("stand_thoom", F_STAND + 14, boom(2.0), 1.0)
    for i in range(11):                                                       # wordmark letters pop in
        n = ["C", "D", "E", "G", "A"][i % 5] + str(6 + i // 5)
        cue("letter_tick", F_TITLE + 20 + i * 2, tone(hz(n), 0.12, ((1, 1.0), (3, 0.2)), decay=30), 0.10, -0.5 + 0.1 * i)
    return music, sfx, cues


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    here = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument("--out", default=os.path.join(here, "..", "audio"), help="output folder")
    ap.add_argument("--seed", type=int, default=11, help="random seed for noise details")
    args = ap.parse_args()
    out = os.path.abspath(args.out)
    os.makedirs(os.path.join(out, "sfx"), exist_ok=True)

    music, sfx, cues = build(args.seed)
    music_w = reverb(music.buf, 2.2, mix=0.30, seed=2)
    sfx_w = reverb(sfx.buf, 1.4, mix=0.18, seed=3)
    # the music thins out for the psych-up and drops out for the leap, back after the catch
    music_w = automate(music_w * 0.9, [(1, 0), (F_PSYCH - 4, 0), (F_PSYCH + 6, -7), (F_LEAP - 8, -11),
                                       (F_LEAP, -45), (F_CATCH + 3, -45), (F_CATCH + 6, 0), (FRAMES, 0)])
    mix, gain = master(music_w + sfx_w)
    # stems share the mix's gain, fades and DC filter, so music + sfx sum exactly to the mix
    write_wav24(os.path.join(out, "clairvoyant_orb_merge_mix.wav"), mix)
    write_wav24(os.path.join(out, "clairvoyant_orb_merge_music.wav"), fades(fft_filter_stereo(music_w, lo=18)) * gain)
    write_wav24(os.path.join(out, "clairvoyant_orb_merge_sfx.wav"), fades(fft_filter_stereo(sfx_w, lo=18)) * gain)

    seen = {}
    with open(os.path.join(out, "cue_sheet.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["frame", "time_s", "cue", "file"])
        for name, frame, x in sorted(cues, key=lambda c: c[1]):
            fname = f"sfx/{name}.wav"
            if name not in seen:
                one = np.stack([x, x], axis=1)
                one = one / (np.max(np.abs(one)) + 1e-9) * 10 ** (-1 / 20)
                write_wav24(os.path.join(out, fname), one)
                seen[name] = True
            w.writerow([frame, f"{sec(frame):.3f}", name, fname])
    print(f"Wrote {out}: mix, music and sfx stems ({DUR:.3f} s, 48 kHz / 24-bit), "
          f"{len(seen)} one-shots, cue_sheet.csv.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
