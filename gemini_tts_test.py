#!/usr/bin/env python3
"""Gemini TTS test for Persian. Usage: python gemini_tts_test.py prepared.json outdir   (needs env GEMINI_API_KEY)"""
import base64, json, os, sys, urllib.error, urllib.request

URL = "https://generativelanguage.googleapis.com/v1beta/interactions"
MODELS = ["gemini-3.8-flash-tts"]          # first one that works is used
PICK = [1, 5]                               # same segments heard with edge-tts
STYLES = {
    "calm": "calm, clear and friendly, like explaining something to a smart friend",
    "curious": "curious and lightly intrigued, natural conversational pace",
    "serious": "serious, steady and respectful",
    "excited": "warm and energetic, not shouting",
    "warm": "warm and conclusive, relaxed pace",
}
# (label, voice, use_style)
VARIANTS = [("plain_Kore", "Kore", False), ("styled_Kore", "Kore", True), ("styled_Sulafat", "Sulafat", True)]

def find_audio(node):
    """Return base64 audio data from the last audio block anywhere in the response."""
    found = []
    def walk(n):
        if isinstance(n, dict):
            if n.get("type") == "audio" and isinstance(n.get("data"), str):
                found.append(n["data"])
            for v in n.values():
                walk(v)
        elif isinstance(n, list):
            for v in n:
                walk(v)
    walk(node)
    return found[-1] if found else None

def synth(model, text, voice, style):
    ann = {"type": "speech_metadata"}
    if style:
        ann["style"] = style
    body = {"model": model,
            "input": [{"type": "user_input", "content": [{"type": "text", "text": text, "annotations": [ann]}]}],
            "response_format": {"type": "audio"},
            "generation_config": {"speech_config": [{"voice": voice}]}}
    req = urllib.request.Request(URL, data=json.dumps(body).encode(), method="POST",
                                 headers={"Content-Type": "application/json", "x-goog-api-key": os.environ["GEMINI_API_KEY"]})
    with urllib.request.urlopen(req, timeout=300) as r:
        return find_audio(json.loads(r.read()))

def main(src, outdir):
    segs = json.load(open(src, encoding="utf-8"))
    os.makedirs(outdir, exist_ok=True)
    model = None
    for i in PICK:
        s = segs[i - 1]
        for label, voice, use_style in VARIANTS:
            style = STYLES[s["tone"]] if use_style else None
            for m in ([model] if model else MODELS):
                try:
                    data = synth(m, s["tts_text"], voice, style)
                except urllib.error.HTTPError as e:
                    print("model", m, "HTTP", e.code, e.read().decode()[:400], flush=True)
                    continue
                if data:
                    model = m
                    open(f"{outdir}/seg{i}_{label}.wav", "wb").write(base64.b64decode(data))
                    print("saved seg", i, label, "with", m, flush=True)
                    break
                print("no audio in response for", m, flush=True)
    if model is None:
        sys.exit("No model produced audio. See messages above.")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
