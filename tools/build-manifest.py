#!/usr/bin/env python3
"""Build immutable NuPhy Inspired theme and comparison releases."""
import hashlib
import json
import os
from pathlib import Path

root = Path(__file__).resolve().parents[1]
repository = os.environ.get('GITHUB_REPOSITORY', 'anti-ltd/clink-themes-nuphy')
metadata = json.loads((root / 'comparisons.json').read_text())
files = sorted(p for folder in ['Themes', 'Images'] for p in (root / folder).iterdir()
               if p.is_file() and not p.name.startswith('.'))
themes = [p for p in files if p.suffix == '.clinktheme']
if set(metadata) != {p.stem for p in themes}:
    raise SystemExit('Each theme must have exactly one comparisons.json entry')
identity = [(str(p.relative_to(root)), hashlib.sha256(p.read_bytes()).hexdigest()) for p in files]
identity.append(('comparisons.json', hashlib.sha256((root / 'comparisons.json').read_bytes()).hexdigest()))
version = 'themes-' + hashlib.sha256(json.dumps(identity, separators=(',', ':')).encode()).hexdigest()
base = f'https://github.com/{repository}/releases/download/{version}'
entries = []
for path in themes:
    raw = path.read_bytes()
    theme = json.loads(raw)
    if theme['id'] != path.stem or not theme['name'].startswith('NuPhy Inspired '):
        raise SystemExit(f'{path.name}: preserve the theme ID and NuPhy Inspired label')
    if len(raw) > 128_000:
        raise SystemExit(f'{path.name}: theme exceeds app size limit')
    reference = metadata[path.stem]
    comparison = {'model': reference['model']}
    for field in ['keyboardImage', 'themeImage']:
        name = reference[field]
        if Path(name).name != name or not (root / 'Images' / name).is_file():
            raise SystemExit(f'{path.name}: missing comparison image {name}')
        comparison[field] = f'{base}/{name}'
    entries.append({'id':theme['id'], 'name':theme['name'], 'version':version,
                    'preview':theme, 'link':'https://nuphy.com/', 'comparison':comparison,
                    'asset':{'path':path.name, 'url':f'{base}/{path.name}',
                             'sha256':hashlib.sha256(raw).hexdigest(), 'byteCount':len(raw)}})
(root / 'manifest.json').write_text(json.dumps({'version':version,'themes':entries}, indent=2)+'\n')
print(f'{len(entries)} NuPhy Inspired themes · {version}')
