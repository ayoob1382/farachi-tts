#!/usr/bin/env python3
"""ترکیب صدا + موزیک + تصویر.
- صدای گوینده کمی فشرده می‌شه تا ته جمله‌ها نخوابه
- بلندی موزیک اندازه‌گیری می‌شه و به یه سطح ثابت و آروم می‌رسه (مستقل از آهنگی که انتخاب کردی)
- موزیک وقتی گوینده حرف می‌زنه بازم کم می‌شه (ducking)
- محو شدن موزیک بعد از تموم شدن آخرین جمله شروع می‌شه
usage: mix.py timings.json voice.wav music_file silent.mp4 out.mp4"""
import json, re, subprocess, sys
tim, voice, music, video, out = sys.argv[1:6]
T = json.load(open(tim))
D = T['duration']
last_end = T['sentences'][-1]['end']

MUSIC_TARGET_LUFS = -33.0   # بلندی موزیک قبل از ducking. گوینده حدود -21 است.


def lufs(path):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', path, '-af', 'ebur128', '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    m = re.findall(r'I:\s+(-?[\d.]+)\s+LUFS', r)
    return float(m[-1]) if m else None


ml = lufs(music)
gain_db = (MUSIC_TARGET_LUFS - ml) if ml is not None else -14.0
gain_db = max(-40.0, min(10.0, gain_db))
print(f"موزیک: {ml} LUFS -> تنظیم {gain_db:+.1f} dB (هدف {MUSIC_TARGET_LUFS})")

fo_start = last_end + 0.2
if D - fo_start < 1.2:
    fo_start = max(0.0, D - 1.2)
fo_dur = D - fo_start

fc = (
 f"[1:a]aloop=loop=-1:size=2000000000,atrim=0:{D},asetpts=N/SR/TB,volume={gain_db}dB,"
 f"afade=t=in:st=0:d=2,afade=t=out:st={fo_start:.3f}:d={fo_dur:.3f}[m];"
 f"[0:a]acompressor=threshold=0.03:ratio=3:attack=10:release=250:makeup=3,"
 f"aformat=sample_rates=44100:channel_layouts=stereo,asplit=2[v1][v2];"
 f"[m]aformat=sample_rates=44100:channel_layouts=stereo[ms];"
 f"[ms][v2]sidechaincompress=threshold=0.02:ratio=6:attack=60:release=700[md];"
 f"[v1][md]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11[a]"
)
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', voice, '-i', music, '-i', video,
  '-filter_complex', fc, '-map', '2:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
  '-t', str(D), out], check=True)
print('mixed ->', out)
