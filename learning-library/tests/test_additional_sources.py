# -*- coding: utf-8 -*-
"""Check source preservation separately from the quality of authored teaching."""
import unittest,json,hashlib,zipfile,xml.etree.ElementTree as ET,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from build_site import load_library,validate_library
@unittest.skipUnless((ROOT/"sources/french-stories/reader.json").exists(), "Full-source checks run in the local edition")
class AdditionalSourceTests(unittest.TestCase):
 def test_epub_archive_and_spine_text_are_retained(self):
  d=ROOT/'sources/french-stories';m=json.loads((d/'manifest.json').read_text());source=Path('/Users/ziye/Downloads')/m['source_file']
  self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),m['sha256'])
  chunks=[json.loads(s) for s in (d/'chunks.jsonl').read_text().splitlines()]
  self.assertEqual([c['source_ref'] for c in chunks],m['spine'])
  self.assertEqual(len(chunks),313)
  with zipfile.ZipFile(source) as z:
   for name in z.namelist():
    if not name.endswith('/'):self.assertEqual((d/'raw'/name).read_bytes(),z.read(name),name)
   for c in chunks:
    body=ET.fromstring(z.read(c['source_ref'])).find('{*}body')
    original=[' '.join(''.join(e.itertext()).split()) for e in body]
    self.assertEqual([s for s in original if s],[b.get('source_text',b['text']) for b in c['blocks']],c['source_ref'])
 def test_epub_markdown_links_and_images_resolve(self):
  p=ROOT/'sources/french-stories/book.md'
  for link in re.findall(r'\]\(([^)]+)\)',p.read_text()):
   if not link or '://' in link or link.startswith(('mailto:','#')):continue
   self.assertTrue((p.parent/link.split('#')[0]).resolve().exists(),link)
 def test_reader_retains_all_epub_text_blocks(self):
  d=ROOT/'sources/french-stories';r=json.loads((d/'reader.json').read_text());chunks=[json.loads(s) for s in (d/'chunks.jsonl').read_text().splitlines()]
  original={b['id']:b['text'] for c in chunks for b in c['blocks']}
  retained=[b for u in r['units'] for b in u['blocks']]+[b for f in r['front_matter'] for b in f.get('blocks',[])]
  self.assertEqual(len({b['id'] for b in retained}),len(retained))
  self.assertEqual({b['id']:b['text'] for b in retained},original)
  self.assertEqual([sum(u['volume']==v for u in r['units']) for v in [1,2,3]],[10,10,20])
  for u in r['units']:
   roles={b['role'] for b in u['blocks']}
   self.assertTrue({'story','vocabulary','exercise','answer'}<=roles,u['unit'])
 def test_oxford_all_physical_pages_and_half_pages(self):
  d=ROOT/'sources/oxford-take-off';m=json.loads((d/'manifest.json').read_text());source=Path(m['source_file'])
  self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),m['sha256'])
  self.assertEqual(len(m['pages']),131)
  r=json.loads((d/'reader.json').read_text());self.assertEqual(len(r['units']),22)
  blocks=[b for u in r['units'] for b in u['blocks']]+r['front_matter'];self.assertEqual(len({b['id'] for b in blocks}),len(blocks))
  byhalf={}
  for b in blocks:byhalf.setdefault((b['pdf_page'],b['side']),[]).append(b['text'])
  book=(d/'book.md').read_text()
  for n in range(1,132):
   self.assertTrue((d/'pages'/f'{n:04}.md').exists());self.assertTrue((d/'images'/f'{n:04}.jpg').exists())
   self.assertIn((d/'raw'/f'{n:04}.txt').read_text(),book)
   for side in ['L','R']:
    text=(d/'halves'/f'{n:04}-{side}.txt').read_text()
    self.assertEqual(byhalf.get((n,side),[]),[s for s in re.split(r'\n\s*\n',text.strip()) if s.strip()])
 def test_new_lessons_have_valid_provenance(self):
  lessons=load_library(ROOT/'french');validate_library(lessons,ROOT/'french/coverage.json')
  byid={l['id']:l for l in lessons}
  for prefix,bid,count in [('S','french-stories',40),('T','oxford-take-off',22)]:
   reader=json.loads((ROOT/'sources'/bid/'reader.json').read_text())
   for n in range(1,count+1):
    l=byid[f'{prefix}{n:02}'];self.assertEqual(l['source_reader'],{'book_id':bid,'unit':n})
    self.assertTrue(next(u for u in reader['units'] if u['unit']==n)['blocks'])
if __name__=='__main__':unittest.main()
