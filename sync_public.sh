#!/bin/sh
# Собирает сайт и копирует результат в public/ (каталог деплоя Cloudflare)
set -e
python3 build.py
for f in index.html contacts.html policy.html 404.html robots.txt sitemap.xml data.js app.js style.css favicon.svg; do
  [ -f "$f" ] && cp "$f" "public/$f"
done
echo "public/ обновлён"
