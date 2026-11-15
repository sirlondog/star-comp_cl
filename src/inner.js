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
  // Видео: плеер не грузится, пока человек не нажал на обложку.
  // Если ролик вертикальный (.video--vertical), он всегда вертикальный;
  // иначе на десктопе горизонтальный, на телефоне вертикальный.
  // На телефоне вертикальное видео запускается сразу: без звука, в цикле, без кнопок.
  var v = document.getElementById('video');
  if (!v) return;
  var vertical = v.classList.contains('video--vertical');
  function play(id, background, sound) {
    var f = document.createElement('iframe');
    // background=1 — фоновое видео без кнопок; sound — со звуком и элементами управления
    f.src = 'https://kinescope.io/embed/' + id + '?autoplay=1&loop=1&playsinline=1&transparent=1' + (sound ? '' : '&muted=1') + (background ? '&background=1&controls=0' : '');
    f.title = v.dataset.title || 'Видео';
    f.allow = 'autoplay; fullscreen; picture-in-picture; encrypted-media';
    f.allowFullscreen = true;
    f.style.background = '#000';
    var old = v.querySelector('iframe');
    if (old) {
      // замена плеера: Chromium рисует новый iframe белым, пока грузится документ,
      // поэтому новый держим прозрачным до загрузки, а старый показываем до этого момента
      Array.prototype.forEach.call(v.children, function (c) { if (c !== old) c.remove(); });
      f.style.opacity = '0';
      f.style.transition = 'opacity .25s';
      var swap = function () {
        f.style.opacity = '1';
        old.remove();
      };
      f.addEventListener('load', swap);
      // если load задержится (медленная сеть), показываем новый плеер по таймауту
      setTimeout(function () {
        if (old.parentNode === v) swap();
      }, 5000);
    } else {
      v.innerHTML = '';
    }
    v.appendChild(f);
  }
  if (window.matchMedia('(max-width:63.99rem)').matches) {
    var id = v.dataset.v || v.dataset.h;
    // на телефоне вертикальное видео играет сразу: без звука, в цикле, без кнопок
    play(id, true, false);
    // тап по видео: обычный плеер — появляются элементы управления и включается звук.
    // Слой-перехватчик нужен, чтобы тап не уходил внутрь фонового плеера
    var tap = document.createElement('div');
    tap.style.cssText = 'position:absolute;inset:0;z-index:2;cursor:pointer';
    v.appendChild(tap);
    tap.addEventListener('click', function () { play(id, false, true); });
  } else {
    v.querySelector('.video__play').addEventListener('click', function () {
      play(vertical || !window.matchMedia('(min-width:64rem)').matches ? v.dataset.v : v.dataset.h, false, false);
    });
  }
})();
