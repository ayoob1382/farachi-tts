#!/usr/bin/env python3
"""ترکیب صدا + موزیک + تصویر. موزیک وقتی گوینده حرف می‌زنه کم می‌شه (ducking).
usage: mix.py timings.json voice.wav music_file silent.mp4 out.mp4"""
import json, subprocess, sys
tim, voice, music, video, out = sys.argv[1:6]
D = json.load(open(tim))['duration']
fc = (
 f"[1:a]aloop=loop=-1:size=2000000000,atrim=0:{D},asetpts=N/SR/TB,volume=0.35,"
 f"afade=t=in:st=0:d=2,afade=t=out:st={D-3}:d=3[m];"
 f"[0:a]aformat=sample_rates=44100:channel_layouts=stereo,asplit=2[v1][v2];"
 f"[m]aformat=sample_rates=44100:channel_layouts=stereo[ms];"
 f"[ms][v2]sidechaincompress=threshold=0.02:ratio=8:attack=60:release=700[md];"
 f"[v1][md]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11[a]"
)
subprocess.run(['ffmpeg','-y','-loglevel','error','-i',voice,'-i',music,'-i',video,
  '-filter_complex',fc,'-map','2:v','-map','[a]','-c:v','copy','-c:a','aac','-b:a','192k','-t',str(D),out],check=True)
print('mixed ->',out)
