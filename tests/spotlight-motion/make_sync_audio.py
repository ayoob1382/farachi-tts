#!/usr/bin/env python3
"""Create a short audible sync-marker track for the spotlight motion test (not narration)."""
import json, math, wave, struct
from pathlib import Path
T=json.loads(Path(__file__).with_name("timings.json").read_text(encoding="utf8"))
sr=48000; duration=T["duration"]; samples=[0.0]*int(sr*duration)
# Two brief beeps at each subtitle onset: deliberately distinct from narration.
for i,seg in enumerate(T["sentences"]):
    start=seg["start"]; freq=880 if i%2==0 else 660
    for offset in (0.0,0.14):
        st=int(sr*(start+offset)); n=min(int(sr*.075),len(samples)-st)
        for k in range(n):
            env=max(0,1-k/n)*0.22
            samples[st+k]+=env*math.sin(2*math.pi*freq*k/sr)
with wave.open(str(Path(__file__).parent/"sync-cues.wav"),"wb") as w:
    w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr)
    w.writeframes(b''.join(struct.pack('<h',int(max(-1,min(1,x))*32767)) for x in samples))
print(f"cue track ready: {duration:.3f}s, {len(T['sentences'])} subtitle anchors")
