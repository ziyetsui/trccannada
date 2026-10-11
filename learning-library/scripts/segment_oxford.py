"""Separate two-page spreads before OCR to preserve reading order and unit boundaries."""
from import_oxford import ROOT,DEST,SOURCE
from pathlib import Path
import pymupdf,subprocess,os,json,concurrent.futures
SECTIONS=[('1 · Starting out — Ça va ?',1,14),('2 · Asking the way — Pour aller… ?',15,28),('3 · Numbers, times and dates — Quel jour et à quelle heure ?',29,42),('Review 1',43,46),('4 · Accommodation — L’hébergement',47,60),('5 · Personal information — Renseignements personnels',61,74),('6 · Shopping — Dans les magasins',75,88),('7 · Eating out — Au restaurant',89,102),('Review 2',103,106),('8 · Getting around — En route',107,120),('9 · Health and fitness — En bonne santé',121,134),('10 · Free time — Les loisirs',135,148),('Review 3',149,152),('11 · At home — Chez nous',153,166),('12 · Making plans — Faire des projets',167,180),('13 · All in the past — Le passé',181,194),('14 · The world of work — Au travail',195,208),('Review 4',209,212),('Answers',213,223),('Grammar Summary',224,236),('Vocabulary',237,244),('Glossary of Grammatical Terms / Grammar index',245,248)]
# Answers are retained in reader unit19; lesson19 teaches using/checking answers, never invents missing CD.
def half(job):
 n,side=job;dest=DEST/'halves'/f'{n:04}-{side}.txt'
 if not dest.exists():
  with pymupdf.open(SOURCE) as d:
   p=d[n-1];r=p.rect;mid=(r.x0+r.x1)/2
   clip=pymupdf.Rect(r.x0 if side=='L' else mid,r.y0,mid if side=='L' else r.x1,r.y1)
   png=DEST/'ocr'/f'{n:04}-{side}.png';p.get_pixmap(dpi=240,clip=clip).save(png)
   result=subprocess.run(['tesseract',str(png),'stdout','--tessdata-dir','/tmp/trcc-tessdata','-l','fra+eng','--psm','3'],check=True,capture_output=True,text=True,env={**os.environ,'OMP_THREAD_LIMIT':'1'})
   dest.write_text(result.stdout);png.unlink()
 return n,side,dest.read_text()
def run():
 import hashlib
 if json.loads((DEST/'manifest.json').read_text())['sha256']!=hashlib.sha256(SOURCE.read_bytes()).hexdigest():raise ValueError('Source PDF changed; old half-page OCR cannot be reused.')
 (DEST/'halves').mkdir(exist_ok=True);(DEST/'units').mkdir(exist_ok=True)
 jobs=[(n,s) for n in range(1,132) for s in ['L','R']]
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:rows=list(pool.map(half,jobs))
 units=[{'unit':i,'title':title,'printed_start':start,'printed_end':end,'blocks':[]} for i,(title,start,end) in enumerate(SECTIONS,1)];front=[]
 for n,side,text in rows:
  printed=2*n-12+(side=='R') if n>=6 else None
  # This derived mapping was verified against the contents, unit1, and appendix headings.
  target=next((u for u in units if printed is not None and u['printed_start']<=printed<=u['printed_end']),None)
  blocks=target['blocks'] if target else front
  for j,part in enumerate(__import__('re').split(r'\n\s*\n',text.strip()),1):
   if part.strip():blocks.append({'id':f'OX-P{n:04}-{side}-B{j:03}','text':part,'lang':'mixed','role':'source','source_ref':f'PDF {n}, {side}, printed {printed}' if printed is not None and 1<=printed<=248 else f'PDF {n}, {side}, unnumbered front/back matter','pdf_page':n,'side':side,'printed_page':printed if printed and 1<=printed<=248 else None,'image_file':f'sources/oxford-take-off/images/{n:04}.jpg'})
 for u in units:
  (DEST/'units'/f'{u["unit"]:02}.md').write_text('# '+u['title']+'\n\n'+ '\n\n'.join('<!-- '+b['id']+'; '+b['source_ref']+' -->\n'+b['text'] for b in u['blocks']))
 reader={'book_id':'oxford-take-off','title':'Oxford Take Off in French','notice':'扫描本机器转录；法英混排与题目布局请核原图。未提供CD，TTS不是原录音。','units':units,'front_matter':front}
 issues=ROOT/'docs/oxford-reader-issues.json'
 if issues.exists():reader['issues']=json.loads(issues.read_text())
 (DEST/'reader.json').write_text(json.dumps(reader,ensure_ascii=False,indent=2))
 (DEST/'contents.md').write_text('# Oxford Take Off in French — 目录核对\n\n目录经PDF3页图核对。131个PDF页是双页扫描，PDF6右侧为印刷1页。正文按左右半页独立OCR以防跨栏混读。\n\n'+'\n'.join(f'- [{u["title"]}](units/{u["unit"]:02}.md)：印刷{u["printed_start"]}–{u["printed_end"]}，学习课T{u["unit"]:02}。' for u in units)+'\n')
 p=DEST/'manifest.json';m=json.loads(p.read_text());m.update({'contents_pdf_pages':[3],'reader_units':22,'half_page_chunks':len(rows),'printed_mapping':'n>=6: left 2*n-12, right 2*n-11; front/back outside numbered text may be blank','half_page_ocr':True});p.write_text(json.dumps(m,ensure_ascii=False,indent=2))
 print('Oxford segments',len(rows),'units',len(units),flush=True)
if __name__=='__main__':run()
