"""Erzeugt die animierten SVGs für das GitHub Profil.

Aufruf:  python scripts/build_assets.py
Ausgabe: assets/header.svg, assets/terminal.svg, assets/stack.svg, assets/footer.svg
"""

from __future__ import annotations

import base64
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

# Farben, abgenommen vom Nachtstudio Banner
PAPER = "#F8DD8E"
BUTTER = "#FAC650"
MOON = "#FCE48A"
INK = "#1D2025"
INK_2 = "#2A2D33"
INK_3 = "#3A3E46"
CREAM = "#EDE6D6"
MUTED = "#9C978B"

MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"
SANS = "'Segoe UI', -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif"


def write(name: str, svg: str) -> None:
    path = ASSETS / name
    path.write_text(svg.strip() + "\n", encoding="utf-8")
    print(f"{name}: {path.stat().st_size / 1024:.0f} KB")


def esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ---------------------------------------------------------------------------
# Typing helper: Text mit fester Zeichenbreite (textLength) wird über ein
# Clip Rechteck Zeichen für Zeichen freigelegt. Funktioniert ohne Webfonts.
# ---------------------------------------------------------------------------


def appear(t: float) -> str:
    """Unsichtbar bis t, danach sichtbar. Ohne SMIL bleibt das Element sichtbar."""
    return (
        f'<animate attributeName="opacity" values="0;0;1" keyTimes="0;0.999;1" '
        f'dur="{t + 0.01:.2f}s" fill="freeze"/>'
    )


def discrete(values: list[float], times: list[float]) -> tuple[str, str]:
    return ";".join(f"{v:g}" for v in values), ";".join(f"{t:.4f}" for t in times)


# ---------------------------------------------------------------------------
# Header: echter Banner + Sterne, Sternschnuppe, Mondschein, Laptop Puls und
# eine Statuszeile, die abwechselnd tippt, was gerade gebaut wird.
# ---------------------------------------------------------------------------


def build_header() -> str:
    jpg = base64.b64encode((ASSETS / "banner-nachtstudio.jpg").read_bytes()).decode()
    rnd = random.Random(31)

    # Sterne im dunklen Himmel (nur Bereiche, die im Banner sicher dunkel sind)
    stars = [(1302, 139, 2.6), (1350, 201, 2.4), (1294, 257, 2.2)]
    candidates = [
        (1030, 30), (1085, 70), (1150, 22), (1215, 58), (1262, 18), (1330, 52),
        (1395, 28), (1452, 74), (1478, 160), (1425, 205), (1462, 290), (1388, 300),
        (1260, 95), (1180, 105), (1420, 120), (1340, 92), (1120, 48), (1480, 30),
    ]
    stars += [(x, y, rnd.uniform(0.9, 1.6)) for x, y in candidates]

    star_svg = []
    for i, (x, y, r) in enumerate(stars):
        dur = rnd.uniform(2.4, 5.5)
        delay = rnd.uniform(0, 4)
        low = rnd.uniform(0.15, 0.4)
        star_svg.append(
            f'<g><circle cx="{x}" cy="{y}" r="{r * 3.2:.1f}" fill="url(#starGlow)"/>'
            f'<circle cx="{x}" cy="{y}" r="{r:.1f}" fill="#FFF6D8"/>'
            f'<animate attributeName="opacity" values="1;{low:.2f};1" dur="{dur:.1f}s" '
            f'begin="{delay:.1f}s" repeatCount="indefinite"/></g>'
        )

    # Statuszeile im dunklen Boden unten rechts
    prefix = "> gerade im Bau: "
    phrases = ["eigene Apps", "AI Workflows", "das erste Video", "dieses Profil"]
    char_w, x0, y0 = 10.8, 1046, 463
    px_prefix = len(prefix) * char_w
    type_t, del_t, hold, pause = 0.085, 0.035, 2.0, 0.45
    segments = []
    t = 0.0
    for phrase in phrases:
        n = len(phrase)
        segments.append((phrase, t))
        t += n * type_t + hold + n * del_t + pause
    total = t

    status = []
    cursor_x_vals, cursor_times = [], []
    for phrase, start in segments:
        n = len(phrase)
        vals, times = [0.0], [0.0]
        tt = start
        vals.append(0.0)
        times.append(tt / total)
        for k in range(1, n + 1):
            tt += type_t
            vals.append(k * char_w)
            times.append(tt / total)
        tt += hold
        for k in range(n - 1, -1, -1):
            tt += del_t
            vals.append(k * char_w)
            times.append(tt / total)
        cursor_x_vals += vals[1:]
        cursor_times += times[1:]
        v, kt = discrete(vals, times)
        cid = f"st{len(status)}"
        status.append(
            f'<clipPath id="{cid}"><rect x="{x0 + px_prefix:.1f}" y="{y0 - 18}" height="26" width="{n * char_w if not status else 0:.1f}">'
            f'<animate attributeName="width" values="{v}" keyTimes="{kt}" dur="{total:.2f}s" '
            f'calcMode="discrete" repeatCount="indefinite"/></rect></clipPath>'
            f'<text x="{x0 + px_prefix:.1f}" y="{y0}" textLength="{n * char_w:.1f}" lengthAdjust="spacingAndGlyphs" '
            f'clip-path="url(#{cid})" class="status hl">{esc(phrase)}</text>'
        )
    # Cursor folgt dem getippten Text
    order = sorted(zip(cursor_times, cursor_x_vals))
    times = [0.0] + [o[0] for o in order]
    xs = [0.0] + [o[1] for o in order]
    xs = [x0 + px_prefix + 2 + x for x in xs]
    v, kt = discrete(xs, times)
    cursor = (
        f'<rect y="{y0 - 15}" width="9" height="18" fill="{BUTTER}" x="{x0 + px_prefix + 2 + len(phrases[0]) * char_w:.1f}">'
        f'<animate attributeName="x" values="{v}" keyTimes="{kt}" dur="{total:.2f}s" '
        f'calcMode="discrete" repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1s" repeatCount="indefinite"/>'
        f"</rect>"
    )

    return f"""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1500 500" width="1500" height="500" role="img" aria-labelledby="title">
  <title id="title">Solo Stack: AI, Code, Side Projects, Business</title>
  <defs>
    <radialGradient id="moonHalo">
      <stop offset="0.58" stop-color="{MOON}" stop-opacity="0"/>
      <stop offset="0.66" stop-color="{MOON}" stop-opacity="0.55"/>
      <stop offset="0.8" stop-color="{BUTTER}" stop-opacity="0.18"/>
      <stop offset="1" stop-color="{BUTTER}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="starGlow">
      <stop offset="0" stop-color="#FFF3C4" stop-opacity="0.85"/>
      <stop offset="1" stop-color="#FFF3C4" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="codeGlow">
      <stop offset="0" stop-color="{MOON}" stop-opacity="0.9"/>
      <stop offset="1" stop-color="{BUTTER}" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="trail" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#FFF3C4" stop-opacity="0"/>
      <stop offset="1" stop-color="#FFF8E0" stop-opacity="0.95"/>
    </linearGradient>
    <clipPath id="sky"><path d="M1000 0 H1500 V330 H1240 V115 H1000 Z"/></clipPath>
    <style>
      .status {{ font: 600 18px {MONO}; fill: {CREAM}; white-space: pre; }}
      .hl {{ fill: {BUTTER}; }}
    </style>
  </defs>

  <image width="1500" height="500" href="data:image/jpeg;base64,{jpg}"/>

  <!-- Mondschein atmet -->
  <circle cx="1128" cy="236" r="172" fill="url(#moonHalo)" opacity="0.5">
    <animate attributeName="opacity" values="0.35;0.85;0.35" dur="7s" repeatCount="indefinite"/>
    <animate attributeName="r" values="168;178;168" dur="7s" repeatCount="indefinite"/>
  </circle>

  <!-- Sterne funkeln -->
  <g clip-path="url(#sky)">
    {"".join(star_svg)}
    <!-- Sternschnuppe -->
    <g opacity="0">
      <line x1="0" y1="0" x2="120" y2="0" stroke="url(#trail)" stroke-width="2.2" stroke-linecap="round"/>
      <circle cx="120" cy="0" r="2.4" fill="#FFF8E0"/>
      <animateTransform attributeName="transform" type="translate" values="1500 10; 1500 10; 1250 105; 1250 105"
        keyTimes="0;0.62;0.72;1" dur="11s" begin="1.5s" repeatCount="indefinite" additive="replace"/>
      <animateTransform attributeName="transform" type="rotate" values="159" dur="11s" begin="1.5s" repeatCount="indefinite" additive="sum"/>
      <animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;0.62;0.64;0.68;0.72;1" dur="11s" begin="1.5s" repeatCount="indefinite"/>
    </g>
  </g>

  <!-- Laptop: der Code Tag glimmt -->
  <circle cx="1117" cy="329" r="17" fill="url(#codeGlow)" opacity="0.2">
    <animate attributeName="opacity" values="0.15;0.75;0.15" dur="2.6s" repeatCount="indefinite"/>
  </circle>

  <!-- Statuszeile -->
  <text x="{x0}" y="{y0}" textLength="{px_prefix:.1f}" lengthAdjust="spacingAndGlyphs" class="status" opacity="0.85" xml:space="preserve">{esc(prefix)}</text>
  {"".join(status)}
  {cursor}
</svg>
"""


# ---------------------------------------------------------------------------
# Terminal: whoami & Co. werden nacheinander getippt.
# ---------------------------------------------------------------------------


def build_terminal() -> str:
    W, H = 900, 340
    cw, fs, lh = 9.6, 16, 30
    x_text, y_first = 34, 92
    prompt = "~/solo-stack $ "
    script = [
        ("whoami", [[("Softwareentwickler aus Deutschland. Baut eigene Apps mit AI", CREAM)],
                    [("und zeigt Fortschritte, Fehler und Learnings auf YouTube.", CREAM)]]),
        ("cat stack.txt", [[("AI", BUTTER), ("  ·  ", MUTED), ("Code", BUTTER), ("  ·  ", MUTED),
                            ("Side Projects", BUTTER), ("  ·  ", MUTED), ("Business", BUTTER)]]),
        ("status", [[("Kanal: frisch gestartet", CREAM), ("  │  ", MUTED), ("Sprache: Deutsch", CREAM),
                     ("  │  ", MUTED), ("Modus: Nachtschicht ☾", BUTTER)]]),
    ]

    out = []
    t = 0.6
    y = y_first
    clip_id = 0

    def line_parts(parts, x, y, begin):
        nonlocal clip_id
        frags = []
        for text, color in parts:
            w = len(text) * cw
            frags.append(
                f'<text x="{x:.1f}" y="{y}" textLength="{w:.1f}" lengthAdjust="spacingAndGlyphs" fill="{color}" '
                f'class="t">{esc(text)}{appear(begin)}</text>'
            )
            x += w
        return "".join(frags)

    for cmd, outputs in script:
        # Prompt erscheint
        out.append(line_parts([("~/solo-stack", BUTTER), (" $ ", MUTED)], x_text, y, t))
        # Befehl wird getippt
        cx = x_text + len(prompt) * cw
        w = len(cmd) * cw
        steps = len(cmd)
        vals = ";".join(f"{k * cw:.1f}" for k in range(steps + 1))
        dur = steps * 0.09
        t0 = t + 0.35
        total = t0 + dur
        kt = "0;" + ";".join(f"{(t0 + k * 0.09) / total:.4f}" for k in range(steps + 1))
        clip_id += 1
        out.append(
            f'<clipPath id="c{clip_id}"><rect x="{cx:.1f}" y="{y - 18}" height="26" width="{w:.1f}">'
            f'<animate attributeName="width" values="0;{vals}" keyTimes="{kt}" calcMode="discrete" '
            f'dur="{t0 + dur:.2f}s" fill="freeze"/></rect></clipPath>'
            f'<text x="{cx:.1f}" y="{y}" textLength="{w:.1f}" lengthAdjust="spacingAndGlyphs" class="t" fill="#FFFFFF" '
            f'clip-path="url(#c{clip_id})">{esc(cmd)}</text>'
        )
        t += 0.35 + dur + 0.35
        y += lh
        for parts in outputs:
            out.append(line_parts(parts, x_text, y, t))
            t += 0.12
            y += lh
        t += 0.5
        y += 10

    # letzter Prompt mit blinkendem Cursor
    out.append(line_parts([("~/solo-stack", BUTTER), (" $ ", MUTED)], x_text, y, t))
    cur_x = x_text + len(prompt) * cw
    out.append(
        f'<g>{appear(t)}<rect x="{cur_x:.1f}" y="{y - 15}" width="9" height="19" fill="{BUTTER}">'
        f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1.05s" '
        f'begin="{t:.2f}s" repeatCount="indefinite"/></rect></g>'
    )
    H = y + 34

    return f"""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="title">
  <title id="title">Terminal: whoami, Softwareentwickler aus Deutschland, baut eigene Apps mit AI</title>
  <defs>
    <filter id="grain" x="0" y="0" width="100%" height="100%">
      <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="7" result="n"/>
      <feColorMatrix in="n" type="matrix" values="0 0 0 0 1  0 0 0 0 0.95  0 0 0 0 0.8  0 0 0 0.05 0"/>
      <feComposite in2="SourceGraphic" operator="in"/>
    </filter>
    <style>.t {{ font: 500 {fs}px {MONO}; white-space: pre; }} .title {{ font: 600 13px {SANS}; fill: {MUTED}; }}</style>
  </defs>
  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="16" fill="{INK}" stroke="{INK_3}" stroke-width="1.5"/>
  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="16" fill="#fff" filter="url(#grain)"/>
  <path d="M1 44 V17 a16 16 0 0 1 16 -16 H{W - 17} a16 16 0 0 1 16 16 V44 Z" fill="{INK_2}"/>
  <line x1="1" y1="44" x2="{W - 1}" y2="44" stroke="{INK_3}"/>
  <circle cx="26" cy="23" r="6.5" fill="{BUTTER}"/>
  <circle cx="48" cy="23" r="6.5" fill="{PAPER}" opacity="0.8"/>
  <circle cx="70" cy="23" r="6.5" fill="{INK_3}"/>
  <text x="{W / 2}" y="27.5" text-anchor="middle" class="title">solo@stack: ~/solo-stack</text>
  {"".join(out)}
</svg>
"""


# ---------------------------------------------------------------------------
# Stack: vier Ebenen fallen nacheinander aufeinander.
# ---------------------------------------------------------------------------


def build_stack() -> str:
    W, H = 900, 440
    cx, w, h, thick, gap = 205, 122, 61, 28, 34
    layers = [  # von unten nach oben
        ("Code", "Softwareentwicklung aus echter Praxis"),
        ("AI", "Neue Modelle und Tools selbst getestet"),
        ("Side Projects", "Eigene Apps vom ersten Commit bis zum Launch"),
        ("Business", "Selbstständigkeit, Zahlen und Entscheidungen"),
    ]
    tops = ["#F3C653", "#F6D06B", "#F8DA83", PAPER]
    base_y = 328
    parts = []
    labels = []
    for i, (name, desc) in enumerate(layers):
        y = base_y - i * (thick + gap)
        begin = 0.4 + i * 0.55
        k1 = begin / (begin + 0.75)
        k2 = (begin + 0.585) / (begin + 0.75)
        top = f"M{cx} {y - h} L{cx + w} {y} L{cx} {y + h} L{cx - w} {y} Z"
        left = f"M{cx - w} {y} L{cx} {y + h} L{cx} {y + h + thick} L{cx - w} {y + thick} Z"
        right = f"M{cx + w} {y} L{cx} {y + h} L{cx} {y + h + thick} L{cx + w} {y + thick} Z"
        parts.append(
            f'<g>{appear(begin)}'
            f'<animateTransform attributeName="transform" type="translate" values="0 -360; 0 -360; 0 7; 0 0" '
            f'keyTimes="0;{k1:.4f};{k2:.4f};1" calcMode="spline" '
            f'keySplines="0 0 1 1; 0.55 0 1 0.45; 0.2 0.6 0.4 1" dur="{begin + 0.75:.2f}s" fill="freeze"/>'
            f'<path d="{left}" fill="{INK}"/><path d="{right}" fill="{INK_2}"/>'
            f'<path d="{top}" fill="{tops[i]}"/><path d="{top}" fill="#fff" filter="url(#paper)"/>'
            f'<path d="{top}" fill="none" stroke="{INK}" stroke-width="2" stroke-linejoin="round"/>'
            f'<line x1="{cx}" y1="{y + h}" x2="{cx}" y2="{y + h + thick}" stroke="{INK_3}" stroke-width="1"/>'
            f"</g>"
        )
        ly = y + 6
        labels.append(
            f'<g>{appear(begin + 0.6)}'
            f'<animateTransform attributeName="transform" type="translate" values="-14 0; -14 0; 0 0" '
            f'keyTimes="0;{(begin + 0.6) / (begin + 1.0):.4f};1" dur="{begin + 1.0:.2f}s" fill="freeze"/>'
            f'<line x1="{cx + w + 14}" y1="{y}" x2="{404}" y2="{y}" stroke="{INK}" stroke-width="1.5" stroke-dasharray="2 5" stroke-linecap="round"/>'
            f'<circle cx="{cx + w + 8}" cy="{y}" r="3.5" fill="{INK}"/>'
            f'<text x="420" y="{ly - 4}" class="name">{esc(name)}</text>'
            f'<text x="420" y="{ly + 18}" class="desc">{esc(desc)}</text></g>'
        )

    top_y = base_y - 3 * (thick + gap) - h
    done = 0.4 + 3 * 0.55 + 0.75
    moon = (
        f'<g>{appear(done)}'
        f'<circle cx="{cx}" cy="{top_y - 38}" r="21" fill="{MOON}" stroke="{INK}" stroke-width="2"/>'
        f'<circle cx="{cx}" cy="{top_y - 38}" r="21" fill="#fff" filter="url(#paper)"/>'
        f'<animateTransform attributeName="transform" type="translate" values="0 0; 0 -6; 0 0" dur="3.2s" '
        f'begin="{done:.2f}s" repeatCount="indefinite"/></g>'
    )

    return f"""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="title">
  <title id="title">Ein Mensch, ein ganzer Stack: Code, AI, Side Projects, Business</title>
  <defs>
    <filter id="paper" x="0" y="0" width="100%" height="100%">
      <feTurbulence type="fractalNoise" baseFrequency="0.035 0.05" numOctaves="4" seed="3" result="n"/>
      <feColorMatrix in="n" type="matrix" values="0 0 0 0 0.93  0 0 0 0 0.62  0 0 0 0 0.12  0 0 0 0.55 -0.12"/>
      <feComposite in2="SourceGraphic" operator="in"/>
    </filter>
    <style>
      .h {{ font: 800 30px {SANS}; fill: {INK}; letter-spacing: -0.5px; }}
      .sub {{ font: 500 15px {MONO}; fill: #5B5442; }}
      .name {{ font: 800 21px {SANS}; fill: {INK}; }}
      .desc {{ font: 500 15px {SANS}; fill: #4A4436; }}
    </style>
  </defs>
  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="18" fill="{PAPER}" stroke="{INK}" stroke-width="2"/>
  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="18" fill="#fff" filter="url(#paper)"/>
  <text x="420" y="70" class="h">Ein Mensch. Ein ganzer Stack.</text>
  <text x="422" y="98" class="sub">// alles selbst gebaut, mit AI im Team</text>
  <clipPath id="card"><rect x="3" y="3" width="{W - 6}" height="{H - 6}" rx="16"/></clipPath>
  <g clip-path="url(#card)">
  {"".join(parts)}
  {moon}
  </g>
  {"".join(labels)}
</svg>
"""


# ---------------------------------------------------------------------------
# Footer: kleiner Nachthimmel als Abschluss.
# ---------------------------------------------------------------------------


def build_footer() -> str:
    W, H = 900, 130
    rnd = random.Random(7)
    stars = []
    for _ in range(26):
        x, y = rnd.uniform(150, W - 20), rnd.uniform(14, H - 14)
        r = rnd.uniform(0.7, 1.7)
        stars.append(
            f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.1f}" fill="#FFF3C4">'
            f'<animate attributeName="opacity" values="1;0.15;1" dur="{rnd.uniform(2, 5):.1f}s" '
            f'begin="{rnd.uniform(0, 3):.1f}s" repeatCount="indefinite"/></circle>'
        )
    text = "Gebaut bei Mondschein, mit AI und einer Tasse Kaffee zu viel."
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="title">
  <title id="title">{esc(text)}</title>
  <defs>
    <radialGradient id="halo"><stop offset="0.5" stop-color="{MOON}" stop-opacity="0.5"/><stop offset="1" stop-color="{BUTTER}" stop-opacity="0"/></radialGradient>
    <filter id="paper" x="0" y="0" width="100%" height="100%">
      <feTurbulence type="fractalNoise" baseFrequency="0.05" numOctaves="4" seed="9" result="n"/>
      <feColorMatrix in="n" type="matrix" values="0 0 0 0 0.93  0 0 0 0 0.62  0 0 0 0 0.12  0 0 0 0.6 -0.15"/>
      <feComposite in2="SourceGraphic" operator="in"/>
    </filter>
    <style>.f {{ font: 600 17px {SANS}; fill: {CREAM}; }} .m {{ font: 500 13px {MONO}; fill: {MUTED}; }}</style>
  </defs>
  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="18" fill="{INK}" stroke="{INK_3}" stroke-width="1.5"/>
  {"".join(stars)}
  <circle cx="78" cy="65" r="58" fill="url(#halo)">
    <animate attributeName="opacity" values="0.5;1;0.5" dur="6s" repeatCount="indefinite"/>
  </circle>
  <circle cx="78" cy="65" r="30" fill="{MOON}"/>
  <circle cx="78" cy="65" r="30" fill="#fff" filter="url(#paper)"/>
  <text x="150" y="60" class="f">{esc(text)}</text>
  <text x="150" y="86" class="m">// danke fürs Vorbeischauen ☾</text>
</svg>
"""


if __name__ == "__main__":
    write("header.svg", build_header())
    write("terminal.svg", build_terminal())
    write("stack.svg", build_stack())
    write("footer.svg", build_footer())
