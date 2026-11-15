#!/usr/bin/env python3
"""Test Persian Chatterbox (community finetune) on CPU. Usage: python chatterbox_fa_test.py prepared.json outdir"""
import json, os, sys, time, traceback
import torchaudio as ta
from huggingface_hub import hf_hub_download
from safetensors.torch import load_file
from chatterbox.mtl_tts import ChatterboxMultilingualTTS

src, outdir = sys.argv[1], sys.argv[2]
PICK = [1, 5]          # segment numbers to test (same ones heard with edge-tts)
EXAG = [0.5, 0.8]      # emotion exaggeration levels to compare
os.makedirs(outdir, exist_ok=True)
segs = json.load(open(src, encoding="utf-8"))
ref = "ref.wav" if os.path.exists("ref.wav") else None
print("reference voice:", ref, flush=True)
try:
    t0 = time.time()
    model = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
    path = hf_hub_download("Thomcles/Chatterbox-TTS-Persian-Farsi", "t3_fa.safetensors")
    res = model.t3.load_state_dict(load_file(path, device="cpu"), strict=False)
    print("weights loaded: missing", len(res.missing_keys), "unexpected", len(res.unexpected_keys), "in", round(time.time() - t0), "s", flush=True)
    model.t3.to("cpu").eval()
    for i in PICK:
        text = segs[i - 1]["tts_text"]
        for ex in EXAG:
            start, wav, used = time.time(), None, None
            for lang in (None, "ar"):
                try:
                    wav = model.generate(text, language_id=lang, audio_prompt_path=ref, exaggeration=ex, cfg_weight=0.5)
                    used = lang
                    break
                except Exception as e:
                    print("language_id", lang, "failed:", repr(e)[:300], flush=True)
            if wav is None:
                continue
            name = f"{outdir}/seg{i}_ex{ex}.wav"
            ta.save(name, wav, model.sr)
            print("saved", name, "in", round(time.time() - start), "s, language_id", used, flush=True)
except Exception:
    traceback.print_exc()
    sys.exit(1)
