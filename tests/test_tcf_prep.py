"""Browser contracts: navigation, exact asset binding, recall and degraded modes."""
import functools
import http.server
import json
import threading
import unittest
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


class PrefixHandler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        if path.startswith('/trccannada/'):
            path = path[len('/trccannada'):]
        return super().translate_path(path)

    def log_message(self, *args):
        pass


class PrepTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = http.server.ThreadingHTTPServer(
            ('127.0.0.1', 0), functools.partial(PrefixHandler, directory=str(ROOT)))
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.base = f'http://127.0.0.1:{cls.server.server_port}/trccannada/'
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch()

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        cls.server.shutdown()
        cls.server.server_close()

    def setUp(self):
        self.context = self.browser.new_context(viewport={'width': 1440, 'height': 1000})
        self.page = self.context.new_page()
        self.errors = []
        self.page.on('pageerror', lambda error: self.errors.append(str(error)))

    def tearDown(self):
        self.assertEqual(self.errors, [])
        self.context.close()

    def open_prep(self):
        response = self.page.goto(self.base + 'learning-library/tcf-canada/')
        self.assertEqual(response.status, 200, 'The preparation route must be published')

    def test_route_is_available_beneath_repository_prefix(self):
        self.open_prep()
        self.assertIn('TCF Canada', self.page.locator('h1').inner_text())
        self.page.locator('header').get_by_role('link', name='返回法语学习库').click()
        self.assertEqual(self.page.locator('.book-card').count(), 9)
        self.assertEqual(self.page.locator('.lesson-card').count(), 230)

    def test_library_entry_survives_build(self):
        self.page.goto(self.base + 'learning-library/')
        self.page.get_by_role('link', name='TCF Canada 备考', exact=True).click()
        self.assertTrue(self.page.url.endswith('/learning-library/tcf-canada/'))

    def test_images_and_original_sentences_match_existing_manifest(self):
        self.open_prep()
        manifest = json.loads((ROOT / 'learning-library/scripts/content/sentence-illustrations.json').read_text())
        cards = self.page.locator('[data-memory-id]')
        self.assertEqual(cards.count(), 3)
        for card in cards.all():
            entry = manifest[card.get_attribute('data-memory-id')]
            self.assertEqual(card.locator('[lang="fr"]').inner_text(), entry['fr'])
            self.assertTrue(card.locator('img').get_attribute('src').endswith(entry['asset']))
            card.locator('img').scroll_into_view_if_needed()
            self.page.wait_for_function('(img) => img.complete && img.naturalWidth > 0', arg=card.locator('img').element_handle())

    def test_recall_hides_answer_and_hints_until_revealed(self):
        self.open_prep()
        card = self.page.locator('[data-memory-id]').first
        self.assertTrue(card.locator('[data-answer]').is_visible())
        card.get_by_role('button', name='藏起答案，自己说').click()
        self.assertFalse(card.locator('[data-answer]').is_visible())
        self.assertTrue(card.locator('img').is_visible())
        card.get_by_role('button', name='揭晓答案').click()
        self.assertTrue(card.locator('[data-answer]').is_visible())

    def test_no_french_voice_keeps_learning_readable(self):
        self.context.add_init_script("Object.defineProperty(window,'speechSynthesis',{value:{getVoices:()=>[],addEventListener:()=>{},cancel:()=>{}}});")
        self.open_prep()
        self.assertTrue(self.page.locator('[data-speak]').first.is_disabled())
        self.assertTrue(self.page.locator('[data-resource]').first.is_visible())

    def test_french_voice_and_exact_sentence_reach_device_speech(self):
        # Only the OS speech boundary is replaced; page handlers and recall are real.
        self.context.add_init_script("""
          window.__spoken=[];
          window.SpeechSynthesisUtterance=function(text){this.text=text};
          Object.defineProperty(window,'speechSynthesis',{value:{
            getVoices:()=>[{name:'English',lang:'en-US'},{name:'France',lang:'fr-FR'},{name:'Canada',lang:'fr-CA'}],
            addEventListener:()=>{},cancel:()=>{},speak:u=>window.__spoken.push({text:u.text,lang:u.lang,rate:u.rate})}});
        """)
        self.open_prep()
        self.page.get_by_label('练习法语声音').select_option('fr-CA')
        self.page.locator('[data-memory-id]').first.locator('[data-speak]').click()
        self.assertEqual(self.page.evaluate('window.__spoken.at(-1)'), {
            'text': 'Je m’appelle Lin. Ça s’écrit L-I-N.', 'lang': 'fr-CA', 'rate': 0.85})

    def test_theme_mobile_and_blocked_storage(self):
        self.open_prep()
        self.page.get_by_role('button', name='切换到深色模式').click()
        self.page.reload()
        self.assertEqual(self.page.locator('html').get_attribute('data-theme'), 'dark')
        for width in (360, 390, 768):
            self.page.set_viewport_size({'width': width, 'height': 844})
            self.assertTrue(self.page.evaluate('document.documentElement.scrollWidth <= innerWidth'))
        self.context.add_init_script("Object.defineProperty(window,'localStorage',{get(){throw new Error('blocked')}})")
        self.page.reload()
        self.page.locator('[data-recall]').first.click()
        self.assertFalse(self.page.locator('[data-answer]').first.is_visible())

    def test_sources_remain_available_without_javascript(self):
        context = self.browser.new_context(java_script_enabled=False)
        try:
            page = context.new_page()
            response = page.goto(self.base + 'learning-library/tcf-canada/')
            self.assertEqual(response.status, 200)
            self.assertGreaterEqual(page.locator('[data-resource] a').count(), 7)
            self.assertTrue(page.locator('[data-answer]').first.is_visible())
            self.assertTrue(page.locator('header').get_by_role('link', name='返回法语学习库').is_visible())
        finally:
            context.close()


if __name__ == '__main__':
    unittest.main()
