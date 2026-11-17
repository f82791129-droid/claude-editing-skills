#!/usr/bin/env python3
"""glass-fx showcase: the promo wrapper around finished reels, on an animated fluted-glass background.

    <kit>/.venv/bin/python showcase.py showcase.json

layout "fan":          kicker / chrome title / serif subtitle, a center phone playing the main reel,
                       four tilted cards with label pills around it (more cards cycle in), a pill row under it.
layout "before_after": comment bubble, two-line kicker, chrome title, the raw clip small (BEFORE),
                       the edit big (AFTER), and a terminal card "Render reel.mp4?".
See SKILL.md for the fields.
"""
import html
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'kit'))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import reel  # noqa: E402
from reel import Comp, duration, sheet  # noqa: E402
from build import THEMES, icon, serif  # noqa: E402


def esc(s):
    return html.escape(str(s))


def aspect(p):
    import subprocess
    w, h = subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height',
                                    '-of', 'csv=p=0', str(p)]).decode().strip().split(',')[:2]
    return int(w) / int(h)


class Lite:
    """the bits of reel.Job that Comp needs, without a transcript"""

    def __init__(self, spec_path):
        self.spec_file = Path(spec_path).resolve()
        self.s = json.loads(self.spec_file.read_text())
        self.base = self.spec_file.parent
        self.out = self.path(self.s.get('out', 'showcase.mp4'))
        self.work = self.out.parent / '.work' / self.out.stem
        self.work.mkdir(parents=True, exist_ok=True)

    def get(self, k, d=None):
        return self.s.get(k, d)

    def path(self, v):
        p = Path(str(v)).expanduser()
        p = p if p.is_absolute() else (self.base / p).resolve()
        return p


class Show:
    def __init__(self, spec):
        self.j = j = Lite(spec)
        self.layout = j.get('layout', 'fan')
        main = j.get('center') if self.layout == 'fan' else j.get('after')
        if not main:
            sys.exit('fan needs "center"; before_after needs "after"')
        self.main = j.path(main)
        if not self.main.exists():
            sys.exit(f'not found: {self.main}')
        j.clip = j.path(j.get('music')) if j.get('music') else self.main
        dur = float(j.get('duration') or min(12.0, duration(self.main)))
        reel.FPS = reel.pick_fps(self.main)
        j.dur = math.floor(dur * reel.FPS - 1) / reel.FPS
        self.c = Comp(j, 'showcase')
        self.T = THEMES[j.get('theme', 'violet')]

    def js(self, s):
        self.c.js.append(s)

    def media(self, path, box_style, vid, fit='cover', loop=True):
        """a video (looped by chaining copies) or an image, filling a box"""
        p = self.j.path(path)
        if not p.exists():
            sys.exit(f'not found: {p}')
        inner = f'width:100%;height:100%;object-fit:{fit};position:absolute;left:0;top:0'
        if p.suffix.lower() in ('.jpg', '.jpeg', '.png', '.webp'):
            return f'<div style="{box_style}"><img src="{self.c.asset(p)}" style="{inner}"></div>'
        ln = duration(p)
        parts, t, k = [], 0.0, 0
        while t < self.c.dur and (loop or k == 0):
            d = min(ln - 0.05, self.c.dur - t)
            parts.append(self.c.video(p, inner, f'{vid}_{k}', start=t, dur=d))
            t += d
            k += 1
        return f'<div style="{box_style}">{"".join(parts)}</div>'

    # ------------------------------------------------------------ background
    def background(self):
        T, d = self.T, self.c.dur
        self.c.css.append(f'''
#root{{background:{T['deep']};perspective:1600px}}
.chrome{{font-family:'Anton',sans-serif;text-transform:uppercase;line-height:.88;color:transparent;letter-spacing:.005em;
  background:linear-gradient(180deg,#fff 0%,#ececf3 32%,#8e8e9e 50%,#50505e 53%,#dadae4 68%,#fff 84%,#a2a2b0 100%);
  -webkit-background-clip:text;background-clip:text;filter:drop-shadow(0 12px 30px rgba(0,0,0,.6))}}
.sf{{font-family:'Instrument Serif',serif;font-style:italic;font-weight:400}}
.lp{{display:inline-flex;align-items:center;gap:10px;padding:10px 20px;border-radius:99px;background:#fff;color:#111;
  font:600 26px Inter;letter-spacing:-.01em;box-shadow:0 10px 26px rgba(0,0,0,.35)}}
.lp i{{width:12px;height:12px;border-radius:50%;background:{T['accent']}}}
.card{{position:absolute;overflow:hidden;border-radius:34px;border:4px solid rgba(255,255,255,.9);
  box-shadow:0 40px 90px rgba(0,0,0,.6),0 0 0 1px rgba(0,0,0,.3);background:#111}}
@font-face{{font-family:'Anton';src:url(fonts/anton-400-normal.woff2) format('woff2')}}''')
        b = self.c.body
        b.append(f'<div class="a" id="glowA" style="left:-300px;top:200px;width:1100px;height:1500px;border-radius:50%;'
                 f'background:radial-gradient(closest-side,{T["accent"]},transparent);opacity:.75;filter:blur(40px)"></div>')
        b.append(f'<div class="a" id="glowB" style="left:400px;top:700px;width:1000px;height:1400px;border-radius:50%;'
                 f'background:radial-gradient(closest-side,{T["mid"]},transparent);opacity:.9;filter:blur(40px)"></div>')
        b.append(f'<div class="a" id="glowC" style="left:300px;top:-300px;width:600px;height:900px;border-radius:50%;'
                 f'background:radial-gradient(closest-side,{T["accent2"]}88,transparent);filter:blur(50px)"></div>')
        # the flutes: vertical glass ridges (light edge, dark trough), slightly uneven
        b.append('<div class="a" style="inset:0;background:repeating-linear-gradient(90deg,rgba(255,255,255,.16) 0,rgba(255,255,255,.04) 6px,'
                 'rgba(0,0,0,.05) 20px,rgba(0,0,0,.42) 34px,rgba(255,255,255,.2) 36px),repeating-linear-gradient(90deg,transparent 0,'
                 'rgba(0,0,0,.18) 90px,transparent 180px)"></div>')
        b.append(f'<div class="a" style="inset:0;background:linear-gradient(180deg,{T["deep"]}00 0%,{T["deep"]}00 55%,{T["deep"]}cc 100%),'
                 'radial-gradient(130% 80% at 50% 40%,transparent 50%,rgba(0,0,0,.6) 100%)"></div>')
        self.js(f'tl.fromTo("#glowA",{{x:0,y:0}},{{x:260,y:-120,duration:{d:.3f},ease:"sine.inOut"}},0);'
                f'tl.fromTo("#glowB",{{x:0,y:0}},{{x:-280,y:80,duration:{d:.3f},ease:"sine.inOut"}},0);'
                f'tl.fromTo("#glowC",{{x:0}},{{x:220,duration:{d:.3f},ease:"sine.inOut"}},0);')

    def rise(self, sel, at, frm='y:40,scale:.9', dur=.6, ease='power3.out'):
        self.js(f'tl.fromTo({json.dumps(sel)},{{autoAlpha:0,filter:"blur(14px)",{frm}}},{{autoAlpha:1,filter:"blur(0px)",x:0,y:0,scale:1,'
                f'rotation:0,duration:{dur},ease:"{ease}"}},{at:.3f});')

    def chrome_line(self, text, top, size, cid):
        self.c.body.append(f'<div class="a" id="{cid}" style="left:0;width:1080px;top:{top}px;text-align:center">'
                           f'<span class="chrome" style="font-size:{size}px">{esc(text)}</span></div>')

    # ------------------------------------------------------------ fan
    def fan(self):
        j, b, T = self.j, self.c.body, self.T
        b.append(f'<div class="a" id="kick" style="left:0;width:1080px;top:236px;text-align:center;font:700 40px Inter;color:#fff;'
                 f'letter-spacing:-.02em">{esc(j.get("kicker", "12 video"))}</div>')
        title = str(j.get('title', 'effects'))
        self.chrome_line(title, 278, int(min(200, 860 / max(1, len(title) * .5))), 'ttl')
        b.append(f'<div class="a" id="sub" style="left:0;width:1080px;top:470px;text-align:center;font-size:56px;color:#fff" class="sf">'
                 f'<span class="sf">{esc(j.get("subtitle", "our Claude skill makes"))}</span></div>')
        b.append(f'<div class="a" id="badge" style="left:512px;top:552px;width:56px;height:56px;border-radius:14px;background:#fff;'
                 f'display:flex;align-items:center;justify-content:center;color:{T["accent"]};box-shadow:0 8px 20px rgba(0,0,0,.35)">'
                 f'{icon(j.get("badge", "sparkle"), 34, 2.2)}</div>')
        cards = j.get('cards') or []
        slots = [(70, 700, -7), (760, 690, 7), (60, 1110, 6), (770, 1100, -6)]
        groups = [cards[k:k + 4] for k in range(0, len(cards), 4)] or [[]]
        swap = self.c.dur / len(groups)
        labels = []
        for g, grp in enumerate(groups):
            for q, k in enumerate(grp):
                x, y, r = slots[q]
                cid = f'cd{g}_{q}'
                lab = (f'<div style="position:absolute;left:14px;bottom:14px;z-index:3"><span class="lp" style="font-size:22px;padding:8px 16px">'
                       f'<i></i>{esc(k["label"])}</span></div>') if k.get('label') else ''
                src = k.get('video') or k.get('image')
                b.append(f'<div class="card" id="{cid}" style="left:{x}px;top:{y}px;width:250px;height:380px;transform:rotate({r}deg)">'
                         f'{self.media(src, "position:absolute;inset:0", cid + "v")}{lab}</div>')
                t0 = 0.35 + q * .08 if g == 0 else g * swap
                frm = f'x:{(540 - x - 125) * .8:.0f},y:{(1000 - y - 190) * .6:.0f},scale:.6,rotation:{-r}'
                self.rise(f'#{cid}', t0, frm, .7, 'back.out(1.3)')
                self.js(f'tl.to("#{cid}",{{y:-18,duration:{swap - .6:.3f},ease:"sine.inOut"}},{t0 + .6:.3f});')
                if g + 1 < len(groups):
                    self.js(f'tl.to("#{cid}",{{autoAlpha:0,rotationY:90,duration:.3,ease:"power2.in"}},{(g + 1) * swap - .3:.3f});')
                if k.get('label') and g == 0:
                    labels.append(k['label'])
        b.append(f'<div class="card" id="phone" style="left:310px;top:640px;width:460px;height:818px;border-radius:44px;border:6px solid #fff;z-index:5">'
                 f'{self.media(self.main, "position:absolute;inset:0", "main")}</div>')
        self.rise('#phone', .1, 'y:220,scale:.8,rotationX:25', .8, 'power4.out')
        self.js(f'tl.fromTo("#phone",{{rotationY:-4}},{{rotationY:4,duration:{self.c.dur:.3f},ease:"sine.inOut"}},0);')
        pills = ''.join(f'<span class="lp lpp" style="margin:0 6px;font-size:24px"><i></i>{esc(t)}</span>' for t in (j.get('pills') or labels)[:4])
        b.append(f'<div class="a" id="pills" style="left:0;width:1080px;top:1500px;text-align:center;white-space:nowrap">{pills}</div>')
        self.rise('#kick', .05)
        self.rise('#ttl', .12, 'y:60,scale:1.15')
        self.rise('#sub', .3)
        self.rise('#badge', .42, 'scale:0,rotation:-40', .5, 'back.out(2.4)')
        self.js('tl.fromTo(".lpp",{autoAlpha:0,y:30},{autoAlpha:1,y:0,duration:.4,stagger:.07,ease:"back.out(2)"},.9);')

    # ------------------------------------------------------------ before / after
    def before_after(self):
        j, b, T = self.j, self.c.body, self.T
        if j.get('comment'):
            b.append(f'<div class="a" id="cmt" style="left:0;width:1080px;top:232px;text-align:center"><span style="display:inline-flex;align-items:center;'
                     f'gap:16px;padding:12px 28px 12px 14px;border-radius:99px;background:#fff;box-shadow:0 14px 34px rgba(0,0,0,.4)">'
                     f'<i style="width:54px;height:54px;border-radius:50%;background:linear-gradient(160deg,#d4d4d8,#71717a)"></i>'
                     f'<span style="text-align:left"><span style="display:block;font:500 20px Inter;color:#71717a">{esc(j.get("handle", "someone · 2m"))}</span>'
                     f'<span style="display:block;font:700 32px Inter;color:#111;letter-spacing:-.02em">{esc(j.get("comment"))}</span></span></span></div>')
        kick = (j.get('kicker') or 'I stopped paying for every reel.\nOne Claude skill').split('\n')
        b.append(f'<div class="a" id="kick" style="left:0;width:1080px;top:340px;text-align:center;font:600 44px/1.12 Inter;color:#fff;letter-spacing:-.02em">'
                 + '<br>'.join(esc(x) for x in kick) + '</div>')
        title = str(j.get('title', 'edits them all'))
        self.chrome_line(title, 450, int(min(210, 860 / max(1, len(title) * .5))), 'ttl')
        portrait = aspect(self.main) < 1
        bef_box = 'left:80px;top:700px;width:300px;height:533px' if portrait else 'left:70px;top:700px;width:470px;height:300px'
        aft_box = ('left:560px;top:690px;width:440px;height:782px;transform:rotateY(-10deg)' if portrait else
                   'left:60px;top:900px;width:960px;height:560px;transform:rotateY(-8deg) rotateX(4deg)')
        b.append(f'<div class="a" id="bef" style="{bef_box};transform:rotate(-3deg)">'
                 '<div class="card" style="inset:0;border-radius:24px;border-width:3px">'
                 + self.media(j.get('before'), 'position:absolute;inset:0', 'bef')
                 + '</div><div class="a" style="left:22px;top:18px;font:800 22px Inter;color:#fff;letter-spacing:.08em;text-shadow:0 2px 8px #000">BEFORE</div></div>')
        b.append(f'<div class="a" id="aft" style="{aft_box}">'
                 '<div class="card" style="inset:0;border-radius:28px;border-width:3px">'
                 + self.media(self.main, 'position:absolute;inset:0', 'aft')
                 + '</div><div class="a" style="left:26px;top:20px;font:800 22px Inter;color:#fff;letter-spacing:.08em;text-shadow:0 2px 8px #000">AFTER</div></div>')
        lines = j.get('terminal') or ['Render reel.mp4?', 'raw.mp4 → reel.mp4 · 10 s', '1. Yes', "2. Yes, and don't ask again", '3. No']
        mono = "'DejaVu Sans Mono','Menlo','Consolas',monospace"
        rows = (f'<div style="font:700 27px {mono};color:#fff">{esc(lines[0])}</div>'
                f'<div style="margin:6px 0 12px;font:400 20px {mono};color:#8b8b98">{esc(lines[1])}</div>'
                + ''.join(f'<div class="tl{n}" style="white-space:nowrap;font:400 {19 if portrait else 23}px/1.55 {mono};color:{T["accent2"] if n == 0 else "#d4d4d8"}">'
                          f'{"❯ " if n == 0 else "&nbsp;&nbsp;"}{esc(x)}</div>' for n, x in enumerate(lines[2:])))
        b.append(f'<div class="a" id="term" style="left:{50 if portrait else 250}px;top:{1262 if portrait else 1480}px;width:{470 if portrait else 580}px;border-radius:22px;background:#151518;'
                 f'border:1.5px solid rgba(255,255,255,.14);box-shadow:0 30px 70px rgba(0,0,0,.6);padding:18px 22px 22px">'
                 f'<div style="display:flex;gap:9px;margin-bottom:16px"><i style="width:13px;height:13px;border-radius:50%;background:#ff5f57"></i>'
                 f'<i style="width:13px;height:13px;border-radius:50%;background:#febc2e"></i><i style="width:13px;height:13px;border-radius:50%;background:#28c840"></i></div>'
                 f'<div style="border:1.5px solid {T["accent"]}99;border-radius:12px;padding:18px 20px">{rows}</div></div>')
        self.rise('#cmt', .05, 'y:-30,scale:.8', .5, 'back.out(2)')
        self.rise('#kick', .15)
        self.rise('#ttl', .25, 'y:60,scale:1.15')
        self.rise('#bef', .45, 'x:-80,rotation:-8')
        self.rise('#aft', .65, 'y:140,scale:.85', .8, 'power4.out')
        self.rise('#term', .95, 'y:80', .55, 'back.out(1.5)')
        self.js(f'tl.fromTo("#aft",{{rotationY:{-10 if portrait else -8}}},{{rotationY:-2,duration:{self.c.dur:.3f},ease:"sine.inOut"}},0);')

    def build(self):
        self.background()
        if self.layout == 'fan':
            self.fan()
        elif self.layout == 'before_after':
            self.before_after()
        else:
            sys.exit('layout must be fan or before_after')
        self.c.write()
        self.c.render(self.j.out)
        sh = self.j.out.with_name(self.j.out.stem + '.sheet.jpg')
        sheet(self.j.out, sh)
        print(f'\nDONE  {self.j.out}\ncheck {sh}')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    Show(sys.argv[1]).build()
