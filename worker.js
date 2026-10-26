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
  "X-Spru-Version": "nav-fix-5",
};

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
    return out;
  },
};
