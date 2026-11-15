#!/usr/bin/env python3
"""Audio edit test: before (one-shot edge-tts) vs after (per-sentence, pauses, EQ, compression, light room, loudness).
Usage: python audio_edit.py prepared.json outdir"""
import asyncio, json, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
TONES = json.load(open(os.path.join(HERE, "tones.json"), encoding="utf-8"))["edge"]
VOICE, PICK = "fa-IR-DilaraNeural", [1, 5]
PAUSE = {".": 0.45, "!": 0.45, "؟": 0.6, "?": 0.6}   # seconds after a sentence ending
FAKE = os.environ.get("FAKE_TTS") == "1"               # offline test mode (tones instead of speech)
CHAIN = ("highpass=f=70,equalizer=f=200:width_type=o:width=1.5:g=2,equalizer=f=3500:width_type=o:width=1.5:g=1.5,"
         "acompressor=threshold=-20dB:ratio=3:attack=10:release=150:makeup=3,"
         "aecho=0.9:0.85:40|70:0.2|0.12,loudnorm=I=-16:TP=-1.5:LRA=11")

def ff(*a):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *a], check=True)

async def synth(text, path, tone):
    if FAKE:
        ff("-f", "lavfi", "-i", f"sine=frequency=220:duration={max(1, len(text) / 30):.1f}", path)
        return
    import edge_tts
    e = TONES[tone]
    await edge_tts.Communicate(text, VOICE, rate=e["rate"], pitch=e["pitch"]).save(path)

def split_sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!؟?])\s+", text) if s.strip()]

async def main(src, outdir):
    segs = json.load(open(src, encoding="utf-8"))
    os.makedirs(outdir, exist_ok=True)
    for i in PICK:
        s = segs[i - 1]
        await synth(s["tts_text"], f"{outdir}/seg{i}_before.mp3", s["tone"])
        with tempfile.TemporaryDirectory() as tmp:
            lines = []
            for n, sent in enumerate(split_sentences(s["tts_text"])):
                mp3, wav = f"{tmp}/s{n}.mp3", f"{tmp}/s{n}.wav"
                await synth(sent, mp3, s["tone"])
                ff("-i", mp3, "-ar", "24000", "-ac", "1", wav)
                lines.append(f"file '{wav}'")
                sil = f"{tmp}/p{n}.wav"
                ff("-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", str(PAUSE.get(sent[-1], 0.4)), sil)
                lines.append(f"file '{sil}'")
            lst = f"{tmp}/list.txt"
            open(lst, "w").write("\n".join(lines))
            joined = f"{tmp}/joined.wav"
            ff("-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", joined)
            ff("-i", joined, "-af", CHAIN, "-ar", "44100", "-b:a", "192k", f"{outdir}/seg{i}_after.mp3")
        print("ok seg", i, flush=True)

asyncio.run(main(sys.argv[1], sys.argv[2]))
