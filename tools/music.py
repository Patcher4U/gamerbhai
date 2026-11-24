"""Original synthwave background music, generated from scratch (no samples, no copyright).
  python tools/music.py out.wav 30 [seed]
Each seed gives a different key/progression/tempo, so Shorts don't all sound the same.
"""
import sys, wave, numpy as np

SR = 44100
PROGS = [[0, -4, 3, -2], [0, 3, -4, -2], [0, -2, -4, -5], [0, 5, 3, -2]]   # semitone offsets from the key root
MINOR = [0, 3, 7]; MAJOR = [0, 4, 7]

def note(semis_from_a4): return 440.0 * 2 ** (semis_from_a4 / 12)
def env(n, a=0.01, r=0.2):
    e = np.ones(n); ai = int(a * SR); ri = int(r * SR)
    if ai: e[:ai] = np.linspace(0, 1, ai)
    if ri and ri < n: e[-ri:] *= np.linspace(1, 0, ri)
    return e
def saw(f, n, detune=0.0):
    t = np.arange(n) / SR
    return sum(2 * ((t * f * (1 + d)) % 1) - 1 for d in (-detune, 0, detune)) / 3
def lowpass(x, k):
    return np.convolve(x, np.ones(k) / k, mode="same")

def make(seconds, seed=0):
    rng = np.random.default_rng(seed)
    bpm = int(rng.choice([96, 100, 104, 110])); beat = 60 / bpm
    key = int(rng.integers(-9, -2))          # root a bit below A4 (around E3..C4 region after octave shifts)
    prog = PROGS[seed % len(PROGS)]
    n = int(seconds * SR); out = np.zeros(n)
    bar = 4 * beat; nbars = int(np.ceil(seconds / bar))
    t_kick = np.arange(int(0.25 * SR)) / SR
    kick = np.sin(2 * np.pi * (50 + 90 * np.exp(-t_kick * 30)) * t_kick) * np.exp(-t_kick * 9)
    noise = rng.standard_normal(int(0.2 * SR))
    snare = noise * np.exp(-np.arange(len(noise)) / SR * 22) * 0.5
    hat = np.diff(rng.standard_normal(int(0.05 * SR)), prepend=0) * np.exp(-np.arange(int(0.05 * SR)) / SR * 90) * 0.25
    def put(sig, at, gain=1.0):
        i = int(at * SR)
        if i >= n: return
        j = min(n, i + len(sig)); out[i:j] += sig[: j - i] * gain
    for b in range(nbars):
        root = key + prog[b % len(prog)]
        chord = MINOR if prog[b % len(prog)] in (0, 5) else MAJOR
        t0 = b * bar
        # pad: detuned saws, softened
        pn = int(bar * SR)
        pad = sum(saw(note(root + c), pn, 0.004) for c in chord) / 3
        put(lowpass(pad, 18) * env(pn, 0.3, 0.4), t0, 0.16)
        # bass: 8th notes on the root, an octave down
        bn = int(beat / 2 * SR)
        for k in range(8):
            put(lowpass(saw(note(root - 12), bn), 6) * env(bn, 0.005, 0.08), t0 + k * beat / 2, 0.22)
        # arp: 16ths over the chord, two octaves of variety
        an = int(beat / 4 * SR)
        for k in range(16):
            c = chord[k % 3] + (12 if (k // 3) % 2 else 0)
            put(np.sign(np.sin(2 * np.pi * note(root + c + 12) * np.arange(an) / SR)) * env(an, 0.002, 0.05), t0 + k * beat / 4, 0.035)
        # drums
        for k in range(4):
            put(kick, t0 + k * beat, 0.55)
            if k in (1, 3): put(snare, t0 + k * beat, 0.35)
        for k in range(8): put(hat, t0 + k * beat / 2, 0.6 if k % 2 else 0.35)
    out *= env(n, 1.0, 1.5)                      # fade in/out
    out /= max(1e-9, np.max(np.abs(out))) / 0.8  # normalize
    return out

def whoosh(seconds=0.5, seed=0):
    rng = np.random.default_rng(seed + 99); n = int(seconds * SR)
    x = lowpass(rng.standard_normal(n), 30) * np.sin(np.linspace(0, np.pi, n)) ** 2
    return x / max(1e-9, np.max(np.abs(x))) * 0.5

def write(path, x):
    st = np.stack([x, x], axis=1)
    data = (np.clip(st, -1, 1) * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(data.tobytes())

def soundtrack(path, seconds, cut_times, seed=0):
    """Music bed + a soft whoosh at each slide change."""
    m = make(seconds, seed)
    for t in cut_times:
        w = whoosh(0.5, seed); i = int(max(0, t - 0.25) * SR); j = min(len(m), i + len(w)); m[i:j] += w[: j - i] * 0.6
    m /= max(1e-9, np.max(np.abs(m))) / 0.85
    write(path, m)

if __name__ == "__main__":
    write(sys.argv[1], make(float(sys.argv[2]), int(sys.argv[3]) if len(sys.argv) > 3 else 0)); print("ok")
