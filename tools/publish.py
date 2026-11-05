#!/usr/bin/env python3
"""Publish a Mao update to GitHub (sanctumares1-svg/mao).

  python3 publish.py web "Что нового"   — new screens only (design, writing, texts, dictionary).
                                           Phones download it quietly and switch on «Перезапустить» / next start.
  python3 publish.py app "Что нового"   — after build.sh: a new APK (Android part changed: icon, splash, permissions…).
                                           Phones show «Доступна версия X · Обновить».
"""
import json, os, re, shutil, subprocess, sys, hashlib
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.environ.get('MAO_REPO', '/home/claude/mao')
WWW = os.path.join(HERE, 'www')
FILES = ['index.html', 'react.js', 'native.js', 'dict.js', 'writecheck.js', 'strokes.txt', 'topics.txt', 'support.js', 'fonts.css', 'dict.txt', 'explain.js', 'decomp.txt']
BUILD = open(os.path.join(HERE, 'android', 'build.sh'), encoding='utf8').read()
CODE = int(re.search(r'android:versionCode="(\d+)"', BUILD).group(1))
NAME = re.search(r'android:versionName="([^"]+)"', BUILD).group(1)

def git(*a): subprocess.run(['git', '-C', REPO] + list(a), check=True)
def sha(p): return hashlib.sha256(open(p, 'rb').read()).hexdigest()

def copy_web(ver):
    dst = os.path.join(REPO, 'web')
    shutil.rmtree(dst, ignore_errors=True); os.makedirs(dst)
    for f in FILES: shutil.copy2(os.path.join(WWW, f), dst)
    shutil.copytree(os.path.join(WWW, 'fonts'), os.path.join(dst, 'fonts'))
    files = {}
    for root, _, names in os.walk(dst):
        for n in names:
            p = os.path.join(root, n); files[os.path.relpath(p, dst).replace(os.sep, '/')] = sha(p)
    return dict(sorted(files.items()))

def main():
    kind, notes = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else '')
    upath = os.path.join(REPO, 'update.json')
    u = json.load(open(upath, encoding='utf8')) if os.path.exists(upath) else {}
    vfile = os.path.join(HERE, 'webver.txt')
    ver = int(open(vfile).read().strip())
    if kind == 'web':
        ver += 1                                     # screens get a new number; the APK inside phones stays
        open(vfile, 'w').write(str(ver))
    files = copy_web(ver)
    u['web'] = {'ver': ver, 'tag': f'web-{ver}', 'minApp': CODE, 'notes': notes if kind == 'web' else (u.get('web', {}).get('notes', '')), 'files': files}
    tags = [f'web-{ver}']
    if kind == 'app':
        apk = os.path.join(HERE, 'android', 'out', 'EVINE.apk')
        os.makedirs(os.path.join(REPO, 'apk'), exist_ok=True)
        shutil.copy2(apk, os.path.join(REPO, 'apk', 'Mao.apk'))
        u['app'] = {'code': CODE, 'name': NAME, 'tag': f'app-{CODE}', 'path': 'apk/Mao.apk', 'notes': notes}
        tags.append(f'app-{CODE}')
    json.dump(u, open(upath, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    git('add', '-A')
    git('commit', '-m', f'Mao {NAME}: ' + (f'экраны {ver}' if kind == 'web' else f'приложение {NAME} (код {CODE})') + (f' — {notes}' if notes else ''))
    existing = subprocess.run(['git', '-C', REPO, 'tag'], capture_output=True, text=True).stdout.split()
    for t in tags:
        if t not in existing: git('tag', t)
    if os.environ.get('NOPUSH')!='1':
        git('push', 'origin', 'HEAD:main')
        git('push', 'origin', *[t for t in tags if t not in existing] or ['--tags'])
    print('published', kind, 'web', ver, 'app', CODE, NAME)

if __name__ == '__main__':
    main()
