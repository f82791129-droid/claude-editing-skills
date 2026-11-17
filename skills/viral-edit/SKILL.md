---
name: viral-edit
description: Edits a talking-head clip into a viral creator-style reel - natural cinematic colour, dead air trimmed with alternating jump-cut zooms, a black-and-white-to-colour hook, huge words behind the speaker's head (bold, chrome, serif, echo or counting numbers) with a serif italic accent in front, glowing halo rings and light rays behind the head, full-screen paper or grid B-roll cards with taped photos, hand-drawn circles and red stamps, taped polaroids, colour label boxes, chat bubbles, star ratings, dot shapes that build a trophy or target, flash, pixel and whip transitions, captions with serif accent words, and soft, sparse sound design. Works in Azerbaijani, Turkish, Uzbek and English (ə ş ğ ı İ ç ö ü). Use when the user runs /viral-edit, sends creator reels and wants edits like these, or asks for a premium, viral, After-Effects-style edit of a 9:16 talking head.
---

# /viral-edit

```
┌──────────────────────┐
│     HEÇ  KİM          │  huge word BEHIND the head (cutout), serif accent word in front
│   ◜ halo ring ◝       │  light rays / ring behind the head
│      (face)  bilmir   │
│  [KİÇİK SAXLAYIR]     │  colour label box
│   montaj  *kiçik*     │  captions: key word in serif italic, accent colour
└──────────────────────┘
 B&W → colour hook · paper / grid B-roll cards · polaroids · pixel / flash / whip cuts · soft sound
```

Built on the glass-fx engine (`../glass-fx/build.py`), so every glass-fx effect (halo search, stat, checklist, name tag, CTA, depth focus …) works here too. The difference is the look: natural cinematic colour instead of the violet glass.

## First use
```bash
SKILL_DIR="<base directory of this skill>"
KIT=$(python3 -c 'import os,sys;print(os.path.realpath(os.path.join(sys.argv[1],"..","..","kit")))' "$SKILL_DIR")
PY="$KIT/.venv/bin/python"; [ -x "$PY" ] || bash "$KIT/setup.sh" --cutout
```
Transcripts: `GROQ_API_KEY`, or `bash "$KIT/setup.sh" --local-asr` once for local Whisper. For Azerbaijani set `"lang": "az"` (Uzbek `uz`, Turkish `tr`).

## Steps
1. **Clip.** The user's 9:16 talking head.
2. **Words.** `"$PY" "$KIT/reel.py" words <video>`. Choose 8 to 30 s of whole sentences (`start`, `end`).
3. **Eye line.** `"$PY" "$KIT/reel.py" frame <video> <t> frame.jpg` → `eye_y`.
4. **Write the edit like an editor**, beat by beat (see Recipe below). Each sentence gets ONE hero effect on its key word. Leave a breath between heroes.
5. **Spec** `<clip>.viral-edit.json`. Times are seconds or spoken words (`"kiçik"`, `"hook.#2"`, `"word+0.2"`).
6. **Build** `"$PY" "$SKILL_DIR/build.py" <spec.json>` (a 15 s reel takes a few minutes; `REEL_QUALITY=draft` for a fast check of a short `start`/`end`).
7. **Check** `<out>.sheet.jpg` and a few frames: nothing in the red zones, no letter clipped, nothing left on screen after its moment, captions clear of the mouth.
8. **Hand over** the mp4 and one line per beat.

## Recipe: what makes it feel viral
- **0.0–1.0 s, the hook:** `trim_pauses` on, `transition` `bw` on the 2nd word (raw B&W → colour), a `word_behind` with the hook word, `cut_zoom` alternates framing on every cut.
- **Every 2–3 s a new hero:** word_behind → label_box → halo/light rays → B-roll card → number → list. Never two heroes at once.
- **B-roll every 6–10 s:** a `paper_card` (or grid) breaks the talking head, enters on a `pixel`, `flash` or `whip`.
- **Numbers count** (`count_from`), **lists tick** (`label_box` items or `checklist`), **claims get a circle** (`scribble`).
- **End on the ask:** `cta` ("Şərhə *EDIT* yaz").
- **Sound:** soft and sparse by default (`sfx: "soft"`, one sound per ≥0.8 s, highest-priority beats only). `"sfx": "off"` for none, `{"level": "medium"}` for a little more. `music: {"src": "bed.mp3", "volume": 0.1}` adds the user's own music.

## Spec
```json
{
  "video": "clip.mp4", "start": 12.0, "end": 31.5,
  "lang": "az", "theme": "gold", "eye_y": 720, "cutout": true,
  "trim_pauses": 0.4, "cut_zoom": 1.1,
  "brand": {"accent": "#ffc533", "name": "Ad Soyad", "handle": "@hesab"},
  "captions": {"keys": ["kiçik", "sadədir"], "style": "editorial"},
  "effects": [
    {"type": "transition", "kind": "bw", "at": "kim"},
    {"type": "word_behind", "style": "bold", "at": "heç", "until": "montaj", "text": "heç kim", "front": "bilmir", "front_at": "demir"},
    {"type": "halo_ring", "at": "montaj", "rays": true},
    {"type": "label_box", "at": "kiçik", "items": [{"text": "kiçik saxlayır", "style": "red", "big": true, "at": "kiçik"}]},
    {"type": "word_behind", "at": "on", "text": "10K", "count_from": 0, "color": "accent", "sub": "baxış"},
    {"type": "paper_card", "at": "həll", "until": "hook", "title": "sadə", "sub": "…", "photo": "photo.jpg", "circle": true},
    {"type": "transition", "kind": "pixel", "at": "hook"},
    {"type": "cta", "at": "şərhə", "text": "Şərhə *EDIT* yaz"}
  ]
}
```

### Presets, several clips, studio voice
- **`"preset": "shahlar"`** loads `presets/shahlar.json` under the spec (the spec's own fields win; effects are never preset). **When the user says "Şahlar bəy üçün edit et" (edit for Şahlar bəy), use `"preset": "shahlar"`.** Make a new preset by saving a reel's look fields (lang, look, theme, brand, voice, cutout, trim_pauses, cut_zoom, grain, sfx, captions) as `presets/<name>.json`, and update one when the user changes their mind about a style. The `shahlar` preset is provisional until the user confirms it.
- **`"clips": [["part1.mp4", 0, 18.1], ["part2.mp4"]]`** joins several takes (with optional source in/out seconds) into one reel before transcription. Leave out `video`, `start`, `end` and `transcript` then. Use it whenever the user sends a story split across files: one reel that pays off at the end keeps people watching longer than two halves.
- **`"voice": "mic"`** gives the voice a studio-microphone finish: de-noise (no hiss), low cut, warmth, presence, de-esser, compression, −14 LUFS. Use it for phone or room recordings, and whenever the user asks for a serious, "spoken into a microphone" sound.
- **Sound palette:** `"sfx": {"palette": "clean"}` uses pure tones only (swipe, swell, chime, pop, soft sub) — zero noise, so no hiss. Use it whenever the user mentions hiss/xışıltı or wants it cleaner. `level`: `soft` (fewest), `medium`; `gap` is the minimum seconds between sounds.

### Clean picture (no freezing, no blocks)
- The reel renders at the footage's own frame rate (25 stays 25). Never force 30 on 25 fps footage: every 5th frame repeats and the picture seems to freeze. `fps` overrides only if the user asks.
- Source frames are pulled as PNG and encoded at CRF 14, so the render adds no block artifacts of its own.
- Phone and CapCut exports often already have blocks in smooth, out-of-focus backgrounds. `"deblock": true` cleans them lightly. With a cutout, `bg_soften` (3 px by default in `cinema`) softens only the background, which melts the blocks while the speaker stays sharp. Use 0 for none, 5–6 for a heavy case.
- Avoid `grain` on such footage: noise compresses into blocks on Instagram. Contrast in `cinema` is kept gentle for the same reason.
- When you hand over a file for upload, export it with `-c:v libx264 -preset slow -crf 16 -tune film -x264-params aq-mode=3 -movflags +faststart` (fewer blocks after Instagram recompresses it).

### Look
- `look`: `cinema` (default here) or `glass` (the violet glass-fx look).
- `theme`: `gold` (default), `lime`, `red`, `sky`, or the glass ones; `brand.accent` overrides with your own colour.
- `cutout: true`: the speaker is cut out so words, rings, rays, dots and photos go BEHIND them. It makes the biggest difference; always use it unless the user can't wait.
- `captions.style`: `editorial` (white bold, key words serif italic in the accent colour), `punch` (one big condensed word at a time), `glass`. `grain: 0.07` film grain (0 = off).

### Effects (beyond glass-fx's)
| type | what it is | fields |
|---|---|---|
| `word_behind` | huge word behind the head; letters rise from a mask | `text`, `style: bold\|chrome\|serif\|echo\|outline`, `color` (`"accent"` or #hex), `front` + `front_at` (serif italic word in front, accent colour), `sub` + `sub_at`, `count_from` (numbers count up: `"10K"`, `"$15"`, `"2026"`), `size`, `y` |
| `halo_ring` | glowing ring behind the head, optional light rays | `rays`, `ring`, `r`, `color`, `y` |
| `light_rays` | rays only, slowly turning | `color` |
| `paper_card` | full-screen B-roll card over the speaker (voice continues, captions pause) | `bg: paper\|grid\|dark`, `title`, `title_style: bold\|serif`, `title_color`, `sub`, `photo` + `photo_caption`, `circle` (red hand-drawn oval round the title), `stamp` (red box), `enter: slide\|flash` |
| `polaroids` | 1–3 taped photos drop in | `images`, `captions`, `behind` (behind the head), `y` |
| `scribble` | marker circle / underline / arrow drawn on the frame | `box: [x,y,w,h]`, `shape`, `label`, `color` |
| `label_box` | colour boxes that pop one by one | `items: [{text, at, style: accent\|yellow\|red\|teal\|white\|black, big}]`, `y` |
| `bubble` | chat bubble: typing dots, then the message | `text`, `from`, `side`, `color: blue\|green\|gray\|white`, `text_at` |
| `star_rating` | five stars fill in, score and label | `score`, `label`, `y` |
| `dot_shape` | glowing dots fly in and build a shape | `shape: target\|trophy\|heart\|star\|check\|arrow\|chart\|bolt`, `label`, `behind`, `size`, `y` |
| `transition` | a cut accent | `kind: flash\|pixel\|whip\|bw\|leak`, `at` |

Plus from glass-fx: `hook`, `depth_focus`, `stat`, `name_tag`, `cta`, `checklist`, `quote_note`, `typing_search`, `halo_search`, `takeover`, `ribbon_wrap`, `falling_cards`, `social_orbit`, `icon_pop`, `film_strip`, `chrome_title`, `glass_card`, `light_leak`.

## Taste
- Land everything on the word, never before it. The reel must read with the sound off.
- One hero per beat. Big word, label box, ring, B-roll: one at a time, with air between.
- Words on screen are the speaker's words or the user's facts. Never invent numbers, names, reviews or results.
- Keep text out of the top 220 px, bottom 420 px and 100 px each side.
- Soft sound only: no booms, no stacked whooshes. If in doubt, fewer.
