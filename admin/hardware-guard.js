/* Предупреждение о дублях в «Базе железа» для Sveltia CMS.
 *
 * Пока владелец заполняет модель на странице коллекции «База железа», скрипт
 * сверяет её с моделями, которые уже есть в репозитории (GitHub). Если такая
 * модель уже есть — над редактором появляется красная плашка «Это дубль».
 * Sveltia не умеет блокировать сохранение по значению поля, поэтому это
 * предупреждение, а не запрет: запишите модель по-другому, если это другой товар.
 */
(function () {
  var API = 'https://api.github.com/repos/sirlondog/star-comp_cl/contents/content/hardware';
  var COLLECTION = 'hardware';
  var known = null;          // [{model, file}]
  var banner = null;

  function getToken() {
    try {
      var u = JSON.parse(localStorage.getItem('sveltia-cms.user') || 'null');
      return u && u.token ? u.token : null;
    } catch (e) { return null; }
  }

  function headers() {
    var h = { Accept: 'application/vnd.github.raw' };
    var token = getToken();
    if (token) { h.Authorization = 'Bearer ' + token; }
    return h;
  }

  /* список моделей из репозитория; обновляем не чаще раза в 10 минут */
  var fetchedAt = 0;
  function loadKnown() {
    if (known && Date.now() - fetchedAt < 10 * 60 * 1000) { return Promise.resolve(known); }
    return fetch(API, { headers: headers() })
      .then(function (r) { return r.json(); })
      .then(function (list) {
        var files = (Array.isArray(list) ? list : []).filter(function (f) { return f.name.endsWith('.json'); });
        return Promise.all(files.map(function (f) {
          return fetch(f.url, { headers: headers() })
            .then(function (r) { return r.text(); })
            .then(function (text) {
              var d = null;
              try { d = JSON.parse(text); } catch (e) { return null; }
              return { model: ((d && d.model) || '').trim(), file: f.name.replace(/\.json$/, '') };
            })
            .catch(function () { return null; });
        }));
      })
      .then(function (arr) {
        known = arr.filter(Boolean);
        fetchedAt = Date.now();
        return known;
      })
      .catch(function () { known = known || []; return known; });
  }

  function norm(s) { return (s || '').trim().toLowerCase(); }

  function currentFile() {
    var m = location.hash.match(/collections\/hardware\/entries\/([^#?]+)/);
    return m ? decodeURIComponent(m[1]) : '';
  }

  function show(hit) {
    if (!banner) {
      banner = document.createElement('div');
      banner.id = 'sveltia-dupe-warning';
      banner.style.cssText =
        'position:fixed;top:0;left:0;right:0;z-index:99999;padding:10px 16px;' +
        'background:#c62828;color:#fff;font:600 14px/1.4 -apple-system,Segoe UI,Roboto,sans-serif;' +
        'text-align:center;box-shadow:0 2px 8px rgba(0,0,0,.4)';
      document.body.appendChild(banner);
    }
    banner.textContent = '⚠ В «Базе железа» уже есть модель «' + hit.model + '» (' + hit.file +
      '). Не сохраняйте дубль — отредактируйте существующую запись или впишите другую модель.';
  }

  function hide() {
    if (banner) { banner.remove(); banner = null; }
  }

  function check() {
    if (location.hash.indexOf('#/collections/' + COLLECTION) !== 0) { hide(); return; }
    if (!known || !known.length) { hide(); return; }
    var own = currentFile();
    var inputs = Array.prototype.slice.call(document.querySelectorAll('.page-root input[type="text"]'));
    var hit = null;
    for (var i = 0; i < inputs.length && !hit; i++) {
      var v = norm(inputs[i].value);
      if (!v) { continue; }
      for (var j = 0; j < known.length && !hit; j++) {
        var k = known[j];
        if (norm(k.model) === v && k.file !== own) { hit = k; }
      }
    }
    if (hit) { show(hit); } else { hide(); }
  }

  /* перечитываем модели, когда владелец открывает коллекцию железа */
  document.addEventListener('click', function (e) {
    var t = e.target.closest && e.target.closest('a[href*="#/collections/hardware"]');
    if (t) { loadKnown().then(check); }
  });

  document.addEventListener('input', function () {
    if (location.hash.indexOf('#/collections/' + COLLECTION) === 0) { check(); }
  }, true);

  var mo = new MutationObserver(function () { check(); });
  mo.observe(document.body, { childList: true, subtree: true });
  check();
})();
