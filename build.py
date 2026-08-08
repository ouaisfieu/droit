#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Générateur du site « Droit belge, expliqué ».
Produit un site 100 % statique (HTML/CSS/JS) dans ../docs (ou OUT).
"""
import json
import os
import re
import shutil
import sys
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("OUT", os.path.join(HERE, "out"))
CONTENT = os.path.join(HERE, "content")
DATA = os.path.join(HERE, "data")
ASSETS = os.path.join(HERE, "assets")

SITE_TITLE = "Droit belge, expliqué"
SITE_DESC = ("Une introduction claire et complète au droit belge : institutions, "
             "élaboration des lois, fédéralisme, Europe, droits humains, justice civile et pénale.")

# ---------------------------------------------------------------- structure

PARTS = [
    ("I", "Comprendre le droit", "Ce qu'est une règle de droit, d'où elle vient, comment elle s'impose."),
    ("II", "L'État belge", "La Constitution, le Parlement, le gouvernement, le fédéralisme, les communes."),
    ("III", "Au-delà des frontières", "L'Union européenne, la Cour de Strasbourg, l'ONU."),
    ("IV", "Les grands principes", "État de droit, démocratie, droits humains, égalité."),
    ("V", "La justice", "Qui juge, comment, avec quelles garanties — au civil comme au pénal."),
]

# (num, slug, title, part, lede)
CHAPTERS = [
    (1, "quest-ce-que-le-droit", "Qu'est-ce que le droit ?", "I",
     "Une règle de droit n'est pas une règle de politesse. Ce qui la distingue, c'est la contrainte organisée."),
    (2, "sources-du-droit", "Les sources du droit", "I",
     "Constitution, traités, lois, arrêtés, jurisprudence, coutume : d'où sortent les règles qui vous obligent."),
    (3, "hierarchie-des-normes", "La hiérarchie des normes", "I",
     "Toutes les règles ne se valent pas. Quand deux normes se contredisent, il faut savoir laquelle l'emporte."),
    (4, "etat-et-constitution", "L'État et la Constitution", "II",
     "Un territoire, une population, un pouvoir — et un texte qui limite ce pouvoir depuis 1831."),
    (5, "institutions-federales", "Les institutions fédérales", "II",
     "La Chambre, le Sénat, le Roi, le gouvernement : qui fait quoi au sommet de l'État."),
    (6, "fabrication-de-la-loi", "Comment se fabrique une loi", "II",
     "D'une idée de ministre au Moniteur belge : le parcours complet d'un texte, étape par étape."),
    (7, "belgique-federale", "La Belgique fédérale", "II",
     "Trois communautés, trois régions, aucune hiérarchie entre elles. Mode d'emploi d'un pays compliqué."),
    (8, "communes-et-provinces", "Communes et provinces", "II",
     "Le niveau de pouvoir que vous croisez le plus souvent, et pourtant le moins connu."),
    (9, "controler-les-pouvoirs-publics", "Contrôler les pouvoirs publics", "II",
     "Cour constitutionnelle, Conseil d'État, article 159 : ce qui arrive quand l'État viole le droit."),
    (10, "union-europeenne", "L'Union européenne", "III",
     "Un ordre juridique qui produit des règles directement applicables chez vous, sans passer par la Chambre."),
    (11, "conseil-de-l-europe", "Le Conseil de l'Europe et la CEDH", "III",
     "46 États, une Convention, une Cour à Strasbourg où un particulier peut attaquer son propre pays."),
    (12, "droit-international-onu", "Le droit international et l'ONU", "III",
     "Comment des États souverains se lient les uns aux autres — et ce qui se passe quand ils ne tiennent pas parole."),
    (13, "etat-de-droit", "L'État de droit", "IV",
     "L'idée que le pouvoir lui-même obéit à des règles, et que quelqu'un peut le lui rappeler."),
    (14, "democratie", "La démocratie", "IV",
     "Le vote obligatoire, la proportionnelle, le référendum qui n'existe pas : la démocratie belge en pratique."),
    (15, "droits-humains", "Les droits humains", "IV",
     "Ce que l'État ne peut pas vous faire, ce qu'il doit vous garantir, et jusqu'où il peut restreindre vos libertés."),
    (16, "egalite-non-discrimination", "Égalité et non-discrimination", "IV",
     "Traiter tout le monde pareil ne suffit pas toujours. Le droit belge en a tiré des conséquences précises."),
    (17, "organisation-judiciaire", "L'organisation judiciaire", "V",
     "Justice de paix, tribunal de police, cour d'assises : qui juge quoi, et comment s'y retrouver."),
    (18, "acteurs-de-la-justice", "Les acteurs de la justice", "V",
     "Juges, procureurs, avocats, greffiers, huissiers : le personnel du procès et ses règles du jeu."),
    (19, "proces-civil", "Le procès civil", "V",
     "Un litige entre deux personnes, du premier courrier d'avocat à l'huissier qui exécute le jugement."),
    (20, "regler-autrement", "Régler un conflit autrement", "V",
     "Médiation, conciliation, arbitrage : sortir d'un conflit sans passer par le tribunal."),
    (21, "proces-penal", "Le procès pénal", "V",
     "De la plainte au jugement : enquête, instruction, détention préventive, audience, recours, peine."),
    (22, "raisonnement-juridique", "Raisonner et argumenter en droit", "V",
     "Qualifier les faits, interpréter la règle, prouver : les trois gestes de base du juriste."),
]

PAGES = [
    ("glossaire", "Glossaire", "Plus de 200 termes juridiques belges définis en langage clair."),
    ("quiz", "Quiz", "Testez vos connaissances : plus de 90 questions à choix multiple, avec explications."),
    ("ressources", "Ressources", "Où trouver les textes officiels, la jurisprudence et une aide juridique gratuite."),
    ("a-propos", "À propos", "Comment ce site est fait, ce qu'il vaut, ce qu'il ne vaut pas."),
]

CH_BY_SLUG = {c[1]: c for c in CHAPTERS}
SLUGS = [c[1] for c in CHAPTERS]

# ---------------------------------------------------------------- utilities

def slugify(text):
    text = re.sub(r"<[^>]+>", "", text)
    text = text.lower()
    repl = {"à": "a", "â": "a", "ä": "a", "é": "e", "è": "e", "ê": "e", "ë": "e",
            "î": "i", "ï": "i", "ô": "o", "ö": "o", "û": "u", "ù": "u", "ü": "u",
            "ç": "c", "œ": "oe", "’": "", "'": "", "«": "", "»": "", "“": "", "”": ""}
    for k, v in repl.items():
        text = text.replace(k, v)
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text or "section"


def strip_tags(html):
    html = re.sub(r"<(script|style|svg)[^>]*>.*?</\1>", " ", html, flags=re.S | re.I)
    html = re.sub(r"<[^>]+>", " ", html)
    html = html.replace("&nbsp;", " ").replace("&amp;", "&").replace("&laquo;", "«").replace("&raquo;", "»")
    return re.sub(r"\s+", " ", html).strip()


def reading_minutes(html):
    words = len(strip_tags(html).split())
    return max(2, round(words / 190))


# ------------------------------------------------- headings & § numbering

def process_headings(body, chapter_num):
    """Ajoute id + numérotation marginale § n.m aux h2/h3, renvoie (html, toc)."""
    toc = []
    counters = {"h2": 0, "h3": 0}

    def repl(m):
        level, attrs, inner = m.group(1), m.group(2) or "", m.group(3)
        if level == "h2":
            counters["h2"] += 1
            counters["h3"] = 0
            ref = "%s.%d" % (chapter_num, counters["h2"])
        else:
            counters["h3"] += 1
            ref = "%s.%d.%d" % (chapter_num, counters["h2"], counters["h3"])
        hid = slugify(inner)
        base = hid
        n = 2
        while any(t["id"] == hid for t in toc):
            hid = "%s-%d" % (base, n)
            n += 1
        toc.append({"id": hid, "text": strip_tags(inner), "level": 2 if level == "h2" else 3, "ref": ref})
        marker = ('<a class="sec-ref" href="#%s" aria-label="Lien vers cette section">'
                  '<span aria-hidden="true">§</span>&nbsp;%s</a>') % (hid, ref)
        return ('<%s id="%s"%s class="h-anchor">%s<span class="h-text">%s</span></%s>'
                % (level, hid, attrs, marker, inner, level))

    body = re.sub(r"<(h2|h3)( [^>]*)?>(.*?)</\1>", repl, body, flags=re.S)
    return body, toc


# ---------------------------------------------------------------- layout

def head(title, desc, depth, extra_css="", canonical=""):
    up = "../" * depth
    return f"""<!DOCTYPE html>
<html lang="fr" data-theme="auto">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<meta name="description" content="{escape(desc)}">
<meta name="color-scheme" content="light dark">
<meta property="og:type" content="website">
<meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="{escape(desc)}">
<meta property="og:site_name" content="{SITE_TITLE}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{up}assets/img/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Newsreader:ital,opsz,wght@0,6..72,300..700;1,6..72,300..600&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{up}assets/css/style.css">{extra_css}
<script>(function(){{try{{var t=localStorage.getItem('db-theme');if(t)document.documentElement.setAttribute('data-theme',t);}}catch(e){{}}}})();</script>
</head>
<body>
<a class="skip" href="#main">Aller au contenu</a>
"""


def header_html(depth, active=""):
    up = "../" * depth
    def cls(name):
        return ' class="on"' if active == name else ""
    return f"""<header class="topbar">
  <div class="topbar-in">
    <a class="brand" href="{up}index.html">
      <span class="brand-bars" aria-hidden="true"><i></i><i></i><i></i></span>
      <span class="brand-txt">Droit belge<span class="brand-sub">expliqué</span></span>
    </a>
    <nav class="topnav" aria-label="Navigation principale">
      <a href="{up}index.html#sommaire"{cls('sommaire')}>Sommaire</a>
      <a href="{up}glossaire.html"{cls('glossaire')}>Glossaire</a>
      <a href="{up}quiz.html"{cls('quiz')}>Quiz</a>
      <a href="{up}ressources.html"{cls('ressources')}>Ressources</a>
    </nav>
    <div class="topbar-tools">
      <button class="ico" id="search-open" aria-label="Rechercher (touche /)" title="Rechercher — /"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="6.5"/><path d="M16 16l4.5 4.5"/></svg></button>
      <button class="ico" id="theme-toggle" aria-label="Changer de thème" title="Thème clair / sombre"><svg viewBox="0 0 24 24" aria-hidden="true" class="i-sun"><circle cx="12" cy="12" r="4.2"/><path d="M12 2.5v2.2M12 19.3v2.2M2.5 12h2.2M19.3 12h2.2M5.2 5.2l1.6 1.6M17.2 17.2l1.6 1.6M18.8 5.2l-1.6 1.6M6.8 17.2l-1.6 1.6"/></svg><svg viewBox="0 0 24 24" aria-hidden="true" class="i-moon"><path d="M20 14.5A8.2 8.2 0 0 1 9.5 4 8.3 8.3 0 1 0 20 14.5z"/></svg></button>
      <button class="ico only-mob" id="menu-open" aria-label="Ouvrir le sommaire" aria-expanded="false"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3.5 7h17M3.5 12h17M3.5 17h17"/></svg></button>
    </div>
  </div>
  <div class="readbar" id="readbar" aria-hidden="true"><span></span></div>
</header>
"""


def sidebar_html(depth, active_slug=""):
    up = "../" * depth
    out = ['<nav class="sidenav" id="sidenav" aria-label="Sommaire des chapitres">',
           '<div class="sidenav-in">',
           '<p class="rail-title">Sommaire</p>']
    for pnum, ptitle, _ in PARTS:
        out.append('<p class="rail-part"><span>%s</span>%s</p><ul class="rail-list">' % (pnum, escape(ptitle)))
        for num, slug, title, part, _l in CHAPTERS:
            if part != pnum:
                continue
            on = ' class="on" aria-current="page"' if slug == active_slug else ""
            out.append('<li><a href="%schapitres/%s.html"%s><b>%02d</b>%s</a></li>' % (up, slug, on, num, escape(title)))
        out.append("</ul>")
    out.append('<p class="rail-part"><span>+</span>Outils</p><ul class="rail-list">')
    for slug, title, _d in PAGES:
        out.append('<li><a href="%s%s.html"><b>·</b>%s</a></li>' % (up, slug, escape(title)))
    out.append("</ul></div></nav>")
    return "\n".join(out)


def footer_html(depth):
    up = "../" * depth
    return f"""<footer class="foot">
  <div class="foot-in">
    <div>
      <p class="foot-mark">Droit belge, expliqué</p>
      <p class="foot-note">Ressource pédagogique gratuite et libre. Le contenu décrit l'état du droit belge tel qu'il se présentait à la mi‑2026. Ce site n'est pas un conseil juridique : pour une situation personnelle, consultez un professionnel ou une permanence d'aide juridique.</p>
    </div>
    <nav aria-label="Pied de page">
      <a href="{up}index.html#sommaire">Sommaire</a>
      <a href="{up}glossaire.html">Glossaire</a>
      <a href="{up}quiz.html">Quiz</a>
      <a href="{up}ressources.html">Ressources</a>
      <a href="{up}a-propos.html">À propos</a>
    </nav>
  </div>
</footer>
<div class="searchbox" id="searchbox" hidden>
  <div class="searchbox-panel" role="dialog" aria-modal="true" aria-label="Recherche">
    <div class="searchbox-head">
      <svg viewBox="0 0 24 24" aria-hidden="true" class="sb-ico"><circle cx="11" cy="11" r="6.5"/><path d="M16 16l4.5 4.5"/></svg>
      <input type="search" id="search-input" placeholder="Rechercher : cassation, arrêté royal, prescription…" autocomplete="off" aria-label="Rechercher dans le site">
      <button class="sb-close" id="search-close" aria-label="Fermer">Échap</button>
    </div>
    <div class="searchbox-results" id="search-results"></div>
  </div>
</div>
<div class="dfn-pop" id="dfn-pop" hidden></div>
<script>window.DB_BASE="{up}";</script>
<script src="{up}assets/js/app.js" defer></script>
</body>
</html>
"""


# ---------------------------------------------------------------- pages

def build_chapter(ch, prev_ch, next_ch):
    num, slug, title, part, lede = ch
    raw = open(os.path.join(CONTENT, "%s.html" % slug), encoding="utf-8").read()
    body, toc = process_headings(raw, num)
    mins = reading_minutes(raw)
    part_title = next(p[1] for p in PARTS if p[0] == part)

    toc_html = ['<nav class="onthis" aria-label="Sur cette page"><p class="rail-title">Sur cette page</p><ol>']
    for t in toc:
        toc_html.append('<li class="lv%d"><a href="#%s"><span class="ot-ref">%s</span>%s</a></li>'
                        % (t["level"], t["id"], t["ref"], escape(t["text"])))
    toc_html.append("</ol></nav>")

    nav_prev = ('<a class="pn prev" href="%s.html"><span>Chapitre précédent</span><b>%s</b></a>'
                % (prev_ch[1], escape(prev_ch[2]))) if prev_ch else '<span class="pn empty"></span>'
    nav_next = ('<a class="pn next" href="%s.html"><span>Chapitre suivant</span><b>%s</b></a>'
                % (next_ch[1], escape(next_ch[2]))) if next_ch else '<span class="pn empty"></span>'

    html = head("%s — %s" % (title, SITE_TITLE), strip_tags(lede), 1)
    html += header_html(1)
    html += '<div class="shell">'
    html += sidebar_html(1, slug)
    html += '<main id="main" class="chapter">'
    html += f"""<article>
<header class="ch-head">
  <p class="eyebrow"><span class="eb-num">Chapitre {num:02d}</span><span class="eb-sep">/</span><span>Partie {part} · {escape(part_title)}</span></p>
  <h1>{escape(title)}</h1>
  <p class="lede">{lede}</p>
  <p class="meta"><span>{mins} min de lecture</span><span class="dot">·</span><span>{len(toc)} sections</span></p>
</header>
{body}
</article>
<nav class="pagenav" aria-label="Navigation entre chapitres">{nav_prev}{nav_next}</nav>
</main>
{"".join(toc_html)}
</div>
"""
    html += footer_html(1)
    write(os.path.join(OUT, "chapitres", "%s.html" % slug), html)
    return {"num": num, "slug": slug, "title": title, "toc": toc, "body": raw, "mins": mins}


def build_simple_page(slug, title, desc, body, active=""):
    html = head("%s — %s" % (title, SITE_TITLE), desc, 0)
    html += header_html(0, active)
    html += '<div class="shell">'
    html += sidebar_html(0)
    html += '<main id="main" class="chapter wide">' + body + "</main></div>"
    html += footer_html(0)
    write(os.path.join(OUT, "%s.html" % slug), html)


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


# ---------------------------------------------------------------- index

def build_home(chapters_data):
    hero = open(os.path.join(CONTENT, "_home.html"), encoding="utf-8").read()

    cards = []
    for pnum, ptitle, pdesc in PARTS:
        cards.append('<section class="part"><header class="part-head">'
                     '<p class="part-num">Partie %s</p><h3>%s</h3><p>%s</p></header><ol class="ch-grid">'
                     % (pnum, escape(ptitle), escape(pdesc)))
        for num, slug, title, part, lede in CHAPTERS:
            if part != pnum:
                continue
            m = next(c["mins"] for c in chapters_data if c["slug"] == slug)
            cards.append('<li><a href="chapitres/%s.html"><span class="cg-num">%02d</span>'
                         '<span class="cg-body"><b>%s</b><em>%s</em></span>'
                         '<span class="cg-min">%d min</span></a></li>' % (slug, num, escape(title), lede, m))
        cards.append("</ol></section>")

    total_min = sum(c["mins"] for c in chapters_data)
    html = head(SITE_TITLE + " — introduction complète au droit belge", SITE_DESC, 0)
    html += header_html(0)
    html += '<main id="main" class="home">'
    html += hero.replace("{{TOTAL_MIN}}", str(total_min)).replace("{{N_CH}}", str(len(CHAPTERS)))
    html += '<section class="sommaire" id="sommaire"><div class="wrap">'
    html += '<h2 class="sec-title">Le sommaire complet</h2>'
    html += '<p class="sec-sub">Vingt‑deux chapitres, du concept de règle de droit jusqu\'à l\'exécution d\'un jugement. Chacun se lit seul.</p>'
    html += "".join(cards)
    html += "</div></section>"
    html += "</main>"
    html += footer_html(0)
    write(os.path.join(OUT, "index.html"), html)


# ---------------------------------------------------------------- search

def build_search_index(chapters_data):
    docs = []
    for c in chapters_data:
        body = c["body"]
        # découpe par h2
        parts = re.split(r"(?=<h2[ >])", body)
        cur_title, cur_id = c["title"], ""
        toc_map = {t["text"]: t["id"] for t in c["toc"]}
        for p in parts:
            m = re.match(r"<h2[^>]*>(.*?)</h2>", p, flags=re.S)
            if m:
                cur_title = strip_tags(m.group(1))
                cur_id = toc_map.get(cur_title, "")
            text = strip_tags(p)
            if len(text) < 40:
                continue
            for i in range(0, len(text), 900):
                chunk = text[i:i + 900]
                if len(chunk) < 60:
                    continue
                docs.append({
                    "u": "chapitres/%s.html%s" % (c["slug"], "#" + cur_id if cur_id else ""),
                    "c": c["title"],
                    "n": c["num"],
                    "s": cur_title if cur_title != c["title"] else "",
                    "t": chunk,
                })
    # glossaire
    gl = json.load(open(os.path.join(DATA, "glossaire.json"), encoding="utf-8"))
    for g in gl:
        docs.append({"u": "glossaire.html#g-%s" % slugify(g["t"]), "c": "Glossaire", "n": 0,
                     "s": g["t"], "t": g["t"] + " — " + strip_tags(g["d"])})
    write(os.path.join(OUT, "assets", "js", "search-index.json"),
          json.dumps(docs, ensure_ascii=False, separators=(",", ":")))
    return len(docs)


# ---------------------------------------------------------------- glossaire / quiz

def build_glossaire():
    gl = json.load(open(os.path.join(DATA, "glossaire.json"), encoding="utf-8"))
    gl.sort(key=lambda g: slugify(g["t"]))
    letters = sorted({slugify(g["t"])[0].upper() for g in gl})
    body = ['<header class="ch-head"><p class="eyebrow"><span class="eb-num">Outil</span><span class="eb-sep">/</span><span>Vocabulaire</span></p>',
            "<h1>Glossaire</h1>",
            '<p class="lede">Le droit a son vocabulaire, et c\'est souvent le premier obstacle. Voici %d termes, définis en langage ordinaire.</p></header>' % len(gl)]
    body.append('<div class="gl-tools"><input type="search" id="gl-filter" placeholder="Filtrer : saisir un mot…" aria-label="Filtrer le glossaire"><p class="gl-count" id="gl-count" aria-live="polite"></p></div>')
    body.append('<nav class="gl-alpha" aria-label="Index alphabétique">')
    for L in letters:
        body.append('<a href="#lettre-%s">%s</a>' % (L, L))
    body.append("</nav>")
    cur = None
    body.append('<div id="gl-list">')
    for g in gl:
        L = slugify(g["t"])[0].upper()
        if L != cur:
            if cur is not None:
                body.append("</dl>")
            cur = L
            body.append('<h2 class="gl-letter" id="lettre-%s">%s</h2><dl class="gl">' % (L, L))
        rel = ""
        if g.get("v"):
            rel = '<span class="gl-see">Voir aussi : %s</span>' % ", ".join(
                '<a href="#g-%s">%s</a>' % (slugify(v), escape(v)) for v in g["v"])
        ch = ""
        if g.get("c"):
            c = CH_BY_SLUG.get(g["c"])
            if c:
                ch = '<a class="gl-ch" href="chapitres/%s.html">Chapitre %02d</a>' % (c[1], c[0])
        body.append('<div class="gl-item" id="g-%s"><dt>%s%s</dt><dd>%s%s</dd></div>'
                    % (slugify(g["t"]), escape(g["t"]), ch, g["d"], rel))
    body.append("</dl></div>")
    build_simple_page("glossaire", "Glossaire", "Plus de %d termes du droit belge définis simplement." % len(gl),
                      "".join(body), "glossaire")
    return len(gl)


def build_quiz():
    qz = json.load(open(os.path.join(DATA, "quiz.json"), encoding="utf-8"))
    opts = []
    themes = []
    for q in qz:
        if q["th"] not in themes:
            themes.append(q["th"])
    for t in themes:
        opts.append('<option value="%s">%s</option>' % (escape(t), escape(t)))
    body = f"""<header class="ch-head"><p class="eyebrow"><span class="eb-num">Outil</span><span class="eb-sep">/</span><span>Auto‑évaluation</span></p>
<h1>Quiz</h1>
<p class="lede">{len(qz)} questions à choix multiple pour vérifier ce qui est resté. Chaque réponse est expliquée et renvoie au chapitre concerné.</p></header>
<div class="quiz-setup" id="quiz-setup">
  <div class="qs-row">
    <label for="q-theme">Thème</label>
    <select id="q-theme"><option value="">Tous les chapitres</option>{''.join(opts)}</select>
  </div>
  <div class="qs-row">
    <label for="q-count">Nombre de questions</label>
    <select id="q-count"><option value="10">10</option><option value="20">20</option><option value="0">Toutes</option></select>
  </div>
  <button class="btn" id="q-start">Commencer</button>
</div>
<div class="quiz" id="quiz" hidden></div>
<div class="quiz-result" id="quiz-result" hidden></div>
"""
    build_simple_page("quiz", "Quiz", "Testez vos connaissances en droit belge : %d questions expliquées." % len(qz),
                      body, "quiz")
    shutil.copy(os.path.join(DATA, "quiz.json"), os.path.join(OUT, "assets", "js", "quiz.json"))
    shutil.copy(os.path.join(DATA, "glossaire.json"), os.path.join(OUT, "assets", "js", "glossaire.json"))
    return len(qz)


# ---------------------------------------------------------------- main

def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT, exist_ok=True)
    shutil.copytree(ASSETS, os.path.join(OUT, "assets"))

    chapters_data = []
    for i, ch in enumerate(CHAPTERS):
        prev_ch = CHAPTERS[i - 1] if i > 0 else None
        next_ch = CHAPTERS[i + 1] if i < len(CHAPTERS) - 1 else None
        chapters_data.append(build_chapter(ch, prev_ch, next_ch))

    build_home(chapters_data)
    ng = build_glossaire()
    nq = build_quiz()

    for slug, title, desc in PAGES:
        if slug in ("glossaire", "quiz"):
            continue
        raw = open(os.path.join(CONTENT, "_%s.html" % slug), encoding="utf-8").read()
        build_simple_page(slug, title, desc, raw, slug)

    nd = build_search_index(chapters_data)

    # 404 + fichiers techniques
    write(os.path.join(OUT, "404.html"),
          head("Page introuvable — " + SITE_TITLE, "Page introuvable", 0) + header_html(0) +
          '<main id="main" class="home"><section class="wrap notfound"><p class="eyebrow"><span class="eb-num">Erreur 404</span></p>'
          '<h1>Cette page n\'existe pas</h1><p class="lede">Le lien est peut‑être ancien, ou mal recopié. '
          'Le sommaire complet reste le meilleur point de départ.</p>'
          '<p><a class="btn" href="index.html#sommaire">Voir le sommaire</a></p></section></main>' + footer_html(0))
    write(os.path.join(OUT, ".nojekyll"), "")
    write(os.path.join(OUT, "robots.txt"), "User-agent: *\nAllow: /\n")

    urls = ["index.html", "glossaire.html", "quiz.html", "ressources.html", "a-propos.html"]
    urls += ["chapitres/%s.html" % s for s in SLUGS]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        sm.append("<url><loc>https://ouaisfieu.github.io/droit/%s</loc></url>" % u)
    sm.append("</urlset>")
    write(os.path.join(OUT, "sitemap.xml"), "\n".join(sm))

    print("OK — %d chapitres, %d termes, %d questions, %d fragments indexés"
          % (len(CHAPTERS), ng, nq, nd))
    print("Sortie :", OUT)


if __name__ == "__main__":
    main()
