/* Кнопка «Дублировать» для Sveltia CMS (коллекция «Страницы сборок»).
 *
 * Как работает: на странице коллекции рядом с кнопкой «Удалить» появляется
 * «Дублировать». Отметьте галочками одну или несколько страниц сборок — копии
 * создадутся через GitHub сразу, и первая из них откроется на редактирование.
 * В названии копии в конце добавляется « - копия», в адресе — «-kopiya»
 * (если такой адрес занят, добавляется -2, -3 и т.д. — при сохранении можно поменять).
 *
 * Технически: кнопка добавляется в тулбар коллекции обычным DOM-скриптом
 * (Sveltia не даёт API для своих кнопок), данные читаются из localStorage
 * («sveltia-cms.user» — токен входа), файлы создаются через GitHub Contents API.
 */
(function () {
  var REPO = 'sirlondog/star-comp_cl';
  var DIR = 'content/builds';
  var COLLECTION = 'builds';
  var API = 'https://api.github.com/repos/' + REPO + '/contents/' + DIR;

  var busy = false;

  function getUser() {
    try { return JSON.parse(localStorage.getItem('sveltia-cms.user') || 'null'); } catch (e) { return null; }
  }

  function getToken() {
    var u = getUser();
    return u && u.token ? u.token : null;
  }

  function api(method, url, body, raw) {
    var token = getToken();
    return fetch(url, {
      method: method,
      headers: {
        Authorization: 'Bearer ' + token,
        Accept: raw ? 'application/vnd.github.raw' : 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28',
      },
      body: body ? JSON.stringify(body) : undefined,
    }).then(function (r) {
      if (!r.ok) { return r.json().then(function (j) { throw new Error((j && j.message) || ('HTTP ' + r.status)); }); }
      return raw ? r.text() : r.json();
    });
  }

  /* имя → {slug, json} по всем файлам коллекции */
  function loadEntries() {
    return api('GET', API).then(function (list) {
      var files = list.filter(function (f) { return f.name.endsWith('.json'); });
      return Promise.all(files.map(function (f) {
        var slug = f.name.replace(/\.json$/, '');
        return api('GET', API + '/' + f.name, null, true).then(function (text) {
          try { return { slug: slug, json: JSON.parse(text) }; } catch (e) { return null; }
        });
      })).then(function (entries) { return entries.filter(Boolean); });
    });
  }

  function makeSlug(base, taken) {
    var slug = base + '-kopiya';
    var n = 2;
    while (taken.indexOf(slug) !== -1) { slug = base + '-kopiya-' + n; n += 1; }
    return slug;
  }

  function duplicateSelected() {
    if (busy) return;
    var token = getToken();
    if (!token) { alert('Дублирование: нет токена входа. Перелогиньтесь в админке.'); return; }

    /* выбранные строки: чекбоксы с aria-label «Select ⁨Имя⁩» и aria-checked=true */
    var checked = Array.prototype.slice.call(
      document.querySelectorAll('button[role="checkbox"][aria-checked="true"]')
    ).filter(function (b) { return /^Select ⁨/.test(b.getAttribute('aria-label') || ''); });

    if (!checked.length) { alert('Сначала отметьте галочками страницы, которые нужно продублировать.'); return; }

    /* работаем только в коллекции «Страницы сборок» */
    if (location.hash.indexOf('#/collections/' + COLLECTION) !== 0) return;

    var names = checked.map(function (b) {
      var row = b.closest('.grid-row');
      return row ? (row.getAttribute('aria-label') || '').trim() : '';
    }).filter(Boolean);

    busy = true;
    setButtonBusy(true);

    loadEntries()
      .then(function (entries) {
        var taken = entries.map(function (e) { return e.slug; });
        var jobs = [];
        var opened = null;

        names.forEach(function (name) {
          var src = entries.find(function (e) { return e.json.name === name; });
          if (!src) return; /* имя не нашлось — пропускаем */
          var slug = makeSlug(src.slug, taken);
          taken.push(slug);
          var copy = JSON.parse(JSON.stringify(src.json));
          copy.name = src.json.name + ' - копия';
          copy.slug = slug;
          if (!opened) { opened = slug; }
          jobs.push(api('PUT', API + '/' + slug + '.json', {
            message: 'Админка: создана копия «' + src.slug + '» → «' + slug + '»',
            content: btoa(unescape(encodeURIComponent(JSON.stringify(copy, null, 2) + '\n'))),
          }));
        });

        if (!jobs.length) {
          busy = false;
          setButtonBusy(false);
          alert('Не удалось найти выбранные записи в репозитории. Обновите страницу и попробуйте ещё раз.');
          return;
        }

        return Promise.all(jobs).then(function () {
          /* копии готовы: перезагружаем админку и открываем первую копию */
          location.hash = '#/collections/' + COLLECTION + '/entries/' + opened;
          location.reload();
        });
      })
      .catch(function (e) {
        busy = false;
        setButtonBusy(false);
        alert('Не получилось создать копию: ' + (e && e.message ? e.message : 'неизвестная ошибка'));
      });
  }

  function setButtonBusy(state) {
    var b = document.getElementById('sveltia-duplicate-btn');
    if (!b) return;
    b.setAttribute('aria-disabled', state ? 'true' : 'false');
    b.style.opacity = state ? '.5' : '';
    var label = b.querySelector('.sui-dup-label');
    if (label) { label.textContent = state ? 'Копирую…' : 'Дублировать'; }
  }

  function buildButton() {
    var b = document.createElement('button');
    b.type = 'button';
    b.id = 'sveltia-duplicate-btn';
    b.className = 'sui button ghost medium';
    b.setAttribute('aria-label', 'Дублировать выбранные записи');
    b.setAttribute('aria-keyshortcuts', '');
    b.title = 'Создать копии выбранных страниц сборок и открыть первую для редактирования';
    b.innerHTML =
      '<span class="label" dir=""><span class="sui-dup-label">Дублировать</span></span>';
    b.style.marginLeft = 'auto';
    b.addEventListener('click', duplicateSelected);
    return b;
  }

  /* следим за DOM: тулбар коллекции перерисовывается Sveltia, кнопка должна жить постоянно */
  function inject() {
    /* только в коллекции «Страницы сборок» */
    if (location.hash.indexOf('#/collections/' + COLLECTION) !== 0) { remove(); return; }
    var del = Array.prototype.slice.call(document.querySelectorAll('button'))
      .find(function (b) { return /^Удалить выбран/.test(b.getAttribute('aria-label') || ''); });
    if (!del) { remove(); return; }
    if (document.getElementById('sveltia-duplicate-btn')) {
      /* кнопка уже есть; если Sveltia перерисовал тулбар — переносим её в конец */
      if (del.nextElementSibling !== document.getElementById('sveltia-duplicate-btn')) {
        del.insertAdjacentElement('afterend', document.getElementById('sveltia-duplicate-btn'));
      }
      return;
    }
    del.insertAdjacentElement('afterend', buildButton());
  }

  function remove() {
    var b = document.getElementById('sveltia-duplicate-btn');
    if (b) { b.remove(); }
  }

  var mo = new MutationObserver(function () { inject(); });
  mo.observe(document.body, { childList: true, subtree: true });
  inject();
})();
