"""Real browser contracts for textbook microcourses under the Pages prefix."""
import functools
import http.server
import os
import threading
import unittest
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(os.environ.get('TEXTBOOK_TEST_ROOT', Path(__file__).resolve().parents[1]))
class Handler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        if path.startswith('/trccannada/'):
            path = path[len('/trccannada'):]
        return super().translate_path(path)
    def log_message(self, *args): pass

class BrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)))
        threading.Thread(target=cls.server.serve_forever,daemon=True).start()
        cls.url = f'http://127.0.0.1:{cls.server.server_port}/trccannada/learning-library/textbooks/'
        cls.p = sync_playwright().start()
        cls.browser = cls.p.chromium.launch()
    @classmethod
    def tearDownClass(cls):
        cls.browser.close(); cls.p.stop(); cls.server.shutdown(); cls.server.server_close()
    def setUp(self):
        self.context = self.browser.new_context(viewport={'width':390,'height':844})
        self.page = self.context.new_page(); self.errors=[]
        self.page.on('pageerror',lambda e:self.errors.append(str(e)))
    def tearDown(self):
        self.assertEqual(self.errors,[])
        self.context.close()
    def open(self):
        response = self.page.goto(self.url)
        self.assertEqual(response.status,200,'Textbook route is missing')
    def test_catalogue_search_and_mobile(self):
        self.open()
        self.assertEqual(self.page.locator('.book-card').count(),5)
        self.assertGreaterEqual(self.page.locator('.lesson-card').count(),160)
        self.assertIn('A2',self.page.locator('#roadmap').inner_text())
        self.page.locator('#search').fill('JM101')
        self.assertEqual(self.page.locator('.lesson-card').count(),1)
        self.assertTrue(self.page.evaluate('document.documentElement.scrollWidth<=innerWidth'))
    def test_recall_hides_all_answer_hints_and_keeps_same_image(self):
        self.open(); self.page.locator('.lesson-card').first.click()
        self.page.locator('#anchor-fr').wait_for(state='visible')
        original = self.page.locator('#anchor-image').get_attribute('src')
        original_alt = self.page.locator('#anchor-image').get_attribute('alt')
        movie = self.page.locator('#movie').inner_text()
        french = self.page.locator('#anchor-fr').inner_text()
        self.page.locator('#recall').click()
        self.assertFalse(self.page.locator('#answer-content').is_visible())
        self.assertFalse(self.page.locator('#anchor-fr').is_visible())
        self.assertTrue(self.page.locator('#anchor-image').is_visible())
        self.assertEqual(self.page.locator('#anchor-image').get_attribute('src'),original)
        self.assertNotIn(french,self.page.locator('#anchor-image').get_attribute('alt'))
        self.assertNotIn(movie,self.page.locator('#anchor-image').get_attribute('alt'))
        self.page.locator('#reveal').click()
        self.assertEqual(self.page.locator('#anchor-fr').inner_text(),french)
        self.assertTrue(self.page.locator('#answer-content').is_visible())
        self.assertEqual(self.page.locator('#anchor-image').get_attribute('alt'),original_alt)
    def test_search_indexes_application_and_quiz_text(self):
        self.open(); self.page.locator('.lesson-card').first.click()
        self.page.locator('#anchor-fr').wait_for(state='visible')
        lid=self.page.locator('#breadcrumb').inner_text().split(' / ')[-1]
        application=self.page.locator('#application').inner_text()
        prompt=self.page.locator('#quizzes legend').first.inner_text().split('. ',1)[1]
        self.page.locator('#back').click()
        for query in (application,prompt):
            self.page.locator('#search').fill(query)
            self.assertGreaterEqual(self.page.locator(f'.lesson-card[data-lesson="{lid}"]').count(),1)
    def test_failed_image_does_not_expose_movie_during_recall(self):
        self.page.route('**/*.webp',lambda route:route.abort())
        self.open();self.page.locator('.lesson-card').first.click()
        self.page.locator('#image-status').wait_for(state='visible')
        movie=self.page.locator('#movie').inner_text()
        self.page.locator('#recall').click()
        self.assertNotIn(movie,self.page.locator('#anchor-image').get_attribute('alt'))
    def test_quiz_feedback_and_manual_progress(self):
        self.open(); self.page.locator('.lesson-card').first.click()
        self.assertEqual(self.page.locator('.quiz-feedback').count(),0)
        self.page.locator('#check-answers').click()
        self.assertGreaterEqual(self.page.locator('.quiz-feedback').count(),2)
        self.assertNotIn('已学',self.page.locator('#mark').inner_text())
        self.page.locator('#mark').click(); self.page.reload()
        self.assertIn('已学',self.page.locator('#mark').inner_text())
    def test_no_voice_and_storage_failure_still_allow_learning(self):
        self.context.add_init_script("Object.defineProperty(window,'localStorage',{get(){throw new Error('denied')}});Object.defineProperty(window,'speechSynthesis',{value:{getVoices:()=>[],cancel(){},addEventListener(){}}});")
        self.open(); self.page.locator('.lesson-card').first.click()
        self.assertTrue(self.page.locator('#listen').is_disabled())
        self.assertIn('法语声音',self.page.locator('#voice-status').inner_text())
        self.page.locator('#mark').click(); self.page.locator('#theme-toggle').click()
        self.assertTrue(self.page.evaluate('document.documentElement.scrollWidth<=innerWidth'))
    def test_french_voice_and_exact_sentence(self):
        self.context.add_init_script("window.__spoken=[];Object.defineProperty(window,'speechSynthesis',{value:{getVoices:()=>[{name:'Français',lang:'fr-CA',voiceURI:'fr-ca'}],cancel(){},speak:u=>window.__spoken.push({text:u.text,lang:u.lang}),addEventListener(){}}});window.SpeechSynthesisUtterance=function(t){this.text=t};")
        self.open(); self.page.locator('.lesson-card').first.click()
        self.page.locator('#anchor-fr').wait_for(state='visible')
        french = self.page.locator('#anchor-fr').inner_text()
        self.page.locator('#listen').click()
        self.assertEqual(self.page.evaluate('window.__spoken.at(-1)'),{'text':french,'lang':'fr-CA'})
        self.page.locator('.word').first.click()
        self.assertEqual(self.page.evaluate('window.__spoken.at(-1).lang'),'fr-CA')
    def test_theme_persistence_invalid_route_and_library_links(self):
        self.open(); self.page.locator('#theme-toggle').click(); theme=self.page.locator('html').get_attribute('data-theme')
        self.page.reload(); self.assertEqual(self.page.locator('html').get_attribute('data-theme'),theme)
        self.page.goto(self.url+'#%ZZ'); self.assertTrue(self.page.locator('#catalogue').is_visible())
        self.page.get_by_role('link',name='原有学习库',exact=True).click()
        self.assertEqual(self.page.locator('.book-card').count(),9)

if __name__=='__main__': unittest.main()
