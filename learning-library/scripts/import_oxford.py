"""Resumable French+English OCR with stable physical-page provenance."""
from pathlib import Path
import pymupdf,json,hashlib,subprocess,os,concurrent.futures,time
ROOT=Path(__file__).resolve().parents[1];DEST=ROOT/'sources/oxford-take-off'
SOURCE=next(Path('/Users/ziye/Downloads').glob('Oxford take off in French*.pdf'))

def page_job(i):
 n=i+1;raw=DEST/'raw'/f'{n:04}.txt';image=DEST/'images'/f'{n:04}.jpg'
 if raw.exists() and image.exists():return n
 with pymupdf.open(SOURCE) as doc:
  page=doc[i]
  if not image.exists():page.get_pixmap(dpi=150).save(image,jpg_quality=85)
  if not raw.exists():
   png=DEST/'ocr'/f'{n:04}.png';page.get_pixmap(dpi=240).save(png)
   result=subprocess.run(['tesseract',str(png),'stdout','--tessdata-dir','/tmp/trcc-tessdata','-l','fra+eng','--psm','3'],check=True,capture_output=True,text=True,env={**os.environ,'OMP_THREAD_LIMIT':'1'})
   raw.write_text(result.stdout);png.unlink()
 return n

def convert():
 existing=DEST/'manifest.json'
 if existing.exists() and json.loads(existing.read_text())['sha256']!=hashlib.sha256(SOURCE.read_bytes()).hexdigest():raise ValueError('Source PDF changed: move existing source output to a backup before reconverting; stale OCR will not be reused.')
 for sub in ['raw','images','ocr','pages']:(DEST/sub).mkdir(exist_ok=True,parents=True)
 with pymupdf.open(SOURCE) as doc:n=len(doc)
 start=time.time()
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
  for k,num in enumerate(pool.map(page_job,range(n)),1):
   if k%10==0:print(f'Oxford OCR {k}/{n}; {time.time()-start:.0f}s',flush=True)
 records=[];book=['# Oxford Take Off in French — 完整逐页 OCR', '', '> 用户提供131页扫描本。法英双语机器识别；音标、表格、题目与答案对应需回查原图。PDF物理页不等于印刷页；未提供CD或配套音频。', '']
 for num in range(1,n+1):
  text=(DEST/'raw'/f'{num:04}.txt').read_text()
  md=f'## PDF 第 {num} 页\n\n[原页图](../images/{num:04}.jpg)\n\n```text\n{text}\n```\n'
  (DEST/'pages'/f'{num:04}.md').write_text(md)
  book.extend([f'## PDF 第 {num} 页', '', f'[原页图](images/{num:04}.jpg)', '', '```text',text,'```',''])
  records.append({'book_id':'oxford-take-off','pdf_page':num,'printed_page':None,'extraction':'ocr-fra-eng','source_text':text,'text':text,'markdown_file':f'pages/{num:04}.md','raw_file':f'raw/{num:04}.txt','image_file':f'images/{num:04}.jpg','review_flags':['machine-ocr','exercise-layout-unverified','source-audio-not-supplied']})
 (DEST/'book.md').write_text('\n'.join(book))
 (DEST/'chunks.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in records))
 manifest={'id':'oxford-take-off','title':'Oxford Take Off in French','source_file':str(SOURCE),'sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'pdf_pages':n,'native_pages':0,'ocr_pages':n,'conversion_status':'automatic-extraction-needs-review','ocr_language':'fra+eng','dpi':240,'pages':records,'contents_pdf_pages':[]}
 (DEST/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
 print('Oxford complete',n,flush=True)
if __name__=='__main__':convert()
