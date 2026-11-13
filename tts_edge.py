#!/usr/bin/env python3
"""python tts_edge.py prepared.json outdir
For each segment: raw (plain text, default settings) vs prepared (skill output + tone settings), so the skill's effect can be heard."""
import asyncio, json, os, sys
import edge_tts
HERE = os.path.dirname(os.path.abspath(__file__))
TONES = json.load(open(os.path.join(HERE, "tones.json"), encoding="utf-8"))["edge"]
DILARA, FARID = "fa-IR-DilaraNeural", "fa-IR-FaridNeural"

async def main(src, outdir):
    segs = json.load(open(src, encoding="utf-8"))
    os.makedirs(outdir, exist_ok=True)
    for i, s in enumerate(segs, 1):
        e = TONES[s["tone"]]
        jobs = [("A_raw_Dilara", s["raw_text"], DILARA, "+0%", "+0Hz"),
                ("B_prepared_Dilara", s["tts_text"], DILARA, e["rate"], e["pitch"]),
                ("C_prepared_Farid", s["tts_text"], FARID, e["rate"], e["pitch"])]
        for tag, text, voice, rate, pitch in jobs:
            await edge_tts.Communicate(text, voice, rate=rate, pitch=pitch).save(f"{outdir}/seg{i}_{tag}.mp3")
            print("ok", i, tag)

asyncio.run(main(sys.argv[1], sys.argv[2]))
