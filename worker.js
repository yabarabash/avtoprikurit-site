// Воркер для автоприкурить.рф: отдаёт статические ассеты и добавляет
// заголовки безопасности + редиректы (вместо _headers/_redirects, которые
// ломали деплой с ошибкой 100324).
const SECURITY_HEADERS = {
  "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline' https://mc.yandex.ru https://yastatic.net; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com data:; img-src 'self' data: https://mc.yandex.ru https://yastatic.net; connect-src 'self' https://mc.yandex.ru https://yastatic.net https://profi-reviews.spru.run https://lead-relay-pomoshch.spru.run; frame-src https://mc.yandex.ru; object-src 'none'; base-uri 'self'; form-action 'self' https://lead-relay-pomoshch.spru.run; upgrade-insecure-requests",
  "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
  "X-Content-Type-Options": "nosniff",
  "X-Frame-Options": "SAMEORIGIN",
  "Referrer-Policy": "strict-origin-when-cross-origin",
  "Permissions-Policy": "geolocation=(), microphone=(), camera=(), payment=(), interest-cohort=()",
  "Cross-Origin-Opener-Policy": "same-origin",
};

const SERVICE_PAGES = [
  "prikurit-avto", "shinomontazh", "zamen-akb",
  "vskrytie-avtomobilya", "zapusk-dvigatelya", "diagnostika",
];

const SHORT_PATHS = {
  "/contacts": "/contacts.html",
  "/policy": "/policy.html",
  "/privacy": "/policy.html",
  "/privacy.html": "/policy.html",
};

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // www -> без www, http -> https
    if (url.hostname.startsWith("www.") || url.protocol === "http:") {
      const host = url.hostname.replace(/^www\./, "");
      return Response.redirect(`https://${host}${url.pathname}${url.search}`, 301);
    }

    // /prikurit-avto -> /prikurit-avto/ (каталоги посадочных страниц)
    if (!url.pathname.endsWith("/") && !/\.[a-zA-Z0-9]{2,5}$/.test(url.pathname)
        && SERVICE_PAGES.includes(url.pathname.slice(1))) {
      return Response.redirect(`https://${url.hostname}${url.pathname}/${url.search}`, 301);
    }

    // короткие адреса страниц
    if (SHORT_PATHS[url.pathname]) {
      return Response.redirect(`https://${url.hostname}${SHORT_PATHS[url.pathname]}`, 301);
    }

    // html_handling = "none": корень и каталоги отдаём как index.html.
    // Заголовки Sec-Fetch-* убираем: с ними слой ассетов отвечает 404 на "/".
    const target = new URL(request.url);
    if (target.pathname.endsWith("/")) target.pathname += "index.html";

    const headers = new Headers(request.headers);
    headers.delete("Sec-Fetch-Mode");
    headers.delete("Sec-Fetch-Dest");
    headers.delete("Sec-Fetch-Site");
    headers.delete("Sec-Fetch-User");

    const assetRequest = new Request(target.toString(), {
      method: "GET",
      headers,
    });

    const response = await env.ASSETS.fetch(assetRequest);
    const out = new Response(response.body, response);
    for (const [k, v] of Object.entries(SECURITY_HEADERS)) out.headers.set(k, v);
    // Кэшируем картинки и стили надолго: имена файлов меняются при правках.
    if (/\.(webp|jpg|jpeg|png|svg|ico)$/i.test(url.pathname)) {
      // картинки кэшируем надолго: имя меняется при правке
      out.headers.set("Cache-Control", "public, max-age=2592000, immutable");
    } else if (/\.(css|js)$/i.test(url.pathname)) {
      // стили и скрипты — коротко, иначе правки не долетают до вернувшихся посетителей
      out.headers.set("Cache-Control", "public, max-age=600, must-revalidate");
    }
    return out;
  },
};
