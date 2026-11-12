"""Create reproducible Chinese/English source ZIPs from committed files only."""
from pathlib import Path
import argparse
import hashlib
import io
import json
import re
import subprocess
import sys
import tarfile
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def package(output):
    manifest = (ROOT / 'manifest.xml').read_text(encoding='utf-8')
    version = re.search(r'minApiLevel="[^"]+" version="([^"]+)"', manifest).group(1)
    output.mkdir(parents=True, exist_ok=True)
    archive = subprocess.check_output(['git', 'archive', '--format=tar', 'HEAD'], cwd=ROOT)
    sums = []
    for language, code in [(0, 'CN'), (1, 'EN')]:
        with tempfile.TemporaryDirectory() as tmp:
            tree = Path(tmp)
            with tarfile.open(fileobj=io.BytesIO(archive)) as source:
                source.extractall(tree, filter='data')
            config_file = tree / 'config.json'
            config = json.loads(config_file.read_text(encoding='utf-8'))
            config['Language'] = language
            config_file.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding='utf-8')
            properties = tree / 'resources/settings/properties.xml'
            text = properties.read_text(encoding='utf-8')
            text, count = re.subn(r'(<property id="Language" type="number">)\d+(</property>)', rf'\g<1>{language}\g<2>', text)
            assert count == 1, 'Language property missing or ambiguous'
            properties.write_text(text, encoding='utf-8')
            subprocess.run([sys.executable, str(tree / 'tools/make_settings_page.py')], cwd=tree, check=True)
            target = output / f'Aurora6X-Studio-v{version}-Source-{code}.zip'
            with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as result:
                for file in sorted(tree.rglob('*')):
                    if not file.is_file():
                        continue
                    info = zipfile.ZipInfo('Aurora6X-Studio/' + file.relative_to(tree).as_posix(), (2026, 1, 1, 0, 0, 0))
                    info.create_system = 3
                    info.compress_type = zipfile.ZIP_DEFLATED
                    info.external_attr = 0o100644 << 16
                    result.writestr(info, file.read_bytes(), compresslevel=9)
            digest = hashlib.sha256(target.read_bytes()).hexdigest()
            sums.append(f'{digest}  {target.name}')
            print(f'{target.name}: {target.stat().st_size} bytes; SHA-256 {digest}')
    (output / 'SHA256SUMS.txt').write_text('\n'.join(sums) + '\n', encoding='ascii')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'dist')
    package(parser.parse_args().output.resolve())
