/* Поле «фото с точкой фокуса и увеличением» для Sveltia CMS.
 *
 * Как пользоваться: выбрать файл кнопкой ниже, затем кликнуть по большому превью —
 * там поставится точка фокуса (кружок), ползунком «Увеличение» приблизить фото.
 * Голубая рамка на большом фото и кадр 4:3 под ним показывают, что окажется
 * на карточке. Сборщик (focal_derive в src/build.py) вырезает ровно эту область.
 *
 * Значение хранится как объект: { "path": "…", "x": 50, "y": 50, "zoom": 1 }, где x и y —
 * положение точки в процентах от исходного фото (50/50 — центр), zoom — увеличение
 * (1 — без увеличения, 2 — видна половина ширины фото, максимум 4).
 * Старые форматы (строка-путь или объект без zoom) тоже читаются.
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
    if (typeof value === 'string') { return { path: value, x: 50, y: 50, zoom: 1 }; }
    if (value && typeof value === 'object' && value.path) {
      return { path: value.path, x: value.x == null ? 50 : value.x, y: value.y == null ? 50 : value.y, zoom: Number(value.zoom) || 1 };
    }
    return null;
  };

  var FocalControl = function (props) {
    var value = normalize(props.value);
    var path = value ? value.path : '';
    var x = value ? clamp(value.x, 0, 100) : 50;
    var y = value ? clamp(value.y, 0, 100) : 50;
    var zoom = value ? clamp(value.zoom, 1, 4) : 1;

    /* Размер исходного фото в пикселях — нужен, чтобы показать кадр точно как у сборщика */
    var sizeState = React.useState(null);
    var size = sizeState[0];
    var onImgLoad = function (event) {
      var img = event.currentTarget;
      if (img.naturalWidth && (!size || size.src !== img.src)) {
        sizeState[1]({ src: img.src, w: img.naturalWidth, h: img.naturalHeight });
      }
    };

    /* Видимая область в долях фото — та же формула, что в focal_derive (src/build.py) */
    var RATIO = 4 / 3;
    var crop = null;
    if (size) {
      var cw = Math.min(size.w, size.h * RATIO) / zoom;
      var ch = cw / RATIO;
      var left = clamp(x / 100 * size.w - cw / 2, 0, size.w - cw);
      var top = clamp(y / 100 * size.h - ch / 2, 0, size.h - ch);
      crop = { l: left / size.w, t: top / size.h, w: cw / size.w, h: ch / size.h };
    }

    var asset = path && props.getAsset ? props.getAsset(path) : null;
    var src = asset && asset.url ? asset.url : path;

    /* Клик по полному превью: позиция клика = точка фокуса в процентах */
    var onPickFocus = function (event) {
      var rect = event.currentTarget.getBoundingClientRect();
      var nx = clamp(Math.round(((event.clientX - rect.left) / rect.width) * 100), 0, 100);
      var ny = clamp(Math.round(((event.clientY - rect.top) / rect.height) * 100), 0, 100);
      props.onChange({ path: path, x: nx, y: ny, zoom: zoom });
    };

    var pick = function () {
      props.pickFile({ kind: 'image' }).then(function (picked) {
        if (picked) { props.onChange({ path: picked.value, x: 50, y: 50, zoom: 1 }); }
      }).catch(function () {});
    };

    var clear = function () { props.onChange(null); };

    var setZoom = function (z) {
      props.onChange({ path: path, x: x, y: y, zoom: Math.round(clamp(z, 1, 4) * 10) / 10 });
    };
    var onZoomInput = function (event) { setZoom(parseFloat(event.currentTarget.value)); };

    /* Рамка видимой области на большом фото; всё вокруг затемнено */
    var frame = crop ? {
      position: 'absolute',
      left: crop.l * 100 + '%',
      top: crop.t * 100 + '%',
      width: crop.w * 100 + '%',
      height: crop.h * 100 + '%',
      border: '2px solid #00d9ff',
      boxShadow: '0 0 0 9999px rgba(0,0,0,.55)',
      boxSizing: 'border-box',
      pointerEvents: 'none',
    } : null;

    /* Кадр «как на карточке»: фото растянуто и сдвинуто так, чтобы в окне осталась видимая область */
    var previewImg = crop ? {
      position: 'absolute',
      width: 100 / crop.w + '%',
      height: 100 / crop.h + '%',
      left: -crop.l / crop.w * 100 + '%',
      top: -crop.t / crop.h * 100 + '%',
      maxWidth: 'none',
      pointerEvents: 'none',
    } : { width: '100%', height: '100%', objectFit: 'cover', objectPosition: x + '% ' + y + '%', pointerEvents: 'none' };

    var box = {
      position: 'relative',
      maxHeight: '360px',
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
          onClick=${path ? null : pick}
        >
          ${src
            ? html`<div style=${{ position: 'relative', display: 'inline-block', lineHeight: 0, overflow: 'hidden' }} onClick=${onPickFocus}>
                <img
                  src=${src}
                  onLoad=${onImgLoad}
                  style=${{ display: 'block', maxWidth: '100%', maxHeight: '360px', width: 'auto', height: 'auto', userSelect: 'none', pointerEvents: 'none' }}
                  draggable="false"
                  alt=""
                />
                ${frame ? html`<div style=${frame}></div>` : null}
                <div style=${marker}></div>
              </div>`
            : html`<div style=${{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '120px', width: '100%', color: '#999' }}>Нажми, чтобы выбрать фото</div>`}
        </div>
        ${path
          ? html`<label style=${{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '13px' }}>
              <span style=${{ flex: 'none' }}>Увеличение</span>
              <button type="button" onClick=${function () { setZoom(zoom - 0.1); }} style=${button} title="Отдалить">−</button>
              <input type="range" min="1" max="4" step="0.1" value=${zoom} onInput=${onZoomInput} onChange=${onZoomInput} style=${{ flex: '1', minWidth: '80px' }} />
              <button type="button" onClick=${function () { setZoom(zoom + 0.1); }} style=${button} title="Приблизить">+</button>
              <span style=${{ flex: 'none', width: '3em', textAlign: 'right', fontVariantNumeric: 'tabular-nums' }}>×${zoom.toFixed(1)}</span>
            </label>`
          : null}
        <div style=${{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div
            style=${{
              flex: 'none',
              width: '200px',
              aspectRatio: '4/3',
              border: '1px solid rgba(255,255,255,.25)',
              borderRadius: '6px',
              overflow: 'hidden',
              position: 'relative',
              background: '#141414',
            }}
            title="Так кадр выглядит на карточке"
          >
            ${src
              ? html`<img
                  src=${src}
                  style=${previewImg}
                  draggable="false"
                  alt=""
                />`
              : null}
          </div>
          <button type="button" onClick=${pick} style=${button}>${path ? 'Заменить фото' : 'Выбрать фото'}</button>
          ${path ? html`<button type="button" onClick=${clear} style=${button}>Убрать</button>` : null}
        </div>
        <p style=${{ margin: '0', fontSize: '12px', opacity: '.7', lineHeight: 1.4 }}>
          Кликни по большому фото — туда встанет центр кадра. Ползунок «Увеличение» приближает фото. Голубая рамка и кадр снизу показывают, что будет на карточке.
        </p>
      </div>
    `;
  };

  CMS.registerFieldType({
    name: 'imageFocal',
    controlComponent: FocalControl,
  });
})();
