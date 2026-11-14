# Сборка сайта: python3 src/build.py
# Собирает index.html и страницы сборок из исходников в src/ (стили и иконки встраиваются в HTML).
import os,re
SRC=os.path.dirname(os.path.abspath(__file__))
ROOT=os.path.dirname(SRC)
os.chdir(SRC)
A='icons/'
def svg(name, attrs):
    s=open(A+name,encoding='utf-8').read()
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

# ---------- карточки «Популярных конфигураций» из content/cards.json ----------
_cards=load_content('cards.json',{}).get('cards') or []

# ---------- страницы сборок: по одной на каждый файл в content/builds/ ----------
# Данные (название, цена, фото, видео, комплектующие) правятся в админке /admin или прямо в JSON.
# Фото лежат в content/photos/ в исходном виде; нужные размеры AVIF/WebP сборщик нарезает сам в assets/.
import json,glob,html
from PIL import Image,ImageOps

def esc(x): return html.escape(str(x or '').strip(),quote=True)
def typo(x):
    """Неразрывные пробелы после коротких предлогов и перед знаком рубля — чтобы строки не рвались некрасиво."""
    x=re.sub(r'(?<![\w-])(в|на|и|с|к|о|у|а|за|из|по|от|до|для|или|не|но|под|при)\s+',lambda m:m.group(1)+'&nbsp;',x,flags=re.I)
    x=re.sub(r'\s+(—|₽)',r'&nbsp;\1',x)
    return x
def txt(x): return typo(esc(x))
def money(n): return f'{int(n):,}'.replace(',','&nbsp;')+'&nbsp;₽'
def money_tr(n):
    """Цена в тысячах рублей, как на старом сайте: 348 т.р."""
    t=n/1000
    s=f'{t:.0f}' if abs(t-round(t))<0.05 else f'{t:.1f}'.replace('.',',')
    return s+'&nbsp;т.р.'

def derive(src,widths,ratio):
    """Нарезает фото под нужные ширины (обрезка по центру до ratio=ширина/высота). Возвращает (имя, [ширины], высота_на_ширину)."""
    path=os.path.join(ROOT,src.lstrip('/'))
    stem=os.path.splitext(os.path.basename(path))[0]
    with Image.open(path) as im:
        W,H=ImageOps.exif_transpose(im).size
    W=min(W,int(H*ratio))  # ширина после обрезки
    ws=[w for w in widths if w<=W] or [widths[0]]
    todo=[w for w in ws if not all(os.path.exists(os.path.join(ROOT,'assets',f'{stem}-{w}.{e}')) for e in ('avif','webp'))]
    if todo:
        im=ImageOps.exif_transpose(Image.open(path)).convert('RGB')
        for w in todo:
            t=ImageOps.fit(im,(w,round(w/ratio)),Image.LANCZOS)
            t.save(os.path.join(ROOT,'assets',f'{stem}-{w}.webp'),quality=80,method=6)
            t.save(os.path.join(ROOT,'assets',f'{stem}-{w}.avif'),quality=60)
    return stem,ws

def focal_derive(src,widths,ratio,focal):
    """Обрезка фото вокруг фокусной точки. focal=(x,y) — проценты исходного фото (50/50 — центр).
    Имя файла включает точку фокуса: сменишь фокус в админке — сменится и файл, кэш не помешает.
    Кадры пересоздаются при каждой сборке, потому что результат зависит от данных."""
    path=os.path.join(ROOT,src.lstrip('/'))
    X=int(round(max(0,min(100,focal[0]))))
    Y=int(round(max(0,min(100,focal[1]))))
    stem=os.path.splitext(os.path.basename(path))[0]+f'-f{X}x{Y}'
    with Image.open(path) as im:
        W,H=ImageOps.exif_transpose(im).size
    cw=min(W,int(H*ratio))  # ширина видимой области
    ch=round(cw/ratio)      # высота видимой области
    left=min(max(round(X/100*W-cw/2),0),W-cw)   # видимая область прижата к краям
    top=min(max(round(Y/100*H-ch/2),0),H-ch)
    ws=[w for w in widths if w<=cw] or [widths[0]]
    crop=ImageOps.exif_transpose(Image.open(path)).convert('RGB').crop((left,top,left+cw,top+ch))
    for w in ws:
        t=crop.resize((w,round(w/ratio)),Image.LANCZOS)
        t.save(os.path.join(ROOT,'assets',f'{stem}-{w}.webp'),quality=80,method=6)
        t.save(os.path.join(ROOT,'assets',f'{stem}-{w}.avif'),quality=60)
    return stem,ws

def card_image(c):
    """Картинка карточки: либо строка-путь (центральная обрезка), либо объект {path,x,y} (обрезка по фокусу)."""
    img=c.get('image')
    if isinstance(img,dict):
        return focal_derive(img.get('path',''),[480,960],4/3,(img.get('x',50) or 50,img.get('y',50) or 50))
    return derive(img or '',[480,960],4/3)

def og_image(src):
    path=os.path.join(ROOT,src.lstrip('/'))
    stem=os.path.splitext(os.path.basename(path))[0]
    out=os.path.join(ROOT,'assets',f'{stem}-og.jpg')
    if not os.path.exists(out):
        ImageOps.fit(ImageOps.exif_transpose(Image.open(path)).convert('RGB'),(1200,630),Image.LANCZOS).save(out,quality=82,optimize=True,progressive=True)
    return f'assets/{stem}-og.jpg'
def srcset(stem,ws,ext): return ', '.join(f'assets/{stem}-{w}.{ext} {w}w' for w in ws)

# ---------- контакты, соцсети и преимущества: из content/settings.json и perks.json ----------
_soc=(S.get('socials') or {})
_social_defs=[('max',max_svg,'Написать в MAX'),('telegram',tg_svg,'Написать в Telegram'),('vk',vk_svg,'Группа ВКонтакте')]
socials='\n'.join(f'<a class="social" href="{esc(_soc.get(k,""))}" target="_blank" rel="noopener" aria-label="{label}">{ic}</a>'
                  for k,ic,label in _social_defs if _soc.get(k))

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
    """Заголовок главной: обычная часть + выделенный акцент <em> + обычное окончание."""
    h1=txt(H.get('title_before'))
    if H.get('title_accent'): h1+=' <em>'+txt(H.get('title_accent'))+'</em>'
    if H.get('title_after'): h1+=' '+txt(H.get('title_after'))
    return re.sub(r'&nbsp; ',r'&nbsp;',h1)

def _cards_title_html():
    """Заголовок блока конфигураций: обычная часть + выделенный акцент <em>."""
    t=txt(H.get('cards_title') or 'Последние проекты нашей')
    if H.get('cards_title_accent'): t+=' <em>'+txt(H.get('cards_title_accent'))+'</em>'
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
}
def fill_text(x):
    for k,v in FILLS.items(): x=x.replace(k,v)
    return x

SIZES='(min-width: 1920px) 60vw, (min-width: 1024px) min(1160px, calc((100vh - 264px) * 1.34)), (min-width: 608px) 576px, calc(100vw - 32px)'
CARD_SIZES='(min-width: 1920px) 24vw, (min-width: 1240px) 380px, (min-width: 1024px) 31vw, (min-width: 608px) 576px, calc(100vw - 32px)'
ARROW_L='<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M10 3 5 8l5 5"/></svg>'
ARROW_R='<svg viewBox="0 0 16 16" aria-hidden="true"><path d="m6 3 5 5-5 5"/></svg>'

def card_html(c,hidden=False):
    """Одна карточка конфигурации для главной и для блока «Другие конфигурации»."""
    name=esc(c['name'])
    stem,ws=card_image(c)
    w0=ws[0]; h0=round(w0*3/4)
    alt=txt(c.get('alt') or c['name'])
    tag=f'\n          <span class="card__tag">{txt(c["tag"])}</span>' if c.get('tag') else ''
    specs='\n'.join(f'          <div><dt>{esc(s["label"]).rstrip(":")}:</dt><dd>{esc(s["value"])}</dd></div>' for s in c.get('specs') or [])
    href=esc(c.get('page') or '') or '#podbor'
    extra=' hidden' if hidden else ''
    return f'''      <li class="card"{extra}>
        <div class="card__media">
          <picture>
            <source type="image/avif" srcset="{srcset(stem,ws,'avif')}" sizes="{CARD_SIZES}">
            <img src="assets/{stem}-{w0}.webp" srcset="{srcset(stem,ws,'webp')}" sizes="{CARD_SIZES}" width="{w0}" height="{h0}" alt="{alt}" loading="lazy" decoding="async">
          </picture>{tag}
        </div>
        <div class="card__body">
          <h3 class="card__name"><a href="{href}">{name}</a></h3>
          <dl class="specs">
{specs}
          </dl>
          <div class="card__foot">
            <p class="card__price"><span>Стоимость на момент сборки:</span><b>от&nbsp;{money(c['price_from'])}</b></p>
            <span class="card__go" aria-hidden="true"><svg viewBox="0 0 16 16"><path d="M4 12 12 4M5.5 4H12v6.5"/></svg></span>
          </div>
        </div>
      </li>'''

def cards_html(cards,with_hidden=False):
    """Список карточек; with_hidden включает флаг «показывать только по кнопке "Показать ещё"»."""
    return '\n'.join(card_html(c,c.get('extra') and with_hidden) for c in cards)

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

# ---------- главная страница ----------
ld=json.dumps({"@context":"https://schema.org","@type":"ComputerStore","name":"STAR-COMP","url":"https://star-comp.ru","image":"https://star-comp.ru/assets/og-home.jpg","telephone":esc(S.get('phone_schema') or '+7-993-984-55-05'),"email":esc(S.get('email') or 'info@star-comp.ru'),"address":{"@type":"PostalAddress","addressLocality":"Санкт-Петербург","streetAddress":esc(S.get('address_full') or 'Заневский пр., 65 к5, 2 этаж'),"addressCountry":"RU"},"openingHours":esc(S.get('opening_hours_schema') or 'Mo-Su 11:00-19:00'),"sameAs":[v for v in (_soc.get('vk'),_soc.get('telegram')) if v]},ensure_ascii=False,separators=(',',':'))
body=fill_text(_body).replace('{{MENU_LINKS}}',menu_links_html(False))
full=f'''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>STAR-COMP - сборка компьютеров на заказ</title>
<meta name="description" content="Продажа и сборка компьютеров на заказ в Санкт-Петербурге.">
<link rel="canonical" href="https://star-comp.ru">
<meta name="yandex-verification" content="968cf8204a45d4a7">
<meta property="og:url" content="https://star-comp.ru">
<meta property="og:title" content="STAR-COMP - сборка компьютеров на заказ">
<meta property="og:description" content="Продажа и сборка компьютеров на заказ в Санкт-Петербурге.">
<meta property="og:type" content="website">
<meta property="og:locale" content="ru_RU">
<meta property="og:image" content="https://star-comp.ru/assets/og-home.jpg">
<meta name="theme-color" content="#0a0a0a">
<link rel="icon" type="image/svg+xml" href="assets/favicon.svg">
<link rel="apple-touch-icon" href="assets/icon-192.png">
<script type="application/ld+json">{ld.replace('</','<\\/')}</script>
<link rel="preload" href="assets/gilroy-semibold.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/gilroy-regular.woff2" as="font" type="font/woff2" crossorigin>
<style>
{_css}</style>
</head>
<body>
{body.replace('{{CARDS_LIST}}',cards_html(_cards,True)).replace('{{MORE_HIDDEN}}','' if any(c.get('extra') for c in _cards) else ' hidden')}
<script>
{_js}</script>
</body>
</html>
'''
open(os.path.join(ROOT,'index.html'),'w',encoding='utf-8').write(inject_code(full))
frag=f'''<title>STAR-COMP</title>
<meta name="claude:viewport-fit-sides" content="cover">
<style>
{_css}</style>
{body.replace('{{CARDS_LIST}}',cards_html(_cards,True)).replace('{{MORE_HIDDEN}}','' if any(c.get('extra') for c in _cards) else ' hidden')}
<script>
{_js}</script>
'''
os.makedirs(os.path.join(ROOT,'.preview'),exist_ok=True)
open(os.path.join(ROOT,'.preview','star-comp.html'),'w',encoding='utf-8').write(frag)
print(len(full))


def gallery_html(d):
    name=esc(d['name']); slides=[]; dots=[]
    for n,ph in enumerate(d.get('photos') or []):
        stem,ws=derive(ph['image'],[240,640,1024,1600],4/3)
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

def video_html(d):
    v=d.get('video') or {}
    h_id=(v.get('horizontal') or '').strip(); v_id=(v.get('vertical') or '').strip()
    if not (h_id or v_id): return ''
    first=(d.get('photos') or [{}])[0].get('image')
    ch=v.get('cover_h') or v.get('cover_v') or first
    cv=v.get('cover_v') or v.get('cover_h') or first
    if not ch or not cv: return ''
    hs,hw=derive(ch,[640,1280],16/9)
    vs,vw=derive(cv,[480],9/16)
    name=esc(d['name'])
    # Вертикальное видео — узкая колонка (на десктопе справа от текста); обложка тоже вертикальная.
    # Обложка ставится фоном под плеером: пока кадр грузится, видна статичная картинка, а не белый экран.
    if v_id:
        cls=' video video--vertical'
        poster=f"assets/{vs}-{vw[0]}.webp"
        cover=(f'<source type="image/avif" srcset="assets/{vs}-{vw[0]}.avif">'
               f'\n          <img src="{poster}" width="{vw[0]}" height="{round(vw[0]*16/9)}" alt="Смотреть видео о сборке {name}" loading="lazy" decoding="async">')
    else:
        cls=' video'
        h0=hw[0]
        poster=f"assets/{hs}-{h0}.webp"
        cover=(f'<source type="image/avif" srcset="{srcset(hs,hw,"avif")}" sizes="(min-width: 1024px) 1160px, 96vw">'
               f'\n          <img src="assets/{hs}-{h0}.webp" width="{h0}" height="{round(h0*9/16)}" alt="Смотреть видео о сборке {name}" loading="lazy" decoding="async">')
    return f"""      <div class="about__video">
        <div class="{cls}" id="video" data-h="{esc(h_id or v_id)}" data-v="{esc(v_id or h_id)}" data-title="Видео о сборке {name}" style="background:#000 url('{poster}') center/cover no-repeat">
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
    specs='\n'.join(f'      <div><dt>{esc(x["label"]).rstrip(":")}:</dt><dd>{esc(x["value"])}</dd></div>' for x in d.get('specs') or [])
    # Блок «О сборке»: описание и текст рядом с видео (на мобильном — друг под другом)
    lead=f'\n        <p class="section__lead">{txt(d["lead"])}</p>' if d.get('lead') else ''
    about=f'\n        <div class="seo-text"><p>{txt(d["about"])}</p></div>' if d.get('about') else ''
    vid=video_html(d)
    if lead or about or vid:
        has_v=' about--video-v' if 'video--vertical' in vid else (' about--video-h' if vid else '')
        about_section=f'''  <section class="section section--about wrap" aria-label="О сборке">
    <div class="about{has_v}">
      <div class="about__text">{lead}{about}
      </div>
{vid}
    </div>
  </section>'''
    else:
        about_section=''
    return f"""<main>
  <section class="product wrap">
    <div class="product__gallery">
{gallery_html(d)}
    </div>

    <div class="product__info">
      <h1>{name}{sub}</h1>
      <div class="product__cost">
        <p class="product__label">Стоимость:</p>
        <p class="product__price">от&nbsp;{money(d['price'])}</p>
      </div>
      {note}
    </div>
  </section>
{about_section}
  <section class="section section--spec wrap" aria-labelledby="spec-title">
    <h2 class="section__title" id="spec-title">Конфигурация</h2>
    <dl class="spec-grid">
{specs}
    </dl>
{open('inner.flex-note.html',encoding='utf-8').read().rstrip()}
  </section>
</main>"""

src=open('page.body.html',encoding='utf-8').read()
header=src[:src.index('<main>')]
menu=src[src.index('<dialog'):]
def fill(x): return fill_text(x.replace('{{MENU_LINKS}}',menu_links_html(True)).replace('{{LOGO_ICON}}',logo_icon).replace('{{LOGO_WORD}}',logo_word).replace('{{SOCIALS}}',socials).replace('{{SOCIALS_MENU}}',socials.replace('mx-','mxm-')))
header_i=fill(header).replace('<a class="logo" href="/"','<a class="logo" href="index.html"')
menu_i=fill(menu)
menu_js=_js[_js.index("  var menu ="):]
inner_js=open('inner.js',encoding='utf-8').read()
css_i=_css+open('inner.css',encoding='utf-8').read()

def page_html(d):
    slug=d['slug'].strip().strip('/')
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]*',slug): raise SystemExit(f'Плохой адрес страницы: {slug!r} — только латиница, цифры и дефис')
    seo=d.get('seo') or {}
    name=d['name'].strip()
    title=esc(seo.get('title') or (f"{name} — {d['subtitle']}" if d.get('subtitle') else name))
    desc=esc(seo.get('description') or d.get('lead') or d.get('subtitle') or name)
    url=f'https://star-comp.ru/{slug}'
    photos=d.get('photos') or []
    og=og_image(photos[0]['image']) if photos else 'assets/og-home.jpg'
    ld={"@context":"https://schema.org","@type":"Product","name":name,"description":(d.get('lead') or d.get('subtitle') or name),"image":f"https://star-comp.ru/{og}","brand":{"@type":"Brand","name":"STAR-COMP"},"offers":{"@type":"Offer","url":url,"price":str(int(d['price'])),"priceCurrency":"RUB"}}
    return f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{esc(d.get('lead') or desc)}">
<meta property="og:type" content="product">
<meta property="og:locale" content="ru_RU">
<meta property="og:image" content="https://star-comp.ru/{og}">
<meta name="theme-color" content="#0a0a0a">
<link rel="icon" type="image/svg+xml" href="assets/favicon.svg">
<link rel="apple-touch-icon" href="assets/icon-192.png">
<script type="application/ld+json">{json.dumps(ld,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')}</script>
<link rel="preload" href="assets/gilroy-semibold.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/gilroy-regular.woff2" as="font" type="font/woff2" crossorigin>
<style>
:root{{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}}
img{{max-width:100%}}
{css_i}</style>
</head>
<body>
{header_i}
{body_html(d)}

{menu_i}
<script>
{inner_js}
(function () {{
{menu_js}</script>
</body>
</html>
"""

for f in sorted(glob.glob(os.path.join(ROOT,'content','builds','*.json'))):
    d=json.load(open(f,encoding='utf-8'))
    d.setdefault('slug',os.path.splitext(os.path.basename(f))[0])
    out=inject_code(page_html(d))
    open(os.path.join(ROOT,d['slug']+'.html'),'w',encoding='utf-8').write(out)
    print('сборка',d['slug'],len(out))
