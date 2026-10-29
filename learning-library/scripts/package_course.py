"""Package French course and source TOCs without full copyrighted source books."""
from pathlib import Path
import json,re,zipfile
ROOT=Path(__file__).resolve().parents[1]
files={ROOT/'index.html',ROOT/'AI-READING-GUIDE.md',ROOT/'requirements.txt'}
for folder in ['french','web','scripts','tests','docs','research','assets']:
 files.update(p for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc')
files.update([ROOT/'sources/verification.md',ROOT/'sources/verification.json',ROOT/'sources/inventory.json'])
for d in (ROOT/'sources').iterdir():
 if not d.is_dir() or d.name in ['french-stories','oxford-take-off']:continue
 if not (d/'manifest.json').exists():
  # The published checkout contains TOC extracts, not the private originals.
  contents=d/'contents.md'
  if not contents.exists():raise ValueError('Missing source TOC: '+d.name)
  files.add(contents)
  for n in re.findall(r'^## PDF page (\d+)$',contents.read_text(),re.M):
   for sub,ext in [('pages','md'),('images','jpg'),('raw','txt')]:files.add(d/sub/f'{int(n):04}.{ext}')
  continue
 manifest=json.loads((d/'manifest.json').read_text())
 files.add(d/'contents.md')
 for n in manifest['contents_pdf_pages']:
  for sub,ext in [('pages','md'),('images','jpg'),('raw','txt')]:files.add(d/sub/f'{n:04}.{ext}')
# Follow any auxiliary local links from included Markdown (e.g. extracted images).
queue=list(files);broken=[]
while queue:
 p=queue.pop()
 if p.suffix!='.md':continue
 for link in re.findall(r'\]\(([^)]+)\)',p.read_text()):
  link=link.split('#')[0]
  if not link or '://' in link or link.startswith('mailto:'):continue
  target=(p.parent/link).resolve()
  if target==ROOT/'francais-en-pratique.zip':continue
  if not target.exists():broken.append([str(p.relative_to(ROOT)),link]);continue
  # Never silently package a full source book or follow links outside this library.
  if not target.is_relative_to(ROOT) or (target.name=='book.md' and 'sources' in target.parts):continue
  if target.is_file() and target not in files:files.add(target);queue.append(target)
if broken:raise ValueError(broken)
output=ROOT/'francais-en-pratique.zip'
with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as z:
 z.write(ROOT/('START-HERE.md' if (ROOT/'START-HERE.md').exists() else 'README.md'),'README.md')
 for p in sorted(files):
  if p==ROOT/'index.html':
   page=p.read_text();match=re.search(r'(<script id="library-data" type="application/json">)(.*?)(</script>)',page,re.S)
   data=json.loads(match[2]);data['sources']={}
   replacement=json.dumps(data,ensure_ascii=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
   page=page[:match.start(2)]+replacement+page[match.end(2):]
   z.writestr('index.html',page)
  elif p.suffix=='.md':
   def packaged_link(m):
    label,link=m.groups();target=(p.parent/link.split('#')[0]).resolve()
    if target.name=='book.md' and 'sources' in target.parts:return label+'（原书全文仅在本机完整版）'
    return m.group(0)
   z.writestr(str(p.relative_to(ROOT)),re.sub(r'\[([^]\n]+)\]\(([^)]+)\)',packaged_link,p.read_text()))
  else:z.write(p,str(p.relative_to(ROOT)))
with zipfile.ZipFile(output) as z:assert z.testzip() is None
print(json.dumps({'files':len(files)+1,'bytes':output.stat().st_size,'path':str(output)},ensure_ascii=False))
