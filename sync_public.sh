#!/bin/sh
# Собирает сайт и копирует результат в public/ (каталог деплоя Cloudflare)
set -e
python3 build.py
for f in index.html contacts.html policy.html 404.html robots.txt sitemap.xml data.js app.js style.css favicon.svg; do
  [ -f "$f" ] && cp "$f" "public/$f"
done
# посадочные страницы услуг: <slug>/index.html
for d in prikurit-avto shinomontazh zamen-akb vskrytie-avtomobilya zapusk-dvigatelya diagnostika; do
  if [ -d "$d" ]; then
    mkdir -p "public/$d"
    cp "$d/index.html" "public/$d/index.html"
  fi
done
rm -f public/_headers public/_redirects
echo "public/ обновлён"
