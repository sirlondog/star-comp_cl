/* Поле «фото с точкой фокуса» для Sveltia CMS.
 *
 * Как пользоваться: выбрать файл кнопкой ниже, затем кликнуть по большому превью —
 * там поставится точка фокуса (перекрестие), и маленький кадр 4:3 покажет, что
 * окажется на карточке. Сборщик кадрирует фото вокруг этой точки.
 *
 * Значение хранится как объект: { "path": "…", "x": 50, "y": 50 }, где x и y —
 * положение точки в процентах от исходного фото (50/50 — центр).
 * Старый формат (просто строка-путь) тоже читается; при первом изменении
 * значение конвертируется в объект с точкой фокуса в центре.
 */
(function () {
  var React = window.CMS && window.CMS.React;
  var html = window.html;

  if (!React || !html) {
    console.error('Sveltia CMS: не найден window.CMS.React или window.html — поле «фото с фокусом» не зарегистрировано');
    return;
  }

  var clamp = function (n, min, max) { return Math.min(Math.max(n, min), max); };

  /* Старое значение (строка) приводим к объекту с центром в качестве фокуса */
  var normalize = function (value) {
    if (typeof value === 'string') { return { path: value, x: 50, y: 50 }; }
    if (value && typeof value === 'object' && value.path) {
      return { path: value.path, x: value.x == null ? 50 : value.x, y: value.y == null ? 50 : value.y };
    }
    return null;
  };

  var FocalControl = function (props) {
    var value = normalize(props.value);
    var path = value ? value.path : '';
    var x = value ? clamp(value.x, 0, 100) : 50;
    var y = value ? clamp(value.y, 0, 100) : 50;

    var asset = path && props.getAsset ? props.getAsset(path) : null;
    var src = asset && asset.url ? asset.url : path;

    /* Клик по полному превью: позиция клика = точка фокуса в процентах */
    var onPickFocus = function (event) {
      var rect = event.currentTarget.getBoundingClientRect();
      var nx = clamp(Math.round(((event.clientX - rect.left) / rect.width) * 100), 0, 100);
      var ny = clamp(Math.round(((event.clientY - rect.top) / rect.height) * 100), 0, 100);
      props.onChange({ path: path, x: nx, y: ny });
    };

    var pick = function () {
      props.pickFile({ kind: 'image' }).then(function (picked) {
        if (picked) { props.onChange({ path: picked.value, x: 50, y: 50 }); }
      }).catch(function () {});
    };

    var clear = function () { props.onChange(null); };

    var box = {
      position: 'relative',
      maxHeight: '280px',
      border: '1px solid rgba(255,255,255,.25)',
      borderRadius: '8px',
      overflow: 'hidden',
      background: '#141414',
      cursor: 'crosshair',
      display: 'flex',
      justifyContent: 'center',
    };

    var marker = {
      position: 'absolute',
      left: x + '%',
      top: y + '%',
      transform: 'translate(-50%, -50%)',
      width: '20px',
      height: '20px',
      border: '2px solid #00d9ff',
      borderRadius: '50%',
      boxShadow: '0 0 0 1px rgba(0,0,0,.8)',
      pointerEvents: 'none',
    };

    var button = {
      padding: '6px 14px',
      border: '1px solid rgba(255,255,255,.3)',
      borderRadius: '999px',
      background: 'transparent',
      color: 'inherit',
      fontSize: '13px',
      cursor: 'pointer',
    };

    return html`
      <div class=${props.classNameWrapper} style=${{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        <div
          style=${box}
          title="Кликни, чтобы поставить точку фокуса"
          onClick=${path ? onPickFocus : pick}
        >
          ${src
            ? html`<img
                src=${src}
                style=${{ maxWidth: '100%', maxHeight: '280px', width: 'auto', height: 'auto', objectFit: 'contain', userSelect: 'none', pointerEvents: 'none' }}
                draggable="false"
                alt=""
              />`
            : html`<div style=${{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '120px', color: '#999' }}>Нажми, чтобы выбрать фото</div>`}
          ${src ? html`<div style=${marker}></div>` : null}
        </div>
        <div style=${{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div
            style=${{
              flex: 'none',
              width: '96px',
              aspectRatio: '4/3',
              border: '1px solid rgba(255,255,255,.25)',
              borderRadius: '6px',
              overflow: 'hidden',
              background: '#141414',
            }}
            title="Так кадр выглядит на карточке"
          >
            ${src
              ? html`<img
                  src=${src}
                  style=${{ width: '100%', height: '100%', objectFit: 'cover', objectPosition: x + '% ' + y + '%', pointerEvents: 'none' }}
                  draggable="false"
                  alt=""
                />`
              : null}
          </div>
          <button type="button" onClick=${pick} style=${button}>${path ? 'Заменить фото' : 'Выбрать фото'}</button>
          ${path ? html`<button type="button" onClick=${clear} style=${button}>Убрать</button>` : null}
        </div>
        <p style=${{ margin: '0', fontSize: '12px', opacity: '.7', lineHeight: 1.4 }}>
          Кликни по большому фото — перекрестие задаёт видимую область; маленький кадр показывает, что будет на карточке.
        </p>
      </div>
    `;
  };

  CMS.registerFieldType({
    name: 'imageFocal',
    controlComponent: FocalControl,
  });
})();
