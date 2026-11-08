#!/usr/bin/env python3
"""Отправляет IndexNow (Яндекс, Bing) список URL сайта после деплоя."""
import json, os, sys, urllib.request

SITE = os.environ.get("SITE", "https://xn--80aesajwhicohj4j.xn--p1ai")
KEY = os.environ.get("INDEXNOW_KEY", "a348b8e06666758c659d040fa5a440c6")
UA = "Mozilla/5.0 (compatible; IndexNowBot/1.0)"

req = urllib.request.Request(SITE + "/sitemap.xml", headers={"User-Agent": UA})
sm = urllib.request.urlopen(req, timeout=30).read().decode("utf-8")
urls = []
for chunk in sm.split("<loc>")[1:]:
    urls.append(chunk.split("</loc>")[0].strip())
if not urls:
    print("IndexNow: нет URL в sitemap")
    sys.exit(0)

body = json.dumps({
    "host": SITE.replace("https://", "").replace("http://", "").strip("/"),
    "key": KEY,
    "keyLocation": SITE + "/" + KEY + ".txt",
    "urlList": urls,
}).encode("utf-8")

for endpoint in ("https://yandex.com/indexnow", "https://api.indexnow.org/indexnow"):
    try:
        r = urllib.request.Request(endpoint, data=body,
                                  headers={"Content-Type": "application/json", "User-Agent": UA})
        with urllib.request.urlopen(r, timeout=30) as resp:
            print(endpoint, resp.status, resp.read().decode("utf-8")[:120])
    except Exception as e:
        print(endpoint, "error:", e)
