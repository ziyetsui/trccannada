"""Course edits must not silently introduce generic or missing mnemonics."""
import json, sys, tempfile, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from word_memory import load_memories

class WordMemoryValidation(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)/'memory.json'
        self.lessons = [{'examples':[{'pronunciation':{'words':[{'fr':'Yeux'}, {'fr':'L’été'}]}}]}]
        self.catalog = {key:dict(hook='耶＋亲亲圆嘴',line='眼睛喊耶，嘴巴亲亲。',cue='眼睛开心喊耶，同时做亲亲圆嘴。',method='sound') for key in ['yeux',"l'été"]}

    def load(self):
        self.path.write_text(json.dumps(self.catalog,ensure_ascii=False))
        return load_memories(self.path,self.lessons)

    def test_case_and_apostrophe_normalization(self):
        self.assertEqual(len(self.load()),2)

    def test_new_word_requires_authored_memory(self):
        self.lessons[0]['examples'][0]['pronunciation']['words'].append({'fr':'chat'})
        with self.assertRaisesRegex(ValueError,'missing=.*chat'):self.load()

    def test_removed_word_requires_catalog_review(self):
        self.catalog['chat']=self.catalog['yeux']
        with self.assertRaisesRegex(ValueError,'stale=.*chat'):self.load()

    def test_blank_scene_is_rejected(self):
        self.catalog['yeux']['cue']=' '
        with self.assertRaisesRegex(ValueError,'empty'):self.load()

    def test_unknown_method_is_rejected(self):
        self.catalog['yeux']['method']='automatic-fallback'
        with self.assertRaisesRegex(ValueError,'method'):self.load()

    def test_meaning_only_scene_without_sound_hook_is_rejected(self):
        del self.catalog['yeux']['hook']
        self.catalog['yeux']['line']='睁开眼睛看一看。'
        with self.assertRaisesRegex(ValueError,'empty'):self.load()

    def test_ipa_alone_is_not_a_chinese_memory_hook(self):
        self.catalog['yeux']['hook']='jø'
        with self.assertRaisesRegex(ValueError,'Chinese sound hook'):self.load()

    def test_duplicate_entries_are_rejected(self):
        self.path.write_text('{"yeux":{},"yeux":{}}')
        with self.assertRaisesRegex(ValueError,'duplicate'):load_memories(self.path,self.lessons)
