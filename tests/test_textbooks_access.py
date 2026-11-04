"""Exercise the real publishing boundary and browser decryption, without production secrets."""
import functools
import http.server
import os
from pathlib import Path
import subprocess
import tempfile
import threading
import unittest
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PASSWORD = 'Fixture-only-7hQ4-long-access'
SCRIPT = ROOT / 'scripts/protect_textbooks.py'

class AccessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.base = Path(cls.temp.name)
        cls.source = cls.base / 'private'
        cls.source.mkdir()
        (cls.source / 'index.html').write_text('''<!doctype html><html lang="zh-CN"><body>
<h1 id="course">Private fixture course</h1><p id="route"></p>
<script>document.querySelector('#route').textContent=location.hash;</script>
</body></html>''')
        (cls.source / 'content').mkdir()
        (cls.source / 'content/leak.json').write_text('{"secret":"must not publish"}')
        (cls.source / 'lessons').mkdir()
        (cls.source / 'lessons/leak.md').write_text('Private markdown')
        (cls.source / 'assets').mkdir()
        (cls.source / 'assets/metadata.json').write_text('{"secret":"image prompt"}')
        cls.output = cls.base / 'public/learning-library/textbooks'
        cls.env = {**os.environ, 'STATICRYPT_PASSWORD': PASSWORD}
        result = subprocess.run(['python3', str(SCRIPT), '--source', str(cls.source), '--output', str(cls.output)], env=cls.env, capture_output=True, text=True)
        if result.returncode:
            raise AssertionError('Encrypted publisher did not produce the fixture: '+result.stderr)
        class Quiet(http.server.SimpleHTTPRequestHandler):
            def log_message(self, *args): pass
        cls.server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=str(cls.base/'public')))
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.url = f'http://127.0.0.1:{cls.server.server_port}/learning-library/textbooks/'
        cls.p = sync_playwright().start()
        cls.browser = cls.p.chromium.launch()

    @classmethod
    def tearDownClass(cls):
        cls.browser.close(); cls.p.stop(); cls.server.shutdown(); cls.server.server_close(); cls.temp.cleanup()

    def setUp(self):
        self.context = self.browser.new_context(viewport={'width':390,'height':844})
        self.page = self.context.new_page()
        self.errors = []
        self.page.on('pageerror', lambda e: self.errors.append(str(e)))

    def tearDown(self):
        self.assertEqual(self.errors, [])
        self.context.close()

    def unlock(self, remember=False):
        self.page.get_by_label('访问码', exact=True).fill(PASSWORD)
        if remember: self.page.get_by_label('记住此设备 7 天').check()
        self.page.get_by_role('button', name='进入学习室', exact=True).click()
        self.page.locator('#course').wait_for()

    def test_wrong_code_cannot_read_plaintext_then_correct_code_preserves_route(self):
        response = self.page.goto(self.url+'#NA201')
        self.assertNotIn('Private fixture course', response.text())
        self.assertNotIn(PASSWORD, response.text())
        self.assertEqual(self.page.locator('#course').count(), 0)
        self.page.get_by_label('访问码', exact=True).fill('wrong-code')
        self.page.get_by_role('button', name='进入学习室', exact=True).click()
        self.page.get_by_role('alert').filter(has_text='访问码不正确').wait_for()
        self.assertEqual(self.page.locator('#course').count(), 0)
        self.unlock()
        self.assertEqual(self.page.locator('#route').inner_text(), '#NA201')
        self.page.reload()
        self.page.get_by_label('访问码', exact=True).wait_for()
        self.assertEqual(self.page.locator('#course').count(), 0)

    def test_remember_expires_and_logout_does_not_clear_learning_progress(self):
        self.page.goto(self.url)
        self.page.evaluate("localStorage.setItem('francais.textbooks.v1', JSON.stringify({done:['NA101']}))")
        self.unlock(remember=True)
        self.page.reload(); self.page.locator('#course').wait_for()
        self.page.get_by_role('button', name='退出学习室', exact=True).click()
        self.page.get_by_label('访问码', exact=True).wait_for()
        self.assertIn('NA101', self.page.evaluate("localStorage.getItem('francais.textbooks.v1')"))
        self.unlock(remember=True)
        self.page.evaluate("localStorage.setItem('textbooks.access.expiration', '1')")
        self.page.reload(); self.page.get_by_label('访问码', exact=True).wait_for()
        self.assertEqual(self.page.locator('#course').count(), 0)

    def test_mobile_and_storage_disabled_still_unlock(self):
        self.context.add_init_script("Object.defineProperty(window,'localStorage',{get(){throw new Error('denied')}})")
        self.page.goto(self.url)
        self.page.get_by_label('访问码', exact=True).wait_for()
        self.assertTrue(self.page.evaluate('document.documentElement.scrollWidth<=innerWidth'))
        self.unlock()

    def test_only_encrypted_page_and_images_are_published(self):
        self.assertEqual({p.relative_to(self.output).as_posix() for p in self.output.rglob('*') if p.is_file()}, {'index.html'})
        for path in ['lessons/leak.md','content/leak.json','assets/metadata.json']:
            self.assertEqual(self.context.request.get(self.url+path).status, 404)

    def test_missing_weak_or_internal_source_cannot_overwrite_publication(self):
        original = (self.output/'index.html').read_bytes()
        cases = [('',self.source),('123456',self.source),(' '*20,self.source),(PASSWORD, ROOT/'learning-library/textbooks')]
        for code,source in cases:
            result = subprocess.run(['python3', str(SCRIPT), '--source', str(source), '--output', str(self.output)], env={**os.environ,'STATICRYPT_PASSWORD':code}, capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual((self.output/'index.html').read_bytes(), original)

if __name__ == '__main__': unittest.main()
