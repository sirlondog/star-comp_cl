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
socials=f'''<a class="social" href="https://max.ru/u/f9LHodD0cOKrboX3imjyg3cBiLspEiRa0Yz4Pb8i89Zd2AoqQNLb-lqSCpU" target="_blank" rel="noopener" aria-label="Написать в MAX">{max_svg}</a>
<a class="social" href="https://t.me/ST_COMP" target="_blank" rel="noopener" aria-label="Написать в Telegram">{tg_svg}</a>
<a class="social" href="https://vk.com/star_comp_spb" target="_blank" rel="noopener" aria-label="Группа ВКонтакте">{vk_svg}</a>'''

css=open('page.css',encoding='utf-8').read()
body=open('page.body.html',encoding='utf-8').read()
body=body.replace('{{LOGO_ICON}}',logo_icon).replace('{{LOGO_WORD}}',logo_word).replace('{{SOCIALS}}',socials).replace('{{SOCIALS_MENU}}',socials.replace('mx-','mxm-'))
js=open('page.js',encoding='utf-8').read()

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
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"ComputerStore","name":"STAR-COMP","url":"https://star-comp.ru","image":"https://star-comp.ru/assets/og-home.jpg","telephone":"+7-993-984-55-05","email":"info@star-comp.ru","address":{{"@type":"PostalAddress","addressLocality":"Санкт-Петербург","streetAddress":"Заневский пр., 65 к5, 2 этаж","addressCountry":"RU"}},"openingHours":"Mo-Su 11:00-19:00","sameAs":["https://vk.com/star_comp_spb","https://t.me/ST_COMP"]}}</script>
<link rel="preload" href="assets/gilroy-semibold.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/gilroy-regular.woff2" as="font" type="font/woff2" crossorigin>
<style>
{css}</style>
</head>
<body>
{body}
<script>
{js}</script>
</body>
</html>
'''
open(os.path.join(ROOT,'index.html'),'w',encoding='utf-8').write(full)
frag=f'''<title>STAR-COMP</title>
<meta name="claude:viewport-fit-sides" content="cover">
<style>
{css}</style>
{body}
<script>
{js}</script>
'''
os.makedirs(os.path.join(ROOT,'.preview'),exist_ok=True)
open(os.path.join(ROOT,'.preview','star-comp.html'),'w',encoding='utf-8').write(frag)
print(len(full))

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
def og_image(src):
    path=os.path.join(ROOT,src.lstrip('/'))
    stem=os.path.splitext(os.path.basename(path))[0]
    out=os.path.join(ROOT,'assets',f'{stem}-og.jpg')
    if not os.path.exists(out):
        ImageOps.fit(ImageOps.exif_transpose(Image.open(path)).convert('RGB'),(1200,630),Image.LANCZOS).save(out,quality=82,optimize=True,progressive=True)
    return f'assets/{stem}-og.jpg'
def srcset(stem,ws,ext): return ', '.join(f'assets/{stem}-{w}.{ext} {w}w' for w in ws)

SIZES='(min-width: 1920px) 60vw, (min-width: 1024px) min(1160px, calc((100vh - 264px) * 1.34)), (min-width: 608px) 576px, calc(100vw - 32px)'
ARROW_L='<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M10 3 5 8l5 5"/></svg>'
ARROW_R='<svg viewBox="0 0 16 16" aria-hidden="true"><path d="m6 3 5 5-5 5"/></svg>'

def gallery_html(d):
    name=esc(d['name']); slides=[]; thumbs=[]
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
        t=ws[0]
        cur=' aria-current="true"' if n==0 else ''
        thumbs.append(f'        <button type="button" aria-label="Фото {n+1}: {alt}"{cur}><picture><source type="image/avif" srcset="assets/{stem}-{t}.avif"><img src="assets/{stem}-{t}.webp" width="240" height="180" alt="" decoding="async"></picture></button>')
    nl='\n'
    return f"""    <div class="gallery" id="gallery">
      <div class="gallery__stage">
      <ul class="gallery__track" tabindex="0" aria-label="Фотографии сборки. Нажмите, чтобы увеличить">
{nl.join(slides)}
      </ul>
      <button class="gallery__nav gallery__nav--prev" type="button" aria-label="Предыдущее фото">{ARROW_L}</button>
      <button class="gallery__nav gallery__nav--next" type="button" aria-label="Следующее фото">{ARROW_R}</button>
      </div>
      <div class="gallery__thumbs">
{nl.join(thumbs)}
      </div>
    </div>"""

def video_html(d):
    v=d.get('video') or {}
    h_id=(v.get('horizontal') or '').strip(); v_id=(v.get('vertical') or '').strip()
    if not (h_id or v_id): return ''
    first=(d.get('photos') or [{}])[0].get('image')
    ch=v.get('cover_h') or v.get('cover_v') or first
    cv=v.get('cover_v') or v.get('cover_h') or first
    if not ch: return ''
    hs,hw=derive(ch,[640,1280],16/9)
    vs,vw=derive(cv,[480],9/16)
    name=esc(d['name'])
    return f"""
  <section class="section wrap" aria-label="Видео">
    <div class="video" id="video" data-h="{esc(h_id or v_id)}" data-v="{esc(v_id or h_id)}" data-title="Видео о сборке {name}">
      <button class="video__play" type="button">
        <picture>
          <source media="(min-width: 1024px)" type="image/avif" srcset="{srcset(hs,hw,'avif')}" sizes="(min-width: 1240px) 1160px, 96vw">
          <source media="(min-width: 1024px)" type="image/webp" srcset="{srcset(hs,hw,'webp')}" sizes="(min-width: 1240px) 1160px, 96vw">
          <source type="image/avif" srcset="assets/{vs}-{vw[0]}.avif">
          <img src="assets/{vs}-{vw[0]}.webp" width="480" height="853" alt="Смотреть видео о сборке {name}" loading="lazy" decoding="async">
        </picture>
        <span class="video__icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M8 5.5v13l11-6.500z"/></svg></span>
      </button>
    </div>
  </section>
"""

def body_html(d):
    name=esc(d['name'])
    sub=f' <i class="sr-only">— </i><span>{txt(d["subtitle"])}</span>' if d.get('subtitle') else ''
    note=f'\n      <p class="product__note">{txt(d["note"])}</p>' if d.get('note') else ''
    lead=f'\n    <p class="section__lead">{txt(d["lead"])}</p>' if d.get('lead') else ''
    specs='\n'.join(f'      <div><dt>{esc(x["label"]).rstrip(":")}:</dt><dd>{esc(x["value"])}</dd></div>' for x in d.get('specs') or [])
    return f"""<main>
  <section class="product wrap">
{gallery_html(d)}

    <div class="product__info">
      <div class="product__row">
      <h1>{name}{sub}</h1>
      <div class="product__cost">
        <p class="product__label">Стоимость на момент сборки:</p>
        <p class="product__price">{money(d['price'])}</p>
      </div>
      </div>
      <div class="product__row product__row--buy">{note}
      <a class="btn" href="#podbor">Заказать компьютер</a>
      </div>
    </div>
  </section>
{video_html(d)}
  <section class="section wrap" aria-labelledby="spec-title">
    <h2 class="section__title" id="spec-title">Конфигурация {name}</h2>{lead}
    <dl class="spec-grid">
{specs}
    </dl>
{open('inner.flex-note.html',encoding='utf-8').read().rstrip()}
  </section>
{open('inner.other-builds.html',encoding='utf-8').read().rstrip()}
</main>"""

src=open('page.body.html',encoding='utf-8').read()
header=src[:src.index('<main>')]
menu=src[src.index('<dialog'):]
def fill(x): return x.replace('{{LOGO_ICON}}',logo_icon).replace('{{LOGO_WORD}}',logo_word).replace('{{SOCIALS}}',socials).replace('{{SOCIALS_MENU}}',socials.replace('mx-','mxm-'))
header_i=fill(header).replace('<a class="logo" href="/"','<a class="logo" href="index.html"')
menu_i=re.sub(r'href="#(works|nal|ychit|lastvid|preim|proces|gift|otzivy|contakty)"',r'href="index.html#\1"',fill(menu))
menu_js=js[js.index("  var menu ="):]
inner_js=open('inner.js',encoding='utf-8').read()
css_i=css+open('inner.css',encoding='utf-8').read()

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
    out=page_html(d)
    open(os.path.join(ROOT,d['slug']+'.html'),'w',encoding='utf-8').write(out)
    print('сборка',d['slug'],len(out))
