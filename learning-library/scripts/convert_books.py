#!/usr/bin/env python3
"""Faithful local PDF -> Markdown/page chunks; OCR image-only pages; retain page images."""
from pathlib import Path
import concurrent.futures as cf
import hashlib, json, os, re, subprocess, tempfile, time
import pymupdf
import pymupdf4llm
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'learning-library' / 'sources'
NAMES = [('grammar','English Grammar'), ('phrasal-verbs','English Phrasal Verbs in Use ('), ('phrasal-verbs-advanced','English Phrasal Verbs in Use Advanced'), ('pronunciation-introduction','English Pronunciation In Use - Introduction'), ('pronunciation-elementary','English Pronunciation in Use - Elementary'), ('pronunciation-advanced','English Pronunciation in Use Advanced'), ('oxford-idioms','Oxford Word Skills')]

def ocr_page(job):
    source, idx, dest = job
    with tempfile.TemporaryDirectory(prefix='trccanada-ocr-') as tmp:
        doc=pymupdf.open(source)
        page=doc[idx]
        png=Path(tmp)/'page.png'
        page.get_pixmap(dpi=210).save(str(png))
        base=Path(tmp)/'ocr'
        subprocess.run(['tesseract',str(png),str(base),'-l','eng','--psm','3','pdf','txt','tsv'],check=True,capture_output=True,env={**os.environ,'OMP_THREAD_LIMIT':'1'})
        ocrdoc=pymupdf.open(str(base)+'.pdf')
        try:
            chunks=pymupdf4llm.to_markdown(ocrdoc,page_chunks=True,use_ocr=False,show_progress=False)
            text=chunks[0]['text']
        except Exception:
            text=Path(str(base)+'.txt').read_text()
        conf=[]
        for line in Path(str(base)+'.tsv').read_text().splitlines()[1:]:
            cells=line.split('\t')
            if len(cells)>=12 and cells[11].strip() and float(cells[10])>=0: conf.append(float(cells[10]))
        raw=Path(str(base)+'.txt').read_text()
        result={'text':text,'raw_text':raw,'mean_word_confidence':round(sum(conf)/len(conf),2) if conf else None}
        Path(dest).write_text(json.dumps(result,ensure_ascii=False,indent=2))
        return idx,result

def convert(slug,pdf):
    dest=OUT/slug
    for sub in ['pages','images','ocr']: (dest/sub).mkdir(parents=True,exist_ok=True)
    doc=pymupdf.open(pdf)
    native=[i for i,p in enumerate(doc) if len(p.get_text().strip())>=80]
    scan=[i for i in range(len(doc)) if i not in native]
    print(f'{slug}: {len(doc)} pages; {len(scan)} OCR candidates',flush=True)
    chunks=pymupdf4llm.to_markdown(doc,pages=native,page_chunks=True,use_ocr=False,show_progress=False) if native else []
    bypage={c['metadata']['page_number']-1:c for c in chunks}
    pending=[]
    ocr={}
    for i in scan:
        cache=dest/'ocr'/f'{i+1:04}.json'
        if cache.exists(): ocr[i]=json.loads(cache.read_text())
        else: pending.append((str(pdf),i,str(cache)))
    if pending:
        with cf.ProcessPoolExecutor(max_workers=4) as pool:
            for idx,result in pool.map(ocr_page,pending):
                ocr[idx]=result
                if len(ocr)%10==0: print(f'{slug}: OCR {len(ocr)}/{len(scan)}',flush=True)
    manifest={'id':slug,'source_file':pdf.name,'sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'pdf_pages':len(doc),'native_pages':len(native),'ocr_pages':len(scan),'conversion_status':'automatic-extraction-needs-review','tool_versions':{'pymupdf':pymupdf.VersionBind,'pymupdf4llm':str(pymupdf4llm.version)},'pdf_outline':doc.get_toc(),'pages':[]}
    book=[f'---\nbook_id: {slug}\nsource_file: {json.dumps(pdf.name,ensure_ascii=False)}\npdf_pages: {len(doc)}\nstatus: automatic-extraction-needs-review\n---\n\n# {slug}\n\n> Local source conversion. PDF page numbers are physical file pages, not printed page labels. Images and original PDFs are the authority for IPA, diagrams, tables and exercise alignment. No source audio was supplied.\n']
    records=[]
    toc=[]
    for i,page in enumerate(doc):
        n=i+1
        mode='ocr' if i in ocr else 'native-layout'
        result=ocr.get(i,{})
        text=result.get('text',bypage.get(i,{}).get('text','')).strip()
        # Nest source-generated headings under the physical-page heading.
        text=re.sub(r'(?m)^(#{1,6}) ',lambda m:'#'*min(len(m[1])+2,6)+' ',text)
        img=dest/'images'/f'{n:04}.jpg'
        if not img.exists(): page.get_pixmap(dpi=110).save(str(img),jpg_quality=78)
        review=['automatic-extraction','ipa-and-layout-unverified']
        if mode=='ocr':review.append('ocr-review-required')
        if len(text)<80:review.append('little-or-no-recognized-text')
        record={'book_id':slug,'pdf_page':n,'printed_page':None,'extraction':mode,'review_flags':review,'word_confidence':result.get('mean_word_confidence'),'text':text,'source_text':result.get('raw_text',page.get_text(sort=True)),'markdown_file':f'pages/{n:04}.md','image_file':f'images/{n:04}.jpg','layout_boxes':bypage.get(i,{}).get('page_boxes',[])}
        records.append(record)
        md=f'---\nbook_id: {slug}\npdf_page: {n}\nextraction: {mode}\nreview_required: true\n---\n\n## PDF page {n}\n\n[Original page image](../images/{n:04}.jpg)\n\n{text or "[No readable text recognized. Inspect page image.]"}\n'
        (dest/'pages'/f'{n:04}.md').write_text(md)
        book.append(f'\n## PDF page {n}\n\n<!-- extraction: {mode}; review_required: true -->\n\n[Original page image](images/{n:04}.jpg)\n\n{text or "[No readable text recognized. Inspect page image.]"}\n')
        manifest['pages'].append({k:record[k] for k in ['pdf_page','extraction','review_flags','word_confidence','markdown_file','image_file']})
        if 'contents' in text.lower() and i<12:
            toc.append(f'## Contents — PDF page {n}\n\n{text}\n')
    (dest/'book.md').write_text('\n'.join(book))
    (dest/'contents.md').write_text(f'# {slug}: extracted contents\n\n> Source order retained; automatic extraction, verify against page images.\n\n'+ '\n'.join(toc))
    (dest/'chunks.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in records))
    (dest/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    print(f'{slug}: COMPLETE',flush=True)
    return {k:manifest[k] for k in ['id','source_file','pdf_pages','native_pages','ocr_pages','conversion_status']}

if __name__=='__main__':
    OUT.mkdir(parents=True,exist_ok=True)
    summaries=[]
    for slug,prefix in NAMES:
        pdf=next(p for p in ROOT.glob('*.pdf') if p.name.startswith(prefix))
        summaries.append(convert(slug,pdf))
        (OUT/'inventory.json').write_text(json.dumps(summaries,ensure_ascii=False,indent=2))
    (OUT/'README.md').write_text('# Source library\n\nAutomatic local conversion with physical-page provenance. Native layout extraction plus Tesseract OCR for low-text pages. All pages retain images. Human review of phonetic symbols and exercise alignment remains necessary.\n\n'+ '\n'.join(f'- [{s["id"]}]({s["id"]}/book.md): {s["pdf_pages"]} pages; {s["ocr_pages"]} OCR pages; [contents]({s["id"]}/contents.md)' for s in summaries)+'\n')

    from finalize_sources import finalize
    finalize()
