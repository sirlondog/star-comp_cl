/* Предупреждение о дублях папок картинок для Sveltia CMS.
 *
 * Папки картинок (content/photos/…) создаются на GitHub, и GitHub позволяет
 * создать папку с именем, которое уже занято (в другом регистре или с лишним
 * пробелом). Скрипт проверяет папки на одинаковые имена без учёта регистра
 * и показывает красную плашку в «Ресурсах», пока дубль не удалён.
 */
(function () {
  var API = 'https://api.github.com/repos/sirlondog/star-comp_cl/contents/content/photos';
  var banner = null;
  var known = null;
  var fetchedAt = 0;

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

  function norm(s) { return (s || '').trim().toLowerCase(); }

  function loadFolders() {
    if (known && Date.now() - fetchedAt < 10 * 60 * 1000) { return Promise.resolve(known); }
    return fetch(API, { headers: headers() })
      .then(function (r) { return r.json(); })
      .then(function (list) {
        known = (Array.isArray(list) ? list : []).filter(function (f) { return f.type === 'dir'; })
          .map(function (f) { return f.name; });
        fetchedAt = Date.now();
        return known;
      })
      .catch(function () { return known || []; });
  }

  function duplicates(folders) {
    var groups = {};
    folders.forEach(function (name) {
      var key = norm(name);
      if (!key) { return; }
      (groups[key] = groups[key] || []).push(name);
    });
    return Object.keys(groups).filter(function (key) { return groups[key].length > 1; })
      .map(function (key) { return groups[key]; });
  }

  function show(groups) {
    if (!banner) {
      banner = document.createElement('div');
      banner.id = 'sveltia-folder-dupe-warning';
      banner.style.cssText =
        'position:fixed;top:0;left:0;right:0;z-index:99999;padding:10px 16px;' +
        'background:#c62828;color:#fff;font:600 14px/1.4 -apple-system,Segoe UI,Roboto,sans-serif;' +
        'text-align:center;box-shadow:0 2px 8px rgba(0,0,0,.4)';
      document.body.appendChild(banner);
    }
    banner.textContent = '⚠ В «Ресурсах» дубли папок: ' + groups.map(function (g) {
      return '«' + g.join('», «') + '»';
    }).join('; ') + '. Оставьте одну папку из каждой пары — иначе фото двух сборок перемешаются.';
  }

  function hide() {
    if (banner) { banner.remove(); banner = null; }
  }

  function check() {
    if (location.hash.indexOf('#/assets') !== 0) { hide(); return; }
    loadFolders().then(function (folders) {
      var groups = duplicates(folders);
      if (groups.length) { show(groups); } else { hide(); }
    });
  }

  document.addEventListener('click', function (e) {
    var t = e.target.closest && e.target.closest('a[href*="#/assets"]');
    if (t) { loadFolders().then(check); }
  });

  var mo = new MutationObserver(function () { check(); });
  mo.observe(document.body, { childList: true, subtree: true });
  check();
})();
