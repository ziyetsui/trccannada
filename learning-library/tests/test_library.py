import unittest,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from build_site import load_library, validate_library
class LibraryTests(unittest.TestCase):
 def test_complete_curriculum(self):
  lessons=load_library(ROOT/'french')
  self.assertEqual(len(lessons),230)
  validate_library(lessons,ROOT/'french/coverage.json')
 def test_invalid_answer_rejected(self):
  lessons=load_library(ROOT/'french')
  lessons[0]['quiz'][0]['answer']=99
  with self.assertRaisesRegex(ValueError,'answer'):validate_library(lessons,ROOT/'french/coverage.json')
 def test_missing_coverage_rejected(self):
  import json,tempfile
  lessons=load_library(ROOT/'french')
  coverage=json.loads((ROOT/'french/coverage.json').read_text())
  coverage['records'].pop()
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'coverage.json';p.write_text(json.dumps(coverage))
   with self.assertRaisesRegex(ValueError,'coverage'):validate_library(lessons,p)
 def test_missing_added_source_framework_rejected(self):
  import json,tempfile
  coverage=json.loads((ROOT/'french/coverage.json').read_text())
  coverage['source_counts'].pop('french-stories')
  coverage['records']=[r for r in coverage['records'] if r['source_book']!='french-stories']
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'coverage.json';p.write_text(json.dumps(coverage))
   with self.assertRaisesRegex(ValueError,'coverage'):validate_library(load_library(ROOT/'french'),p)
 def test_duplicate_id_rejected(self):
  lessons=load_library(ROOT/'french');lessons[1]['id']=lessons[0]['id']
  with self.assertRaisesRegex(ValueError,'duplicate'):validate_library(lessons,ROOT/'french/coverage.json')
 def test_missing_section_rejected(self):
  import tempfile
  from build_site import parse_lesson
  source=(ROOT/'french/grammar/G01.md').read_text().replace('## 给小朋友的比喻','## 错误标题')
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'G01.md';p.write_text(source)
   with self.assertRaisesRegex(ValueError,'missing section'):parse_lesson(p)
 def test_missing_mapped_target_rejected(self):
  import json,tempfile
  coverage=json.loads((ROOT/'french/coverage.json').read_text());coverage['records'][0]['targets']=['G99']
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'coverage.json';p.write_text(json.dumps(coverage))
   with self.assertRaisesRegex(ValueError,'missing target'):validate_library(load_library(ROOT/'french'),p)
if __name__=='__main__':unittest.main()
