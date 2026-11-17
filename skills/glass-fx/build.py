#!/usr/bin/env python3
"""glass-fx: a talking-head reel dressed in a violet glass look, with up to a dozen word-anchored effects
(halo search, ribbon wrap, falling cards, social orbit, quote note, icon pop, typing search, film strip,
chrome title, glass card, checklist, takeover) and serif-accented word captions.

    <kit>/.venv/bin/python build.py spec.json

Spec (see SKILL.md):
  video, start, end, out, transcript
  theme: violet | teal | ember | mono            the colour of the grade, glass and glow
  eye_y: 760                                       y of the eyes in 1080x1920 (places effects around the head)
  cutout: false | true | "path/to/cutout.webm"     cut the speaker out so effects pass BEHIND them
  captions: {top: 1240, size: 66, keys: [...], maxw: 3}  or false
  zoom: 1.06 | [{"at": "word", "scale": 1.18}]     slow push-in, plus punch-ins on words
  effects: [{type, at, until?, ...}]
"""
import html
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'kit'))
from reel import Job, Comp, bare, groups, rich  # noqa: E402

THEMES = {
    'violet': dict(accent='#8b5cf6', accent2='#c4b5fd', deep='#140630', mid='#3b1d8f', glow='#a78bfa', ink='#1b1035'),
    'teal':   dict(accent='#22d3ee', accent2='#a5f3fc', deep='#031821', mid='#0e5a73', glow='#67e8f9', ink='#062430'),
    'ember':  dict(accent='#fb7185', accent2='#fecdd3', deep='#1f0610', mid='#7f1d3a', glow='#fda4af', ink='#2a0a14'),
    'mono':   dict(accent='#a1a1aa', accent2='#f4f4f5', deep='#09090b', mid='#3f3f46', glow='#e4e4e7', ink='#18181b'),
}

ICONS = {
    'check': '<path d="M5 12.5l4.5 4.5L19 7"/>',
    'eye': '<path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
    'heart': '<path d="M12 20s-7.5-4.6-7.5-10.2A4.3 4.3 0 0 1 12 7.3a4.3 4.3 0 0 1 7.5 2.5C19.5 15.4 12 20 12 20z"/>',
    'star': '<path d="M12 3l2.8 5.8 6.2.7-4.6 4.3 1.3 6.2-5.7-3.1-5.7 3.1 1.3-6.2L3 9.5l6.2-.7z"/>',
    'bolt': '<path d="M13 2L4 14h7l-1 8 9-12h-7z"/>',
    'user': '<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 3.6-7 8-7s8 3 8 7"/>',
    'users': '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20c0-3.6 2.9-6 6.5-6s6.5 2.4 6.5 6"/><path d="M16 4.6a3.5 3.5 0 0 1 0 6.8M18 14.4c2.2.7 3.5 2.8 3.5 5.6"/>',
    'search': '<circle cx="11" cy="11" r="7"/><path d="M20.5 20.5L16 16"/>',
    'plus': '<path d="M12 5v14M5 12h14"/>',
    'chart': '<path d="M4 20V11M10 20V5M16 20v-6M2 20h20"/>',
    'clock': '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.2 2"/>',
    'calendar': '<rect x="3" y="5" width="18" height="16" rx="3"/><path d="M3 10h18M8 3v4M16 3v4"/>',
    'arrow': '<path d="M5 12h14M13 6l6 6-6 6"/>',
    'play': '<path d="M8 5v14l11-7z"/>',
    'message': '<path d="M21 12a8.5 8.5 0 0 1-12.3 7.6L3.5 21l1.6-4.9A8.5 8.5 0 1 1 21 12z"/>',
    'money': '<rect x="2.5" y="6" width="19" height="12" rx="2.5"/><circle cx="12" cy="12" r="2.6"/>',
    'lock': '<rect x="5" y="11" width="14" height="10" rx="2.5"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/>',
    'fire': '<path d="M12 22c4 0 7-2.7 7-6.8 0-4.6-4-6.6-4.6-11.2C11 6 9.8 9 10 11.4 8.6 10.6 8 9.2 8 8 6 9.8 5 12.4 5 15.2 5 19.3 8 22 12 22z"/>',
    'instagram': '<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4.2"/><circle cx="17.4" cy="6.6" r=".9" fill="currentColor"/>',
    'youtube': '<rect x="2" y="5" width="20" height="14" rx="4"/><path d="M10 9v6l5-3z" fill="currentColor"/>',
    'tiktok': '<path d="M14 3v11.5a3.8 3.8 0 1 1-3.8-3.8"/><path d="M14 3c.4 2.6 2.3 4.4 5 4.6"/>',
    'x': '<path d="M4 4l16 16M20 4L4 20"/>',
    'linkedin': '<rect x="3" y="3" width="18" height="18" rx="3"/><path d="M8 10.5V17M8 7.2v.1M12 17v-6.5M12 13.4c0-1.8 1-2.9 2.5-2.9s2.5 1 2.5 2.9V17"/>',
    'mail': '<rect x="3" y="5" width="18" height="14" rx="3"/><path d="M3.5 6.5l8.5 6.5 8.5-6.5"/>',
    'sparkle': '<path d="M12 3l1.9 5.6L19.5 10.5 13.9 12.4 12 18l-1.9-5.6L4.5 10.5l5.6-1.9z"/><path d="M19 16l.8 2.2L22 19l-2.2.8L19 22l-.8-2.2L16 19l2.2-.8z"/>',
}

CURSOR = ('<svg viewBox="0 0 28 34" width="96" height="116"><path d="M4 2v24.5l6.3-6 4.4 10.2 4.4-1.9-4.4-10H23z" '
          'fill="#fff" stroke="#111" stroke-width="1.7" stroke-linejoin="round"/></svg>')


def icon(name, size=44, sw=2.0, color='currentColor'):
    body = ICONS.get(name)
    if body is None:
        sys.exit(f'icon "{name}" is not one of: {", ".join(sorted(ICONS))}')
    return (f'<svg viewBox="0 0 24 24" width="{size}" height="{size}" fill="none" stroke="{color}" stroke-width="{sw}" '
            f'stroke-linecap="round" stroke-linejoin="round">{body}</svg>')


def esc(s):
    return html.escape(str(s))


def serif(s):
    """*word* -> serif italic accent"""
    return rich(s).replace('<em>', '<span class="sf">').replace('</em>', '</span>')


class Reel:
    def __init__(self, spec):
        self.j = j = Job(spec, 'glass-fx')
        self.c = c = Comp(j)
        self.T = THEMES.get(j.get('theme', 'violet'))
        if not self.T:
            sys.exit(f'theme must be one of {", ".join(THEMES)}')
        self.eye = float(j.get('eye_y', 760))
        self.n = 0
        self.cut = None
        cv = j.get('cutout', False)
        if cv:
            self.cut = j.path(cv) if isinstance(cv, str) else j.cutout()

    # ------------------------------------------------------------ helpers
    def js(self, s):
        self.c.js.append(s)

    def add(self, html_, z=30):
        """an absolutely placed layer straight under #root (so z-index can put it behind or in front of the cutout)"""
        self.c.body.append(html_.replace('<div ', f'<div data-z="{z}" ', 1))

    def uid(self, p='e'):
        self.n += 1
        return f'{p}{self.n}'

    def window(self, e, hold=2.8):
        at = self.j.t(e.get('at'), 0)
        until = self.j.t(e.get('until')) if e.get('until') is not None else at + float(e.get('hold', hold))
        return round(at, 3), round(min(until, self.c.dur - 0.05), 3)

    def enter(self, sel, at, frm='scale:.82,y:30', dur=.5, ease='back.out(1.7)'):
        self.js(f'tl.fromTo({json.dumps(sel)},{{autoAlpha:0,filter:"blur(14px)",{frm}}},'
                f'{{autoAlpha:1,filter:"blur(0px)",scale:1,x:0,y:0,rotation:0,duration:{dur},ease:"{ease}"}},{at:.3f});')

    def leave(self, sel, t, dur=.32, after=0.0):
        """exit at t (never before `after` + a beat, so an element always gets seen)"""
        if t >= self.c.dur - 0.06:
            return
        self.js(f'tl.to({json.dumps(sel)},{{autoAlpha:0,scale:.9,filter:"blur(12px)",duration:{dur},ease:"power2.in"}},{max(0, t - dur, after + .45):.3f});')

    # ------------------------------------------------------------ look
    def base(self):
        c, j, T = self.c, self.j, self.T
        c.css.append(f'''
#root{{background:{T['deep']}}}
#root>[data-z]{{position:absolute}}
.gl{{background:linear-gradient(160deg,rgba(255,255,255,.28),rgba(255,255,255,.07) 55%,rgba(255,255,255,.13)),{T['deep']}73;
  border:1.5px solid rgba(255,255,255,.38);box-shadow:inset 0 1.5px 0 rgba(255,255,255,.55),inset 0 -12px 30px rgba(255,255,255,.05),
  0 30px 70px rgba(5,0,25,.5);backdrop-filter:blur(26px) saturate(1.5);-webkit-backdrop-filter:blur(26px) saturate(1.5)}}
.pill{{background:linear-gradient(180deg,#ffffff,#ece8f6);color:{T['ink']};box-shadow:0 0 0 1.5px rgba(255,255,255,.7),
  0 0 60px {T['glow']}88,0 18px 40px rgba(5,0,25,.45)}}
.sf{{font-family:'Instrument Serif',serif;font-style:italic;font-weight:400;letter-spacing:-.01em}}
.ico{{display:flex;align-items:center;justify-content:center;border-radius:50%;color:#fff}}
.sph{{position:absolute;border-radius:50%;background:radial-gradient(circle at 34% 30%,#fff 0,{T['accent2']} 14%,{T['accent']} 42%,{T['deep']} 92%);
  box-shadow:0 0 40px {T['accent']}66}}
.ring{{position:absolute;border-radius:50%;border:2px solid rgba(255,255,255,.22);left:50%;top:50%;transform:translate(-50%,-50%)}}
.chrome{{font-family:'Anton',sans-serif;text-transform:uppercase;line-height:.9;letter-spacing:.005em;color:transparent;
  background:linear-gradient(180deg,#ffffff 0%,#e9e9f1 30%,#8c8c9c 49%,#4b4b58 52%,#d6d6e0 66%,#ffffff 82%,#9d9dac 100%);
  background-size:100% 100%;-webkit-background-clip:text;background-clip:text}}
''')
        c.css.append("@font-face{font-family:'Anton';src:url(fonts/anton-400-normal.woff2) format('woff2')}")
        # the camera: the take, slowly pushed in, with punch-ins on words
        z = j.get('zoom', 1.06)
        c.body.append(f'<div id="cam" data-z="1" style="left:0;top:0;width:1080px;height:1920px;transform-origin:540px {self.eye:.0f}px">'
                      + c.video(j.clip, 'position:absolute;left:0;top:0;width:1080px;height:1920px;'
                                'filter:saturate(1.08) contrast(1.06) brightness(.93)', 'bg') + '</div>')
        if self.cut:
            c.body.append(f'<div id="cutw" data-z="20" style="left:0;top:0;width:1080px;height:1920px;transform-origin:540px {self.eye:.0f}px">'
                          + c.video(self.cut, 'position:absolute;left:0;top:0;width:1080px;height:1920px;'
                                    'filter:saturate(1.08) contrast(1.06) brightness(.93)', 'cut') + '</div>')
        cams = '["#cam","#cutw"]' if self.cut else '"#cam"'
        push = z if isinstance(z, (int, float)) else 1.06
        self.js(f'tl.fromTo({cams},{{scale:1}},{{scale:{push},duration:{c.dur:.3f},ease:"none"}},0);')
        if isinstance(z, list):
            for p in z:
                t = j.t(p.get('at'))
                s = float(p.get('scale', 1.16))
                d = float(p.get('for', 1.2))
                self.js(f'tl.to({cams},{{scale:{s},duration:.35,ease:"power3.out",overwrite:false}},{t:.3f});'
                        f'tl.to({cams},{{scale:{push},duration:.5,ease:"power2.inOut"}},{t + d:.3f});')
        # the grade: colour cast, top and bottom fades, vignette
        c.body.append(f'<div data-z="3" style="inset:0;background:{T["accent"]};mix-blend-mode:color;opacity:.16"></div>')
        c.body.append(f'<div data-z="3" style="inset:0;background:linear-gradient(180deg,{T["deep"]}d0 0%,{T["deep"]}00 26%,'
                      f'{T["deep"]}00 58%,{T["deep"]}e6 100%)"></div>')
        c.body.append('<div data-z="3" style="inset:0;background:radial-gradient(120% 80% at 50% 45%,transparent 55%,rgba(0,0,0,.55) 100%)"></div>')
        c.body.append(f'<div data-z="3" style="left:-200px;top:{self.eye - 600:.0f}px;width:1480px;height:1200px;'
                      f'background:radial-gradient(closest-side,{T["glow"]}30,transparent);mix-blend-mode:screen"></div>')
        # floating glossy spheres (depth of field: the small ones are sharp, the big ones soft)
        if j.get('spheres', True):
            for k, (x, y, r, b, dy) in enumerate([(70, 300, 26, 0, -60), (930, 520, 44, 3, -90), (860, 1180, 22, 0, -50),
                                                   (120, 1050, 60, 8, -110), (640, 230, 14, 0, -40), (990, 1460, 36, 5, -80)]):
                c.body.append(f'<div class="sph" id="sp{k}" data-z="4" style="left:{x}px;top:{y}px;width:{r*2}px;height:{r*2}px;'
                              f'filter:blur({b}px);opacity:.85"></div>')
                self.js(f'tl.fromTo("#sp{k}",{{y:0}},{{y:{dy},duration:{c.dur:.3f},ease:"none"}},0);')

    # ------------------------------------------------------------ captions: lowercase words, key words in serif
    def captions(self):
        cfg = self.j.get('captions', {})
        if cfg is False:
            return
        cfg = cfg or {}
        c, T = self.c, self.T
        top = float(cfg.get('top', 1240))
        size = float(cfg.get('size', 66))
        keys = {bare(k) for k in cfg.get('keys', [])}
        hide = [self.window(e) for e in self.j.get('effects', []) if e.get('type') == 'takeover' and e.get('text')]
        c.css.append(f'''.cp{{position:absolute;left:90px;width:900px;top:{top:.0f}px;text-align:center;visibility:hidden;
  font:600 {size:.0f}px/1.08 'Inter';color:#fff;letter-spacing:-.025em;text-shadow:0 0 30px {T['glow']}aa,0 4px 18px rgba(0,0,0,.55)}}
.cp .w{{display:inline-block;margin:0 .1em}}
.cp .k{{font-family:'Instrument Serif',serif;font-style:italic;font-weight:400;font-size:1.22em;letter-spacing:-.01em;
  color:#fff;text-shadow:0 0 34px {T['glow']},0 4px 18px rgba(0,0,0,.5)}}''')
        gs = groups(self.j.words, int(cfg.get('maxw', 3)), int(cfg.get('maxc', 16)))
        for i, g in enumerate(gs):
            t0 = max(0, g[0][1] - 0.05)
            t1 = gs[i + 1][0][1] - 0.05 if i + 1 < len(gs) else c.dur
            if any(a <= t0 < b for a, b in hide):
                continue
            spans = ''.join(f'<span class="w{" k" if w in keys else ""}" id="cp{i}_{q}">{esc(w)}</span>' for q, (w, _) in enumerate(g))
            c.body.append(f'<div class="cp" id="cp{i}" data-z="40">{spans}</div>')
            self.js(f'tl.set("#cp{i}",{{visibility:"visible"}},{t0:.3f});tl.set("#cp{i}",{{visibility:"hidden"}},{t1:.3f});')
            for q, (w, t) in enumerate(g):
                self.js(f'tl.fromTo("#cp{i}_{q}",{{autoAlpha:0,y:22,filter:"blur(10px)"}},'
                        f'{{autoAlpha:1,y:0,filter:"blur(0px)",duration:.26,ease:"power3.out"}},{max(t0, t - 0.06):.3f});')

    # ------------------------------------------------------------ the effects
    def fx_takeover(self, e):
        """a full-screen glass world (rings, spheres) irises in over the speaker; the voice carries on"""
        T, i = self.T, self.uid('to')
        at, until = self.window(e, 2.4)
        rings = ''.join(f'<div class="ring" style="width:{w}px;height:{w*.62:.0f}px;opacity:{.9 - k*.12:.2f}"></div>'
                        for k, w in enumerate([360, 560, 780, 1020, 1280, 1560]))
        text = e.get('text')
        txt = (f'<div class="a tot" style="left:80px;right:80px;top:{float(e.get("text_y", 1080)):.0f}px;text-align:center;'
               f'font:500 84px/1.04 Inter;color:#fff;letter-spacing:-.03em;text-shadow:0 0 40px {T["glow"]}">{serif(text)}</div>') if text else ''
        kick = (f'<div class="a tok" style="left:0;right:0;top:{float(e.get("text_y", 1080)) - 70:.0f}px;text-align:center">'
                f'<span class="pill" style="display:inline-block;padding:10px 22px;border-radius:99px;font:600 28px Inter">{esc(e["kicker"])}</span></div>'
                ) if e.get('kicker') else ''
        self.add(f'<div id="{i}" style="inset:0;background:radial-gradient(90% 60% at 50% 46%,{T["mid"]} 0%,{T["deep"]} 70%);'
                 f'clip-path:circle(0% at 50% {self.eye:.0f}px);overflow:hidden">'
                 f'<div class="a" id="{i}r" style="left:0;top:{960 - 960:.0f}px;width:1080px;height:1920px">{rings}</div>'
                 f'<div class="sph" style="left:150px;top:520px;width:70px;height:70px;filter:blur(4px)"></div>'
                 f'<div class="sph" style="left:860px;top:700px;width:40px;height:40px"></div>'
                 f'<div class="sph" style="left:780px;top:1320px;width:90px;height:90px;filter:blur(7px)"></div>'
                 f'<div class="sph" style="left:210px;top:1240px;width:26px;height:26px"></div>{kick}{txt}</div>',
                 z=15 if (self.cut and e.get('keep_speaker', True)) else 25)
        self.js(f'tl.to("#{i}",{{clipPath:"circle(150% at 50% {self.eye:.0f}px)",duration:.7,ease:"power3.inOut"}},{at:.3f});')
        self.js(f'tl.fromTo("#{i}r",{{scale:.7,rotation:-6}},{{scale:1.08,rotation:4,duration:{until - at + .4:.3f},ease:"power1.out"}},{at:.3f});')
        if text:
            self.js(f'tl.fromTo("#{i} .tot",{{autoAlpha:0,y:40,filter:"blur(16px)"}},{{autoAlpha:1,y:0,filter:"blur(0px)",duration:.6,ease:"power3.out"}},{at + .35:.3f});')
        if kick:
            self.enter(f'#{i} .tok', at + .25)
        if until < self.c.dur - .06:
            self.js(f'tl.to("#{i}",{{clipPath:"circle(0% at 50% {self.eye:.0f}px)",duration:.55,ease:"power3.inOut"}},{until - .55:.3f});')

    def fx_halo_search(self, e):
        """a glowing search pill with orbit rings; an oversized cursor flies in and clicks it"""
        T, i = self.T, self.uid('hs')
        at, until = self.window(e, 2.6)
        y = float(e.get('y', 960))
        text = esc(e.get('text', 'search'))
        rings = ''.join(f'<div class="ring {i}g" style="width:{w}px;height:{w*.56:.0f}px;border-color:rgba(255,255,255,{.34 - k*.05:.2f})"></div>'
                        for k, w in enumerate([520, 700, 900, 1120]))
        self.add(f'<div id="{i}" style="left:0;top:{y - 300:.0f}px;width:1080px;height:600px">{rings}'
                 f'<div class="a" style="left:240px;top:250px;width:600px;height:100px;border-radius:99px;'
                 f'background:radial-gradient(closest-side,{T["glow"]}aa,transparent);filter:blur(30px)"></div>'
                 f'<div class="a" style="left:0;right:0;top:252px;text-align:center"><span class="pill" id="{i}p" '
                 f'style="display:inline-flex;align-items:center;gap:18px;padding:22px 46px;border-radius:99px;font:500 52px Inter;letter-spacing:-.02em">'
                 f'{text}{icon("arrow", 40, 2.4)}</span></div></div>', z=32)
        self.add(f'<div id="{i}c" style="left:1180px;top:{y + 380:.0f}px;filter:drop-shadow(0 12px 18px rgba(0,0,0,.45))">{CURSOR}</div>', z=45)
        self.enter(f'#{i}p', at, 'scale:.55,y:20')
        self.js(f'tl.fromTo(".{i}g",{{scale:.55,autoAlpha:0}},{{scale:1,autoAlpha:1,duration:.9,stagger:.09,ease:"power3.out"}},{at:.3f});')
        click = self.j.t(e.get('click_at'), at + 1.05)
        tip_x, tip_y = 540 + min(330, len(e.get('text', 'search')) * 14), y + 30
        self.js(f'tl.fromTo("#{i}c",{{x:0,y:0,autoAlpha:1}},{{x:{tip_x - 1180 - 8:.0f},y:{tip_y - (y + 380) - 6:.0f},duration:.7,ease:"power3.out"}},{click - .72:.3f});'
                f'tl.to("#{i}c",{{scale:.86,duration:.08,ease:"power2.in"}},{click:.3f});tl.to("#{i}c",{{scale:1,duration:.18,ease:"back.out(3)"}},{click + .08:.3f});'
                f'tl.to("#{i}p",{{scale:.93,duration:.08}},{click:.3f});tl.to("#{i}p",{{scale:1.04,duration:.28,ease:"back.out(3)"}},{click + .08:.3f});'
                f'tl.fromTo(".{i}g",{{scale:1}},{{scale:1.18,autoAlpha:.25,duration:.6,stagger:.05,ease:"power2.out"}},{click:.3f});')
        self.leave(f'#{i}', until, after=at)
        self.js(f'tl.to("#{i}c",{{x:"+=420",y:"+=360",duration:.4,ease:"power2.in"}},{max(click + .4, until - .4):.3f});')

    def fx_ribbon_wrap(self, e):
        """a glossy ribbon sweeps around the speaker (behind the body in the middle when there is a cutout)"""
        T, i = self.T, self.uid('rb')
        at, until = self.window(e, 2.8)
        y = float(e.get('y', self.eye + 260))
        d = f'M -180 {y + 360:.0f} C 200 {y - 120:.0f}, 420 {y + 300:.0f}, 640 {y + 60:.0f} S 960 {y - 420:.0f}, 1260 {y - 260:.0f}'
        txt = e.get('text', '')

        def svg(sid, mask=''):
            return (f'<div id="{sid}" style="left:0;top:0;width:1080px;height:1920px"><svg width="1080" height="1920" viewBox="0 0 1080 1920">'
                    f'<defs><linearGradient id="{sid}gr" x1="0" x2="1"><stop offset="0" stop-color="{T["mid"]}"/>'
                    f'<stop offset=".35" stop-color="{T["accent"]}"/><stop offset=".55" stop-color="#fff"/>'
                    f'<stop offset=".7" stop-color="{T["accent2"]}"/><stop offset="1" stop-color="{T["accent"]}"/></linearGradient>'
                    f'<mask id="{sid}m"><rect width="1080" height="1920" fill="#fff"/>{mask}</mask>'
                    f'<path id="{sid}p" d="{d}"/></defs><g mask="url(#{sid}m)">'
                    f'<use href="#{sid}p" class="{i}s" fill="none" stroke="{T["glow"]}" stroke-width="150" stroke-linecap="round" opacity=".45" style="filter:blur(30px)"/>'
                    f'<use href="#{sid}p" class="{i}s" fill="none" stroke="url(#{sid}gr)" stroke-width="86" stroke-linecap="round"/>'
                    f'<use href="#{sid}p" class="{i}s" fill="none" stroke="#fff" stroke-width="7" stroke-linecap="round" opacity=".75" transform="translate(0,-24)"/>'
                    + (f'<text dy="18" style="font:italic 400 60px \'Instrument Serif\';fill:{T["ink"]}"><textPath href="#{sid}p" class="{i}t" startOffset="8%">{esc(txt)}</textPath></text>' if txt else '')
                    + '</g></svg></div>')
        if self.cut:
            self.add(svg(i + 'b'), z=12)
            self.add(svg(i + 'f', '<rect x="330" y="0" width="420" height="1920" fill="#000"/>'), z=34)
            sels = f'["#{i}b","#{i}f"]'
        else:
            self.add(svg(i + 'f'), z=34)
            sels = f'"#{i}f"'
        self.js(f'tl.fromTo(".{i}s",{{strokeDasharray:2400,strokeDashoffset:2400}},{{strokeDashoffset:0,duration:1.0,ease:"power2.inOut"}},{at:.3f});')
        self.js(f'tl.fromTo({sels},{{autoAlpha:0}},{{autoAlpha:1,duration:.15}},{at:.3f});')
        if txt:
            self.js(f'tl.fromTo(".{i}t",{{attr:{{startOffset:"-30%"}}}},{{attr:{{startOffset:"34%"}},duration:{until - at:.3f},ease:"power1.out"}},{at:.3f});')
        if until < self.c.dur - .06:
            self.js(f'tl.to(".{i}s",{{strokeDashoffset:-2400,duration:.6,ease:"power2.in"}},{until - .6:.3f});'
                    f'tl.to({sels},{{autoAlpha:0,duration:.2}},{until - .1:.3f});')

    def card_html(self, k, w, h):
        T = self.T
        if k.get('image'):
            img = self.j.images(k['image'])[0]
            lab = (f'<div class="a" style="left:14px;bottom:14px"><span class="pill" style="display:inline-block;padding:7px 14px;border-radius:99px;'
                   f'font:600 {w*.075:.0f}px Inter">{esc(k["label"])}</span></div>') if k.get('label') else ''
            return (f'<div class="gl" style="width:{w}px;height:{h}px;border-radius:{w*.1:.0f}px;padding:10px">'
                    f'<div style="position:relative;width:100%;height:100%;border-radius:{w*.08:.0f}px;overflow:hidden;'
                    f'background:url({self.c.asset(img)}) center/cover">{lab}</div></div>')
        ic = f'<div class="ico gl" style="width:{w*.26:.0f}px;height:{w*.26:.0f}px">{icon(k["icon"], w*.13)}</div>' if k.get('icon') else ''
        return (f'<div class="gl" style="width:{w}px;height:{h}px;border-radius:{w*.1:.0f}px;padding:{w*.09:.0f}px;display:flex;flex-direction:column;'
                f'justify-content:space-between;color:#fff">{ic}<div><div style="font:500 {w*.15:.0f}px/1.02 Inter;letter-spacing:-.03em">{serif(k.get("text", ""))}</div>'
                f'<div style="margin-top:10px;font:500 {w*.065:.0f}px Inter;opacity:.7">{esc(k.get("sub", ""))}</div></div></div>')

    def fx_falling_cards(self, e):
        """glass cards drop in from above and land fanned out"""
        i = self.uid('fc')
        at, until = self.window(e, 3.0)
        items = e.get('cards') or []
        if not items:
            sys.exit('falling_cards needs "cards"')
        n = min(len(items), 5)
        y = float(e.get('y', 300))
        w, h = (300, 380) if n <= 3 else (250, 320)
        span = min(760, (n - 1) * (w * .78))
        for q, k in enumerate(items[:n]):
            cx = 540 + (q - (n - 1) / 2) * (span / max(1, n - 1))
            rot = (q - (n - 1) / 2) * 7
            dy = abs(q - (n - 1) / 2) * 26
            self.add(f'<div id="{i}_{q}" class="{i}" style="left:{cx - w/2:.0f}px;top:{y + dy:.0f}px">{self.card_html(k, w, h)}</div>', z=33 + (q % 2))
            t = self.j.t(k.get('at'), at + q * .12)
            self.js(f'tl.fromTo("#{i}_{q}",{{y:{-y - h - 80:.0f},rotation:{rot * 3 - 25:.0f},autoAlpha:1}},'
                    f'{{y:0,rotation:{rot:.0f},duration:.62,ease:"back.out(1.25)"}},{t:.3f});')
        self.leave(f'.{i}', until, after=at)

    def fx_social_orbit(self, e):
        """icon bubbles orbit the head on a tilted ring, passing behind it when there is a cutout"""
        i = self.uid('so')
        at, until = self.window(e, 3.2)
        names = e.get('icons') or ['instagram', 'tiktok', 'youtube', 'heart', 'message']
        cx, cy = 540, float(e.get('y', self.eye - 30))
        rx, ry = float(e.get('rx', 400)), float(e.get('ry', 110))
        ids = []
        for q, name in enumerate(names[:7]):
            img = None
            if str(name).lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                img = self.j.images(name)[0]
            inner = (f'<div style="width:112px;height:112px;border-radius:50%;background:url({self.c.asset(img)}) center/cover"></div>'
                     if img else icon(name, 50, 2.1))
            lit = (f'background:radial-gradient(circle at 35% 30%,{self.T["accent2"]},{self.T["accent"]} 62%);'
                   f'box-shadow:0 0 36px {self.T["glow"]},inset 0 1.5px 0 rgba(255,255,255,.6);') if q % 2 == 0 and not img else ''
            self.add(f'<div id="{i}_{q}" style="left:{cx - 63:.0f}px;top:{cy - 63:.0f}px"><div class="ico gl {i}b" '
                     f'style="width:126px;height:126px;padding:7px;{lit}">{inner}</div></div>', z=30)
            ids.append(f'{i}_{q}')
        n = len(ids)
        turn = float(e.get('turns', .55))
        self.js(f'''(function(){{const o={{a:0}};const els={json.dumps(ids)}.map(id=>document.getElementById(id));
const place=()=>{{els.forEach((el,k)=>{{const a=o.a*Math.PI*2+k*Math.PI*2/{n}-Math.PI/2;const s=Math.sin(a);
el.style.transform=`translate(${{Math.cos(a)*{rx}}}px,${{s*{ry}-Math.cos(a)*24}}px) scale(${{.72+.28*(s+1)/2}})`;
el.style.zIndex=s>0?36:{'11' if self.cut else '29'};el.style.opacity=.55+.45*(s+1)/2;}});}};
place();tl.to(o,{{a:{turn},duration:{until - at:.3f},ease:"power1.inOut",onUpdate:place}},{at:.3f});}})();''')
        self.js(f'tl.fromTo(".{i}b",{{scale:0,autoAlpha:0}},{{scale:1,autoAlpha:1,duration:.45,stagger:.07,ease:"back.out(2.2)"}},{at:.3f});')
        self.leave(f'.{i}b', until, after=at)

    def fx_quote_note(self, e):
        """a frosted note with a small label and a serif quote that writes itself in"""
        T, i = self.T, self.uid('qn')
        at, until = self.window(e, 3.0)
        y = float(e.get('y', 280))
        words = str(e.get('text', '')).split()
        quote = ' '.join(f'<span class="{i}w" style="display:inline-block">{serif(w)}</span>' for w in words)
        by = f'<div style="margin-top:18px;font:500 26px Inter;opacity:.65">— {esc(e["by"])}</div>' if e.get('by') else ''
        self.add(f'<div id="{i}" class="gl" style="left:150px;top:{y:.0f}px;width:780px;border-radius:40px;padding:34px 42px 38px;color:#fff">'
                 f'<div style="display:flex;align-items:center;gap:12px;font:600 24px Inter;letter-spacing:.14em;text-transform:uppercase;opacity:.75">'
                 f'<i style="width:12px;height:12px;border-radius:50%;background:{T["accent2"]};box-shadow:0 0 14px {T["glow"]}"></i>{esc(e.get("label", "note"))}</div>'
                 f'<div style="margin-top:16px;font:400 64px/1.06 \'Instrument Serif\';font-style:italic;letter-spacing:-.01em">{quote}</div>{by}</div>', z=35)
        self.enter(f'#{i}', at, 'y:-40,rotationX:30,transformPerspective:900')
        self.js(f'tl.fromTo(".{i}w",{{autoAlpha:0,y:16,filter:"blur(8px)"}},{{autoAlpha:1,y:0,filter:"blur(0px)",duration:.3,stagger:{min(.12, 1.2 / max(1, len(words))):.3f},ease:"power2.out"}},{at + .25:.3f});')
        self.leave(f'#{i}', until, after=at)

    def fx_icon_pop(self, e):
        """round glass icon chips pop on the words that name them, joined by a drawn line"""
        T, i = self.T, self.uid('ip')
        items = e.get('items') or []
        if not items:
            sys.exit('icon_pop needs "items"')
        at, until = self.window({**e, 'at': e.get('at', items[0].get('at'))}, 2.8)
        y = float(e.get('y', 1336))
        n = len(items[:4])
        gap = 260 if n <= 3 else 220
        xs = [540 + (q - (n - 1) / 2) * gap for q in range(n)]
        if n > 1:
            self.add(f'<div id="{i}l" style="left:{xs[0]:.0f}px;top:{y + 47:.0f}px;width:{xs[-1] - xs[0]:.0f}px;height:3px;'
                     f'background:linear-gradient(90deg,transparent,rgba(255,255,255,.75),transparent);transform-origin:left center"></div>', z=34)
            self.js(f'tl.fromTo("#{i}l",{{scaleX:0,autoAlpha:1}},{{scaleX:1,duration:.6,ease:"power2.inOut"}},{at:.3f});')
        for q, k in enumerate(items[:4]):
            t = self.j.t(k.get('at'), at + q * .35)
            hot = k.get('hot', q == n - 1)
            bg = f'background:radial-gradient(circle at 35% 30%,{T["accent2"]},{T["accent"]} 60%);border:1.5px solid rgba(255,255,255,.6)' if hot else ''
            lab = (f'<div style="margin-top:12px;text-align:center"><span class="pill" style="display:inline-block;padding:6px 16px;'
                   f'border-radius:99px;font:600 24px Inter">{esc(k["label"])}</span></div>') if k.get('label') else ''
            self.add(f'<div id="{i}_{q}" class="{i}" style="left:{xs[q] - 90:.0f}px;top:{y:.0f}px;width:180px;display:flex;flex-direction:column;align-items:center">'
                     f'<div class="ico gl" style="width:96px;height:96px;{bg}">{icon(k.get("icon", "check"), 44, 2.4)}</div>{lab}</div>', z=35)
            self.js(f'tl.fromTo("#{i}_{q}",{{scale:0,rotation:-25,autoAlpha:0}},{{scale:1,rotation:0,autoAlpha:1,duration:.5,ease:"back.out(2.6)"}},{t:.3f});')
        self.leave(f'.{i}', until, after=at)
        if n > 1:
            self.leave(f'#{i}l', until, after=at)

    def fx_typing_search(self, e):
        """a glass search bar types the query letter by letter; results slide in under it"""
        T, i = self.T, self.uid('ts')
        at, until = self.window(e, 3.0)
        y = float(e.get('y', 300))
        q = str(e.get('text', ''))
        res = e.get('results') or []
        rows = ''.join(f'<div class="{i}r gl" style="margin-top:14px;display:flex;align-items:center;gap:18px;padding:18px 26px;border-radius:26px;'
                       f'font:500 34px Inter;color:#fff">{icon(r.get("icon", "search") if isinstance(r, dict) else "search", 30, 2.2)}'
                       f'<span>{serif(r.get("text", "") if isinstance(r, dict) else r)}</span></div>' for r in res[:3])
        self.add(f'<div id="{i}" style="left:120px;top:{y:.0f}px;width:840px">'
                 f'<div class="gl" style="display:flex;align-items:center;gap:20px;padding:26px 32px;border-radius:99px;color:#fff">'
                 f'{icon("search", 40, 2.4)}<span id="{i}q" style="font:500 44px Inter;letter-spacing:-.02em;white-space:nowrap"></span>'
                 f'<span id="{i}k" style="width:4px;height:48px;background:{T["accent2"]};border-radius:2px"></span></div>{rows}</div>', z=36)
        self.enter(f'#{i}', at, 'y:-30,scale:.9')
        tdur = float(e.get('type_for', min(1.4, .07 * len(q) + .2)))
        self.js(f'''(function(){{const s={json.dumps(q)};const o={{n:0}};const el=document.getElementById("{i}q");
tl.to(o,{{n:s.length,duration:{tdur:.3f},ease:"none",onUpdate:()=>{{el.textContent=s.slice(0,Math.round(o.n));}}}},{at + .25:.3f});}})();''')
        blinks = int((until - at) / .5)
        for b in range(blinks):
            self.js(f'tl.set("#{i}k",{{autoAlpha:{b % 2}}},{at + .25 + tdur + b * .5:.3f});')
        if rows:
            self.js(f'tl.fromTo(".{i}r",{{autoAlpha:0,y:-24,filter:"blur(10px)"}},{{autoAlpha:1,y:0,filter:"blur(0px)",duration:.4,stagger:.1,ease:"power3.out"}},{at + .35 + tdur:.3f});')
        self.leave(f'#{i}', until, after=at)

    def fx_film_strip(self, e):
        """a tilted film strip of frames slides across the top"""
        i = self.uid('fs')
        at, until = self.window(e, 3.0)
        imgs = self.j.images(e.get('images'))
        texts = e.get('texts') or []
        if not imgs and not texts:
            sys.exit('film_strip needs "images" or "texts"')
        y = float(e.get('y', 330))
        frames = []
        items = [('i', p) for p in imgs] + [('t', t) for t in texts]
        while len(items) < 6:
            items = items + items
        for kind, v in items[:8]:
            if kind == 'i':
                frames.append(f'<div style="flex:none;width:250px;height:190px;border-radius:10px;background:url({self.c.asset(v)}) center/cover"></div>')
            else:
                frames.append(f'<div style="flex:none;width:250px;height:190px;border-radius:10px;display:flex;align-items:center;justify-content:center;'
                              f'background:linear-gradient(160deg,{self.T["mid"]},{self.T["deep"]});font:500 40px/1 Inter;color:#fff;text-align:center;padding:12px">{serif(v)}</div>')
        holes = 'repeating-linear-gradient(90deg,transparent 0 16px,rgba(255,255,255,.85) 16px 34px,transparent 34px 50px)'
        self.add(f'<div id="{i}" style="left:-260px;top:{y:.0f}px;width:2400px;height:270px;transform:rotate(-6deg);'
                 f'background:#0b0b10;border-top:1px solid rgba(255,255,255,.2);border-bottom:1px solid rgba(255,255,255,.2);box-shadow:0 30px 70px rgba(0,0,0,.6)">'
                 f'<div class="a" style="left:0;right:0;top:9px;height:14px;background:{holes};opacity:.8;border-radius:3px"></div>'
                 f'<div class="a" style="left:0;right:0;bottom:9px;height:14px;background:{holes};opacity:.8;border-radius:3px"></div>'
                 f'<div id="{i}r" class="a" style="left:0;top:40px;display:flex;gap:18px">{"".join(frames)}</div></div>', z=33)
        self.js(f'tl.fromTo("#{i}",{{x:1300,autoAlpha:0}},{{x:0,autoAlpha:1,duration:.75,ease:"power4.out"}},{at:.3f});'
                f'tl.fromTo("#{i}r",{{x:0}},{{x:-420,duration:{until - at:.3f},ease:"none"}},{at:.3f});')
        if until < self.c.dur - .06:
            self.js(f'tl.to("#{i}",{{x:-1500,autoAlpha:0,duration:.5,ease:"power3.in"}},{until - .5:.3f});')

    def fx_chrome_title(self, e):
        """one huge chrome word; behind the head when there is a cutout"""
        i = self.uid('ct')
        at, until = self.window(e, 2.6)
        word = str(e.get('text', '')).upper()
        size = float(e.get('size') or min(330, 900 / max(1, len(word) * .5)))
        y = float(e.get('y', self.eye - size * .95))
        # the gradient goes on every letter: background-clip:text does not reach children that animate on their own layer
        letters = ''.join(f'<span class="{i}c chrome" style="display:inline-block">{esc(ch) if ch != " " else "&nbsp;"}</span>' for ch in word)
        self.add(f'<div id="{i}" style="left:0;width:1080px;top:{y:.0f}px;text-align:center;filter:drop-shadow(0 12px 28px rgba(0,0,0,.6))">'
                 f'<div id="{i}w" style="display:inline-block;font-size:{size:.0f}px;line-height:.9">{letters}</div></div>', z=12 if self.cut else 31)
        self.js(f'tl.fromTo(".{i}c",{{autoAlpha:0,y:90,scale:1.35,filter:"blur(14px)"}},{{autoAlpha:1,y:0,scale:1,filter:"blur(0px)",duration:.55,stagger:.035,ease:"power3.out"}},{at:.3f});'
                f'tl.fromTo("#{i}w",{{scale:1}},{{scale:1.06,duration:{until - at:.3f},ease:"none"}},{at:.3f});')
        if e.get('sub'):
            self.add(f'<div id="{i}s" style="left:0;width:1080px;top:{y + size * .93:.0f}px;text-align:center">'
                     f'<span class="pill" style="display:inline-block;padding:8px 20px;border-radius:12px;font:700 30px Inter;letter-spacing:.04em;'
                     f'text-transform:uppercase">{esc(e["sub"])}</span></div>', z=36)
            sat = self.j.t(e.get('sub_at'), at + .45)
            self.enter(f'#{i}s', sat)
            self.leave(f'#{i}s', until, after=sat)
        self.leave(f'#{i}', until, after=at)

    def fx_glass_card(self, e):
        """a frosted panel with a title, a line under it and a little input bar"""
        T, i = self.T, self.uid('gc')
        at, until = self.window(e, 3.0)
        y = float(e.get('y', 270))
        side = e.get('side', 'left')
        x = 110 if side == 'left' else (1080 - 110 - 560 if side == 'right' else 260)
        bar = (f'<div style="margin-top:22px;display:flex;align-items:center;gap:12px;padding:12px 14px 12px 22px;border-radius:99px;'
               f'background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.25);font:500 24px Inter;opacity:.9">'
               f'<span style="flex:1">{esc(e["bar"])}</span><span class="ico" style="width:44px;height:44px;background:{T["accent"]}">'
               f'{icon(e.get("bar_icon", "arrow"), 22, 2.6)}</span></div>') if e.get('bar') else ''
        self.add(f'<div id="{i}" class="gl" style="left:{x}px;top:{y:.0f}px;width:560px;border-radius:38px;padding:34px 34px 30px;color:#fff">'
                 f'<div style="font:500 56px/1.02 Inter;letter-spacing:-.035em">{serif(e.get("title", ""))}</div>'
                 + (f'<div style="margin-top:12px;font:500 26px/1.3 Inter;opacity:.68">{esc(e["sub"])}</div>' if e.get('sub') else '')
                 + f'{bar}</div>', z=35)
        self.enter(f'#{i}', at, f'x:{-60 if side == "left" else 60},rotationY:{-25 if side == "left" else 25},transformPerspective:1000')
        self.leave(f'#{i}', until, after=at)

    def fx_checklist(self, e):
        """numbered glass rows that tick off as each is said"""
        T, i = self.T, self.uid('cl')
        items = e.get('items') or []
        if not items:
            sys.exit('checklist needs "items"')
        at, until = self.window({**e, 'at': e.get('at', items[0].get('at'))}, 3.2)
        y = float(e.get('y', 290))
        rows = ''
        for q, k in enumerate(items[:4]):
            rows += (f'<div id="{i}_{q}" class="gl" style="display:flex;align-items:center;gap:22px;margin-top:{0 if q == 0 else 16}px;padding:20px 24px;'
                     f'border-radius:28px;color:#fff"><span style="font:600 26px Inter;opacity:.55;width:40px">{q + 1:02d}</span>'
                     f'<span style="flex:1;font:500 40px Inter;letter-spacing:-.02em">{serif(k.get("text", ""))}</span>'
                     f'<span id="{i}_{q}c" class="ico" style="width:58px;height:58px;border:2px solid rgba(255,255,255,.45)">'
                     f'<svg viewBox="0 0 24 24" width="30" height="30" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">'
                     f'<path id="{i}_{q}k" d="M5 12.5l4.5 4.5L19 7" stroke-dasharray="24" stroke-dashoffset="24"/></svg></span></div>')
        self.add(f'<div id="{i}" style="left:150px;top:{y:.0f}px;width:780px">{rows}</div>', z=35)
        for q, k in enumerate(items[:4]):
            t = self.j.t(k.get('at'), at + q * .5)
            tick = self.j.t(k.get('done_at'), t + .35)
            self.enter(f'#{i}_{q}', t, 'x:-50,scale:.9', .45, 'power3.out')
            self.js(f'tl.to("#{i}_{q}c",{{background:"{T["accent"]}",borderColor:"{T["accent2"]}",boxShadow:"0 0 28px {T["glow"]}",duration:.2}},{tick:.3f});'
                    f'tl.fromTo("#{i}_{q}c",{{scale:.7}},{{scale:1,duration:.4,ease:"back.out(3)"}},{tick:.3f});'
                    f'tl.to("#{i}_{q}k",{{strokeDashoffset:0,duration:.28,ease:"power2.out"}},{tick + .05:.3f});')
        self.leave(f'#{i}', until, after=at)

    # ------------------------------------------------------------ build
    def build(self):
        self.base()
        for e in self.j.get('effects') or []:
            t = e.get('type', '')
            fn = getattr(self, f'fx_{t}', None)
            if not fn:
                sys.exit(f'effect "{t}" is not one of: ' + ', '.join(k[3:] for k in dir(self) if k.startswith('fx_')))
            fn(e)
        self.captions()
        # z order: every top-level layer carries data-z
        out = []
        for b in self.c.body:
            if 'data-z="' in b:
                z = b.split('data-z="', 1)[1].split('"', 1)[0]
                b = b.replace(f'data-z="{z}" ', '', 1).replace(f' data-z="{z}"', '', 1)
                if ' style="' in b.split('>', 1)[0]:
                    b = b.replace(' style="', f' style="position:absolute;z-index:{z};', 1)
                else:
                    b = b.replace('<div ', f'<div style="position:absolute;z-index:{z}" ', 1)
            out.append(b)
        self.c.body = out
        self.j.finish(self.c)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    Reel(sys.argv[1]).build()
