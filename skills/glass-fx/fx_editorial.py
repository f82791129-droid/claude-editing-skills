"""Editorial effects: the look of the creator edits from the references — big words behind the head, serif italic
accents, paper and grid B-roll cards, taped polaroids, hand-drawn circles, colour label boxes, chat bubbles,
dot shapes, star ratings, halo rings and light rays, and cut transitions (flash, pixel, whip, B&W reveal).

A mixin for build.Reel: every fx_* here uses Reel's helpers (add, enter, leave, window, js, uid, T, cut, eye, j, c).
"""
import html
import json
import math
import random
import sys

DIGITS = set('0123456789')


def esc(s):
    return html.escape(str(s))


def upper(s, lang=None):
    """uppercase that knows Azerbaijani/Turkish dotted i (i -> İ, ı -> I)"""
    s = str(s)
    if lang in ('az', 'tr'):
        s = s.replace('i', 'İ').replace('ı', 'I')
    return s.upper()


def lower(s, lang=None):
    s = str(s)
    if len(s.strip('.,!?')) > 1 and s.strip('.,!?').isupper():
        return s                                 # an acronym or brand word (EDIT, AI, CTA) keeps its caps
    if lang in ('az', 'tr'):
        s = s.replace('I', 'ı').replace('İ', 'i')
    return s.lower()


def shape_mask(name, n=26):
    """an n x n grid of 0/1 for a simple icon, drawn with PIL"""
    from PIL import Image, ImageDraw
    S = 200
    im = Image.new('L', (S, S), 0)
    d = ImageDraw.Draw(im)
    if name == 'target':
        for r, f in ((92, 255), (72, 0), (52, 255), (32, 0), (14, 255)):
            d.ellipse((100 - r, 100 - r, 100 + r, 100 + r), fill=f)
    elif name == 'trophy':
        d.pieslice((40, -40, 160, 120), 0, 180, fill=255)
        d.rectangle((40, 20, 160, 40), fill=255)
        d.ellipse((14, 28, 62, 86), outline=255, width=12)
        d.ellipse((138, 28, 186, 86), outline=255, width=12)
        d.rectangle((88, 118, 112, 152), fill=255)
        d.rectangle((58, 152, 142, 176), fill=255)
    elif name == 'heart':
        pts = [(100 + 5.6 * 16 * math.sin(t) ** 3, 92 - 5.6 * (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)))
               for t in [k * 2 * math.pi / 120 for k in range(120)]]
        d.polygon(pts, fill=255)
    elif name == 'star':
        pts = []
        for k in range(10):
            r = 94 if k % 2 == 0 else 40
            a = -math.pi / 2 + k * math.pi / 5
            pts.append((100 + r * math.cos(a), 104 + r * math.sin(a)))
        d.polygon(pts, fill=255)
    elif name == 'check':
        d.line((26, 104, 78, 156, 176, 46), fill=255, width=34, joint='curve')
    elif name == 'arrow':
        d.polygon([(100, 12), (178, 96), (128, 96), (128, 188), (72, 188), (72, 96), (22, 96)], fill=255)
    elif name == 'chart':
        for k, h in enumerate((50, 86, 122, 168)):
            d.rectangle((18 + k * 44, 188 - h, 52 + k * 44, 188), fill=255)
    elif name == 'bolt':
        d.polygon([(112, 6), (36, 112), (92, 112), (78, 194), (166, 80), (108, 80), (130, 6)], fill=255)
    else:
        sys.exit(f'dot_shape "{name}" is not one of target trophy heart star check arrow chart bolt')
    sm = im.resize((n, n), Image.BILINEAR)
    return [[1 if sm.getpixel((x, y)) > 110 else 0 for x in range(n)] for y in range(n)]


def is_dark(hexc):
    return sum(int(hexc[k:k + 2], 16) * w for k, w in ((1, .299), (3, .587), (5, .114))) < 140


class EditorialFX:
    def band(self, e, default='center'):
        """horizontal placement for a text block: side "center" (full width), "left" or "right" half, or x + w"""
        side = e.get('side', default)
        if 'x' in e:
            return f'left:{float(e["x"]):.0f}px;width:{float(e.get("w", 520)):.0f}px;text-align:{e.get("align", "left")}'
        if side == 'left':
            return 'left:60px;width:520px;text-align:center'
        if side == 'right':
            return 'left:520px;width:520px;text-align:center'
        return 'left:0;width:1080px;text-align:center'

    def lit(self):
        """the accent as it should glow on screen: a dark accent (navy) glows in its light tint"""
        return self.T['accent2'] if is_dark(self.T['accent']) else self.T['accent']

    # ------------------------------------------------------------ big words
    def fx_word_behind(self, e):
        """a huge word behind the head (cutout), styles bold | chrome | serif | echo | outline, with an optional
        serif italic word in front of the speaker and a small line under it; numbers can count up"""
        T, i, lang = self.T, self.uid('wb'), self.j.get('lang')
        at, until = self.window(e, 2.6)
        style = e.get('style', 'bold')
        raw = str(e.get('text', ''))
        word = raw if style == 'serif' else upper(raw, lang)
        color = T['accent'] if e.get('color') == 'accent' else e.get('color', '#ffffff')
        if style == 'serif':
            size = float(e.get('size') or min(320, 1600 / max(1, len(word))))
        else:
            size = float(e.get('size') or min(360, 900 / max(1, len(word) * .5)))
        # high enough that the head covers only the bottom of the word: it reads, and it still sits behind
        y = float(e.get('y', self.eye - size * (1.25 if style not in ('echo', 'serif') else (1.6 if style == 'echo' else .95))))
        z = 12 if self.cut else 31
        fam = {"serif": "'Instrument Serif',serif;font-style:italic;font-weight:400",
               }.get(style, "'Anton',sans-serif;font-weight:400")
        looks = {'bold': f'color:{color};text-shadow:0 14px 40px rgba(0,0,0,.45)',
                 'outline': f'color:transparent;-webkit-text-stroke:3px {color}',
                 'serif': f'color:{color};text-shadow:0 0 50px {T["glow"]}88,0 10px 30px rgba(0,0,0,.4)',
                 'chrome': '', 'echo': f'color:{color}'}
        if style not in looks:
            sys.exit('word_behind style must be bold, chrome, serif, echo or outline')
        look = looks[style]
        cls = 'chrome' if style == 'chrome' else ''
        count = e.get('count_from')
        if count is not None:
            pre = ''.join(ch for ch in word[:len(word) - len(word.lstrip('$€£₼₽+'))])
            num = word[len(pre):]
            digits = ''.join(ch for ch in num if ch in DIGITS)
            suf = num[len(num.rstrip('%+kKmM')):] if digits else ''
            inner = f'<span class="{cls}" style="display:inline-block;{look}">{esc(pre)}<span id="{i}n">{esc(count)}</span>{esc(suf)}</span>'
            self.js(f'(function(){{const o={{v:{float(count)}}};const el=document.getElementById("{i}n");'
                    f'tl.to(o,{{v:{int(digits or 0)},duration:{float(e.get("count_for", 1.0)):.2f},ease:"power2.out",'
                    f'onUpdate:()=>{{el.textContent=Math.round(o.v)}}}},{at + .1:.3f});}})();')
            rows = f'<div class="{i}r" style="overflow:hidden;padding:.16em .04em .2em;margin:-.16em 0 -.2em">{inner}</div>'
        elif style == 'echo':
            rows = ''.join(f'<div class="{i}r" style="line-height:.86;{look if k == 1 else f"color:transparent;-webkit-text-stroke:2.5px {color};opacity:.55"}">{esc(word)}</div>'
                           for k in range(3))
        else:
            rows = ''.join(f'<span class="{i}c {cls}" style="display:inline-block;{look}">{esc(ch) if ch != " " else "&nbsp;"}</span>' for ch in word)
            rows = f'<div style="overflow:hidden;padding:.16em .04em .2em;margin:-.16em 0 -.2em">{rows}</div>'   # room for İ dots and Ç cedillas
        self.add(f'<div id="{i}" style="left:0;width:1080px;top:{y:.0f}px;text-align:center;font-family:{fam};font-size:{size:.0f}px;'
                 f'line-height:.92;letter-spacing:{"-.02em" if style == "serif" else ".005em"}"><div id="{i}w" style="display:inline-block">{rows}</div></div>', z=z)
        if style == 'echo':
            self.js(f'tl.fromTo(".{i}r",{{autoAlpha:0,x:(k)=>k%2?-140:140}},{{autoAlpha:1,x:0,duration:.6,stagger:.08,ease:"expo.out"}},{at:.3f});')
        elif count is not None:
            self.enter(f'.{i}r', at, 'y:80,scale:1.15', .55, 'expo.out')
        elif style == 'serif':
            self.js(f'tl.fromTo(".{i}c",{{autoAlpha:0,y:40,filter:"blur(18px)"}},{{autoAlpha:1,y:0,filter:"blur(0px)",duration:.7,stagger:.03,ease:"expo.out"}},{at:.3f});')
        else:
            self.js(f'tl.fromTo(".{i}c",{{yPercent:110}},{{yPercent:0,duration:.6,stagger:.035,ease:"power4.out"}},{at:.3f});')
        self.js(f'tl.fromTo("#{i}w",{{scale:1}},{{scale:{float(e.get("drift", 1.05))},duration:{max(.3, until - at):.3f},ease:"none"}},{at:.3f});')
        self.leave(f'#{i}', until, after=at + .3)
        if e.get('front'):
            fs = float(e.get('front_size', size * .5 if style != 'serif' else 120))
            fy = float(e.get('front_y', y + size * .62))
            self.add(f'<div id="{i}f" style="left:0;width:1080px;top:{fy:.0f}px;text-align:center;font:400 {fs:.0f}px/1 \'Instrument Serif\';'
                     f'font-style:italic;color:{e.get("front_color", self.lit())};text-shadow:0 6px 24px rgba(0,0,0,.6)">'
                     f'<span style="display:inline-block;transform:translateX({float(e.get("front_x", 120)):.0f}px)">{esc(e["front"])}</span></div>', z=36)
            fa = self.j.t(e.get('front_at'), at + .35)
            self.js(f'tl.fromTo("#{i}f",{{autoAlpha:0,scale:1.4,filter:"blur(14px)"}},{{autoAlpha:1,scale:1,filter:"blur(0px)",duration:.5,ease:"expo.out"}},{fa:.3f});')
            self.leave(f'#{i}f', until, after=fa)
        if e.get('sub'):
            sy = float(e.get('sub_y', y + size * .98 + (size * 1.6 if style == 'echo' else 0)))
            self.add(f'<div id="{i}s" style="left:0;width:1080px;top:{sy:.0f}px;text-align:center;font:600 30px Inter;letter-spacing:.22em;'
                     f'color:#fff;text-shadow:0 2px 12px rgba(0,0,0,.6)">{esc(upper(e["sub"], lang))}</div>', z=36)
            self.enter(f'#{i}s', self.j.t(e.get('sub_at'), at + .3), 'y:20', .45, 'power3.out')
            self.leave(f'#{i}s', until, after=at + .3)

    # ------------------------------------------------------------ light behind the speaker
    def fx_halo_ring(self, e):
        """a glowing ring (and optional light rays) behind the head"""
        T, i = self.T, self.uid('hr')
        at, until = self.window(e, 3.0)
        r = float(e.get('r', 270))
        cy = float(e.get('y', self.eye - 40))
        col = self.lit() if e.get('color', 'accent') == 'accent' else e['color']
        parts = ''
        if e.get('rays', False) or e.get('type') == 'light_rays':
            parts += (f'<div id="{i}y" class="a" style="left:{self.hx - 1100:.0f}px;top:{cy - 1100:.0f}px;width:2200px;height:2200px;border-radius:50%;'
                      f'background:repeating-conic-gradient(from 0deg,{col}55 0deg 4deg,transparent 4deg 13deg);mix-blend-mode:screen;'
                      f'-webkit-mask:radial-gradient(closest-side,#000 8%,transparent 70%);mask:radial-gradient(closest-side,#000 8%,transparent 70%);filter:blur(6px)"></div>')
        if e.get('ring', e.get('type') != 'light_rays'):
            parts += (f'<div id="{i}g" class="a" style="left:{self.hx - r:.0f}px;top:{cy - r:.0f}px;width:{2 * r:.0f}px;height:{2 * r:.0f}px;border-radius:50%;'
                      f'border:7px solid {col};box-shadow:0 0 40px {col},0 0 120px {col}aa,inset 0 0 40px {col}88"></div>'
                      f'<div class="a" style="left:{self.hx - r * 1.6:.0f}px;top:{cy - r * 1.6:.0f}px;width:{3.2 * r:.0f}px;height:{3.2 * r:.0f}px;border-radius:50%;'
                      f'background:radial-gradient(closest-side,{col}44,transparent);mix-blend-mode:screen"></div>')
        self.add(f'<div id="{i}" style="left:0;top:0;width:1080px;height:1920px">{parts}</div>', z=11 if self.cut else 29)
        self.js(f'tl.fromTo("#{i}",{{autoAlpha:0,scale:.7,transformOrigin:"{self.hx:.0f}px {cy:.0f}px"}},{{autoAlpha:1,scale:1,duration:.8,ease:"expo.out"}},{at:.3f});')
        if f'{i}y' in parts:
            self.js(f'tl.fromTo("#{i}y",{{rotation:0}},{{rotation:25,duration:{until - at + .5:.3f},ease:"none"}},{at:.3f});')
        if f'{i}g' in parts:
            self.js(f'tl.fromTo("#{i}g",{{scale:.96}},{{scale:1.03,duration:.9,ease:"sine.inOut",yoyo:true,repeat:{max(0, int((until - at) / .9))}}},{at + .8:.3f});')
        self.leave(f'#{i}', until, after=at + .4)

    def fx_light_rays(self, e):
        self.fx_halo_ring({**e, 'type': 'light_rays', 'rays': True})

    # ------------------------------------------------------------ B-roll cards
    def fx_paper_card(self, e):
        """a full-screen B-roll card: cream paper, green grid or dark; big title, line, taped photo, drawn circle, red stamp"""
        T, i, lang = self.T, self.uid('pc'), self.j.get('lang')
        at, until = self.window(e, 2.4)
        bg = e.get('bg', 'paper')
        if bg == 'paper':
            back, ink = 'radial-gradient(120% 90% at 30% 20%,#f8f4ec,#e9e2d4 70%,#ddd4c2)', '#1a1a1a'
        elif bg == 'grid':
            g = e.get('grid_color', '#1f7a45')
            back = (f'linear-gradient(rgba(255,255,255,.14) 2px,transparent 2px) 0 0/72px 72px,'
                    f'linear-gradient(90deg,rgba(255,255,255,.14) 2px,transparent 2px) 0 0/72px 72px,radial-gradient(120% 90% at 50% 30%,{g},#0b2a18)')
            ink = '#ffffff'
        else:
            back, ink = f'radial-gradient(120% 90% at 50% 30%,#1c1c1c,#050505)', '#ffffff'
        tcol = T['accent'] if e.get('title_color', 'accent') == 'accent' else e['title_color']
        title = e.get('title', '')
        ts = e.get('title_style', 'bold')
        if ts == 'serif':
            tsz = float(e.get('title_size') or min(220, 1500 / max(1, len(title))))
            tf = f"font:400 {tsz:.0f}px/1 'Instrument Serif';font-style:italic;color:{tcol};letter-spacing:-.02em"
            ttxt = esc(title)
        else:
            tsz = float(e.get('title_size') or min(260, 880 / max(1, len(title) * .5)))
            tf = f"font:400 {tsz:.0f}px/.9 'Anton';color:{tcol}"
            ttxt = esc(upper(title, lang))
        ty = float(e.get('title_y', 780))
        photo = ''
        if e.get('photo'):
            img = self.j.images(e['photo'])[0]
            photo = (f'<div class="a {i}ph" style="left:{float(e.get("photo_x", 300)):.0f}px;top:{float(e.get("photo_y", 330)):.0f}px;width:480px;padding:18px 18px 70px;'
                     f'background:#fff;box-shadow:0 30px 60px rgba(0,0,0,.35);transform:rotate({float(e.get("photo_rot", -4)):.1f}deg)">'
                     f'<div style="width:444px;height:400px;background:url({self.c.asset(img)}) center/cover"></div>'
                     f'<div style="position:absolute;left:0;right:0;bottom:16px;text-align:center;font:400 38px \'Instrument Serif\';font-style:italic;color:#333">{esc(e.get("photo_caption", ""))}</div>'
                     f'<div style="position:absolute;left:180px;top:-22px;width:130px;height:44px;background:rgba(235,225,200,.85);transform:rotate(3deg);'
                     f'box-shadow:0 2px 6px rgba(0,0,0,.15)"></div></div>')
        sub = (f'<div class="a {i}sb" style="left:80px;right:80px;top:{ty + tsz * 1.02:.0f}px;text-align:center;font:500 40px/1.25 Inter;color:{ink};opacity:.8">'
               f'{esc(e["sub"])}</div>') if e.get('sub') else ''
        stamp = (f'<div class="a {i}st" style="left:0;right:0;top:{float(e.get("stamp_y", ty - 120)):.0f}px;text-align:center"><span style="display:inline-block;'
                 f'padding:10px 24px;background:#e3261d;color:#fff;font:400 58px/1 Anton;letter-spacing:.02em;transform:rotate(-3deg)">{esc(upper(e["stamp"], lang))}</span></div>'
                 ) if e.get('stamp') else ''
        circle = ''
        if e.get('circle'):
            w, h = min(1000, tsz * len(title) * (.5 if ts != 'serif' else .42) + 140), tsz * 1.25
            cx, cy = 540, ty + tsz * .45
            circle = (f'<svg class="a" style="left:0;top:0" width="1080" height="1920" viewBox="0 0 1080 1920">'
                      f'<path class="{i}ci" d="{self._scribble_path(cx, cy, w, h)}" fill="none" stroke="{e.get("circle_color", "#e3261d")}" stroke-width="8" '
                      f'stroke-linecap="round" stroke-dasharray="3200" stroke-dashoffset="3200"/></svg>')
        self.add(f'<div id="{i}" style="inset:0;background:{back};overflow:hidden">'
                 f'<div class="a" style="inset:0;background:radial-gradient(140% 100% at 50% 50%,transparent 60%,rgba(0,0,0,.25))"></div>{photo}'
                 f'<div class="a {i}t" style="left:40px;right:40px;top:{ty:.0f}px;text-align:center;{tf}">{ttxt}</div>{sub}{stamp}{circle}</div>', z=38)
        kind = e.get('enter', 'slide')
        if kind == 'flash':
            self.js(f'tl.fromTo("#{i}",{{autoAlpha:0}},{{autoAlpha:1,duration:.08}},{at:.3f});')
            self.fx_transition({'kind': 'flash', 'at': at})
        else:
            self.js(f'tl.fromTo("#{i}",{{yPercent:105,rotation:4}},{{yPercent:0,rotation:0,duration:.55,ease:"expo.out"}},{at:.3f});')
        # a full-screen card must never stand still: a held frame reads as the video freezing
        self.js(f'tl.fromTo("#{i}",{{scale:1}},{{scale:1.06,duration:{max(.5, until - at):.3f},ease:"none"}},{at:.3f});')
        self.js(f'tl.fromTo("#{i} .{i}t",{{autoAlpha:0,scale:1.3,filter:"blur(16px)"}},{{autoAlpha:1,scale:1,filter:"blur(0px)",duration:.55,ease:"expo.out"}},{at + .2:.3f});')
        if photo:
            self.js(f'tl.fromTo("#{i} .{i}ph",{{autoAlpha:0,y:-400,rotation:-25}},{{autoAlpha:1,y:0,rotation:{float(e.get("photo_rot", -4))},duration:.6,ease:"back.out(1.4)"}},{at + .3:.3f});')
        if sub:
            self.enter(f'#{i} .{i}sb', at + .45, 'y:20', .4, 'power3.out')
        if stamp:
            self.js(f'tl.fromTo("#{i} .{i}st",{{autoAlpha:0,scale:2.2}},{{autoAlpha:1,scale:1,duration:.3,ease:"power4.in"}},{self.j.t(e.get("stamp_at"), at + .6):.3f});')
        if circle:
            self.js(f'tl.to("#{i} .{i}ci",{{strokeDashoffset:0,duration:.6,ease:"power2.inOut"}},{self.j.t(e.get("circle_at"), at + .7):.3f});')
        if until < self.c.dur - .06:
            self.js(f'tl.to("#{i}",{{yPercent:-105,duration:.45,ease:"expo.in"}},{max(at + .8, until - .45):.3f});')

    def _scribble_path(self, cx, cy, w, h, turns=1.15, seed=5):
        """a hand-drawn ellipse that overshoots its start"""
        rnd = random.Random(seed)
        pts, n = [], 48
        for k in range(int(n * turns) + 1):
            a = -math.pi * .8 + k * 2 * math.pi / n
            j = 1 + rnd.uniform(-.035, .035) + .05 * k / n
            pts.append((cx + w / 2 * j * math.cos(a), cy + h / 2 * j * math.sin(a) + (k / n) * 10))
        return 'M ' + ' L '.join(f'{x:.1f} {y:.1f}' for x, y in pts)

    def fx_polaroids(self, e):
        """taped polaroid photos drop onto the frame (behind the head with `behind`)"""
        i = self.uid('pl')
        at, until = self.window(e, 2.8)
        imgs = self.j.images(e.get('images'))[:3]
        if not imgs:
            sys.exit('polaroids needs "images"')
        caps = e.get('captions') or []
        y = float(e.get('y', 300))
        n = len(imgs)
        rots = [-7, 5, -3]
        for k, p in enumerate(imgs):
            x = 540 + (k - (n - 1) / 2) * 300 - 150
            cap = esc(caps[k]) if k < len(caps) else ''
            self.add(f'<div id="{i}_{k}" class="{i}" style="left:{x:.0f}px;top:{y + (k % 2) * 60:.0f}px;width:300px;padding:14px 14px 60px;background:#fff;'
                     f'box-shadow:0 26px 50px rgba(0,0,0,.45);transform:rotate({rots[k]}deg)">'
                     f'<div style="width:272px;height:272px;background:url({self.c.asset(p)}) center/cover"></div>'
                     f'<div style="position:absolute;left:0;right:0;bottom:12px;text-align:center;font:400 34px \'Instrument Serif\';font-style:italic;color:#333">{cap}</div>'
                     f'<div style="position:absolute;left:96px;top:-18px;width:110px;height:38px;background:rgba(235,225,200,.85);transform:rotate({-rots[k]}deg)"></div></div>',
                     z=12 if (self.cut and e.get('behind')) else 33)
            t = self.j.t((e.get('at_each') or [None] * 3)[k] if k < len(e.get('at_each') or []) else None, at + k * .18)
            self.js(f'tl.fromTo("#{i}_{k}",{{autoAlpha:0,y:-500,rotation:{rots[k] * 4}}},{{autoAlpha:1,y:0,rotation:{rots[k]},duration:.6,ease:"back.out(1.3)"}},{t:.3f});')
        self.leave(f'.{i}', until, after=at + .6)

    def fx_scribble(self, e):
        """a marker circle, underline or arrow drawn on the frame, with an optional handwritten-style label"""
        i = self.uid('sc')
        at, until = self.window(e, 2.4)
        x, y, w, h = (float(v) for v in e.get('box', [340, 600, 400, 300]))
        col = e.get('color', self.T['accent'])
        shape = e.get('shape', 'circle')
        if shape == 'circle':
            d = self._scribble_path(x + w / 2, y + h / 2, w * 1.15, h * 1.15, seed=int(x + y))
        elif shape == 'underline':
            d = f'M {x - 10:.0f} {y + h:.0f} C {x + w * .3:.0f} {y + h - 14:.0f}, {x + w * .7:.0f} {y + h + 12:.0f}, {x + w + 20:.0f} {y + h - 6:.0f}'
        elif shape == 'arrow':
            d = (f'M {x:.0f} {y:.0f} C {x + w * .2:.0f} {y + h * .9:.0f}, {x + w * .7:.0f} {y + h:.0f}, {x + w:.0f} {y + h:.0f} '
                 f'M {x + w - 46:.0f} {y + h - 34:.0f} L {x + w:.0f} {y + h:.0f} L {x + w - 50:.0f} {y + h + 30:.0f}')
        else:
            sys.exit('scribble shape must be circle, underline or arrow')
        lab = ''
        if e.get('label'):
            lx, ly = e.get('label_at_xy', [x + w + 20, y - 70])
            lab = (f'<div class="a {i}l" style="left:{float(lx):.0f}px;top:{float(ly):.0f}px;font:400 60px/1 \'Instrument Serif\';font-style:italic;color:{col};'
                   f'text-shadow:0 4px 16px rgba(0,0,0,.5);white-space:nowrap">{esc(e["label"])}</div>')
        self.add(f'<div id="{i}" style="left:0;top:0;width:1080px;height:1920px"><svg width="1080" height="1920" viewBox="0 0 1080 1920" style="position:absolute;left:0;top:0">'
                 f'<path class="{i}p" d="{d}" fill="none" stroke="{col}" stroke-width="{float(e.get("width", 9)):.0f}" stroke-linecap="round" stroke-linejoin="round" '
                 f'stroke-dasharray="4000" stroke-dashoffset="4000" style="filter:drop-shadow(0 4px 10px rgba(0,0,0,.4))"/></svg>{lab}</div>', z=36)
        self.js(f'tl.set("#{i}",{{autoAlpha:1}},{at:.3f});tl.to("#{i} .{i}p",{{strokeDashoffset:0,duration:{float(e.get("draw_for", .65)):.2f},ease:"power2.inOut"}},{at:.3f});')
        if lab:
            self.enter(f'#{i} .{i}l', at + .45, 'y:16,rotation:-6', .4, 'back.out(2)')
        self.leave(f'#{i}', until, after=at + .6)

    # ------------------------------------------------------------ boxes, bubbles, ratings, dots
    def fx_label_box(self, e):
        """coloured boxes with text that pop in one after another (yellow, red, teal or white)"""
        i = self.uid('lb')
        items = e.get('items') or ([{'text': e['text'], 'at': e.get('at')}] if e.get('text') else [])
        if not items:
            sys.exit('label_box needs "text" or "items"')
        at, until = self.window({**e, 'at': e.get('at', items[0].get('at'))}, 2.6)
        y = float(e.get('y', 1060))
        dark = sum(int(self.T['accent'][k:k + 2], 16) * w for k, w in ((1, .299), (3, .587), (5, .114))) < 140
        styles = {'accent': (self.T['accent'], '#fff' if dark else '#111'), 'yellow': ('#ffd60a', '#111'), 'red': ('#e3261d', '#fff'),
                  'teal': ('#2dd4bf', '#062a26'), 'white': ('#ffffff', '#111'), 'black': ('#111111', '#fff')}
        rows = ''
        for k, it in enumerate(items[:4]):
            bgc, fg = styles.get(it.get('style', e.get('style', 'accent')), styles['accent'])
            rot = (-2.2, 1.6, -1.2, 2)[k]
            big = it.get('big', len(items) == 1)
            rows += (f'<div style="margin-top:{0 if k == 0 else 14}px"><span id="{i}_{k}" style="display:inline-block;padding:{"14px 30px" if big else "10px 22px"};'
                     f'background:{bgc};color:{fg};font:{"400 92px/1 Anton" if big else "700 48px/1.1 Inter"};letter-spacing:{".01em" if big else "-.01em"};'
                     f'border-radius:{6 if big else 14}px;transform:rotate({rot}deg);box-shadow:0 14px 34px rgba(0,0,0,.4)">'
                     f'{esc(upper(it["text"], self.j.get("lang")) if big else it["text"])}</span></div>')
        self.add(f'<div id="{i}" style="{self.band(e)};top:{y:.0f}px">{rows}</div>', z=36)
        for k, it in enumerate(items[:4]):
            t = self.j.t(it.get('at'), at + k * .3)
            self.js(f'tl.fromTo("#{i}_{k}",{{autoAlpha:0,scale:.4}},{{autoAlpha:1,scale:1,duration:.42,ease:"back.out(2.4)"}},{t:.3f});')
        self.leave(f'#{i}', until, after=at + .4)

    def fx_bubble(self, e):
        """a chat bubble: typing dots, then the message"""
        i = self.uid('bb')
        at, until = self.window(e, 2.6)
        y = float(e.get('y', 300))
        right = e.get('side', 'left') == 'right'
        col = {'blue': '#0a84ff', 'green': '#30d158', 'gray': '#3a3a3c', 'white': '#ffffff'}.get(e.get('color', 'blue'), e.get('color'))
        fg = '#111' if col == '#ffffff' else '#fff'
        frm = (f'<div style="font:500 24px Inter;color:#fff;opacity:.75;margin:0 18px 8px;text-align:{"right" if right else "left"}">{esc(e["from"])}</div>'
               if e.get('from') else '')
        dots = ''.join(f'<i class="{i}d" style="display:inline-block;width:16px;height:16px;border-radius:50%;background:{fg};opacity:.7;margin:0 5px"></i>' for _ in range(3))
        self.add(f'<div id="{i}" style="{"right" if right else "left"}:110px;top:{y:.0f}px;max-width:760px">{frm}'
                 f'<div style="position:relative;display:inline-block;padding:22px 30px;border-radius:38px;background:{col};color:{fg};'
                 f'font:500 44px/1.2 Inter;letter-spacing:-.01em;box-shadow:0 18px 40px rgba(0,0,0,.35);'
                 f'border-{"bottom-right" if right else "bottom-left"}-radius:10px">'
                 f'<span id="{i}t" style="visibility:hidden">{esc(e.get("text", ""))}</span>'
                 f'<span id="{i}k" style="position:absolute;left:30px;top:50%;transform:translateY(-50%)">{dots}</span></div></div>', z=36)
        self.enter(f'#{i}', at, f'y:30,scale:.6,transformOrigin:"{"right" if right else "left"} bottom"', .4, 'back.out(2)')
        self.js(f'tl.fromTo(".{i}d",{{y:0}},{{y:-10,duration:.2,stagger:.1,yoyo:true,repeat:3,ease:"sine.inOut"}},{at + .1:.3f});')
        reveal = self.j.t(e.get('text_at'), at + .75)
        self.js(f'tl.set("#{i}k",{{autoAlpha:0}},{reveal:.3f});tl.set("#{i}t",{{visibility:"visible"}},{reveal:.3f});'
                f'tl.fromTo("#{i}t",{{autoAlpha:0}},{{autoAlpha:1,duration:.2}},{reveal:.3f});')
        self.leave(f'#{i}', until, after=reveal)

    def fx_star_rating(self, e):
        """five stars fill one by one, with a score and a label"""
        i = self.uid('sr')
        at, until = self.window(e, 2.6)
        y = float(e.get('y', 320))
        star = '<svg viewBox="0 0 24 24" width="70" height="70"><path d="M12 2.5l2.9 6 6.6.8-4.9 4.5 1.3 6.5L12 17l-5.9 3.3 1.3-6.5L2.5 9.3l6.6-.8z" fill="{f}" stroke="{s}" stroke-width="1"/></svg>'
        stars = ''.join(f'<span class="{i}s" style="display:inline-block;margin:0 4px">{star.format(f="#ffc533", s="#ffc533")}</span>' for _ in range(5))
        self.add(f'<div id="{i}" class="gl" style="left:170px;top:{y:.0f}px;width:740px;border-radius:40px;padding:26px 30px;text-align:center;color:#fff">'
                 f'<div style="display:flex;align-items:center;justify-content:center;gap:18px"><span style="font:700 76px/1 Inter;letter-spacing:-.04em">{esc(e.get("score", "5.0"))}</span>'
                 f'<span>{stars}</span></div><div style="margin-top:10px;font:500 30px Inter;opacity:.75">{esc(e.get("label", ""))}</div></div>', z=35)
        self.enter(f'#{i}', at, 'y:30,scale:.85')
        self.js(f'tl.fromTo(".{i}s",{{scale:0,rotation:-90}},{{scale:1,rotation:0,duration:.4,stagger:.1,ease:"back.out(3)"}},{at + .25:.3f});')
        self.leave(f'#{i}', until, after=at + .8)

    def fx_dot_shape(self, e):
        """glowing dots fly in from a scatter and build a shape (target, trophy, heart, star, check, arrow, chart, bolt)"""
        i = self.uid('ds')
        at, until = self.window(e, 2.6)
        grid = shape_mask(e.get('shape', 'target'), int(e.get('grid', 24)))
        n = len(grid)
        size = float(e.get('size', 480))
        step = size / n
        cx, cy = float(e.get('x', 540)), float(e.get('y', 560))
        col = self.lit() if e.get('color', 'accent') == 'accent' else e['color']
        rnd = random.Random(11)
        dots, js = [], []
        k = 0
        for gy in range(n):
            for gx in range(n):
                if not grid[gy][gx]:
                    continue
                x, y = cx - size / 2 + gx * step, cy - size / 2 + gy * step
                sx, sy = rnd.uniform(-520, 520), rnd.uniform(-700, 700)
                dots.append(f'<i id="{i}_{k}" style="position:absolute;left:{x:.1f}px;top:{y:.1f}px;width:{step * .62:.1f}px;height:{step * .62:.1f}px;border-radius:50%;'
                            f'background:{col};box-shadow:0 0 {step * .6:.0f}px {col}"></i>')
                dist = math.hypot(x - cx, y - cy) / size
                js.append(f'tl.fromTo("#{i}_{k}",{{x:{sx:.0f},y:{sy:.0f},autoAlpha:0,scale:.3}},{{x:0,y:0,autoAlpha:1,scale:1,duration:.7,ease:"expo.out"}},{at + dist * .5:.3f});')
                k += 1
        lab = (f'<div style="position:absolute;left:{cx - 400:.0f}px;width:800px;top:{cy + size / 2 + 30:.0f}px;text-align:center;font:600 46px Inter;color:#fff;'
               f'letter-spacing:-.02em;text-shadow:0 4px 16px rgba(0,0,0,.6)" class="{i}l">{esc(e["label"])}</div>') if e.get('label') else ''
        self.add(f'<div id="{i}" style="left:0;top:0;width:1080px;height:1920px">{"".join(dots)}{lab}</div>', z=12 if (self.cut and e.get('behind')) else 34)
        self.c.js.extend(js)
        if lab:
            self.enter(f'#{i} .{i}l', at + .6, 'y:20', .4, 'power3.out')
        self.leave(f'#{i}', until, after=at + .9)

    # ------------------------------------------------------------ transitions
    def fx_transition(self, e):
        """flash | pixel | whip | bw (black-and-white, then colour sweeps back) | leak"""
        kind = e.get('kind', 'flash')
        at = self.j.t(e.get('at'), 0)
        i = self.uid('tr')
        if kind == 'flash':
            self.c.body.append(f'<div id="{i}" data-z="44" style="inset:0;background:#fff;opacity:0;mix-blend-mode:screen"></div>')
            self.js(f'tl.to("#{i}",{{opacity:.85,duration:.06,ease:"power1.in"}},{at:.3f});tl.to("#{i}",{{opacity:0,duration:.3,ease:"power2.out"}},{at + .06:.3f});')
        elif kind == 'pixel':
            col = self.T['accent'] if e.get('color', 'accent') == 'accent' else e['color']
            cols, rows = 9, 16
            cw, ch = 1080 / cols, 1920 / rows
            rnd = random.Random(int(at * 100) + 3)
            cells = []
            for r in range(rows):
                for q in range(cols):
                    d1 = rnd.uniform(0, .18)
                    tone = col if rnd.random() < .7 else '#0b0b0b'
                    cells.append(f'<i class="{i}c" style="position:absolute;left:{q * cw:.1f}px;top:{r * ch:.1f}px;width:{cw + 1:.1f}px;height:{ch + 1:.1f}px;'
                                 f'background:{tone};opacity:0"></i>')
                    self.js(f'tl.to("#{i} i:nth-child({len(cells)})",{{opacity:1,duration:.04}},{at + d1:.3f});'
                            f'tl.to("#{i} i:nth-child({len(cells)})",{{opacity:0,duration:.06}},{at + .24 + d1:.3f});')
            self.c.body.append(f'<div id="{i}" data-z="44" style="inset:0">{"".join(cells)}</div>')
        elif kind == 'whip':
            self.js(f'tl.to("#cam",{{filter:"blur(14px)",duration:.12,ease:"power2.in"}},{at - .12:.3f});'
                    f'tl.to("#cam",{{filter:"blur(0px)",duration:.22,ease:"power2.out"}},{at:.3f});'
                    f'tl.fromTo(".zz",{{scale:1}},{{scale:1.18,duration:.12,ease:"power2.in",immediateRender:false}},{at - .12:.3f});'
                    f'tl.to(".zz",{{scale:1,duration:.3,ease:"expo.out"}},{at:.3f});')
        elif kind == 'bw' and e.get('reverse'):          # colour drains away: an ending, a loss, "nothing changes"
            for sel in ('#cam', '#cutw') if self.cut else ('#cam',):
                self.js(f'tl.fromTo("{sel}",{{filter:"grayscale(0) contrast(1)"}},{{filter:"grayscale(1) contrast(1.12)",duration:{float(e.get("for", 1.2)):.2f},'
                        f'ease:"power1.inOut",immediateRender:false}},{at:.3f});')
        elif kind == 'bw':
            self.js(f'tl.set("#cam",{{filter:"grayscale(1) contrast(1.1)"}},0);'
                    f'tl.to("#cam",{{filter:"grayscale(0) contrast(1)",duration:{float(e.get("for", .6)):.2f},ease:"power2.out"}},{at:.3f});')
            if self.cut:
                self.js(f'tl.set("#cutw",{{filter:"grayscale(1) contrast(1.1)"}},0);'
                        f'tl.to("#cutw",{{filter:"grayscale(0) contrast(1)",duration:{float(e.get("for", .6)):.2f},ease:"power2.out"}},{at:.3f});')
            self.leak(at - .1, .9)
        elif kind == 'leak':
            self.leak(at, float(e.get('for', 1.0)))
        else:
            sys.exit('transition kind must be flash, pixel, whip, bw or leak')
