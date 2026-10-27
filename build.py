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
REQLINE = " · ".join(req) if req else "указывается по запросу"
INNLINE = ("ИНН " + inn) if inn else "указывается по запросу"
LEGALFORM = S.get("legalForm", "")
SCHEDULE = S.get("schedule", "")


# --- Статические отзывы (для поисковиков) ---
REVIEWS = "".join(
    '<article class="review-card"><div class="review-top"><div><div class="review-author">%s</div>'
    '<div class="review-date">%s</div></div><div class="review-mark">★★★★★</div></div>'
    '<p class="review-text">%s</p><div class="review-service">%s</div></article>'
    % (esc(r.get("author", "")), esc(r.get("date", "")), esc(r.get("text", "")), esc(r.get("service", "")))
    for r in S.get("reviewsFallback", []))

REVIEW_COUNT = S.get("reviewsCount", 143)

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
    "__ABOUT_TEXT__": esc((S.get("aboutText") or "").replace("{REVIEWS}", str(REVIEW_COUNT))),
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
    "__REVIEWS_STATIC__": REVIEWS,
    "__FOOT_NAME__": esc(S.get("role", "")),
    "__FOOT_NOTE__": esc(S.get("footerNote", "")),
    "__BRAND_NAME__": esc(S.get("brandName", "")),
    "__BRAND_ROLE__": esc(S.get("brandRole", "")),
    "__REQLINE__": esc(REQLINE),
    "__INNLINE__": esc(INNLINE),
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

# ======================================================================
# Посадочные страницы под коммерческие запросы (servicePages в data.js)
# ======================================================================
SITEURL = "https://xn--80aesajwhicohj4j.xn--p1ai"
pages = S.get("servicePages") or []

def svc_body(pg):
    return "".join('<article class="seo-block"><h2>%s</h2><p>%s</p></article>'
                   % (esc(b["h"]), esc(b["p"])) for b in pg["body"])

def svc_faq(pg):
    return "".join('<div class="faq-item"><h3>%s</h3><p>%s</p></div>'
                   % (esc(f["q"]), esc(f["a"])) for f in pg["faq"])

def svc_reviews():
    items = (S.get("reviewsFallback") or [])[:4]
    return "".join(
        '<article class="review-card"><div class="review-top"><div><div class="review-author">%s</div>'
        '<div class="review-date">%s</div></div><div class="review-mark">★★★★★</div></div>'
        '<p class="review-text">%s</p><div class="review-service">%s</div></article>'
        % (esc(r.get("author", "")), esc(r.get("date", "")), esc(r.get("text", "")), esc(r.get("service", "")))
        for r in items)

def svc_links(pg):
    out = []
    for other in pages:
        if other["slug"] == pg["slug"]:
            continue
        out.append('<li><a href="/%s/">%s</a></li>' % (other["slug"], esc(other["h1"])))
    out.append('<li><a href="/">Помощь на дороге в Москве и области</a></li>')
    return "".join(out)

def svc_ld(pg):
    url = "%s/%s/" % (SITEURL, pg["slug"])
    graph = [
        {
            "@type": "Service",
            "@id": url + "#service",
            "name": pg["h1"],
            "serviceType": pg["h1"],
            "description": pg["desc"],
            "url": url,
            "provider": {"@id": SITEURL + "/#business"},
            "areaServed": [
                {"@type": "City", "name": "Москва"},
                {"@type": "AdministrativeArea", "name": "Московская область"},
            ],
            "availableChannel": {
                "@type": "ServiceChannel",
                "serviceUrl": SITEURL + "/#form",
                "availableLanguage": {"@type": "Language", "name": "Русский"},
            },
            "aggregateRating": {
                "@type": "AggregateRating",
                "ratingValue": "5",
                "bestRating": "5",
                "worstRating": "1",
                "reviewCount": str(REVIEW_COUNT),
            },
        },
        {
            "@type": "FAQPage",
            "@id": url + "#faq",
            "mainEntity": [
                {"@type": "Question", "name": f["q"],
                 "acceptedAnswer": {"@type": "Answer", "text": f["a"]}}
                for f in pg["faq"]
            ],
        },
        {
            "@type": "ItemList",
            "name": "Отзывы клиентов",
            "itemListElement": [
                {"@type": "Review",
                 "itemReviewed": {"@id": SITEURL + "/#business"},
                 "author": {"@type": "Person", "name": r.get("author", "Клиент")},
                 "reviewRating": {"@type": "Rating", "ratingValue": "5", "bestRating": "5"},
                 "reviewBody": r.get("text", "")}
                for r in (S.get("reviewsFallback") or [])[:4]
            ],
        },
        {
            "@type": "BreadcrumbList",
            "@id": url + "#crumbs",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Главная", "item": SITEURL + "/"},
                {"@type": "ListItem", "position": 2, "name": pg["h1"], "item": url},
            ],
        },
    ]
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=2)

SVC_TPL = io.open(os.path.join(ROOT, "service.template.html"), encoding="utf-8").read()
SVC_LINKS_INDEX = []
for pg in pages:
    url = "%s/%s/" % (SITEURL, pg["slug"])
    photo = pg["photo"]
    if not photo.startswith("/") and not photo.startswith("http"):
        photo = "/" + photo
    og = photo if photo.startswith("http") else SITEURL + photo
    html = (SVC_TPL
            .replace("__PAGE_TITLE__", esc(pg["title"]))
            .replace("__PAGE_DESC__", esc(pg["desc"]))
            .replace("__PAGE_KEYWORDS__", esc(pg.get("keywords", "")))
            .replace("__PAGE_URL__", url)
            .replace("__PAGE_OG_IMAGE__", og)
            .replace("__PAGE_H1__", esc(pg["h1"]))
            .replace("__PAGE_SHORT__", esc(pg["h1"]))
            .replace("__PAGE_LEAD__", esc(pg["lead"]))
            .replace("__PAGE_PHOTO__", photo)
            .replace("__PAGE_BODY__", svc_body(pg))
            .replace("__PAGE_FAQ__", svc_faq(pg))
            .replace("__PAGE_REVIEWS__", svc_reviews())
            .replace("__PAGE_LINKS__", svc_links(pg))
            .replace("__PAGE_LD__", svc_ld(pg)))
    d = os.path.join(ROOT, pg["slug"])
    os.makedirs(d, exist_ok=True)
    io.open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(html)
    leftover = re.findall(r"__[A-Z_]+__", html)
    if leftover:
        sys.exit("Страница %s: не подставлены маркеры %s" % (pg["slug"], sorted(set(leftover))))
    words = len(re.sub(r"<[^>]+>", " ", html).split())
    print("/%s/  title %d, desc %d, слов %d" % (pg["slug"], len(pg["title"]), len(pg["desc"]), words))
    SVC_LINKS_INDEX.append('<li><a href="/%s/">%s</a></li>' % (pg["slug"], esc(pg["h1"])))

MAP["__SVC_LINKS__"] = "".join(SVC_LINKS_INDEX)

# sitemap с посадочными страницами
sm = ['<?xml version="1.0" encoding="UTF-8"?>',
      '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
def u(loc, prio, changefreq="weekly", lastmod="2026-10-27"):
    sm.extend(["  <url>", "    <loc>%s</loc>" % loc, "    <lastmod>%s</lastmod>" % lastmod,
               "    <changefreq>%s</changefreq>" % changefreq, "    <priority>%s</priority>" % prio, "  </url>"])
u(SITEURL + "/", "1.0")
for pg in pages:
    u("%s/%s/" % (SITEURL, pg["slug"]), "0.9")
u(SITEURL + "/contacts.html", "0.6", "monthly")
u(SITEURL + "/policy.html", "0.4", "yearly")
sm.append("</urlset>")
io.open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write("\n".join(sm) + "\n")
print("sitemap.xml: %d URL" % (2 + len(pages)))

tpl = fill(io.open(os.path.join(ROOT, "index.template.html"), encoding="utf-8").read())

# отдельные страницы: контакты и политика
for name in ("contacts.html", "policy.html"):
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
