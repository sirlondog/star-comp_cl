(function () {
  // Галерея: стрелки, точки под фото и крупный просмотр по нажатию на фото
  var g = document.getElementById('gallery');
  if (!g) return;
  var track = g.querySelector('.gallery__track');
  var slides = track.children;
  var n = slides.length;
  var dotsBox = g.querySelector('.gallery__dots');
  var dots = dotsBox.children;
  var prev = g.querySelector('.gallery__nav--prev');
  var next = g.querySelector('.gallery__nav--next');
  var current = 0;
  function go(i, instant) {
    i = Math.max(0, Math.min(n - 1, i));
    track.scrollTo({ left: track.clientWidth * i, behavior: instant ? 'instant' : 'smooth' });
  }
  function update() {
    current = Math.max(0, Math.min(n - 1, Math.round(track.scrollLeft / track.clientWidth)));
    for (var i = 0; i < dots.length; i++) dots[i].setAttribute('aria-current', String(i === current));
    prev.disabled = current === 0;
    next.disabled = current === n - 1;
  }
  if (n < 2) dotsBox.hidden = true;
  else g.classList.add('gallery--many');
  for (var i = 0; i < dots.length; i++) dots[i].addEventListener('click', go.bind(null, i, false));
  prev.addEventListener('click', function () { go(current - 1); });
  next.addEventListener('click', function () { go(current + 1); });
  track.addEventListener('scroll', update, { passive: true });
  update();

  // Крупный просмотр: окно создаётся только при первом нажатии
  var box, holder, count, bPrev, bNext, shown = 0;
  var arrow = function (d) { return '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="' + d + '"/></svg>'; };
  function btn(cls, label, icon) {
    var b = document.createElement('button');
    b.type = 'button';
    b.className = 'lightbox__btn ' + cls;
    b.setAttribute('aria-label', label);
    b.innerHTML = arrow(icon);
    box.appendChild(b);
    return b;
  }
  function show(i) {
    shown = Math.max(0, Math.min(n - 1, i));
    holder.classList.remove('zoomed');
    var pic = slides[shown].querySelector('picture').cloneNode(true);
    var parts = pic.querySelectorAll('source,img');
    for (var k = 0; k < parts.length; k++) { parts[k].sizes = '100vw'; parts[k].removeAttribute('loading'); }
    holder.innerHTML = '';
    holder.appendChild(pic);
    count.textContent = (shown + 1) + ' / ' + n;
    bPrev.disabled = shown === 0;
    bNext.disabled = shown === n - 1;
  }
  function build() {
    box = document.createElement('dialog');
    box.className = 'lightbox';
    box.setAttribute('aria-label', 'Просмотр фотографий');
    holder = document.createElement('div');
    holder.className = 'lightbox__img';
    box.appendChild(holder);
    count = document.createElement('p');
    count.className = 'lightbox__count';
    box.appendChild(count);
    bPrev = btn('lightbox__prev', 'Предыдущее фото', 'M10 3 5 8l5 5');
    bNext = btn('lightbox__next', 'Следующее фото', 'm6 3 5 5-5 5');
    var bClose = btn('lightbox__close', 'Закрыть', 'M3.5 3.5l9 9M12.5 3.5l-9 9');
    if (n < 2) { bPrev.hidden = bNext.hidden = count.hidden = true; }
    bPrev.addEventListener('click', function () { show(shown - 1); });
    bNext.addEventListener('click', function () { show(shown + 1); });
    bClose.addEventListener('click', function () { box.close(); });
    // клик по фото: оригинальный размер ↔ вписанный; закрытие — крестик или Esc
    holder.addEventListener('click', function (e) {
      if (e.target.closest('.lightbox__btn')) return;
      holder.classList.toggle('zoomed');
    });
    box.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowLeft') show(shown - 1);
      if (e.key === 'ArrowRight') show(shown + 1);
    });
    // листание пальцем
    var x0 = null;
    holder.addEventListener('touchstart', function (e) { x0 = e.touches.length === 1 ? e.touches[0].clientX : null; }, { passive: true });
    holder.addEventListener('touchend', function (e) {
      if (x0 === null) return;
      var dx = e.changedTouches[0].clientX - x0;
      x0 = null;
      if (Math.abs(dx) > 40) { e.preventDefault(); show(shown + (dx < 0 ? 1 : -1)); }
    });
    // после закрытия основная галерея стоит на том же фото
    box.addEventListener('close', function () { go(shown, true); });
    document.body.appendChild(box);
  }
  function open() {
    if (!box) build();
    show(current);
    box.showModal();
  }
  track.addEventListener('click', open);
  track.addEventListener('keydown', function (e) { if (e.key === 'Enter') open(); });
})();

(function () {
  // Видео: плеер создаётся через API Kinescope один раз, прячется под обложкой —
  // никаких белых вспышек и перезагрузок. Автоплей без звука на всех устройствах,
  // обложка убирается, как только видео реально играет. Тап/клик включает звук
  // через API (iPhone — исключение: команды API туда не пробиваются, жест внутри
  // фрейма — единственный способ), кнопки показывает сам плеер.
  var v = document.getElementById('video');
  if (!v) return;
  var mobile = window.matchMedia('(max-width:63.99rem)').matches;
  // на телефоне вертикальный ролик (или горизонтальный), на десктопе горизонтальный (или вертикальный)
  var id = (mobile ? (v.dataset.v || v.dataset.h) : (v.dataset.h || v.dataset.v) || '').trim();
  if (!id) return;

  // пустой слой под обложкой: API заменит его на iframe с плеером
  var slot = document.createElement('div');
  slot.id = 'kinescope-slot';
  v.insertBefore(slot, v.firstChild);

  var player = null, action = null, playing = false;
  function uncover() {
    var b = v.querySelector('.video__play');
    if (b) b.remove();
  }
  window.onKinescopeIframeAPIReady = function (factory) {
    factory.create('kinescope-slot', {
      url: 'https://kinescope.io/' + id,
      behavior: { autoPlay: true, loop: true, muted: true, playsInline: true, preload: 'metadata' }
    }).then(function (p) {
      player = p;
      // на всякий случай даём фрейму право на автоплей (важно для iPhone)
      var f = v.querySelector('iframe');
      if (f) f.allow = 'autoplay; fullscreen; picture-in-picture; encrypted-media';
      // как только видео реально играет — обложка убирается (видно замьюченное видео)
      p.on(p.Events.Playing, function () { playing = true; uncover(); });
      if (action) { var a = action; action = null; a(); }
    });
  };
  var api = document.createElement('script');
  api.src = 'https://player.kinescope.io/latest/iframe.player.js';
  document.head.appendChild(api);

  function command(fn) {
    if (player) fn();
    else action = fn;
  }

  if (/iPad|iPhone|iPod/.test(navigator.userAgent) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1)) {
    // iPhone (WebKit): команды API не пробиваются внутрь iframe, зато жест
    // внутри самого плеера всегда работает. Убираем только обложку, дальше
    // тапы идут прямо в плеер: свои кнопки, звук — кнопкой громкости в панели
    v.querySelector('.video__play').addEventListener('click', uncover);
  } else {
    // тап/клик: включается звук; кнопки (стоп/плей, громкость, на весь экран) показывает сам плеер
    var tap = document.createElement('div');
    tap.style.cssText = 'position:absolute;inset:0;z-index:2;cursor:pointer';
    v.appendChild(tap);
    tap.addEventListener('click', function () {
      tap.remove();
      uncover();
      command(function () {
        player.unmute();
        player.play();
        // страховка: если за 2с видео так и не начало играть — перезапуск по прямой ссылке
        setTimeout(function () {
          if (playing) return;
          var f = v.querySelector('iframe');
          if (f) f.src = 'https://kinescope.io/embed/' + id + '?autoplay=1&loop=1&playsinline=1&transparent=1';
        }, 2000);
      });
    });
  }
})();
