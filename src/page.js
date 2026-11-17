(function () {
  // Правило главной: видно не более 8 карточек. «Показать ещё» открывает следующую
  // порцию (до 8); если остались ещё скрытые — рядом видна и кнопка «Скрыть»,
  // которая сворачивает блок обратно к первым 8. Когда открыты все карточки,
  // остаётся только «Скрыть».
  var BATCH = 8;
  var more = document.getElementById('cards-more');
  var hide = document.getElementById('cards-hide');
  var wrap = document.getElementById('cards-more-wrap');
  if (!more || !hide || !wrap) return;
  var initial = document.querySelectorAll('#cards > [hidden]');
  if (!initial.length) { wrap.hidden = true; return; }
  var expanded = false;
  var hidden = function () { return document.querySelectorAll('#cards > [hidden]'); };
  var sync = function () {
    var remaining = hidden().length;
    more.hidden = expanded && !remaining;
    hide.hidden = !expanded;
    more.setAttribute('aria-expanded', String(expanded && !remaining));
  };
  more.addEventListener('click', function () {
    var h = hidden();
    for (var i = 0; i < h.length && i < BATCH; i++) {
      h[i].hidden = false;
      h[i].classList.add('card--in');
    }
    if (h.length) h[0].querySelector('a').focus({ preventScroll: true });
    expanded = true;
    sync();
  });
  hide.addEventListener('click', function () {
    for (var i = 0; i < initial.length; i++) {
      initial[i].hidden = true;
      initial[i].classList.remove('card--in');
    }
    expanded = false;
    sync();
    document.getElementById('konfiguracii').scrollIntoView({ block: 'start' });
  });

  var menu = document.getElementById('menu');
  var open = document.getElementById('menu-open');
  if (!menu || !menu.showModal) return;
  open.addEventListener('click', function () { menu.showModal(); });
  menu.addEventListener('click', function (e) {
    // закрываем по клику на фон, на крестик и на любую ссылку меню
    if (e.target === menu || e.target.closest('a, .menu__close')) menu.close();
  });
})();

// Значок рассрочки: открывает окно с краткими условиями Сплита.
// Закрытие — крестик, клик по фону, Esc (встроено в <dialog>).
(function () {
  var dlg = document.getElementById('split-info');
  if (!dlg || !dlg.showModal) return;
  document.addEventListener('click', function (e) {
    var t = e.target.closest && e.target.closest('.card__split');
    if (t) {
      e.preventDefault();
      // showModal переводит фокус в диалог внизу страницы — браузер прыгает скроллом; возвращаем позицию
      var x = window.scrollX, y = window.scrollY;
      dlg.showModal();
      window.scrollTo(x, y);
      requestAnimationFrame(function () { window.scrollTo(x, y); });
      return;
    }
    if (dlg.open && (e.target === dlg || e.target.closest('.split-info .menu__close'))) dlg.close();
  });
})();
