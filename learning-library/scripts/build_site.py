"""Parse editable Markdown lessons and embed a validated offline learning app."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
EXPECTED={'grammar':42,'expressions':28,'advanced-expressions':24,'pronunciation-basic':20,'pronunciation-connected':15,'pronunciation-fluent':15,'idioms':24,'stories':40,'take-off':22}

def parse_lesson(path:Path)->dict:
 raw=path.read_text()
 match=re.match(r'^---\n(.*?)\n---\n',raw,re.S)
 if not match:raise ValueError(f'{path}: missing metadata')
 lesson=json.loads(match[1]);lesson['markdown']=raw;sections={}
 for part in re.split(r'^## ',raw[match.end():],flags=re.M)[1:]:
  label,body=part.split('\n',1);sections[label.strip()]=body.strip()
 for key in ['学完能做什么','讲解','给小朋友的比喻','例句','练习','答案与原因','一分钟应用','相关学习','参考资料']:
  if not sections.get(key):raise ValueError(f'{path}: missing section {key}')
 lesson.update({'goal':sections['学完能做什么'],'explanation':sections['讲解'],'analogy':sections['给小朋友的比喻'],'application':sections['一分钟应用'],'examples':[],'quiz':[],'references':[],'file':str(path.relative_to(ROOT))})
 for line in sections['例句'].splitlines():
  if line.startswith('- '):
   fr,zh=line[2:].split(' → ',1);lesson['examples'].append({'fr':fr,'zh':zh})
 answers={}
 for n,letter,reason in re.findall(r'^(\d+)\. ([A-Z]) — (.+)$',sections['答案与原因'],flags=re.M):answers[int(n)]=(ord(letter)-65,reason)
 for block in re.split(r'^### ',sections['练习'],flags=re.M)[1:]:
  prompt,body=block.split('\n',1);n,text=prompt.split('. ',1)
  choices=re.findall(r'^- [A-Z]\. (.+)$',body,flags=re.M)
  answer,reason=answers[int(n)]
  lesson['quiz'].append({'prompt':text,'choices':choices,'answer':answer,'reason':reason})
 lesson['references']=[{'label':a,'url':b} for a,b in re.findall(r'^- \[([^]]+)\]\((https://[^)]+)\)$',sections['参考资料'],flags=re.M)]
 return lesson

def load_library(root:Path)->list[dict]:
 lessons=[]
 for book in EXPECTED:
  for path in sorted((root/book).glob('[A-Z][0-9][0-9].md')):lessons.append(parse_lesson(path))
 return lessons

def validate_library(lessons:list[dict],coverage_path:Path):
 ids=[l['id'] for l in lessons]
 if len(set(ids))!=len(ids):raise ValueError('duplicate lesson id')
 byid={l['id']:l for l in lessons}
 for book,count in EXPECTED.items():
  actual=sum(l['book']==book for l in lessons)
  if actual!=count:raise ValueError(f'{book}: expected {count}, found {actual}')
 for l in lessons:
  if len(l['examples'])<3 or len(l['quiz'])<2:raise ValueError(f'{l["id"]}: insufficient examples or exercises')
  if not l['references']:raise ValueError(f'{l["id"]}: missing references')
  for p in l['prerequisites']:
   if p not in byid:raise ValueError(f'{l["id"]}: missing prerequisite {p}')
  for q in l['quiz']:
   if not isinstance(q['answer'],int) or not 0<=q['answer']<len(q['choices']):raise ValueError(f'{l["id"]}: invalid answer')
   if len(set(q['choices']))!=len(q['choices']):raise ValueError(f'{l["id"]}: duplicate choices')
   if not q['reason']:raise ValueError(f'{l["id"]}: missing answer reason')
 coverage=json.loads(coverage_path.read_text())
 for book,count in {'french-stories':40,'oxford-take-off':22}.items():
  if coverage['source_counts'].get(book)!=count:raise ValueError('coverage missing new source framework')
 seen=set()
 for row in coverage['records']:
  key=row['source_book'],row['source_unit']
  if key in seen:raise ValueError('coverage duplicate')
  seen.add(key)
  if not row['adaptation'] or not row['targets']:raise ValueError('coverage missing explanation or target')
  if any(t not in byid for t in row['targets']):raise ValueError('coverage missing target')
 expected={(b,n) for b,c in coverage['source_counts'].items() for n in range(1,c+1)}
 if seen!=expected or len(seen)!=sum(coverage['source_counts'].values()):raise ValueError('coverage incomplete')
 lookup={(r['source_book'],r['source_unit']):r for r in coverage['records']}
 for l in lessons:
  for unit in l['source_units']:
   b,n=unit.rsplit(':',1);row=lookup.get((b,int(n)))
   if not row or l['id'] not in row['targets']:raise ValueError('coverage inconsistent with lesson '+l['id'])
 # Prerequisites must be acyclic, including between books.
 def visit(lid,active,done):
  if lid in active:raise ValueError('prerequisite cycle')
  if lid in done:return
  active.add(lid)
  for p in byid[lid]['prerequisites']:visit(p,active,done)
  active.remove(lid);done.add(lid)
 done=set()
 for lid in ids:visit(lid,set(),done)

def build():
 lessons=load_library(ROOT/'french');validate_library(lessons,ROOT/'french/coverage.json')
 from pronunciation import enrich
 pronunciation_report=enrich(lessons,ROOT/'scripts/content')
 from site_tutor import expand_library
 pronunciation_report=expand_library(lessons,ROOT/'scripts/content')
 from word_memory import load_memories
 memories=load_memories(ROOT/'scripts/content/word-memories.json',lessons)
 memory_js='window.wordMemoryCatalog='+json.dumps(memories,ensure_ascii=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')+';\n'
 documents={name:(ROOT/'french'/f'{name}.md').read_text() for name in ['study-guide','reference','review']}
 sources={book:json.loads((ROOT/'sources'/book/'reader.json').read_text()) for book in ['french-stories','oxford-take-off'] if (ROOT/'sources'/book/'reader.json').exists()}
 payload=json.dumps({'sources':sources,'lessons':lessons,'documents':documents,'coverage':json.loads((ROOT/'french/coverage.json').read_text())},ensure_ascii=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
 page=(ROOT/'web/template.html').read_text().replace('/*__CSS__*/',(ROOT/'web/style.css').read_text()).replace('/*__DATA__*/',payload).replace('/*__JS__*/',memory_js+(ROOT/'web/word-memory.js').read_text()+'\n'+(ROOT/'web/pronunciation.js').read_text()+'\n'+(ROOT/'web/app.js').read_text()).replace('{{BOOK_COUNT}}',str(len(EXPECTED))).replace('{{LESSON_COUNT}}',str(len(lessons)))
 (ROOT/'index.html').write_text(page)
 print(json.dumps({'lessons':len(lessons),'examples':sum(len(l['examples']) for l in lessons),'pronunciation':pronunciation_report,'word_memories':len(memories),'sentence_memories':sum(len(l['examples']) for l in lessons),'exercises':sum(len(l['quiz']) for l in lessons),'html_bytes':len(page.encode()),'output':str(ROOT/'index.html')},ensure_ascii=False))

if __name__=='__main__':build()
