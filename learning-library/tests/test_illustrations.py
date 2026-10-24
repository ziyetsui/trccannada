"""Reject stale, missing, corrupt or unsafe visual memory assets."""
import copy, json, sys, tempfile, unittest
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from illustrations import apply_illustrations

class IllustrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);(self.root/'assets').mkdir()
        self.asset=self.root/'assets/test.webp';Image.new('RGB',(768,512),'ivory').save(self.asset)
        self.lessons=[{'id':'T01','book':'take-off','examples':[{'fr':'Bonjour.','zh':'你好。','pronunciation':{'sound_joke':'蹦入','mental_movie':'蹦着打招呼。'}}]}]
        self.entries={'T01:1':{'fr':'Bonjour.','zh':'你好。','sound':'蹦入','movie':'蹦着打招呼。','asset':'assets/test.webp','alt':'一个人蹦着挥手。'}}
        self.path=self.root/'manifest.json'
    def run_apply(self):
        self.path.write_text(json.dumps(self.entries))
        return apply_illustrations(self.lessons,self.path,self.root)
    def test_only_oxford_enriched_with_answer_free_alt(self):
        other=copy.deepcopy(self.lessons[0]);other.update(id='G01',book='grammar');self.lessons.append(other)
        self.assertEqual(self.run_apply(),1)
        self.assertEqual(self.lessons[0]['examples'][0]['illustration']['src'],'assets/test.webp')
        self.assertNotIn('illustration',other['examples'][0])
        self.assertNotIn('Bonjour',self.lessons[0]['examples'][0]['illustration']['alt'])
    def test_missing_entry(self):
        self.entries={}
        with self.assertRaisesRegex(ValueError,'coverage'):self.run_apply()
    def test_stale_sentence_or_memory(self):
        for field in ('fr','zh','sound','movie'):
            with self.subTest(field=field):
                original=self.entries['T01:1'][field];self.entries['T01:1'][field]='changed'
                with self.assertRaisesRegex(ValueError,'stale'):self.run_apply()
                self.entries['T01:1'][field]=original
    def test_missing_asset(self):
        self.asset.unlink()
        with self.assertRaisesRegex(ValueError,'missing'):self.run_apply()
    def test_corrupt_asset(self):
        self.asset.write_bytes(b'not an image')
        with self.assertRaisesRegex(ValueError,'invalid'):self.run_apply()
    def test_external_or_parent_paths(self):
        for path in ('../secret.webp','https://example.com/picture.webp','/tmp/test.webp'):
            with self.subTest(path=path):
                self.entries['T01:1']['asset']=path
                with self.assertRaisesRegex(ValueError,'unsafe'):self.run_apply()
    def test_duplicate_asset_not_counted_as_unique_coverage(self):
        self.lessons[0]['examples'].append(copy.deepcopy(self.lessons[0]['examples'][0]))
        self.entries['T01:2']=copy.deepcopy(self.entries['T01:1'])
        with self.assertRaisesRegex(ValueError,'reused'):self.run_apply()
    def test_missing_alt(self):
        self.entries['T01:1']['alt']=''
        with self.assertRaisesRegex(ValueError,'alt'):self.run_apply()
    def test_validation_is_atomic(self):
        self.lessons[0]['examples'].append(copy.deepcopy(self.lessons[0]['examples'][0]))
        self.entries['T01:2']=copy.deepcopy(self.entries['T01:1']);self.entries['T01:2']['fr']='stale'
        with self.assertRaises(ValueError):self.run_apply()
        self.assertNotIn('illustration',self.lessons[0]['examples'][0])

if __name__=='__main__':unittest.main()
