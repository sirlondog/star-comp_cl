(function () {
  // Галерея: точки и стрелки включаются сами, когда фото больше одного
  var g = document.getElementById('gallery');
  if (!g) return;
  var track = g.querySelector('.gallery__track');
  var slides = track.children;
  if (slides.length < 2) return;
  var dots = g.querySelector('.gallery__dots');
  var prev = g.querySelector('.gallery__nav--prev');
  var next = g.querySelector('.gallery__nav--next');
  var current = 0;
  function go(i) { track.scrollTo({ left: track.clientWidth * i, behavior: 'smooth' }); }
  function update() {
    current = Math.round(track.scrollLeft / track.clientWidth);
    for (var i = 0; i < dots.children.length; i++) dots.children[i].setAttribute('aria-current', String(i === current));
    prev.disabled = current === 0;
    next.disabled = current === slides.length - 1;
  }
  for (var i = 0; i < slides.length; i++) {
    var b = document.createElement('button');
    b.type = 'button';
    b.setAttribute('aria-label', 'Фото ' + (i + 1) + ' из ' + slides.length);
    b.addEventListener('click', go.bind(null, i));
    dots.appendChild(b);
  }
  dots.hidden = false;
  g.classList.add('gallery--many');
  prev.addEventListener('click', function () { go(current - 1); });
  next.addEventListener('click', function () { go(current + 1); });
  track.addEventListener('scroll', update, { passive: true });
  update();
})();

(function () {
  // Видео: плеер не грузится, пока человек не нажал на обложку.
  // На десктопе берём горизонтальный ролик, на телефоне — вертикальный.
  var v = document.getElementById('video');
  if (!v) return;
  v.querySelector('.video__play').addEventListener('click', function () {
    var id = window.matchMedia('(min-width:64rem)').matches ? v.dataset.h : v.dataset.v;
    var f = document.createElement('iframe');
    f.src = 'https://kinescope.io/embed/' + id + '?autoplay=1';
    f.title = 'Видео о сборке SOLAR S1';
    f.allow = 'autoplay; fullscreen; picture-in-picture; encrypted-media';
    f.allowFullscreen = true;
    v.innerHTML = '';
    v.appendChild(f);
  });
})();
