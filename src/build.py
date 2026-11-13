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

# ---------- внутренняя страница сборки ----------
src=open('page.body.html',encoding='utf-8').read()
header=src[:src.index('<main>')]
menu=src[src.index('<dialog'):]
def fill(x): return x.replace('{{LOGO_ICON}}',logo_icon).replace('{{LOGO_WORD}}',logo_word).replace('{{SOCIALS}}',socials).replace('{{SOCIALS_MENU}}',socials.replace('mx-','mxm-'))
header_i=fill(header).replace('<a class="logo" href="/"','<a class="logo" href="index.html"')
menu_i=re.sub(r'href="#(works|nal|ychit|lastvid|preim|proces|gift|otzivy|contakty)"',r'href="index.html#\1"',fill(menu))
menu_js=js[js.index("  var menu ="):]
inner_js=open('inner.js',encoding='utf-8').read()
css_i=css+open('inner.css',encoding='utf-8').read()
inner=f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>SOLAR S1 — игровой компьютер на INTEL CORE i5-12400F и NVIDIA RTX 5050 8GB</title>
<meta name="description" content="Игровой компьютер SOLAR S1: INTEL CORE i5-12400F, NVIDIA RTX 5050 8GB, 16GB DDR4, SSD M.2. Цена от 121 000 ₽. Сборка на заказ в Санкт-Петербурге: привезём, подключим и настроим, оплата после проверки.">
<link rel="canonical" href="https://star-comp.ru/solar-s1-intel-core-i5-12400f-nvidia-rtx-5060-8gb">
<meta property="og:url" content="https://star-comp.ru/solar-s1-intel-core-i5-12400f-nvidia-rtx-5060-8gb">
<meta property="og:title" content="SOLAR S1 — игровой компьютер на INTEL CORE i5-12400F и NVIDIA RTX 5050 8GB">
<meta property="og:description" content="Оптимальная сборка цена/качество для всех игр на высоких настройках.">
<meta property="og:type" content="product">
<meta property="og:locale" content="ru_RU">
<meta property="og:image" content="https://star-comp.ru/assets/og-solar-s1.jpg">
<meta name="theme-color" content="#0a0a0a">
<link rel="icon" type="image/svg+xml" href="assets/favicon.svg">
<link rel="apple-touch-icon" href="assets/icon-192.png">
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"Product","name":"SOLAR S1","description":"Оптимальная сборка цена/качество для всех игр на высоких настройках","image":"https://star-comp.ru/assets/og-solar-s1.jpg","brand":{{"@type":"Brand","name":"STAR-COMP"}},"offers":{{"@type":"Offer","url":"https://star-comp.ru/solar-s1-intel-core-i5-12400f-nvidia-rtx-5060-8gb","price":"121000","priceCurrency":"RUB"}}}}</script>
<link rel="preload" href="assets/gilroy-semibold.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/gilroy-regular.woff2" as="font" type="font/woff2" crossorigin>
<style>
:root{{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}}
img{{max-width:100%}}
{css_i}</style>
</head>
<body>
{header_i}
{open('inner.body.html',encoding='utf-8').read()}
{menu_i}
<script>
{inner_js}
(function () {{
{menu_js}</script>
</body>
</html>
"""
open(os.path.join(ROOT,'solar-s1-intel-core-i5-12400f-nvidia-rtx-5060-8gb.html'),'w',encoding='utf-8').write(inner)
print('inner',len(inner))
