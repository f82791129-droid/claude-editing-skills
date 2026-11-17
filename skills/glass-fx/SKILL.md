---
name: glass-fx
description: Edits a talking-head clip into a premium "glass" reel — a violet (or teal, ember, mono) cinematic grade with floating glossy spheres, word-by-word captions whose key words switch to a serif italic, and up to twelve word-anchored effects - halo search (glowing pill, orbit rings, oversized cursor click), ribbon wrap, falling cards, social orbit, quote note, icon pop, typing search, film strip, chrome title, glass card, checklist and a full-screen takeover. Also renders the promo wrapper (fluted-glass background, chrome headline, a fan of reel cards or a before/after with a terminal prompt). Use when the user runs /glass-fx, sends reels like these and wants "edits like this", asks for glassmorphism / Apple-style / motion-graphics effects on a 9:16 or 16:9 talking head, or wants a "12 effects" / "one skill edits them all" showcase video.
---

# /glass-fx

```
┌──────────────────────┐
│ ╭ quote note ──────╮ │  glass UI lands on the word that names it
│ ╰──────────────────╯ │
│  CHROME (behind head)│  optional cutout: effects pass behind the speaker
│   ◯  (face)  ◯       │  icons orbit, a ribbon wraps
│  ~~~~ribbon~~~~~     │
│  genuinely *right*   │  captions: lowercase, key word in serif italic, blur-in per word
│   (eye) ──── (✓)     │  icon pop
└──────────────────────┘
   takeover: the speaker irises out to a glass world (rings, spheres, a search pill + cursor click)
```

## First use
This skill's folder is the "Base directory" Claude Code shows when it loads it.
```bash
SKILL_DIR="<base directory of this skill>"
KIT=$(python3 -c 'import os,sys;print(os.path.realpath(os.path.join(sys.argv[1],"..","..","kit")))' "$SKILL_DIR")
PY="$KIT/.venv/bin/python"; [ -x "$PY" ] || bash "$KIT/setup.sh"      # add --cutout once if you will use "cutout": true
```
Transcripts: `GROQ_API_KEY` (free, fastest). Without it the kit falls back to a local Whisper (`bash "$KIT/setup.sh" --local-asr` installs it once). Needs ffmpeg and Node.

## Steps
1. **Clip.** The user's talking head (9:16 is ideal; 16:9 is cropped to the center — say so).
2. **Words.** `"$PY" "$KIT/reel.py" words <video>`. Pick 6 to 20 seconds of whole sentences. `start` = first word, `end` = the last sentence's `[ends …]`.
3. **Eye line.** `"$PY" "$KIT/reel.py" frame <video> <t> frame.jpg`, read the eye y on the ruler → `eye_y`.
4. **Plan the beats.** Read the sentence and give each idea ONE effect, landing on the word that names it (table below). 1 effect every 1.5–3 s. Never two big effects at once. Use one `takeover` at the emotional turn ("in five years", "the easiest way").
5. **Spec.** Write `<clip>.glass-fx.json` (below). Times are seconds from `start` or a spoken word (`"right"`, `"right#2"`, `"right+0.2"`).
6. **Build.** `"$PY" "$SKILL_DIR/build.py" <spec.json>` → `<clip>.glass-fx.mp4` and `.sheet.jpg`. Glass blur is heavy: a 15 s reel takes a few minutes (up to ~9 on a small CPU-only machine). To check one effect fast, copy the spec with a narrow `start`/`end`, only that effect, and `REEL_QUALITY=draft`.
7. **Check the sheet** (red = covered by Instagram). Fix and rebuild if: a card sits in the red, captions cover the mouth (`captions.top`), two effects overlap, text is cut off, the chrome word is too wide.
8. **Hand over** the mp4 and one line per effect: what lands on which word.
9. **Promo (optional).** For a "12 effects" / "one skill edits them all" video, run `showcase.py` (below) on the finished reels.

## Spec
```json
{
  "video": "talk.mp4", "start": 3.2, "end": 14.8,
  "theme": "violet",
  "eye_y": 760,
  "cutout": false,
  "zoom": [{"at": "customers", "scale": 1.16, "for": 1.2}],
  "captions": {"top": 1240, "keys": ["right", "easiest", "account"]},
  "effects": [
    {"type": "glass_card", "at": "genuinely", "title": "Genuinely *right*", "sub": "the honest take", "bar": "genuinely"},
    {"type": "icon_pop", "items": [{"icon": "eye", "label": "genuinely", "at": "genuinely"}, {"icon": "check", "label": "right", "at": "right"}]},
    {"type": "chrome_title", "at": "customers", "text": "customers", "sub": "don't want", "sub_at": "want"},
    {"type": "takeover", "at": "in five", "until": "check", "kicker": "it's also"},
    {"type": "halo_search", "at": "in five", "text": "in five years", "click_at": "years"},
    {"type": "checklist", "at": "plan", "items": [{"text": "Plan *it*", "at": "plan"}, {"text": "Film *it*", "at": "film"}, {"text": "Post *it*", "at": "post"}]}
  ]
}
```

### The twelve effects — and the word they belong on
| type | what it is | land it on | fields |
|---|---|---|---|
| `halo_search` | glowing white search pill, orbit rings burst, oversized cursor flies in and clicks | a question, a "what if", a time frame | `text`, `click_at`, `y` |
| `takeover` | a glass world (rings, spheres) irises in; with a cutout the speaker stays standing in it, without one it covers the frame; voice carries on | the turn of the story | `until`, `kicker`, `text` (hides captions while shown), `text_y`, `keep_speaker` (default true with a cutout). Put a `halo_search` inside it with `"y": 330` when the speaker stays |
| `ribbon_wrap` | glossy ribbon draws across the body (behind it in the middle with a cutout); a serif word can ride it | flow, journey, "through", "around" | `text`, `y` |
| `falling_cards` | 2–5 glass cards drop in and land fanned | a list of things, "options", proof | `cards: [{text, sub, icon} \| {image, label}]`, each may have `at`; `y` |
| `social_orbit` | icon bubbles orbit the head on a tilted ring | social, audience, "everyone" | `icons` (names or image paths), `turns`, `rx`, `ry`, `y` |
| `quote_note` | frosted note, small label, serif quote writes itself in | a quote, a belief, a rule | `label`, `text`, `by`, `y` |
| `icon_pop` | round glass chips pop, joined by a drawn line; the last is lit | two or three key words | `items: [{icon, label, at}]`, `y` |
| `typing_search` | glass search bar types the query; results slide in | "I googled", "search", a question | `text`, `results: [{icon, text}]`, `type_for`, `y` |
| `film_strip` | tilted film strip of frames slides across | content, videos, "every reel" | `images` (list or glob) or `texts`, `y` |
| `chrome_title` | one huge chrome condensed word (behind the head with a cutout), letters rise in | THE word of the clip | `text`, `sub`, `sub_at`, `size`, `y` |
| `glass_card` | frosted panel: title (serif accent), sub line, tiny input bar | a claim, a definition | `title`, `sub`, `bar`, `bar_icon`, `side: left\|right\|center`, `y` |
| `checklist` | numbered glass rows that tick off as said | steps, "three things" | `items: [{text, at, done_at}]`, `y` |

### Premium beats
| type | what it is | fields |
|---|---|---|
| `hook` | the first second: a two-line title rises out of a mask while the camera settles from a push, with a light leak | `text` (`\n` between lines, `*word*` serif), `kicker`, `zoom_from`, `y` |
| `depth_focus` | the room blurs and darkens, the speaker stays sharp (needs `cutout`); an optional glowing serif word behind them | `text`, `blur`, `size`, `y` |
| `stat` | a number counts up in a glass card | `value` (`"10,000"`, `"4:12"`), `label`, `sub`, `prefix`, `suffix`, `count_for` |
| `name_tag` | glass pill: avatar, name, verified tick, handle (defaults from `brand`) | `name`, `handle`, `avatar`, `y` |
| `cta` | the ask at the end: a glowing pill that breathes twice | `text` (`"Comment *EDIT*"`), `sub`, `icon`, `y` |
| `light_leak` | a soft light sweep | `for`, `side` |

### Pacing, brand and sound
- `trim_pauses: 0.4` cuts every silence longer than 0.4 s (or give `segments: [[a, b], …]` in source seconds); the framing alternates on each cut (`cut_zoom`, 1.1). Words and effects follow the new timing.
- `brand: {"accent": "#4f7cff", "name": "…", "handle": "@…", "avatar": "me.jpg"}` derives every tone from your colour.
- `sfx`: `"soft"` (default) — synthesized, quiet sounds on the main beats only, at most one per 0.8 s; `"medium"`, `"off"`, or `{"level": "soft", "gap": 1.2}`. Any effect can take `"sfx": false`. `music: {"src": "bed.mp3", "volume": 0.1}` adds the user's own track. Audition the sounds with `"$PY" "$SKILL_DIR/sfx.py" preview out.wav`.
- `grain: 0.07` film grain (0 to turn off). `lang: "az"` for Azerbaijani capitals (i → İ).
- For the creator / After-Effects style (natural colour, words behind the head, paper B-roll …) use `/viral-edit`, which runs on this engine.

Every effect takes `at` and either `until` or `hold` (seconds, default ≈ 2.8). Icons: `check eye heart star bolt user users search plus chart clock calendar arrow play message money lock fire sparkle instagram youtube tiktok x linkedin mail`. In any text, `*word*` turns that word serif italic.

### Look
- `theme`: `violet` (default, the purple glass look), `teal` (blue-cyan), `ember` (rose), `mono` (silver).
- `cutout: true` cuts the speaker out (RobustVideoMatting, ~0.1 s per frame) so `chrome_title`, `ribbon_wrap` and `social_orbit` pass BEHIND the person. It is the single biggest jump in quality; use it whenever the user can wait the extra minute. Or pass a ready alpha webm path.
- `zoom`: a number for the slow push-in (1.06), or a list of punch-ins `{at, scale, for}` — max one per sentence.
- `captions`: `top` (1240; keep under the chin and above 1420), `size` (66), `keys` (2–4 words to set in serif), `maxw` (3). `false` turns them off. `spheres: false` removes the floating spheres.

## Showcase (the promo video)
`"$PY" "$SKILL_DIR/showcase.py" showcase.json` makes the wrapper seen in "12 video effects our Claude skill makes" posts:
```json
{
  "layout": "fan",
  "theme": "violet",
  "duration": 8,
  "kicker": "12 video", "title": "effects", "subtitle": "our Claude skill makes",
  "center": "talk.glass-fx.mp4",
  "cards": [{"video": "a.mp4", "label": "Ribbon wrap"}, {"video": "b.mp4", "label": "Falling cards"},
            {"video": "c.mp4", "label": "Halo search"}, {"video": "d.mp4", "label": "Social orbit"}],
  "out": "promo.mp4"
}
```
- `layout: "fan"` — center phone with the main reel, four tilted cards around it with label pills, pills row under it. `cards` may hold `image` instead of `video`; a card with `at` swaps in at that second (the cards cycle).
- `layout: "before_after"` — `before` (raw clip) small at top-left, `after` (edited reel, 16:9 or 9:16) big under it, a terminal card "Render reel.mp4? › 1. Yes" at the bottom, a comment bubble on top (`comment`, `handle`). Title lines: `kicker` ("I stopped paying for every reel. One Claude skill") + chrome `title` ("edits them all").
- Background: animated fluted glass in the theme colour. Audio comes from `center` / `after` unless `music` is given.

## Taste
- An effect appears on the word, never before it. The reel must read with the sound off.
- One hero per beat. A `takeover` or `chrome_title` owns the screen; nothing else lands with it except captions or the `halo_search` inside a takeover.
- Glass sits over darker areas of the frame. If the background is bright, use `mono` or move the card.
- Words in cards are the speaker's words or the user's own facts. Never invent numbers, names, quotes or results.
- Keep text out of the top 220 px, the bottom 420 px and 100 px each side (the sheet shows it in red).
