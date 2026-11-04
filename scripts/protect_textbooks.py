"""Publish an encrypted course edition from an explicitly private source directory."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]

def publish(source: Path, output: Path):
    source, output = source.resolve(), output.resolve()
    password = os.environ.get('STATICRYPT_PASSWORD', '')
    if len(password.strip()) < 16 or password != password.strip():
        raise ValueError('STATICRYPT_PASSWORD must contain at least 16 characters.')
    if source == ROOT or ROOT in source.parents:
        raise ValueError('Plaintext source must be kept outside the public repository.')
    if source == output or source in output.parents or output in source.parents:
        raise ValueError('Private source and published output must not overlap.')
    html = (source / 'index.html').read_text()
    if 'staticryptEncryptedMsgUniqueVariableName' in html:
        raise ValueError('Source is already encrypted; use the private editable edition.')
    if re.search(r'<script\b[^>]*\bsrc\s*=', html, re.I):
        raise ValueError('Course scripts must be embedded before encryption.')
    # The course already exports Markdown from its embedded data after unlocking.
    # No raw lesson files or source JSON are copied into the published directory.
    logout = '''<button type="button" id="textbooks-lock" style="display:block;margin:1rem auto;padding:.6rem 1rem;cursor:pointer" onclick="try{localStorage.removeItem('textbooks.access.expiration');localStorage.removeItem('textbooks.access.passphrase')}catch(e){}location.replace(location.pathname+'#staticrypt_logout');location.reload()">退出学习室</button>'''
    if '</body>' not in html:
        raise ValueError('Source must be a complete HTML document.')
    html = html.replace('</body>', logout + '</body>')
    output.parent.mkdir(parents=True, exist_ok=True)
    # All fallible preparation happens before replacing the live publication.
    with tempfile.TemporaryDirectory(prefix='.textbooks-encrypt-', dir=output.parent) as tmp:
        tmp = Path(tmp)
        plain = tmp/'index.html'
        plain.write_text(html)
        staged = tmp/'encrypted'
        salt = json.loads((ROOT/'scripts/textbooks-access-salt.json').read_text())['salt']
        args = ['node', str(ROOT/'node_modules/staticrypt/cli/index.js'), str(plain),
                '--config', 'false', '--salt', salt, '--remember', '7',
                '--template', str(ROOT/'scripts/textbooks-access-template.html'),
                '--directory', str(staged)]
        result = subprocess.run(args, cwd=tmp, env=os.environ.copy(), capture_output=True, text=True)
        if result.returncode:
            raise RuntimeError('StatiCrypt encryption failed; publication was not changed.')
        encrypted = (staged/'index.html').read_text()
        if 'staticryptEncryptedMsgUniqueVariableName' not in encrypted or password in encrypted:
            raise ValueError('Encrypted publication validation failed.')
        assets = source/'assets'
        if assets.exists():
            for image in assets.rglob('*'):
                if image.is_file() and image.suffix.lower() in {'.webp','.png','.jpg','.jpeg','.gif','.avif'}:
                    dest = staged/'assets'/image.relative_to(assets)
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(image, dest)
        # Keep rollback inside the temporary directory until the new tree is installed.
        backup = tmp/'previous'
        if output.exists(): output.rename(backup)
        try:
            staged.rename(output)
        except BaseException:
            if backup.exists(): backup.rename(output)
            raise
    print('Published encrypted HTML and image assets; plaintext source and code remain private.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True, help='Private directory containing the built index.html and assets/')
    parser.add_argument('--output', type=Path, default=ROOT/'learning-library/textbooks')
    args = parser.parse_args()
    try:
        publish(args.source, args.output)
    except (ValueError, OSError, RuntimeError) as exc:
        parser.exit(1, str(exc)+'\n')
