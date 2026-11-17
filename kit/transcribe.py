#!/usr/bin/env python3
"""Transcribe a clip with Groq Whisper, keeping word-level timestamps.

    python kit/transcribe.py <video> [--out file.json] [--language en]

Writes <video dir>/<stem>.transcript.json (Groq's verbose_json: segments + words, times in seconds from the
start of the video). Needs GROQ_API_KEY (free at console.groq.com). Long videos are sent in 10-minute chunks.
Without a key it uses faster-whisper locally when installed (kit/setup.sh --local-asr; LOCAL_WHISPER_MODEL=small).
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

MODEL = 'whisper-large-v3'
CHUNK = 600
# a messy priming prompt keeps Whisper verbatim (repeats and fillers stay, so the word times stay honest)
PROMPT = 'Um, so, uh, the the thing is, wait, okay. So, like, verbatim.'


def duration(video):
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                                          '-of', 'default=nw=1:nk=1', str(video)]))


def audio(video, dst, start, dur):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(start), '-i', str(video), '-t', str(dur),
                    '-vn', '-ac', '1', '-ar', '16000', '-c:a', 'flac', str(dst)], check=True)


def call(client, path, language):
    kw = dict(file=(path.name, path.read_bytes()), model=MODEL, response_format='verbose_json',
              timestamp_granularities=['word', 'segment'], temperature=0.0, prompt=PROMPT)
    if language:
        kw['language'] = language
    r = client.audio.transcriptions.create(**kw)
    return r.model_dump() if hasattr(r, 'model_dump') else dict(r)


def transcribe_local(video, out, language=None):
    """no Groq key: faster-whisper on this machine (install once with kit/setup.sh --local-asr)"""
    from faster_whisper import WhisperModel
    model = WhisperModel(os.environ.get('LOCAL_WHISPER_MODEL', 'small'), device='auto', compute_type='int8')
    import numpy as np
    total = duration(video)
    # decode with ffmpeg ourselves (16 kHz mono float), so no PyAV version can break it
    pcm = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(video), '-vn', '-ac', '1', '-ar', '16000', '-f', 'f32le', '-'],
                         check=True, capture_output=True).stdout
    segs, _ = model.transcribe(np.frombuffer(pcm, np.float32).copy(), language=language, word_timestamps=True,
                               initial_prompt=PROMPT, vad_filter=False, temperature=0.0)
    words, segments, text = [], [], []
    for sg in segs:
        segments.append(dict(start=round(sg.start, 3), end=round(sg.end, 3), text=sg.text))
        text.append(sg.text.strip())
        for w in sg.words or []:
            words.append(dict(word=w.word.strip(), start=round(w.start, 3), end=round(w.end, 3)))
    data = dict(text=' '.join(text), segments=segments, words=words, duration=total, model='faster-whisper')
    Path(out).write_text(json.dumps(data, indent=1, ensure_ascii=False))
    return Path(out)


def transcribe(video, out=None, language=None):
    if not os.environ.get('GROQ_API_KEY'):
        try:
            import faster_whisper  # noqa: F401
        except ImportError:
            sys.exit('GROQ_API_KEY is not set. Get a free key at https://console.groq.com/keys and export it,\n'
                     'or run kit/setup.sh --local-asr once to transcribe on this machine instead.')
        video = Path(video).resolve()
        return transcribe_local(video, Path(out) if out else video.with_name(video.stem + '.transcript.json'), language)
    from groq import Groq
    video = Path(video).resolve()
    out = Path(out) if out else video.with_name(video.stem + '.transcript.json')
    client = Groq()
    total = duration(video)
    words, segments, text = [], [], []
    with tempfile.TemporaryDirectory() as tmp:
        t = 0.0
        while t < total - 0.05:
            dur = min(CHUNK, total - t)
            a = Path(tmp) / f'chunk{int(t)}.flac'
            audio(video, a, t, dur)
            r = call(client, a, language)
            for w in r.get('words') or []:
                words.append(dict(word=w['word'], start=round(w['start'] + t, 3), end=round(w['end'] + t, 3)))
            for s in r.get('segments') or []:
                segments.append(dict(start=round(s['start'] + t, 3), end=round(s['end'] + t, 3), text=s['text']))
            text.append(r.get('text', ''))
            t += dur
    data = dict(text=' '.join(x.strip() for x in text), segments=segments, words=words, duration=total, model=MODEL)
    out.write_text(json.dumps(data, indent=1, ensure_ascii=False))
    return out


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('video')
    ap.add_argument('--out')
    ap.add_argument('--language')
    a = ap.parse_args()
    p = transcribe(a.video, a.out, a.language)
    d = json.loads(p.read_text())
    print(f'wrote {p}  ({len(d["words"])} words)')
    for s in d['segments']:
        print(f'{s["start"]:7.2f}-{s["end"]:7.2f}  {s["text"].strip()}')
