# Writes manifest.json for the screens folder: version + SHA-256 of every file. Used by build.sh and publish.py.
import hashlib, json, os, sys
d, ver, min_app = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
files = {}
for root, _, names in os.walk(d):
    for n in names:
        p = os.path.join(root, n); rel = os.path.relpath(p, d).replace(os.sep, '/')
        if rel == 'manifest.json': continue
        files[rel] = hashlib.sha256(open(p, 'rb').read()).hexdigest()
json.dump({'ver': ver, 'minApp': min_app, 'files': dict(sorted(files.items()))}, open(os.path.join(d, 'manifest.json'), 'w'), indent=0)
print('manifest', ver, len(files), 'files')
