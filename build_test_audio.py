import struct, math, wave, os

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "CallMe", "test-message.wav")

SR = 44100
DUR = 2.0  # 2 seconds total
# G major chord arpeggio: G3, B3, D4, G4
freqs = [196.00, 246.94, 293.66, 392.00]
n_per_note = int(SR * (DUR / len(freqs)))

frames = []
for f in freqs:
    for i in range(n_per_note):
        t = i / SR
        env = min(t / 0.03, 1.0, (DUR/len(freqs) - t) / 0.05)
        val = math.sin(2 * math.pi * f * t) * env * 0.45
        frames.append(struct.pack("<h", int(val * 32767)))

with wave.open(OUT, "w") as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(SR)
    for fr in frames:
        w.writeframes(fr)

print(f"✓ Wrote {OUT}  ({len(frames) * 2} bytes, {len(freqs)} notes, {DUR:.1f}s)")
