"""Publishing contracts for independently authored textbook companions."""
import copy
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'learning-library/textbooks/build.py'

class BuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('textbooks_build', SCRIPT)
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)

    def example(self):
        anchor = json.loads((ROOT / 'learning-library/scripts/content/sentence-illustrations.json').read_text())['T01:1']
        return {'id':'TEST01','number':1,'title':'示例','source_title':'第1课','minutes':20,
                'goal':'开口问候','prerequisites':[],
                'sources':[{'book':'nihao-a1-student','location':'pages/0026.md','label':'第1课','review_status':'ocr_unverified'}],
                'explanation':'有针对性的独立中文讲解。','analogy':'一次进门打招呼。',
                'teaching_points':['礼貌称呼','问候语序'],
                'anchor':{**{k:anchor[k] for k in ('fr','zh','sound','movie')},'pronunciation':'先听标准法语。','reuse_id':'T01:1'},
                'quiz':[{'prompt':'称呼谁？','choices':['陈女士','马丁先生'],'answer':0,'reason':'Madame是女士称呼。'},
                        {'prompt':'何时用？','choices':['白天见面','睡前告别'],'answer':0,'reason':'Bonjour用于见面。'}],
                'application':'向一位女士问候。','self_check':['有礼貌称呼'],'teacher_notes':'','status':'original-companion-draft'}

    def book(self):
        return {'id':'test','title':'测试','subtitle':'测试','level':'A1','role':'主线','source_slugs':['nihao-a1-student'],'lessons':[self.example()]}

    def test_reused_illustration_requires_all_four_exact_fields(self):
        book = self.book()
        self.module.validate_books([book], ROOT / 'learning-library')
        book['lessons'][0]['anchor']['fr'] += ' Bonjour.'
        with self.assertRaisesRegex(ValueError, 'stale|exact|mismatch'):
            self.module.validate_books([book], ROOT / 'learning-library')

    def test_source_and_asset_paths_cannot_escape_public_tree(self):
        book = self.book()
        book['lessons'][0]['sources'][0]['location'] = '../../private.pdf'
        with self.assertRaises(ValueError):
            self.module.validate_books([book], ROOT / 'learning-library')

    def test_bad_answers_and_duplicate_ids_cannot_publish(self):
        book = self.book()
        book['lessons'].append(copy.deepcopy(book['lessons'][0]))
        with self.assertRaises(ValueError):
            self.module.validate_books([book], ROOT / 'learning-library')
        book = self.book()
        book['lessons'][0]['quiz'][0]['answer'] = -1
        with self.assertRaises(ValueError):
            self.module.validate_books([book], ROOT / 'learning-library')

    def test_new_anchor_requires_verified_generated_image(self):
        book = self.book()
        book['lessons'][0]['anchor']['reuse_id'] = None
        with self.assertRaisesRegex(ValueError, 'illustration|image'):
            self.module.validate_books([book], ROOT / 'learning-library')

    def test_all_original_lesson_and_review_ids_are_required(self):
        content=ROOT/'learning-library/textbooks/content'
        books=[self.module.read_json(content/(name+'.json')) for name in self.module.EXPECTED_IDS]
        self.module.validate_coverage(books)
        books[0]['lessons'].pop()
        with self.assertRaisesRegex(ValueError,'source coverage mismatch'):
            self.module.validate_coverage(books)

    def test_markdown_export_keeps_teaching_answers_and_provenance(self):
        text = self.module.lesson_markdown(self.example(), self.book())
        for value in ('## 学完能做什么','## 讲解','## 例句','## 练习','## 答案与原因',
                      'pages/0026.md','Bonjour, Madame Chen.','Madame是女士称呼。'):
            self.assertIn(value, text)
        self.assertNotIn('/Users/', text)

    def test_corrupt_webp_is_decoded_even_with_matching_checksum(self):
        book=self.book();book['lessons'][0]['anchor']['reuse_id']=None
        raw=bytearray((ROOT/'learning-library/textbooks/assets/N433.webp').read_bytes())
        raw[64]^=255
        with tempfile.TemporaryDirectory() as folder:
            library=Path(folder)
            (library/'scripts/content').mkdir(parents=True)
            (library/'scripts/content/sentence-illustrations.json').write_text('{}')
            assets=library/'textbooks/assets';assets.mkdir(parents=True)
            (assets/'TEST01.webp').write_bytes(raw)
            entry={**{k:book['lessons'][0]['anchor'][k] for k in ('fr','zh','sound','movie')},
                   'asset':'assets/TEST01.webp','alt':'A neutral fixture scene',
                   'sha256':hashlib.sha256(raw).hexdigest(),'visual_review':'approved'}
            (library/'textbooks/illustrations.json').write_text(json.dumps({'TEST01':entry}))
            with self.assertRaisesRegex(ValueError,'image|decode'):
                self.module.validate_books([book],library)

if __name__ == '__main__':
    unittest.main()
