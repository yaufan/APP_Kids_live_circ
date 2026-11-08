"""小小生活家 (Little Life Expert): every sound in the app, made here from sine
waves and noise, so every one is ours: nothing recorded, nothing downloaded,
and every tune written for this app (except the garbage truck, which plays
the first phrase of Beethoven's "Für Elise", as Taiwan's garbage trucks do;
Beethoven's melody has been public domain for about two hundred years, and
the music box playing it is synthesized here).

- Music (WAV, 16,000 Hz, seamless loops of 21 to 24 s): one tune for each
  time of the game day and one for each place outside the house, and a
  lullaby for the rest screen. All toy-like and simple (music box,
  xylophone, kalimba, soft bells, ukulele plucks), each in its own key and
  tempo, so a child can hear what time it is.
- Short sounds (WAV, 22,050 Hz): one for every action in the house, every
  little event, and each buddy's voice. All soft and friendly: the
  earthquake and thunder are short, low and quiet, never scary.
- Voices (yum, yawn, sneeze, the buddies) are a buzz through formant
  filters, as in the sibling apps.
- Every random choice uses a fixed seed, so each run writes the same files.
- Every short sound is set to the same loudness as heard through a phone
  speaker (A-weighting, nothing under 250 Hz), plus or minus a few dB where
  it should sit softer, with its peak at most 0.72. The music is set the same
  way, 8 to 12 dB under the short sounds.

The helpers (t_of, env, sweep, decay, lowpass, bandpass, highpass, norm,
partial, bell, marimba, place, tune_loop, resonator, voice, ease, glide,
bubble, above, spans, melody, root_of, pluck_bass, metal, shaker, kick,
jingle, noise_through, soft_piano, carry, celesta, chime, plink, clack,
a_weight, loudness, chord_tones, chord_at, harmonics, pizz, toy_horn, pad,
chirp, yay, ocarina, recorder, harp, toy_piano, fm_bell, hum_voice, sleigh,
clap, tidy, phone_ready, level, write, seam, report, read, preview) come
from 迷宮小冒險's design/sounds/make_sounds.py (and through it from the other
sibling apps). New here: the music box, kalimba, ukulele, xylophone, vibes,
wood block, the running-water and whoosh builders, every tune and every
sound.

    python3 design/sounds/make_sounds.py                  # writes app/assets/sounds/*.wav
    python3 design/sounds/make_sounds.py preview OUT.m4a  # and a listening preview
    python3 design/sounds/make_sounds.py tap yum ...       # only these (while working on one)
"""
import os
import pathlib
import subprocess
import sys
import tempfile
import wave

import numpy as np
from scipy.signal import lfilter, resample_poly

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "app" / "assets" / "sounds"
SR = 22050       # short sounds, footsteps and voices
LOOP_SR = 16000  # music
LIMIT = 12_000_000  # bytes, the whole folder (ten tunes of 19 to 27 s at 16 kHz are about 7 MB)

# Notes (Hz), with flats as well as sharps.
NOTE = {f"{n}{o}": 440 * 2 ** ((k - 9) / 12 + o - 4)
        for o in range(1, 9) for k, n in enumerate("C C# D D# E F F# G G# A A# B".split())}
for _o in range(1, 9):
    for _flat, _sharp in (("Db", "C#"), ("Eb", "D#"), ("Gb", "F#"), ("Ab", "G#"), ("Bb", "A#")):
        NOTE[f"{_flat}{_o}"] = NOTE[f"{_sharp}{_o}"]


# ---------------------------------------------------------------- helpers (from 迷宮小冒險 and the other sibling apps)


def t_of(dur, sr=SR):
    return np.arange(int(dur * sr)) / sr


def env(n, attack=0.005, release=0.05, sr=SR):
    """Up quickly, down smoothly: no clicks at either end."""
    e = np.ones(n)
    a, r = max(1, min(n, int(attack * sr))), max(1, min(n, int(release * sr)))
    e[:a] = np.linspace(0, 1, a) ** 2
    e[-r:] *= np.linspace(1, 0, r) ** 2
    return e


def sweep(f, sr=SR):
    """A sine whose frequency follows the array [f] (Hz per sample)."""
    return np.sin(2 * np.pi * np.cumsum(f) / sr)


def decay(n, tau, sr=SR):
    return np.exp(-np.arange(n) / (tau * sr))


def lowpass(x, cutoff, sr=SR):
    spec = np.fft.rfft(x)
    freqs = np.fft.rfftfreq(len(x), 1 / sr)
    spec *= 1 / (1 + (freqs / cutoff) ** 4)
    return np.fft.irfft(spec, len(x))


def bandpass(x, lo, hi, sr=SR):
    spec = np.fft.rfft(x)
    freqs = np.fft.rfftfreq(len(x), 1 / sr)
    spec *= 1 / (1 + (lo / np.maximum(freqs, 1)) ** 4) / (1 + (freqs / hi) ** 4)
    return np.fft.irfft(spec, len(x))


def highpass(x, cutoff, sr=SR):
    spec = np.fft.rfft(x)
    freqs = np.fft.rfftfreq(len(x), 1 / sr)
    spec *= 1 / (1 + (cutoff / np.maximum(freqs, 1e-3)) ** 4)
    return np.fft.irfft(spec, len(x))


def norm(x):
    return x / max(1e-9, np.abs(x).max())


def partial(freq, t, sr):
    """A sine at [freq], or silence if it is too high for [sr] (it would fold
    back down as a wrong note)."""
    return np.sin(2 * np.pi * freq * t) if freq < 0.45 * sr else np.zeros_like(t)


def bell(freq, dur=0.5, sr=SR, bright=1.0):
    """A soft glockenspiel note: a few partials, the high ones dying first."""
    t = t_of(dur, sr)
    x = (partial(freq, t, sr) * np.exp(-t / (dur * 0.35))
         + 0.35 * bright * partial(freq * 2.76, t, sr) * np.exp(-t / (dur * 0.12))
         + 0.15 * bright * partial(freq * 5.4, t, sr) * np.exp(-t / (dur * 0.06)))
    return x * env(len(t), 0.002, 0.03, sr)


def marimba(freq, dur=0.5, sr=SR):
    t = t_of(dur, sr)
    x = partial(freq, t, sr) * np.exp(-t / (dur * 0.3)) + 0.2 * partial(freq * 4, t, sr) * np.exp(-t / (dur * 0.05))
    return x * env(len(t), 0.003, 0.03, sr)


def place(total, parts, sr=SR):
    """[parts]: (start seconds, signal) mixed into [total] seconds."""
    out = np.zeros(int(total * sr))
    for start, sig in parts:
        i = int(start * sr)
        j = min(len(out), i + len(sig))
        out[i:j] += sig[: j - i]
    return out


def tune_loop(seconds, notes, sr=LOOP_SR):
    """[notes]: (start seconds, signal); what rings past [seconds] wraps to the start."""
    n = int(round(seconds * sr))
    tail = max(len(sig) + int(start * sr) for start, sig in notes) - n
    out = np.zeros(n + max(0, tail))
    for start, sig in notes:
        i = int(start * sr)
        out[i:i + len(sig)] += sig
    loop = out[:n].copy()
    if tail > 0:
        loop[:tail] += out[n:]
    return loop


def resonator(x, freq, bw, sr=SR, block=64):
    """A two-pole resonance at [freq] Hz (a number, or one per sample, for a
    sound that changes) of bandwidth [bw] Hz."""
    freq = np.broadcast_to(np.asarray(freq, dtype=float), x.shape)
    y, zi = np.zeros_like(x), np.zeros(2)
    r = np.exp(-np.pi * bw / sr)
    for i in range(0, len(x), block):
        th = 2 * np.pi * freq[i] / sr
        y[i:i + block], zi = lfilter([1 - r], [1, -2 * r * np.cos(th), r * r], x[i:i + block], zi=zi)
    return y


def voice(f0, formants, rng, breath=0.03, rough=0.0, sr=SR):
    """A voice at pitch [f0] (Hz per sample) through [formants]: (Hz or Hz
    per sample, bandwidth, gain). [rough] jitters the pitch, for a growl."""
    n = len(f0)
    if rough:
        f0 = f0 * (1 + rough * lowpass(rng.standard_normal(n), 60, sr) * 3)
    buzz = 2 * (np.cumsum(f0) / sr % 1) - 1 + breath * rng.standard_normal(n)
    out = np.zeros(n)
    for f, bw, gain in formants:
        y = resonator(buzz, f, bw, sr)
        out += gain * y / max(1e-9, np.abs(y).max())
    return lowpass(out, 3800, sr)  # soft, not a kazoo


def ease(u):
    """0 to 1, smoothly, over u in 0..1."""
    u = np.clip(u, 0, 1)
    return u * u * (3 - 2 * u)


def glide(t, *points):
    """A value that moves smoothly between (time, value) [points]."""
    ts, vs = zip(*points)
    out = np.interp(t, ts, vs)
    return lowpass(out - out.mean(), 25) + out.mean() if len(t) > 64 else out


def bubble(rng, sr=SR, low=(300, 550), rise=(2.2, 3.2), dur=(0.04, 0.08)):
    """One little bubble: a quick rising blip that starts and ends at zero."""
    d = rng.uniform(*dur)
    t = t_of(d, sr)
    f0 = rng.uniform(*low)
    f = np.geomspace(f0, f0 * rng.uniform(*rise), len(t))
    return sweep(f, sr) * np.sin(np.pi * t / d)


def above(name, low):
    """The note called [name] (no octave) at or just above the note [low]."""
    for o in range(1, 9):
        if NOTE[f"{name}{o}"] >= NOTE[low] * 0.999:
            return f"{name}{o}"
    raise ValueError(name)


def spans(bars, beats_per_bar):
    """Bars like "F" or "Gm-C" (two chords, half a bar each) -> (beat, length in beats, chord)."""
    out = []
    for i, bar in enumerate(bars):
        parts = bar.split("-")
        each = beats_per_bar / len(parts)
        out += [(i * beats_per_bar + k * each, each, c) for k, c in enumerate(parts)]
    return out


def melody(tune, beat, start=0.0, swing=0.0, bars=None, beats_per_bar=4):
    """[tune]: (note or None for a rest, beats) one after another ->
    (seconds, note, seconds long). [swing] (in beats) delays each note that
    falls halfway through a beat, for a lilt. [bars]: check the tune fills them."""
    if bars is not None:
        assert abs(sum(b for _, b in tune) - bars * beats_per_bar) < 1e-9, tune
    out, b = [], 0.0
    for name, beats in tune:
        if name:
            late = swing if abs(b % 1 - 0.5) < 1e-6 else 0.0
            out.append((start + (b + late) * beat, name, (beats - late) * beat))
        b += beats
    return out


def root_of(chord):
    return chord[:2] if len(chord) > 1 and chord[1] in "#b" else chord[0]


def pluck_bass(freq, dur=1.0, sr=LOOP_SR):
    """A plucked double bass: round, short, warm."""
    t = t_of(dur, sr)
    x = (partial(freq, t, sr) * np.exp(-t / (dur * 0.35))
         + 0.45 * partial(freq * 2, t, sr) * np.exp(-t / (dur * 0.15))
         + 0.15 * partial(freq * 3, t, sr) * np.exp(-t / (dur * 0.08)))
    return x * env(len(t), 0.006, 0.08, sr)


def metal(freq, dur, sr=SR, ratios=(1, 1.59, 2.14, 2.65, 3.15), amps=(1, .6, .45, .3, .2), taus=(.5, .3, .2, .15, .1)):
    """A small metal ting (a bell, a coin): partials that are not
    whole-number multiples; [taus] are fractions of [dur]."""
    t = t_of(dur, sr)
    x = sum(a * partial(freq * r, t, sr) * np.exp(-t / (dur * k)) for r, a, k in zip(ratios, amps, taus))
    return x * env(len(t), 0.0008, 0.03, sr)


def shaker(rng, sr=LOOP_SR, dur=0.06, lo=3000, hi=7000):
    n = int(dur * sr)
    return norm(bandpass(rng.standard_normal(n), lo, hi, sr)) * env(n, 0.006, dur * 0.8, sr)


def kick(sr=LOOP_SR, dur=0.16):
    n = int(dur * sr)
    return sweep(np.geomspace(130, 55, n), sr) * decay(n, 0.05, sr) * env(n, 0.002, 0.04, sr)


def jingle(rng, dur=0.2, sr=SR):
    """A tambourine's little cymbals."""
    t = t_of(dur, sr)
    x = sum(rng.uniform(0.4, 1.0) * partial(f, t, sr) * np.exp(-t / rng.uniform(0.03, 0.07))
            for f in rng.uniform(4500, 9000, 8))
    x += 0.5 * norm(bandpass(rng.standard_normal(len(t)), 5000, 10000, sr)) * np.exp(-t / 0.02)
    return x * env(len(t), 0.001, 0.04, sr)


def noise_through(rng, centre, bw, n, sr=SR):
    """Noise through a resonance that can move: the voice of air and water."""
    return norm(resonator(rng.standard_normal(n), centre, bw, sr))


def soft_piano(freq, dur=2.5, sr=LOOP_SR):
    """A felt piano: a marimba's warm knock and a bell's soft ring, blended,
    over a plain tone that rings a little longer."""
    t = t_of(dur, sr)
    body = (partial(freq, t, sr) * np.exp(-t / (dur * 0.32))
            + 0.25 * partial(freq * 2, t, sr) * np.exp(-t / (dur * 0.12)))
    x = 0.45 * marimba(freq, dur, sr) + 0.3 * bell(freq, dur, sr, bright=0.25) + 0.5 * body
    return x * env(len(t), 0.006, 0.08, sr)


def carry(x, amount=0.3, lo=500, hi=3000, drive=2.5, sr=SR):
    """Phone speakers hardly play anything under about 300 Hz. For a low
    sound, add its own overtones (a soft saturation of it, kept to [lo]..[hi]
    Hz): a phone plays those, and the ear still hears the low note."""
    peak = max(1e-9, np.abs(x).max())
    over = bandpass(np.tanh(drive * x / peak), lo, hi, sr)
    return x + amount * peak * norm(over)


def celesta(freq, dur=1.0, sr=LOOP_SR):
    """A celesta: a felt hammer on a small steel bar over a wooden box. A
    sweet, round tone with a little of its octave, and a soft tick."""
    t = t_of(dur, sr)
    x = (partial(freq, t, sr) * np.exp(-t / (dur * 0.3))
         + 0.25 * partial(freq * 2, t, sr) * np.exp(-t / (dur * 0.12))
         + 0.06 * partial(freq * 4.1, t, sr) * np.exp(-t / 0.02))
    return x * env(len(t), 0.0015, 0.05, sr)


def chime(freq, dur, sr=SR):
    """A soft, warm bell: whole-number partials (no glockenspiel clang), two
    tones a hair apart so it shimmers as it rings."""
    t = t_of(dur, sr)
    x = ((partial(freq, t, sr) + 0.5 * partial(freq * 1.003, t, sr)) * np.exp(-t / (dur * 0.38))
         + 0.28 * partial(freq * 2.0, t, sr) * np.exp(-t / (dur * 0.16))
         + 0.1 * partial(freq * 3.01, t, sr) * np.exp(-t / (dur * 0.07)))
    return x * env(len(t), 0.003, 0.08, sr)


def plink(freq, dur=0.25, sr=LOOP_SR):
    """A little glassy plink, like a bead dropped on a toy block."""
    t = t_of(dur, sr)
    x = partial(freq, t, sr) * np.exp(-t / 0.05) + 0.3 * partial(freq * 2.76, t, sr) * np.exp(-t / 0.012)
    return x * env(len(t), 0.0008, 0.03, sr)


def clack(rng, sr=LOOP_SR, dur=0.06):
    """Two wooden blocks knocked together: a short, hollow clack."""
    n = int(dur * sr)
    t = np.arange(n) / sr
    hit = rng.standard_normal(n) * np.exp(-t / 0.002)
    x = norm(resonator(hit, 1250, 120, sr)) + 0.6 * norm(resonator(hit, 2650, 200, sr))
    return x * np.exp(-t / 0.018) * env(n, 0.0005, 0.015, sr)


def a_weight(x, sr):
    """[x] as the ear hears it out of a phone: A-weighting (the ear is less
    sensitive to low and very high sounds) and nothing under about 250 Hz."""
    spec = np.fft.rfft(x)
    f2 = np.fft.rfftfreq(len(x), 1 / sr) ** 2
    ra = 12194 ** 2 * f2 ** 2 / ((f2 + 20.6 ** 2) * np.sqrt((f2 + 107.7 ** 2) * (f2 + 737.9 ** 2)) * (f2 + 12194 ** 2))
    phone = 1 / (1 + (250 ** 2 / np.maximum(f2, 1e-6)) ** 2)
    return np.fft.irfft(spec * ra * 1.2589 * phone, len(x))


def loudness(x, sr):
    """How loud [x] sounds, roughly, in dB: the weighted power in 200 ms
    windows (the ear adds up about that long, so a click sounds softer than
    a note as loud), over the windows within 20 dB of the loudest one."""
    y = a_weight(np.asarray(x, dtype=np.float64), sr) ** 2
    w, hop = int(0.2 * sr), int(0.025 * sr)
    y = np.concatenate([y, np.zeros(max(0, w - len(y)))])
    c = np.concatenate([[0], np.cumsum(y)])
    e = (c[w::hop] - c[:len(c) - w:hop]) / w
    return 10 * np.log10(max(1e-12, np.mean(e[e >= e.max() * 0.01])))


QUALITY = {"": (0, 4, 7), "m": (0, 3, 7), "7": (0, 4, 7, 10), "m7": (0, 3, 7, 10),
           "maj7": (0, 4, 7, 11), "7sus": (0, 5, 7, 10)}


def chord_tones(chord, low):
    """The notes (Hz) of [chord], root first, the root at or just above [low]."""
    root = root_of(chord)
    f = NOTE[above(root, low)]
    return [f * 2 ** (s / 12) for s in QUALITY[chord[len(root):]]]


def chord_at(span_list, b):
    """The chord sounding at beat [b]."""
    return [c for s, _, c in span_list if s <= b + 1e-9][-1]


def harmonics(f, sr=SR, tilt=1.0):
    """A bright tone at pitch [f] (Hz per sample) with every harmonic up to
    near half the sample rate, each 1/k^[tilt]: a sawtooth without the
    harsh folded-back tones."""
    ph = 2 * np.pi * np.cumsum(f) / sr
    top = int(0.45 * sr // np.max(f))
    return sum(np.sin(k * ph) / k ** tilt for k in range(1, max(2, top + 1)))


def pizz(freq, dur=0.5, sr=LOOP_SR, pos=0.14):
    """A pizzicato string, plucked with a finger: it rings only a moment,
    the high harmonics dying first; low notes ring a little longer."""
    t = t_of(dur, sr)
    tau = min(0.3, 0.07 + 50 / freq)
    x = np.zeros_like(t)
    for k in range(1, 9):
        x += abs(np.sin(np.pi * k * pos)) / k * partial(freq * k, t, sr) * np.exp(-t * (1 + 0.7 * (k - 1)) / tau)
    return x * env(len(t), 0.0012, 0.04, sr)


def toy_horn(freq, dur, sr=SR):
    """A soft toy trumpet: every harmonic, the high ones quieter, opening up
    as it speaks; a little vibrato on a long note."""
    t = t_of(dur, sr)
    vib = 1 + 0.006 * np.sin(2 * np.pi * 5.5 * t) * ease((t - 0.15) / 0.2)
    ph = 2 * np.pi * np.cumsum(freq * vib) / sr
    opening = ease(t / 0.05)
    x = np.zeros_like(t)
    for k in range(1, 9):
        if freq * k < 0.4 * sr:
            x += (1 if k == 1 else opening) / k ** 1.4 * np.sin(k * ph)
    return lowpass(x, 3500, sr) * env(len(t), 0.015, min(0.1, dur * 0.4), sr)


def pad(chord, length, low="Ab3", sr=LOOP_SR):
    """A warm pad, like soft strings far away: the chord held, fading in over
    most of a second and out over a second after [length] (so it melts into
    the next), each tone three voices a hair apart (so it breathes), with a
    little of their octave."""
    d = length + 1.0
    t = t_of(d, sr)
    shape = ease(t / 0.7) * (1 - ease((t - length + 0.1) / 1.0))
    x = np.zeros_like(t)
    for f in chord_tones(chord, low)[:3]:
        for det in (0.996, 1.0, 1.004):
            x += np.sin(2 * np.pi * f * det * t) + 0.22 * np.sin(2 * np.pi * 2 * f * det * t)
    return x * shape / 9


def chirp(points, dur, sr=SR):
    """A bird's chirp: a pure whistle whose pitch follows (fraction of
    [dur], Hz) [points], swelling in and out."""
    t = t_of(dur, sr)
    fs, hz = zip(*points)
    f = np.interp(t / dur, fs, hz)
    return (sweep(f, sr) + 0.12 * sweep(2 * f, sr)) * np.sin(np.pi * t / dur) ** 1.2


def yay(rng, f, dur=0.32, size=1.15):
    """A small, happy "yay!" (ye-ay), jumping up."""
    t = t_of(dur)
    f0 = glide(t, (0, f), (0.08, f * 1.25), (dur, f * 1.05))
    f1 = np.interp(t, [0, 0.05, 0.2, dur], [300, 750, 700, 450]) * size
    f2 = np.interp(t, [0, 0.05, 0.2, dur], [2300, 1800, 1900, 2200]) * size
    return voice(f0, [(f1, 130, 1.0), (f2, 180, 0.55), (3000 * size, 300, 0.12)], rng, breath=0.1) * env(len(t), 0.02, 0.1)



def ocarina(freq, dur, rng, sr=LOOP_SR):
    """A clay ocarina: an almost pure, round, hollow tone (a vessel flute has
    hardly any overtones), a soft breath of air around it, a little puff as
    each note speaks and a slow vibrato on long notes."""
    t = t_of(dur, sr)
    n = len(t)
    vib = 1 + 0.005 * np.sin(2 * np.pi * 4.8 * t) * ease((t - 0.25) / 0.3)
    ph = 2 * np.pi * np.cumsum(freq * vib) / sr
    x = np.sin(ph) + 0.06 * np.sin(2 * ph) + 0.035 * np.sin(3 * ph)
    breath = 0.045 * norm(bandpass(rng.standard_normal(n), freq * 0.8, min(freq * 2.5, 0.45 * sr), sr))
    puff = 0.12 * norm(bandpass(rng.standard_normal(n), freq, min(freq * 4, 0.45 * sr), sr)) * np.exp(-t / 0.02)
    return (x + breath + puff) * env(n, 0.03, min(0.08, dur * 0.35), sr)
def recorder(freq, dur, rng, sr=LOOP_SR):
    """A soprano recorder: a clear, sweet tone, a little brighter than a
    flute (a touch of its octave and twelfth), the quick "t" of the tongue
    as each note starts, and no vibrato."""
    t = t_of(dur, sr)
    n = len(t)
    ph = 2 * np.pi * freq * t
    x = np.sin(ph) + 0.22 * np.sin(2 * ph) + 0.1 * np.sin(3 * ph) + 0.04 * np.sin(4 * ph)
    breath = 0.04 * norm(resonator(rng.standard_normal(n), freq * 2, 600, sr))
    chiff = 0.25 * norm(bandpass(rng.standard_normal(n), freq * 2, min(freq * 6, 0.45 * sr), sr)) * np.exp(-t / 0.008)
    return (x + breath + chiff) * env(n, 0.012, min(0.06, dur * 0.3), sr)
def harp(freq, dur=1.6, sr=LOOP_SR):
    """A harp string, plucked with the fingertip: round and warm, ringing
    long, the high harmonics fading first."""
    t = t_of(dur, sr)
    x = np.zeros_like(t)
    for k in range(1, 8):
        a = abs(np.sin(np.pi * k * 0.3)) / k ** 1.5
        x += a * partial(freq * k, t, sr) * np.exp(-t / (dur * 0.35 / (1 + 0.6 * (k - 1))))
    return x * env(len(t), 0.004, 0.08, sr)
def toy_piano(freq, dur=0.7, sr=LOOP_SR):
    """A toy piano: a little hammer on a metal rod. A sweet, tinkly note
    (the rod's next modes are not whole multiples) with a second rod a hair
    out of tune, as on a real toy, and a tiny wooden knock."""
    t = t_of(dur, sr)
    x = ((partial(freq, t, sr) + 0.35 * partial(freq * 1.004, t, sr)) * np.exp(-t / (dur * 0.3))
         + 0.3 * partial(freq * 2.0, t, sr) * np.exp(-t / (dur * 0.1))
         + 0.18 * partial(freq * 5.4, t, sr) * np.exp(-t / 0.02)
         + 0.1 * partial(1250, t, sr) * np.exp(-t / 0.006))
    return x * env(len(t), 0.0015, 0.06, sr)
def fm_bell(freq, dur=1.2, sr=LOOP_SR, ratio=1.0, index=1.2):
    """A soft electric bell: one sine wobbling another so fast that it makes
    new overtones, which fade as the note rings (like a struck tine), with a
    faint glassy tine above."""
    t = t_of(dur, sr)
    idx = index * np.exp(-t / 0.15)
    x = np.sin(2 * np.pi * freq * t + idx * np.sin(2 * np.pi * freq * ratio * t)) * np.exp(-t / (dur * 0.35))
    x += 0.06 * partial(freq * 4.03, t, sr) * np.exp(-t / 0.02)
    return x * env(len(t), 0.002, 0.08, sr)
def hum_voice(freq, dur, rng, sr=LOOP_SR):
    """Someone humming softly, mouth closed ("mmm"): a gentle voice that
    comes out mostly as its lowest tone, a slow vibrato and a little drift,
    a breath of air."""
    t = t_of(dur, sr)
    n = len(t)
    drift = 1 + 0.002 * norm(lowpass(rng.standard_normal(n), 3, sr))
    f0 = freq * drift * (1 + 0.005 * np.sin(2 * np.pi * 5.2 * t) * ease((t - 0.3) / 0.4))
    x = voice(f0, [(300, 90, 1.0), (900, 150, 0.12), (2400, 250, 0.03)], rng, breath=0.04, sr=sr)
    return lowpass(x, 1400, sr) * env(n, 0.08, min(0.25, dur * 0.4), sr)
def sleigh(rng, dur=0.22, sr=LOOP_SR):
    """Sleigh bells shaken once: a few tiny round bells, each a moment
    apart, and a little rattle."""
    t = t_of(dur, sr)
    x = np.zeros_like(t)
    for f in rng.uniform(2800, 5200, 6):
        d = rng.uniform(0, 0.02)
        tt = np.clip(t - d, 0, None)
        x += rng.uniform(0.5, 1) * (partial(f, tt, sr) + 0.3 * partial(2.4 * f, tt, sr)) * np.exp(-tt / rng.uniform(0.04, 0.08))
    rattle = norm(bandpass(rng.standard_normal(len(t)), 3500, 7000, sr)) * np.exp(-t / 0.03)
    return (norm(x) + 0.3 * rattle) * env(len(t), 0.001, 0.05, sr)
def clap(rng, sr=LOOP_SR):
    """A soft hand clap: three quick slaps of air close together, and the
    clap itself."""
    n = int(0.12 * sr)
    shape = np.zeros(n)
    for k, d in enumerate((0, 0.008, 0.017, 0.026)):
        i = int(d * sr)
        shape[i:] += (0.6 if k < 3 else 1) * np.exp(-np.arange(n - i) / sr / (0.004 if k < 3 else 0.03))
    return norm(bandpass(rng.standard_normal(n), 900, 4000, sr) * shape) * env(n, 0.0005, 0.03, sr)


# ---------------------------------------------------------------- new instruments


def music_box(freq, dur=1.4, sr=LOOP_SR):
    """A music box: a pin plucks a steel comb tooth. A sweet, pure note with a
    second tooth a hair out of tune (so it shimmers), the tooth's own high
    overtone (not a whole multiple) dying quickly, a touch of its octave
    from the wooden box, and the tiny tick of the pin."""
    t = t_of(dur, sr)
    x = ((partial(freq, t, sr) + 0.4 * partial(freq * 1.0025, t, sr)) * np.exp(-t / (dur * 0.33))
         + 0.22 * partial(freq * 2.0, t, sr) * np.exp(-t / (dur * 0.12))
         + 0.2 * partial(freq * 2.76, t, sr) * np.exp(-t / 0.05)
         + 0.07 * partial(freq * 5.4, t, sr) * np.exp(-t / 0.012)
         + 0.05 * partial(3100, t, sr) * np.exp(-t / 0.004))
    return x * env(len(t), 0.001, 0.06, sr)


def kalimba(freq, dur=0.9, sr=LOOP_SR):
    """A kalimba (thumb piano): a thumb plucks a metal tine over a wooden
    box. Warm and round, mostly its lowest tone, the tine's high overtone
    (about six times up) dying at once, and the soft "tk" of the thumbnail."""
    t = t_of(dur, sr)
    x = (partial(freq, t, sr) * np.exp(-t / (dur * 0.3))
         + 0.12 * partial(freq * 2.0, t, sr) * np.exp(-t / (dur * 0.1))
         + 0.3 * partial(freq * 6.27, t, sr) * np.exp(-t / 0.018)
         + 0.08 * np.sin(2 * np.pi * 1800 * t) * np.exp(-t / 0.003))
    return x * env(len(t), 0.0015, 0.06, sr)


def ukulele(freq, dur=0.6, sr=LOOP_SR, pos=0.22):
    """A ukulele string, nylon, plucked with the thumb: soft, round, a little
    hollow (the small body rings about 500 Hz), dying in half a second."""
    t = t_of(dur, sr)
    x = np.zeros_like(t)
    tau = min(0.25, 0.08 + 40 / freq)
    for k in range(1, 10):
        a = abs(np.sin(np.pi * k * pos)) / k ** 1.2
        x += a * partial(freq * k, t, sr) * np.exp(-t * (1 + 0.8 * (k - 1)) / tau)
    body = norm(resonator(x, 520, 300, sr)) * np.abs(x).max()
    return (x + 0.35 * body) * env(len(t), 0.0015, 0.05, sr)


def strum(chord, low="G3", dur=0.6, sr=LOOP_SR, up=False, gap=0.014):
    """A ukulele strum: the chord's notes (and the octave of the root), one
    string after another, [gap] seconds apart; [up] strums from the top."""
    tones = chord_tones(chord, low)[:3]
    tones = tones + [2 * tones[0]]
    if up:
        tones = tones[::-1]
    return place(dur + gap * len(tones), [(gap * k, ukulele(f, dur, sr)) for k, f in enumerate(tones)], sr)


def xylophone(freq, dur=0.45, sr=LOOP_SR):
    """A toy xylophone: a hard mallet on a bright wooden bar. Short and
    bright: the bar's third tone rings with it, and the mallet clicks."""
    t = t_of(dur, sr)
    x = (partial(freq, t, sr) * np.exp(-t / (dur * 0.25))
         + 0.45 * partial(freq * 3.0, t, sr) * np.exp(-t / (dur * 0.07))
         + 0.12 * partial(freq * 6.0, t, sr) * np.exp(-t / 0.01)
         + 0.1 * np.sin(2 * np.pi * 2400 * t) * np.exp(-t / 0.003))
    return x * env(len(t), 0.001, 0.04, sr)


def vibes(freq, dur=1.4, sr=LOOP_SR):
    """A vibraphone: a soft electric bell with the slow wobble of its fans."""
    t = t_of(dur, sr)
    return fm_bell(freq, dur, sr, index=0.8) * (0.8 + 0.2 * np.sin(2 * np.pi * 4.5 * t))


def woodblock(rng, sr=LOOP_SR):
    """A small wood block, tapped: a bright, hollow "tok"."""
    return clack(rng, sr, 0.05)


def triangle(dur=1.0, sr=LOOP_SR, freq=4100):
    return metal(freq, dur, sr, ratios=(1, 2.7, 4.1), amps=(1, .4, .2), taus=(.5, .2, .1))


# ---------------------------------------------------------------- music


class Tune:
    """A tune: its length, the tune itself and the band (lists of (seconds,
    signal)), and the soft top it is played through."""

    def __init__(self, seconds, lead, band, cutoff):
        self.seconds, self.lead, self.band, self.cutoff = seconds, lead, band, cutoff

    def render(self, lead=True, band=True):
        x = tune_loop(self.seconds, (self.lead if lead else []) + (self.band if band else []))
        return lowpass(x, self.cutoff, LOOP_SR)


def beats_in(sp, b):
    """The (start beat, length, chord) of the chord sounding at beat [b]."""
    return [s for s in sp if s[0] <= b + 1e-9][-1]


def music_morning():
    """早上 (waking up): bright and fresh, 4/4 in C, 120 to the minute. A
    music box sings the tune (C-E-G, up like the sun), a glockenspiel joins
    an octave up from bar 9; a ukulele strums down on one and three and up
    on the "and" of two and four; a plucked bass; a soft kick; a shaker on
    the off-beats. 12 bars, 24 s."""
    beat = 0.5
    bars = ["C", "C", "F", "G", "C", "Am", "F", "G7", "C", "F", "C-G7", "C"]
    tune = [("C5", .5), ("E5", .5), ("G5", 1), ("E5", .5), ("G5", .5), ("C6", 1),
            ("B5", 1), ("G5", .5), ("E5", .5), ("G5", 2),
            ("A5", .5), ("C6", .5), ("A5", 1), ("F5", .5), ("A5", .5), ("C6", 1),
            ("B5", 1), ("G5", 1), ("D5", .5), ("F5", .5), ("G5", 1),
            ("C5", .5), ("E5", .5), ("G5", 1), ("E5", .5), ("G5", .5), ("C6", 1),
            ("A5", 1), ("E5", .5), ("C5", .5), ("E5", 2),
            ("F5", .5), ("A5", .5), ("C6", 1), ("A5", .5), ("F5", .5), ("A5", 1),
            ("G5", 1.5), ("F5", .5), ("D5", 1), ("G5", 1),
            ("E5", .5), ("G5", .5), ("C6", 1), ("D6", .5), ("C6", .5), ("B5", 1),
            ("A5", 1), ("C6", .5), ("A5", .5), ("F5", 1), ("A5", 1),
            ("G5", .5), ("E5", .5), ("C5", 1), ("D5", .5), ("F5", .5), ("B4", 1),
            ("C5", 2), (None, 2)]
    rng = np.random.default_rng(201)
    sp = spans(bars, 4)
    lead, band = [], []
    for at, n, d in melody(tune, beat, bars=12):
        f = NOTE[n]
        lead.append((at, 0.5 * music_box(f, max(0.8, d + 0.5))))
        if at >= 32 * beat - 1e-9:
            lead.append((at, 0.06 * bell(2 * f, 0.4, LOOP_SR, bright=0.4)))
    for b in range(48):
        chord = chord_at(sp, b)
        if b % 2 == 0:
            band.append((b * beat, 0.16 * strum(chord, "G3", 0.5)))
            band.append((b * beat, 0.2 * kick()))
            r = NOTE[above(root_of(chord), "C2")]
            band.append((b * beat, 0.6 * pluck_bass(r if b % 4 == 0 else r * 2 ** (7 / 12), 0.6)))
        else:
            band.append(((b + 0.5) * beat, 0.1 * strum(chord, "G3", 0.35, up=True)))
        band.append(((b + 0.5) * beat, 0.035 * shaker(rng, dur=0.05)))
    return Tune(len(bars) * 4 * beat, lead, band, 5000)


def music_day():
    """白天 (kindergarten hours): playful and quick, 4/4 in F, 136 to the
    minute. A toy xylophone plays the tune; a ukulele chord on every beat; a
    kick on one and three, a soft clap on two and four; a plucked bass. From
    bar 9 a glockenspiel answers the tune on the beats. 12 bars, 21 s."""
    beat = 0.44
    bars = ["F", "Bb", "F", "C7", "F", "Bb", "C7", "F", "Dm", "Bb", "F-C7", "F"]
    tune = [("F5", .5), ("G5", .5), ("A5", .5), ("F5", .5), ("C6", 1), ("A5", 1),
            ("Bb5", .5), ("A5", .5), ("G5", .5), ("Bb5", .5), ("D6", 1), ("Bb5", 1),
            ("A5", .5), ("F5", .5), ("C5", .5), ("F5", .5), ("A5", 1), ("C6", 1),
            ("Bb5", .5), ("G5", .5), ("E5", .5), ("G5", .5), ("C5", 1), (None, 1),
            ("F5", .5), ("A5", .5), ("C6", .5), ("A5", .5), ("F5", 1), ("A5", 1),
            ("D6", .5), ("C6", .5), ("Bb5", .5), ("A5", .5), ("Bb5", 1), ("D6", 1),
            ("C6", .5), ("Bb5", .5), ("G5", .5), ("E5", .5), ("G5", 1), ("Bb5", 1),
            ("A5", 1), ("F5", 1), ("C6", 1), (None, 1),
            ("D6", .5), ("C6", .5), ("A5", .5), ("F5", .5), ("A5", 1), ("D6", 1),
            ("D6", .5), ("C6", .5), ("Bb5", .5), ("D6", .5), ("F6", 1), ("D6", 1),
            ("C6", .5), ("A5", .5), ("F5", .5), ("C5", .5), ("E5", .5), ("G5", .5), ("Bb5", .5), ("G5", .5),
            ("F5", 1.5), ("A5", .5), ("F5", 1), (None, 1)]
    rng = np.random.default_rng(202)
    sp = spans(bars, 4)
    lead, band = [], []
    for at, n, d in melody(tune, beat, bars=12):
        f = NOTE[n]
        lead.append((at, 0.5 * xylophone(f, max(0.4, d + 0.15))))
        if at >= 32 * beat - 1e-9 and abs(at / beat - round(at / beat)) < 1e-6:
            lead.append((at + 0.5 * beat, 0.05 * bell(f, 0.3, LOOP_SR, bright=0.4)))
    for b in range(48):
        chord = chord_at(sp, b)
        band.append((b * beat, (0.14 if b % 2 == 0 else 0.1) * strum(chord, "G3", 0.3, up=b % 2 == 1)))
        r = NOTE[above(root_of(chord), "C2")]
        if b % 2 == 0:
            band.append((b * beat, 0.22 * kick()))
            band.append((b * beat, 0.6 * pluck_bass(r if b % 4 == 0 else r * 2 ** (7 / 12), 0.5)))
        else:
            band.append((b * beat, 0.07 * clap(rng)))
        band.append(((b + 0.5) * beat, 0.03 * shaker(rng, dur=0.045)))
    return Tune(len(bars) * 4 * beat, lead, band, 5500)


def music_afternoon():
    """下午 (snack, play, chores): bouncy, 4/4 in G with a swing, 120 to the
    minute. A kalimba plays the tune; pizzicato strings go oom (one, three)
    and a toy piano answers pah (two, four); a swinging shaker; from bar 9
    the toy piano doubles the tune. 12 bars, 24 s."""
    beat, swing = 0.5, 0.15
    bars = ["G", "Em", "C", "D7", "G", "Em", "C-D7", "G", "C", "G", "D7", "G"]
    tune = [("G5", .5), ("B5", .5), ("D6", 1), ("B5", .5), ("G5", .5), ("B5", 1),
            ("E5", .5), ("G5", .5), ("B5", 1), ("G5", .5), ("E5", .5), ("G5", 1),
            ("C5", .5), ("E5", .5), ("G5", 1), ("A5", .5), ("G5", .5), ("E5", 1),
            ("D5", .5), ("F#5", .5), ("A5", 1), ("C6", .5), ("A5", .5), ("F#5", 1),
            ("G5", .5), ("B5", .5), ("D6", 1), ("E6", .5), ("D6", .5), ("B5", 1),
            ("G5", .5), ("E5", .5), ("B5", 1), ("G5", .5), ("E5", .5), ("B5", 1),
            ("C6", .5), ("A5", .5), ("E5", 1), ("A5", .5), ("F#5", .5), ("D5", 1),
            ("G5", 1.5), ("B5", .5), ("G5", 1), (None, 1),
            ("E6", .5), ("D6", .5), ("C6", 1), ("E6", .5), ("G5", .5), ("C6", 1),
            ("D6", .5), ("B5", .5), ("G5", 1), ("B5", .5), ("D6", .5), ("G6", 1),
            ("F#6", .5), ("D6", .5), ("A5", 1), ("C6", .5), ("A5", .5), ("F#5", 1),
            ("G5", 2), (None, 2)]
    rng = np.random.default_rng(203)
    sp = spans(bars, 4)
    lead, band = [], []
    for at, n, d in melody(tune, beat, swing=swing, bars=12):
        f = NOTE[n]
        lead.append((at, 0.55 * kalimba(f, max(0.6, d + 0.3))))
        if at >= 32 * beat - 1e-9:
            lead.append((at, 0.14 * toy_piano(f, 0.5)))
    for b in range(48):
        chord = chord_at(sp, b)
        r = NOTE[above(root_of(chord), "D2")]
        if b % 2 == 0:
            band.append((b * beat, 0.8 * pizz(r if b % 4 == 0 else r * 2 ** (7 / 12), 0.5)))
            band.append((b * beat, 0.16 * kick()))
        else:
            band += [(b * beat + 0.006 * k, 0.13 * toy_piano(f, 0.35)) for k, f in enumerate(chord_tones(chord, "G4")[:3])]
        band.append((b * beat, 0.02 * shaker(rng, dur=0.05)))
        band.append(((b + 0.5 + swing) * beat, 0.04 * shaker(rng, dur=0.05)))
    return Tune(len(bars) * 4 * beat, lead, band, 5000)


def music_evening():
    """傍晚 (dinner, bath): warm and a little slower, a 3/4 waltz in E flat,
    100 to the minute. A felt piano sings the tune with a celesta on it from
    bar 7; a harp rocks up each chord; a warm pad; a round plucked bass on
    one. 12 bars, 22 s."""
    beat = 0.6
    bars = ["Eb", "Ab", "Bb7", "Eb", "Cm", "Ab", "Bb7", "Eb", "Ab", "Eb", "Bb7", "Eb"]
    tune = [("G5", 1), ("Bb5", 1), ("Eb6", 1),
            ("C6", 2), ("Ab5", 1),
            ("Bb5", 1), ("Ab5", 1), ("F5", 1),
            ("G5", 3),
            ("Eb5", 1), ("G5", 1), ("C6", 1),
            ("Ab5", 2), ("C6", 1),
            ("Bb5", 1), ("D5", 1), ("F5", 1),
            ("Eb5", 3),
            ("C6", 1), ("Eb6", 1), ("C6", 1),
            ("Bb5", 2), ("G5", 1),
            ("Ab5", 1), ("F5", 1), ("D5", 1),
            ("Eb5", 2), (None, 1)]
    lead, band = [], []
    for at, n, d in melody(tune, beat, bars=12, beats_per_bar=3):
        f = NOTE[n]
        lead.append((at, 0.5 * soft_piano(f, max(1.0, d + 0.6))))
        if at >= 18 * beat - 1e-9:
            lead.append((at, 0.16 * celesta(f, max(0.8, d + 0.4))))
    for b, length, chord in spans(bars, 3):
        c = chord_tones(chord, "Eb3")
        for k, f in enumerate([c[0], c[2], 2 * c[0], 2 * c[1], 2 * c[0], c[2]]):
            band.append(((b + 0.5 * k) * beat, (0.22 if k == 0 else 0.14) * harp(f, 1.4)))
        band.append((b * beat, 0.16 * pad(chord, length * beat, low="Eb3")))
        band.append((b * beat, 0.55 * pluck_bass(NOTE[above(root_of(chord), "Eb2")], 1.0)))
    return Tune(len(bars) * 3 * beat, lead, band, 4000)


def music_night():
    """晚上 (bedtime): a lullaby, very soft and slow, 6/8 in D flat. A music
    box alone sings the tune over a glassy pad; a harp touches the root and
    fifth on the two beats of each bar; a soft low note on one. 10 bars,
    22 s."""
    eighth = 0.36
    bars = ["Db", "Gb", "Db", "Ab7", "Db", "Bbm", "Gb", "Ab7", "Db", "Db"]
    tune = [("F5", 2), ("Ab5", 1), ("Db6", 3),
            ("Bb5", 2), ("Ab5", 1), ("Gb5", 3),
            ("F5", 2), ("Ab5", 1), ("F5", 2), ("Eb5", 1),
            ("Eb5", 3), ("C5", 3),
            ("Db5", 2), ("F5", 1), ("Ab5", 3),
            ("Bb5", 2), ("Db6", 1), ("F5", 3),
            ("Gb5", 2), ("Bb5", 1), ("Db6", 2), ("Bb5", 1),
            ("Ab5", 3), ("Gb5", 2), ("Eb5", 1),
            ("F5", 2), ("Eb5", 1), ("Db5", 3),
            ("Db5", 3), (None, 3)]
    lead, band = [], []
    for at, n, d in melody(tune, eighth, bars=10, beats_per_bar=6):
        lead.append((at, 0.6 * music_box(NOTE[n], max(1.4, d + 0.8))))
    for b, length, chord in spans(bars, 6):
        c = chord_tones(chord, "Db3")
        band.append((b * eighth, 0.36 * harp(c[0], 1.6)))
        band.append(((b + 3) * eighth, 0.26 * harp(c[2], 1.4)))
        band.append(((b + 4) * eighth, 0.18 * harp(2 * c[0], 1.2)))
        band.append((b * eighth, 0.24 * pad(chord, length * eighth, low="Db3")))
        band.append((b * eighth, 0.4 * pluck_bass(NOTE[above(root_of(chord), "Db2")], 1.6)))
    return Tune(len(bars) * 6 * eighth, lead, band, 3200)


def music_outside():
    """外面 (the street, the park): a walking tune, 4/4 in D, 120 to the
    minute. A ukulele picks the tune with a marimba under it; a bass walks
    every beat; a wood block taps on two and four; a shaker; from bar 9 a
    glockenspiel an octave up. 12 bars, 24 s."""
    beat = 0.5
    bars = ["D", "G", "A7", "D", "D", "G", "A7-D", "D", "Bm", "G", "A7", "D"]
    tune = [("D5", .5), ("F#5", .5), ("A5", 1), ("F#5", .5), ("A5", .5), ("D6", 1),
            ("B5", 1), ("G5", .5), ("B5", .5), ("D6", 2),
            ("C#6", .5), ("A5", .5), ("E5", 1), ("G5", .5), ("E5", .5), ("C#5", 1),
            ("D5", 1.5), ("F#5", .5), ("A5", 1), (None, 1),
            ("A5", .5), ("F#5", .5), ("D5", 1), ("F#5", .5), ("A5", .5), ("D6", 1),
            ("B5", .5), ("D6", .5), ("G5", 1), ("B5", .5), ("G5", .5), ("D5", 1),
            ("E5", .5), ("G5", .5), ("C#6", .5), ("A5", .5), ("F#5", 1), ("D5", 1),
            ("D5", 2), (None, 2),
            ("F#5", .5), ("A5", .5), ("D6", 1), ("B5", .5), ("D6", .5), ("F#6", 1),
            ("G5", .5), ("B5", .5), ("D6", 1), ("G6", .5), ("D6", .5), ("B5", 1),
            ("A5", .5), ("C#6", .5), ("E6", 1), ("C#6", .5), ("A5", .5), ("G5", 1),
            ("F#5", 1), ("D5", 1), ("D5", 1), (None, 1)]
    walk = ["D2 F#2 A2 F#2", "G2 B2 D3 B2", "A2 C#3 E3 G3", "D3 A2 F#2 A2",
            "D2 F#2 A2 F#2", "G2 B2 D3 B2", "A2 E3 D3 A2", "D3 A2 F#2 A2",
            "B2 D3 F#3 D3", "G2 B2 D3 B2", "A2 C#3 E3 G3", "D3 A2 F#2 A2"]
    rng = np.random.default_rng(206)
    lead, band = [], []
    for at, n, d in melody(tune, beat, bars=12):
        f = NOTE[n]
        lead.append((at, 0.55 * ukulele(f, max(0.5, d + 0.2))))
        lead.append((at, 0.22 * marimba(f, 0.4, LOOP_SR)))
        if at >= 32 * beat - 1e-9:
            lead.append((at, 0.05 * bell(2 * f, 0.4, LOOP_SR, bright=0.4)))
    for i, bar in enumerate(walk):
        for k, name in enumerate(bar.split()):
            band.append(((4 * i + k) * beat, 0.65 * pluck_bass(NOTE[name], 0.6)))
    for b in range(48):
        if b % 2 == 1:
            band.append((b * beat, 0.08 * woodblock(rng)))
        band.append(((b + 0.5) * beat, 0.035 * shaker(rng, dur=0.05)))
    return Tune(len(bars) * 4 * beat, lead, band, 5000)


def music_school():
    """幼兒園 (kindergarten): a clapping song, 4/4 in A, 130 to the minute.
    A toy piano plays the tune (notes in pairs, like a song to clap to); hand
    claps on two and four, a kick on one and three; a plucked bass; a
    tambourine on every quaver from bar 9. 12 bars, 22 s."""
    beat = 0.46
    bars = ["A", "D", "E7", "A", "A", "D", "E7", "A", "D", "A", "E7", "A"]
    tune = [("C#6", .5), ("C#6", .5), ("E6", 1), ("C#6", .5), ("A5", .5), ("C#6", 1),
            ("D6", .5), ("D6", .5), ("F#6", 1), ("D6", .5), ("A5", .5), ("D6", 1),
            ("E6", .5), ("D6", .5), ("B5", .5), ("G#5", .5), ("B5", 1), ("E5", 1),
            ("A5", 1), ("C#6", 1), ("A5", 1), (None, 1),
            ("E6", .5), ("E6", .5), ("C#6", 1), ("A5", .5), ("C#6", .5), ("E6", 1),
            ("F#6", .5), ("F#6", .5), ("D6", 1), ("A5", .5), ("D6", .5), ("F#6", 1),
            ("E6", .5), ("G#5", .5), ("B5", .5), ("D6", .5), ("E6", 1), ("D6", 1),
            ("C#6", 1), ("A5", 1), ("A5", 1), (None, 1),
            ("F#6", .5), ("F#6", .5), ("A6", 1), ("F#6", .5), ("D6", .5), ("A5", 1),
            ("C#6", .5), ("C#6", .5), ("E6", 1), ("C#6", .5), ("A5", .5), ("E5", 1),
            ("B5", .5), ("B5", .5), ("D6", 1), ("G#5", .5), ("B5", .5), ("E6", 1),
            ("A5", 1.5), ("C#6", .5), ("A5", 1), (None, 1)]
    rng = np.random.default_rng(207)
    sp = spans(bars, 4)
    lead, band = [], []
    for at, n, d in melody(tune, beat, bars=12):
        lead.append((at, 0.5 * toy_piano(NOTE[n], max(0.5, d + 0.3))))
    for b in range(48):
        chord = chord_at(sp, b)
        r = NOTE[above(root_of(chord), "E2")]
        if b % 2 == 0:
            band.append((b * beat, 0.22 * kick()))
            band.append((b * beat, 0.6 * pluck_bass(r if b % 4 == 0 else r * 2 ** (7 / 12), 0.5)))
        else:
            band.append((b * beat, 0.1 * clap(rng)))
            band += [(b * beat + 0.006 * k, 0.09 * ukulele(f, 0.3)) for k, f in enumerate(chord_tones(chord, "A3")[:3])]
        if b >= 32:
            band.append((b * beat, 0.03 * jingle(rng, 0.12, LOOP_SR)))
            band.append(((b + 0.5) * beat, 0.02 * jingle(rng, 0.1, LOOP_SR)))
    return Tune(len(bars) * 4 * beat, lead, band, 5500)


def music_market():
    """超市 (the supermarket): light shop music, 4/4 in B flat with soft
    seventh chords, 120 to the minute. A vibraphone plays the tune, a celesta
    doubles it from bar 9; a felt piano puts a chord on two and four; a warm
    pad; a plucked bass on one and three; a soft brush on every quaver.
    12 bars, 24 s."""
    beat = 0.5
    bars = ["Bbmaj7", "Gm7", "Cm7", "F7", "Bbmaj7", "Gm7", "Cm7-F7", "Bbmaj7", "Ebmaj7", "Dm7", "Cm7-F7", "Bbmaj7"]
    tune = [("D5", 1), ("F5", 1), ("A5", 1.5), ("Bb5", .5),
            ("D6", 1), ("Bb5", 1), ("G5", 2),
            ("Eb5", 1), ("G5", 1), ("Bb5", 1.5), ("C6", .5),
            ("A5", 1), ("F5", 1), ("C5", 2),
            ("D5", 1), ("F5", 1), ("A5", 1.5), ("Bb5", .5),
            ("D6", 1), ("F6", 1), ("D6", 2),
            ("Eb6", .5), ("C6", .5), ("G5", 1), ("A5", .5), ("F5", .5), ("C5", 1),
            ("D5", 1), ("F5", 1), ("D5", 2),
            ("G5", 1), ("Bb5", 1), ("D6", 1.5), ("Eb6", .5),
            ("F6", 1), ("D6", 1), ("A5", 2),
            ("G5", .5), ("Eb5", .5), ("C5", 1), ("Eb5", .5), ("F5", .5), ("A5", 1),
            ("Bb5", 2), (None, 2)]
    rng = np.random.default_rng(208)
    sp = spans(bars, 4)
    lead, band = [], []
    for at, n, d in melody(tune, beat, bars=12):
        f = NOTE[n]
        lead.append((at, 0.5 * vibes(f, max(0.9, d + 0.5))))
        if at >= 32 * beat - 1e-9:
            lead.append((at, 0.15 * celesta(f, max(0.6, d + 0.3))))
    for b in range(48):
        chord = chord_at(sp, b)
        r = NOTE[above(root_of(chord), "Eb2")]
        if b % 2 == 0:
            band.append((b * beat, 0.55 * pluck_bass(r if b % 4 == 0 else r * 2 ** (7 / 12), 0.6)))
        else:
            band += [(b * beat + 0.008 * k, 0.1 * soft_piano(f, 0.6)) for k, f in enumerate(chord_tones(chord, "F3")[:4])]
        band.append((b * beat, 0.03 * shaker(rng, dur=0.08, lo=2000, hi=5000)))
        band.append(((b + 0.5) * beat, 0.02 * shaker(rng, dur=0.06, lo=2000, hi=5000)))
    for b, length, chord in sp:
        band.append((b * beat, 0.12 * pad(chord, length * beat, low="F3")))
    return Tune(len(bars) * 4 * beat, lead, band, 4500)


def music_clinic():
    """診所 (the clinic): calm and reassuring, 4/4 in E, slow (86 to the
    minute). A soft chime sings the tune; a harp rocks slowly through each
    chord; a warm pad; a round bass on one. 8 bars, 22 s."""
    beat = 0.7
    bars = ["E", "A", "E", "B7", "E", "C#m", "A-B7", "E"]
    tune = [("G#5", 2), ("B5", 1), ("E6", 1),
            ("C#6", 2), ("A5", 2),
            ("B5", 1.5), ("G#5", .5), ("E5", 2),
            ("F#5", 2), ("D#5", 1), ("F#5", 1),
            ("G#5", 2), ("B5", 1), ("E6", 1),
            ("C#6", 1.5), ("B5", .5), ("G#5", 2),
            ("A5", 1), ("F#5", 1), ("B5", 1), ("D#5", 1),
            ("E5", 3), (None, 1)]
    lead, band = [], []
    for at, n, d in melody(tune, beat, bars=8):
        lead.append((at, 0.5 * chime(NOTE[n], max(1.4, d + 0.8), LOOP_SR)))
    for b, length, chord in spans(bars, 4):
        c = chord_tones(chord, "E3")
        ripple = [c[0], c[2], 2 * c[0], 2 * c[1], 2 * c[0], c[2], 2 * c[0], 2 * c[1]][:int(length * 2)]
        for k, f in enumerate(ripple):
            band.append(((b + 0.5 * k) * beat, (0.22 if k == 0 else 0.13) * harp(f, 1.6)))
        band.append((b * beat, 0.18 * pad(chord, length * beat, low="E3")))
        band.append((b * beat, 0.5 * pluck_bass(NOTE[above(root_of(chord), "E2")], 1.6)))
    return Tune(len(bars) * 4 * beat, lead, band, 3600)


def music_rest():
    """休息 (the rest screen): the quietest lullaby, 6/8 in A flat, slower
    than the night tune. A music box, far away, over a soft pad; a harp on
    the first beat of each bar. 10 bars, 24 s."""
    eighth = 0.4
    bars = ["Ab", "Db", "Ab", "Eb7", "Fm", "Db", "Ab-Eb7", "Ab", "Db-Eb7", "Ab"]
    tune = [("C5", 2), ("Eb5", 1), ("Ab5", 3),
            ("Ab5", 2), ("F5", 1), ("Db5", 3),
            ("Eb5", 2), ("C5", 1), ("Ab4", 3),
            ("Bb4", 3), ("G4", 3),
            ("Ab4", 2), ("C5", 1), ("F5", 3),
            ("F5", 2), ("Db5", 1), ("Ab5", 3),
            ("Eb5", 2), ("C5", 1), ("Bb4", 3),
            ("Ab4", 3), (None, 3),
            ("Db5", 2), ("F5", 1), ("Eb5", 2), ("Db5", 1),
            ("Ab4", 3), (None, 3)]
    lead, band = [], []
    for at, n, d in melody(tune, eighth, bars=10, beats_per_bar=6):
        lead.append((at, 0.6 * music_box(NOTE[n] * 2, max(1.6, d + 1.0))))
    for b, length, chord in spans(bars, 6):
        c = chord_tones(chord, "Ab2")
        band.append((b * eighth, 0.4 * harp(c[0], 2.0)))
        band.append(((b + 3) * eighth, 0.24 * harp(c[2] * 2, 1.6)))
        band.append((b * eighth, 0.26 * pad(chord, length * eighth, low="Ab3")))
    return Tune(len(bars) * 6 * eighth, lead, band, 3000)


# name: (make, loudness in dB beside the short sounds: 8 to 12 under them).
MUSIC = {
    "music_morning": (music_morning, -8),
    "music_day": (music_day, -8),
    "music_afternoon": (music_afternoon, -8.5),
    "music_evening": (music_evening, -9.5),
    "music_night": (music_night, -11),
    "music_outside": (music_outside, -8.5),
    "music_school": (music_school, -8.5),
    "music_market": (music_market, -9.5),
    "music_clinic": (music_clinic, -10),
    "music_rest": (music_rest, -12),
}


# ---------------------------------------------------------------- builders for the short sounds


def burst(rng, dur, lo, hi, tau, sr=SR, attack=0.001):
    """A puff of noise between [lo] and [hi] Hz, dying away over [tau] s."""
    n = int(dur * sr)
    return norm(bandpass(rng.standard_normal(n), lo, hi, sr)) * np.exp(-np.arange(n) / (tau * sr)) * env(n, attack, min(0.02, dur / 3), sr)


def knock(rng, freq, dur=0.07, bw=180, tau=0.015, sr=SR, second=2.4):
    """A small knock or click: a tap through a resonance at [freq] (and a
    weaker one [second] times up), over in a moment. Wood, plastic, metal,
    by the numbers."""
    n = int(dur * sr)
    t = np.arange(n) / sr
    hit = rng.standard_normal(n) * np.exp(-t / 0.0015)
    x = norm(resonator(hit, freq, bw, sr)) + 0.5 * norm(resonator(hit, freq * second, bw * 1.6, sr))
    return x * np.exp(-t / tau) * env(n, 0.0004, min(0.01, dur / 3), sr)


def mix(*sigs):
    """Signals added together, the shorter ones padded with silence."""
    n = max(len(s) for s in sigs)
    return sum(np.concatenate([s, np.zeros(n - len(s))]) for s in sigs)


def thud(f0, f1, dur, tau, sr=SR):
    """A soft, round thump: a tone falling from [f0] to [f1] Hz."""
    n = int(dur * sr)
    t = np.arange(n) / sr
    f = np.geomspace(f0, f1, n)
    return (sweep(f, sr) + 0.2 * sweep(2 * f, sr)) * np.exp(-t / tau) * env(n, 0.002, 0.02, sr)


def blip(f0, f1, dur, shape=0.8, sr=SR):
    """A quick round "bloop": a tone sliding from [f0] to [f1] under a
    rounded window."""
    t = t_of(dur, sr)
    f = np.geomspace(f0, f1, len(t))
    return (sweep(f, sr) + 0.15 * sweep(2 * f, sr)) * np.sin(np.pi * t / dur) ** shape


def whoosh(rng, dur, points, bw=700, shape=2.0, sr=SR):
    """Air moving: noise through a resonance that follows (seconds, Hz)
    [points], swelling in and out."""
    t = t_of(dur, sr)
    return noise_through(rng, glide(t, *points), bw, len(t), sr) * np.sin(np.pi * t / dur) ** shape


def water(rng, dur, centre=(1800, 1600), bubbles=8, bubble_low=(350, 900), thin=False, sr=SR):
    """Running water: a hiss through two resonances that wander (the stream
    is never still), with little bubbles in it. [centre]: where the hiss
    sits at the start and end; [thin] for a trickle."""
    n = int(dur * sr)
    t = np.arange(n) / sr
    wander = 1 + 0.08 * norm(lowpass(rng.standard_normal(n), 6, sr))
    c = np.linspace(centre[0], centre[1], n) * wander
    hiss = noise_through(rng, c, 900 if thin else 1400, n, sr) + 0.5 * noise_through(rng, c * 0.45, 500, n, sr)
    x = norm(hiss)
    for _ in range(bubbles):
        b = bubble(rng, sr, bubble_low, (1.8, 2.6), (0.03, 0.07))
        i = rng.integers(0, max(1, n - len(b)))
        x[i:i + len(b)] += rng.uniform(0.15, 0.4) * b
    return x


def say(rng, dur, f0, f1, f2, breath=0.08, size=1.0, shape=None, sr=SR, g3=0.1):
    """A small voice saying one sound: pitch [f0] and mouth [f1], [f2] as
    (seconds, Hz) points (the mouth moves between them), through child-sized
    formants ([size] over 1 for a smaller mouth), under [shape] (a function
    of t) or a rounded window."""
    t = t_of(dur, sr)
    p = glide(t, *f0)
    a = glide(t, *f1) * size
    b = glide(t, *f2) * size
    x = voice(p, [(a, 110, 1.0), (b, 160, 0.5), (2900 * size, 300, g3)], rng, breath=breath, sr=sr)
    w = shape(t) if shape else np.sin(np.pi * t / dur) ** 0.7
    return x * w


def steps(rng, times, f0=300, f1=190, dur=0.09, sr=SR):
    """Soft footsteps (socks on a wooden floor) at [times] seconds."""
    parts = []
    for k, at in enumerate(times):
        n = int(dur * sr)
        t = np.arange(n) / sr
        pat = (0.6 * norm(lowpass(rng.standard_normal(n), 900, sr)) * np.exp(-t / 0.008)
               + 0.8 * sweep(np.geomspace(f0 * rng.uniform(0.95, 1.05), f1, n), sr) * np.exp(-t / 0.025))
        parts.append((at, rng.uniform(0.8, 1.0) * carry(pat * env(n, 0.001, 0.03, sr), 0.25, lo=500, hi=2500)))
    return parts


def run(instr, notes, every, dur=None, gain=1.0, start=0.0):
    """Notes one after another on [instr]: (seconds, signal) for place()."""
    out = []
    for k, n in enumerate(notes):
        g = gain(k) if callable(gain) else gain
        out.append((start + every * k, g * (instr(NOTE[n], dur) if dur else instr(NOTE[n]))))
    return out


def crackle(rng, dur, count, lo, hi, each=(0.004, 0.012), sr=SR):
    """[count] tiny crackles (paper, velcro, kibble) spread over [dur] s."""
    n = int(dur * sr)
    x = np.zeros(n + int(0.05 * sr))
    for at in np.sort(rng.uniform(0, dur, count)):
        m = int(rng.uniform(*each) * sr)
        i = int(at * sr)
        x[i:i + m] += rng.uniform(0.3, 1) * rng.standard_normal(m) * np.exp(-np.arange(m) / (m / 3))
    return norm(bandpass(x, lo, hi, sr)[:n])


def tick_tone(freq, dur, sr=SR, shape=0.08):
    """A small electronic beep: a sine with a touch of its octave."""
    t = t_of(dur, sr)
    return (np.sin(2 * np.pi * freq * t) + 0.12 * np.sin(4 * np.pi * freq * t)) * env(len(t), 0.004, shape, sr)


def hum_at(freq, dur, rng):
    return hum_voice(freq, dur, rng, SR)


def mbox(freq, dur=0.8):
    return music_box(freq, dur, SR)


def cel(freq, dur=0.5):
    return celesta(freq, dur, SR)


def xylo(freq, dur=0.4):
    return xylophone(freq, dur, SR)


def glock(freq, dur=0.35):
    return bell(freq, dur, SR, bright=0.4)


# ---------------------------------------------------------------- general


def fx_tap():
    """A button: a soft, round "pok", like a finger on a felt button."""
    t = t_of(0.08)
    f = np.interp(t, [0, 0.008, 0.08], [640, 760, 720])
    x = (sweep(f) + 0.18 * sweep(2 * f)) * np.exp(-t / 0.016) + 0.12 * partial(2400, t, SR) * np.exp(-t / 0.003)
    return lowpass(x * env(len(t), 0.0008, 0.02), 3500)


def fx_pop():
    """A little pop: a bubble bursting, quick and round, with a tiny tick."""
    t = t_of(0.05)
    return place(0.1, [(0, blip(420, 1300, 0.05, 0.7)), (0, 0.2 * partial(3200, t, SR) * np.exp(-t / 0.002))])


def fx_yay():
    """Done! A happy three-note jingle: xylophone C-E-G with a glockenspiel
    on top, and a sparkle after."""
    parts = run(xylo, ["C5", "E5", "G5"], 0.11, 0.4, lambda k: 0.5 + 0.1 * k)
    parts += run(glock, ["C6", "E6", "G6"], 0.11, 0.3, 0.14)
    parts += [(0.36, 0.22 * glock(NOTE["C7"], 0.4)), (0.42, 0.14 * glock(NOTE["E7"], 0.35))]
    return place(0.85, parts)


def fx_sticker():
    """A sticker popping onto the chart: a round, bubbly "pop!" going up, a
    soft pat as it sticks, and a tiny twinkle."""
    rng = np.random.default_rng(309)
    pop = blip(350, 1250, 0.075)
    tp = t_of(0.06)
    pat = (0.6 * norm(lowpass(rng.standard_normal(len(tp)), 1400)) * np.exp(-tp / 0.008)
           + 0.5 * sweep(np.geomspace(420, 280, len(tp))) * np.exp(-tp / 0.018)) * env(len(tp), 0.0008, 0.015)
    return place(0.45, [(0, 0.8 * pop), (0.07, 0.55 * pat), (0.1, 0.2 * glock(NOTE["E7"], 0.3)), (0.16, 0.14 * glock(NOTE["B7"], 0.25))])


def fx_hint():
    """A hint: a little sparkle, four quick bells running up."""
    return place(0.7, run(glock, ["G6", "B6", "D7", "G7"], 0.07, 0.4, lambda k: 0.3 - 0.04 * k))


def fx_wrong():
    """Not quite: a soft, curious "mm?" (two hummed notes, the second up,
    like a question), friendly, never a buzzer."""
    rng = np.random.default_rng(310)
    t = t_of(0.42)
    f0 = glide(t, (0, 330), (0.15, 320), (0.22, 380), (0.42, 440))
    x = voice(f0, [(320, 90, 1.0), (1000, 160, 0.14), (2400, 250, 0.03)], rng, breath=0.05)
    x = lowpass(x, 1500) * ease(t / 0.03) * (1 - ease((t - 0.3) / 0.12)) * (1 - 0.35 * np.exp(-((t - 0.2) / 0.025) ** 2))
    return x


def fx_walk():
    """Walking to another room: four soft footsteps, socks on a wooden floor."""
    rng = np.random.default_rng(311)
    return place(0.85, steps(rng, (0, 0.22, 0.44, 0.66)))


def fx_door():
    """A door: a little creak as it opens (a hinge sticking and slipping),
    then the latch clicks."""
    rng = np.random.default_rng(312)
    d = 0.4
    t = t_of(d)
    n = len(t)
    f = glide(t, (0, 520), (0.2, 640), (d, 600))
    stick = (np.cumsum(f * 0.07) / SR % 1 < 0.3).astype(float)  # a stick-slip pulse train
    creak = norm(resonator(stick - stick.mean(), f, 60)) + 0.5 * norm(resonator(stick - stick.mean(), f * 2.2, 120))
    creak = lowpass(creak, 3000) * np.sin(np.pi * t / d) ** 1.2 * (0.7 + 0.3 * np.sin(2 * np.pi * 9 * t))
    return place(0.75, [(0, 0.7 * creak), (0.5, 0.35 * knock(rng, 1500, 0.08, 200, 0.02)), (0.53, 0.3 * knock(rng, 900, 0.07, 150, 0.025))])


def fx_stairs():
    """Up the stairs: four soft steps, each a little higher."""
    rng = np.random.default_rng(313)
    parts = []
    for k, at in enumerate((0, 0.16, 0.32, 0.48)):
        parts += steps(rng, (at,), f0=300 + 70 * k, f1=190 + 50 * k)
    return place(0.65, parts)


def fx_clock_tick():
    """The clock hand turns one notch: a small wooden "tok"."""
    rng = np.random.default_rng(314)
    return mix(0.7 * knock(rng, 1800, 0.1, 50, 0.025), 0.6 * knock(rng, 750, 0.1, 40, 0.03))


def fx_clock_set():
    """A time chosen: a small chime, two bells a fifth apart."""
    return place(0.75, [(0, 0.6 * chime(NOTE["A5"], 0.6)), (0.09, 0.45 * chime(NOTE["E6"], 0.6))])


def fx_night():
    """The house dims for the night: a soft chime stepping down G-E-C."""
    return place(1.3, run(cel, ["G5", "E5", "C5"], 0.24, 0.7, lambda k: 0.5 - 0.06 * k))


def fx_grow():
    """The height chart: the child has grown! Four quick xylophone notes
    climbing, and a bright ding on top."""
    parts = run(xylo, ["C5", "E5", "G5", "C6"], 0.09, 0.35, lambda k: 0.45 + 0.08 * k)
    parts.append((0.36, 0.5 * glock(NOTE["E7"], 0.5)))
    return place(0.95, parts)


def fx_deco():
    """A decoration earned: a twinkle of little bells, high and random."""
    rng = np.random.default_rng(316)
    names = ["C7", "E7", "G7", "D7", "B6", "G7", "E7"]
    return place(0.85, [(0.07 * k + rng.uniform(0, 0.02), (0.3 - 0.03 * k) * glock(NOTE[n], 0.35)) for k, n in enumerate(names)])


# ---------------------------------------------------------------- waking and sleeping


def fx_curtain():
    """Curtains drawn open: the rings slide along the rod (a quick run of
    tiny metal tings) with a swish of cloth."""
    rng = np.random.default_rng(320)
    parts = [(0, 0.5 * whoosh(rng, 0.6, [(0, 500), (0.3, 1500), (0.6, 900)], 900, 1.5))]
    for k in range(9):
        parts.append((0.03 + 0.055 * k + rng.uniform(0, 0.01), rng.uniform(0.15, 0.3) * metal(rng.uniform(3200, 4800), 0.12, ratios=(1, 1.7, 2.9), amps=(1, .5, .3), taus=(.4, .2, .1))))
    return place(0.75, parts)


def fx_stretch():
    """A big stretch: "mmm~" rising, mouth closed, opening into "ah" at the
    top."""
    rng = np.random.default_rng(321)
    d = 0.9
    t = t_of(d)
    f0 = glide(t, (0, 260), (0.6, 400), (d, 430))
    f1 = glide(t, (0, 300), (0.55, 320), (0.75, 750), (d, 700))
    f2 = glide(t, (0, 900), (0.55, 950), (0.75, 1400), (d, 1300))
    x = voice(f0, [(f1, 110, 1.0), (f2, 170, 0.35), (2600, 280, 0.06)], rng, breath=0.06)
    closed = 1 - ease((t - 0.55) / 0.2)
    x = x * (1 - closed) + 1.4 * lowpass(x, 800) * closed
    return x * ease(t / 0.12) * (1 - ease((t - 0.7) / 0.18))


def fx_yawn():
    """A yawn: a small, breathy "haa-aum" that sinks and closes into a
    sleepy hum."""
    rng = np.random.default_rng(322)
    dur = 0.95
    t = t_of(dur)
    f0 = glide(t, (0, 380), (0.15, 450), (0.55, 330), (dur, 260))
    f1 = glide(t, (0, 550), (0.2, 900), (0.55, 760), (0.75, 450), (dur, 320))
    f2 = glide(t, (0, 1500), (0.2, 1350), (0.6, 1000), (dur, 900))
    x = voice(f0, [(f1, 150, 1.0), (f2, 190, 0.45), (2800, 300, 0.07)], rng, breath=0.35) * env(len(t), 0.12, 0.3)
    closing = ease((t - 0.6) / 0.25)
    return x * (1 - closing) + 1.6 * lowpass(x, 700) * closing


def fx_light_on():
    """The light switch on: a plastic click and a tiny blip up."""
    rng = np.random.default_rng(323)
    return place(0.16, [(0, 0.7 * knock(rng, 2600, 0.05, 300, 0.008)), (0.03, 0.35 * blip(900, 1500, 0.06))])


def fx_light_off():
    """The light switch off: a plastic click and a tiny blip down."""
    rng = np.random.default_rng(324)
    return place(0.16, [(0, 0.7 * knock(rng, 2200, 0.05, 300, 0.008)), (0.03, 0.35 * blip(1300, 700, 0.07))])


def fx_snore():
    """A little snore: a soft "khrrr" in (a purr, rising) and a round "puu"
    out."""
    rng = np.random.default_rng(325)
    d = 0.55
    t = t_of(d)
    n = len(t)
    purr = (np.sin(2 * np.pi * np.cumsum(np.linspace(22, 28, n)) / SR) > 0.3).astype(float)
    x_in = norm(resonator(rng.standard_normal(n) * (0.3 + purr), glide(t, (0, 330), (d, 420)), 160)) * np.sin(np.pi * t / d) ** 1.3
    x_in = lowpass(x_in, 2200)
    d2 = 0.45
    t2 = t_of(d2)
    f = glide(t2, (0, 170), (d2, 140))
    out = voice(f, [(380, 90, 1.0), (900, 160, 0.25)], rng, breath=0.5) * np.sin(np.pi * t2 / d2) ** 1.5
    return carry(place(1.2, [(0, 0.8 * x_in), (0.7, 0.8 * lowpass(out, 1200))]), 0.3, lo=500, hi=2500)


def fx_book_open():
    """A storybook opened: a light, papery "fwip" and a soft pat."""
    rng = np.random.default_rng(326)
    dur = 0.2
    t = t_of(dur)
    n = len(t)
    air = noise_through(rng, glide(t, (0, 700), (0.12, 1800), (dur, 1200)), 700, n)
    paper = norm(bandpass(rng.standard_normal(n), 1500, 7000)) * (0.6 + 0.4 * norm(lowpass(rng.standard_normal(n), 60)))
    flip = (0.6 * air + 0.45 * paper) * ease(t / 0.05) * (1 - ease((t - 0.12) / 0.08))
    tp = t_of(0.05)
    pat = norm(lowpass(rng.standard_normal(len(tp)), 1500)) * np.exp(-tp / 0.007) * env(len(tp), 0.0008, 0.01)
    return place(0.3, [(0, 0.8 * flip), (0.19, 0.35 * pat)])


def fx_blanket():
    """A blanket pulled up: a soft swish of cloth."""
    rng = np.random.default_rng(327)
    return whoosh(rng, 0.5, [(0, 600), (0.25, 1400), (0.5, 800)], 1200, 1.6) * 0.8 + 0.2 * crackle(rng, 0.5, 40, 1500, 5000) * np.sin(np.pi * t_of(0.5) / 0.5)


# ---------------------------------------------------------------- bathroom


def fx_toothpaste():
    """Toothpaste squeezed out: a wet little squirt."""
    rng = np.random.default_rng(330)
    d = 0.28
    t = t_of(d)
    squelch = noise_through(rng, glide(t, (0, 900), (0.12, 2600), (d, 1800)), 500, len(t)) * np.sin(np.pi * t / d) ** 1.5
    return place(0.3, [(0, 0.6 * squelch), (0.02, 0.5 * blip(500, 1400, 0.14, 1.2))])


def fx_brush():
    """Brushing teeth: sha-sha-sha, six quick strokes."""
    rng = np.random.default_rng(331)
    d = 1.0
    t = t_of(d)
    n = len(t)
    strokes = np.abs(np.sin(np.pi * 6 * t)) ** 1.5
    x = norm(bandpass(rng.standard_normal(n), 1800, 6500)) * strokes * (0.75 + 0.25 * np.sin(2 * np.pi * 3 * t))
    return x * env(n, 0.02, 0.1)


def fx_rinse():
    """Rinsing: a gargle (a low voice bubbling) and a little "pfft" as the
    water goes out."""
    rng = np.random.default_rng(332)
    d = 0.55
    t = t_of(d)
    n = len(t)
    f0 = np.full(n, 150.0) * (1 + 0.05 * np.sin(2 * np.pi * 7 * t))
    g = voice(f0, [(400, 100, 1.0), (1100, 180, 0.3)], rng, breath=0.25) * (0.6 + 0.4 * (np.sin(2 * np.pi * 21 * t) > 0)) * np.sin(np.pi * t / d) ** 0.8
    for _ in range(6):
        b = bubble(rng, SR, (250, 500), (1.6, 2.2), (0.03, 0.06))
        i = rng.integers(0, n - len(b))
        g[i:i + len(b)] += 0.4 * b
    pfft = burst(rng, 0.2, 500, 3500, 0.05, attack=0.004)
    return carry(place(0.95, [(0, 0.8 * lowpass(g, 2500)), (0.68, 0.6 * pfft)]), 0.3, lo=500, hi=2500)


def fx_water_on():
    """The tap turned on: water starts to run."""
    rng = np.random.default_rng(333)
    d = 0.8
    t = t_of(d)
    return water(rng, d, (1400, 1900), 6) * ease(t / 0.08) * (1 - 0.3 * ease((t - 0.5) / 0.3)) * env(len(t), 0.01, 0.15)


def fx_water_off():
    """The tap turned off: the water stops, and two drips fall."""
    rng = np.random.default_rng(334)
    d = 0.3
    t = t_of(d)
    stream = water(rng, d, (1900, 1500), 2) * (1 - ease((t - 0.15) / 0.12))
    drips = [(0.5, 0.6 * blip(700, 1800, 0.07, 1.0)), (0.82, 0.45 * blip(900, 2100, 0.06, 1.0))]
    return place(0.95, [(0, 0.7 * stream), (0.2, 0.3 * knock(rng, 1200, 0.05, 200, 0.012))] + drips)


def fx_soap():
    """The soap pump: a little squeak and a puff."""
    rng = np.random.default_rng(335)
    d = 0.12
    t = t_of(d)
    squeak = (sweep(glide(t, (0, 1900), (d, 1300))) + 0.2 * sweep(glide(t, (0, 3800), (d, 2600)))) * np.sin(np.pi * t / d) ** 1.2
    return place(0.3, [(0, 0.5 * squeak), (0.08, 0.6 * burst(rng, 0.15, 800, 4000, 0.04, attack=0.005))])


def fx_rub():
    """Rubbing hands with soap: a soft, slippery rub-rub-rub."""
    rng = np.random.default_rng(336)
    d = 1.0
    t = t_of(d)
    n = len(t)
    strokes = np.abs(np.sin(np.pi * 5 * t)) ** 1.2
    x = noise_through(rng, 1300 + 400 * np.sin(2 * np.pi * 5 * t), 900, n) * strokes
    return lowpass(x, 3500) * env(n, 0.03, 0.12)


def fx_towel():
    """Drying with a towel: two fluffy pats."""
    rng = np.random.default_rng(337)
    parts = []
    for at in (0, 0.22):
        n = int(0.16 * SR)
        parts.append((at, norm(lowpass(rng.standard_normal(n), 1200)) * np.sin(np.pi * np.arange(n) / n) ** 1.5))
    return place(0.42, parts)


def fx_toilet_flush():
    """The toilet flushed: a swirl of water going down, gurgling, and a last
    gloop."""
    rng = np.random.default_rng(338)
    d = 1.35
    t = t_of(d)
    n = len(t)
    c = glide(t, (0, 1200), (0.3, 2000), (0.9, 900), (d, 500))
    swirl = (noise_through(rng, c, 1100, n) + 0.6 * noise_through(rng, c * 0.5, 500, n)) * ease(t / 0.12) * (1 - ease((t - 0.95) / 0.35))
    x = norm(swirl)
    for k in range(10):
        b = bubble(rng, SR, (180, 420), (1.6, 2.4), (0.04, 0.09))
        i = int(rng.uniform(0.45, 1.15) * SR)
        x[i:i + len(b)] += rng.uniform(0.25, 0.5) * b
    return carry(place(1.5, [(0, x), (1.25, 0.5 * blip(260, 700, 0.14, 1.0))]), 0.25, lo=500, hi=2500)


def fx_hum():
    """Humming a little tune while washing: four notes, "mm mm mm mm"."""
    rng = np.random.default_rng(339)
    return place(1.15, [(0.26 * k, 0.8 * hum_at(NOTE[n], 0.3, rng)) for k, n in enumerate(["C5", "E5", "G5", "E5"])])


def fx_paper():
    """Toilet paper torn off: a short crisp tear."""
    rng = np.random.default_rng(340)
    d = 0.22
    t = t_of(d)
    return crackle(rng, d, 60, 1500, 7000, (0.003, 0.008)) * np.sin(np.pi * t / d) ** 0.8 * (0.6 + 0.4 * ease(t / 0.1))


def fx_splash():
    """A splash: water thrown up, droplets falling back."""
    rng = np.random.default_rng(341)
    parts = [(0, 0.8 * burst(rng, 0.3, 600, 5000, 0.06, attack=0.003))]
    for k in range(7):
        parts.append((0.08 + rng.uniform(0, 0.4), rng.uniform(0.15, 0.35) * blip(rng.uniform(600, 1100), rng.uniform(1600, 2600), 0.05, 1.0)))
    return place(0.6, parts)


def fx_bubble():
    """One bath bubble: a round "bloop" going up."""
    return blip(260, 700, 0.14, 0.8)


def fx_hairdryer():
    """A hairdryer: a soft whirr that spins up, blows, and winds down."""
    rng = np.random.default_rng(343)
    d = 1.0
    t = t_of(d)
    n = len(t)
    speed = ease(t / 0.2) * (1 - ease((t - 0.75) / 0.25))
    f = 140 + 120 * speed
    motor = harmonics(f, tilt=1.6)
    wind = norm(lowpass(rng.standard_normal(n), 2500)) * (0.5 + 0.5 * speed)
    x = (0.4 * carry(norm(bandpass(motor, 200, 3000)), 0.3) + 0.8 * wind) * (0.15 + 0.85 * speed)
    return x * env(n, 0.02, 0.1)


def fx_lotion():
    """Lotion squeezed out: a tiny wet squelch."""
    rng = np.random.default_rng(344)
    d = 0.22
    t = t_of(d)
    x = noise_through(rng, glide(t, (0, 600), (0.1, 2200), (d, 1200)), 400, len(t)) * np.sin(np.pi * t / d) ** 1.4
    return place(d, [(0, 0.6 * x), (0.02, 0.35 * blip(380, 900, 0.16, 1.2))])


def fx_nail_clip():
    """Nail clippers: one small, clean click."""
    rng = np.random.default_rng(345)
    return mix(0.7 * knock(rng, 3400, 0.05, 250, 0.006), 0.4 * knock(rng, 1300, 0.06, 90, 0.012))


# ---------------------------------------------------------------- getting dressed


def fx_zipper():
    """A zipper, up: a quick buzz of tiny teeth, rising."""
    rng = np.random.default_rng(350)
    d = 0.4
    t = t_of(d)
    n = len(t)
    rate = glide(t, (0, 60), (0.15, 130), (d, 150))
    teeth = (np.diff(np.floor(np.cumsum(rate) / SR), prepend=0) > 0).astype(float)
    x = norm(resonator(teeth * rng.uniform(0.5, 1, n), glide(t, (0, 1600), (d, 2600)), 500)) + 0.4 * norm(bandpass(teeth * rng.standard_normal(n), 2000, 7000))
    return x * np.sin(np.pi * t / d) ** 0.5 * env(n, 0.005, 0.04)


def fx_button():
    """A button done up: a small click."""
    rng = np.random.default_rng(351)
    return mix(0.6 * knock(rng, 2800, 0.06, 200, 0.008), 0.5 * knock(rng, 1100, 0.07, 80, 0.015))


def fx_cloth():
    """Clothes pulled on: a rustle of cloth."""
    rng = np.random.default_rng(352)
    d = 0.45
    t = t_of(d)
    n = len(t)
    x = norm(bandpass(rng.standard_normal(n), 900, 5000)) * (0.4 + 0.6 * norm(lowpass(rng.standard_normal(n), 25)) ** 2)
    return x * np.sin(np.pi * t / d) ** 1.2


def fx_sneeze():
    """A cute little sneeze: "ah-ah-CHOO", the choo a soft puff and a small
    falling "oo"."""
    rng = np.random.default_rng(353)
    parts = []
    for at, f in ((0, 380), (0.14, 420)):
        parts.append((at, 0.5 * say(rng, 0.1, [(0, f), (0.1, f * 1.15)], [(0, 700)], [(0, 1300)], breath=0.3, size=1.2)))
    parts.append((0.3, 0.8 * burst(rng, 0.14, 1500, 7000, 0.04, attack=0.003)))
    parts.append((0.34, 0.6 * say(rng, 0.3, [(0, 480), (0.3, 300)], [(0, 400), (0.3, 330)], [(0, 1000), (0.3, 800)], breath=0.15, size=1.2)))
    return place(0.75, parts)


def fx_shiver():
    """Cold! A little "brrr": lips fluttering, the voice trembling."""
    rng = np.random.default_rng(354)
    d = 0.55
    t = t_of(d)
    n = len(t)
    flutter = 0.55 + 0.45 * (np.sin(2 * np.pi * 26 * t) > 0)
    f0 = glide(t, (0, 300), (d, 240)) * (1 + 0.03 * np.sin(2 * np.pi * 26 * t))
    x = voice(f0, [(450, 100, 1.0), (1100, 160, 0.4), (2500, 250, 0.08)], rng, breath=0.1) * flutter
    return lowpass(x, 3000) * np.sin(np.pi * t / d) ** 0.8


def fx_sweat():
    """Hot! A drop of sweat falls, and a tired little sigh "haa"."""
    rng = np.random.default_rng(355)
    sigh = say(rng, 0.5, [(0, 360), (0.5, 260)], [(0, 800), (0.5, 650)], [(0, 1400), (0.5, 1200)], breath=0.7, size=1.15)
    return place(0.75, [(0, 0.6 * blip(1500, 700, 0.08, 1.0)), (0.18, 0.8 * lowpass(sigh, 3000))])


# ---------------------------------------------------------------- eating and drinking


def fx_chew():
    """Eating: "nom nom", two soft munches."""
    rng = np.random.default_rng(360)
    parts = []
    for at in (0, 0.28):
        d = 0.2
        t = t_of(d)
        n = len(t)
        f0 = glide(t, (0, 260), (d, 220))
        m = voice(f0, [(glide(t, (0, 350), (0.06, 650), (d, 350)), 110, 1.0), (1100, 180, 0.3)], rng, breath=0.1) * np.sin(np.pi * t / d) ** 0.9
        wet = norm(lowpass(rng.standard_normal(n), 1800)) * np.exp(-t / 0.02) * 0.3
        parts.append((at, 0.8 * lowpass(m, 2500) + wet))
    return place(0.55, parts)


def fx_spoon():
    """A spoon on the bowl: a small clink."""
    return metal(3300, 0.3, ratios=(1, 2.3, 3.9), amps=(1, .5, .25), taus=(.5, .25, .1))


def fx_pour():
    """Pouring a drink: water into a cup, the cup filling (the note rising)."""
    rng = np.random.default_rng(362)
    d = 1.0
    t = t_of(d)
    n = len(t)
    x = water(rng, d, (900, 2200), 10, (300, 800))
    tone = sweep(glide(t, (0, 500), (d, 1100))) * 0.15 * (0.5 + 0.5 * norm(lowpass(rng.standard_normal(n), 30)))
    return (x + tone) * env(n, 0.04, 0.12) * (1 - 0.2 * ease((t - 0.7) / 0.3))


def fx_drink():
    """Drinking: "gulp, gulp", then a happy "ahh"."""
    rng = np.random.default_rng(363)
    parts = []
    for at in (0, 0.26):
        d = 0.14
        t = t_of(d)
        g = voice(glide(t, (0, 170), (d, 110)), [(glide(t, (0, 350), (d, 650)), 120, 1.0), (1200, 200, 0.2)], rng, breath=0.15) * np.sin(np.pi * t / d) ** 1.1
        parts.append((at, mix(0.8 * carry(lowpass(g, 2000), 0.3, lo=500, hi=2500), 0.25 * blip(300, 600, 0.08))))
    parts.append((0.6, 0.7 * say(rng, 0.4, [(0, 400), (0.15, 440), (0.4, 360)], [(0, 800)], [(0, 1350)], breath=0.15, size=1.15)))
    return place(1.05, parts)


def fx_dishes():
    """Clearing the dishes: bowls clinking, three little tings."""
    rng = np.random.default_rng(364)
    parts = []
    for k, (at, f) in enumerate(((0, 2300), (0.11, 2750), (0.25, 2050))):
        parts.append((at + rng.uniform(0, 0.01), (0.6 - 0.1 * k) * metal(f, 0.35, ratios=(1, 1.9, 3.2), amps=(1, .4, .2), taus=(.4, .2, .1))))
    return place(0.65, parts)


def fx_yum():
    """"Mm~ yummy!": a happy hum, two notes going up and settling."""
    rng = np.random.default_rng(365)
    d = 0.6
    t = t_of(d)
    f0 = glide(t, (0, 350), (0.2, 360), (0.3, 440), (0.45, 450), (d, 420))
    x = voice(f0, [(330, 90, 1.0), (1000, 160, 0.14), (2400, 250, 0.03)], rng, breath=0.05)
    return lowpass(x, 1600) * ease(t / 0.04) * (1 - ease((t - 0.45) / 0.15))


# ---------------------------------------------------------------- school and outside


def fx_bag_zip():
    """The school bag zipped: a longer, lower zip."""
    rng = np.random.default_rng(370)
    d = 0.5
    t = t_of(d)
    n = len(t)
    rate = glide(t, (0, 50), (0.2, 110), (d, 90))
    teeth = (np.diff(np.floor(np.cumsum(rate) / SR), prepend=0) > 0).astype(float)
    x = norm(resonator(teeth * rng.uniform(0.5, 1, n), glide(t, (0, 1100), (d, 1500)), 400)) + 0.4 * norm(bandpass(teeth * rng.standard_normal(n), 1500, 6000))
    return x * np.sin(np.pi * t / d) ** 0.5 * env(n, 0.005, 0.04)


def fx_shoes():
    """Shoes on: two velcro straps pressed down, "rrip, rrip"."""
    rng = np.random.default_rng(371)
    parts = []
    for at in (0, 0.3):
        d = 0.14
        t = t_of(d)
        parts.append((at, crackle(rng, d, 70, 1200, 6000, (0.002, 0.006)) * np.sin(np.pi * t / d) ** 0.7))
    return place(0.5, parts)


def fx_hat():
    """A hat put on: a soft pat."""
    rng = np.random.default_rng(372)
    n = int(0.12 * SR)
    t = np.arange(n) / SR
    return mix(norm(lowpass(rng.standard_normal(n), 900)) * np.exp(-t / 0.02) * env(n, 0.001, 0.04), 0.4 * thud(260, 180, 0.1, 0.02))


def fx_bus_horn():
    """The school bus: a cute "beep-beep"."""
    parts = []
    for at in (0, 0.2):
        for f in (NOTE["E5"], NOTE["G#5"]):
            parts.append((at, 0.4 * toy_horn(f, 0.14)))
    return place(0.45, parts)


def fx_bus_ride():
    """Riding the bus: a toy engine puttering along, and a little jingle as
    it goes."""
    rng = np.random.default_rng(374)
    d = 1.5
    t = t_of(d)
    n = len(t)
    puffs = np.abs(np.sin(np.pi * 9 * t)) ** 3
    engine = norm(bandpass(harmonics(np.full(n, 95.0) * (1 + 0.02 * np.sin(2 * np.pi * 1.5 * t)), tilt=1.3), 150, 1800)) * (0.4 + 0.6 * puffs)
    engine = carry(engine, 0.35, lo=500, hi=2500) * env(n, 0.05, 0.3)
    parts = [(0, 0.5 * engine)]
    parts += run(glock, ["E6", "G#6", "B6", "E7"], 0.13, 0.35, lambda k: 0.2 + 0.03 * k, start=0.5)
    return place(d, parts)


def fx_seatbelt():
    """The seatbelt clicked in: a firm little click."""
    rng = np.random.default_rng(375)
    return mix(0.7 * knock(rng, 3000, 0.06, 250, 0.007), 0.6 * knock(rng, 800, 0.08, 70, 0.02))


def fx_bell():
    """The school bell: a hand bell rung, ring-a-ling."""
    rng = np.random.default_rng(376)
    ring = dict(ratios=(1, 2.0, 3.0, 4.2), amps=(1, .6, .3, .15), taus=(.5, .3, .15, .08))
    parts = [(0.12 * k + rng.uniform(0, 0.01), (0.6 - 0.05 * k) * metal(2650 * rng.uniform(0.995, 1.005), 0.7, **ring)) for k in range(6)]
    return place(1.4, parts)


def fx_clap():
    """Two claps."""
    rng = np.random.default_rng(377)
    return place(0.45, [(0, clap(rng, SR)), (0.22, 0.9 * clap(rng, SR))])


def fx_sing():
    """Singing along: "la la la la la", five notes."""
    rng = np.random.default_rng(378)
    parts = []
    for k, n in enumerate(["C5", "D5", "E5", "D5", "C5"]):
        f = NOTE[n]
        d = 0.2
        la = say(rng, d, [(0, f * 0.97), (0.05, f), (d, f)], [(0, 350), (0.03, 750), (d, 720)], [(0, 1500), (0.03, 1300), (d, 1300)], breath=0.08, size=1.2,
                 shape=lambda t: ease(t / 0.025) * (1 - ease((t - 0.15) / 0.05)))
        parts.append((0.22 * k, 0.8 * la))
    return place(1.3, parts)


def fx_line_up():
    """Line up! A gentle whistle, "fwee-fwit"."""
    rng = np.random.default_rng(379)
    def wh(d, pts):
        t = t_of(d)
        f = glide(t, *pts)
        return (sweep(f) + 0.08 * sweep(2 * f) + 0.12 * noise_through(rng, f, 300, len(t))) * np.sin(np.pi * t / d) ** 0.9
    return place(0.65, [(0, 0.8 * wh(0.3, [(0, 1700), (0.3, 2300)])), (0.36, 0.7 * wh(0.22, [(0, 2300), (0.22, 1900)]))])


def fx_bye():
    """Bye-bye! A two-note wave on the music box, high then low."""
    return place(0.8, [(0, 0.6 * mbox(NOTE["G5"], 0.6)), (0.2, 0.55 * mbox(NOTE["E5"], 0.7))])


def fx_traffic_wait():
    """The red man: wait. Three slow, soft ticks."""
    rng = np.random.default_rng(381)
    return place(1.1, [(0.4 * k, 0.8 * knock(rng, 1400, 0.06, 200, 0.012)) for k in range(3)])


def fx_traffic_go():
    """The green man: go! The crossing's cuckoo chirp, twice."""
    rng = np.random.default_rng(382)
    parts = []
    for at in (0, 0.42):
        for k, (f, d) in enumerate(((NOTE["E6"], 0.12), (NOTE["C6"], 0.16))):
            parts.append((at + 0.14 * k, 0.6 * ocarina(f, d, rng, SR)))
    return place(0.9, parts)


def fx_slide():
    """Down the slide: "wheee!", a tone sliding down with a whoosh."""
    rng = np.random.default_rng(383)
    d = 0.6
    t = t_of(d)
    f = glide(t, (0, 1500), (0.4, 600), (d, 520))
    tone = (sweep(f) + 0.25 * sweep(2 * f) + 0.08 * sweep(3 * f)) * np.sin(np.pi * t / d) ** 0.8
    return 0.7 * tone + 0.3 * whoosh(rng, d, [(0, 2500), (d, 800)], 900, 1.5)


def fx_swing():
    """On the swing: the chain creaks, and the swing whooshes past."""
    rng = np.random.default_rng(384)
    d = 0.3
    t = t_of(d)
    f = glide(t, (0, 700), (d, 820))
    stick = (np.cumsum(f * 0.05) / SR % 1 < 0.3).astype(float)
    creak = lowpass(norm(resonator(stick - stick.mean(), f, 50)), 3000) * np.sin(np.pi * t / d) ** 1.2
    return place(0.85, [(0, 0.35 * creak), (0.2, 0.8 * whoosh(rng, 0.6, [(0, 500), (0.3, 1400), (0.6, 600)], 900, 1.8))])


def fx_dig():
    """Digging in the sand: a scoop, crumbly and soft."""
    rng = np.random.default_rng(385)
    d = 0.3
    t = t_of(d)
    x = crackle(rng, d, 90, 500, 3500, (0.002, 0.006)) * np.sin(np.pi * t / d) ** 0.9
    return 0.7 * x + 0.5 * whoosh(rng, d, [(0, 500), (d, 1200)], 600, 1.5)


def fx_ball_kick():
    """A ball kicked: a round thump and the ball flying off."""
    rng = np.random.default_rng(386)
    return place(0.5, [(0, 0.8 * carry(thud(190, 90, 0.2, 0.05), 0.35, lo=500, hi=2500)), (0.04, 0.4 * whoosh(rng, 0.4, [(0, 900), (0.4, 2200)], 900, 1.5))])


def fx_shell():
    """A shell found on the beach: a bright ding."""
    return metal(2900, 0.65, ratios=(1, 2.4, 4.1), amps=(1, .4, .15), taus=(.5, .2, .08))


def fx_cart():
    """The shopping cart rolling: a rattle of little wheels."""
    rng = np.random.default_rng(388)
    d = 0.8
    t = t_of(d)
    n = len(t)
    rattle = crackle(rng, d, 45, 800, 3500, (0.004, 0.01))
    rumble = norm(lowpass(rng.standard_normal(n), 300)) * (0.6 + 0.4 * np.sin(2 * np.pi * 7 * t))
    return (0.6 * rattle + 0.5 * carry(rumble, 0.3, lo=500, hi=2000)) * np.sin(np.pi * t / d) ** 0.6


def fx_scan():
    """The checkout scanner: one soft beep."""
    return tick_tone(1700, 0.13)


def fx_coins():
    """Coins: three small bright clinks."""
    rng = np.random.default_rng(390)
    ring = dict(ratios=(1, 2.32, 4.25), amps=(1, .5, .25), taus=(.35, .18, .08))
    return place(0.55, [(0, 0.5 * metal(4300, 0.3, **ring)), (0.07, 0.4 * metal(5100, 0.28, **ring)), (0.16, 0.35 * metal(4700, 0.3, **ring)),
                        (0, 0.1 * burst(rng, 0.1, 4000, 9000, 0.02))])


def fx_bag_rustle():
    """A shopping bag: a crinkle of plastic."""
    rng = np.random.default_rng(391)
    d = 0.5
    t = t_of(d)
    return crackle(rng, d, 110, 1500, 8000, (0.002, 0.007)) * (0.5 + 0.5 * norm(lowpass(rng.standard_normal(len(t)), 20)) ** 2) * np.sin(np.pi * t / d) ** 0.7


# ---------------------------------------------------------------- the clinic


def fx_thermometer():
    """The thermometer: beep-beep-beep, done."""
    return place(0.5, [(0.14 * k, 0.6 * tick_tone(2200, 0.08)) for k in range(3)])


def fx_ahh():
    """"Ahh" for the doctor: a clear, steady little "ahh"."""
    rng = np.random.default_rng(393)
    return say(rng, 0.7, [(0, 330), (0.1, 350), (0.7, 340)], [(0, 780)], [(0, 1350)], breath=0.08, size=1.15,
               shape=lambda t: ease(t / 0.06) * (1 - ease((t - 0.55) / 0.15)))


def fx_heartbeat():
    """The stethoscope: lub-dub, two soft thumps."""
    rng = np.random.default_rng(394)
    parts = []
    for at, g, f in ((0, 1.0, 110), (0.17, 0.75, 100)):
        n = int(0.08 * SR)
        pat = norm(lowpass(rng.standard_normal(n), 700)) * np.exp(-np.arange(n) / SR / 0.012) * env(n, 0.001, 0.03)
        parts += [(at, 0.5 * g * thud(f, 55, 0.2, 0.05)), (at, 0.8 * g * pat)]
    return carry(place(0.6, parts), 1.0, lo=300, hi=1500, drive=3)


def fx_breath():
    """Breathe in, breathe out: air in through the nose, out through the
    mouth."""
    rng = np.random.default_rng(395)
    d1, d2 = 0.6, 0.8
    t1, t2 = t_of(d1), t_of(d2)
    inhale = noise_through(rng, glide(t1, (0, 700), (d1, 1500)), 600, len(t1)) * np.sin(np.pi * t1 / d1) ** 1.5
    exhale = noise_through(rng, glide(t2, (0, 1300), (d2, 500)), 700, len(t2)) * np.sin(np.pi * t2 / d2) ** 1.3
    return place(1.5, [(0, 0.8 * inhale), (0.65, exhale)])


def fx_poke():
    """A tiny poke: one small tick."""
    rng = np.random.default_rng(396)
    return knock(rng, 2400, 0.05, 200, 0.008)


def fx_medicine():
    """The medicine bottle shaken: a rattle, three shakes."""
    rng = np.random.default_rng(397)
    parts = []
    for at in (0, 0.16, 0.32):
        parts.append((at, crackle(rng, 0.1, 14, 1500, 5000, (0.003, 0.008)) * np.exp(-np.arange(int(0.1 * SR)) / SR / 0.04)))
        parts.append((at, 0.15 * knock(rng, 1200, 0.06, 250, 0.012)))
    return place(0.55, parts)


def fx_brave():
    """So brave! A little fanfare: four toy-horn notes up with bells."""
    parts = []
    for k, (at, n, d) in enumerate(((0, "C5", 0.14), (0.16, "E5", 0.14), (0.32, "G5", 0.14), (0.48, "C6", 0.5))):
        parts.append((at, 0.5 * toy_horn(NOTE[n], d)))
        parts.append((at, 0.2 * glock(NOTE[n] * 2, 0.4)))
    parts += [(0.5, 0.3 * glock(NOTE["E7"], 0.5)), (0.56, 0.2 * glock(NOTE["G7"], 0.45))]
    return place(1.2, parts)


# ---------------------------------------------------------------- little events


def fx_drop():
    """A drip of water: "plink"."""
    return place(0.25, [(0, blip(900, 2200, 0.06, 1.0)), (0.03, 0.4 * blip(1800, 2600, 0.05, 1.0))])


def fx_tummy():
    """A hungry tummy: a soft gurgle, bubbles rising."""
    rng = np.random.default_rng(401)
    parts = []
    for k in range(6):
        at = 0.1 * k + rng.uniform(0, 0.04)
        parts.append((at, rng.uniform(0.5, 0.9) * bubble(rng, SR, (120 + 25 * k, 180 + 25 * k), (1.8, 2.6), (0.07, 0.11))))
    return carry(lowpass(place(0.8, parts), 1800), 0.5, lo=500, hi=2500)


def fx_tissue():
    """Blowing the nose: a cute little honk, "hmmff"."""
    rng = np.random.default_rng(402)
    d = 0.45
    t = t_of(d)
    n = len(t)
    f0 = glide(t, (0, 180), (0.2, 200), (d, 150))
    honk = voice(f0, [(450, 110, 1.0), (1300, 200, 0.5), (2600, 300, 0.1)], rng, breath=0.3, rough=0.3)
    air = norm(bandpass(rng.standard_normal(n), 800, 4000)) * 0.35
    return carry(lowpass(honk + air, 3200) * np.sin(np.pi * t / d) ** 0.9, 0.3, lo=500, hi=2500)


def fx_bandage():
    """A bandage: the backing peeled off, then pressed on with a pat."""
    rng = np.random.default_rng(403)
    d = 0.3
    t = t_of(d)
    peel = crackle(rng, d, 70, 1500, 7000, (0.002, 0.006)) * np.sin(np.pi * t / d) ** 0.7 * (0.5 + 0.5 * ease(t / d))
    n = int(0.08 * SR)
    pat = norm(lowpass(rng.standard_normal(n), 1000)) * np.exp(-np.arange(n) / SR / 0.012) * env(n, 0.001, 0.03)
    return place(0.6, [(0, 0.7 * peel), (0.42, 0.7 * pat)])


def fx_mosquito():
    """A mosquito: a thin little buzz that wanders by."""
    rng = np.random.default_rng(404)
    d = 1.0
    t = t_of(d)
    n = len(t)
    f = 620 * (1 + 0.06 * norm(lowpass(rng.standard_normal(n), 4))) * (1 + 0.01 * np.sin(2 * np.pi * 30 * t))
    x = norm(bandpass(harmonics(f, tilt=0.9), 500, 5000)) * (0.6 + 0.4 * norm(lowpass(rng.standard_normal(n), 3)) ** 2)
    return x * np.sin(np.pi * t / d) ** 1.2


def fx_flashlight():
    """The flashlight: a click and a soft hum as the light comes on."""
    rng = np.random.default_rng(405)
    d = 0.4
    t = t_of(d)
    hum = (np.sin(2 * np.pi * 1200 * t) + 0.3 * np.sin(2 * np.pi * 1800 * t)) * ease(t / 0.1) * (1 - ease((t - 0.25) / 0.15)) * (1 + 0.1 * np.sin(2 * np.pi * 8 * t))
    return place(0.5, [(0, 0.8 * knock(rng, 2700, 0.05, 350, 0.007)), (0.05, 0.3 * hum)])


def fx_doorbell():
    """The doorbell: ding-dong."""
    return place(1.3, [(0, 0.6 * chime(NOTE["E5"], 0.9)), (0.4, 0.55 * chime(NOTE["C5"], 1.0))])


def fx_phone_ring():
    """The telephone: an old bell phone, two rings."""
    rng = np.random.default_rng(407)
    parts = []
    for start in (0, 0.75):
        for k in range(8):
            at = start + 0.05 * k
            f = 1750 if k % 2 == 0 else 2150
            parts.append((at, (0.5 - 0.03 * k) * metal(f * rng.uniform(0.997, 1.003), 0.2, ratios=(1, 1.8, 2.9), amps=(1, .4, .2), taus=(.5, .25, .1))))
    return place(1.45, parts)


def fx_garbage_truck():
    """The garbage truck coming down the street: a music box playing the
    first phrase of Beethoven's "Für Elise" (as Taiwan's trucks do), with
    a soft bass note under each half-bar."""
    tune = [("E5", 1), ("D#5", 1), ("E5", 1), ("D#5", 1), ("E5", 1), ("B4", 1), ("D5", 1), ("C5", 1),
            ("A4", 2), (None, 1), ("C4", 1), ("E4", 1), ("A4", 1),
            ("B4", 2), (None, 1), ("E4", 1), ("G#4", 1), ("B4", 1),
            ("C5", 2), (None, 1)]
    step = 0.19
    parts = []
    for at, n, d in melody(tune, step):
        parts.append((at, 0.5 * mbox(NOTE[n], max(0.9, d + 0.6))))
    for at, n in ((8 * step, "A2"), (11 * step, "E3"), (14 * step, "E2"), (17 * step, "E3"), (20 * step, "A2")):
        parts.append((at, 0.5 * carry(pluck_bass(NOTE[n], 1.2, SR), 0.3)))
    return place(23 * step + 0.9, parts)


def fx_earthquake():
    """A little earthquake: the ground hums softly and things on the shelf
    rattle, then it passes. Low, short and quiet, never scary."""
    rng = np.random.default_rng(409)
    d = 1.5
    t = t_of(d)
    n = len(t)
    shape = np.sin(np.pi * t / d) ** 1.4
    rumble = norm(lowpass(rng.standard_normal(n), 110)) * (0.7 + 0.3 * np.sin(2 * np.pi * 4 * t))
    shake = norm(bandpass(rng.standard_normal(n), 300, 1200)) * (0.5 + 0.5 * np.sin(2 * np.pi * 11 * t) ** 2)
    x = (0.8 * carry(rumble, 0.9, lo=300, hi=1800, drive=3) + 0.3 * shake) * shape
    for _ in range(14):
        at = rng.uniform(0.2, 1.2)
        k = knock(rng, rng.uniform(1500, 3200), 0.05, 300, 0.008)
        i = int(at * SR)
        x[i:i + len(k)] += rng.uniform(0.2, 0.45) * k * shape[i]
    return x


def fx_thunder():
    """Distant thunder: a soft, far-off rumble that rolls and fades."""
    rng = np.random.default_rng(410)
    d = 1.4
    t = t_of(d)
    n = len(t)
    roll = norm(lowpass(rng.standard_normal(n), 180)) * (0.6 + 0.4 * norm(lowpass(rng.standard_normal(n), 5)) ** 2)
    shape = ease(t / 0.15) * np.exp(-t / 0.5)
    return carry(roll * shape, 0.8, lo=300, hi=1500, drive=3)


def fx_rain():
    """Soft rain (a 2 s loop): a fine patter of drops and a gentle hiss."""
    rng = np.random.default_rng(411)
    d = 2.0
    n = int(d * SR)
    x = np.zeros(n)
    for _ in range(260):
        m = rng.integers(40, 120)
        drop = rng.standard_normal(m) * np.exp(-np.arange(m) / (m / 4)) * rng.uniform(0.2, 1)
        i = rng.integers(0, n)
        idx = (i + np.arange(m)) % n  # drops that run past the end come round to the start
        x[idx] += drop
    x = norm(bandpass(x, 1500, 8000))
    hiss = 0.35 * norm(bandpass(rng.standard_normal(n), 2500, 9000))
    return x + hiss


def fx_wind():
    """Wind: a gust that rises and passes."""
    rng = np.random.default_rng(412)
    return whoosh(rng, 1.0, [(0, 350), (0.5, 1100), (1.0, 450)], 500, 1.5)


def fx_toy_drop():
    """A toy dropped into the box: a wooden clunk and a little bounce."""
    rng = np.random.default_rng(413)
    return place(0.4, [(0, 0.8 * knock(rng, 650, 0.12, 50, 0.04, second=2.2)), (0, 0.5 * carry(thud(240, 150, 0.1, 0.02), 0.5)), (0.16, 0.4 * knock(rng, 750, 0.1, 50, 0.03, second=2.2))])


def fx_broom():
    """Sweeping: swish, swish."""
    rng = np.random.default_rng(414)
    return place(0.8, [(0, whoosh(rng, 0.35, [(0, 900), (0.35, 2600)], 1500, 1.3)), (0.4, 0.9 * whoosh(rng, 0.35, [(0, 2400), (0.35, 1000)], 1500, 1.3))])


def fx_dustpan():
    """The dustpan: a little clatter of plastic and crumbs."""
    rng = np.random.default_rng(415)
    parts = [(0, 0.8 * knock(rng, 1100, 0.08, 200, 0.02)), (0.1, 0.5 * knock(rng, 1400, 0.07, 220, 0.015)), (0.16, 0.4 * knock(rng, 900, 0.08, 180, 0.02))]
    parts.append((0.05, 0.4 * crackle(rng, 0.3, 30, 1000, 5000)))
    return place(0.5, parts)


def fx_wipe():
    """Wiping the table: a cloth, once there and back."""
    rng = np.random.default_rng(416)
    d = 0.6
    t = t_of(d)
    n = len(t)
    x = noise_through(rng, 1200 + 500 * np.sin(2 * np.pi * 1.6 * t), 1200, n) * np.abs(np.sin(np.pi * 1.6 * t + 0.3)) ** 1.2
    return lowpass(x, 4500) * np.sin(np.pi * t / d) ** 0.8


def fx_peg():
    """A clothes peg clipped on: a wooden snap."""
    rng = np.random.default_rng(417)
    return mix(0.8 * knock(rng, 1900, 0.06, 200, 0.01), 0.5 * knock(rng, 700, 0.08, 60, 0.025))


def fx_watering():
    """Watering the plants: a thin trickle of water."""
    rng = np.random.default_rng(418)
    d = 1.0
    t = t_of(d)
    return water(rng, d, (2600, 2200), 14, (600, 1400), thin=True) * np.sin(np.pi * t / d) ** 0.6 * env(len(t), 0.05, 0.15)


def fx_feed():
    """Feeding the buddy: kibble pouring into the bowl, a patter of tiny
    knocks."""
    rng = np.random.default_rng(419)
    d = 0.8
    t = t_of(d)
    x = crackle(rng, d, 70, 1200, 5000, (0.004, 0.01)) * np.sin(np.pi * t / d) ** 0.8
    n = int(0.06 * SR)
    for _ in range(12):
        k = knock(rng, rng.uniform(1800, 3200), 0.06, 300, 0.006)
        i = int(rng.uniform(0.05, d - 0.08) * SR)
        x[i:i + n] += 0.4 * k[:n]
    return x


def fx_trash():
    """The rubbish bag put out: a soft thud and a rustle of plastic."""
    rng = np.random.default_rng(420)
    n = int(0.1 * SR)
    pat = norm(lowpass(rng.standard_normal(n), 900)) * np.exp(-np.arange(n) / SR / 0.015) * env(n, 0.001, 0.03)
    return place(0.45, [(0, 0.45 * carry(thud(220, 90, 0.2, 0.04), 1.0, lo=300, hi=1800, drive=3)), (0, 0.8 * pat),
                        (0.02, 0.6 * crackle(rng, 0.35, 60, 1500, 7000) * np.exp(-t_of(0.35) / 0.12))])


def fx_recycle():
    """Recycling: two bottles clink."""
    rng = np.random.default_rng(421)
    glass = dict(ratios=(1, 2.2, 3.6), amps=(1, .45, .2), taus=(.5, .25, .1))
    return place(0.55, [(0, 0.6 * metal(2500, 0.4, **glass)), (0.14 + rng.uniform(0, 0.02), 0.5 * metal(2900, 0.4, **glass))])


def fx_spill():
    """Oops, a spill: a splash and a small "oh!"."""
    rng = np.random.default_rng(422)
    parts = [(0, 0.8 * burst(rng, 0.25, 600, 5000, 0.05, attack=0.003))]
    for k in range(5):
        parts.append((0.05 + rng.uniform(0, 0.25), rng.uniform(0.15, 0.3) * blip(rng.uniform(600, 1100), rng.uniform(1600, 2600), 0.05, 1.0)))
    parts.append((0.32, 0.7 * say(rng, 0.3, [(0, 420), (0.08, 460), (0.3, 340)], [(0, 500), (0.3, 420)], [(0, 1000), (0.3, 850)], breath=0.1, size=1.2)))
    return place(0.75, parts)


def fx_deep_breath():
    """A slow, calming breath: in through the nose, out through the mouth,
    two seconds."""
    rng = np.random.default_rng(423)
    d1, d2 = 0.85, 1.05
    t1, t2 = t_of(d1), t_of(d2)
    inhale = noise_through(rng, glide(t1, (0, 600), (d1, 1300)), 500, len(t1)) * np.sin(np.pi * t1 / d1) ** 1.6
    exhale = noise_through(rng, glide(t2, (0, 1100), (d2, 450)), 600, len(t2)) * np.sin(np.pi * t2 / d2) ** 1.4
    return place(2.0, [(0, 0.8 * inhale), (0.92, exhale)])


def fx_share():
    """Sharing: a happy two-note, up."""
    return place(0.7, [(0, 0.5 * cel(NOTE["E5"], 0.5)), (0.14, 0.6 * cel(NOTE["G5"], 0.6))])


# ---------------------------------------------------------------- the buddies


def fx_buddy_dog():
    """The puppy: "woof woof", two small round barks."""
    rng = np.random.default_rng(430)
    parts = []
    for at, f in ((0, 230), (0.3, 215)):
        d = 0.16
        t = t_of(d)
        w = say(rng, d, [(0, f * 0.8), (0.03, f * 1.15), (d, f * 0.85)], [(0, 350), (0.03, 650), (d, 500)], [(0, 900), (0.03, 1150), (d, 1000)],
                breath=0.2, size=1.0, shape=lambda t: ease(t / 0.015) * (1 - ease((t - 0.09) / 0.06)), g3=0.15)
        parts.append((at, carry(lowpass(w, 3200), 0.3, lo=500, hi=2500)))
    return place(0.55, parts)


def fx_buddy_cat():
    """The kitten: "meow", small and sweet, the mouth opening and closing."""
    rng = np.random.default_rng(431)
    d = 0.55
    t = t_of(d)
    f0 = glide(t, (0, 420), (0.15, 600), (0.35, 560), (d, 380))
    f1 = glide(t, (0, 350), (0.12, 850), (0.35, 800), (d, 450))
    f2 = glide(t, (0, 2300), (0.12, 1500), (0.35, 1400), (d, 950))
    x = voice(f0, [(f1, 110, 1.0), (f2, 170, 0.5), (3000, 300, 0.1)], rng, breath=0.08)
    return lowpass(x, 3800) * ease(t / 0.05) * (1 - ease((t - 0.4) / 0.14))


def fx_buddy_rabbit():
    """The bunny: a tiny squeak, "eek"."""
    rng = np.random.default_rng(432)
    return place(0.4, [(0, chirp([(0, 1900), (0.4, 2700), (1, 2200)], 0.14)), (0.18, 0.6 * chirp([(0, 2200), (0.5, 2900), (1, 2500)], 0.11))])


def fx_buddy_duck():
    """The duckling: "quack quack", nasal and funny."""
    rng = np.random.default_rng(433)
    parts = []
    for at, f in ((0, 300), (0.26, 280)):
        d = 0.17
        t = t_of(d)
        q = voice(glide(t, (0, f * 1.1), (0.05, f), (d, f * 0.85)), [(900, 150, 1.0), (1700, 220, 0.8), (2800, 300, 0.3)], rng, breath=0.1, rough=0.25)
        parts.append((at, lowpass(q, 4000) * ease(t / 0.01) * (1 - ease((t - 0.1) / 0.06))))
    return place(0.5, parts)


def fx_buddy_happy():
    """The buddy is happy: a joyful little chirp, two notes bouncing up."""
    return place(0.45, [(0, chirp([(0, 1200), (0.5, 1700), (1, 1600)], 0.14)), (0.17, 0.9 * chirp([(0, 1600), (0.6, 2400), (1, 2200)], 0.18))])


# ---------------------------------------------------------------- the list

# name: (make, loudness in dB beside the others: below 0 sits softer).
EFFECTS = {
    # general
    "tap": (fx_tap, -4), "pop": (fx_pop, -3), "yay": (fx_yay, 0), "sticker": (fx_sticker, -2), "hint": (fx_hint, -3),
    "wrong": (fx_wrong, -4), "walk": (fx_walk, -6), "door": (fx_door, -3), "stairs": (fx_stairs, -6),
    "clock_tick": (fx_clock_tick, -6), "clock_set": (fx_clock_set, -3), "night": (fx_night, -4), "grow": (fx_grow, 0), "deco": (fx_deco, -2),
    # waking and sleeping
    "curtain": (fx_curtain, -3), "stretch": (fx_stretch, -2), "yawn": (fx_yawn, -2), "light_on": (fx_light_on, -4), "light_off": (fx_light_off, -4),
    "snore": (fx_snore, -4), "book_open": (fx_book_open, -4), "blanket": (fx_blanket, -5),
    # bathroom
    "toothpaste": (fx_toothpaste, -3), "brush": (fx_brush, -3), "rinse": (fx_rinse, -2), "water_on": (fx_water_on, -3), "water_off": (fx_water_off, -3),
    "soap": (fx_soap, -3), "rub": (fx_rub, -4), "towel": (fx_towel, -5), "toilet_flush": (fx_toilet_flush, -3), "hum": (fx_hum, -2),
    "paper": (fx_paper, -4), "splash": (fx_splash, -2), "bubble": (fx_bubble, -3), "hairdryer": (fx_hairdryer, -5), "lotion": (fx_lotion, -4), "nail_clip": (fx_nail_clip, -5),
    # getting dressed
    "zipper": (fx_zipper, -3), "button": (fx_button, -5), "cloth": (fx_cloth, -5), "sneeze": (fx_sneeze, -1), "shiver": (fx_shiver, -2), "sweat": (fx_sweat, -3),
    # eating and drinking
    "chew": (fx_chew, -3), "spoon": (fx_spoon, -4), "pour": (fx_pour, -3), "drink": (fx_drink, -2), "dishes": (fx_dishes, -3), "yum": (fx_yum, -1),
    # school and outside
    "bag_zip": (fx_bag_zip, -3), "shoes": (fx_shoes, -4), "hat": (fx_hat, -5), "bus_horn": (fx_bus_horn, -1), "bus_ride": (fx_bus_ride, -3),
    "seatbelt": (fx_seatbelt, -4), "bell": (fx_bell, -1), "clap": (fx_clap, -2), "sing": (fx_sing, -1), "line_up": (fx_line_up, -2), "bye": (fx_bye, -2),
    "traffic_wait": (fx_traffic_wait, -5), "traffic_go": (fx_traffic_go, -1), "slide": (fx_slide, -1), "swing": (fx_swing, -3), "dig": (fx_dig, -4),
    "ball_kick": (fx_ball_kick, -2), "shell": (fx_shell, -2), "cart": (fx_cart, -4), "scan": (fx_scan, -3), "coins": (fx_coins, -3), "bag_rustle": (fx_bag_rustle, -5),
    # the clinic
    "thermometer": (fx_thermometer, -3), "ahh": (fx_ahh, -1), "heartbeat": (fx_heartbeat, -3), "breath": (fx_breath, -4), "poke": (fx_poke, -6),
    "medicine": (fx_medicine, -4), "brave": (fx_brave, 0),
    # little events
    "drop": (fx_drop, -4), "tummy": (fx_tummy, -3), "tissue": (fx_tissue, -2), "bandage": (fx_bandage, -4), "mosquito": (fx_mosquito, -6),
    "flashlight": (fx_flashlight, -4), "doorbell": (fx_doorbell, -1), "phone_ring": (fx_phone_ring, -2), "garbage_truck": (fx_garbage_truck, -2),
    "earthquake": (fx_earthquake, -6), "thunder": (fx_thunder, -7), "rain": (fx_rain, -7), "wind": (fx_wind, -5), "toy_drop": (fx_toy_drop, -3),
    "broom": (fx_broom, -4), "dustpan": (fx_dustpan, -4), "wipe": (fx_wipe, -5), "peg": (fx_peg, -4), "watering": (fx_watering, -4), "feed": (fx_feed, -4),
    "trash": (fx_trash, -3), "recycle": (fx_recycle, -3), "spill": (fx_spill, -1), "deep_breath": (fx_deep_breath, -5), "share": (fx_share, -2),
    # the buddies
    "buddy_dog": (fx_buddy_dog, 0), "buddy_cat": (fx_buddy_cat, 0), "buddy_rabbit": (fx_buddy_rabbit, -1), "buddy_duck": (fx_buddy_duck, 0), "buddy_happy": (fx_buddy_happy, -1),
}
LONGEST = {name: 1.5 for name in EFFECTS}  # seconds
LONGEST.update({"garbage_truck": 6.0, "deep_breath": 2.2, "rain": 2.1, "bus_ride": 1.7, "breath": 1.6, "toilet_flush": 1.6, "earthquake": 1.6})
EFFECT_LOOPS = {"rain"}  # short sounds that repeat seamlessly: not faded at the ends
TARGET = -21.0  # dB, the loudness of a short sound at 0 (about where the sibling apps' sit)
MAX_PEAK = 0.72


# ---------------------------------------------------------------- writing and checking


def tidy(x, sr=SR):
    """A short sound: drop the silent end, then fade both ends so neither clicks."""
    x = np.asarray(x, dtype=np.float64)
    loud = np.nonzero(np.abs(x) > np.abs(x).max() * 1e-3)[0]
    x = x[: min(len(x), loud[-1] + int(0.01 * sr))]
    return x * env(len(x), 0.002, 0.012, sr)


def phone_ready(x, sr=SR):
    """Take out what a phone cannot play anyway (under 70 Hz), for more room
    under the peak. The filter works on the whole sound at once and wraps
    round, so pad it with silence on both sides first: what it rings before
    the start and after the end then stays out of the sound."""
    pad_ = int(0.1 * sr)
    return highpass(np.concatenate([np.zeros(pad_), x, np.zeros(pad_)]), 70, sr)[pad_:]


def level(x, offset, sr=SR):
    """[x] at the loudness TARGET + [offset] dB, unless that would put its
    peak over MAX_PEAK: then at MAX_PEAK. Returns the peak."""
    x = norm(x)
    return min(MAX_PEAK, 10 ** ((TARGET + offset - loudness(x, sr)) / 20))


def write(path, x, peak, sr):
    x = np.asarray(x, dtype=np.float64)
    x = x / max(1e-9, np.abs(x).max()) * peak
    data = np.round(x * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(data.tobytes())
    return data


def seam(data, sr):
    """A loop's seam, checked two ways: the jump from the last sample back to
    the first (beside the biggest step from one sample to the next in the
    20 ms either side of it: a click would stand out above them), and the
    sound over 3 kHz in the 20 ms around the seam (a click would show as a
    burst there) beside the loudest 20 ms anywhere else in the loop."""
    x = data.astype(np.float64)
    steps_ = np.abs(np.diff(x))
    jump = abs(x[0] - x[-1])
    half = len(x) // 2
    h = highpass(np.roll(x, half), 3000, sr) ** 2  # the seam now sits at [half]
    w = int(0.02 * sr)
    c = np.concatenate([[0], np.cumsum(h)])
    starts = np.arange(0, len(h) - w + 1, w // 2)
    at = half - w // 2
    here = c[at + w] - c[at]
    others = (c[starts + w] - c[starts])[np.abs(starts - at) >= w]
    near = np.concatenate([steps_[-w:], steps_[:w]]).max()  # the biggest step in the 20 ms either side
    return jump, near, here / max(1e-9, others.max())


def report(name, data, sr, loop, want=None):
    x = data.astype(np.float64) / 32767
    peak = np.abs(x).max()
    loud = loudness(x, sr)
    clipped = int(np.sum(np.abs(data) >= 32767))
    assert clipped == 0, name
    if loop:
        jump, near, burst_ = seam(data, sr)
        assert jump <= near and burst_ < 0.5, (name, jump, near, burst_)
        edge = f"seam jump {jump:3.0f} (biggest step near it {near:.0f}), seam highs {burst_:.2f} of the loudest elsewhere"
    else:
        edge = f"ends {int(data[0]):+d} / {int(data[-1]):+d}"
    short = "" if want is None or loud > want - 0.5 else f"  ({want - loud:.1f} dB under, held by the peak)"
    print(f"  {name:16s} {len(x) / sr:5.2f} s  {len(data) * 2 + 44:9,d} bytes  peak {peak:.2f}  "
          f"loudness {loud:6.1f} dB  clipped {clipped}  {edge}{short}")


def read(path):
    with wave.open(str(path), "rb") as w:
        return np.frombuffer(w.readframes(w.getnframes()), "<i2").astype(np.float64) / 32767, w.getframerate()


def preview(path, loop_seconds=6.0, gap=0.5):
    """A listening preview: [loop_seconds] of each tune, then every short
    sound in order, [gap] apart (the rain loop three times over). Prints
    where each one starts."""
    path = pathlib.Path(path)
    sr, pieces, at = 22050, [], 0.0
    print(f"preview {path}:")
    for name in list(MUSIC) + list(EFFECTS):
        x, rate = read(OUT / f"{name}.wav")
        if rate != sr:
            x = resample_poly(x, sr, rate)
        if name in MUSIC:
            x = x[: int(loop_seconds * sr)] * env(int(loop_seconds * sr), 0.01, 0.5, sr)
        elif name in EFFECT_LOOPS:
            x = np.tile(x, 3) * env(3 * len(x), 0.01, 0.3, sr)
        print(f"  {int(at // 60)}:{at % 60:04.1f}  {name}")
        pieces += [x, np.zeros(int((0.8 if name in MUSIC else gap) * sr))]
        at += (len(x) + len(pieces[-1])) / sr
    whole = np.concatenate(pieces)
    scratch = "/dev/shm" if os.path.isdir("/dev/shm") else tempfile.gettempdir()
    fd, wav = tempfile.mkstemp(suffix=".wav", dir=scratch)
    os.close(fd)
    try:
        write(wav, whole, np.abs(whole).max(), sr)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-c:a", "aac", "-b:a", "96k", str(path)], check=True)
    finally:
        os.unlink(wav)
    print(f"  total {at:.1f} s")


def main():
    only = sys.argv[1:] if len(sys.argv) > 1 and sys.argv[1] != "preview" else None
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / ".keep").unlink(missing_ok=True)
    print("music (16,000 Hz, loops), 8 to 12 dB under the short sounds:")
    for name, (make, offset) in MUSIC.items():
        if only and name not in only:
            continue
        tune = make()
        x = tune.render()
        assert 18 <= len(x) / LOOP_SR <= 30, (name, len(x) / LOOP_SR)
        report(name, write(OUT / f"{name}.wav", x, level(x, offset, LOOP_SR), LOOP_SR), LOOP_SR, True)
        over = loudness(tune.render(band=False), LOOP_SR) - loudness(tune.render(lead=False), LOOP_SR)
        print(f"  {'':16s} the tune is {over:.1f} dB over the band (through a phone)")
    print(f"short sounds (22,050 Hz), loudness {TARGET:.0f} dB plus or minus, peaks at most {MAX_PEAK}:")
    for name, (make, offset) in EFFECTS.items():
        if only and name not in only:
            continue
        x = make()
        if name in EFFECT_LOOPS:
            x = np.asarray(x, dtype=np.float64)
            x = highpass(x, 70, SR)  # wraps round, as a loop should
        else:
            x = tidy(phone_ready(x))
        assert len(x) / SR <= LONGEST[name], (name, len(x) / SR)
        data = write(OUT / f"{name}.wav", x, level(x, offset), SR)
        if name in EFFECT_LOOPS:
            report(name, data, SR, True)
        else:
            assert data[0] == 0 and data[-1] == 0, name
            report(name, data, SR, False, TARGET + offset)
    if only:
        return
    names = {p.stem for p in OUT.glob("*.wav")}
    assert names == set(MUSIC) | set(EFFECTS), names ^ (set(MUSIC) | set(EFFECTS))
    assert {p.name for p in OUT.iterdir()} == {f"{n}.wav" for n in names}, "only the sounds belong in the folder"
    total = sum(p.stat().st_size for p in OUT.glob("*.wav"))
    print(f"{len(MUSIC) + len(EFFECTS)} sounds, {total:,} bytes ({total / 1024 / 1024:.2f} MiB) in {OUT}")
    assert total < LIMIT, f"the sounds must stay under {LIMIT:,} bytes"
    if len(sys.argv) == 3 and sys.argv[1] == "preview":
        preview(sys.argv[2])


if __name__ == "__main__":
    main()
