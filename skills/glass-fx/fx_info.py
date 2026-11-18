"""Animated infographics in the "max.vfx" creator style, in premium dark blue (or any accent): a glowing glossy
number, glossy pill badges, choice cards with arrows, a full-screen card with a big glowing glyph, a full-screen
line chart that draws itself, and a persistent name bar with a verified tick.

A mixin for build.Reel, like fx_editorial.EditorialFX. Numbers on charts are never invented: the chart shows a
direction (up / flat / down) and the words the speaker says.
"""
import html
import math
import random

NAVY = dict(hi='#8fb3ff', top='#4f7dff', mid='#1f4fd6', low='#0b2a7a', glow='#3d7bff', deep='#040b24')


def esc(s):
    return html.escape(str(s))


def hl(s):
    """*word* -> premium highlight box"""
    s = esc(s)
    out, on = '', False
    for part in s.split('*'):
        out += f'<span class="hlk">{part}</span>' if on else part
        on = not on
    return out


TICK = ('<svg viewBox="0 0 40 40" width="{s}" height="{s}" style="vertical-align:-.12em"><path fill="#3897f0" d="{p}"/>'
        '<path d="M12.5 20.5l5 5 10-11" fill="none" stroke="#fff" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"/></svg>')


def tick_path():
    pts = []
    for k in range(32):
        a = k * math.pi / 16
        r = 19 if k % 2 == 0 else 16.6
        pts.append(f'{20 + r * math.cos(a):.2f} {20 + r * math.sin(a):.2f}')
    return 'M' + ' L'.join(pts) + 'Z'


class InfoFX:
    def info_css(self):
        if getattr(self, '_info_css', False):
            return
        self._info_css = True
        N = NAVY
        self.c.css.append(f'''
.hlk{{display:inline-block;color:#fff;padding:0 .2em .04em;margin:0 .04em;border-radius:.2em;
  background:linear-gradient(180deg,{N['top']} 0%,{N['mid']} 48%,{N['low']} 100%);
  box-shadow:0 0 26px {N['glow']}99,inset 0 2px 0 rgba(255,255,255,.45),inset 0 -6px 12px rgba(0,8,40,.35)}}
.npill{{display:inline-flex;align-items:center;gap:.28em;white-space:nowrap;color:#fff;border-radius:999px;padding:.16em .62em .2em;
  background:linear-gradient(180deg,{N['hi']} 0%,{N['top']} 18%,{N['mid']} 52%,{N['low']} 100%);border:2px solid rgba(255,255,255,.6);
  box-shadow:0 0 44px {N['glow']},0 0 90px {N['glow']}66,0 22px 40px rgba(0,0,0,.5),inset 0 4px 0 rgba(255,255,255,.55),inset 0 -12px 22px rgba(0,6,40,.45);
  text-shadow:0 2px 10px rgba(0,10,60,.55);font-weight:800;letter-spacing:-.02em}}
.gnum{{font:800 1em/1 Inter;letter-spacing:-.06em;color:transparent;
  background:linear-gradient(180deg,#ffffff 0%,{N['hi']} 22%,{N['top']} 48%,{N['mid']} 70%,{N['low']} 100%);-webkit-background-clip:text;background-clip:text}}
.dglass{{background:linear-gradient(160deg,rgba(255,255,255,.10),rgba(255,255,255,.03));border:1.5px solid rgba(255,255,255,.14);
  box-shadow:0 30px 70px rgba(0,0,0,.55),inset 0 1px 0 rgba(255,255,255,.18)}}''')

    # ------------------------------------------------------------ the persistent name bar
    def info_bar(self):
        cfg = self.j.get('info_bar')
        if not cfg:
            return
        self.info_css()
        y = float(cfg.get('y', 1440))
        tick = TICK.format(s=34, p=tick_path()) if cfg.get('verified', True) else ''
        self.c.body.append(
            f'<div id="ibar" data-z="42" style="left:0;width:1080px;top:{y:.0f}px;text-align:center">'
            f'<span style="display:inline-flex;align-items:center;gap:12px;padding:12px 28px;border-radius:999px;background:rgba(6,12,30,.62);'
            f'border:1px solid rgba(255,255,255,.16);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);box-shadow:0 14px 34px rgba(0,0,0,.4);'
            f'font:600 30px Inter;color:#fff;white-space:nowrap"><b style="font-weight:800">{esc(cfg.get("name", ""))}</b>{tick}'
            f'<span style="opacity:.55">•</span><span style="opacity:.88">{esc(cfg.get("role", ""))}</span></span></div>')
        self.js(f'tl.fromTo("#ibar",{{autoAlpha:0,y:40}},{{autoAlpha:1,y:0,duration:.6,ease:"expo.out"}},{float(cfg.get("at", .35)):.3f});')

    # ------------------------------------------------------------ glowing number + two lines
    def fx_glow_number(self, e):
        self.info_css()
        i = self.uid('gn')
        at, until = self.window(e, 2.6)
        y = float(e.get('y', 360))
        size = float(e.get('size', 400))
        lines = e.get('lines') or []
        rows = ''.join(f'<div class="{i}l" style="font:800 {float(e.get("line_size", 58)):.0f}px/1.08 Inter;color:#fff;letter-spacing:-.03em;'
                       f'text-shadow:0 4px 18px rgba(0,0,0,.6);white-space:nowrap">{hl(l)}</div>' for l in lines)
        self.add(f'<div id="{i}" style="{self.band(e, "left")};top:{y:.0f}px">'
                 f'<div id="{i}n" style="position:relative;display:inline-block;font-size:{size:.0f}px;filter:drop-shadow(0 0 40px {NAVY["glow"]}) drop-shadow(0 20px 30px rgba(0,0,0,.55))">'
                 f'<span class="gnum">{esc(e.get("text", "1"))}</span></div><div style="margin-top:-{size * .1:.0f}px">{rows}</div></div>', z=36)
        self.js(f'tl.fromTo("#{i}n",{{autoAlpha:0,scale:.35,rotationY:-60,filter:"blur(20px) drop-shadow(0 0 0px {NAVY["glow"]})"}},'
                f'{{autoAlpha:1,scale:1,rotationY:0,filter:"blur(0px) drop-shadow(0 0 40px {NAVY["glow"]})",duration:.8,ease:"expo.out"}},{at:.3f});'
                f'tl.fromTo("#{i}n",{{y:0}},{{y:-14,duration:{max(.4, until - at - .8):.3f},ease:"sine.inOut"}},{at + .8:.3f});'
                f'tl.fromTo(".{i}l",{{autoAlpha:0,x:-40,filter:"blur(10px)"}},{{autoAlpha:1,x:0,filter:"blur(0px)",duration:.5,stagger:.18,ease:"expo.out"}},{at + .3:.3f});')
        self.leave(f'#{i}', until, after=at + .8)

    # ------------------------------------------------------------ glossy pill badge
    def fx_neon_pill(self, e):
        self.info_css()
        i = self.uid('np')
        at, until = self.window(e, 2.2)
        y = float(e.get('y', 520))
        over = (f'<div class="{i}o" style="font:800 {float(e.get("over_size", 46)):.0f}px/1.1 Inter;color:#fff;letter-spacing:-.02em;margin-bottom:18px;text-shadow:0 4px 16px rgba(0,0,0,.6)">'
                f'{hl(e["over"])}</div>') if e.get('over') else ''
        ico = self.icon_svg(e['icon']) if e.get('icon') else ''
        self.add(f'<div id="{i}" style="{self.band(e, "left")};top:{y:.0f}px">{over}'
                 f'<span id="{i}p" class="npill" style="font:800 {float(e.get("size", 92)):.0f}px/1 Inter">{ico}{esc(e.get("text", ""))}</span></div>', z=37)
        if over:
            self.js(f'tl.fromTo("#{i} .{i}o",{{autoAlpha:0,y:20}},{{autoAlpha:1,y:0,duration:.4,ease:"power3.out"}},{at:.3f});')
        pa = self.j.t(e.get('pill_at'), at + (.25 if over else 0))
        self.js(f'tl.fromTo("#{i}p",{{autoAlpha:0,scale:.3,rotation:-8}},{{autoAlpha:1,scale:1,rotation:0,duration:.55,ease:"back.out(2.2)"}},{pa:.3f});'
                f'tl.to("#{i}p",{{scale:1.05,duration:.5,ease:"sine.inOut",yoyo:true,repeat:1}},{pa + .6:.3f});')
        self.leave(f'#{i}', until, after=pa)

    def icon_svg(self, name, size='.8em'):
        paths = {'up': '<path d="M4 18l6-6 4 4 7-8"/><path d="M15 8h6v6"/>', 'flat': '<path d="M3 12h18"/><path d="M15 6l6 6-6 6"/>',
                 'down': '<path d="M4 6l6 6 4-4 7 8"/><path d="M15 16h6v-6"/>', 'message': '<path d="M21 12a8.5 8.5 0 0 1-12.3 7.6L3.5 21l1.6-4.9A8.5 8.5 0 1 1 21 12z"/>',
                 'check': '<path d="M5 12.5l4.5 4.5L19 7"/>', 'question': '<path d="M9.2 9a3 3 0 1 1 4.1 2.8c-.8.4-1.3 1.1-1.3 2v.7"/><path d="M12 18h.01"/>'}
        return (f'<svg viewBox="0 0 24 24" width="{size}" height="{size}" fill="none" stroke="#fff" stroke-width="2.6" stroke-linecap="round" '
                f'stroke-linejoin="round">{paths.get(name, paths["check"])}</svg>')

    # ------------------------------------------------------------ choice cards with arrows
    def fx_choice_cards(self, e):
        self.info_css()
        i = self.uid('cc')
        items = e.get('items') or []
        at, until = self.window({**e, 'at': e.get('at', items[0].get('at') if items else 0)}, 3.0)
        y = float(e.get('y', 420))
        rows = ''
        for k, it in enumerate(items[:3]):
            rows += (f'<div id="{i}_{k}" class="dglass" style="display:flex;align-items:center;gap:22px;margin-top:{0 if k == 0 else 18}px;padding:18px 26px 18px 18px;'
                     f'border-radius:30px;color:#fff;backdrop-filter:blur(14px)"><span class="npill" style="font-size:44px;padding:.28em">'
                     f'{self.icon_svg(it.get("icon", "check"), "1em")}</span><span style="font:800 46px/1.05 Inter;letter-spacing:-.025em">{hl(it.get("text", ""))}</span></div>')
        self.add(f'<div id="{i}" style="{self.band(e, "left")};top:{y:.0f}px;text-align:left">{rows}</div>', z=36)
        for k, it in enumerate(items[:3]):
            t = self.j.t(it.get('at'), at + k * .5)
            self.js(f'tl.fromTo("#{i}_{k}",{{autoAlpha:0,x:-80,filter:"blur(12px)"}},{{autoAlpha:1,x:0,filter:"blur(0px)",duration:.55,ease:"expo.out"}},{t:.3f});')
        self.leave(f'#{i}', until, after=at + .6)

    # ------------------------------------------------------------ full-screen cards
    def _card_shell(self, i, inner):
        N = NAVY
        rnd = random.Random(7)
        dots = ''.join(f'<i style="position:absolute;left:{rnd.uniform(0, 1080):.0f}px;top:{rnd.uniform(0, 1920):.0f}px;width:{s}px;height:{s}px;border-radius:50%;'
                       f'background:#fff;opacity:{rnd.uniform(.08, .35):.2f}"></i>' for s in [2] * 40 + [3] * 10)
        return (f'<div id="{i}" style="inset:0;overflow:hidden;background:radial-gradient(80% 55% at 50% 42%,#0c1d55 0%,{N["deep"]} 62%,#01040f 100%)">'
                f'<div class="a" style="inset:0;background-image:radial-gradient(rgba(255,255,255,.07) 1.5px,transparent 1.5px);background-size:44px 44px;'
                f'-webkit-mask:radial-gradient(70% 60% at 50% 45%,#000,transparent);mask:radial-gradient(70% 60% at 50% 45%,#000,transparent)"></div>'
                f'<div class="a {i}d" style="inset:0">{dots}</div>{inner}</div>')

    def _card_in_out(self, i, at, until, enter=.45):
        self.js(f'tl.fromTo("#{i}",{{autoAlpha:0,scale:1.08,filter:"blur(18px)"}},{{autoAlpha:1,scale:1,filter:"blur(0px)",duration:{enter:.2f},ease:"expo.out"}},{at:.3f});'
                f'tl.fromTo("#{i} .{i}d",{{y:0}},{{y:-60,duration:{max(.5, until - at):.3f},ease:"none"}},{at:.3f});')
        if until < self.c.dur - .06:
            self.js(f'tl.to("#{i}",{{autoAlpha:0,scale:.96,filter:"blur(14px)",duration:.35,ease:"power2.in"}},{max(at + .8, until - .35):.3f});')

    def fx_icon_card(self, e):
        """a full-screen dark card with one big glowing glyph (default "?") and a title"""
        self.info_css()
        i = self.uid('ic')
        at, until = self.window(e, 2.0)
        g = esc(e.get('glyph', '?'))
        inner = (f'<div class="a" style="left:0;right:0;top:{float(e.get("glyph_y", 470)):.0f}px;text-align:center">'
                 f'<span id="{i}g" style="display:inline-block;font-size:{float(e.get("glyph_size", 560)):.0f}px;'
                 f'filter:drop-shadow(0 0 50px {NAVY["glow"]}) drop-shadow(0 30px 40px rgba(0,0,0,.6))"><span class="gnum">{g}</span></span></div>'
                 f'<div class="a {i}t" style="left:60px;right:60px;top:{float(e.get("title_y", 1110)):.0f}px;text-align:center;font:800 76px/1.1 Inter;'
                 f'color:#fff;letter-spacing:-.03em;text-shadow:0 6px 24px rgba(0,0,0,.6)">{hl(e.get("title", ""))}</div>')
        self.add(self._card_shell(i, inner), z=38)
        self._card_in_out(i, at, until, float(e.get('enter_for', .45)))
        self.js(f'tl.fromTo("#{i}g",{{scale:.4,rotationY:-90,autoAlpha:0}},{{scale:1,rotationY:0,autoAlpha:1,duration:.9,ease:"expo.out"}},{at + .05:.3f});'
                f'tl.fromTo("#{i}g",{{rotationY:0,y:0}},{{rotationY:14,y:-18,duration:{max(.5, until - at - .9):.3f},ease:"sine.inOut"}},{at + .95:.3f});'
                f'tl.fromTo("#{i} .{i}t",{{autoAlpha:0,y:40,filter:"blur(12px)"}},{{autoAlpha:1,y:0,filter:"blur(0px)",duration:.5,ease:"expo.out"}},{at + .3:.3f});')

    def fx_chart_card(self, e):
        """a full-screen line chart that draws itself: trend up | flat | down, a glowing dot rides the tip"""
        self.info_css()
        i = self.uid('ch')
        at, until = self.window(e, 2.6)
        trend = e.get('trend', 'up')
        W, H = 860, 520
        ys = {'up': [430, 400, 410, 330, 350, 250, 260, 150, 90],
              'flat': [300, 280, 300, 290, 305, 295, 310, 300, 305],
              'down': [120, 150, 140, 210, 200, 280, 300, 380, 440]}[trend]
        xs = [40 + k * (W - 80) / (len(ys) - 1) for k in range(len(ys))]
        d = f'M {xs[0]:.1f} {ys[0]}'
        for k in range(1, len(ys)):
            cx = (xs[k - 1] + xs[k]) / 2
            d += f' C {cx:.1f} {ys[k - 1]}, {cx:.1f} {ys[k]}, {xs[k]:.1f} {ys[k]}'
        area = d + f' L {xs[-1]:.1f} {H} L {xs[0]:.1f} {H} Z'
        col = e.get('color', NAVY['glow'] if trend != 'down' else '#5b6b8f')
        grid = ''.join(f'<line x1="0" x2="{W}" y1="{k * H / 4:.0f}" y2="{k * H / 4:.0f}" stroke="rgba(255,255,255,.07)" stroke-width="2"/>' for k in range(1, 4))
        tag = (f'<div class="a {i}g" style="right:46px;top:34px"><span class="npill" style="font-size:40px">{self.icon_svg(trend, "1em")}'
               f'{esc(e.get("tag", ""))}</span></div>') if e.get('tag') else ''
        inner = (f'<div class="a {i}t" style="left:70px;right:70px;top:{float(e.get("title_y", 330)):.0f}px;text-align:center;font:800 70px/1.1 Inter;'
                 f'color:#fff;letter-spacing:-.03em;text-shadow:0 6px 24px rgba(0,0,0,.6)">{hl(e.get("title", ""))}</div>'
                 f'<div class="a dglass {i}p" style="left:{(1080 - W) / 2:.0f}px;top:{float(e.get("chart_y", 560)):.0f}px;width:{W}px;height:{H + 60}px;border-radius:46px;overflow:hidden">'
                 f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" style="position:absolute;left:0;top:40px;overflow:visible">'
                 f'<defs><linearGradient id="{i}lg" x1="0" x2="1"><stop offset="0" stop-color="{col}"/><stop offset="1" stop-color="{NAVY["hi"]}"/></linearGradient>'
                 f'<linearGradient id="{i}ag" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{col}" stop-opacity=".45"/><stop offset="1" stop-color="{col}" stop-opacity="0"/></linearGradient></defs>'
                 f'{grid}<path id="{i}a" d="{area}" fill="url(#{i}ag)" opacity="0"/>'
                 f'<path d="{d}" fill="none" stroke="{col}" stroke-width="22" opacity=".35" style="filter:blur(10px)" class="{i}s"/>'
                 f'<path id="{i}l" d="{d}" fill="none" stroke="url(#{i}lg)" stroke-width="9" stroke-linecap="round" class="{i}s"/>'
                 f'<circle id="{i}c" r="15" fill="#fff" stroke="{col}" stroke-width="7" cx="{xs[0]:.1f}" cy="{ys[0]}" style="filter:drop-shadow(0 0 16px {col})"/></svg>{tag}</div>'
                 + (f'<div class="a {i}u" style="left:60px;right:60px;top:{float(e.get("chart_y", 560)) + H + 110:.0f}px;text-align:center;font:700 46px/1.2 Inter;'
                    f'color:#fff;opacity:.95;text-shadow:0 4px 16px rgba(0,0,0,.6)">{hl(e["sub"])}</div>' if e.get('sub') else ''))
        self.add(self._card_shell(i, inner), z=38)
        self._card_in_out(i, at, until, float(e.get('enter_for', .45)))
        draw = float(e.get('draw_for', 1.3))
        self.js(f'tl.fromTo("#{i} .{i}t",{{autoAlpha:0,y:40,filter:"blur(12px)"}},{{autoAlpha:1,y:0,filter:"blur(0px)",duration:.5,ease:"expo.out"}},{at + .1:.3f});'
                f'tl.fromTo("#{i} .{i}p",{{autoAlpha:0,y:80,scale:.92}},{{autoAlpha:1,y:0,scale:1,duration:.6,ease:"expo.out"}},{at + .2:.3f});'
                f'(function(){{const L=document.getElementById("{i}l");const n=L.getTotalLength();const C=document.getElementById("{i}c");'
                f'document.querySelectorAll(".{i}s").forEach(p=>{{p.style.strokeDasharray=n;p.style.strokeDashoffset=n;}});const o={{p:0}};'
                f'tl.to(o,{{p:1,duration:{draw:.2f},ease:"power2.inOut",onUpdate:()=>{{document.querySelectorAll(".{i}s").forEach(p=>p.style.strokeDashoffset=n*(1-o.p));'
                f'const pt=L.getPointAtLength(n*o.p);C.setAttribute("cx",pt.x);C.setAttribute("cy",pt.y);}}}},{at + .5:.3f});}})();'
                f'tl.to("#{i}a",{{opacity:1,duration:.8,ease:"power1.out"}},{at + .5 + draw * .5:.3f});')
        if tag:
            self.js(f'tl.fromTo("#{i} .{i}g",{{autoAlpha:0,scale:.3}},{{autoAlpha:1,scale:1,duration:.5,ease:"back.out(2.4)"}},{at + .5 + draw:.3f});')
        if e.get('sub'):
            self.js(f'tl.fromTo("#{i} .{i}u",{{autoAlpha:0,y:24}},{{autoAlpha:1,y:0,duration:.45,ease:"power3.out"}},{self.j.t(e.get("sub_at"), at + .8 + draw):.3f});')
