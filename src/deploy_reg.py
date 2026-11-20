# Выгрузка готового сайта на боевой хостинг reg.ru по SFTP.
#
# Запускается в GitHub Actions после публикации на GitHub Pages:
#   python src/deploy_reg.py _reg
#
# Правила (по просьбе владельца):
# - заливаем только содержимое _reg/ (готовый сайт, без admin/ и .preview/);
# - старые файлы на сервере НЕ удаляем — только перезаписываем изменившиеся;
# - чтобы не гонять 240 МБ каждый раз, рядом с сайтом хранится маленький
#   файл .deploy-manifest.json с хэшами файлов. Сравниваем хэши и грузим
#   только то, что реально поменялось.
# - самый первый запуск: манифеста ещё нет, поэтому файлы, которые уже
#   лежат на сервере с таким же размером, считаем загруженными и просто
#   запоминаем их хэш. Так первая выгрузка не копирует весь сайт заново.
#
# Параметры подключения берутся из GitHub Secrets:
#   REG_SFTP_SERVER, REG_SFTP_PORT, REG_SFTP_USERNAME,
#   REG_SFTP_PASSWORD, REG_SFTP_DIR
import hashlib
import json
import os
import posixpath
import stat
import sys

import paramiko

MANIFEST = '.deploy-manifest.json'


def secret(name):
    value = os.environ.get(name, '').strip()
    if not value:
        raise SystemExit('Не задан секрет ' + name)
    return value


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def ensure_dir(sftp, remote_dir):
    current = ''
    for part in [p for p in remote_dir.split('/') if p]:
        current = current + '/' + part if current else part
        try:
            info = sftp.stat(current)
            if not stat.S_ISDIR(info.st_mode):
                raise SystemExit('На сервере файл вместо папки: ' + current)
        except IOError:
            sftp.mkdir(current)


def main():
    local_root = sys.argv[1] if len(sys.argv) > 1 else '_reg'
    if not os.path.isdir(local_root):
        raise SystemExit('Нет папки ' + local_root)

    server = secret('REG_SFTP_SERVER')
    port = int(secret('REG_SFTP_PORT'))
    username = secret('REG_SFTP_USERNAME')
    password = secret('REG_SFTP_PASSWORD')
    server_dir = secret('REG_SFTP_DIR').strip().strip('/')

    local = {}
    sizes = {}
    for dirpath, dirnames, filenames in os.walk(local_root):
        dirnames.sort()
        filenames.sort()
        for name in filenames:
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, local_root).replace(os.sep, '/')
            local[rel] = sha256(full)
            sizes[rel] = os.path.getsize(full)

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, port=port, username=username, password=password,
                   timeout=30, allow_agent=False, look_for_keys=False)
    sftp = client.open_sftp()

    ensure_dir(sftp, server_dir)
    manifest_path = posixpath.join(server_dir, MANIFEST)

    try:
        with sftp.open(manifest_path, 'r') as f:
            old = json.loads(f.read().decode('utf-8'))
        if not isinstance(old, dict):
            old = {}
        have_manifest = True
    except (IOError, ValueError):
        old = {}
        have_manifest = False

    def remote_size(rel):
        try:
            return sftp.stat(posixpath.join(server_dir, rel)).st_size
        except IOError:
            return None

    changed = []
    for rel, digest in sorted(local.items()):
        if old.get(rel) == digest:
            continue
        if not have_manifest and remote_size(rel) == sizes[rel]:
            # файл уже есть на сервере и того же размера — не трогаем
            continue
        changed.append(rel)

    print('Файлов в сборке: {}'.format(len(local)), flush=True)
    print('К загрузке: {}'.format(len(changed)), flush=True)

    for i, rel in enumerate(changed, 1):
        remote = posixpath.join(server_dir, rel)
        parent = posixpath.dirname(remote)
        if parent and parent != server_dir:
            ensure_dir(sftp, parent)
        sftp.put(os.path.join(local_root, rel.replace('/', os.sep)), remote)
        if i % 25 == 0 or i == len(changed):
            print('  загружено {}/{}'.format(i, len(changed)), flush=True)

    # манифест пишем последним: если заливка прервётся, следующий запуск
    # повторит незагруженные файлы
    with sftp.open(manifest_path, 'w') as f:
        f.write(json.dumps(local, sort_keys=True).encode('utf-8'))

    print('Загружено всего: {}'.format(len(changed)), flush=True)
    for rel in changed[:30]:
        print('  + ' + rel, flush=True)
    if len(changed) > 30:
        print('  ... и ещё {}'.format(len(changed) - 30), flush=True)
    print('Старые файлы на сервере не удалялись.', flush=True)

    sftp.close()
    client.close()


if __name__ == '__main__':
    main()
