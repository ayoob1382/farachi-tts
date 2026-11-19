#!/usr/bin/env python3
"""Loudness-normalize every .wav in a folder to YouTube-friendly level. Usage: python normalize.py folder"""
import glob, os, subprocess, sys
folder = sys.argv[1]
for f in sorted(glob.glob(os.path.join(folder, "*.wav"))):
    if f.endswith("_norm.wav"):
        continue
    out = f[:-4] + "_norm.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f,
                    "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", "44100", "-ac", "1", out], check=True)
    print("ok", os.path.basename(out), flush=True)
