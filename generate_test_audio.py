#!/usr/bin/env python3
"""
Generate a test audio file for CallMe prototype.
Creates a pleasant 5-second WAV with a soft chord/melody.
"""
import struct, math, os

SAMPLE_RATE = 44100
DURATION = 6.0
OUT_PATH = os.path.join(os.path.dirname(__file__), "CallMe", "test-message.wav")

def tone(freq, dur, sr=SAMPLE_RATE):
    n = int(sr * dur)
    return [math.sin(2*math.pi*freq*i/sr) for i in range(n)]

def envelope(samples, fade=0.08):
    n = len(samples)
    out = []
    for i, s in enumerate(samples):
        t = i / SAMPLE_RATE
        env = min(t/fade, 1.0, (DURATION-t)/fade)
        out.append(s * env)
    return out

# Build a gentle ascending chord progression
raw = []
raw.extend(tone(261.63, 1.2))   # C4
raw.extend(tone(329.63, 1.2))   # E4
raw.extend(tone(392.00, 1.2))   # G4
raw.extend(tone(523.25, 1.2))   # C5
raw.extend(tone(392.00, 1.2))   # G4
raw.extend(tone(329.63, 1.2))   # E4

# Mix down to mono sum and normalize
mixed = [sum(ch) for ch in zip(*[raw[i::len(raw)] for i in range(len(raw))])] if len(raw) > 1 else raw
maxv = max(abs(x) for x in mixed) or 1.0
norm = [x / maxv * 0.4 for x in mixed]

with open(OUT_PATH, "wb") as f:
    f.write(b"RIFF")
    f.write(struct.pack("<I", 36 + len(norm)*2))
    f.write(b"WAVE")
    f.write(b"fmt ")
    f.write(struct.pack("<I", 16))
    f.write(struct.pack("<H", 1))    # PCM
    f.write(struct.pack("<H", 1))    # mono
    f.write(struct.pack("<I", SAMPLE_RATE))
    f.write(struct.pack("<I", SAMPLE_RATE*2))
    f.write(struct.pack("<H", 2))
    f.write(struct.pack("<H", 16))
    f.write(b"data")
    f.write(struct.pack("<I", len(norm)*2))
    for s in norm:
        f.write(struct.pack("<h", int(s*32767)))

print(f"Wrote {OUT_PATH}  ({len(norm)/SAMPLE_RATE:.1f}s, {SAMPLE_RATE}Hz)")
