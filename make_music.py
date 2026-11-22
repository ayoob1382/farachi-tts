#!/usr/bin/env python3
"""موزیک موقت (فقط برای تست). آهنگ واقعی رو توی video/music/ بذار تا جایگزین بشه."""
import sys, wave, numpy as np
out = sys.argv[1] if len(sys.argv) > 1 else "music.wav"
SR, dur = 44100, 32
t = np.arange(int(SR * dur)) / SR
chords = [(220.0, 277.18, 329.63), (196.0, 246.94, 293.66), (174.61, 220.0, 261.63), (196.0, 246.94, 329.63)]
x = np.zeros_like(t)
step = dur / 8
for i in range(8):
    a, b = int(i * step * SR), int((i + 1) * step * SR)
    seg = t[a:b] - t[a]
    env = np.minimum(1, seg / 1.2) * np.minimum(1, (step - seg) / 1.2)
    for f in chords[i % 4]:
        x[a:b] += np.sin(2 * np.pi * f * seg) * env * 0.12
        x[a:b] += np.sin(2 * np.pi * f * 2.003 * seg) * env * 0.04
x *= 0.9 / np.abs(x).max()
with wave.open(out, "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((x * 32767).astype(np.int16).tobytes())
print("music ->", out)
