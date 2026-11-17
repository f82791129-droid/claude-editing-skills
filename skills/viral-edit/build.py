#!/usr/bin/env python3
"""viral-edit: a creator-style edit of a talking-head clip — natural cinematic colour, big words behind the head,
serif italic accents, paper and grid B-roll cards, taped polaroids, hand-drawn circles, colour label boxes,
chat bubbles, halo rings, light rays, dot shapes, cut transitions, punchy captions and soft sound design.

    <kit>/.venv/bin/python build.py spec.json

It runs on the glass-fx engine (../glass-fx), with look "cinema" by default. Every glass-fx effect works here too.
See SKILL.md for the spec.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'glass-fx'))
from build import main  # noqa: E402

if __name__ == '__main__':
    main(sys.argv, 'viral-edit', 'cinema', __doc__)
