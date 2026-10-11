"""Prepare Pages from the reviewed local research edition and course ZIP."""
from pathlib import Path
import argparse, re, shutil, zipfile
p=argparse.ArgumentParser();p.add_argument('--research-root',type=Path,required=True);p.add_argument('--library-root',type=Path,required=True);a=p.parse_args()
root=Path(__file__).resolve().parents[1]
page=(a.research_root/'artifacts/英法汉对比研究.html').read_text()
# Published at the repository root, rather than under local artifacts/.
page=page.replace('href="../docs/','href="docs/')
# PDFs and research download caches are local archives, not deployed assets.
def local_link(m):
 href,label=m.groups()
 if '.pdf' in href.lower() or '/literature' in href or '/search-logs' in href:
  return '<span title="此资料保留在本机研究档案">'+label+'（本机档案）</span>'
 return m.group(0)
page=re.sub(r'<a\b[^>]*href="([^"]+)"[^>]*>(.*?)</a>',local_link,page,flags=re.S)
page=page.replace('<main id="top">','<main id="top"><p style="padding:1rem;border:1px solid var(--rule);border-radius:8px"><a href="learning-library/">进入法语学习库 → 9 册 · 230 课</a> · 支持法语朗读、练习和明暗模式</p>')
(root/'index.html').write_text(page)
for rel in ['research/英法汉对比研究-研究稿.md','research/文献目录与证据状态.md','research/三语平行语料核验.md','research/检索方法与后续研究.md','research/质量检查记录.md','source/原书目录与页码.md','source/英汉对比研究-结构化OCR.md','source/英汉对比研究-逐页OCR.md','research/example-audit/coverage.md']:
 dest=root/'docs'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(a.research_root/'docs'/rel,dest)
(root/'learning-library').mkdir(exist_ok=True)
with zipfile.ZipFile(a.library_root/'francais-en-pratique.zip') as z, zipfile.ZipFile(root/'learning-library/francais-en-pratique.zip','w',zipfile.ZIP_DEFLATED) as clean:
 for info in z.infolist():
  if any(part.startswith('.') for part in Path(info.filename).parts):continue
  data=z.read(info.filename);dest=root/'learning-library'/info.filename;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data);clean.writestr(info.filename,data)
path=root/'learning-library/index.html';s=path.read_text();s=s.replace('<body>','<body><a href="../" style="display:block;padding:.65rem 1rem;color:inherit">← 英法汉对比研究</a>',1);path.write_text(s)
print('Prepared root edition and 230-lesson public library')
# Source-preservation checks require the private originals; keep course tests active.
test=root/'learning-library/tests/test_additional_sources.py'
s=test.read_text().replace('class AdditionalSourceTests', '@unittest.skipUnless((ROOT/"sources/french-stories/reader.json").exists(), "Full-source checks run in the local edition")\nclass AdditionalSourceTests')
test.write_text(s)
