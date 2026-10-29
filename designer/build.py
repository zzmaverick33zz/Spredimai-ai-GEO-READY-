#!/usr/bin/env python3
"""Builds the three designer variants (a.html dark, b.html editorial, c.html Swiss) from one content set.
Content = our real photos, videos and texts (see MEDIA_MAP.md); structure and look follow the designer's mock-ups.
Run: python3 build.py"""
import html

FONTS = {
 'a': 'Space+Grotesk:wght@300;400;500;600&family=Hanken+Grotesk:wght@300;400;500;600',
 'b': 'Instrument+Serif:ital@0;1&family=Hanken+Grotesk:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500',
 'c': 'Inter+Tight:wght@300;400;500;600;700&family=Hanken+Grotesk:wght@300;400;500;600',
}
THEME = {'a': '#101a17', 'b': '#f3efe8', 'c': '#ecece6'}
DESC = 'Bog oak and bog ash, carbon-dated and crafted in Lithuania. Technical specification, products and project consultation for architects, designers and interior specialists.'

def vid(name, label, cls='', eager=False):
    return (f'<div class="vid {cls}"><video muted loop playsinline preload="{"metadata" if eager else "none"}" poster="media/{name}-poster.webp" role="img" aria-label="{html.escape(label)}">'
            f'<source src="media/{name}-hd.mp4" type="video/mp4" media="(min-width: 1100px)"><source src="media/{name}-sd.mp4" type="video/mp4"><source src="media/{name}-hd.webm" type="video/webm"></video></div>')
def pic(f, alt, w, h, cls='', eager=False):
    return f'<figure class="pic {cls}"><img src="media/{f}.webp" alt="{html.escape(alt)}" width="{w}" height="{h}" {"" if eager else "loading=\"lazy\" "}decoding="async"></figure>'

SPECIES = [('bog-oak', 'Bog oak', 's14-img', 'Ancient', 1006, 1341, 'Bog oak chevron parquet'), ('bog-ash', 'Bog ash', 's15-img', 'Ancient', 1200, 1600, 'Bog ash pentagon parquet'),
           ('black-walnut', 'Black walnut', 's19-img', 'From the forest', 324, 432, 'Black walnut parquet in a broken geometric pattern'), ('elm', 'Elm', 's17-img', 'From the forest', 770, 1027, 'Elm slab with golden grain'),
           ('oak', 'Oak', 's16-img', 'From the forest', 1200, 1600, 'Oak floor laid in a sunburst pattern'), ('ash', 'Ash', 's18-img', 'From the forest', 1200, 1600, 'Ash planks with pale, flowing grain')]
STEPS = [('An oak falls into the water', 'Long before us, trees fell into lakes and peat bogs and sank into the silt.'),
         ('Sealed from oxygen', 'Without oxygen the wood does not rot. Over centuries, tannins react with minerals and the timber turns from gold to deep brown and black.'),
         ('Found and raised', 'Our divers have searched the deepest lakes for more than twenty years. Each piece is chosen by hand.'),
         ('Dated', 'A sample from the trunk is carbon-dated. The result tells us when the tree was alive.'),
         ('Slow drying', 'Wood that has lived under water comes out saturated. It is dried slowly and under control, because rushing this step cracks it.'),
         ('Crafted and installed', 'Made into multilayer boards in our workshop in Lithuania, and laid by our own craftsmen.')]
PRODUCTS = [('Bog wood floors', 'Planks and parquet in bog oak and bog ash', 's20-floors', 1007, 1258, 'A bright room with a dark parquet floor in a wide pattern and a glass door',
             'Multilayer boards in bog oak and bog ash. Every board is dated, dried slowly and finished by hand, stable with changes in temperature and humidity and compatible with underfloor heating.', ['Multilayer', 'Bog oak', 'Bog ash', 'Underfloor heating', 'Carbon-dated'], None),
            ('Parquet patterns', 'Chevron, herringbone and custom geometries', 's14-img', 1006, 1341, 'Bog oak chevron parquet',
             'Pattern is part of the design. We design, stain, pattern and finish every board in our workshop, from chevron and herringbone to fully custom layouts drawn by you.', ['Chevron', 'Herringbone', 'Custom layouts'], 'patterns'),
            ('Walls & ceilings', 'Cladding and ceilings matched to the floor batch', 's22-img', 1500, 1875, 'A bedroom with wood-panelled walls',
             'The same wood continues up the wall and across the ceiling, so the whole room reads as one material.', ['Wall cladding', 'Ceilings', 'Made to measure'], 'walls'),
            ('Stairs', 'Treads and risers in the same batch as the floor', 's21-stairs', 1007, 1258, 'Oak stair treads and a white wall in a modern house',
             'Stair treads and risers, made to your drawings and matched to the floor.', ['Treads', 'Risers', 'Made to measure'], 'stairs'),
            ('Tables & wine cellars', 'Furniture and cellars from solid bog wood', 's24-img', 1007, 1259, 'A dark wooden table with a live edge in a dark room',
             'Tables, wine cellars and other pieces, crafted by hand from the same wood as the floor.', ['Tables', 'Wine cellars', 'Bespoke'], 'tables')]
ENVS = [('Residences & villas', 'Wide planks, parquet, stairs and walls for homes where every surface is considered.', 'Floors · Walls · Stairs', 's28-img', 1025, 1281, 'A living room with oak walls and warm lighting'),
        ('Superyachts', 'Stable multilayer boards for interiors that live with changing temperature and humidity.', 'Floors · Cabinetry', 's26-img', 1280, 720, 'A yacht saloon with a round dining table on a pale wooden floor'),
        ('Commercial spaces', 'Floors, walls and ceilings made to measure for lobbies, showrooms and public interiors.', 'Floors · Walls · Ceilings', 's29-img', 682, 853, 'A lobby with a staircase and a pale wooden floor')]
PROCESS = [('Tell us about the project', 'Describe the space and share plans, references and the mood you are after.'), ('Consultation', 'We invite you to talk it through: species, pattern, format and finish for your project.'),
           ('Proposal & approval', 'The material, pattern and finish are agreed with you before production starts.'), ('Made & installed', 'Produced in our workshop in Lithuania and installed by our own craftsmen, wherever your project is.')]
ABOUT_P = 'We craft our wood in Lithuania. The craft has passed through three generations of our family, and bog wood asks for all of it.'
FACTS = [('3rd', 'Generation of woodworkers'), ('20+', 'Years diving for bog wood'), ('LT · ES', 'Workshop in Lithuania, showroom in Marbella')]
HOT = [('Tannins meet minerals', 'In oxygen-free water, tannins in the wood react with minerals and slowly darken it.'), ('No two logs are alike', 'Some are honey-brown, some nearly black. The water decided, not us.'),
       ('Raised, not felled', 'The trees were never cut down. Each trunk is located by hand and lifted.'), ('Dated', 'A sample from the trunk is carbon-dated, so the age is known, not guessed.')]
HOTPOS = [(24, 30), (70, 24), (55, 62), (22, 78)]
PROJ = [('s27-img', 1123, 1404, 'A staircase and timber walls in a private residence'), ('s28-img', 1025, 1281, 'A living room with oak walls and warm lighting'), ('s29-img', 682, 853, 'A lobby with a staircase and a pale wooden floor'), ('s30-img', 1029, 1286, 'A double-height living room with wood walls')]

NAV = [('#origin', 'Origin'), ('#make', 'Products'), ('#species', 'Species'), ('#specify', 'Specification'), ('#process', 'Process'), ('#projects', 'Projects')]

def head(t, title):
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{DESC}">
<meta name="theme-color" content="{THEME[t]}">
<meta property="og:title" content="{title}"><meta property="og:description" content="{DESC}"><meta property="og:type" content="website">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 32 32%27%3E%3Crect width=%2732%27 height=%2732%27 fill=%27%23101a17%27/%3E%3Ccircle cx=%2716%27 cy=%2716%27 r=%2710%27 fill=%27none%27 stroke=%27%23C29A62%27/%3E%3Ccircle cx=%2716%27 cy=%2716%27 r=%275%27 fill=%27none%27 stroke=%27%23C29A62%27/%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family={FONTS[t]}&display=swap" media="print" onload="this.media='all'">
<noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family={FONTS[t]}&display=swap"></noscript>
<link rel="stylesheet" href="css/base.css">
<link rel="stylesheet" href="css/theme-{t}.css">
</head>
<body class="t-{t}">
<a class="skip" href="#main">Skip to content</a>
'''

def header(t, logo):
    links = ''.join(f'<a href="{h}">{n}</a>' for h, n in NAV)
    drawer = ''.join(f'<a href="{h}">{n}</a>' for h, n in NAV)
    return f'''<header class="hd" id="hdr"><div class="w hd__row">
  <a class="logo" href="#top">{logo}</a>
  <nav class="nav" aria-label="Main">{links}</nav>
  <a class="btn btn--line hd__cta" href="#consultation">Book a consultation</a>
  <button class="menu-btn" id="menuBtn" aria-expanded="false" aria-controls="drawer" aria-label="Open menu"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M3 7h18M3 12h18M3 17h18"/></svg></button>
</div></header>
<div class="drawer" id="drawer" hidden>{drawer}<a class="btn btn--solid" href="#consultation">Book a consultation</a></div>
<main id="main">
'''

def chips(name, items, kind='checkbox', pre=''):
    out = ''
    for i, (val, label, chk) in enumerate(items):
        out += f'<input type="{kind}" id="{pre}{i}" name="{name}" value="{val}"{" checked" if chk else ""}><label for="{pre}{i}">{label}</label>'
    return out

def form_html():
    return f'''<form id="form" class="frm" novalidate>
  <div class="row2"><div class="field"><label for="f-name">Name and studio</label><input id="f-name" name="name" autocomplete="name" required></div>
  <div class="field"><label for="f-email">Email</label><input id="f-email" name="email" type="email" autocomplete="email" required><span class="err" id="f-email-err" hidden>Enter an email like name@domain.com</span></div></div>
  <div class="row2"><div class="field"><label for="f-country">Project location</label><input id="f-country" name="country" autocomplete="country-name" placeholder="City, country"></div>
  <div class="field"><label for="f-time">Timeline</label><select id="f-time" name="timeline"><option>Within 3 months</option><option selected>3–12 months</option><option>Later / exploring</option></select></div></div>
  <fieldset class="field"><legend>Project type</legend><div class="chips">{chips('project', [('residence','Residence',1),('yacht','Superyacht',0),('commercial','Commercial',0),('other','Other',0)], 'radio', 'p')}</div></fieldset>
  <fieldset class="field"><legend>Material</legend><div class="chips">{chips('species', [('bog oak','Bog oak',0),('bog ash','Bog ash',0),('black walnut','Black walnut',0),('elm','Elm',0),('oak','Oak',0),('ash','Ash',0)], 'checkbox', 'm')}</div></fieldset>
  <fieldset class="field"><legend>I need</legend><div class="chips">{chips('need', [('floors','Floors',1),('patterns','Patterns',0),('walls and ceilings','Walls &amp; ceilings',0),('stairs','Stairs',0),('tables and cellars','Tables &amp; cellars',0),('documents','Documents',0)], 'checkbox', 'n')}</div></fieldset>
  <div class="field"><label for="f-msg">About the project</label><textarea id="f-msg" name="message" placeholder="Describe the project: the space, its size, the style, who is involved. Add links to plans or references."></textarea><small>Drawings can be shared during the consultation.</small></div>
  <div><button class="btn btn--solid" type="submit">Book a consultation</button></div>
</form>
<div class="form-done" id="formDone" hidden role="status"><h3>Thank you.</h3><p>Your request is in. We will be in touch to arrange a consultation. <span id="stubNote">(Prototype: nothing was sent.)</span></p></div>'''

def contact():
    return '''<div class="contact-block"><span class="lbl">Direct</span><span>info@bffloors.com</span><span>+1 (801) 608 6876</span><span><a href="https://www.instagram.com/big_foot_parquet/" target="_blank" rel="noopener">Instagram @big_foot_parquet</a></span></div>
<div class="contact-block"><span class="lbl">Showroom · Veneks Boutique</span><span>Calle Santa Maria 10, San Pedro de Alcántara, 29670 Marbella</span><span>+370 615 85000</span><span>dainius@veneksboutique.es</span></div>'''

def spec_core(extra_swatch=False):
    sw = '<div class="spec__swatch" data-spec-swatch aria-hidden="true"></div>' if extra_swatch else ''
    return f'''<div class="spec__tabs" role="tablist" aria-label="Species" data-spec-tabs></div>
{sw}<div class="spec__head"><span class="spec__kind" data-spec-kind></span><h3 data-spec-title></h3><p data-spec-note></p></div>
<dl class="spec__rows" data-spec-rows></dl>
<p class="spec__tbc" data-spec-tbc hidden>Values marked <b>TBC</b> come from the design mock-up and are awaiting confirmation by Big Foot Floors.</p>
<a class="btn btn--solid" href="#consultation" data-prefill="spec">Discuss this specification</a>'''

def dates_block():
    return '''<div class="dates-wrap"><ol class="dates" data-samples-list aria-label="Radiocarbon ages of dated samples, in years before present"></ol>
<div class="dates__axis" data-samples-axis aria-hidden="true"></div><p class="mat__src" data-samples-src></p>
<noscript><p class="mat__src">Radiocarbon ages of recent samples range from 274 to 3,334 years (BP). Source: protocol BGRL-357, Nature Research Centre, Vilnius, 2025.</p></noscript></div>'''

def tones():
    return '<ol class="tones" aria-label="Four tones of timber, from light to black">' + ''.join(
        f'<li class="tone"><figure><img src="media/tone{i}.webp" width="480" height="640" loading="lazy" decoding="async" alt="Close-up of timber in a {n.lower()} tone"></figure><span class="tone__n">{r}</span><b>{n}</b></li>'
        for i, (n, r) in enumerate([('Honey', 'I'), ('Umber', 'II'), ('Ash grey', 'III'), ('Ink black', 'IV')], 1)) + '</ol>'

def accordion():
    out = '<ul class="mk">'
    for i, (name, desc, img, w, h, alt, txt, tags, pre) in enumerate(PRODUCTS):
        o = i == 0
        btn = f'<a class="btn btn--line" href="#specify">See the specification</a>' if pre is None else f'<a class="btn btn--line" href="#consultation" data-prefill="{pre}">Discuss this</a>'
        out += (f'<li class="mk__item{" is-open" if o else ""}"><button class="mk__row" type="button" aria-expanded="{str(o).lower()}" aria-controls="mk-{i}" data-cursor="Open"><span class="mk__no">{i+1:02d}</span><span class="mk__name">{name.replace("&", "&amp;")}</span><span class="mk__desc">{desc}</span>'
                f'<img class="mk__thumb" src="media/{img}.webp" alt="" width="120" height="150" loading="lazy" decoding="async"><i class="mk__plus" aria-hidden="true"></i></button>'
                f'<div class="mk__panel" id="mk-{i}"><div class="mk__inner"><figure class="mk__img"><img src="media/{img}.webp" alt="{alt}" width="{w}" height="{h}" loading="lazy" decoding="async"></figure>'
                f'<div class="mk__txt"><p>{txt}</p><ul class="tags">{"".join(f"<li>{t}</li>" for t in tags)}</ul>{btn}</div></div></div></li>')
    return out + '</ul>'

def species_discs():
    return '<ul class="spcA" data-species-list>' + ''.join(
        f'<li><button type="button" class="spc__b" data-species="{i}"><span class="spc__disc"><img src="media/{img}.webp" alt="" width="300" height="300" loading="lazy" decoding="async"><svg viewBox="-50 -50 100 100" aria-hidden="true" class="spc__rings"></svg></span><b>{n}</b><em class="{"is-anc" if tag=="Ancient" else ""}">{tag}</em></button></li>'
        for i, n, img, tag, *_ in SPECIES) + '</ul>'

def projects_reel(title_cls=''):
    return '<div class="reel" id="reel" tabindex="0" aria-label="Projects, scroll sideways" data-cursor="Drag">' + ''.join(
        f'<article class="proj">{pic(f, a, w, h)}<div class="proj__meta"><span>Private commission</span><span>Details on request</span></div><h3>Private residence</h3></article>' for f, w, h, a in PROJ) + '</div>'

def footer(t, extra=''):
    return f'''</main>
<footer class="ftr"><div class="w">
  <div class="ftr__grid">
    <div><a class="logo" href="#top">{LOGO[t]}</a></div>
    <div><h3>Material</h3><ul><li><a href="#origin">Origin</a></li><li><a href="#species">Species</a></li></ul></div>
    <div><h3>For specifiers</h3><ul><li><a href="#specify">Specification toolkit</a></li><li><a href="#make">Products</a></li><li><a href="#process">Process</a></li><li><a href="#consultation">Book a consultation</a></li></ul></div>
    <div><h3>On bffloors.com</h3><ul><li><a href="https://bffloors.com/bog-oak/" rel="noopener">Bog Oak</a></li><li><a href="https://bffloors.com/bog-ash/" rel="noopener">Bog Ash</a></li><li><a href="https://bffloors.com/material/" rel="noopener">Materials</a></li></ul></div>
    <div><h3>Contact</h3><ul><li>info@bffloors.com</li><li><a href="https://www.instagram.com/big_foot_parquet/" target="_blank" rel="noopener">Instagram @big_foot_parquet</a></li></ul></div>
  </div>
  <div class="ftr__base"><span>© 2026 Big Foot Floors</span><span>Crafted in Lithuania</span></div>
  {extra}
</div></footer>
<script src="js/core.js"></script><script src="js/data/samples.js"></script><script src="js/data/spec.js"></script><script src="js/effects/cursor.js"></script><script src="js/site.js"></script>
</body></html>
'''

LOGO = {'a': '<b>BIG FOOT</b><span>FLOORS · BOG WOOD</span>', 'b': '<b>Big Foot <i>Floors</i></b><span>Bog wood · Lithuania</span>', 'c': '<b>Big Foot Floors</b>'}
RV = ' rv'
HERO_VID = ('s01-hero', 'Underwater: a huge ancient trunk resting on a lake bed')
HERO_P = 'Ancient bog oak and bog ash, carbon-dated and handcrafted in Lithuania into floors, stairs, walls and bespoke interiors, specified for architects, designers and interior specialists.'

# ---------------------------------------------------------------- A: dark
def page_a():
    h = head('a', 'Big Foot Floors — Bog Wood for architects and designers (A, dark)') + header('a', LOGO['a'])
    h += f'''<section class="hA" id="top" aria-labelledby="h-hero">
  {vid(*HERO_VID, cls="hA__media", eager=True)}
  <div class="w hA__body">
    <h1 id="h-hero">Raised from the water. <b>Made for the room.</b></h1>
    <div class="hA__side"><p>{HERO_P}</p><div class="hA__cta"><a class="btn btn--solid" href="#consultation">Book a consultation</a><a class="btn btn--line" href="#specify">Specification toolkit</a></div></div>
  </div>
</section>
<section class="sec" id="origin" aria-labelledby="h-origin"><div class="w">
  <header class="hA2{RV}"><h2 id="h-origin">A lead time of centuries, <b>even millennia.</b></h2><p>Bog trees were never cut down. They fell into lakes and bogs long ago, and the water kept them. Every trunk is located by hand, lifted, dated and slowly dried before a single board is made.</p></header>
  <ol class="tlA{RV}">{"".join(f'<li><span class="tlA__t"><b>{n}</b><span>{p}</span></span></li>' for (n, p) in STEPS)}</ol>
</div></section>
<section class="sec alt" id="make" aria-labelledby="h-make"><div class="w">
  <header class="hA2{RV}"><h2 id="h-make">What we make <b>for your project.</b></h2><p>Floors are where we started. Today the same wood becomes stairs, walls, ceilings, tables and wine cellars, made to measure for each project.</p></header>
  <div class="{RV}">{accordion()}</div>
</div></section>
<section class="sec" id="environments" aria-labelledby="h-env"><div class="w">
  <header class="hA2{RV}"><h2 id="h-env">One material. <b>Three environments.</b></h2><p>From private homes to yachts and commercial interiors, the material follows the room: the same wood, matched across floors, walls, stairs and ceilings.</p></header>
  <div class="envA">{"".join(f'<article class="envA__c{RV}" data-cursor="View">{pic(img, alt, w, hh)}<div class="envA__t"><h3>{n}</h3><p>{p}</p><span>{m}</span></div></article>' for n, p, m, img, w, hh, alt in ENVS)}</div>
</div></section>
<section class="sec alt" id="species" aria-labelledby="h-species"><div class="w">
  <header class="hA2{RV}"><h2 id="h-species">Six species. <b>Two of them ancient.</b></h2><p>Bog oak and bog ash are our signature. Alongside them we work with oak, elm, ash and black walnut. Choose a species to see its specification.</p></header>
  <div class="{RV}">{species_discs()}</div>
</div></section>
<section class="sec" id="colour" aria-labelledby="h-colour"><div class="w">
  <header class="hA2{RV}"><h2 id="h-colour">Coloured by time, <b>not by stain.</b></h2><p>Long years under water and peat leave their mark on a trunk: its colour, its age, its character. Every board carries a record of that.</p></header>
  <div class="{RV}">{tones()}</div>
  <div class="colA{RV}"><h3 class="lblA">Examples from the latest laboratory protocol</h3>{dates_block()}</div>
</div></section>
<section class="sec alt" id="specify" aria-labelledby="h-spec"><div class="w specA">
  <div class="specA__side{RV}"><span class="lblA">Specification toolkit</span><h2 id="h-spec">Specify it <b>with confidence.</b></h2><p>Everything you need to write the material into your drawings. Ask for any of these during your consultation.</p><div class="spec__tabs" role="tablist" aria-label="Species" data-spec-tabs></div><ul class="docs" data-docs></ul></div>
  <div class="specA__card{RV}"><div class="spec__head"><span class="spec__kind" data-spec-kind></span><h3 data-spec-title></h3><p data-spec-note></p></div><dl class="spec__rows" data-spec-rows></dl><p class="spec__tbc" data-spec-tbc hidden>Values marked <b>TBC</b> come from the design mock-up and are awaiting confirmation by Big Foot Floors.</p><a class="btn btn--solid" href="#consultation" data-prefill="spec">Discuss this specification</a></div>
</div></section>
<section class="sec" id="process" aria-labelledby="h-process"><div class="w">
  <header class="hA2{RV}"><h2 id="h-process">From first sketch <b>to final board.</b></h2><p>One conversation, one team, from the first drawing to the last board laid.</p></header>
  <ol class="pr prA">{"".join(f'<li class="{RV.strip()}"><span class="pr__n">{i:02d}</span><h3>{n}</h3><p>{p}</p></li>' for i, (n, p) in enumerate(PROCESS, 1))}</ol>
</div></section>
<section class="sec alt" id="projects" aria-labelledby="h-proj"><div class="w">
  <header class="hA2{RV}"><h2 id="h-proj">Selected work, <b>around the world.</b></h2><p>Residences in Norway, Switzerland, France, Germany, Cyprus and the USA, and yachts. We respect our clients’ privacy, so we do not always share the name or photos of a project.</p></header>
  {projects_reel()}
  <div class="reel-nav"><button type="button" aria-label="Previous" data-dir="-1">←</button><button type="button" aria-label="Next" data-dir="1">→</button></div>
  <div class="aboutA{RV}">{pic("s31-img", "A woodworker standing beside a finished dark oak cabinet in the workshop", 883, 1104)}<div><span class="lblA">Big Foot Floors</span><h3>Three generations of woodworking, in the heart of Europe</h3><p>{ABOUT_P}</p><div class="facts">{"".join(f'<div class="fact"><b>{b}</b><span>{s}</span></div>' for b, s in FACTS)}</div></div></div>
</div></section>
<section class="cA" id="consultation" aria-labelledby="h-con">
  <div class="cA__bg" aria-hidden="true"><img src="media/s21-stairs.webp" alt="" width="1007" height="1258" loading="lazy" decoding="async"></div>
  <div class="w cA__grid">
    <div class="cA__side"><h2 id="h-con">Tell us about <b>your project.</b></h2><p>Describe your project and we will invite you to a consultation to talk it through.</p>{contact()}</div>
    <div class="cA__card">{form_html()}</div>
  </div>
</section>
'''
    return h + footer('a')

# ---------------------------------------------------------------- B: editorial
def page_b():
    h = head('b', 'Big Foot Floors — Bog Wood for architects and designers (B, editorial)') + header('b', LOGO['b'])
    stages = [('Found', 'Located by divers in lakes and peat bogs, then chosen by hand.', vid('s03-dive', 'A diver with a torch inspects a trunk on the lake bed', 'stB__m')),
              ('Raised & dated', 'Lifted from the water; a sample is carbon-dated.', pic('s06-img', 'Cross-section disc of a bog trunk by the lake, measured with a tape', 1024, 640, 'stB__m')),
              ('Dried slowly', 'Dried slowly and under control: rushing this step cracks the wood.', pic('s09-img', 'Stacks of boards drying in the kiln', 1200, 750, 'stB__m')),
              ('Crafted by hand', 'Cut, layered, stained and finished by hand in our workshop in Lithuania.', vid('s10-hands', 'Hands cutting a layered board in the workshop', 'stB__m'))]
    rows = [('Residences & villas', ENVS[0][1], 's28-img', 1025, 1281, ENVS[0][6]), ('Superyachts', ENVS[1][1], 's26-img', 1280, 720, ENVS[1][6]), ('Commercial spaces', ENVS[2][1], 's29-img', 682, 853, ENVS[2][6]), ('Wine cellars & furniture', 'Cellars, tables and pieces crafted by hand from the same wood as the floor.', 's25-img', 1024, 576, 'A wine cellar with wooden racks and arched alcoves')]
    h += f'''<section class="hB" id="top" aria-labelledby="h-hero"><div class="w hB__grid">
  <div class="hB__txt"><h1 id="h-hero">Wood the water kept for <em>millennia.</em></h1><p>{HERO_P}</p>
    <div class="hB__cta"><a class="btn btn--solid" href="#consultation">Book a consultation</a><a class="btn btn--line" href="#specify">Open the specification</a></div>
    <div class="age" data-age><span class="age__k">The age of the wood · recent radiocarbon samples</span><div class="age__bar"><i class="age__line"></i></div><div class="age__axis" aria-hidden="true"></div></div></div>
  {vid(*HERO_VID, cls="hB__media", eager=True)}
</div></section>
<section class="sec" id="origin" aria-labelledby="h-origin"><div class="w">
  <header class="shB{RV}"><span class="idx">01 / Origin</span><h2 id="h-origin">From the water to your room, <em>never cut down.</em></h2><p>Bog trees fell into lakes and bogs long ago, and the water kept them. Every trunk is located by hand, lifted, dated and slowly dried before a single board is made.</p></header>
  <div class="stB">{"".join(f'<article class="stB__c{RV}"><span class="idx">Stage {i:02d}</span>{m}<h3>{n}</h3><p>{p}</p></article>' for i, (n, p, m) in enumerate(stages, 1))}</div>
</div></section>
<section class="sec" id="species" aria-labelledby="h-species"><div class="w">
  <header class="shB{RV}"><span class="idx">02 / Material edition</span><h2 id="h-species">Six woods. One standard of <em>patience.</em></h2><p>Bog oak and bog ash are our signature. Alongside them we work with oak, elm, ash and black walnut. Choose a wood to see its specification.</p></header>
  <ul class="wdB{RV}">{"".join(f'<li><a href="#specify" data-species="{i}" class="wdB__a">{pic(img, alt, w, hh)}<b>{n}</b><span class="tagB{" is-anc" if tag=="Ancient" else ""}">{tag}</span></a></li>' for i, n, img, tag, w, hh, alt in SPECIES)}</ul>
</div></section>
<section class="sec" id="environments" aria-labelledby="h-env"><div class="w">
  <header class="shB{RV}"><span class="idx">03 / Where it lives</span><h2 id="h-env">Built for land, sea <em>and air.</em></h2><p>From private homes to yachts and commercial interiors, the material follows the room. Residences in Norway, Switzerland, France, Germany, Cyprus and the USA, and yachts.</p></header>
  <ul class="rwB">{"".join(f'<li class="{RV.strip()}"><span class="idx">{i:02d}</span><h3>{n.replace("&", "&amp;")}</h3><p>{p}</p>{pic(img, alt, w, hh)}</li>' for i, (n, p, img, w, hh, alt) in enumerate(rows, 1))}</ul>
</div></section>
<section class="sec band" id="specify" aria-labelledby="h-spec"><div class="w spB">
  <div class="spB__side{RV}"><span class="idx">04 / The specification</span><h2 id="h-spec">Everything you need to <em>write it into the drawings.</em></h2><p>Technical information for each wood, ready before the first call. Ask for any of these documents during your consultation.</p>
    <ul class="docs" data-docs></ul></div>
  <div class="spB__card{RV}"><span class="idx" data-spec-kind></span>{spec_core(True).replace('<span class="spec__kind" data-spec-kind></span>', '')}</div>
</div></section>
<section class="sec" id="colour" aria-labelledby="h-colour"><div class="w">
  <header class="shB{RV}"><span class="idx">05 / Colour and age</span><h2 id="h-colour">Coloured by time. <em>Matched by hand.</em></h2><p>Long years under water and peat leave their mark on a trunk: its colour, its age, its character. We match the tone to your palette in consultation.</p></header>
  <div class="mhB">
    <div class="mhB__l{RV}">{pic('s20-floors', 'A bright room with a dark parquet floor in a wide pattern and a glass door', 1007, 1258)}</div>
    <div class="mhB__r">
      <div class="{RV}"><span class="idx">The colour of time</span>{tones()}</div>
      <div class="mhB__stat{RV}"><b data-oldest>3,334</b><span>years: the oldest sample of our latest radiocarbon protocol (<span data-oldest-line>oak</span>). Every tree is different, and every trunk is dated on its own.</span></div>
      <div class="{RV}"><span class="idx">Recent samples</span>{dates_block()}</div>
    </div>
  </div>
  <ul class="pdB{RV}">{"".join(f'<li>{pic(img, alt, w, hh)}<b>{n}</b></li>' for n, img, w, hh, alt in [("Stairs", "s21-stairs", 1007, 1258, "Oak stair treads and a white wall"), ("Walls", "s22-img", 1500, 1875, "A bedroom with wood-panelled walls"), ("Ceilings", "s23-img", 1500, 1875, "A living room with a wood ceiling"), ("Tables", "s24-img", 1007, 1259, "A dark wooden table with a live edge")])}</ul>
</div></section>
<section class="sec" id="process" aria-labelledby="h-process"><div class="w">
  <header class="shB{RV}"><span class="idx">06 / Working with your studio</span><h2 id="h-process">From first sketch <em>to final board.</em></h2></header>
  <ol class="prB">{"".join(f'<li class="{RV.strip()}"><span class="idx">{i:02d}</span><h3>{n}</h3><p>{p}</p></li>' for i, (n, p) in enumerate(PROCESS, 1))}</ol>
</div></section>
<section class="sec band" id="projects" aria-labelledby="h-proj"><div class="w">
  <header class="shB{RV}"><span class="idx">07 / Selected work</span><h2 id="h-proj">Residences, yachts and <em>commercial spaces.</em></h2><p>We respect our clients’ privacy, so we do not always share the name or photos of a project.</p></header>
  {projects_reel()}
  <div class="reel-nav"><button type="button" aria-label="Previous" data-dir="-1">←</button><button type="button" aria-label="Next" data-dir="1">→</button></div>
  <blockquote class="qB{RV}"><p>“The craft has passed through three generations of our family, and bog wood asks for all of it.”</p><footer>Big Foot Floors · Lithuania</footer></blockquote>
  <ul class="lkB{RV}"><li><b>The workshop</b><span>Lithuania, where every board is made</span></li><li><b>The craft</b><span>Third generation of woodworkers</span></li><li><b>The care</b><span>Aftercare, repair and refresh</span></li></ul>
</div></section>
<section class="sec" id="consultation" aria-labelledby="h-con"><div class="w cB">
  <div class="cB__side"><span class="idx">08 / Start a project</span><h2 id="h-con">Tell us about <em>your project.</em></h2><p>Describe your project and we will invite you to a consultation to talk it through.</p>{contact()}</div>
  <div class="cB__form">{form_html()}</div>
</div></section>
'''
    return h + footer('b')

# ---------------------------------------------------------------- C: Swiss
def page_c():
    h = head('c', 'Big Foot Floors — Bog Wood for architects and designers (C, Swiss)') + header('c', LOGO['c'])
    h += f'''<section class="hC" id="top" aria-labelledby="h-hero"><div class="w">
  <h1 id="h-hero">Millennia in the water. <span>Now ready for your drawings.</span></h1>
  <div class="hC__row"><div class="hC__side"><p>{HERO_P}</p><div class="hC__cta"><a class="btn btn--solid" href="#consultation">Book a consultation</a><a class="btn btn--line" href="#specify">View specification</a></div></div>
  {vid(*HERO_VID, cls="hC__media", eager=True)}</div>
  <ul class="pillC"><li>Private residences</li><li>Villas</li><li>Superyachts</li><li>Commercial spaces</li><li>Stairs, walls, ceilings</li></ul>
</div></section>
<section class="sec" id="make" aria-labelledby="h-make"><div class="w">
  <header class="shC{RV}"><h2 id="h-make">One rare material, <b>carried across every surface</b> of the interior.</h2></header>
  <div class="bentoC">
    <a class="bC bC--1{RV}" href="#consultation" data-prefill="spec">{pic('s20-floors', PRODUCTS[0][5], 1007, 1258)}<span><b>Bog wood floors</b>Multilayer boards in bog oak and bog ash, dated and finished by hand.</span></a>
    <a class="bC bC--2{RV}" href="#consultation" data-prefill="patterns">{pic('s14-img', PRODUCTS[1][5], 1006, 1341)}<span><b>Parquet patterns</b>Chevron, herringbone and custom geometries.</span></a>
    <a class="bC bC--3{RV}" href="#consultation" data-prefill="walls">{pic('s22-img', PRODUCTS[2][5], 1500, 1875)}<span><b>Walls &amp; ceilings</b>Cladding matched to the floor batch.</span></a>
    <a class="bC bC--4{RV}" href="#consultation" data-prefill="stairs">{pic('s21-stairs', PRODUCTS[3][5], 1007, 1258)}<span><b>Stairs</b>Treads and risers in the same batch.</span></a>
    <a class="bC bC--5{RV}" href="#consultation" data-prefill="tables">{pic('s25-img', 'A wine cellar with wooden racks and arched alcoves', 1024, 576)}<span><b>Tables &amp; wine cellars</b>Furniture and cellars from solid bog wood.</span></a>
  </div>
</div></section>
<section class="sec" id="colour" aria-labelledby="h-colour"><div class="w">
  <header class="shC{RV}"><h2 id="h-colour">Coloured by time, <b>not by stain.</b></h2><p>Oak that lay for millennia under water and peat, sealed from oxygen. Tannins reacted with minerals and darkened the wood all the way through.</p></header>
  <div class="colC">
    <div class="hot{RV}">{vid('s11-grain', 'Close-up of weathered, dark bog wood grain', 'hotC__m')}{"".join(f'<button class="hot__pt" type="button" style="--x:{x}%;--y:{y}%" aria-expanded="false" aria-controls="hp-{i}"><i>{i+1}</i><span class="sr-only">Annotation {i+1}</span></button>' for i, (x, y) in enumerate(HOTPOS))}</div>
    <ol class="hot__list{RV}">{"".join(f'<li id="hp-{i}"><b>{a}</b><span>{b}</span></li>' for i, (a, b) in enumerate(HOT))}</ol>
  </div>
  <div class="{RV} tonesC">{tones()}</div>
  <div class="{RV} datesC"><h3 class="lblC">Examples from the latest laboratory protocol</h3>{dates_block()}</div>
</div></section>
<section class="sec" id="environments" aria-labelledby="h-env"><div class="w">
  <header class="shC{RV}"><h2 id="h-env">Engineered for land, <b>sea and air.</b></h2></header>
  <div class="tabsC" role="tablist" aria-label="Environments" data-envtabs><button type="button" role="tab" data-env="res" aria-selected="true">Residences &amp; villas</button><button type="button" role="tab" data-env="yacht" aria-selected="false">Superyachts</button><button type="button" role="tab" data-env="com" aria-selected="false">Commercial spaces</button></div>
  <div class="envC">
    <div data-envpanel="res" class="envC__p">{pic('s28-img', ENVS[0][6], 1025, 1281)}<div><h3>Floors that hold their line at home</h3><p>{ENVS[0][1]}</p><dl><dt>Stable construction</dt><dd>Multilayer boards stay stable with changes in temperature and humidity.</dd><dt>Underfloor heating</dt><dd>Compatible with underfloor heating systems.</dd><dt>Installation</dt><dd>By our own craftsmen, wherever your project is.</dd></dl></div></div>
    <div data-envpanel="yacht" class="envC__p" hidden>{pic('s26-img', ENVS[1][6], 1280, 720)}<div><h3>Floors that hold their line at sea</h3><p>{ENVS[1][1]}</p><dl><dt>Stable construction</dt><dd>Multilayer boards stay stable with changes in temperature and humidity.</dd><dt>Made to measure</dt><dd>Floors and cabinetry matched to the vessel.</dd><dt>Installation</dt><dd>By our own craftsmen, wherever your project is.</dd></dl></div></div>
    <div data-envpanel="com" class="envC__p" hidden>{pic('s29-img', ENVS[2][6], 682, 853)}<div><h3>Floors for spaces that are used every day</h3><p>{ENVS[2][1]}</p><dl><dt>Wear</dt><dd>Bog oak resists discolouring from sunlight and wear from daily use.</dd><dt>Made to measure</dt><dd>Floors, walls and ceilings in one matched batch.</dd><dt>Installation</dt><dd>By our own craftsmen, wherever your project is.</dd></dl></div></div>
  </div>
</div></section>
<section class="sec band" id="specify" aria-labelledby="h-spec"><div class="w">
  <header class="shC{RV}"><h2 id="h-spec">Everything needed to <b>write it into the drawings.</b></h2><p>Ask for any of these documents during your consultation.</p></header>
  <div class="spC{RV}">
    <div class="spC__nav"><div class="spec__tabs" role="tablist" aria-label="Species" data-spec-tabs></div><ul class="docs" data-docs></ul></div>
    <div class="spC__card"><div class="spec__head"><span class="spec__kind" data-spec-kind></span><h3 data-spec-title></h3><p data-spec-note></p></div><dl class="spec__rows" data-spec-rows></dl><p class="spec__tbc" data-spec-tbc hidden>Values marked <b>TBC</b> come from the design mock-up and are awaiting confirmation by Big Foot Floors.</p><a class="btn btn--solid" href="#consultation" data-prefill="spec">Discuss this specification</a></div>
  </div>
</div></section>
<section class="sec" id="species" aria-labelledby="h-species"><div class="w">
  <header class="shC{RV}"><h2 id="h-species">Six species, from <b>forest oak to ancient bog wood.</b></h2></header>
  <ul class="swC{RV}">{"".join(f'<li><a href="#specify" data-species="{i}" class="swC__a">{pic(img, alt, w, hh)}<b>{n}</b><span>{tag}</span></a></li>' for i, n, img, tag, w, hh, alt in SPECIES)}</ul>
</div></section>
<section class="sec" id="process" aria-labelledby="h-process"><div class="w">
  <header class="shC{RV}"><h2 id="h-process">How we work <b>with your studio.</b></h2></header>
  <ol class="prC">{"".join(f'<li class="{RV.strip()}"><span class="prC__n">{i}</span><h3>{n}</h3><p>{p}</p></li>' for i, (n, p) in enumerate(PROCESS, 1))}</ol>
</div></section>
<section class="sec band" id="projects" aria-labelledby="h-proj"><div class="w">
  <header class="shC{RV}"><h2 id="h-proj">Selected work, <b>around the world.</b></h2><p>Residences in Norway, Switzerland, France, Germany, Cyprus and the USA, and yachts. We respect our clients’ privacy, so we do not always share the name or photos of a project.</p></header>
  {projects_reel()}
  <div class="reel-nav"><button type="button" aria-label="Previous" data-dir="-1">←</button><button type="button" aria-label="Next" data-dir="1">→</button></div>
  <div class="abC{RV}">{pic("s31-img", "A woodworker standing beside a finished dark oak cabinet in the workshop", 883, 1104)}<div><h3>Three generations of woodworkers. <b>Every board still passes through a craftsman’s hands.</b></h3><p>{ABOUT_P}</p><div class="facts">{"".join(f'<div class="fact"><b>{b}</b><span>{s}</span></div>' for b, s in FACTS)}</div></div></div>
</div></section>
<section class="sec" id="consultation" aria-labelledby="h-con"><div class="w cC">
  <div class="cC__side"><h2 id="h-con">Book a consultation <b>for your project.</b></h2><p>Describe your project and we will invite you to a consultation to talk it through.</p>{contact()}</div>
  <div class="cC__card">{form_html()}</div>
</div></section>
'''
    return h + footer('c', '<div class="giant" aria-hidden="true">Big Foot Floors</div>')

for name, fn in (('a', page_a), ('b', page_b), ('c', page_c)):
    open(f'{name}.html', 'w', encoding='utf8').write(fn())
    print(name, 'ok')
