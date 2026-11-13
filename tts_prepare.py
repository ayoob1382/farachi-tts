#!/usr/bin/env python3
"""Prepare Persian narration segments for TTS.
Input JSON: [{"text": "...", "tone": "calm"}, ...]   Output JSON: tts_text + two prompt formats + flags."""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
Z = "\u200c"
ONES = ["صفر","یک","دو","سه","چهار","پنج","شش","هفت","هشت","نه"]
TEENS = ["ده","یازده","دوازده","سیزده","چهارده","پانزده","شانزده","هفده","هجده","نوزده"]
TENS = ["","","بیست","سی","چهل","پنجاه","شصت","هفتاد","هشتاد","نود"]
HUND = ["","صد","دویست","سیصد","چهارصد","پانصد","ششصد","هفتصد","هشتصد","نهصد"]

def _below(n):
    p = []
    if n // 100: p.append(HUND[n // 100])
    r = n % 100
    if r >= 20:
        p.append(TENS[r // 10])
        if r % 10: p.append(ONES[r % 10])
    elif r >= 10: p.append(TEENS[r - 10])
    elif r: p.append(ONES[r])
    return " و ".join(p)

def n2w(n):
    if n == 0: return ONES[0]
    p = []
    for s, name in ((10**9, "میلیارد"), (10**6, "میلیون"), (1000, "هزار")):
        q, n = divmod(n, s)
        if q:
            p.append(name if (s == 1000 and q == 1) else _below(q) + " " + name)
    if n: p.append(_below(n))
    return " و ".join(p)

def to_ascii_digits(t):
    return t.translate(str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789"))

def numbers(t):
    t = to_ascii_digits(t)
    t = re.sub(r"(?<=\d)[,٬](?=\d{3})", "", t)
    dec = lambda m: n2w(int(m.group(1))) + " ممیز " + " ".join(ONES[int(c)] for c in m.group(2))
    t = re.sub(r"(\d+)[.٫](\d+)", dec, t)
    t = re.sub(r"(\d+)\s*[%٪]", lambda m: n2w(int(m.group(1))) + " درصد", t)
    return re.sub(r"\d+", lambda m: n2w(int(m.group(0))), t)

def respell(t, d):
    for k in sorted(d, key=len, reverse=True):
        t = re.sub(r"(?<![\w%s])%s(?![\w%s])" % (Z, re.escape(k), Z), d[k], t, flags=re.I)
    return t

def prepare(segs):
    d = {k: v for k, v in json.load(open(os.path.join(HERE, "pronunciations.json"), encoding="utf-8")).items() if not k.startswith("_")}
    tones = json.load(open(os.path.join(HERE, "tones.json"), encoding="utf-8"))
    out = []
    for s in segs:
        raw = s["text"]
        flags = ["علامت [؟] نزدیک: «%s»" % m.group(1) for m in re.finditer(r"(\S+)\s*\[؟\]", raw)]
        t = respell(numbers(raw.replace("[؟]", "")), d)
        flags += ["کلمه‌ی لاتین بدون تلفظ: «%s»" % w for w in sorted(set(re.findall(r"[A-Za-z][A-Za-z\-]+", t)))]
        prompt = tones["_base"] + " " + tones[s.get("tone", "calm")]
        out.append({"raw_text": raw.replace("[؟]", "").strip(), "tone": s.get("tone", "calm"), "tts_text": re.sub(r"[ \t]+", " ", t).strip(), "prompt_separate": prompt,
                    "prompt_inline": prompt + "\n\n" + t.strip(), "flags": flags})
    return out

if __name__ == "__main__":
    segs = json.load(open(sys.argv[1], encoding="utf-8"))
    print(json.dumps(prepare(segs), ensure_ascii=False, indent=2))
