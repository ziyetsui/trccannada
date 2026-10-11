#!/usr/bin/env python3
"""Retain raw text, readable OCR transcripts, complete continued contents and audit files."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'learning-library'/'sources'
CONTENTS={'grammar':[5,6,7,8],'phrasal-verbs':[4,5],'phrasal-verbs-advanced':[4,5],'pronunciation-introduction':[3,4],'pronunciation-elementary':[4,5],'pronunciation-advanced':[2,3],'oxford-idioms':[3,4]}

def finalize():
 report={'total_books':0,'total_pages':0,'ocr_pages':0,'native_pages':0,'errors':[],'books':[],'scope':'file coverage and integrity; not a human proofread'}
 for book in json.loads((OUT/'inventory.json').read_text()):
  slug=book['id'];dest=OUT/slug
  manifest=json.loads((dest/'manifest.json').read_text())
  rows=[json.loads(line) for line in (dest/'chunks.jsonl').read_text().splitlines()]
  (dest/'raw').mkdir(exist_ok=True)
  combined=[f'---\nbook_id: {slug}\nsource_file: {json.dumps(book["source_file"])}\npdf_pages: {len(rows)}\nstatus: automatic-extraction-needs-review\n---\n\n# {slug}\n\n> 自动抽取资料，尚未逐页校订。PDF page 是物理页码。音标、表格、图示与题目配对请核对原页。OCR 页采用纯文本转录，避免自动表格转换造成单词粘连。\n']
  table_count=0;low=[];confidence=[]
  for rec in rows:
   n=rec['pdf_page'];raw=rec['source_text']
   if 'layout_markdown' not in rec:rec['layout_markdown']=rec['text']
   if rec['extraction']=='ocr':
    rec['text']='### OCR transcription\n\n```text\n'+raw.strip()+'\n```'
    if rec.get('word_confidence') is not None:confidence.append(rec['word_confidence'])
   if re.search(r'(?m)^\|.*\|$',rec['layout_markdown']):
    table_count+=1
    if 'table-alignment-review-required' not in rec['review_flags']:rec['review_flags'].append('table-alignment-review-required')
   rec['raw_file']=f'raw/{n:04}.txt'
   (dest/rec['raw_file']).write_text(raw)
   links=f'[Original page image](../images/{n:04}.jpg) · [Raw text](../raw/{n:04}.txt)'
   body=rec['text'] or '[No readable text recognized. Inspect page image.]'
   md=f'---\nbook_id: {slug}\npdf_page: {n}\nextraction: {rec["extraction"]}\nreview_required: true\n---\n\n## PDF page {n}\n\n{links}\n\n{body}\n'
   (dest/rec['markdown_file']).write_text(md)
   combined.append(f'\n## PDF page {n}\n\n<!-- extraction: {rec["extraction"]}; review_required: true -->\n\n[Original page image](images/{n:04}.jpg) · [Raw text](raw/{n:04}.txt)\n\n{body}\n')
   for item in [rec['markdown_file'],rec['image_file'],rec['raw_file']]:
    if not (dest/item).is_file():report['errors'].append(f'{slug}: missing {item}')
   if len(raw.strip())<80:low.append(n)
   manifest['pages'][n-1].update({'raw_file':rec['raw_file'],'review_flags':rec['review_flags']})
  (dest/'book.md').write_text('\n'.join(combined))
  (dest/'chunks.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))
  manifest['contents_pdf_pages']=CONTENTS[slug]
  manifest['ocr_display']='plain-text transcript; layout_markdown retained in chunks.jsonl for comparison'
  (dest/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
  contents=[f'# {slug}: source contents\n\n> 包含续页；编号与音标尚须核对页图。目录纯文本保留原始阅读顺序，不伪装为人工校订的目录。\n']
  for n in CONTENTS[slug]:
   rec=rows[n-1]
   contents.append(f'## PDF page {n}\n\n[Page image](images/{n:04}.jpg) · [Extracted Markdown](pages/{n:04}.md)\n\n```text\n{rec["source_text"].strip()}\n```\n')
  (dest/'contents.md').write_text('\n'.join(contents))
  if len(rows)!=book['pdf_pages']:report['errors'].append(f'{slug}: count mismatch')
  if [r['pdf_page'] for r in rows]!=list(range(1,book['pdf_pages']+1)):report['errors'].append(f'{slug}: page sequence mismatch')
  if hashlib.sha256((ROOT/book['source_file']).read_bytes()).hexdigest()!=manifest['sha256']:report['errors'].append(f'{slug}: source hash mismatch')
  if len(re.findall(r'^## PDF page \d+$',(dest/'book.md').read_text(),flags=re.M))!=book['pdf_pages']:report['errors'].append(f'{slug}: full markdown page count mismatch')
  report['total_books']+=1;report['total_pages']+=len(rows)
  report['ocr_pages']+=book['ocr_pages'];report['native_pages']+=book['native_pages']
  report['books'].append({**book,'pages_with_layout_tables':table_count,'low_text_pages':low,'mean_ocr_page_confidence':round(sum(confidence)/len(confidence),2) if confidence else None})
 report['passed']=not report['errors'] and report['total_books']==7 and report['total_pages']==1369
 (OUT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
 lines=['# 转换完整性报告','',f'- 书籍：{report["total_books"]}','- 检查范围：文件存在、页数、连续页码、原文件哈希；不等于逐字校订。',f'- 总页数：{report["total_pages"]}；原生文本页：{report["native_pages"]}；OCR 页：{report["ocr_pages"]}。',f'- 完整性检查：{"通过" if report["passed"] else "未通过"}。','', '| 书目 ID | 页数 | OCR 页 | 少字页 | 含自动表格页 |','|---|---:|---:|---|---:|']
 for b in report['books']:lines.append(f'| {b["id"]} | {b["pdf_pages"]} | {b["ocr_pages"]} | {", ".join(map(str,b["low_text_pages"])) or "无"} | {b["pages_with_layout_tables"]} |')
 lines+=['','少字页已保留页图；封面、空白和含图页不自动删除。含表格页须核对行列和题干选项。OCR 平均词置信度不代表音标准确率。','', '## 抽样视觉检查','', '- Grammar：PDF 第 14 页，讲解、例句可读；并排动词形式的文本抽取失去部分对齐，应参考页图。','- Phrasal Verbs Advanced：PDF 第 9 页，主要段落可读；嵌入式新闻标题的阅读顺序与杂字符需校订。','- Pronunciation Elementary：PDF 第 12 页，练习表格和音标 OCR 有错误；不能直接拿来自动判题。已保留原页并将 OCR 原始转录作为主要显示文本。','- Elementary 目录：PDF 第 4–5 页，有 50 个单元及参考附录；自动 Markdown 表格存在单词粘连，目录改为纯文本显示并保留页图。','', '## 后续编辑边界','', '当前输出是可检索的来源资料，不是经过校订的学习教材。后续法语内容必须使用独立单元文件，核验规则并原创例句、练习与答案。']
 (OUT/'verification.md').write_text('\n'.join(lines)+'\n')
 print(json.dumps({k:report[k] for k in ['passed','total_books','total_pages','native_pages','ocr_pages','errors']},ensure_ascii=False))
 if not report['passed']:raise SystemExit(1)

if __name__=='__main__':finalize()
