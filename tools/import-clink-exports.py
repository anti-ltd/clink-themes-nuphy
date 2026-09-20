#!/usr/bin/env python3
"""Import JSON attachments exported by Clink's NuPhyThemeReviewTests."""
import argparse
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('attachments', type=Path, help='xcresulttool export attachments output directory')
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
expected = set(json.loads((root/'comparisons.json').read_text()))
documents = {}
for path in args.attachments.glob('*.clinktheme'):
    if path.name.startswith('.'):
        continue
    raw = path.read_bytes()
    theme = json.loads(raw)
    if theme['id'] in expected:
        if not theme['name'].startswith('NuPhy Inspired '):
            raise SystemExit('Exported theme names must start with NuPhy Inspired')
        documents[theme['id']] = raw
if set(documents) != expected:
    raise SystemExit(f'Missing theme exports: {sorted(expected-set(documents))}')
for theme_id, raw in documents.items():
    (root/'Themes'/f'{theme_id}.clinktheme').write_bytes(raw)
print(f'Imported {len(documents)} NuPhy Inspired theme documents')
