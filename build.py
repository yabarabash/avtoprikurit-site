# -*- coding: utf-8 -*-
"""
Сборка статической версии сайта из data.js.
Запуск:  python3 build.py
Результат: index.html с текстом прямо в разметке (поисковики видят текст),
плюс app.js перерисовывает блоки из data.js, если данные изменились.
"""
import io, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.abspath(__file__))

def site():
    out = subprocess.check_output(
        ["node", "-e", "global.window={};require('%s/data.js');console.log(JSON.stringify(window.SITE))" % ROOT],
        cwd=ROOT).decode("utf-8")
    return json.loads(out)

def esc(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))

S = site()

BADGES = "".join("<li>%s</li>" % esc(b) for b in S["badges"])

TRUST = "".join('<li><b>%s</b><span>%s</span></li>' % (esc(t["label"]), esc(t["note"])) for t in S["trust"])

TOP = "".join(
    '<article class="top-card">'
    '<figure><img src="%s" alt="%s" width="1000" height="688" loading="lazy" decoding="async"></figure>'
    '<div class="top-num">%s</div><h3>%s</h3><p>%s</p>'
    '<div class="top-price"><a href="#form">%s</a></div></article>'
    % (esc(t["photo"]), esc(t["title"]), esc(t["num"]), esc(t["title"]), esc(t["text"]), esc(t["price"]))
    for t in S["topServices"])

SVC = "".join('<li><span class="idx">%02d</span><b>%s</b><span>%s</span></li>'
              % (i + 1, esc(s["title"]), esc(s["note"])) for i, s in enumerate(S["services"]))

PRICE = "".join('<tr><td>%s</td><td><a href="#form">%s</a></td></tr>'
                % (esc(r["name"]), esc(r["price"])) for r in S["priceRows"])

FACTS = "".join('<li><span>%s</span><em>%s</em></li>' % (esc(f["k"]), esc(f["v"])) for f in S["aboutFacts"])

AREAS = "".join('<li class="area-card">%s</li>' % esc(a) for a in S["areas"])

FAQ = "".join('<div class="faq-item"><h3>%s</h3><p>%s</p></div>' % (esc(f["q"]), esc(f["a"])) for f in S["faq"])

STEPS = "".join('<li><span class="num">%s</span><h3>%s</h3><p>%s</p></li>'
                % (esc(s["num"]), esc(s["title"]), esc(s["text"])) for s in S["steps"])

GALLERY = "".join(
    '<figure><img src="%s" alt="%s" width="1000" height="750" loading="lazy" decoding="async">'
    '<figcaption>%s</figcaption></figure>' % (esc(g["src"]), esc(g["caption"]), esc(g["caption"]))
    for g in S["gallery"])

SEO = "".join(
    '<article class="seo-block"><h3>%s</h3><p>%s</p></article>' % (esc(b["h"]), esc(b["p"]))
    for b in S["seoText"])

# --- реквизиты ---
inn = (S.get("inn") or "").strip()
ogrn = (S.get("ogrn") or "").strip()
req = []
if inn:
    req.append("ИНН %s" % inn)
if ogrn:
    req.append("ОГРНИП %s" % ogrn)
REQLINE = " · ".join(req) if req else "ИНН и ОГРНИП указываются по запросу"
LEGALFORM = S.get("legalForm", "")
SCHEDULE = S.get("schedule", "")

MAP = {
    "__BADGES__": BADGES,
    "__TRUST__": TRUST,
    "__TOP__": TOP,
    "__SVC__": SVC,
    "__PRICE__": PRICE,
    "__FACTS__": FACTS,
    "__AREAS__": AREAS,
    "__FAQ__": FAQ,
    "__STEPS__": STEPS,
    "__GALLERY__": GALLERY,
    "__SEO__": SEO,
    "__HERO_TITLE__": esc(S["heroTitle"]),
    "__HERO_LEAD__": esc(S["heroLead"]),
    "__ABOUT_TITLE__": esc(S["aboutTitle"]),
    "__ABOUT_TEXT__": esc((S.get("aboutText") or "").replace("{REVIEWS}", "140")),
    "__PRICE_NOTE__": esc(S.get("priceNote", "")),
    "__PRICE_DISCOUNT__": esc(S.get("priceDiscount", "")),
    "__PRICE_DISCOUNT_NOTE__": esc(S.get("priceDiscountNote", "")),
    "__FORM_TITLE__": esc(S.get("formTitle", "")),
    "__FORM_NOTE__": esc(S.get("formNote", "")),
    "__AREAS_TITLE__": esc(S.get("areasTitle", "")),
    "__AREAS_LEAD__": esc(S.get("areasLead", "")),
    "__FAQ_TITLE__": esc(S.get("faqTitle", "")),
    "__REVIEWS_TITLE__": esc(S.get("reviewsTitle", "")),
    "__REVIEWS_SUB__": esc(S.get("reviewsSub", "")),
    "__FOOT_NAME__": esc(S.get("role", "")),
    "__FOOT_NOTE__": esc(S.get("footerNote", "")),
    "__BRAND_NAME__": esc(S.get("brandName", "")),
    "__BRAND_ROLE__": esc(S.get("brandRole", "")),
    "__REQLINE__": esc(REQLINE),
    "__PUBDATE__": "26 октября 2026 г.",
    "__SITEURL__": "https://xn--80aesajwhicohj4j.xn--p1ai",
    "__OPNAME__": esc(S.get("legalName", "")),
    "__OPCONTACTS__": "Заявки принимаются через форму на Сайте, профиль на Профи.ру и мессенджер мастера, указанный на Сайте.",
    "__LEGALFORM__": esc(LEGALFORM),
    "__SCHEDULE__": esc(SCHEDULE),
    "__LEGAL_NAME__": esc(S.get("legalName", "")),
    "__LEGAL_ADDRESS__": esc(S.get("legalAddress", "")),
    "__OGRN_NOTE__": esc(S.get("ogrnNote", "")),
}

def fill(text):
    for k, v in MAP.items():
        text = text.replace(k, v)
    return text

tpl = fill(io.open(os.path.join(ROOT, "index.template.html"), encoding="utf-8").read())

# отдельные страницы: контакты и политика
for name in ("contacts.html", "policy.html", "privacy.html"):
    src = os.path.join(ROOT, name.replace(".html", ".template.html"))
    if os.path.exists(src):
        io.open(os.path.join(ROOT, name), "w", encoding="utf-8").write(
            fill(io.open(src, encoding="utf-8").read()))

left = re.findall(r"__[A-Z_]+__", tpl)
if left:
    sys.exit("Не подставлены маркеры: %s" % sorted(set(left)))

io.open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(tpl)

# проверки длины мета-тегов
def taglen(name, s):
    print("%-12s %3d симв." % (name, len(s)))

title = re.search(r"<title>(.*?)</title>", tpl, re.S).group(1)
desc = re.search(r'<meta name="description" content="(.*?)">', tpl, re.S).group(1)
taglen("title", title)
taglen("description", desc)
words = len(re.sub(r"<[^>]+>", " ", tpl).split())
print("слов на странице: ~%d" % words)
print("OK")
