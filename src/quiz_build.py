"""Квиз «Подобрать компьютер»: шаги из content/quiz/*.json → assets/quiz-data.js.

Движок (src/quiz.js) и стили (src/quiz.css) копируются в assets/.
Шаги редактирует владелец в админке, вкладка «Квиз».
"""
import glob
import json
import os
import shutil

import thanks_build

TYPES = {'choice', 'text', 'slider', 'phone', 'login'}


def _str(d, key):
    return str(d.get(key) or '').strip()


def _load(root):
    steps = []
    for path in glob.glob(os.path.join(root, 'content', 'quiz', '*.json')):
        with open(path, encoding='utf-8') as f:
            d = json.load(f)
        step = {
            'id': _str(d, 'id'),
            'order': d.get('order') or 0,
            'type': _str(d, 'type') or 'choice',
            'style': _str(d, 'style'),
            'title': _str(d, 'title'),
            'hint': _str(d, 'hint'),
            'notice': _str(d, 'notice'),
            'button': _str(d, 'button'),
            'next': _str(d, 'next'),
            'slider': d.get('slider') or None,
            'options': [
                {
                    'label': _str(o, 'label'),
                    'note': _str(o, 'note'),
                    'icon': _str(o, 'icon'),
                    'next': _str(o, 'next'),
                }
                for o in (d.get('options') or []) if _str(o, 'label')
            ],
        }
        if not step['id'] or not step['title']:
            print('квиз: пропущен шаг без id или заголовка:', os.path.basename(path))
            continue
        if step['type'] not in TYPES:
            print('квиз: неизвестный тип шага', step['id'], step['type'])
        steps.append(step)
    steps.sort(key=lambda s: (s['order'], s['id']))
    return steps


def build(root):
    steps = _load(root)
    ids = {s['id'] for s in steps}
    for s in steps:
        for target in [s['next']] + [o['next'] for o in s['options']]:
            if target and target not in ids:
                print('квиз: шаг', s['id'], 'ведёт в несуществующий шаг', target)
    if not steps:
        print('квиз: шагов нет, блок квиза пустой')

    data = json.dumps(steps, ensure_ascii=False, indent=1)
    os.makedirs(os.path.join(root, 'assets'), exist_ok=True)
    thanks = thanks_build.load(root)['slug']
    with open(os.path.join(root, 'assets', 'quiz-data.js'), 'w', encoding='utf-8') as f:
        f.write('window.QUIZ_STEPS = ' + data + ';\n')
        f.write('window.QUIZ_THANKS_URL = ' + json.dumps(thanks) + ';\n')
    shutil.copyfile(os.path.join(root, 'src', 'quiz.js'), os.path.join(root, 'assets', 'quiz.js'))
    shutil.copyfile(os.path.join(root, 'src', 'quiz.css'), os.path.join(root, 'assets', 'quiz.css'))
    print('квиз: шагов', len(steps))


def test_block(stamp):
    return (
        f'<link rel="stylesheet" href="assets/quiz.css?v={stamp}">\n'
        '<section class="wrap" style="padding-block:3rem;text-align:center">\n'
        '  <button type="button" class="quiz-open" data-quiz-open>Подобрать компьютер</button>\n'
        '</section>\n'
        f'<script src="assets/quiz-data.js?v={stamp}"></script>\n'
        f'<script src="assets/quiz.js?v={stamp}"></script>\n'
    )
