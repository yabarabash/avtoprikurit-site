(function () {
  var S = window.SITE || {};
  var $ = function (s) { return document.querySelector(s); };

  function el(tag, cls, html) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (html != null) n.innerHTML = html;
    return n;
  }
  function esc(t) {
    return String(t == null ? '' : t).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }
  function set(sel, text) { var n = $(sel); if (n) n.textContent = text || ''; }

  /* --- Шапка, имя, подвал --- */
  set('#heroTitle', S.heroTitle);
  set('#heroLead', S.heroLead);
  set('#aboutTitle', S.aboutTitle);
  set('#aboutText', (S.aboutText || '').replace(/\{REVIEWS\}/g, '140'));
  set('#formTitle', S.formTitle);
  set('#formNote', S.formNote);
  set('#priceNote', S.priceNote);
  set('#consentText', S.consentText);
  set('#footName', S.role || '');
  set('#footNote', S.footerNote);

  set('#brandName', S.brandName || S.name);
  set('#brandRole', S.brandRole || (S.role + ' · ' + (S.region || '')));
  set('#areasTitle', S.areasTitle);
  set('#areasLead', S.areasLead);
  set('#faqTitle', S.faqTitle);
  set('#priceDiscount', S.priceDiscount);
  set('#priceDiscountNote', S.priceDiscountNote);

  /* --- Бейджи --- */
  var kb = $('#heroBadges');
  (S.badges || []).forEach(function (b) { kb.appendChild(el('li', null, esc(b))); });

  /* --- Телефон --- */
  var PHONE_ICON = '<svg class="call-ico-svg" viewBox="0 0 24 24" width="16" height="16" aria-hidden="true" focusable="false"><path fill="currentColor" d="M6.6 10.8c1.4 2.8 3.8 5.2 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 1.1.4 2.3.6 3.6.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1C10.6 21 3 13.4 3 4c0-.6.4-1 1-1h3.5c.6 0 1 .4 1 1 0 1.2.2 2.4.6 3.6.1.4 0 .8-.2 1l-2.3 2.2z"/></svg>';

  var phoneMode = S.phoneMode || 'hidden';
  var callEls = [$('#headPhone'), $('#heroPhone'), $('#callFab'), $('#footPhone')].filter(Boolean);

  function fetchPhone() {
    if (!S.callNumberUrl) return Promise.resolve('');
    return fetch(S.callNumberUrl, { cache: 'no-store' })
      .then(function (r) { return r.ok ? r.json() : {}; })
      .then(function (j) { return j.phone || ''; })
      .catch(function () { return ''; });
  }

  function dial(phone) {
    if (phone) window.location.href = 'tel:' + phone.replace(/[^\d+]/g, '');
  }

  if (phoneMode === 'full') {
    fetchPhone().then(function (phone) {
      if (!phone) return;
      var tel = 'tel:' + phone.replace(/[^\d+]/g, '');
      callEls.forEach(function (n) { n.hidden = false; });
      var hp = $('#headPhone');
      hp.innerHTML = PHONE_ICON + '<span>Позвонить</span>';
      var hn = $('#heroPhoneNum');
      if (hn) hn.textContent = 'Позвонить';
      var fp = $('#footPhone');
      if (fp) fp.textContent = phone;
      var fc = $('#formCall');
      if (fc) fc.innerHTML = 'Срочно? Позвоните: <a href="' + tel + '">' + esc(phone) + '</a>';
      document.addEventListener('click', function (e) {
        var a = e.target.closest && e.target.closest('[data-call]');
        if (a) { e.preventDefault(); dial(phone); }
      });
    });
  } else if (phoneMode === 'click') {
    callEls.forEach(function (n) { n.hidden = false; });
    var hp2 = $('#headPhone');
    hp2.innerHTML = PHONE_ICON + '<span>Позвонить</span>';
    var hn2 = $('#heroPhoneNum');
    if (hn2) hn2.textContent = 'Позвонить';
    var fc2 = $('#formCall');
    if (fc2) fc2.textContent = S.formCallHidden || '';
    // Номер подгружаем заранее и держим в памяти: в коде страницы его нет,
    // а звонок при клике уходит мгновенно (без ожидания сети).
    var cachedPhone = '';
    fetchPhone().then(function (p) { cachedPhone = p || ''; });
    document.addEventListener('click', function (e) {
      var a = e.target.closest && e.target.closest('[data-call]');
      if (!a) return;
      e.preventDefault();
      if (cachedPhone) { dial(cachedPhone); return; }
      fetchPhone().then(function (p) { cachedPhone = p || ''; dial(cachedPhone); });
    });
  } else {
    callEls.forEach(function (n) { n.hidden = true; });
    var fc3 = $('#formCall');
    if (fc3) fc3.textContent = S.formCallHidden || '';
  }

  /* --- Мессенджеры --- */
  function setLinks(sel, href, visible) {
    var n = $(sel);
    if (!n) return;
    if (href) { n.href = href; n.hidden = false; } else { n.hidden = true; }
  }
  var hasMsg = false;
  if (S.telegram) { hasMsg = true; }
  if (S.whatsapp) { hasMsg = true; }
  if (!hasMsg) { var ml = $('#msgLinks'); if (ml) ml.innerHTML = 'в <a id="profiLink2b" target="_blank" rel="noopener">Профи.ру</a>'; }
  setLinks('#tgLink', S.telegram || '');
  setLinks('#waLink', S.whatsapp || '');
  setLinks('#shareTg', 'https://t.me/share/url?url=' + encodeURIComponent(location.href) + '&text=' + encodeURIComponent(S.heroTitle));
  setLinks('#shareWa', 'https://api.whatsapp.com/send?text=' + encodeURIComponent(S.heroTitle + ' ' + location.href));
  setLinks('#shareVk', 'https://vk.com/share.php?url=' + encodeURIComponent(location.href) + '&title=' + encodeURIComponent(S.heroTitle));

  /* --- Профи.ру --- */
  ['#profiBtnTop', '#profiLink2', '#profiLink2b', '#profiLink3'].forEach(function (s) {
    var n = $(s); if (n && S.profi) n.href = S.profi;
  });
  var ob = $('#orderBtn');
  if (ob) ob.href = 'https://profi.ru/remont/?seamless=1&tabName=ORDER&chosenProfileId=AfoninMV14';

  /* --- Доверие --- */
  var tr = $('#trustRow');
  (S.trust || []).forEach(function (t) {
    var li = el('li');
    li.appendChild(el('b', null, esc(t.label)));
    li.appendChild(el('span', null, esc(t.note)));
    tr.appendChild(li);
  });

  /* --- Топ-услуги --- */
  var tg = $('#topGrid');
  (S.topServices || []).forEach(function (t) {
    var card = el('article', 'top-card');
    var fig = el('figure');
    var img = el('img');
    img.src = t.photo; img.alt = t.title; img.decoding = 'async';
    fig.appendChild(img);
    card.appendChild(fig);
    card.appendChild(el('div', 'top-num', esc(t.num)));
    card.appendChild(el('h3', null, esc(t.title)));
    card.appendChild(el('p', null, esc(t.text)));
    var priceBox = el('div', 'top-price');
    var pl = el('a', null, esc(t.price || 'Узнать цену'));
    pl.href = '#form';
    priceBox.appendChild(pl);
    card.appendChild(priceBox);
    tg.appendChild(card);
  });

  /* --- Список услуг --- */
  var sl = $('#svcList');
  (S.services || []).forEach(function (s, i) {
    var li = el('li');
    li.appendChild(el('span', 'idx', String(i + 1).padStart(2, '0')));
    li.appendChild(el('b', null, esc(s.title)));
    li.appendChild(el('span', null, esc(s.note)));
    sl.appendChild(li);
  });

  /* --- Цены --- */
  var pb = $('#priceBody');
  (S.priceRows || []).forEach(function (r) {
    var tr2 = el('tr');
    tr2.appendChild(el('td', null, esc(r.name)));
    var td = el('td');
    var a = el('a', null, esc(r.price || 'Узнать цену'));
    a.href = '#form';
    td.appendChild(a);
    tr2.appendChild(td);
    pb.appendChild(tr2);
  });

  /* --- О себе: факты --- */
  var af = $('#aboutFacts');
  (S.aboutFacts || []).forEach(function (f) {
    var li = el('li');
    li.appendChild(el('span', null, esc(f.k)));
    li.appendChild(el('em', null, esc(f.v)));
    af.appendChild(li);
  });

  /* --- География --- */
  var al = $('#areaList');
  (S.areas || []).forEach(function (a) {
    al.appendChild(el('li', 'area-card', esc(a)));
  });

  /* --- Вопросы --- */
  var fl = $('#faqList');
  (S.faq || []).forEach(function (f) {
    var d = el('div', 'faq-item');
    d.appendChild(el('h3', null, esc(f.q)));
    d.appendChild(el('p', null, esc(f.a)));
    fl.appendChild(d);
  });

  /* --- Отзывы с Профи.ру --- */
  set('#reviewsTitle', S.reviewsTitle);
  set('#reviewsSub', S.reviewsSub);

  function fmtCount(n) {
    return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
  }
  function renderReviews(items, count, rating) {
    var grid = $('#reviewsGrid');
    grid.innerHTML = '';
    (items || []).forEach(function (r) {
      var card = el('article', 'review-card');
      var top = el('div', 'review-top');
      var left = el('div');
      left.appendChild(el('div', 'review-author', esc(r.author || 'Клиент')));
      left.appendChild(el('div', 'review-date', esc(r.date || '')));
      top.appendChild(left);
      top.appendChild(el('div', 'review-mark', '★★★★★'));
      card.appendChild(top);
      card.appendChild(el('p', 'review-text', esc(r.text || '')));
      if (r.service) card.appendChild(el('div', 'review-service', esc(r.service)));
      grid.appendChild(card);
    });
    if (count) {
      set('#reviewsCount', fmtCount(count) + ' отзывов');
      var link = $('#reviewsLink');
      if (link) link.textContent = 'Все ' + fmtCount(count) + ' отзывов на Профи.ру';
    }
    if (rating) set('#reviewsScore', String(rating).replace('.', ','));
    set('#reviewsStars', '★★★★★');
  }

  var rl = $('#reviewsLink');
  if (rl && S.reviewsLink) { rl.href = S.reviewsLink; rl.textContent = S.reviewsLinkText || 'Все отзывы на Профи.ру'; }

  renderReviews(S.reviewsFallback, 140, 5);

  if (S.reviewsApi) {
    fetch(S.reviewsApi, { cache: 'no-store' })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (d) {
        if (!d || !d.reviews || !d.reviews.length) return;
        renderReviews(d.reviews, d.count, d.rating);
        if (d.count) {
          var at = $('#aboutText');
          if (at) at.textContent = at.textContent.replace(/\{REVIEWS\}/g, fmtCount(d.count)).replace(/более\s+(\d+)\s+отзывов/i, 'более ' + fmtCount(d.count) + ' отзывов');
          var ld = document.getElementById('ld-business');
          if (ld) {
            try {
              var data = JSON.parse(ld.textContent);
              var node = null;
              (data['@graph'] || []).forEach(function (n) { if (n['@type'] === 'AutomotiveBusiness') node = n; });
              if (node && node.aggregateRating) node.aggregateRating.reviewCount = String(d.count);
              ld.textContent = JSON.stringify(data);
            } catch (e) {}
          }
        }
        if (d.fetched_at) {
          var when = new Date(d.fetched_at);
          var txt = 'Обновлено ' + when.toLocaleString('ru-RU', { day: 'numeric', month: 'long', hour: '2-digit', minute: '2-digit' });
          set('#reviewsUpdated', txt);
        }
      })
      .catch(function () {});
  }

  /* --- Галерея --- */
  var g = $('#gallery');
  (S.gallery || []).forEach(function (p) {
    var fig = el('figure');
    var img = el('img');
    img.src = p.src; img.alt = p.caption; img.loading = 'lazy';
    fig.appendChild(img);
    fig.appendChild(el('figcaption', null, esc(p.caption)));
    g.appendChild(fig);
  });

  /* --- Этапы --- */
  var st = $('#steps');
  (S.steps || []).forEach(function (s) {
    var li = el('li');
    li.appendChild(el('span', 'num', esc(s.num)));
    li.appendChild(el('h3', null, esc(s.title)));
    li.appendChild(el('p', null, esc(s.text)));
    st.appendChild(li);
  });

  /* --- Форма --- */
  var form = $('#requestForm');
  var status = $('#formStatus');
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    status.textContent = 'Отправляю…';
    status.className = 'form-status';
    var body = new URLSearchParams(new FormData(form)).toString();
    var done = function (ok) {
      if (!ok) return;
      form.reset();
      status.textContent = 'Заявка отправлена. Напишу вам в ближайшее время.';
      status.className = 'form-status ok';
    };
    var fail = function () {
      status.textContent = 'Не отправилось. Попробуйте ещё раз или напишите в мессенджер.';
      status.className = 'form-status err';
    };

    /* Заявка уходит только в Telegram-бот (одна копия). */
    if (S.relayUrl) {
      fetch(S.relayUrl, {
        method: 'POST',
        mode: 'cors',
        keepalive: true,
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: body
      }).then(function (r) {
        if (!r.ok) throw new Error('bad');
        done(true);
      }).catch(function () {
        /* Резерв: если бот недоступен — отправляем через форму сайта */
        fetch(form.action, { method: 'POST', body: body })
          .then(function (r) { done(r.ok); })
          .catch(function () { fail(); });
      });
    } else {
      fetch(form.action, { method: 'POST', body: body })
        .then(function (r) { done(r.ok); })
        .catch(function () { fail(); });
    }
  });
})();


/* --- Карусели (свайп + стрелки) --- */
(function () {
  function stepOf(track) {
    var card = track.querySelector('.review-card, .area-card');
    if (!card) return 320;
    var gap = parseFloat(getComputedStyle(track).columnGap || getComputedStyle(track).gap || 16) || 16;
    return card.getBoundingClientRect().width + gap;
  }
  function init(btn) {
    var track = document.getElementById(btn.getAttribute('data-target'));
    if (!track) return;
    btn.addEventListener('click', function () {
      var dir = btn.classList.contains('carousel-next') ? 1 : -1;
      track.scrollBy({ left: dir * stepOf(track), behavior: 'smooth' });
    });
  }
  Array.prototype.forEach.call(document.querySelectorAll('.carousel-btn'), init);

  /* подсказка исчезает, когда пользователь начал листать сам */
  Array.prototype.forEach.call(document.querySelectorAll('.carousel'), function (car) {
    var track = car.querySelector('.carousel-track, .area-list');
    if (!track) return;
    var hint = car.parentNode.querySelector('.swipe-hint');
    if (!hint) return;
    track.addEventListener('scroll', function () {
      if (Math.abs(track.scrollLeft) > 8) hint.classList.add('is-hidden');
    }, { passive: true });
  });
})();
