#!/usr/bin/env python3
"""Draw the profile README cards as animated SVGs in cards/.

Every card is a standalone SVG shown through <img>, so it may only use CSS
animations, SMIL and fonts embedded as data URIs (GitHub runs no JS there).

Edit the PROFILE block below to change the text. Live numbers come from
data/contributions.json, written by fetch_contributions.py.
Set STATIC=1 to render every animation at its final frame (handy for previews).
"""
import base64
import datetime as dt
import io
import json
import os
from html import escape

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
CARDS = os.path.join(ROOT, "cards")
STATIC = bool(os.environ.get("STATIC"))
USER = os.environ.get("GH_USER", "hamzaezz2803-star")

# ───────────────────────────── PROFILE ─────────────────────────────
# Fonts are subset to plain ASCII: avoid accented letters in this block.
PROFILE = {
    "kicker": "FULL-STACK DEVELOPER  /  CASABLANCA",
    "first": "Hamza",
    "last": "Ezzouek",
    "tagline": ["I build SaaS platforms, CRMs and AI workflows,", "from the database to the interface."],
    "link": "portfolio-eta-liard-84.vercel.app",
    "terminal": "hamza@github:~$ whoami",
}
TILES = [  # (file, label, colour, text colour, number, word, blurb)
    ("build", "BUILD", "blue", "#ffffff", "9", "projects",
     "Qarizmi OS, Maw3id, OCP Pointage, plus school, finance and HR apps."),
    ("work", "WORK", "red", "#ffffff", "4", "internships",
     "Qarizmi, Muntadaacom, FSJES Casablanca and All Formations (remote, FR)."),
    ("learn", "LEARN", "yellow", "#111111", "3", "diplomas",
     "Now an engineering student in Data Science and Software at ESTEM."),
]
REPOS = [  # (repo, description, language, colour)
    ("NAIA-CRM", "Qarizmi OS: modular SaaS with CRM, AI workflows and Supabase multi-tenant RLS.",
     "TypeScript", "blue"),
    ("Maw3id", "Multi-organisation SaaS for booking and managing appointments, in French and Arabic.",
     "TypeScript", "red"),
    ("Pre.dashboard", "Attendance tracking for OCP: biometric clock data, shift rules, Excel and PDF exports.",
     "TypeScript", "yellow"),
]

# ───────────────────────────── TOKENS ─────────────────────────────
PAPER, PAPER_2, RULE = "#f3f3f1", "#e2e2de", "#dcdcd7"
INK, INK_2, MUTED, FAINT = "#111111", "#3a3a3c", "#6e6e73", "#c9c9c4"
COLOURS = {"blue": "#2f55ff", "red": "#ef3b2d", "yellow": "#ffc81a"}
BLUE = COLOURS["blue"]
HEAT = [PAPER_2, "#c8d3ff", "#94a8ff", "#6280ff", BLUE, "#1a3be0"]

W, GAP = 880, 12
THIRD = W / 3
SERIF = "'Instrument Serif', Georgia, serif"
SANS = "Geist, system-ui, -apple-system, 'Segoe UI', sans-serif"
MONO = "'Geist Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
FONTS = {
    "serif": ("Instrument Serif", "normal", 400, "serif-400.woff"),
    "serif-i": ("Instrument Serif", "italic", 400, "serif-italic.woff"),
    "sans": ("Geist", "normal", 400, "geist-400.woff"),
    "sans-b": ("Geist", "normal", 600, "geist-600.woff"),
    "mono": ("Geist Mono", "normal", 400, "geistmono-400.woff"),
}

MOTION = """
@keyframes up{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
@keyframes in{from{opacity:0}to{opacity:1}}
@keyframes bar{from{transform:scaleY(0)}to{transform:scaleY(1)}}
@keyframes dot{0%{opacity:0;transform:scale(.3)}70%{opacity:1;transform:scale(1.12)}to{opacity:1;transform:none}}
@keyframes blink{50%{opacity:.25}}
@keyframes drift{50%{transform:translateX(4px)}}
@keyframes driftup{50%{transform:translate(3px,-3px)}}
@keyframes drop{0%{opacity:0;transform:translateY(80px) scale(.65) rotate(-8deg)}60%{opacity:1;transform:translateY(-8px) scale(1.04) rotate(1.5deg)}80%{transform:translateY(2px) rotate(-.5deg)}to{opacity:1;transform:none}}
@keyframes slide{from{opacity:0;transform:translateX(-24px)}to{opacity:1;transform:none}}
@keyframes glint{0%{transform:translateX(-200px) skewX(-20deg)}25%,to{transform:translateX(400px) skewX(-20deg)}}
@keyframes ripple{0%{opacity:.7;transform:scale(.2)}to{opacity:0;transform:scale(2.4)}}
.a-up{opacity:0;transform-box:fill-box;animation:up .8s cubic-bezier(.2,.7,.2,1) both}
.a-in{opacity:0;animation:in .9s ease-out both}
.a-bar{transform-box:fill-box;transform-origin:bottom;transform:scaleY(0);animation:bar .8s cubic-bezier(.2,.7,.2,1) both}
.a-dot{opacity:0;transform-box:fill-box;transform-origin:center;animation:dot .4s ease-out both}
.a-blink{animation:blink 1.6s ease-in-out infinite}
.a-drift{transform-box:fill-box;animation:drift 1.8s ease-in-out infinite}
.a-driftup{transform-box:fill-box;animation:driftup 1.8s ease-in-out infinite}
.a-drop{opacity:0;transform-box:fill-box;transform-origin:50% 60%;animation:drop 1.1s cubic-bezier(.2,.8,.2,1) both}
.a-slide{opacity:0;transform-box:fill-box;animation:slide .6s cubic-bezier(.2,.7,.2,1) both}
.a-glint{animation:glint 5s ease-in-out infinite}
.a-ripple{opacity:0;transform-box:fill-box;transform-origin:center;animation:ripple 1s ease-out both}
@media (prefers-reduced-motion:reduce){ANIMATED{animation:none!important;opacity:1!important;transform:none!important}.a-glint,.a-ripple{display:none}}
"""
ANIMATED = ".a-up,.a-in,.a-bar,.a-dot,.a-blink,.a-drift,.a-driftup,.a-drop,.a-slide"
MOTION = MOTION.replace("ANIMATED", ANIMATED)
FREEZE = ANIMATED + "{animation:none!important;opacity:1!important;transform:none!important}.a-glint,.a-ripple{display:none}"


def at(t):
    return f'style="animation-delay:{t:.2f}s"'


def embed(keys):
    css = ""
    for k in keys:
        family, style, weight, file = FONTS[k]
        with open(os.path.join(ROOT, "fonts", file), "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        css += (f"@font-face{{font-family:'{family}';font-style:{style};font-weight:{weight};"
                f"src:url(data:font/woff;base64,{b64}) format('woff')}}")
    return css


def save(name, w, h, body, fonts, label, left=0, right=0, bottom=GAP):
    """Wrap a w x h card in a transparent canvas whose padding makes rows tile evenly."""
    if left:
        body = f'<g transform="translate({left:.3f} 0)">{body}</g>'
    cw, ch = w + left + right, h + bottom
    css = embed(fonts) + MOTION + (FREEZE if STATIC else "")
    out = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{cw:.3f}" height="{ch}" '
           f'viewBox="0 0 {cw:.3f} {ch}" role="img" aria-label="{escape(label)}">'
           f'<title>{escape(label)}</title><style>{css}</style>{body}</svg>')
    os.makedirs(CARDS, exist_ok=True)
    with open(os.path.join(CARDS, name), "w", encoding="utf-8") as f:
        f.write(out)
    print(f"cards/{name}  {len(out) // 1024} KB")


def wrap(text, width):
    lines, cur = [], ""
    for word in text.split():
        if cur and len(cur) + len(word) + 1 > width:
            lines.append(cur)
            cur = word
        else:
            cur = (cur + " " + word).strip()
    return lines + [cur] if cur else lines


def lines_svg(x, y, lines, step, attrs, cls="", start=None):
    out = ""
    for i, line in enumerate(lines):
        anim = f'class="{cls}" {at(start + i * 0.1)} ' if cls else ""
        out += f'<text {anim}x="{x}" y="{y + i * step}" {attrs}>{escape(line)}</text>'
    return out


# ───────────────────────────── PORTRAIT ─────────────────────────────
RAMP = " .`:-=+*cs#%@"


def load_photo():
    from PIL import Image

    for name in ("photo.png", "photo.jpg", "photo.jpeg"):
        path = os.path.join(ROOT, "assets", name)
        if os.path.exists(path):
            return Image.open(path)
    import requests  # fall back to the GitHub avatar

    r = requests.get(f"https://github.com/{USER}.png?size=460", timeout=30)
    r.raise_for_status()
    return Image.open(io.BytesIO(r.content))


def ascii_rows(cols, rows):
    from PIL import ImageEnhance, ImageOps

    img = ImageOps.autocontrast(load_photo().convert("L"), cutoff=2)
    img = ImageEnhance.Contrast(img).enhance(1.15)
    img = img.resize((cols, rows))
    px = img.load()
    out = []
    for y in range(rows):
        row = ""
        for x in range(cols):
            lum = (px[x, y] / 255) ** 1.15
            # soft round vignette: fade the photo's edges to paper so the subject stands out
            r = (((x + .5) / cols - .5) ** 2 + ((y + .5) / rows - .5) ** 2) ** .5 / .5
            fade = min(1.0, max(0.0, (r - .6) / .35))
            lum += (1 - lum) * fade * fade * (3 - 2 * fade)
            row += " " if lum > 0.86 else RAMP[min(len(RAMP) - 1, round((1 - lum) * (len(RAMP) - 1)))]
        out.append(row)
    return out


# ───────────────────────────── CARDS ─────────────────────────────
def hero():
    h = 420
    px, py, pw = 528, 40, 312  # portrait box
    cols = 84
    cw = pw / cols
    chh = cw * 1.875
    rows = int(round((h - 2 * py) / chh))
    try:
        art = ascii_rows(cols, rows)
    except Exception as e:  # no photo, no network: keep the card, skip the portrait
        print(f"portrait skipped: {e}")
        art = []
    portrait = "".join(
        f'<text class="a-in" style="animation-delay:{0.25 + i * 0.02:.2f}s;animation-duration:.35s" '
        f'xml:space="preserve" x="{px}" y="{py + (i + 0.8) * chh:.1f}" font-size="{chh * 0.9:.2f}" '
        f'textLength="{pw}" lengthAdjust="spacing">{escape(r)}</text>'
        for i, r in enumerate(art)
    )
    p = PROFILE
    link_end = 48 + len(p["link"]) * 7.9
    body = f"""
<defs><linearGradient id="shine" gradientUnits="userSpaceOnUse" x1="0" x2="560" y1="0" y2="0">
  <stop offset="0" stop-color="{INK}"/><stop offset=".42" stop-color="{INK}"/><stop offset=".5" stop-color="{BLUE}"/>
  <stop offset=".58" stop-color="{INK}"/><stop offset="1" stop-color="{INK}"/>
  <animateTransform attributeName="gradientTransform" type="translate" values="-560 0;560 0;560 0"
    keyTimes="0;.45;1" dur="7s" begin="1.6s" repeatCount="indefinite"/></linearGradient></defs>
<rect width="{W}" height="{h}" rx="14" fill="{PAPER}"/>
<g class="a-in" {at(0)}>
  <rect class="a-blink" x="48" y="49" width="8" height="8" rx="2" fill="{BLUE}"/>
  <text x="66" y="57" font-family="{MONO}" font-size="12" letter-spacing="1" fill="{MUTED}">{escape(p["kicker"])}</text>
</g>
<text class="a-up" {at(.15)} x="44" y="190" font-family="{SERIF}" font-size="112" letter-spacing="-2.5" fill="{INK}">{escape(p["first"])}</text>
<text class="a-up" {at(.3)} x="44" y="288" font-family="{SERIF}" font-style="italic" font-size="112" letter-spacing="-2.5" fill="url(#shine)">{escape(p["last"])}</text>
<g class="a-up" {at(.55)}>{lines_svg(48, 336, p["tagline"], 26, f'font-family="{SANS}" font-size="17" fill="{INK_2}"')}</g>
<g class="a-in" {at(.8)}>
  <text x="48" y="394" font-family="{MONO}" font-size="13" fill="{INK}">{escape(p["link"])}</text>
  <text class="a-driftup" x="{link_end:.0f}" y="394" font-family="{MONO}" font-size="13" fill="{BLUE}">&#8599;</text>
</g>
<g font-family="{MONO}" fill="{INK}">{portrait}</g>
"""
    save("hero.svg", W, h, body, ["serif", "serif-i", "sans", "mono"],
         f'{p["first"]} {p["last"]}. Full-stack developer in Casablanca. ' + " ".join(p["tagline"]))


def counter(num, word, x, y, attrs, begin, dur=1.0, frames=14):
    """Count a number up from 0 with SMIL <set> frames (works inside <img>)."""
    tail = f' <tspan font-style="italic">{escape(word)}</tspan>'
    digits = "".join(c for c in num if c.isdigit() or c == ".")
    suffix = num[len(digits):]
    if STATIC or not digits:
        return f'<text x="{x}" y="{y}" {attrs}>{escape(num)}{tail}</text>'
    target = float(digits)
    places = len(digits.split(".")[1]) if "." in digits else 0
    out = ""
    for i in range(frames + 1):
        t0 = begin + dur * i / frames
        value = num if i == frames else f"{target * (1 - (1 - i / frames) ** 3):.{places}f}{suffix}"
        hide = "" if i == frames else f'<set attributeName="opacity" to="0" begin="{begin + dur * (i + 1) / frames:.3f}s"/>'
        out += (f'<text x="{x}" y="{y}" {attrs} opacity="0">{escape(value)}{tail}'
                f'<set attributeName="opacity" to="1" begin="{t0:.3f}s"/>{hide}</text>')
    return out


def tile(pos, name, label, colour, fg, num, word, blurb):
    tw, th = THIRD - 8, 210
    t = 3.1 + pos * 0.25
    bg = COLOURS[colour]
    body = f"""
<defs>
  <clipPath id="c"><rect width="{tw}" height="{th}" rx="14"/></clipPath>
  <clipPath id="s"><rect y="62" width="{tw}" height="62"/></clipPath>
  <linearGradient id="gl" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>
    <stop offset=".5" stop-color="#fff" stop-opacity=".35"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
</defs>
<g class="a-drop" {at(t)}>
  <g clip-path="url(#c)">
    <rect width="{tw}" height="{th}" fill="{bg}"/>
    <circle class="a-ripple" {at(t + .5)} cx="{tw - 40:.1f}" cy="{th - 40}" r="60" fill="none" stroke="{fg}" stroke-opacity=".5" stroke-width="2"/>
    <rect class="a-glint" style="animation-delay:{t + 1.4:.2f}s" y="-20" width="90" height="{th + 40}" fill="url(#gl)" transform="translate(-200 0)"/>
  </g>
  <text class="a-slide" {at(t + .35)} x="24" y="38" font-family="{MONO}" font-size="12" letter-spacing="1.2" fill="{fg}">{label}</text>
  <g class="a-slide" {at(t + .5)}><text class="a-drift" style="animation-delay:{t + 1.3:.2f}s" x="{tw - 36:.0f}" y="38" font-family="{MONO}" font-size="14" fill="{fg}">&#8594;</text></g>
  <g clip-path="url(#s)"><g class="a-up" {at(t + .45)}>{counter(num, word, 22, 112, f'font-family="{SERIF}" font-size="44" fill="{fg}"', t + .45)}</g></g>
  {lines_svg(24, 150, wrap(blurb, 34), 20, f'font-family="{SANS}" font-size="14" fill="{fg}" opacity=".92"', "a-up", t + .75)}
</g>"""
    save(f"{name}.svg", tw, th, body, ["serif", "serif-i", "sans", "mono"],
         f"{label}: {num} {word}. {blurb}", left=4 * pos, right=8 - 4 * pos)


def heatmap(data):
    days = data["days"]
    lead = (dt.date.fromisoformat(days[0]["date"]).weekday() + 1) % 7  # weeks start on Sunday
    size, step, x0, y0 = 12, 15, 44, 96
    cells, labels, seen = "", "", set()
    weeks = (len(days) + lead + 6) // 7
    for i, day in enumerate(days):
        col, row = divmod(i + lead, 7)
        d = dt.date.fromisoformat(day["date"])
        if row == 0 and d.day <= 7 and (d.year, d.month) not in seen and col < weeks - 10:
            seen.add((d.year, d.month))
            labels += (f'<text x="{x0 + col * step}" y="{y0 + 7 * step + 16}" font-family="{MONO}" '
                       f'font-size="11" fill="{MUTED}">{d.strftime("%b")}</text>')
        c = day["count"]
        lvl = 0 if c == 0 else 1 if c <= 2 else 2 if c <= 5 else 3 if c <= 10 else 4 if c <= 20 else 5
        cells += (f'<rect class="a-dot" style="animation-delay:{1 + col * .03 + row * .02:.2f}s" '
                  f'x="{x0 + col * step}" y="{y0 + row * step}" width="{size}" height="{size}" rx="3" '
                  f'fill="{HEAT[lvl]}"><title>{day["date"]}: {c}</title></rect>')
    right = x0 + weeks * step - 3
    lx = right - len(HEAT) * 14
    ly = y0 + 7 * step + 6
    legend = "".join(f'<rect x="{lx + i * 14}" y="{ly}" width="11" height="11" rx="2.5" fill="{c}"/>'
                     for i, c in enumerate(HEAT))
    h = y0 + 7 * step + 44
    body = f"""
<rect width="{W}" height="{h}" rx="14" fill="{PAPER}"/>
<text class="a-up" {at(.8)} x="42" y="62" font-family="{SERIF}" font-size="34" fill="{INK}">Every day, <tspan font-style="italic" fill="{BLUE}">in blue</tspan></text>
<text class="a-in" {at(.8)} x="{right}" y="60" text-anchor="end" font-family="{MONO}" font-size="12" letter-spacing="1" fill="{MUTED}">REFRESHED DAILY</text>
{cells}
<g class="a-in" {at(2.4)}>{labels}
<text x="{lx - 8}" y="{ly + 10}" text-anchor="end" font-family="{MONO}" font-size="11" fill="{MUTED}">less</text>{legend}
<text x="{lx + len(HEAT) * 14 + 2}" y="{ly + 10}" font-family="{MONO}" font-size="11" fill="{MUTED}">more</text></g>"""
    save("heatmap.svg", W, h, body, ["serif", "serif-i", "mono"],
         f'Contribution graph: {data["total"]:,} contributions in the last year')


def activity(data):
    h = 340
    months = data["months"][-12:]
    best = max(months[:-1] or months, key=lambda m: m["total"])
    top = max(best["total"], 1)
    x0, x1, base, tall, gap = 40, 600, 292, 140, 10
    bw = (x1 - x0 - gap * (len(months) - 1)) / len(months)
    bars = ""
    for i, m in enumerate(months):
        x = x0 + i * (bw + gap)
        bh = max(4, round(m["total"] / top * tall))
        fill = BLUE if m is best else FAINT if i == len(months) - 1 else INK
        name = dt.date.fromisoformat(m["month"] + "-01").strftime("%b")
        t = 2.2 + i * .07
        bars += (f'<rect class="a-bar" {at(t)} x="{x:.1f}" y="{base - bh}" width="{bw:.1f}" height="{bh}" rx="4" '
                 f'fill="{fill}"><title>{name}: {m["total"]}</title></rect>'
                 f'<text class="a-in" {at(t)} x="{x + bw / 2:.1f}" y="{base + 22}" text-anchor="middle" '
                 f'font-family="{MONO}" font-size="11" fill="{MUTED}">{name}</text>')
        if m is best:
            bars += (f'<text class="a-dot" {at(3.2)} x="{x + bw / 2:.1f}" y="{base - bh - 10}" text-anchor="middle" '
                     f'font-family="{MONO}" font-size="11" fill="{BLUE}">{m["total"]}</text>')
    cur, lng = data["current_streak"], data["longest_streak"]
    side_stats = [
        (f'{cur} <tspan font-style="italic">days</tspan>',
         "current streak, and the longest" if cur >= lng else f"current streak, longest {lng}"),
        (f'{data["active_days"]}<tspan fill="#8e8e93"> / {len(data["days"])}</tspan>', "days with a commit"),
        (str(data["best_day"]["count"]), "on the busiest day"),
    ]
    side = ""
    for i, (big, small) in enumerate(side_stats):
        y = 104 + i * 92
        side += (f'<g class="a-up" {at(2.6 + i * .15)}><text x="650" y="{y}" font-family="{SERIF}" font-size="40" '
                 f'fill="{INK}">{big}</text><text x="650" y="{y + 24}" font-family="{SANS}" font-size="13" '
                 f'fill="{MUTED}">{small}</text></g>')
        if i < 2:
            side += f'<rect class="a-in" {at(2.6)} x="650" y="{y + 44}" width="190" height="1" fill="{RULE}"/>'
    body = f"""
<rect width="{W}" height="{h}" rx="14" fill="{PAPER}"/>
<text class="a-in" {at(1.9)} x="40" y="58" font-family="{MONO}" font-size="12" letter-spacing="1" fill="{MUTED}">THE LAST 12 MONTHS ON GITHUB</text>
<text class="a-up" {at(2)} x="38" y="114" font-family="{SERIF}" font-size="52" fill="{INK}">{data["total"]:,} <tspan font-style="italic">contributions</tspan></text>
{bars}{side}"""
    save("activity.svg", W, h, body, ["serif", "serif-i", "sans", "mono"],
         f'{data["total"]:,} contributions in the last year, {cur}-day streak')


def section(text, italic, theme):
    fg = "#e6edf3" if theme == "dark" else INK
    body = (f'<text class="a-up" {at(4.4)} x="2" y="46" font-family="{SERIF}" font-size="34" fill="{fg}">'
            f'{escape(text)} <tspan font-style="italic">{escape(italic)}</tspan></text>')
    save(f"title-coding-{theme}.svg", W, 64, body, ["serif", "serif-i"], f"{text} {italic}", bottom=0)


def repo(pos, name, desc, lang, colour, stars):
    rw, rh = THIRD - 8, 176
    meta = f"{lang}  /  {stars} star{'s' if stars != 1 else ''}" if stars else lang
    body = f"""
<rect width="{rw}" height="{rh}" rx="14" fill="{PAPER}"/>
<g class="a-up" {at(4.6 + pos * .12)}>
  <rect x="24" y="30" width="8" height="8" rx="2" fill="{COLOURS[colour]}"/>
  <text x="40" y="39" font-family="{SANS}" font-weight="600" font-size="18" fill="{INK}">{escape(name)}</text>
  {lines_svg(24, 72, wrap(desc, 34), 21, f'font-family="{SANS}" font-size="14" fill="{INK_2}"')}
  <text x="24" y="{rh - 24}" font-family="{MONO}" font-size="12" fill="{MUTED}">{escape(meta)}</text>
</g>"""
    save(f"repo-{name.lower().replace('.', '-')}.svg", rw, rh, body, ["sans", "sans-b", "mono"],
         f"{name}: {desc}", left=4 * pos, right=8 - 4 * pos)


def stars():
    try:
        import requests

        out = {}
        for name, *_ in REPOS:
            r = requests.get(f"https://api.github.com/repos/{USER}/{name}", timeout=10)
            if r.ok:
                out[name] = r.json().get("stargazers_count", 0)
        return out
    except Exception as e:
        print(f"stars skipped: {e}")
        return {}


if __name__ == "__main__":
    with open(os.path.join(ROOT, "data", "contributions.json"), encoding="utf-8") as f:
        data = json.load(f)
    hero()
    heatmap(data)
    activity(data)
    for i, t in enumerate(TILES):
        tile(i, *t)
    section("What I'm", "coding", "dark")
    section("What I'm", "coding", "light")
    counts = stars()
    for i, (name, desc, lang, colour) in enumerate(REPOS):
        repo(i, name, desc, lang, colour, counts.get(name, 0))
