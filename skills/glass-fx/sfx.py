#!/usr/bin/env python3
"""Soft sound design for glass-fx, synthesized here (no sample files, no licences).

    python sfx.py preview out.wav       # every sound once, one second apart, to audition them

Every sound is gentle on purpose: slow attacks, low-passed, no hard transients, quiet under a voice.
A reel gets few of them: `mix()` keeps at most one sound per `gap` seconds, highest priority first.
"""
import math
import sys
import wave
from pathlib import Path

import numpy as np

SR = 44100
RNG = np.random.default_rng(7)          # fixed seed: the same spec always sounds the same


def env(n, attack, release, curve=2.0):
    """attack/release envelope over n samples (seconds), smooth on both ends"""
    t = np.arange(n) / SR
    a = np.clip(t / max(attack, 1e-4), 0, 1) ** curve
    r = np.clip((n / SR - t) / max(release, 1e-4), 0, 1) ** curve
    return np.minimum(a, r)


def lowpass(x, cutoff):
    """one-pole low-pass; cutoff may be a number or an array (a sweep)"""
    cut = np.broadcast_to(np.asarray(cutoff, dtype=float), x.shape)
    k = 1 - np.exp(-2 * math.pi * cut / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc += k[i] * (x[i] - acc)
        y[i] = acc
    return y


def noise(n):
    return RNG.standard_normal(n)


def whoosh(d=.55):
    """air moving past: band of noise sweeping up then down"""
    n = int(d * SR)
    t = np.linspace(0, 1, n)
    sweep = 300 + 2600 * np.sin(np.pi * t) ** 2
    x = lowpass(noise(n), sweep)
    x = x - lowpass(x, 180)                                   # take out the rumble
    return x * env(n, d * .55, d * .45) * 2.4


def pop(f0=660):
    """a soft bubble: sine falling in pitch, rounded attack"""
    n = int(.16 * SR)
    t = np.arange(n) / SR
    f = f0 * np.exp(-t * 7)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * env(n, .004, .14, 1.4) * .55


def tick():
    """a quiet glass tick"""
    n = int(.05 * SR)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * 2350 * t) * np.exp(-t * 90) + lowpass(noise(n), 3500) * np.exp(-t * 160) * .3
    return x * env(n, .001, .04) * .32


def shimmer(d=1.4):
    """a soft bell cluster that rings out"""
    n = int(d * SR)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for f, a in ((1318.5, .5), (1975.5, .35), (2637, .25), (3951, .12)):
        det = 1 + RNG.uniform(-.002, .002)
        x += a * np.sin(2 * np.pi * f * det * t + RNG.uniform(0, 6)) * np.exp(-t * (2.2 + f / 2400))
    return x * env(n, .012, d * .5, 1.2) * .32


def rise(d=.9):
    """a gentle swell into a moment"""
    n = int(d * SR)
    t = np.linspace(0, 1, n)
    x = lowpass(noise(n), 250 + 3200 * t ** 2.2)
    x = x - lowpass(x, 150)
    return x * (t ** 2.4) * env(n, .01, .06) * 2.2


def sub(d=.7):
    """a low, soft landing: felt more than heard"""
    n = int(d * SR)
    t = np.arange(n) / SR
    f = 72 * np.exp(-t * 1.6) + 38
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * env(n, .012, d * .8, 1.5) * .7


def typing(chars=8, d=.8):
    out = np.zeros(int(d * SR) + SR // 10)
    for k in range(chars):
        s = tick() * RNG.uniform(.5, .9)
        at = int((k * d / max(1, chars)) * SR + RNG.uniform(0, .02) * SR)
        out[at:at + len(s)] += s
    return out


SOUNDS = {
    'whoosh': whoosh, 'pop': pop, 'tick': tick, 'shimmer': shimmer, 'rise': rise, 'sub': sub, 'typing': typing,
}

# what each effect sounds like: [(sound, offset from the effect's time, priority, gain)]
CUES = {
    'hook': [('whoosh', -.05, 3, 1.0), ('shimmer', .25, 2, .8)],
    'takeover': [('rise', -.85, 3, .9), ('sub', 0, 3, 1.0)],
    'halo_search': [('pop', 0, 2, .9), ('tick', 'click', 2, 1.0)],
    'ribbon_wrap': [('whoosh', 0, 2, .9)],
    'falling_cards': [('whoosh', -.05, 2, .7), ('pop', .45, 1, .6)],
    'social_orbit': [('shimmer', 0, 1, .7)],
    'quote_note': [('whoosh', -.05, 1, .6)],
    'icon_pop': [('pop', 0, 1, .8)],
    'typing_search': [('typing', .25, 1, .8)],
    'film_strip': [('whoosh', 0, 2, .8)],
    'chrome_title': [('sub', 0, 3, .9), ('shimmer', .1, 1, .5)],
    'glass_card': [('whoosh', -.05, 1, .6)],
    'checklist': [('tick', 'items', 1, 1.0)],
    'depth_focus': [('sub', 0, 3, .8), ('whoosh', 0, 1, .4)],
    'stat': [('rise', -.5, 2, .7), ('pop', 'end', 2, .7)],
    'name_tag': [('whoosh', -.05, 1, .5)],
    'cta': [('pop', 0, 2, .9), ('shimmer', .15, 1, .5)],
    'light_leak': [('whoosh', 0, 1, .5)],
}

LEVELS = {'off': 0.0, 'soft': .32, 'medium': .55}
# every sound is levelled to its own peak, so a whoosh never shouts over a tick
PEAK = {'whoosh': .42, 'rise': .36, 'pop': .5, 'tick': .28, 'shimmer': .3, 'sub': .62, 'typing': .26}


def mix(events, dur, out, level='soft', gap=.8):
    """events: [(time, sound, priority, gain)]. Keeps the strongest event in any `gap` window, writes a wav."""
    vol = LEVELS.get(level, level if isinstance(level, (int, float)) else .32)
    kept = []
    for ev in sorted(events, key=lambda e: (-e[2], e[0])):
        if 0 <= ev[0] < dur and all(abs(ev[0] - k[0]) >= gap for k in kept):
            kept.append(ev)
    buf = np.zeros(int((dur + 2) * SR))
    for t, name, _, g in sorted(kept):
        s = SOUNDS[name]()
        s = s / (np.max(np.abs(s)) or 1) * PEAK[name]
        a = int(t * SR)
        buf[a:a + len(s)] += s[:max(0, len(buf) - a)] * g
    buf = buf[:int(dur * SR)] * vol
    peak = np.max(np.abs(buf)) or 1
    if peak > .9:
        buf *= .9 / peak
    st = np.stack([buf, np.roll(buf, 9) * .96], 1)        # a hair of width
    pcm = (np.clip(st, -1, 1) * 32767).astype('<i2')
    with wave.open(str(out), 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    return [(round(k[0], 2), k[1]) for k in sorted(kept)]


if __name__ == '__main__':
    if len(sys.argv) != 3 or sys.argv[1] != 'preview':
        sys.exit(__doc__)
    names = list(SOUNDS)
    print(mix([(1 + k * 1.2, n, 1, 1.0) for k, n in enumerate(names)], 1 + len(names) * 1.2 + 1, Path(sys.argv[2]), 'medium', .1))
