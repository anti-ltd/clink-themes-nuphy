import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

class ManifestTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        source = Path(__file__).resolve().parents[1]
        for folder in ['Themes', 'Images', 'tools']:
            shutil.copytree(source / folder, self.root / folder, ignore=shutil.ignore_patterns('._*', '__pycache__'))
        shutil.copyfile(source / 'comparisons.json', self.root / 'comparisons.json')

    def build(self):
        subprocess.run([sys.executable, str(self.root/'tools/build-manifest.py')], check=True,
                       env={**os.environ, 'GITHUB_REPOSITORY':'example/themes'}, capture_output=True)
        return json.loads((self.root/'manifest.json').read_text())

    def test_all_themes_and_artwork_match_release(self):
        manifest = self.build()
        self.assertEqual(len(manifest['themes']), 17)
        for entry in manifest['themes']:
            raw = (self.root/'Themes'/entry['asset']['path']).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), entry['asset']['sha256'])
            self.assertEqual(len(raw), entry['asset']['byteCount'])
            self.assertEqual(json.loads(raw), entry['preview'])
            self.assertTrue(entry['name'].startswith('NuPhy Inspired '))
            self.assertEqual(entry['link'], 'https://nuphy.com/')
            prefix = f'https://github.com/example/themes/releases/download/{manifest["version"]}/'
            self.assertTrue(entry['asset']['url'].startswith(prefix))
            for key in ['keyboardImage', 'themeImage']:
                url = entry['comparison'][key]
                self.assertTrue(url.startswith(prefix))
                self.assertTrue((self.root/'Images'/url.removeprefix(prefix)).is_file())

    def test_artwork_and_metadata_changes_create_new_release(self):
        first = self.build()
        photo = next((self.root/'Images').glob('*.jpg'))
        photo.write_bytes(photo.read_bytes()+b'changed')
        second = self.build()
        self.assertNotEqual(first['version'], second['version'])
        metadata = json.loads((self.root/'comparisons.json').read_text())
        metadata[next(iter(metadata))]['model'] += ' revised'
        (self.root/'comparisons.json').write_text(json.dumps(metadata))
        self.assertNotEqual(second['version'], self.build()['version'])

    def test_repeat_builds_ignore_appledouble(self):
        first = self.build()
        (self.root/'Images/._junk').write_bytes(b'junk')
        self.assertEqual(first, self.build())

    def test_missing_image_fails(self):
        next((self.root/'Images').glob('*.jpg')).unlink()
        with self.assertRaises(subprocess.CalledProcessError):
            self.build()
