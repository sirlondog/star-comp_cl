(function () {
  var STEPS = window.QUIZ_STEPS || [];
  if (!STEPS.length) {
    return;
  }

  var BY_ID = {};
  STEPS.forEach(function (step) {
    BY_ID[step.id] = step;
  });

  var ICONS = {
    phone: '<path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2z"/>',
    chat: '<path d="M4 5h16v11H9l-5 4z"/><path d="M8 9h8M8 12h5"/>',
    plane: '<path d="M21 4 3 11l6 2 2 7 3-4 5 4z"/>'
  };

  var dialog = document.createElement('dialog');
  dialog.className = 'quiz';
  dialog.setAttribute('aria-label', 'Подбор компьютера');
  dialog.innerHTML =
    '<div class="quiz__card">' +
      '<div class="quiz__progress"><div class="quiz__progress-bar" style="width: 0%"></div></div>' +
      '<div class="quiz__top">' +
        '<p class="quiz__counter"></p>' +
        '<button type="button" class="quiz__close" aria-label="Закрыть квиз">&times;</button>' +
      '</div>' +
      '<div class="quiz__body"></div>' +
    '</div>';
  document.body.appendChild(dialog);

  var bar = dialog.querySelector('.quiz__progress-bar');
  var counter = dialog.querySelector('.quiz__counter');
  var body = dialog.querySelector('.quiz__body');
  var history = [];
  var answers = {};
  var total = 1;

  function esc(value) {
    return String(value == null ? '' : value).replace(/[&<>"']/g, function (ch) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[ch];
    });
  }

  function longestPath(id, seen) {
    var step = BY_ID[id];
    if (!step || seen.indexOf(id) !== -1) {
      return 0;
    }
    var targets = [step.next].concat((step.options || []).map(function (opt) {
      return opt.next;
    }));
    var best = 0;
    targets.forEach(function (target) {
      if (target) {
        best = Math.max(best, longestPath(target, seen.concat([id])));
      }
    });
    return 1 + best;
  }

  function formatBudget(value) {
    return String(value).replace(/\B(?=(\d{3})+(?!\d))/g, '\u00A0') + '\u00A0₽';
  }

  function formatPhone(value) {
    var digits = value.replace(/\D/g, '');
    if (digits.length > 10 && (digits.charAt(0) === '7' || digits.charAt(0) === '8')) {
      digits = digits.slice(1);
    }
    digits = digits.slice(0, 10);
    var parts = [digits.slice(0, 3), digits.slice(3, 6), digits.slice(6, 8), digits.slice(8, 10)];
    return parts.filter(Boolean).join(' ');
  }

  function navHtml(step, withNext) {
    var back = history.length > 1 ? '<button type="button" class="quiz__back" data-back>Назад</button>' : '';
    var next = withNext ? '<button type="button" class="quiz__next" data-next>' + esc(step.button || 'Далее') + '</button>' : '';
    return '<div class="quiz__nav">' + back + next + '</div>';
  }

  function render() {
    var id = history[history.length - 1];
    var step = BY_ID[id];
    var saved = answers[id];

    counter.innerHTML = 'Шаг ' + history.length + ' из ' + total;
    bar.style.width = Math.min(100, Math.round(history.length / total * 100)) + '%';

    var notice = step.notice ? '<p class="quiz__notice">' + esc(step.notice) + '</p>' : '';
    var error = '<p class="quiz__error" hidden>' + esc(step.error || 'Заполните поле') + '</p>';
    var title = '<h2 class="quiz__title">' + esc(step.title) + '</h2>';
    var html = '';

    if (step.type === 'choice') {
      var list = step.style === 'list';
      var selected = saved ? saved.index : -1;
      var options = (step.options || []).map(function (opt, index) {
        var cls = list ? 'quiz__option quiz__option--radio' : 'quiz__option quiz__option--card';
        if (index === selected) {
          cls += ' is-selected';
        }
        var inner = '';
        if (list) {
          inner = '<span class="quiz__radio" aria-hidden="true"></span>' +
            '<span class="quiz__option-title">' + esc(opt.label) + '</span>';
        } else {
          var icon = ICONS[opt.icon] ? '<span class="quiz__option-icon" aria-hidden="true"><svg viewBox="0 0 24 24">' + ICONS[opt.icon] + '</svg></span>' : '';
          var note = opt.note ? '<span class="quiz__option-note">' + esc(opt.note) + '</span>' : '';
          inner = icon + '<span class="quiz__option-title">' + esc(opt.label) + '</span>' + note;
        }
        return '<button type="button" class="' + cls + '" data-index="' + index + '" role="' + (list ? 'radio' : 'button') + '"' +
          (list ? ' aria-checked="' + (index === selected) + '"' : '') + '>' + inner + '</button>';
      }).join('');
      html = title +
        '<div class="quiz__options' + (list ? ' quiz__options--list' : '') + '"' + (list ? ' role="radiogroup"' : '') + '>' + options + '</div>' +
        notice + error + navHtml(step, list);
    } else if (step.type === 'text') {
      var text = saved || '';
      html = title +
        '<label class="quiz__field"><textarea class="quiz__input" rows="4" placeholder="' + esc(step.hint) + '">' + esc(text) + '</textarea></label>' +
        notice + error + navHtml(step, true);
    } else if (step.type === 'slider') {
      var conf = step.slider || {};
      var min = Number(conf.min) || 0;
      var max = Number(conf.max) || 100;
      var stepSize = Number(conf.step) || 1;
      var value = saved != null ? saved : (Number(conf.default) || min);
      html = title +
        '<div class="budget">' +
          '<output class="budget__amount">' + formatBudget(value) + '</output>' +
          '<input type="range" class="budget__slider" min="' + min + '" max="' + max + '" step="' + stepSize + '" value="' + value + '" aria-label="' + esc(step.title) + '">' +
          '<div class="budget__range"><span>' + formatBudget(min) + '</span><span>' + formatBudget(max) + '</span></div>' +
        '</div>' +
        notice + error + navHtml(step, true);
    } else if (step.type === 'phone' || step.type === 'login') {
      var isPhone = step.type === 'phone';
      var field = isPhone
        ? '<label class="quiz__field quiz__phone-field"><span class="quiz__phone-prefix" aria-hidden="true">+7</span>' +
          '<input type="tel" class="quiz__input quiz__input--single quiz__phone" inputmode="tel" autocomplete="tel" placeholder="' + esc(step.hint || '000 000 00 00') + '" value="' + esc(saved ? saved.replace(/^\+7\s?/, '') : '') + '"></label>'
        : '<label class="quiz__field"><input type="text" class="quiz__input quiz__input--single quiz__login" autocomplete="username" placeholder="' + esc(step.hint || 'Ваш логин') + '" value="' + esc(saved || '') + '"></label>';
      html = title +
        '<form class="quiz__form" novalidate>' + field + notice + error +
          '<div class="quiz__nav">' +
            (history.length > 1 ? '<button type="button" class="quiz__back" data-back>Назад</button>' : '') +
            '<button type="submit" class="quiz__next quiz__submit">' + esc(step.button || 'Далее') + '</button>' +
          '</div>' +
        '</form>';
    }

    body.innerHTML = '<div class="quiz__step">' + html + '</div>';
    bind(step);
    var first = body.querySelector('input, textarea, .quiz__option');
    if (first) {
      first.focus();
    }
  }

  function bind(step) {
    var list = step.type === 'choice' && step.style === 'list';

    body.querySelectorAll('.quiz__option').forEach(function (button) {
      button.addEventListener('click', function () {
        var index = Number(button.dataset.index);
        var opt = step.options[index];
        if (list) {
          answers[step.id] = { index: index, label: opt.label, next: opt.next || step.next || '' };
          body.querySelectorAll('.quiz__option').forEach(function (item) {
            item.classList.toggle('is-selected', item === button);
            item.setAttribute('aria-checked', String(item === button));
          });
          body.querySelector('.quiz__error').hidden = true;
          return;
        }
        answers[step.id] = { index: index, label: opt.label };
        advance(opt.next || step.next || '');
      });
    });

    var nextBtn = body.querySelector('[data-next]');
    if (nextBtn) {
      nextBtn.addEventListener('click', function () {
        if (step.type === 'choice') {
          var saved = answers[step.id];
          if (!saved) {
            body.querySelector('.quiz__error').hidden = false;
            return;
          }
          advance(saved.next);
          return;
        }
        if (step.type === 'text') {
          answers[step.id] = body.querySelector('textarea').value.trim();
        }
        if (step.type === 'slider') {
          answers[step.id] = Number(body.querySelector('.budget__slider').value);
        }
        advance(step.next || '');
      });
    }

    var slider = body.querySelector('.budget__slider');
    if (slider) {
      slider.addEventListener('input', function () {
        body.querySelector('.budget__amount').textContent = formatBudget(slider.value);
        slider.style.setProperty('--fill', ((slider.value - slider.min) / (slider.max - slider.min) * 100) + '%');
      });
      slider.dispatchEvent(new Event('input'));
    }

    var phone = body.querySelector('.quiz__phone');
    if (phone) {
      phone.addEventListener('input', function () {
        phone.value = formatPhone(phone.value);
        body.querySelector('.quiz__error').hidden = true;
      });
    }

    var login = body.querySelector('.quiz__login');
    if (login) {
      login.addEventListener('input', function () {
        body.querySelector('.quiz__error').hidden = true;
      });
    }

    var form = body.querySelector('.quiz__form');
    if (form) {
      form.addEventListener('submit', function (event) {
        event.preventDefault();
        var error = body.querySelector('.quiz__error');
        if (phone) {
          if (phone.value.replace(/\D/g, '').length !== 10) {
            error.hidden = false;
            phone.focus();
            return;
          }
          answers[step.id] = '+7 ' + phone.value;
        } else {
          if (!login.value.trim()) {
            error.hidden = false;
            login.focus();
            return;
          }
          answers[step.id] = login.value.trim();
        }
        advance(step.next || '');
      });
    }

    body.querySelectorAll('[data-back]').forEach(function (button) {
      button.addEventListener('click', back);
    });
  }

  function advance(target) {
    if (!target || !BY_ID[target]) {
      finish();
      return;
    }
    history.push(target);
    render();
  }

  function back() {
    if (history.length > 1) {
      history.pop();
      render();
    }
  }

  function finish() {
    var data = {};
    Object.keys(answers).forEach(function (id) {
      data[id] = answers[id];
    });
    document.dispatchEvent(new CustomEvent('quiz:submit', { detail: { answers: data, path: history.slice() } }));
    dialog.close();
  }

  function open() {
    history = [STEPS[0].id];
    answers = {};
    total = Math.max(1, longestPath(STEPS[0].id, []));
    render();
    dialog.showModal();
  }

  document.querySelectorAll('[data-quiz-open]').forEach(function (button) {
    button.addEventListener('click', open);
  });

  dialog.querySelector('.quiz__close').addEventListener('click', function () {
    dialog.close();
  });

  dialog.addEventListener('click', function (event) {
    if (event.target === dialog) {
      dialog.close();
    }
  });
})();
