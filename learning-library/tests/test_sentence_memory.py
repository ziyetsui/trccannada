"""Reject missing or stale sentence stories when the curriculum changes."""
import copy,json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from sentence_memory import apply_sentence_memories

class SentenceMemoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.content=Path(self.tmp.name);self.path=self.content/'sentence-memories.json'
        self.lessons=[{'id':'G01','examples':[{'fr':'Je suis étudiant.','zh':'我是男学生。','pronunciation':{'rule_memory':'保留规则'}}]}]
        self.entries={'G01:1':{'fr':'Je suis étudiant.','zh':'我是男学生。','sound':'热水里，学生举起玉笛。','movie':'学生拿玉笛当勺子，搅动热水，一边介绍自己。'}}
    def apply(self):
        self.path.write_text(json.dumps(self.entries,ensure_ascii=False))
        return apply_sentence_memories(self.lessons,self.content)
    def test_applies_separate_fields_and_retains_rules(self):
        self.assertEqual(self.apply(),1)
        p=self.lessons[0]['examples'][0]['pronunciation']
        self.assertEqual(p['sound_joke'],self.entries['G01:1']['sound'])
        self.assertEqual(p['mental_movie'],self.entries['G01:1']['movie'])
        self.assertEqual(p['rule_memory'],'保留规则')
    def test_new_sentence_needs_a_story(self):
        self.lessons[0]['examples'].append(copy.deepcopy(self.lessons[0]['examples'][0]))
        with self.assertRaisesRegex(ValueError,'coverage.*G01:2'):self.apply()
    def test_french_edit_requires_review(self):
        self.lessons[0]['examples'][0]['fr']='Je suis professeur.'
        with self.assertRaisesRegex(ValueError,'stale sentence'):self.apply()
    def test_meaning_edit_requires_review(self):
        self.lessons[0]['examples'][0]['zh']='我是教师。'
        with self.assertRaisesRegex(ValueError,'stale sentence'):self.apply()
    def test_generic_template_is_rejected(self):
        self.entries['G01:1']['movie']='句子小怪兽抱着发光大招牌。'
        with self.assertRaisesRegex(ValueError,'generic'):self.apply()
    def test_empty_movie_is_rejected(self):
        self.entries['G01:1']['movie']=' '
        with self.assertRaisesRegex(ValueError,'empty'):self.apply()
    def test_duplicate_sentence_key_is_rejected(self):
        self.path.write_text('{"G01:1":{},"G01:1":{}}')
        with self.assertRaisesRegex(ValueError,'duplicate'):apply_sentence_memories(self.lessons,self.content)
