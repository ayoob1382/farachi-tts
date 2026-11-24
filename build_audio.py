#!/usr/bin/env python3
"""
ساخت صدا: هر segment یک درخواست جدا به Gemini.
خروجی: <out>/voice.wav و <out>/timings.json (زمان دقیق شروع/پایان هر segment از طول واقعی صدا)

استفاده:
  python build_audio.py scripts/spotlight.json --out build            # با Gemini
  python build_audio.py scripts/spotlight.json --out build --fake     # صدای ساختگی برای تست

متغیرهای محیطی:
  GEMINI_API_KEY   کلید Gemini
  GEMINI_TTS_MODEL اسم مدل (پیش‌فرض: gemini-3.8-flash-tts)
"""
import argparse, json, os, sys, time, wave, hashlib
import numpy as np

SR = 24000            # خروجی Gemini: PCM 16bit مونو ۲۴ کیلوهرتز
LEAD = 0.6            # سکوت اول ویدیو
GAP = 0.45            # مکث بین segmentها
TAIL = 1.8            # سکوت آخر ویدیو
TARGET_RMS_DB = -21.0 # بلندی هدف هر segment (برای یکدست شدن بین درخواست‌ها)


def fake_speech(text, seed):
    """صدای ساختگی: نویز مدوله‌شده شبیه هجا. طولش متناسب با تعداد حروف است."""
    rng = np.random.default_rng(seed)
    dur = max(1.2, len(text) * 0.07)
    n = int(dur * SR)
    t = np.arange(n) / SR
    f0 = 120 + 25 * np.sin(2 * np.pi * 0.7 * t)
    phase = 2 * np.pi * np.cumsum(f0) / SR
    tone = sum(np.sin(k * phase) / k for k in range(1, 6))
    syl = 0.5 + 0.5 * np.sin(2 * np.pi * 4.2 * t + rng.uniform(0, 6))
    env = np.clip(syl, 0, 1) ** 1.5
    fade = np.minimum(1, np.minimum(t / 0.05, (dur - t) / 0.12))
    x = tone * env * fade
    x = x / (np.abs(x).max() + 1e-9) * (0.2 + 0.05 * rng.random())  # بلندی تصادفی؛ نرمال‌سازی درستش می‌کند
    return (x * 32767).astype(np.int16)


# لحن‌های آماده (همون‌هایی که توی gemini_tts_test.py بود). توی اسکریپت با "tone": "calm" صدا می‌زنی.
STYLES = {
    "calm": "calm, clear and friendly, like explaining something to a smart friend",
    "curious": "curious and lightly intrigued, natural conversational pace",
    "serious": "serious, steady and respectful",
    "excited": "warm and energetic, not shouting",
    "warm": "warm and conclusive, relaxed pace",
}


def resolve(seg, spec):
    """صدا و لحن یک جمله. اولویت: خود جمله، بعد پیش‌فرض کل اسکریپت. لحن خالی = بدون دستور لحن."""
    voice = seg.get("voice") or spec.get("voice") or "Kore"
    style = seg.get("style") or STYLES.get(seg.get("tone", ""), None)
    if not style and "style" not in seg and "tone" not in seg:
        style = spec.get("style") or STYLES.get(spec.get("tone", ""), None)
    return voice, style


URL = os.environ.get("GEMINI_URL") or "https://generativelanguage.googleapis.com/v1beta/interactions"


def find_audio(node):
    """آخرین بلوک صوتی (base64) رو هرجای پاسخ باشه پیدا می‌کنه. مثل gemini_tts_test.py"""
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


def decode_to_pcm(blob):
    """هر فرمت صوتی (wav و...) رو با ffmpeg به PCM مونو ۲۴ کیلوهرتز تبدیل می‌کنه.
    اگه هدر نداشت، PCM خام ۲۴ کیلوهرتز فرض می‌شه."""
    import subprocess
    if blob[:4] in (b"RIFF", b"ID3\x03", b"OggS", b"fLaC") or blob[:2] == b"\xff\xfb":
        try:
            r = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", "pipe:0", "-f", "s16le",
                                "-ar", str(SR), "-ac", "1", "pipe:1"], input=blob, capture_output=True)
        except FileNotFoundError:
            sys.exit("ffmpeg روی این سیستم نصب نیست. (روی GitHub باید توی مرحله‌ی نصب ابزارها نصب بشه)")
        if r.returncode != 0:
            sys.exit("ffmpeg نتونست صدا رو بخونه: " + r.stderr.decode(errors="replace")[:300])
        return np.frombuffer(r.stdout, dtype=np.int16).copy()
    return np.frombuffer(blob, dtype=np.int16).copy()


def gemini_speech(text, voice, model, style=None, retries=5):
    import base64, urllib.request, urllib.error
    ann = {"type": "speech_metadata"}
    if style:
        ann["style"] = style
    body = {"model": model,
            "input": [{"type": "user_input", "content": [
                {"type": "text", "text": text, "annotations": [ann]}]}],
            "response_format": {"type": "audio"},
            "generation_config": {"speech_config": [{"voice": voice}]}}
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(URL, data=json.dumps(body).encode(), method="POST",
                headers={"Content-Type": "application/json", "x-goog-api-key": os.environ["GEMINI_API_KEY"]})
            with urllib.request.urlopen(req, timeout=300) as r:
                data = find_audio(json.loads(r.read()))
            if not data:
                raise RuntimeError("پاسخ بدون صدا برگشت")
            return decode_to_pcm(base64.b64decode(data))
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="replace")[:400]
            print(f"  تلاش {attempt}/{retries} ناموفق: HTTP {e.code} {detail}", file=sys.stderr)
            if e.code in (400, 401, 403, 404):  # تکرارش فایده نداره
                sys.exit(f"خطای HTTP {e.code} (تکرار نمی‌شه). مدل: {model}. جزئیات بالا.")
            if attempt == retries:
                sys.exit(f"بعد از {retries} تلاش نشد (HTTP {e.code}).")
            time.sleep(min(60, 5 * attempt * attempt))
        except Exception as e:
            print(f"  تلاش {attempt}/{retries} ناموفق: {str(e)[:200]}", file=sys.stderr)
            if attempt == retries:
                sys.exit(f"بعد از {retries} تلاش نشد. آخرین خطا: {str(e)[:300]}")
            time.sleep(min(60, 5 * attempt * attempt))


def trim_silence(x, thresh=0.01, keep=0.08):
    """سکوت اضافه‌ی اول و آخر هر segment رو کم می‌کنه تا زمان‌بندی دقیق بشه."""
    a = np.abs(x.astype(np.float32)) / 32768
    idx = np.where(a > thresh)[0]
    if len(idx) == 0:
        return x
    s = max(0, idx[0] - int(keep * SR))
    e = min(len(x), idx[-1] + int(keep * SR))
    return x[s:e]


def normalize_rms(x, target_db=TARGET_RMS_DB):
    f = x.astype(np.float32) / 32768
    active = f[np.abs(f) > 0.01]
    rms = np.sqrt(np.mean(active ** 2)) if len(active) else 1e-4
    gain = 10 ** (target_db / 20) / max(rms, 1e-6)
    gain = min(gain, 8.0)
    y = np.clip(f * gain, -0.97, 0.97)
    return (y * 32767).astype(np.int16)


def f0_of(x):
    """زیر و بمی (هرتز) = میانه‌ی فرکانس پایه‌ی فریم‌های صدادار. اگه صدایی پیدا نشد None."""
    f = x.astype(np.float32) / 32768
    f = f[: len(f) // 3 * 3].reshape(-1, 3).mean(axis=1)   # ۲۴k -> ۸k
    sr = SR // 3
    win, hop = int(0.04 * sr), int(0.02 * sr)
    lo, hi = int(sr / 400), int(sr / 70)
    vals = []
    for a in range(0, len(f) - win - hi, hop):
        fr = f[a:a + win + hi]
        seg = fr[:win]
        if np.sqrt(np.mean(seg ** 2)) < 0.02:
            continue
        seg = seg - seg.mean()
        ac = np.array([np.dot(seg, fr[l:l + win]) for l in range(lo, hi)])
        e0 = np.dot(seg, seg) + 1e-9
        k = int(np.argmax(ac))
        if ac[k] / e0 > 0.5:
            vals.append(sr / (lo + k))
    return float(np.median(vals)) if len(vals) >= 5 else None


def fix_voice_outliers(xs, segs, plan, model, cache_files, tol=0.25, tries=3):
    """جمله‌هایی که زیر و بمی‌شون با میانه‌ی جمله‌های هم‌صدای خودشون فرق داره دوباره ساخته می‌شن.
    مقایسه فقط داخل هر صدا انجام می‌شه، چون صداهای مختلف طبیعتاً زیر و بمی متفاوت دارن."""
    f0s = [f0_of(x) for x in xs]
    for voice in sorted({v for v, _ in plan}):
        idx = [i for i, (v, _) in enumerate(plan) if v == voice]
        known = [f0s[i] for i in idx if f0s[i]]
        if len(known) < 3:
            print(f"کنترل صدا برای {voice}: جمله‌ی کافی نیست (حداقل ۳ تا)، رد شد.")
            continue
        ref = float(np.median(known))
        print(f"کنترل یکدستی صدای {voice}: مرجع ~{ref:.0f} هرتز")
        for i in idx:
            v = f0s[i]
            label = f"{v:.0f} هرتز" if v else "نامشخص"
            if v is None or abs(v - ref) / ref <= tol:
                print(f"  segment {i+1}: {label}  OK")
                continue
            print(f"  segment {i+1}: {label}  با بقیه نمی‌خونه")
            best_dev, best_x = abs(v - ref) / ref, xs[i]
            for t in range(1, tries + 1):
                print(f"    ساخت دوباره {t}/{tries}")
                time.sleep(1.0)
                x = normalize_rms(trim_silence(gemini_speech(segs[i]["text"].strip(), plan[i][0], model, plan[i][1])))
                v2 = f0_of(x)
                dev = abs(v2 - ref) / ref if v2 else 9
                print(f"    -> {v2:.0f} هرتز" if v2 else "    -> نامشخص")
                if dev < best_dev:
                    best_dev, best_x = dev, x
                if dev <= tol:
                    break
            xs[i] = best_x
            np.save(cache_files[i], best_x)
            if best_dev > tol:
                print(f"  هشدار: segment {i+1} بعد از {tries} بار هنوز با بقیه نمی‌خونه. موقع دیدن ویدیو گوش بده و اگه لازم بود متنش رو بلندتر کن یا با جمله‌ی کناری ادغام کن.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("script")
    ap.add_argument("--out", default="build")
    ap.add_argument("--fake", action="store_true")
    args = ap.parse_args()

    spec = json.load(open(args.script, encoding="utf-8"))
    segs = spec["segments"]
    plan = [resolve(sg, spec) for sg in segs]   # (صدا، لحن) هر جمله
    model = os.environ.get("GEMINI_TTS_MODEL") or "gemini-3.8-flash-tts"
    os.makedirs(args.out, exist_ok=True)
    cache_dir = os.path.join(args.out, "seg_cache")
    os.makedirs(cache_dir, exist_ok=True)

    if not args.fake and not os.environ.get("GEMINI_API_KEY"):
        sys.exit("GEMINI_API_KEY تنظیم نشده. یا secret رو بذار یا با --fake تست کن.")

    xs, cache_files = [], []
    for i, s in enumerate(segs):
        text = s["text"].strip()
        voice, style = plan[i]
        key = hashlib.sha1(f"{model}|{voice}|{style}|{text}|{args.fake}".encode()).hexdigest()[:16]
        cf = os.path.join(cache_dir, f"{i:03d}_{key}.npy")
        if os.path.exists(cf):
            x = np.load(cf)
            print(f"[{i+1}/{len(segs)}] از کش")
        else:
            print(f"[{i+1}/{len(segs)}] {voice}{' | ' + style[:30] if style else ''} | {text[:30]}")
            raw = fake_speech(text, i) if args.fake else gemini_speech(text, voice, model, style)
            x = normalize_rms(trim_silence(raw))
            np.save(cf, x)
            if not args.fake:
                time.sleep(1.0)  # فاصله‌ی کوچک برای محدودیت نرخ
        xs.append(x)
        cache_files.append(cf)

    if not args.fake:
        fix_voice_outliers(xs, segs, plan, model, cache_files)

    chunks, timings, cur = [], [], LEAD
    chunks.append(np.zeros(int(LEAD * SR), dtype=np.int16))
    for i, (s, x) in enumerate(zip(segs, xs)):
        text = s["text"].strip()
        dur = len(x) / SR
        timings.append({"start": round(cur, 3), "end": round(cur + dur, 3), "text": text})
        chunks.append(x)
        gap = GAP if i < len(segs) - 1 else TAIL
        chunks.append(np.zeros(int(gap * SR), dtype=np.int16))
        cur += dur + gap

    total = cur
    audio = np.concatenate(chunks)
    with wave.open(os.path.join(args.out, "voice.wav"), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(audio.tobytes())
    json.dump({"duration": round(total, 3), "title": spec.get("title", ""), "sentences": timings},
              open(os.path.join(args.out, "timings.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"voice.wav و timings.json ساخته شد. مدت کل: {total:.1f} ثانیه، {len(segs)} segment")


if __name__ == "__main__":
    main()
