(function () {
  // «Показать ещё» открывает по 3 скрытые карточки (их фото грузятся только в этот момент);
  // когда открыты все, кнопка превращается в «Скрыть» и возвращает блок в исходный вид
  var more = document.getElementById('cards-more');
  var extra = document.querySelectorAll('#cards > [hidden]');
  if (more && extra.length) more.addEventListener('click', function () {
    var hidden = document.querySelectorAll('#cards > [hidden]');
    var i;
    if (hidden.length) {
      for (i = 0; i < hidden.length && i < 3; i++) {
        hidden[i].hidden = false;
        hidden[i].classList.add('card--in');
      }
      hidden[0].querySelector('a').focus({ preventScroll: true });
      if (hidden.length <= 3) more.textContent = 'Скрыть';
    } else {
      for (i = 0; i < extra.length; i++) {
        extra[i].hidden = true;
        extra[i].classList.remove('card--in');
      }
      more.textContent = 'Показать ещё';
      document.getElementById('konfiguracii').scrollIntoView({ block: 'start' });
    }
    more.setAttribute('aria-expanded', String(!document.querySelector('#cards > [hidden]')));
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
