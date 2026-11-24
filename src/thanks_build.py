"""Страница «Спасибо» после отправки заявки из квиза.

Тексты и адрес страницы — content/thanks.json (правится в админке, вкладка «Страница спасибо»).
Сборщик пишет <адрес>.html в корень сайта. Если адрес поменяли, старый файл страницы
удаляется: такие файлы помечены мета-тегом thanks-page.
"""
import glob
import html
import json
import os

MARK = '<meta name="thanks-page" content="1">'


def load(root):
    path = os.path.join(root, 'content', 'thanks.json')
    with open(path, encoding='utf-8') as f:
        d = json.load(f)
    slug = (d.get('slug') or 'spasibo').strip().strip('/').replace('.html', '') or 'spasibo'
    return {
        'slug': slug,
        'title': (d.get('title') or 'Спасибо!').strip(),
        'text': (d.get('text') or '').strip(),
        'button': (d.get('button') or 'Назад').strip(),
        'fallback': (d.get('fallback_url') or '/').strip(),
    }


PAGE = '''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title} — STAR-COMP</title>
<meta name="robots" content="noindex, nofollow">
{mark}
<meta name="theme-color" content="#0a0a0c">
<style>
:root{{color-scheme:dark}}
*{{box-sizing:border-box}}
html,body{{margin:0;min-height:100%}}
body{{min-height:100svh;display:flex;align-items:center;justify-content:center;padding:24px;background:#0a0a0c;color:#fff;font-family:Gilroy,Arial,sans-serif;text-align:center}}
.box{{width:min(100%,560px)}}
.logo{{margin:0 0 24px;font-size:14px;font-weight:600;letter-spacing:.16em;color:#bdbdc2}}
h1{{margin:0 0 16px;font-size:32px;line-height:1.2}}
p.lead{{margin:0 auto 32px;max-width:34rem;color:#bdbdc2;font-size:16px;line-height:1.5}}
.btn{{display:inline-flex;align-items:center;justify-content:center;gap:.5rem;min-height:52px;padding:12px 28px;border:0;border-radius:100px;background:#00d9ff;color:#0a0a0c;font:600 18px/1.2 Gilroy,Arial,sans-serif;text-decoration:none;cursor:pointer;transition:transform .2s}}
@media (hover:hover){{.btn:hover{{transform:translateY(-2px)}}}}
@media (max-width:480px){{h1{{font-size:26px}}}}
</style>
</head>
<body>
<main class="box">
  <p class="logo">STAR-COMP</p>
  <h1>{title}</h1>
  <p class="lead">{text}</p>
  <a class="btn" id="back-link" href="{fallback}">{button} <span aria-hidden="true">&larr;</span></a>
</main>
<script>
(function(){{
  var link=document.getElementById('back-link');
  link.addEventListener('click',function(e){{
    if(history.length>1){{e.preventDefault();history.back();}}
  }});
}})();
</script>
</body>
</html>
'''


def build(root, inject_code):
    cfg = load(root)
    page = PAGE.format(
        title=html.escape(cfg['title']),
        text=html.escape(cfg['text']),
        button=html.escape(cfg['button']),
        fallback=html.escape(cfg['fallback'], quote=True),
        mark=MARK,
    )
    for old in glob.glob(os.path.join(root, '*.html')):
        name = os.path.splitext(os.path.basename(old))[0]
        with open(old, encoding='utf-8') as f:
            text = f.read()
        if MARK in text and name != cfg['slug']:
            os.remove(old)
            print('страница спасибо: удалён старый адрес', name + '.html')
    with open(os.path.join(root, cfg['slug'] + '.html'), 'w', encoding='utf-8') as f:
        f.write(inject_code(page))
    print('страница спасибо', cfg['slug'] + '.html')
