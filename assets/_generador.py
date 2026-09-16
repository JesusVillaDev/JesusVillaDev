# -*- coding: utf-8 -*-
"""Genera el sistema de diseño SVG del perfil de GitHub.
Toda la geometría se calcula: W=1000 de lienzo, margen 40, contenido 920.
"""
import os

OUT = "/home/claude/profile"
AS = os.path.join(OUT, "assets")
os.makedirs(AS, exist_ok=True)

SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"

W = 1000
M = 40           # margen lateral
C = W - 2 * M    # 920 ancho de contenido

DARK = dict(
    name="dark",
    bg1="#0B0F14", bg2="#11161D",
    panel="#0E131A", chip="#161B22",
    border="#21262D", line="#1C2128",
    text="#E6EDF3", muted="#9198A1", faint="#6E7681",
    accent="#58A6FF", accent2="#1F6FEB", ok="#3FB950",
    grid="#8B949E", gridop="0.16", glowop="0.18",
)
LIGHT = dict(
    name="light",
    bg1="#FFFFFF", bg2="#F3F6F9",
    panel="#FFFFFF", chip="#F6F8FA",
    border="#D6DDE4", line="#E4E9EE",
    text="#1F2328", muted="#5B646E", faint="#818B98",
    accent="#0969DA", accent2="#0550AE", ok="#1A7F37",
    grid="#57606A", gridop="0.14", glowop="0.10",
)


# ─────────────────────────── utilidades ───────────────────────────
def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def wm(t, s, ls=0.0):            # ancho aprox. monoespaciada
    return len(t) * (s * 0.601 + ls)


def ws(t, s, bold=False, ls=0.0):  # ancho aprox. sans
    return len(t) * (s * (0.578 if bold else 0.536) + ls)


def txt(x, y, s, size=13, fill="#fff", anchor="start", fam=None, weight="400",
        ls=None, style=None, cls=None, italic=False):
    fam = fam or SANS
    a = [f'x="{x:.1f}"', f'y="{y:.1f}"', f'font-family="{fam}"',
         f'font-size="{size}"', f'fill="{fill}"']
    if weight != "400":
        a.append(f'font-weight="{weight}"')
    if anchor != "start":
        a.append(f'text-anchor="{anchor}"')
    if ls is not None:
        a.append(f'letter-spacing="{ls}"')
    if italic:
        a.append('font-style="italic"')
    if cls:
        a.append(f'class="{cls}"')
    if style:
        a.append(f'style="{style}"')
    return f'<text {" ".join(a)}>{esc(s)}</text>'


def rect(x, y, w, h, fill="none", stroke=None, rx=0, op=None, cls=None):
    a = [f'x="{x:.1f}"', f'y="{y:.1f}"', f'width="{w:.1f}"', f'height="{h:.1f}"',
         f'fill="{fill}"']
    if rx:
        a.append(f'rx="{rx}"')
    if stroke:
        a.append(f'stroke="{stroke}"')
        a.append('stroke-width="1"')
    if op is not None:
        a.append(f'opacity="{op}"')
    if cls:
        a.append(f'class="{cls}"')
    return f'<rect {" ".join(a)}/>'


def hline(x1, x2, y, color):
    return f'<line x1="{x1:.1f}" y1="{y:.1f}" x2="{x2:.1f}" y2="{y:.1f}" stroke="{color}" stroke-width="1"/>'


def vline(x, y1, y2, color):
    return f'<line x1="{x:.1f}" y1="{y1:.1f}" x2="{x:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="1"/>'


def svg(w, h, body, extra_defs="", style=""):
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img">\n'
        f'<defs>{extra_defs}</defs>\n'
        + (f'<style>{style}</style>\n' if style else "")
        + body + "\n</svg>\n"
    )


def panel(T, h, y=0):
    """Tarjeta base de ancho completo."""
    return rect(0.5, y + 0.5, W - 1, h - 1, fill=T["panel"], stroke=T["border"], rx=14)


def mono_chip(x, y, label, T, h=26, size=10.5, ls=1.6, fg=None, bd=None, dot=None):
    fg = fg or T["faint"]
    bd = bd or T["border"]
    tw = wm(label, size, ls)
    extra = 16 if dot else 0
    w = tw + 28 + extra
    o = [rect(x, y, w, h, fill=T["chip"], stroke=bd, rx=h / 2)]
    tx = x + 14 + extra
    if dot:
        o.append(f'<circle cx="{x + 18:.1f}" cy="{y + h/2:.1f}" r="3.2" fill="{dot}" class="pulse"/>')
    o.append(txt(tx, y + h / 2 + size * 0.36, label, size=size, fill=fg, fam=MONO, ls=ls))
    return "".join(o), w


def tech_chip(x, y, label, color, T, h=28, size=12):
    tw = ws(label, size)
    w = tw + 42
    o = [rect(x, y, w, h, fill=T["chip"], stroke=T["border"], rx=8),
         f'<circle cx="{x + 15:.1f}" cy="{y + h/2:.1f}" r="3.6" fill="{color}"/>',
         txt(x + 26, y + h / 2 + size * 0.35, label, size=size, fill=T["muted"])]
    return "".join(o), w


def chip_row(x0, y, items, T, gap=8, kind="tech"):
    """Fila de chips desde x0. Devuelve (markup, ancho_total)."""
    out, x = [], x0
    for it in items:
        if kind == "tech":
            m, w = tech_chip(x, y, it[0], it[1], T)
        else:
            m, w = mono_chip(x, y, it, T)
        out.append(m)
        x += w + gap
    return "".join(out), (x - gap - x0)


def centered_chip_row(y, items, T, gap=10, kind="tech"):
    """Mide primero, luego centra el grupo completo."""
    total = 0
    widths = []
    for it in items:
        if kind == "tech":
            w = ws(it[0], 12) + 42
        else:
            w = wm(it, 10.5, 1.6) + 28 + (16 if isinstance(it, str) and False else 0)
        widths.append(w)
        total += w
    total += gap * (len(items) - 1)
    x = (W - total) / 2
    out = []
    for it, w in zip(items, widths):
        if kind == "tech":
            m, _ = tech_chip(x, y, it[0], it[1], T)
        else:
            m, _ = mono_chip(x, y, it, T)
        out.append(m)
        x += w + gap
    return "".join(out)


# ─────────────────────────── 01 · cabecera ───────────────────────────
def header(T):
    H = 300
    defs = (
        f'<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0%" stop-color="{T["bg1"]}"/><stop offset="100%" stop-color="{T["bg2"]}"/></linearGradient>'
        f'<pattern id="grid" width="22" height="22" patternUnits="userSpaceOnUse">'
        f'<circle cx="1" cy="1" r="1" fill="{T["grid"]}" opacity="{T["gridop"]}"/></pattern>'
        f'<radialGradient id="glow" cx="50%" cy="4%" r="72%">'
        f'<stop offset="0%" stop-color="{T["accent"]}" stop-opacity="{T["glowop"]}"/>'
        f'<stop offset="100%" stop-color="{T["accent"]}" stop-opacity="0"/></radialGradient>'
        f'<clipPath id="cp"><rect x="0" y="0" width="{W}" height="{H}" rx="14"/></clipPath>'
    )
    style = (
        ".r{animation:fu .8s cubic-bezier(.2,.7,.3,1) both}"
        ".d1{animation-delay:.05s}.d2{animation-delay:.18s}.d3{animation-delay:.31s}"
        ".d4{animation-delay:.44s}.d5{animation-delay:.57s}"
        "@keyframes fu{from{opacity:0}to{opacity:1}}"
        ".rule{transform-box:fill-box;transform-origin:center;animation:gw .9s cubic-bezier(.2,.7,.3,1) .3s both}"
        "@keyframes gw{from{transform:scaleX(0)}to{transform:scaleX(1)}}"
        ".pulse{animation:pl 2.4s ease-in-out infinite}"
        "@keyframes pl{0%,100%{opacity:1}50%{opacity:.35}}"
    )
    b = ['<g clip-path="url(#cp)">',
         rect(0, 0, W, H, fill="url(#bg)"),
         rect(0, 0, W, H, fill="url(#grid)"),
         rect(0, 0, W, H, fill="url(#glow)"),
         '</g>',
         rect(0.5, 0.5, W - 1, H - 1, fill="none", stroke=T["border"], rx=14)]

    b.append(txt(W / 2, 78, "INGENIERÍA INFORMÁTICA  ·  ESPECIALIDAD BACKEND", size=12,
                 fill=T["accent"], anchor="middle", fam=MONO, ls=3.4, cls="r d1"))
    b.append(txt(W / 2, 144, "Jesús Francisco Gutiérrez Villa", size=41,
                 fill=T["text"], anchor="middle", weight="700", ls=-0.6, cls="r d2"))
    b.append(rect(W / 2 - 42, 168, 84, 3, fill=T["accent"], rx=1.5, cls="rule"))
    b.append(txt(W / 2, 210, "Backend  ·  Arquitectura de Software  ·  Bases de Datos",
                 size=16, fill=T["muted"], anchor="middle", cls="r d4"))

    chips = ["MICHOACÁN, MÉXICO", "ÚLTIMO SEMESTRE"]
    widths = [wm(c, 10.5, 1.6) + 28 for c in chips]
    ok_label = "DISPONIBLE"
    ok_w = wm(ok_label, 10.5, 1.6) + 28 + 16
    total = sum(widths) + ok_w + 20 * 2
    x = (W - total) / 2
    g = ['<g class="r d5">']
    for c, w in zip(chips, widths):
        m, _ = mono_chip(x, 238, c, T)
        g.append(m)
        x += w + 20
    m, _ = mono_chip(x, 238, ok_label, T, fg=T["ok"], bd=T["border"], dot=T["ok"])
    g.append(m)
    g.append('</g>')
    b.append("".join(g))
    return svg(W, H, "\n".join(b), defs, style)


# ─────────────────────────── 02 · perfil ───────────────────────────
PILLARS = [
    ("01", "DESARROLLO BACKEND",
     ["APIs RESTful, autenticación JWT y lógica", "de negocio con tipado estricto."]),
    ("02", "ARQUITECTURA DE SOFTWARE",
     ["Principios SOLID, separación estricta de", "responsabilidades y diseño modular."]),
    ("03", "BASES DE DATOS",
     ["Modelado relacional, normalización e", "integridad referencial con PDO."]),
]


def perfil(T):
    H = 252
    b = [panel(T, H)]
    b.append(txt(W / 2, 58, "Estudiante de Ingeniería Informática en último semestre, con especialidad en desarrollo backend.",
                 size=15, fill=T["text"], anchor="middle"))
    b.append(txt(W / 2, 82, "Diseño y construyo sistemas orientados a código limpio, seguro y mantenible.",
                 size=15, fill=T["muted"], anchor="middle"))
    b.append(hline(M, W - M, 112, T["line"]))

    cell = W / 3                 # 333.33 -> retícula regular
    centers = [cell * i + cell / 2 for i in range(3)]
    for i, (idx, title, lines) in enumerate(PILLARS):
        cx = centers[i]
        b.append(txt(cx, 148, idx, size=11, fill=T["accent"], anchor="middle", fam=MONO, ls=2.2))
        b.append(txt(cx, 174, title, size=13.5, fill=T["text"], anchor="middle", weight="600", ls=0.4))
        for j, ln in enumerate(lines):
            b.append(txt(cx, 200 + j * 19, ln, size=12.5, fill=T["muted"], anchor="middle"))
    for i in (1, 2):
        b.append(vline(cell * i, 132, 228, T["line"]))
    return svg(W, H, "\n".join(b))


# ─────────────────────────── 03 · stack ───────────────────────────
STACK = [
    ("01", "BACKEND", ["PHP", "Node.js", "Python", "Java"]),
    ("02", "FRONTEND", ["JavaScript", "HTML", "CSS", "React"]),
    ("03", "DATOS Y HERRAMIENTAS", ["MySQL", "Docker", "Git", "GitHub"]),
    ("04", "SISTEMAS", ["Linux", "Ubuntu", "Debian", "Windows"]),
]
STACK_COLORS = {
    "PHP": "#787CB5", "Node.js": "#5FA04E", "Python": "#3776AB", "Java": "#E76F00",
    "JavaScript": "#F0DB4F", "HTML": "#E34F26", "CSS": "#1572B6", "React": "#61DAFB",
    "MySQL": "#4479A1", "Docker": "#2496ED", "Git": "#F05032", "GitHub": "#8B949E",
    "Linux": "#FCC624", "Ubuntu": "#E95420", "Debian": "#A81D33", "Windows": "#0078D4",
}


def stack(T):
    H = 288
    b = [panel(T, H)]
    cell = W / 4                      # 250 -> retícula regular
    centers = [cell * i + cell / 2 for i in range(4)]
    chip_w, chip_h, gap = 188, 30, 6
    for i, (idx, cat, items) in enumerate(STACK):
        cx = centers[i]
        b.append(txt(cx, 64, idx, size=11, fill=T["accent"], anchor="middle", fam=MONO, ls=2.2))
        b.append(txt(cx, 90, cat, size=12.5, fill=T["text"], anchor="middle", weight="600", ls=0.4))
        for j, it in enumerate(items):
            y = 108 + j * (chip_h + gap)
            x = cx - chip_w / 2
            b.append(rect(x, y, chip_w, chip_h, fill=T["chip"], stroke=T["border"], rx=8))
            b.append(f'<circle cx="{x + 16:.1f}" cy="{y + chip_h/2:.1f}" r="3.6" fill="{STACK_COLORS[it]}"/>')
            b.append(txt(x + 28, y + chip_h / 2 + 4.3, it, size=12, fill=T["muted"]))
    for i in range(1, 4):
        b.append(vline(cell * i, 40, 248, T["line"]))
    return svg(W, H, "\n".join(b))


# ─────────────────────────── 04 · proyectos ───────────────────────────
def project(T, idx, title, tagline, status, techs, highlights, details):
    H = 420
    b = [panel(T, H)]
    # índice
    b.append(rect(M, 42, 34, 34, fill=T["chip"], stroke=T["border"], rx=9))
    b.append(txt(M + 17, 64, idx, size=13, fill=T["accent"], anchor="middle", fam=MONO, weight="600"))
    b.append(txt(M + 48, 66, title, size=23, fill=T["text"], weight="700", ls=-0.3))
    # chips de estado, alineados a la derecha
    ws_ = [wm(s, 10.5, 1.6) + 28 for s in status]
    x = W - M - sum(ws_) - 8 * (len(status) - 1)
    for s, w in zip(status, ws_):
        m, _ = mono_chip(x, 46, s, T)
        b.append(m)
        x += w + 8
    b.append(txt(M, 106, tagline, size=14, fill=T["muted"], italic=True))
    r, _ = chip_row(M, 130, techs, T, gap=8)
    b.append(r)
    b.append(hline(M, W - M, 188, T["line"]))
    for j, (lab, rest) in enumerate(highlights):
        y = 216 + j * 28
        b.append(f'<circle cx="{M + 4}" cy="{y - 4}" r="2.6" fill="{T["accent"]}"/>')
        b.append(f'<text x="{M + 18}" y="{y}" font-family="{SANS}" font-size="13.5">'
                 f'<tspan fill="{T["text"]}" font-weight="600">{esc(lab)}</tspan>'
                 f'<tspan fill="{T["muted"]}">{esc(rest)}</tspan></text>')
    b.append(txt(M, 310, "DETALLES TÉCNICOS", size=10.5, fill=T["faint"], fam=MONO, ls=2.4))
    b.append(hline(M + 150, W - M, 306, T["line"]))
    for j, (lab, rest) in enumerate(details):
        y = 338 + j * 24
        b.append(f'<text x="{M + 18}" y="{y}" font-family="{SANS}" font-size="12.5">'
                 f'<tspan fill="{T["muted"]}" font-weight="600">{esc(lab)}</tspan>'
                 f'<tspan fill="{T["faint"]}">{esc(rest)}</tspan></text>')
    return svg(W, H, "\n".join(b))


P1 = dict(
    idx="01", title="EnfocaKids",
    tagline="Plataforma web modular de evaluación cognitiva infantil y soporte escolar con telemetría en tiempo real.",
    status=["INNOVATECNM 2024", "REPOSITORIO PRIVADO"],
    techs=[("PHP 8.3", "#787CB5"), ("MySQL", "#4479A1"), ("JavaScript", "#F0DB4F"),
           ("CSS", "#1572B6"), ("JWT", "#8957E5")],
    highlights=[
        ("Rendimiento", " — Arquitectura 100 % Vanilla Web, sin frameworks, con tiempos de carga mínimos."),
        ("Seguridad y control", " — API RESTful en PHP 8.3 con tipado estricto, JWT y aislamiento de datos por tutor."),
        ("Telemetría cognitiva", " — Tiempos de reacción y precisión en tiempo real, con cálculo de baremos psicométricos."),
    ],
    details=[
        ("Principios SOLID", " — Separación estricta de responsabilidades y desacople completo de los clientes HTTP."),
        ("Modelo relacional", " — Esquema MySQL normalizado, integridad referencial y consultas preparadas con PDO."),
        ("Módulos independientes", " — Aislamiento entre actividades lúdicas cognitivas y componentes escolares."),
    ],
)
P2 = dict(
    idx="02", title="Portafolio Personal",
    tagline="Espacio profesional para presentación técnica de ingeniería, casos de estudio y demostraciones interactivas.",
    status=["EN DESARROLLO", "PRÓXIMAMENTE EN LÍNEA"],
    techs=[("React", "#61DAFB"), ("Node.js", "#5FA04E"), ("CSS3", "#1572B6"),
           ("GitHub Pages", "#8B949E")],
    highlights=[
        ("Diseño UI/UX", " — Interfaz con tema oscuro, microinteracciones fluidas y tipografía cuidada."),
        ("Casos de estudio", " — Desglose técnico de decisiones de arquitectura, diseño y problemas resueltos."),
        ("Diseño adaptativo", " — Maquetación totalmente responsiva, optimizada para móvil y escritorio."),
    ],
    details=[
        ("Componentes modulares", " — Estructura reutilizable centrada en rendimiento y buenas prácticas."),
        ("Documentación técnica", " — Resúmenes de arquitectura y métricas de los proyectos destacados."),
        ("Despliegue continuo", " — Flujo de integración y publicación automatizada."),
    ],
)


# ─────────────────────────── 05 · trayectoria ───────────────────────────
TRAYECTORIA = [
    ("01", "InnovaTecNM 2024",
     ["Participación en el certamen nacional", "de innovación tecnológica organizado", "por el TecNM."]),
    ("02", "Certificación técnica",
     ["Formación continua en sistemas backend,", "bases de datos relacionales y", "arquitectura de software."]),
    ("03", "Hackathons y retos",
     ["Resolución colaborativa de", "problemas algorítmicos y de", "lógica de sistemas."]),
]


def trayectoria(T):
    H = 192
    b = [panel(T, H)]
    cell = W / 3
    centers = [cell * i + cell / 2 for i in range(3)]
    for i, (idx, title, lines) in enumerate(TRAYECTORIA):
        cx = centers[i]
        b.append(txt(cx, 56, idx, size=11, fill=T["accent"], anchor="middle", fam=MONO, ls=2.2))
        b.append(txt(cx, 82, title, size=14.5, fill=T["text"], anchor="middle", weight="600", ls=-0.1))
        for j, ln in enumerate(lines):
            b.append(txt(cx, 108 + j * 19, ln, size=12.5, fill=T["muted"], anchor="middle"))
    for i in (1, 2):
        b.append(vline(cell * i, 40, 152, T["line"]))
    return svg(W, H, "\n".join(b))


def intereses(T):
    H = 92
    items = ["FÚTBOL", "VOLEIBOL", "VIDEOJUEGOS", "AUTODIDACTA"]
    b = [panel(T, H)]
    cell = W / 4
    for i, it in enumerate(items):
        cx = cell * i + cell / 2
        b.append(txt(cx, 51, it, size=12.5, fill=T["muted"], anchor="middle", fam=MONO, ls=2.6))
    for i in range(1, 4):
        b.append(vline(cell * i, 26, 66, T["line"]))
    return svg(W, H, "\n".join(b))


# ─────────────────────────── 06 · botones de contacto ───────────────────────────
def button(T, label, value):
    BW, BH = 250, 60
    b = [rect(0.5, 0.5, BW - 1, BH - 1, fill=T["chip"], stroke=T["border"], rx=12),
         txt(20, 25, label, size=9.5, fill=T["faint"], fam=MONO, ls=2.2),
         txt(20, 44, value, size=12.5, fill=T["text"], weight="500"),
         f'<path d="M{BW-30} 32 l10 -10 M{BW-28} 22 h8 v8" stroke="{T["accent"]}" '
         f'stroke-width="1.6" fill="none" stroke-linecap="round" stroke-linejoin="round"/>']
    return svg(BW, BH, "\n".join(b))


def footer(T):
    H = 70
    defs = (f'<linearGradient id="fg" x1="0" y1="0" x2="1" y2="0">'
            f'<stop offset="0%" stop-color="{T["accent"]}" stop-opacity="0"/>'
            f'<stop offset="50%" stop-color="{T["accent"]}" stop-opacity="0.75"/>'
            f'<stop offset="100%" stop-color="{T["accent"]}" stop-opacity="0"/></linearGradient>')
    b = [rect(0, 0, W, 2, fill="url(#fg)"),
         txt(W / 2, 44, "github.com/JesusGutzVil", size=12, fill=T["faint"],
             anchor="middle", fam=MONO, ls=2.4)]
    return svg(W, H, "\n".join(b), defs)


# ─────────────────────────── escritura ───────────────────────────
def write(name, content):
    with open(os.path.join(AS, name), "w", encoding="utf-8") as f:
        f.write(content)


for T in (DARK, LIGHT):
    s = T["name"]
    write(f"header-{s}.svg", header(T))
    write(f"perfil-{s}.svg", perfil(T))
    write(f"stack-{s}.svg", stack(T))
    write(f"proyecto-01-{s}.svg", project(T, **P1))
    write(f"proyecto-02-{s}.svg", project(T, **P2))
    write(f"trayectoria-{s}.svg", trayectoria(T))
    write(f"intereses-{s}.svg", intereses(T))
    write(f"footer-{s}.svg", footer(T))
    write(f"btn-correo-{s}.svg", button(T, "CORREO", "jesusfgv.dev@gmail.com"))
    write(f"btn-linkedin-{s}.svg", button(T, "LINKEDIN", "in/jesusfgv"))
    write(f"btn-github-{s}.svg", button(T, "GITHUB", "JesusGutzVil"))

print("OK:", len(os.listdir(AS)), "archivos")
for f in sorted(os.listdir(AS)):
    print("  ", f, os.path.getsize(os.path.join(AS, f)), "bytes")
