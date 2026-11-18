# Переименование загруженных фото: <слаг папки>_<номер>.<расширение>
#
# Зачем: фото загружаются в админке с любыми именами (IMG_1234.webp, «1-водопад.webp»).
# Этот скрипт перед сборкой приводит их к единому виду: имя папки + номер,
# например папка «TITAN R2» → titan_r2_1.webp, titan_r2_2.webp …
#
# Правила:
# - слаг = имя папки: кириллица → латиница, пробелы/точки/прочие знаки → «_», всё строчными;
# - файлы, уже названные правильно (<слаг>_<номер> или <слаг>-<номер>), не трогаем,
#   их номера сохраняются; остальные получают свободные номера по порядку;
# - ссылки в content/*.json на переименованные файлы обновляются автоматически;
# - если переименовывать нечего, скрипт молча ничего не делает (запуск каждый раз безопасен).
#
# Запускается в .github/workflows/build.yml до src/build.py. Ручной запуск:
#   python src/rename_photos.py [--dry-run]
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PHOTOS = os.path.join(ROOT, 'content', 'photos')
IMG_EXT = {'.webp', '.jpg', '.jpeg', '.png', '.avif', '.gif', '.jfif', '.bmp'}

# Транслитерация кириллицы для слага
_T = {'а':'a','б':'b','в':'v','г':'g','д':'d','е':'e','ё':'yo','ж':'zh','з':'z','и':'i',
      'й':'y','к':'k','л':'l','м':'m','н':'n','о':'o','п':'p','р':'r','с':'s','т':'t',
      'у':'u','ф':'f','х':'h','ц':'c','ч':'ch','ш':'sh','щ':'sch','ъ':'','ы':'y','ь':'',
      'э':'e','ю':'yu','я':'ya'}

def slugify(name):
    """«TITAN R2» → titan_r2; «06.11.2026_15805_cryo_m1» → 06_11_2026_15805_cryo_m1."""
    s = name.strip().lower()
    s = ''.join(_T.get(ch, ch) for ch in s)
    s = re.sub(r'[^a-z0-9_-]+', '_', s)   # любые прочие знаки → _
    s = re.sub(r'_+', '_', s).strip('_')  # схлопнуть повторы _
    return s or 'photos'

def natural_key(s):
    """Сортировка по-человечески: 2.webp раньше 10.webp."""
    return [int(p) if p.isdigit() else p for p in re.split(r'(\d+)', s.lower())]

def plan_folder(fdir, folder):
    """Возвращает [(старое_имя, новое_имя)] для файлов, которые надо переименовать."""
    slug = slugify(folder)
    stable, unstable = {}, []
    for fname in os.listdir(fdir):
        ext = os.path.splitext(fname)[1].lower()
        if ext not in IMG_EXT:
            continue  # .gitkeep и прочее не трогаем
        stem = fname[:-len(ext)]
        m = re.fullmatch(re.escape(slug) + r'[_-](\d+)', stem)
        if m and int(m.group(1)) not in stable:
            stable[int(m.group(1))] = fname  # уже назван верно — номер занят
        else:
            unstable.append(fname)
    if not unstable:
        return []
    unstable.sort(key=natural_key)
    used = set(stable)
    out = []
    for fname in unstable:
        n = 1
        while n in used:
            n += 1
        used.add(n)
        ext = os.path.splitext(fname)[1].lower()
        out.append((fname, f'{slug}_{n}{ext}'))
    return out

def update_json_refs(renames):
    """Заменяет старые пути на новые во всех content/*.json. Пути хранятся со слэшем: /content/photos/…"""
    changed = []
    for dirpath, _, files in os.walk(os.path.join(ROOT, 'content')):
        for f in files:
            if not f.endswith('.json'):
                continue
            p = os.path.join(dirpath, f)
            with open(p, encoding='utf-8') as fh:
                text = fh.read()
            new_text = text
            for old, new in renames.items():
                new_text = new_text.replace('/' + old, '/' + new).replace(old, new)
            if new_text != text:
                with open(p, 'w', encoding='utf-8', newline='') as fh:
                    fh.write(new_text)
                changed.append(os.path.relpath(p, ROOT))
    return changed

def main():
    dry = '--dry-run' in sys.argv
    rel = lambda d, f: '/'.join(('content/photos', d, f))
    renames = {}
    if os.path.isdir(PHOTOS):
        # Правило: две папки с одинаковым слагом (например, «TITAN R2» и «titan r2»)
        # это дубль — переименование в них пропускается, чтобы фото двух сборок
        # не смешались в одну кучу. Оставьте одну папку, вторую удалите.
        slugs = {}
        for folder in sorted(os.listdir(PHOTOS)):
            fdir = os.path.join(PHOTOS, folder)
            if os.path.isdir(fdir):
                slugs.setdefault(slugify(folder), []).append(folder)
        for slug, folders in sorted(slugs.items()):
            if len(folders) > 1:
                print(f'ВНИМАНИЕ: папки {", ".join(folders)} дают один слаг «{slug}» — это дубли.')
                print('  Переименование в этих папках пропущено, чтобы фото не смешались.')
                print('  Оставьте одну папку, остальные удалите (или переименуйте по-другому).')
        for folder in sorted(os.listdir(PHOTOS)):
            fdir = os.path.join(PHOTOS, folder)
            # дубли (папки с одинаковым слагом) пропускаем — см. предупреждение выше
            if os.path.isdir(fdir) and len(slugs[slugify(folder)]) == 1:
                for old, new in plan_folder(fdir, folder):
                    renames[rel(folder, old)] = rel(folder, new)
    if not renames:
        return
    for old in sorted(renames, key=natural_key):
        print('rename:', old, '->', renames[old])
    json_changed = update_json_refs(renames)
    for j in json_changed:
        print('refs updated:', j)
    if dry:
        print('dry-run: реальные изменения не записаны')
        return
    # Переименование в два прохода, чтобы не было конфликтов имён
    tmp = {old: old + '.renaming' for old in renames}
    for old, t in tmp.items():
        os.rename(os.path.join(ROOT, *old.split('/')), os.path.join(ROOT, *t.split('/')))
    for old, new in renames.items():
        os.rename(os.path.join(ROOT, *tmp[old].split('/')), os.path.join(ROOT, *new.split('/')))

if __name__ == '__main__':
    main()
