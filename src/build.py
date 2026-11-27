# Сборка сайта: python3 src/build.py
# Собирает index.html и страницы сборок из исходников в src/ (стили и иконки встраиваются в HTML).
# Быстрая сборка только тестовой страницы: python3 src/build.py --test-only
# (секунды вместо ~10 минут: не трогает страницы сборок, sitemap и нарезку фото).
import os,re,sys
TEST_ONLY='--test-only' in sys.argv
SRC=os.path.dirname(os.path.abspath(__file__))
ROOT=os.path.dirname(SRC)
os.chdir(SRC)
A='icons/'
def svg(name, attrs, folder=None):
    s=open((folder or A)+name,encoding='utf-8').read()
    s=re.sub(r'<\?xml[^>]*\?>\s*','',s).strip()
    s=re.sub(r'<metadata>.*?</metadata>','',s)
    s=re.sub(r'></(path|rect|circle|stop)>','/>',s)
    s=re.sub(r'<svg ', '<svg '+attrs+' ', s, count=1)
    return s
logo_icon=svg('logo-icon.svg','class="logo__icon" aria-hidden="true"')
logo_word=svg('logo2.svg','class="logo__word" aria-hidden="true"')
max_svg=svg('MAX.svg','width="35" height="35" aria-hidden="true"').replace('id="a"','id="mx-a"').replace('id="b"','id="mx-b"').replace('id="c"','id="mx-c"').replace('id="d"','id="mx-d"').replace('href="#a"','href="#mx-a"').replace('href="#b"','href="#mx-b"').replace('url(#c)','url(#mx-c)').replace('url(#d)','url(#mx-d)')
vk_svg=re.sub(r' width="800px" height="800px"','',svg('vk-v2-svgrepo-com.svg','width="35" height="35" aria-hidden="true"'))
tg_svg='<svg width="35" height="35" viewBox="0 0 100 100" aria-hidden="true"><circle cx="50" cy="50" r="46" fill="#fff"/><path fill="#29a9eb" fill-rule="evenodd" d="M50 100c27.614 0 50-22.386 50-50S77.614 0 50 0 0 22.386 0 50s22.386 50 50 50Zm21.977-68.056c.386-4.38-4.24-2.576-4.24-2.576-3.415 1.414-6.937 2.85-10.497 4.302-11.04 4.503-22.444 9.155-32.159 13.734-5.268 1.932-2.184 3.864-2.184 3.864l8.351 2.577c3.855 1.16 5.91-.129 5.91-.129l17.988-12.238c6.424-4.38 4.882-.773 3.34.773l-13.49 12.882c-2.056 1.804-1.028 3.35-.129 4.123 2.55 2.249 8.82 6.364 11.557 8.16.712.467 1.185.778 1.292.858.642.515 4.111 2.834 6.424 2.319 2.313-.516 2.57-3.479 2.57-3.479l3.083-20.226c.462-3.511.993-6.886 1.417-9.582.4-2.546.705-4.485.767-5.362Z"/></svg>'

# ---------- контент сайта из content/*.json: правится в админке /admin ----------
import json as _json
def load_content(name,default):
    try:
        return _json.load(open(os.path.join(ROOT,'content',name),encoding='utf-8'))
    except FileNotFoundError:
        return default
S=load_content('settings.json',{})            # контакты, соцсети, цифры рейтинга
H=load_content('home.json',{})                # тексты главной
P=load_content('perks.json',{}).get('perks') or []  # блок «Наши преимущества»
F=load_content('faq.json',{})                 # вопросы и ответы (управляется в админке)
_codes=load_content('codes.json',{})          # коды счётчиков для всех страниц

def inject_code(html):
    """Вставляет коды из CMS: head_code — перед </head>, body_code — перед </body>.
    Значение может быть строкой или объектом {code, lang} (так сохраняет виджет кода)."""
    def text(v):
        if isinstance(v,dict): v=v.get('code') or ''
        return (v or '').strip()
    head=text(_codes.get('head_code'))
    body=text(_codes.get('body_code'))
    if head: html=html.replace('</head>',head+'\n</head>')
    if body: html=html.replace('</body>',body+'\n</body>')
    return html

_css=open('page.css',encoding='utf-8').read()
_body=open('page.body.html',encoding='utf-8').read()
_js=open('page.js',encoding='utf-8').read()
_inner_css=open('inner.css',encoding='utf-8').read()
_inner_js=open('inner.js',encoding='utf-8').read()
_v1_css=open('v1.css',encoding='utf-8').read()
_v1_body=open('v1.body.html',encoding='utf-8').read()

# ---------- внешние файлы стилей и скриптов ----------
# Раньше CSS/JS вшивались в каждую страницу (25–43 КБ на страницу). Теперь они
# лежат в assets/ отдельными файлами: браузер скачивает их один раз и кэширует
# при переходах между страницами. Метка времени в адресе (?v=...) сбрасывает
# кэш после каждой сборки — посетители всегда видят свежие стили.
import time,shutil
_STAMP=time.strftime('%Y%m%d%H%M')
_V1_FONTS=('InterDisplay-Light.woff2','InterDisplay-Regular.woff2','InterDisplay-Medium.woff2',
           'InterDisplay-SemiBold.woff2','InterDisplay-Bold.woff2','orbitron-bold.ttf')
def _copy_v1_assets():
    """Шрифты и фото тестовой страницы v1 лежат в исходниках, в assets их кладёт сборка."""
    for _fn in _V1_FONTS:
        shutil.copy2(os.path.join(SRC,'fonts',_fn),os.path.join(ROOT,'assets',_fn))
    shutil.copy2(os.path.join(ROOT,'content','photos','v1','v1_1.webp'),
                 os.path.join(ROOT,'assets','v1-hero.webp'))
_inner_css_full=(':root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}\n'
                 'img{max-width:100%}\n'+_css+_inner_css)
def _menu_js_part():
    return '(function () {\n'+_js[_js.index('  var menu ='):]

# ---------- карточки «Популярных конфигураций» из content/cards.json ----------
_cards=load_content('cards.json',{}).get('cards') or []

# бейджи-фильтры по процессору (AMD/INTEL) над карточками на главной.
# ВНИМАНИЕ: пока выключены по решению владельца (17.11.2026) — «продолжу с ним работать».
# Чтобы вернуть фильтр, поставьте _FILTERS_ON=True и пересоберите сайт.
_FILTERS_ON=False

# ---------- карточки «Компьютеров в наличии» из content/stock.json ----------
# Ползунок «Скрыть блок» (hidden) в админке прячет весь блок на главной.
_STK=load_content('stock.json',{})
_stk_cards=_STK.get('cards') or []

# ---------- страницы сборок: по одной на каждый файл в content/builds/ ----------
# Данные (название, цена, фото, видео, комплектующие) правятся в админке /admin или прямо в JSON.
# Фото лежат в content/photos/ в исходном виде; нужные размеры AVIF/WebP сборщик нарезает сам в assets/.
import json,glob,html

# ---------- контроль дублей в «Базе железа» ----------
# Владелец может случайно добавить модель, которая уже есть (Sveltia при этом
# молча создаёт файл с «-1» в имени). Сайт это переживает (значения — обычные
# строки), но в админке модели будут повторяться — сообщаем в лог сборки.
_hw={}
for _hf in glob.glob(os.path.join(ROOT,'content','hardware','*.json')):
    try:
        _hd=json.load(open(_hf,encoding='utf-8'))
    except Exception:
        continue
    _hm=(_hd.get('model') or '').strip().lower()
    if _hm:
        _hw.setdefault(_hm,[]).append(os.path.basename(_hf))
_hw_dupes={m:files for m,files in _hw.items() if len(files)>1}
if _hw_dupes:
    print('ВНИМАНИЕ: в «Базе железа» дубли моделей — на сайте всё работает, но модели повторяются в админке:')
    for _hm,_hfiles in _hw_dupes.items():
        print('  «'+_hm.upper()+'»:', ', '.join(_hfiles))
    print('  Оставьте один файл, лишние удалите (в админке или на GitHub).')
from PIL import Image,ImageOps

# ---------- очередь кодирования фото ----------
# Кодирование AVIF медленное (~10-40 сек на крупный кадр). Все кадры нарезки
# ставятся в очередь, а кодируются пулом потоков в конце сборки — быстрее в ~4 раза.
import concurrent.futures as _fut
_enc_jobs=[]
def _enc(fn,*a):
    _enc_jobs.append((fn,a))
def _encode_width(path,base,w,ratio):
    """Кадр `w` по центру исходника: WebP 95 + AVIF 80."""
    im=ImageOps.exif_transpose(Image.open(path)).convert('RGB')
    t=ImageOps.fit(im,(w,round(w/ratio)),Image.LANCZOS)
    t.save(_asset_path(base,f'-{w}.webp'),quality=95,method=6)
    t.save(_asset_path(base,f'-{w}.avif'),quality=80)
def _encode_crop(crop,base,w,ratio):
    """Кадр `w` из уже вырезанной области (по точке фокуса)."""
    t=crop.resize((w,round(w/ratio)),Image.LANCZOS)
    t.save(_asset_path(base,f'-{w}.webp'),quality=95,method=6)
    t.save(_asset_path(base,f'-{w}.avif'),quality=80)
def _run_enc_queue():
    """Кодирует всё, что накопилось в очереди, пулом потоков."""
    if not _enc_jobs:
        return
    n=len(_enc_jobs)
    t0=time.time()
    with _fut.ThreadPoolExecutor(max_workers=min(8,n)) as pool:
        futures=[pool.submit(fn,*a) for fn,a in _enc_jobs]
        for f in futures: f.result()
    _enc_jobs.clear()
    print('нарезка фото:',n,'кадров за',round(time.time()-t0,1),'сек')

def esc(x): return html.escape(str(x or '').strip(),quote=True)
def typo(x):
    """Неразрывные пробелы после коротких предлогов и перед знаком рубля — чтобы строки не рвались некрасиво."""
    x=re.sub(r'(?<![\w-])(в|на|и|с|к|о|у|а|за|из|по|от|до|для|или|не|но|под|при)\s+',lambda m:m.group(1)+'&nbsp;',x,flags=re.I)
    x=re.sub(r'\s+(—|₽)',r'&nbsp;\1',x)
    return x
def txt(x): return typo(esc(x))
def money(n): return f'{int(n):,}'.replace(',','&nbsp;')+'&nbsp;₽'

# бейджи-фильтры по процессору (AMD/INTEL) над карточками на главной:
# показываются, только если у сборок встречается больше одного бренда
_brands=[]
for _c in _cards:
    _sp=_c.get('specs')
    _cpu=(_sp.get('cpu') if isinstance(_sp,dict) else '') or ''
    _b=_cpu.split()[0].upper() if _cpu else ''
    if _b and _b not in _brands: _brands.append(_b)
_cpu_filters=('' if not _FILTERS_ON or len(_brands)<2 else
    '<div class="filters" id="cpu-filters" aria-label="Фильтр по процессору">'
    +''.join(f'<button class="filters__btn" type="button" data-cpu="{esc(b)}" aria-pressed="false">{esc(b)}</button>' for b in _brands)
    +'</div>')
def money_tr(n):
    """Цена в тысячах рублей, как на старом сайте: 348 т.р."""
    t=n/1000
    s=f'{t:.0f}' if abs(t-round(t))<0.05 else f'{t:.1f}'.replace('.',',')
    return s+'&nbsp;т.р.'

def asset_base(src):
    """Путь производного файла внутри assets/ (без расширения и суффикса размера), с подпапками как в CMS.
    content/photos/golden/1.webp -> golden/1, content/photos/cards/foo.webp -> cards/foo."""
    rel=src.lstrip('/').replace('\\','/')
    for p in ('content/photos/','content\\photos\\'):
        if rel.startswith(p): rel=rel[len(p):]
    return os.path.splitext(rel)[0]


def _asset_path(base, suffix):
    """Полный путь на диске для производного файла; создаёт подпапку при необходимости."""
    path=os.path.join(ROOT,'assets',base.replace('/',os.sep)+suffix)
    os.makedirs(os.path.dirname(path),exist_ok=True)
    return path

def derive(src,widths,ratio):
    """Нарезает фото под нужные ширины (обрезка по центру до ratio=ширина/высота). Возвращает (базовый путь в assets, [ширины])."""
    path=os.path.join(ROOT,src.lstrip('/'))
    base=asset_base(src)
    with Image.open(path) as im:
        W,H=ImageOps.exif_transpose(im).size
    W=min(W,int(H*ratio))  # ширина после обрезки
    ws=[w for w in widths if w<=W] or [widths[0]]
    todo=[w for w in ws if not all(os.path.exists(os.path.join(ROOT,'assets',base.replace('/',os.sep)+f'-{w}.{e}')) for e in ('avif','webp'))]
    for w in todo:
        _enc(_encode_width,path,base,w,ratio)
    return base,ws

def focal_derive(src,widths,ratio,focal,zoom=1):
    """Обрезка фото вокруг фокусной точки. focal=(x,y) — проценты исходного фото (50/50 — центр).
    zoom — увеличение (1 — без увеличения, 2 — видна половина ширины, максимум 4); то же считает admin/custom-fields.js.
    Имя файла включает точку фокуса и увеличение: сменишь фокус в админке — сменится и файл, кэш не помешает.
    Кадры пересоздаются при каждой сборке, потому что результат зависит от данных."""
    path=os.path.join(ROOT,src.lstrip('/'))
    X=int(round(max(0,min(100,focal[0]))))
    Y=int(round(max(0,min(100,focal[1]))))
    try: Z=max(1.0,min(4.0,float(zoom or 1)))
    except (TypeError,ValueError): Z=1.0
    base=asset_base(src)+f'-f{X}x{Y}'+(f'z{round(Z*10)}' if Z>1 else '')
    with Image.open(path) as im:
        W,H=ImageOps.exif_transpose(im).size
    cw=round(min(W,int(H*ratio))/Z)  # ширина рамки кадрирования
    ch=round(cw/ratio)               # высота рамки кадрирования
    left=min(max(round(X/100*W-cw/2),0),W-cw)   # верхний левый угол кадра (внутри
    top=min(max(round(Y/100*H-ch/2),0),H-ch)
    ws=[w for w in widths if w<=cw] or [widths[0]]
    crop=ImageOps.exif_transpose(Image.open(path)).convert('RGB').crop((left,top,left+cw,top+ch))
    for w in ws:
        _enc(_encode_crop,crop,base,w,ratio)
    return base,ws

def card_image(c):
    """Картинка карточки: либо строка-путь (центральная обрезка), либо объект {path,x,y,zoom} (обрезка по фокусу с увеличением)."""
    img=c.get('image')
    if isinstance(img,dict):
        return focal_derive(img.get('path',''),[480,960],4/3,(img.get('x',50) or 50,img.get('y',50) or 50),img.get('zoom',1))
    return derive(img or '',[480,960],4/3)

def og_image(src):
    path=os.path.join(ROOT,src.lstrip('/'))
    base=asset_base(src)
    rel=f'assets/{base}-og.jpg'
    out=os.path.join(ROOT,rel.replace('/',os.sep))
    if not os.path.exists(out):
        os.makedirs(os.path.dirname(out),exist_ok=True)
        ImageOps.fit(ImageOps.exif_transpose(Image.open(path)).convert('RGB'),(1200,630),Image.LANCZOS).save(out,quality=82,optimize=True,progressive=True)
    return rel
def srcset(stem,ws,ext): return ', '.join(f'assets/{stem}-{w}.{ext} {w}w' for w in ws)

# ---------- контакты, соцсети и преимущества: из content/settings.json и perks.json ----------
_soc=(S.get('socials') or {})
_social_defs=[('max',max_svg,'Написать в MAX'),('telegram',tg_svg,'Написать в Telegram'),('vk',vk_svg,'Группа ВКонтакте')]
socials='\n'.join(f'<a class="social" href="{esc(_soc.get(k,""))}" target="_blank" rel="noopener" aria-label="{label}">{ic}</a>'
                  for k,ic,label in _social_defs if _soc.get(k))

# ---------- футер: блок «Отзывы» ----------
# Рейтинг организации в Яндексе (виден в блоке отзывов; та же оценка уходит в разметку магазина)
_YA_SCORE='5.0'    # оценка по 5-балльной шкале
_YA_REVIEWS=120    # число отзывов (в блоке показывается как «120+»)
_reviews=[
 ('Женя Мележик','24.06.2026','Заказывали два компа с одинаковой сборкой ко дням рождения. Всё супер – сделали и красиво, и быстро, и качественно и очень выгодно по цене. Всем большое спасибо за вашу проделанную работу и, безусловно, доставку и подключение💥💥💥','ava-1.webp'),
 ('Виктория Трофимова','14.06.2026','Сегодня приобрела компьютер сыну, и хочу поделиться своим восторгом от покупки и процесса доставки! Во-первых, сам компьютер превзошел все мои ожидания. Он работает быстро и без сбоев, все программы открываются...','ava-4.webp'),
 ('Евгений А.','10.02.2026','Заказал компьютер, всё сделали быстро и качественно! Собрали отличную конфигурацию! Привезли как мне было удобно, подключили, объяснили! Ребята молодцы. Доставлял и подключал Игорь, ему отдельный респект! Советую всем! Цены ниже чем в DNS и у других...','ava-5.webp'),
 ('Александр Михайлов','15.02.2026','Спасибо большое команде star-comp. Ребята делают на уровне и качественно Специалисты отзывчевы и оперативны Только заказал и вечром уже стоял в работе Все супер! Еще раз спасибо огромное я доволен работе star-corm 🤝🤝🤝🤝','ava-3.webp'),
 ('Эдуард Дроздов','31.01.2026','Заказал игровой компьютер с монитором для внуков, оптимально скомплектовали, разъяснили. Доставили по адресу в удобное для меня время, настроили. Компетентно, в разумной достаточности по характеристикам и цене. Итог, выше ожиданий.','ava-2.webp'),
]
_quote='<svg class="tf-quote" viewBox="0 0 28 16" aria-hidden="true"><path d="M0 16V9.6C0 4.3 3.2 1 8.9 0l1.2 2.6C6.9 3.7 5.3 5.5 5 8h4.4v8H0Zm18.6 0V9.6c0-5.3 3.2-8.6 8.9-9.6l1.2 2.6c-3.2 1.1-4.8 2.9-5.1 5.4H28v8h-9.4Z" fill="#00d9ff"/></svg>'
_reviews_cards=''
for _n,_r in enumerate(_reviews):
    _name,_date,_text,_ava=_r
    _reviews_cards+=f"""        <article class="tf-review2">
          <p class="tf-review2__text">{esc(_text)}</p>
          <div class="tf-review2__meta">
            <img class="tf-avatar" src="assets/footer/{_ava}" alt="Аватар: {esc(_name)}" loading="lazy" decoding="async">
            <div class="tf-review2__who"><b>{esc(_name)}</b><span>{esc(_date)}</span></div>
            {_quote}
          </div>
        </article>"""
REVIEWS_HTML=f'''  <section class="tf-section tf-reviews" id="otzivy" aria-label="Отзывы">
    <h2 class="tf-title">Доверие, подтверждённое отзывами</h2>
    <p class="tf-lead">Каждый компьютер собирается с вниманием к деталям, а лучшая оценка нашей работы — рекомендации и отзывы клиентов.</p>
    <div class="tf-reviews__grid">
{_reviews_cards}
        <div class="tf-ya-cell">
          <div class="tf-ya-card">
            <div class="tf-ya-top">
              <span class="tf-ya-ya">Я</span>
              <svg class="tf-ya-star" viewBox="0 0 35 35" aria-hidden="true"><path d="M17.5 1l4.4 11.4 12.6.5-10 8 3.4 12.1-10.4-6.6L7.1 33l3.4-12.1-10-8 12.6-.5z" fill="#ffc61b"/></svg>
              <b class="tf-ya-score">{_YA_SCORE}</b><span class="tf-ya-of">/5</span>
            </div>
            <div class="tf-ya-strip">Рейтинг организации в Яндексе</div>
          </div>
          <a class="tf-ya-btn" href="https://yandex.ru/maps/org/star_comp/101485963947/reviews/" target="_blank" rel="noopener">Смотреть на Яндекс</a>
          <span class="tf-ya-badge status-pill status-pill--stock">{_YA_REVIEWS}+ отзывов</span>
        </div>
    </div>
  </section>'''

# ---------- блок FAQ: стоит в футере сразу перед контактами ----------
# Раньше жил в page.body.html между «Наличием» и «7 причинами». Теперь это отдельный
# фрагмент, который вставляется в FOOTER после отзывов. На страницах сборок
# (inner-страницы) блок не показываем — там свой набор секций.
# Заголовок, текст кнопки и все вопросы берутся из content/faq.json (правятся в админке).
_faq_items=F.get('items') or []
_faq_title=txt(F.get('title') or 'Остались вопросы?')
_faq_accent=txt(F.get('title_accent') or '')
_faq_heading=(' '.join(x for x in [_faq_title,_faq_accent] if x))
_faq_lead=txt(F.get('lead') or 'Ответим на то, что чаще всего спрашивают перед заказом. Если вашего вопроса здесь нет — напишите нам.')
_faq_btn=txt(F.get('button') or 'Написать нам')
_faq_schedule='{{SCHEDULE}}'   # подставится из «Настроек сайта» ниже, в fill_text()

def _faq_answer_html(s):
    """Один абзац, а если в ответе есть пустая строка — несколько."""
    parts=[p.strip() for p in re.split(r'\n\s*\n', str(s or '')) if p.strip()]
    if not parts: parts=[str(s or '')]
    return ''.join('<p>'+txt(p)+'</p>' for p in parts)

_faq_rows=[]
for _it in _faq_items:
    if not isinstance(_it,dict): continue
    _q=txt(_it.get('question') or '')
    if not _q: continue
    _a=_faq_answer_html(_it.get('answer') or '')
    _i=len(_faq_rows)+1
    _faq_rows.append(f'''        <div class="faq__item">
          <button class="faq__q" type="button" aria-expanded="false" aria-controls="faq-a{_i}">{_q}<span class="faq__plus" aria-hidden="true"></span></button>
          <div class="faq__a" id="faq-a{_i}">{_a}</div>
        </div>''')

# Если вопросы все удалили — блока на сайте не будет
FAQ_SECTION='' if not _faq_rows else f'''    <section class="tf-section faq" id="faq" aria-labelledby="faq-title">
      <div class="faq__side">
        <h2 class="section__title" id="faq-title">{_faq_heading}</h2>
        <p class="faq__lead">{_faq_lead}</p>
      </div>
      <div class="faq__list">
{chr(10).join(_faq_rows)}
      </div>
    </section>
'''

# ---------- футер: блок «Контакты» из content/contacts.json ----------
C=load_content('contacts.json',{})
_tf_ph=[(p.get('image') if isinstance(p,dict) else p) for p in (C.get('photos') or [])]
# путь делаем относительным: сайт может жить в подпапке (GitHub Pages), абсолютный /content/... отвалится
_tf_ph=[str(p).strip().lstrip('/') for p in _tf_ph if p and str(p).strip()]
_tf_cells=''
for _n in range(3):
    if _n<len(_tf_ph):
        # фото нарезается как все: маленькая ячейка не должна тянуть 300КБ оригинал
        _stem,_ws=derive(_tf_ph[_n],[240,480],9/16)
        _src=f'assets/{_stem}-{_ws[-1]}.webp'
        _tf_cells+=f'\n            <img src="{esc(_src)}" alt="Фото мастерской STAR-COMP" loading="lazy" decoding="async">'
    else:
        _tf_cells+='\n            <div class="tf-ph" aria-hidden="true"></div>'
_tf_embed=(C.get('map_embed') or '').strip()
_tf_map=f'<iframe src="{esc(_tf_embed)}" title="Карта: как нас найти" loading="lazy"></iframe>' if _tf_embed else '<div class="tf-map-ph" aria-hidden="true"></div>'
_tf_social=''
for _k,_f,_l in [('telegram','tg-white.svg','Написать в Telegram'),('vk','vk-white.svg','Группа ВКонтакте'),('max','max-white.svg','Написать в MAX')]:
    _href=_soc.get(_k)
    if _href:
        _tf_social+=f'<a href="{esc(_href)}" target="_blank" rel="noopener" aria-label="{_l}"><img src="assets/footer/{_f}" alt="" loading="lazy" decoding="async"></a>'
# белые монохромные иконки (как в футере) — для меню
_social_white_defs=[('max','max-white.svg','Написать в MAX'),('telegram','tg-white.svg','Написать в Telegram'),('vk','vk-white.svg','Группа ВКонтакте')]
socials_white='\n'.join(f'<a class="social" href="{esc(_soc.get(k,""))}" target="_blank" rel="noopener" aria-label="{label}"><img src="assets/footer/{f}" alt="" loading="lazy" decoding="async"></a>'
                        for k,f,label in _social_white_defs if _soc.get(k))
_tf_title=txt(C.get('title') or 'Личная консультация там, где удобно вам')
_tf_accent=txt(C.get('title_accent') or '')
_tf_title_full=(' '.join(x for x in [_tf_title,_tf_accent] if x))
_tf_lead=txt(C.get('lead') or 'Проконсультируем по телефону, в мессенджере или при встрече в мастерской.')
FOOTER=f'''<footer class="tfooter">
  <div class="wrap">
    {REVIEWS_HTML}
    {FAQ_SECTION}    <section class="tf-section tf-contacts" id="contakty" aria-label="Контакты">
      <h2 class="tf-title">{_tf_title_full}</h2>
      <p class="tf-lead">{_tf_lead}</p>
      <div class="tf-contacts__grid">
        <div class="tf-photos">
          <p class="tf-label">Фото нашей мастерской:</p>
          <div class="tf-shop__grid">{_tf_cells}
          </div>
        </div>
        <div class="tf-map">{_tf_map}</div>
        <div class="tf-details">
          <p class="tf-label">Адрес:</p>
          <p class="tf-value">{txt(S.get('address_full') or 'г. Санкт-Петербург, Заневский пр. 65 к5, 2 этаж.')}</p>
          <p class="tf-label">Телефон:</p>
          <p class="tf-value"><a href="tel:{esc(S.get('phone_tel') or '+79939845505')}">{txt(S.get('phone_display') or '8 (993) 984-55-05')}</a></p>
          <p class="tf-label">График работы:</p>
          <p class="tf-value">{txt(S.get('schedule') or 'Ежедневно: 11:00–19:00')}</p>
          <p class="tf-label">Почта:</p>
          <p class="tf-value"><a href="mailto:{esc(S.get('email') or 'info@star-comp.ru')}">{esc(S.get('email') or 'info@star-comp.ru')}</a></p>
          <p class="tf-label">Социальные сети:</p>
          <div class="tf-socials">{_tf_social}</div>
        </div>
      </div>
      <div class="tf-bottom">
        <p>2009–2026 © STARCOMP. Все права защищены. Политика обработки данных.</p>
        <p>ИНН: 784200735088 ОГРН: 322784700364590.<br>Вся информация, размещённая на сайте, носит ознакомительный характер.</p>
      </div>
    </section>
  </div>
</footer>'''
FOOTER+='''
<script>
(function () {
  // фото мастерской: клик открывает просмотр на весь экран
  var t = document.querySelector('.tfooter');
  if (!t) return;
  t.addEventListener('click', function (e) {
    var img = e.target.closest('.tf-shop__grid img');
    if (!img) return;
    var box = document.createElement('dialog');
    box.className = 'tf-view';
    var big = document.createElement('img');
    big.src = img.currentSrc || img.src;
    big.alt = img.alt || '';
    var close = document.createElement('button');
    close.className = 'tf-view__close';
    close.type = 'button';
    close.setAttribute('aria-label', 'Закрыть');
    close.textContent = '×';
    box.append(big, close);
    document.body.appendChild(box);
    box.addEventListener('click', function () { box.close(); });
    box.addEventListener('close', function () { box.remove(); });
    box.showModal();
  });
})();
</script>'''

_perk_icons={
 'no-extra':'<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="5" y="5" width="14" height="14" rx="2"/><path d="M9 2v3M15 2v3M9 19v3M15 19v3M2 9h3M2 15h3M19 9h3M19 15h3"/><path d="M9 14l3-3 3 3"/></svg>',
 'warranty':'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3l7 3v5.5c0 4.4-2.9 8-7 9.5-4.1-1.5-7-5.1-7-9.5V6l7-3z"/><path d="M8.8 12.2l2.2 2.2 4.2-4.4"/></svg>',
 'price':'<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="4" y="3" width="16" height="18" rx="2.5"/><path d="M8 8h8M8 12h4M13 16.5l1.8 1.8 3.2-3.6"/></svg>',
}
perks_list='\n'.join(f'''      <li class="perk">
        <h2>{_perk_icons.get(p.get('icon'),_perk_icons['no-extra'])}{txt(p.get('title'))}</h2>
        <p>{txt(p.get('text'))}</p>
      </li>''' for p in P)

_st=S.get('stats') or {}
stats_list='\n'.join(f'        <li><b>{esc(_st.get(k,""))}</b><span>{lbl}</span></li>'
                     for k,lbl in (('rating','Рейтинг'),('reviews','Отзывов'),('experience','Лет опыта')) if _st.get(k))
maps_note=''
if _st.get('maps_url'):
    maps_note=f'{txt(_st.get("maps_note") or "*оценка организации на")} <a href="{esc(_st["maps_url"])}" target="_blank" rel="noopener">Яндекс картах</a>'

def hero_picture():
    """Фото первого экрана: если в настройках задан hero_image — нарезаем его; иначе готовые размеры из assets."""
    sizes='(min-width: 532px) 500px, calc(100vw - 32px)'
    srcimg=(H.get('hero_image') or '').strip()
    alt=esc(H.get('hero_alt') or 'Игровой компьютер STAR-COMP')
    if srcimg:
        stem,ws=derive(srcimg,[600,800,1000],0.8)
        av=', '.join(f'assets/{stem}-{w}.avif {w}w' for w in ws)
        wp=', '.join(f'assets/{stem}-{w}.webp {w}w' for w in ws)
        w0=ws[0]
        return (f'<source type="image/avif" srcset="{av}" sizes="{sizes}">'
                f'<source type="image/webp" srcset="{wp}" sizes="{sizes}">'
                f'<img src="assets/{stem}-{w0}.webp" width="{w0}" height="{round(w0*1.25)}" alt="{alt}" fetchpriority="high" decoding="async">')
    return (f'<source type="image/avif" srcset="assets/hero-600.avif 600w, assets/hero-800.avif 800w, assets/hero-1000.avif 1000w" sizes="{sizes}">'
            f'<source type="image/webp" srcset="assets/hero-600.webp 600w, assets/hero-800.webp 800w, assets/hero-1000.webp 1000w" sizes="{sizes}">'
            f'<img src="assets/hero-600.webp" width="600" height="750" alt="{alt}" fetchpriority="high" decoding="async">')

def _title_html():
    """Заголовок главной: все части одной строкой (без цветного акцента)."""
    parts=[txt(H.get('title_before')), txt(H.get('title_accent')), txt(H.get('title_after'))]
    h1=' '.join(p for p in parts if p)
    return re.sub(r'&nbsp; ',r'&nbsp;',h1)

def _more_hidden():
    """Флаг «спрятать кнопки "Показать ещё"/"Скрыть"»: когда прятать нечего."""
    return ' hidden' if not (len(_cards) > 8 or any(c.get('extra') for c in _cards)) else ''

def _cards_title_html():
    """Заголовок блока конфигураций (без цветного акцента)."""
    parts=[txt(H.get('cards_title') or 'Последние проекты нашей'), txt(H.get('cards_title_accent'))]
    t=' '.join(p for p in parts if p)
    return re.sub(r'&nbsp; ',r'&nbsp;',t)

def _stock_title_html():
    """Заголовок блока «Компьютеры в наличии» (без цветного акцента)."""
    parts=[txt(_STK.get('title') or 'Компьютеры в наличии'), txt(_STK.get('title_accent'))]
    t=' '.join(p for p in parts if p)
    return re.sub(r'&nbsp; ',r'&nbsp;',t)

# ---------- боковое меню из content/menu.json ----------
_menu_links=load_content('menu.json',{}).get('links') or []
def menu_links_html(inner=False):
    """Пункты бокового меню. inner=True — для страниц сборок: якоря ведут на главную."""
    base='index.html' if inner else ''
    out=[]
    for l in _menu_links:
        label=(l.get('label') or '').strip()
        url=(l.get('url') or '').strip()
        if not label or not url: continue
        href=base+url if url.startswith('#') else url
        # На главной «Главная» = плавная прокрутка наверх (scroll-behavior:smooth),
        # а не перезагрузка страницы по index.html.
        if not inner and href=='index.html':
            href='#top'
        out.append(f'    <a href="{esc(href)}">{txt(label)}</a>')
    return '\n'.join(out)

# Подстановки для шапки, меню и главной страницы
FILLS={
 '{{PHONE_TEL}}':esc(S.get('phone_tel') or '+79939845505'),
 '{{PHONE_DISPLAY}}':txt(S.get('phone_display') or '8 (993) 984-55-05'),
 '{{PHONE_NOTE}}':txt(S.get('phone_note') or 'Без выходных, 11:00 до 19:00'),
 '{{MENU_NOTE}}':txt(S.get('menu_note') or 'Пн-Вс, 11:00 до 19:00'),
 '{{EMAIL}}':esc(S.get('email') or 'info@star-comp.ru'),
 '{{ADDRESS}}':txt(S.get('address') or 'Заневский 65к5, ст. м. Ладожская'),
 '{{SCHEDULE}}':txt(S.get('schedule') or 'Ежедневно, 11:00–19:00'),
 '{{STATS_LIST}}':stats_list,
 '{{MAPS_NOTE}}':maps_note,
 '{{PERKS_LIST}}':perks_list,
 '{{BADGE}}':txt(H.get('badge') or 'Профессиональная сборка'),
 '{{TITLE_HTML}}':_title_html(),
 '{{HERO_LEAD}}':txt(H.get('lead') or ''),
 '{{HERO_BUTTON}}':txt(H.get('button') or 'Подобрать компьютер'),
 '{{HERO_CAPTION}}':txt(H.get('hero_caption') or ''),
 '{{HERO_PICTURE}}':hero_picture(),
 '{{CARDS_LEAD}}':txt(H.get('cards_lead') or ''),
 '{{CARDS_TITLE}}':_cards_title_html(),
 '{{LOGO_ICON}}':logo_icon,
 '{{LOGO_WORD}}':logo_word,
 '{{SOCIALS}}':socials,
 '{{SOCIALS_MENU}}':socials.replace('mx-','mxm-'),
 '{{SOCIALS_WHITE}}':socials_white,
 '{{ADDRESS_FULL}}':txt(S.get('address_full') or 'г. Санкт-Петербург, Заневский пр. 65 к5, 2 этаж.'),
 '{{MAPS_URL}}':esc(C.get('maps_url') or 'https://yandex.ru/maps/-/CXbR7LiO'),
}
def fill_text(x):
    for k,v in FILLS.items(): x=x.replace(k,v)
    return x

# Общий футер: на главной и её SEO-клоне показываем FAQ перед контактами,
# на страницах сборок оставляем только отзывы и контакты.
FOOTER_MAIN=fill_text(FOOTER)
FOOTER_INNER=FOOTER.replace(FAQ_SECTION,'')

SIZES='(min-width: 1024px) max(66.6667vw, calc(100svh * 1.3334)), max(100vw, calc(70svh * 1.3334))'
CARD_SIZES='(min-width: 1920px) 24vw, (min-width: 1240px) 380px, (min-width: 1024px) 31vw, (min-width: 608px) 576px, calc(100vw - 32px)'
ARROW_L='<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M10 3 5 8l5 5"/></svg>'
ARROW_R='<svg viewBox="0 0 16 16" aria-hidden="true"><path d="m6 3 5 5-5 5"/></svg>'

def card_cpu(c):
    """Бренд процессора карточки (AMD/INTEL) — для бейджей-фильтров и атрибута data-cpu."""
    sp=c.get('specs')
    cpu=(sp.get('cpu') if isinstance(sp,dict) else '') or ''
    return cpu.split()[0].upper() if cpu else ''

def card_html(c,hidden=False):
    """Одна карточка конфигурации для главной и для блока «Другие конфигурации»."""
    name=esc(c['name'])
    stem,ws=card_image(c)
    w0=ws[0]; h0=round(w0*3/4)
    alt=txt(c.get('alt') or c['name'])
    def card_specs(c):
        sp = c.get('specs')
        rows = []
        if isinstance(sp, dict):
            # новый формат карточек: ровно две строки — процессор и видеокарта
            if sp.get('cpu'): rows.append(('Процессор', sp['cpu']))
            if sp.get('gpu'): rows.append(('Видеокарта', sp['gpu']))
        else:
            for s in sp or []:
                if s.get('label') and s.get('value'): rows.append((s['label'], s['value']))
        return '\n'.join(f'          <div><dt>{esc(l).rstrip(":")}:</dt><dd>{esc(v)}</dd></div>' for l, v in rows)
    specs = card_specs(c)
    href=esc(c.get('page') or '') or '#podbor'
    hidden_cls=' card--extra' if hidden else ''   # метка для «Показать ещё» и фильтра
    hidden_attr=' hidden' if hidden else ''
    _cpu=f' data-cpu="{esc(card_cpu(c))}"' if card_cpu(c) else ''
    return f'''      <li class="card{hidden_cls}"{hidden_attr}{_cpu}>
        <div class="card__media">
          <picture>
            <source type="image/avif" srcset="{srcset(stem,ws,'avif')}" sizes="{CARD_SIZES}">
            <img src="assets/{stem}-{w0}.webp" srcset="{srcset(stem,ws,'webp')}" sizes="{CARD_SIZES}" width="{w0}" height="{h0}" alt="{alt}" loading="lazy" decoding="async">
          </picture>
        </div>
        <div class="card__body">
          <h3 class="card__name"><a href="{href}">{name}</a></h3>
          <dl class="specs">
{specs}
          </dl>
          <div class="card__foot">
            <div class="card__foot-left">
              <p class="card__price"><span>Стоимость:</span><b>{'от&nbsp;' if c.get('show_from') is not False else ''}{money(c['price_from'])}</b></p>
            </div>
            <a class="card__go" href="{href}" aria-label="Открыть страницу: {name}"><svg viewBox="0 0 16 16"><path d="M4 12 12 4M5.5 4H12v6.5"/></svg></a>
          </div>
        </div>
      </li>'''

def cards_html(cards,with_hidden=False):
    """Список карточек; with_hidden включает флаг «показывать только по кнопке "Показать ещё"».
    Правило главной: видно не более 8 карточек (в порядке списка) — остальные под кнопкой."""
    return '\n'.join(card_html(c,(c.get('extra') or i>=8) and with_hidden) for i,c in enumerate(cards))

def other_builds_html(cards):
    """Блок «Другие конфигурации» внизу страниц сборок — из тех же данных, что и главная."""
    items='\n'.join(card_html(c) for c in cards)
    return f'''  <section class="section section--other wrap" aria-labelledby="other-title">
    <h2 class="section__title" id="other-title">Другие конфигурации</h2>
    <p class="section__lead">Соберём под ваш бюджет и задачи</p>
    <!-- Карточки собираются из content/cards.json — того же файла, что и «Популярные конфигурации» на главной -->
    <ul class="cards">
{items}
    </ul>
  </section>'''

def stock_section_html(exclude_slug=None):
    """Блок «Компьютеры в наличии» на главной и внизу страниц сборок — из content/stock.json.
    Показывается только когда в админке выключен ползунок «Скрыть блок» и есть карточки.
    exclude_slug: на странице сборки прячем карточку этой же сборки, чтобы не было
    ссылки на саму себя (зацикливание)."""
    if _STK.get('hidden') or not _stk_cards: return ''
    cards=[c for c in _stk_cards if (c.get('page') or '').replace('.html', '') != (exclude_slug or '')]
    if not cards: return ''
    lead=f'\n    <p class="section__lead">{txt(_STK.get("lead"))}</p>' if _STK.get('lead') else ''
    return f'''  <section class="section wrap" id="v-nalichii" aria-labelledby="stock-title">
    <h2 class="section__title" id="stock-title">{_stock_title_html()}</h2>{lead}
    <!-- Карточки собираются из content/stock.json — страница «Компьютеры в наличии» в админке -->
    <ul class="cards">
{cards_html(cards,False)}
    </ul>
  </section>'''

# ---------- блок «Подарки всем клиентам»: общий для всех страниц ----------
# Экспорт Frame 128. Разметка — src/gifts.body.html, картинки — уже скачанные
# с Тильды promo_1/promo_2, нарезку делает сборщик. Стили — в page.css,
# поэтому блок попадает и на главную, и на страницы сборок (inner.css = page.css + inner.css).
def _promo_picture(stem,ws,h,alt):
    """Картинка подарка: те же AVIF/WebP-нарезки, что и у остальных фото."""
    _sizes='(min-width:64rem) 18rem, 100vw'
    return (f'          <picture>\n'
            f'            <source type="image/avif" srcset="{srcset(stem,ws,"avif")}" sizes="{_sizes}">\n'
            f'            <img src="assets/{stem}-{ws[-1]}.webp" srcset="{srcset(stem,ws,"webp")}" sizes="{_sizes}" width="{ws[-1]}" height="{h}" alt="{alt}" loading="lazy" decoding="async">\n'
            f'          </picture>')

_gift_av_stem,_gift_av_ws=derive('content/photos/promo/promo_2.webp',[480],1)          # Kaspersky, квадрат
_gift_ms_stem,_gift_ms_ws=derive('content/photos/promo/promo_1.webp',[480,960],3/2)    # клавиатура и мышь, 3:2
_gift_antivirus=_promo_picture(_gift_av_stem,_gift_av_ws,480,'Антивирус Kaspersky в подарок — лицензия на 1 год')
_gift_mouse=_promo_picture(_gift_ms_stem,_gift_ms_ws,320,'Клавиатура и мышь в подарок при заказе от 155 000 ₽')
GIFTS_SECTION=(fill_text(open(os.path.join(ROOT,'src','gifts.body.html'),encoding='utf-8').read())
    .replace('{{GIFT_ANTIVIRUS}}',_gift_antivirus)
    .replace('{{GIFT_MOUSE}}',_gift_mouse))

# ---------- главная страница ----------
_street=esc(S.get('street_address') or 'Заневский пр., 65 к5, 2 этаж')
_postal=esc(S.get('postal_code') or '195112')
_geo_lat=S.get('geo_lat') or 59.932551
_geo_lon=S.get('geo_lon') or 30.434457
_price_range=esc(S.get('price_range') or '90000-530000 RUB')
ld=json.dumps({"@context":"https://schema.org","@type":"ComputerStore","name":"STAR-COMP","url":"https://star-comp.ru","image":"https://star-comp.ru/assets/og-home.jpg","telephone":esc(S.get('phone_schema') or '+7-993-984-55-05'),"email":esc(S.get('email') or 'info@star-comp.ru'),"address":{"@type":"PostalAddress","streetAddress":_street,"addressLocality":"Санкт-Петербург","postalCode":_postal,"addressCountry":"RU"},"geo":{"@type":"GeoCoordinates","latitude":_geo_lat,"longitude":_geo_lon},"openingHours":esc(S.get('opening_hours_schema') or 'Mo-Su 11:00-19:00'),"priceRange":_price_range,"sameAs":[v for v in (_soc.get('vk'),_soc.get('telegram')) if v],"aggregateRating":{"@type":"AggregateRating","ratingValue":_YA_SCORE,"bestRating":"5","reviewCount":str(_YA_REVIEWS)}},ensure_ascii=False,separators=(',',':'))
# фото блока «7 причин» (перенос с Тильды): нарезка под десктопную колонку 23rem
_why_stem,_why_ws=derive('content/photos/blocktest/blocktest_1.webp',[480,800],5/8)
_why_photo=(f'      <picture class="why__photo">\n'
            f'        <source type="image/avif" srcset="{srcset(_why_stem,_why_ws,"avif")}" sizes="(min-width:64rem) 23rem, 1px">\n'
            f'        <img src="assets/{_why_stem}-{_why_ws[-1]}.webp" srcset="{srcset(_why_stem,_why_ws,"webp")}" sizes="(min-width:64rem) 23rem, 1px" width="{_why_ws[-1]}" height="{round(_why_ws[-1]*8/5)}" alt="Мастер собирает компьютер в мастерской STAR-COMP" loading="lazy">\n'
            f'      </picture>')
# popup контактов (вариант 4 без логотипа) — общий для всех страниц
_soc_links = (S.get('socials') or {})
_cp_tg = esc(_soc_links.get('telegram') or 'https://t.me/ST_COMP')
_cp_max = esc(_soc_links.get('max') or '#')
_cp_vk = esc(_soc_links.get('vk') or 'https://vk.com/star_comp_spb')
CONTACT_POPUP=f"""<dialog class="contact-popup" id="contact-popup" aria-label="Свяжитесь с нами">
  <div class="cp">
    <button class="menu__close cp__close" type="button" aria-label="Закрыть">×</button>
    <div class="cp__top"><h2 class="cp__title">Свяжитесь с нами</h2><p class="cp__lead">Выберите удобный канал — ответим быстро.</p></div>
    <div class="cp__list">
      <a class="cp__item" href="{_cp_tg}" target="_blank" rel="noopener"><span class="cp__icon">{svg('tg-white.svg','aria-hidden="true"',os.path.join(ROOT,'assets','footer')+os.sep)}</span><span class="cp__text"><b>Telegram</b><small>Написать в мессенджер</small></span><span class="cp__arr">→</span></a>
      <a class="cp__item" href="{_cp_max}" target="_blank" rel="noopener"><span class="cp__icon">{svg('max-white.svg','aria-hidden="true"',os.path.join(ROOT,'assets','footer')+os.sep)}</span><span class="cp__text"><b>MAX</b><small>Написать в MAX</small></span><span class="cp__arr">→</span></a>
      <a class="cp__item" href="{_cp_vk}" target="_blank" rel="noopener"><span class="cp__icon">{svg('vk-white.svg','aria-hidden="true"',os.path.join(ROOT,'assets','footer')+os.sep)}</span><span class="cp__text"><b>ВКонтакте</b><small>Сообщество STAR-COMP</small></span><span class="cp__arr">→</span></a>
      <a class="cp__item cp__item--accent" href="tel:{esc(S.get('phone_tel') or '+79939845505')}"><span class="cp__icon cp__icon--text">☎</span><span class="cp__text"><b>{txt(S.get('phone_display') or '8 (993) 984-55-05')}</b><small>Позвонить</small></span><span class="cp__arr">→</span></a>
      <a class="cp__item" href="mailto:{esc(S.get('email') or 'info@star-comp.ru')}"><span class="cp__icon cp__icon--text">@</span><span class="cp__text"><b>{esc(S.get('email') or 'info@star-comp.ru')}</b><small>Написать на почту</small></span><span class="cp__arr">→</span></a>
    </div>
    <div class="cp__footer"><p class="cp__address"><b>Адрес:</b> Заневский пр., 65 к5, 2 этаж<br><span class="cp__muted">Пн-Вс, 11:00-19:00</span></p><a class="cp__mapbtn" href="{esc(S.get('map_url') or 'https://yandex.ru/maps/-/CXbR7LiO')}" target="_blank" rel="noopener">Маршрут</a></div>
  </div>
</dialog>"""
body=(fill_text(_body).replace('{{CPU_FILTERS}}',_cpu_filters).replace('{{WHY_PHOTO}}',_why_photo)
      .replace('{{GIFTS_SECTION}}',GIFTS_SECTION).replace('{{MENU_LINKS}}',menu_links_html(False)))

_HOME_TITLE='STAR-COMP - сборка компьютеров на заказ'
_HOME_DESC='Игровые и рабочие компьютеры на заказ в СПб с 2009 года: 20+ готовых ПК в наличии, гарантия до 5 лет. Шоурум у м. Ладожская, доставка 0 ₽.'
_HOME_KEYWORDS='компьютеры на заказ СПб, игровые компьютеры СПб, сборка ПК на заказ, готовые игровые ПК, STAR-COMP, Стар Комп'
full=f'''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{_HOME_TITLE}</title>
<meta name="description" content="{_HOME_DESC}">
<meta name="keywords" content="{_HOME_KEYWORDS}">
<link rel="canonical" href="https://star-comp.ru">
<meta name="yandex-verification" content="968cf8204a45d4a7">
<meta property="og:url" content="https://star-comp.ru">
<meta property="og:title" content="{_HOME_TITLE}">
<meta property="og:description" content="{_HOME_DESC}">
<meta property="og:type" content="website">
<meta property="og:locale" content="ru_RU">
<meta property="og:image" content="https://star-comp.ru/assets/og-home.jpg">
<meta name="theme-color" content="#0a0a0c">
<link rel="icon" type="image/svg+xml" href="assets/favicon.svg">
<link rel="apple-touch-icon" href="assets/icon-192.png">
<script type="application/ld+json">{ld.replace('</','<\\/')}</script>
<link rel="preload" href="assets/gilroy-semibold.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/gilroy-regular.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/style.css?v={_STAMP}">
</head>
<body>
{body.replace('{{CARDS_LIST}}',cards_html(_cards,True)).replace('{{MORE_HIDDEN}}',_more_hidden()).replace('{{STOCK_SECTION}}',stock_section_html()).replace('{{FOOTER}}',FOOTER_MAIN)}
<script src="assets/page.js?v={_STAMP}"></script>
{CONTACT_POPUP}
</body>
</html>
'''
open(os.path.join(ROOT,'index.html'),'w',encoding='utf-8').write(inject_code(full))

# ---------- SEO-страницы-клоны главной ----------
# Собираются из тех же исходников, что и главная: любое изменение главной
# автоматически попадает сюда. Отличается только служебная часть для поисковиков
# (title, description, canonical) и заголовок H1, чтобы страницы не конкурировали
# в поиске друг с другом и с главной. Все SEO-тексты — в этом блоке.
_SEO_SLUGS=[]
def seo_clone(slug,title,desc,h1,keywords=''):
    _SEO_SLUGS.append(slug)
    kw=esc((keywords or '').strip())
    kw_tag=f'\n<meta name="keywords" content="{kw}">' if kw else ''
    return full.replace(
        f'<title>{_HOME_TITLE}</title>',
        f'<title>{title}</title>').replace(
        f'<meta name="description" content="{_HOME_DESC}">',
        f'<meta name="description" content="{desc}">{kw_tag}').replace(
        f'<meta name="keywords" content="{_HOME_KEYWORDS}">',
        '').replace(
        '<link rel="canonical" href="https://star-comp.ru">',
        f'<link rel="canonical" href="https://star-comp.ru/{slug}">').replace(
        '<meta property="og:url" content="https://star-comp.ru">',
        f'<meta property="og:url" content="https://star-comp.ru/{slug}">').replace(
        f'<meta property="og:title" content="{_HOME_TITLE}">',
        f'<meta property="og:title" content="{title}">').replace(
        f'<meta property="og:description" content="{_HOME_DESC}">',
        f'<meta property="og:description" content="{desc}">').replace(
        '<h1>'+_title_html()+'</h1>',
        f'<h1>{h1}</h1>')

def write_seo_clone(slug,title,desc,h1,keywords=''):
    html=seo_clone(slug,title,desc,h1,keywords)
    open(os.path.join(ROOT,slug+'.html'),'w',encoding='utf-8').write(inject_code(html))
    print('SEO-страница',slug,len(html))

# «Купить компьютер в СПб» — запрос «купить компьютер…»
_KUPIT_TITLE='Купить компьютер в Санкт-Петербурге — сборка на заказ с гарантией | STAR-COMP'
_KUPIT_DESC='Купить компьютер в СПб с гарантией до 5 лет: 20+ готовых ПК в наличии, без предоплаты. Шоурум у м. Ладожская, доставка и подключение 0 ₽.'
_KUPIT_KEYWORDS='купить компьютер СПб, купить игровой компьютер в Санкт-Петербурге, магазин компьютеров СПб, готовые игровые ПК'
_KUPIT_H1='Купить компьютер с гарантией и запасом на 5 лет'
write_seo_clone('kupit-kompyuter-spb',_KUPIT_TITLE,_KUPIT_DESC,_KUPIT_H1,_KUPIT_KEYWORDS)

# «Сборка компьютеров на заказ» — адрес, который владелец продвигал ссылкой на Тильде.
# Title и H1 — дословно с тильдовской страницы (из индекса Яндекса), чтобы не сбить позицию.
# Description — текст с той же страницы, который Яндекс показывает в сниппете.
_SBORKA_TITLE='STARCOMP - сборка компьютеров на заказ'
_SBORKA_DESC='Сборка компьютеров на заказ в СПб с 2009 года. Расчёт за 15 минут, сборка от 2 дней, только новые комплектующие, Windows и Office в цене. Гарантия до 5 лет.'
_SBORKA_KEYWORDS='сборка компьютера на заказ, сборка ПК СПб, собрать компьютер на заказ, сборка игрового компьютера, подбор комплектующих'
_SBORKA_H1='СБОРКА КОМПЬЮТЕРОВ НА ЗАКАЗ С ГАРАНТИЕЙ ДО 5 ЛЕТ'
write_seo_clone('sborka-kompyuterov-na-zakaz',_SBORKA_TITLE,_SBORKA_DESC,_SBORKA_H1,_SBORKA_KEYWORDS)

# ---------- тестовая страница blocktest: блок «7 причин заказать у нас» ----------
# Шапка, меню и подвал — от главной; вместо содержимого главной — один тестовый блок.
# Стили блока — assets/blocktest.css (из src/blocktest.css). Страница закрыта от поиска.
_bt_stem,_bt_ws=derive('content/photos/blocktest/blocktest_1.webp',[480,800],5/8)
_bt_photo=(f'      <picture class="why__photo">\n'
           f'        <source type="image/avif" srcset="{srcset(_bt_stem,_bt_ws,"avif")}" sizes="(min-width:64rem) 23rem, 1px">\n'
           f'        <img src="assets/{_bt_stem}-{_bt_ws[-1]}.webp" srcset="{srcset(_bt_stem,_bt_ws,"webp")}" sizes="(min-width:64rem) 23rem, 1px" width="{_bt_ws[-1]}" height="{round(_bt_ws[-1]*8/5)}" alt="Мастер собирает компьютер в мастерской STAR-COMP" loading="lazy">\n'
           f'      </picture>')
_bt_block=fill_text(open(os.path.join(ROOT,'src','blocktest.body.html'),encoding='utf-8').read()).replace('{{WHY_PHOTO}}',_bt_photo)
_bt_block+= '\n'+GIFTS_SECTION   # подарки показываем и на старой тестовой странице
_bt_main=full[full.index('<main>'):full.index('</main>')+len('</main>')]
_bt=full.replace(_bt_main,'<main>\n'+_bt_block+'</main>').replace(
    '<title>STAR-COMP - сборка компьютеров на заказ</title>',
    '<title>Тест блока «7 причин» | STAR-COMP</title>\n<meta name="robots" content="noindex, nofollow">')
open(os.path.join(ROOT,'blocktest.html'),'w',encoding='utf-8').write(inject_code(_bt))
print('тестовая страница blocktest',len(_bt))

# ---------- тестовая страница test: площадка новых блоков ----------
# Отдельная от blocktest.html страница (noindex) для доработки новых блоков.
# Шапку, меню, FAQ и контакты с главной НЕ берём. Сейчас на странице:
# «7 причин» №8, палитра для Figma и «Подарки всем клиентам». Блок отзывов
# временно скрыт — чтобы вернуть, поставить _TEST_REVIEWS_ON=True.
# Стили новых блоков — src/test.css → assets/test.css.
_TEST_REVIEWS_ON=False

_test_photo=(f'        <picture>\n'
             f'          <source type="image/avif" srcset="{srcset(_bt_stem,_bt_ws,"avif")}" sizes="(min-width:65rem) 44vw, 100vw">\n'
             f'          <img src="assets/{_bt_stem}-{_bt_ws[-1]}.webp" srcset="{srcset(_bt_stem,_bt_ws,"webp")}" sizes="(min-width:65rem) 44vw, 100vw" width="{_bt_ws[-1]}" height="{round(_bt_ws[-1]*8/5)}" alt="Мастер собирает компьютер в мастерской STAR-COMP" loading="lazy">\n'
             f'        </picture>')
# Отзывы — тот же фрагмент REVIEWS_HTML, что и на основном сайте, только по флагу.
_test_reviews=f'<div class="wrap">\n{REVIEWS_HTML}\n  </div>' if _TEST_REVIEWS_ON else ''
_test_block=(fill_text(open(os.path.join(ROOT,'src','test.body.html'),encoding='utf-8').read())
    .replace('{{TEST_PHOTO}}',_test_photo)
    .replace('{{GIFTS_SECTION}}',GIFTS_SECTION)
    .replace('{{REVIEWS_BLOCK}}',_test_reviews)
    .replace('{{STOCK_SECTION}}',stock_section_html())
    .replace('{{POPUP_LOGO}}',svg('logo-icon.svg','class="pp__logo" aria-hidden="true"'))
    .replace('{{POPUP_TG}}',svg('tg-white.svg','aria-hidden="true"',os.path.join(ROOT,'assets','footer')+os.sep))
    .replace('{{POPUP_MAX}}',svg('max-white.svg','aria-hidden="true"',os.path.join(ROOT,'assets','footer')+os.sep))
    .replace('{{POPUP_VK}}',svg('vk-white.svg','aria-hidden="true"',os.path.join(ROOT,'assets','footer')+os.sep)))
import quiz_build
quiz_build.build(ROOT)
_test_block=_test_block+'\n'+quiz_build.test_block(_STAMP)
# Берём только <head> от главной, чтобы сохранить шрифты, метатеги и счётчики.
_test_head=full[:full.index('<body>')].replace(
    '<title>STAR-COMP - сборка компьютеров на заказ</title>',
    '<title>Тестовые блоки | STAR-COMP</title>\n<meta name="robots" content="noindex, nofollow">').replace(
    f'<link rel="stylesheet" href="assets/style.css?v={_STAMP}">',
    f'<link rel="stylesheet" href="assets/style.css?v={_STAMP}">\n<link rel="stylesheet" href="assets/test.css?v={_STAMP}">')
_test=f'{_test_head}<body>\n<main>\n{_test_block}\n</main>\n</body>\n</html>\n'
open(os.path.join(ROOT,'test.html'),'w',encoding='utf-8').write(inject_code(_test))
print('тестовая страница test',len(_test))

# ---------- страница v1: первый блок нового редизайна ----------
# Отдельная noindex-страница, не наследует стили старого сайта. Верстка лежит в
# src/v1.body.html и src/v1.css; страница масштабируется до ширины окна, сохраняя
# геометрию макета 1440x1332. Шрифты и фото копируются в assets/ при сборке.
_copy_v1_assets()
_v1_head=f'''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Верстка редизайна v1 | STAR-COMP</title>
<meta name="robots" content="noindex, nofollow">
<meta name="theme-color" content="#0A0A0C">
<link rel="icon" type="image/svg+xml" href="assets/favicon.svg">
<link rel="preload" href="assets/InterDisplay-Regular.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/InterDisplay-SemiBold.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/v1.css?v={_STAMP}">
</head>
'''
_v1=f'''{_v1_head}<body>
<main class="v1-stage">
{_v1_body}
</main>
<script>
(function(){{
  function fit(){{
    var scale=Math.min(1,window.innerWidth/1440);
    document.documentElement.style.setProperty('--v1-scale',scale);
  }}
  fit();
  window.addEventListener('resize',fit,{{passive:true}});
}})();
</script>
</body>
</html>
'''
open(os.path.join(ROOT,'v1.html'),'w',encoding='utf-8').write(inject_code(_v1))
print('страница редизайна v1',len(_v1))

# Быстрый режим: дальше идут страницы сборок и нарезка всех фото — самое долгое.
# Для правок тестовой страницы они не нужны, поэтому выходим сразу, обновив
# только три внешних файла, от которых зависит test.html.
if TEST_ONLY:
    for _f,_data in [('style.css',_css),('page.js',_js),('test.css',open('test.css',encoding='utf-8').read()),('v1.css',_v1_css)]:
        open(os.path.join(ROOT,'assets',_f),'w',encoding='utf-8').write(_data)
    print('быстрая сборка: готово test.html, v1.html + assets/style.css, page.js, test.css, v1.css')
    raise SystemExit(0)

# ---------- страница 404: GitHub Pages отдаёт её для несуществующих адресов ----------
# Сделана самодостаточной (стили внутри), чтобы работала и из вложенного адреса,
# где относительные пути к assets/ уже не находятся.
_404_HTML=r'''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Страница не найдена — STAR-COMP</title>
<meta name="description" content="Такой страницы нет. Вернитесь на главную STAR-COMP.">
<meta name="robots" content="noindex, nofollow">
<meta name="theme-color" content="#0a0a0c">
<style>
:root{color-scheme:dark}
*{box-sizing:border-box}
html,body{margin:0;min-height:100%}
body{min-height:100svh;display:flex;align-items:center;justify-content:center;padding:24px;background:#0a0a0c;color:#fff;font-family:Gilroy,Arial,sans-serif;text-align:center}
.box{width:min(100%,560px)}
.code{margin:0 0 12px;font-size:96px;font-weight:600;line-height:1;color:#00d9ff;letter-spacing:-.04em}
.logo{margin:0 0 24px;font-size:14px;font-weight:600;letter-spacing:.16em;color:#bdbdc2}
h1{margin:0 0 16px;font-size:32px;line-height:1.2}
p.lead{margin:0 auto 32px;max-width:34rem;color:#bdbdc2;font-size:16px;line-height:1.5}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:.5rem;min-height:52px;padding:12px 28px;border-radius:100px;background:#00d9ff;color:#0a0a0c;font-size:18px;font-weight:600;text-decoration:none;transition:transform .2s}
@media (hover:hover){.btn:hover{transform:translateY(-2px)}}
@media (max-width:480px){.code{font-size:72px}h1{font-size:26px}}
</style>
</head>
<body>
<main class="box">
  <p class="code">404</p>
  <p class="logo">STAR-COMP</p>
  <h1>Страница не найдена</h1>
  <p class="lead">Видимо информация устарела и мы её убрали. Вернитесь на главную — там все сборки и контакты.</p>
  <a class="btn" id="home-link" href="/">На главную <span aria-hidden="true">&rarr;</span></a>
</main>
<script>
(function(){
  var p=location.pathname, m=p.match(/^\/star-comp_cl\//);
  document.getElementById('home-link').href=(m?m[0]:'/');
})();
</script>
</body>
</html>
'''
open(os.path.join(ROOT,'404.html'),'w',encoding='utf-8').write(inject_code(_404_HTML))
print('страница 404',len(_404_HTML))
import thanks_build
thanks_build.build(ROOT,inject_code)
frag=f'''<title>STAR-COMP</title>
<meta name="claude:viewport-fit-sides" content="cover">
<style>
{_css}</style>
{body.replace('{{CARDS_LIST}}',cards_html(_cards,True)).replace('{{MORE_HIDDEN}}',_more_hidden()).replace('{{STOCK_SECTION}}',stock_section_html()).replace('{{FOOTER}}',FOOTER_MAIN)}
<script>
{_js}</script>
'''
os.makedirs(os.path.join(ROOT,'.preview'),exist_ok=True)
open(os.path.join(ROOT,'.preview','star-comp.html'),'w',encoding='utf-8').write(frag)
print(len(full))


def gallery_html(d):
    name=esc(d['name']); slides=[]; dots=[]
    for n,ph in enumerate(d.get('photos') or []):
        stem,ws=derive(ph['image'],[240,640,1024,1600,2400],4/3)
        big=[w for w in ws if w>=640] or ws
        mid=1024 if 1024 in big else big[-1]
        alt=esc(ph.get('alt')) or f'фото {n+1}'
        load='fetchpriority="high"' if n==0 else 'loading="lazy"'
        slides.append(f"""        <li>
          <picture>
            <source type="image/avif" srcset="{srcset(stem,big,'avif')}" sizes="{SIZES}">
            <img src="assets/{stem}-{mid}.webp" srcset="{srcset(stem,big,'webp')}" sizes="{SIZES}" width="{mid}" height="{round(mid*3/4)}" alt="{name}: {alt}" {load} decoding="async">
          </picture>
        </li>""")
        cur=' aria-current="true"' if n==0 else ''
        dots.append(f'        <button type="button" aria-label="Фото {n+1}: {alt}"{cur}></button>')
    nl='\n'
    return f"""    <div class="gallery" id="gallery">
      <div class="gallery__stage">
      <ul class="gallery__track" tabindex="0" aria-label="Фотографии сборки. Нажмите, чтобы увеличить">
{nl.join(slides)}
      </ul>
      <button class="gallery__nav gallery__nav--prev" type="button" aria-label="Предыдущее фото">{ARROW_L}</button>
      <button class="gallery__nav gallery__nav--next" type="button" aria-label="Следующее фото">{ARROW_R}</button>
      </div>
      <div class="gallery__dots">
{nl.join(dots)}
      </div>
    </div>"""

def vcode(x):
    """Только код ролика: если вставили полную ссылку kinescope.io/…, вытаскиваем её последний сегмент."""
    x=str(x or '').strip()
    return x.split('/')[-1].split('?')[0] if x else ''

def video_html(d):
    v=d.get('video') or {}
    h_id=vcode(v.get('horizontal')); v_id=vcode(v.get('vertical'))
    if not (h_id or v_id): return ''
    name=esc(d['name'])
    # Статичная обложка — первый кадр прямо с Kinescope (poster.jpg, 4K):
    # показывается, пока плеер грузится в фоне. Если кадр не отдался — просто чёрный фон.
    if v_id and not h_id:
        cls=' video video--vertical'
        poster=f"https://kinescope.io/{v_id}/poster.jpg"
        cover=(f'\n          <img src="{poster}" alt="Смотреть видео о сборке {name}" loading="lazy" decoding="async" onerror="this.style.display=\'none\'">')
    else:
        cls=' video'
        poster=f"https://kinescope.io/{(h_id or v_id)}/poster.jpg"
        cover=(f'\n          <img src="{poster}" alt="Смотреть видео о сборке {name}" loading="lazy" decoding="async" onerror="this.style.display=\'none\'">')
    return f"""      <div class="about__video">
        <div class="{cls}" id="video" data-h="{esc(h_id or v_id)}" data-v="{esc(v_id or h_id)}" data-title="Видео о сборке {name}" style="background:#0a0a0c url('{poster}') center/cover no-repeat">
          <button class="video__play" type="button">
            <picture>
              {cover}
            </picture>
            <span class="video__icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M8 5.5v13l11-6.500z"/></svg></span>
          </button>
        </div>
      </div>"""

def body_html(d):
    name=esc(d['name'])
    sub=f' <i class="sr-only">— </i><span>{txt(d["subtitle"])}</span>' if d.get('subtitle') else ''
    note=f'\n      <p class="product__note">{txt(d["note"])}</p>' if d.get('note') else ''
    # Комплектующие: новый формат — объект {cpu: '…', gpu: '…', …} (из админки,
    # каждое поле — своя категория железа). Старый список [{label, value}] тоже читается.
    _SPEC_FIELDS=[('cpu','Процессор'),('gpu','Видеокарта'),('motherboard','Материнская плата'),
                  ('ram','Оперативная память'),('storage','Накопитель'),('psu','Блок питания'),
                  ('cooling','Охлаждение'),('case','Корпус')]
    def spec_rows(specs):
        if isinstance(specs, dict):
            return [(label, specs.get(key)) for key, label in _SPEC_FIELDS if specs.get(key)]
        return [(x.get('label'), x.get('value')) for x in specs or [] if x.get('label') and x.get('value')]
    specs='\n'.join(f'      <div><dt>{esc(l).rstrip(":")}:</dt><dd>{esc(v)}</dd></div>' for l, v in spec_rows(d.get('specs')))
    # Блок «О сборке»: описание и текст рядом с видео (на мобильном — друг под другом)
    lead=f'\n        <p class="section__lead">{txt(d["lead"])}</p>' if d.get('lead') else ''
    about=f'\n        <div class="seo-text"><p>{txt(d["about"])}</p></div>' if d.get('about') else ''
    vid=video_html(d)
    text=lead+about
    # только вертикальное видео: на десктопе видео ставится вторым столбцом в блок «Конфигурация»
    vertical_only='video--vertical' in vid
    # страницы без видео и с горизонтальным видео — блок «Конфигурация» в две колонки
    # на всю ширину; только с вертикальным видео — плашки слева, видео справа
    spec_cols='' if vertical_only else ' section--spec--2col'
    flex_note=open('inner.flex-note.html',encoding='utf-8').read().rstrip()
    if vertical_only:
        # блок «О сборке» — только текст, без видео
        if text:
            text_html=f'\n      <div class="about__text">{lead}{about}\n      </div>'
            about_section=f'''  <section class="section section--about wrap" aria-label="О сборке">
    <div class="about">{text_html}
    </div>
  </section>'''
        else:
            about_section=''
        spec_section=f'''  <section class="section section--spec wrap spec--video-v" aria-labelledby="spec-title">
    <h2 class="section__title" id="spec-title">Конфигурация</h2>
    <div class="spec__cols">
      <div class="spec__main">
    <dl class="spec-grid">
{specs}
    </dl>
{flex_note}
      </div>
      <div class="spec__video">
{vid}
      </div>
    </div>
  </section>'''
    else:
        if text or vid:
            has_v=' about--video-h' if vid else ''
            # без текста секция прижимается к первому экрану (галерее) без верхнего отступа
            flush='' if text else ' section--flush'
            text_html=f'\n      <div class="about__text">{lead}{about}\n      </div>' if text else ''
            about_section=f'''  <section class="section section--about wrap{flush}" aria-label="О сборке">
    <div class="about{has_v}">{text_html}
{vid}
    </div>
  </section>'''
        else:
            about_section=''
        spec_section=f'''  <section class="section section--spec wrap{spec_cols}" aria-labelledby="spec-title">
    <h2 class="section__title" id="spec-title">Конфигурация</h2>
    <dl class="spec-grid">
{specs}
    </dl>
{flex_note}
  </section>'''
    _p_price = d['price']
    _p_show_from = d.get('show_from') is not False
    # Price source of truth: card in "Блоки на главной" (stock/cards), fallback to build json.
    _slug = d.get('slug') or ''
    for _src in (_STK.get('cards', []) if isinstance(_STK, dict) else [], _cards):
        for _c in _src:
            if str(_c.get('page') or '') == _slug:
                if _c.get('price_from') is not None:
                    try: _p_price = int(_c['price_from'])
                    except Exception: pass
                _p_show_from = _c.get('show_from') is not False
                break
        else:
            continue
        break
    return f"""<main>
  <section class="product wrap">
    <div class="product__gallery">
{gallery_html(d)}
    </div>

    <div class="product__info">
      <h1>{name}{sub}</h1>
      <div class="product__cost">
        <p class="product__label">Стоимость:</p>
        <p class="product__price">{'от&nbsp;' if _p_show_from else ''}{money(_p_price)}</p>
        <button class="tf-ya-btn product__contact" type="button" data-contact-popup>Связаться</button>
      </div>
      {note}
    </div>
  </section>
{about_section}
{spec_section}
{stock_section_html(d['slug'])}
{GIFTS_SECTION}
</main>"""

src=open('page.body.html',encoding='utf-8').read()
header=src[:src.index('<main>')]
menu=src[src.index('<dialog'):]
def fill(x): return fill_text(x.replace('{{MENU_LINKS}}',menu_links_html(True)).replace('{{LOGO_ICON}}',logo_icon).replace('{{LOGO_WORD}}',logo_word).replace('{{SOCIALS}}',socials).replace('{{SOCIALS_MENU}}',socials.replace('mx-','mxm-')))
header_i=fill(header)
menu_i=fill(menu)
# файлы стилей/скриптов для внутренних страниц пишем заранее (см. блок в конце сборки)
_inner_js_full=_inner_js+_menu_js_part()

def page_html(d):
    slug=d['slug'].strip().strip('/')
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]*',slug): raise SystemExit(f'Плохой адрес страницы: {slug!r} — только латиница, цифры и дефис')
    seo=d.get('seo') or {}
    name=d['name'].strip()
    title=esc(seo.get('title') or (f"{name} — {d['subtitle']}" if d.get('subtitle') else name))
    desc=esc(seo.get('description') or d.get('lead') or d.get('subtitle') or name)
    keywords=esc((seo.get('keywords') or '').strip())
    keywords_tag=f'\n<meta name="keywords" content="{keywords}">' if keywords else ''
    url=f'https://star-comp.ru/{slug}'
    photos=d.get('photos') or []
    og=og_image(photos[0]['image']) if photos else 'assets/og-home.jpg'
    ld={"@context":"https://schema.org","@type":"Product","name":name,"description":(d.get('lead') or d.get('subtitle') or name),"image":f"https://star-comp.ru/{og}","brand":{"@type":"Brand","name":"STAR-COMP"},"offers":{"@type":"Offer","url":url,"price":str(int(d['price'])),"priceCurrency":"RUB","availability":"https://schema.org/InStock"}}
    return f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">{keywords_tag}
<link rel="canonical" href="{url}">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{esc(d.get('lead') or desc)}">
<meta property="og:type" content="product">
<meta property="og:locale" content="ru_RU">
<meta property="og:image" content="https://star-comp.ru/{og}">
<meta name="theme-color" content="#0a0a0c">
<link rel="icon" type="image/svg+xml" href="assets/favicon.svg">
<link rel="apple-touch-icon" href="assets/icon-192.png">
<script type="application/ld+json">{json.dumps(ld,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')}</script>
<link rel="preload" href="assets/gilroy-semibold.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/gilroy-regular.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/inner.css?v={_STAMP}">
</head>
<body>
{header_i}
{body_html(d)}

{FOOTER_INNER}

{menu_i}
{CONTACT_POPUP}
<script src="assets/inner.js?v={_STAMP}"></script>
</body>
</html>
"""

# Защита от публикации копий: две сборки с одним адресом (slug) не должны перезаписывать друг друга
_slugs={}
_dupes=[]
for f in sorted(glob.glob(os.path.join(ROOT,'content','builds','*.json'))):
    d=json.load(open(f,encoding='utf-8'))
    d.setdefault('slug',os.path.splitext(os.path.basename(f))[0])
    s=d['slug'].strip().strip('/')
    if s in _slugs:
        _dupes.append((s,os.path.basename(_slugs[s]),os.path.basename(f)))
    _slugs[s]=f
if _dupes:
    print('ОШИБКА: найдены сборки с одинаковым адресом (slug). Публикация заблокирована.')
    for s,a,b in _dupes:
        print(f'  адрес «{s}»: {a} и {b} — измените адрес у копии в админке')
    raise SystemExit(1)

for f in sorted(glob.glob(os.path.join(ROOT,'content','builds','*.json'))):
    d=json.load(open(f,encoding='utf-8'))
    d.setdefault('slug',os.path.splitext(os.path.basename(f))[0])
    out=inject_code(page_html(d))
    open(os.path.join(ROOT,d['slug']+'.html'),'w',encoding='utf-8').write(out)
    print('сборка',d['slug'],len(out))

# sitemap.xml: главная + SEO-клоны + все страницы сборок. Адреса без .html — ровно как в canonical.
from datetime import date as _date
_today=_date.today().isoformat()
def _lastmod(*paths):
    dates=[]
    for p in paths:
        try:
            dates.append(_date.fromtimestamp(os.path.getmtime(p)).isoformat())
        except OSError:
            pass
    return max(dates) if dates else _today

_common=[os.path.join(ROOT,'src','build.py'),os.path.join(ROOT,'src','page.body.html'),
         os.path.join(ROOT,'src','page.css'),os.path.join(ROOT,'src','page.js'),
         os.path.join(ROOT,'content','settings.json'),os.path.join(ROOT,'content','home.json'),
         os.path.join(ROOT,'content','cards.json'),os.path.join(ROOT,'content','stock.json')]
_home_last=_lastmod(*_common, os.path.join(ROOT,'content','faq.json'), os.path.join(ROOT,'content','perks.json'),
                    os.path.join(ROOT,'src','gifts.body.html'))
_url_dates=[('https://star-comp.ru', _home_last)]
for s in _SEO_SLUGS:
    _url_dates.append((f'https://star-comp.ru/{s}', _home_last))
for s in sorted(_slugs):
    _url_dates.append((f'https://star-comp.ru/{s}', _lastmod(os.path.join(ROOT,'content','builds',f'{s}.json'),
                                                             os.path.join(ROOT,'src','inner.css'), os.path.join(ROOT,'src','inner.js'))))
open(os.path.join(ROOT,'sitemap.xml'),'w',encoding='utf-8').write(
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    +'\n'.join(f'  <url><loc>{u}</loc><lastmod>{d}</lastmod></url>' for u,d in _url_dates)
    +'\n</urlset>\n')
print('sitemap:',len(_url_dates),'адресов')

# robots.txt: закрываем служебные папки, указываем карту сайта
open(os.path.join(ROOT,'robots.txt'),'w',encoding='utf-8').write(
    'User-agent: *\n'
    'Disallow: /admin/\n'
    'Disallow: /content/\n'
    '\n'
    'Sitemap: https://star-comp.ru/sitemap.xml\n')
print('robots.txt: готово')

# ---------- внешние стили и скрипты в assets/ (кэшируются между страницами) ----------
open(os.path.join(ROOT,'assets','style.css'),'w',encoding='utf-8').write(_css)
open(os.path.join(ROOT,'assets','page.js'),'w',encoding='utf-8').write(_js)
open(os.path.join(ROOT,'assets','inner.css'),'w',encoding='utf-8').write(_inner_css_full)
open(os.path.join(ROOT,'assets','inner.js'),'w',encoding='utf-8').write(_inner_js_full)
open(os.path.join(ROOT,'assets','test.css'),'w',encoding='utf-8').write(open('test.css',encoding='utf-8').read())
open(os.path.join(ROOT,'assets','v1.css'),'w',encoding='utf-8').write(_v1_css)
print('стили/скрипты: assets/style.css, page.js, inner.css, inner.js, test.css, v1.css (метка',_STAMP+')')

# ---------- чистка assets: удаляем файлы, на которые не ссылается ни одна страница ----------
# Сначала дописываем отложенную нарезку фото (пул потоков) — чистка видит готовые файлы.
_run_enc_queue()
# Сюда попадают дубли после переименования фото и нарезки, потерявшие актуальность.
_STATIC={'favicon.svg','icon-192.png','og-home.jpg','gilroy-regular.woff2','gilroy-semibold.woff2',

         'style.css','page.js','inner.css','inner.js','blocktest.css','test.css','v1.css',
         'v1-hero.webp',*_V1_FONTS,
         # готовые файлы, которые сборщик не создаёт: фото первого экрана и аватарки отзывов
         'hero-600.avif','hero-800.avif','hero-1000.avif','hero-600.webp','hero-800.webp','hero-1000.webp'}
for _ava in ('ava-1','ava-2','ava-3','ava-4','ava-5'):
    _STATIC.add(f'footer/{_ava}.webp')
_build_start=time.time()
_referenced=set()
for _page in glob.glob(os.path.join(ROOT,'*.html'))+glob.glob(os.path.join(ROOT,'.preview','*.html')):
    _referenced.update(re.findall(r'assets/[A-Za-z0-9._\-/]+',open(_page,encoding='utf-8').read()))
_used={p[len('assets/'):].rstrip('\'",) ') for p in _referenced}
_assets_dir=os.path.join(ROOT,'assets')
_removed=0; _freed=0
for _dirpath,_dirs,_files in os.walk(_assets_dir,topdown=False):
    for _fn in _files:
        _rel=os.path.relpath(os.path.join(_dirpath,_fn),_assets_dir).replace('\\','/')
        _p=os.path.join(_dirpath,_fn)
        # страховка от параллельных сборок: не трогаем файлы, обновлённые после старта сборки
        if os.path.getmtime(_p)>_build_start: continue
        if _rel in _STATIC or _rel in _used: continue
        _freed+=os.path.getsize(_p); os.remove(_p); _removed+=1
    if not os.listdir(_dirpath) and _dirpath!=_assets_dir: os.rmdir(_dirpath)
print('чистка assets: удалено',_removed,'файлов,',round(_freed/1048576,1),'МБ')
