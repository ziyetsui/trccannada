# -*- coding: utf-8 -*-
"""Merge new import ledgers without altering the existing seven source mappings."""
from pathlib import Path
import json,hashlib
from build_site import ROOT,load_library,validate_library

def finalize():
 inventory=json.loads((ROOT/'sources/inventory.json').read_text())
 inventory=[x for x in inventory if x['id'] not in ['french-stories','oxford-take-off']]
 coverage=json.loads((ROOT/'french/coverage.json').read_text())
 coverage['records']=[x for x in coverage['records'] if x['source_book'] not in ['french-stories','oxford-take-off']]
 for bid,prefix in [('french-stories','S'),('oxford-take-off','T')]:
  dest=ROOT/'sources'/bid;m=json.loads((dest/'manifest.json').read_text());reader=json.loads((dest/'reader.json').read_text())
  inventory.append({k:m[k] for k in ['id','source_file','conversion_status']})
  inventory[-1].update({'format':'epub' if bid=='french-stories' else 'pdf','sha256':m['sha256'],'reader_units':len(reader['units'])})
  if bid=='french-stories':inventory[-1].update({'spine_documents':m['spine_documents'],'story_units':40})
  else:inventory[-1].update({'pdf_pages':131,'native_pages':0,'ocr_pages':131})
  coverage['source_counts'][bid]=len(reader['units'])
  for u in reader['units']:
   coverage['records'].append({'source_book':bid,'source_unit':u['unit'],'source_title':u['title'],'targets':[f'{prefix}{u["unit"]:02}'],'source_body_available':True,'adaptation':'完整法语底本按原序保留；新课另编中文解释、幼儿类比、法语例句与理解/语言练习。原题与原答案在原文标签，不冒充新题或原录音。'})
 (ROOT/'sources/inventory.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2))
 (ROOT/'french/coverage.json').write_text(json.dumps(coverage,ensure_ascii=False,indent=2))
 lines=['# 原书框架对应', '', '原七册505条框架对应保留；新增40篇故事与Oxford22个单元/复习/附录入口，合计567条。七册原创法语课为主题适配；两份新增资料已是法语，全文另存并配中文辅助。以下是框架条目，不是原书全部例句数。', '']
 for bid in coverage['source_counts']:
  lines.extend(['## '+bid, ''])
  for r in coverage['records']:
   if r['source_book']==bid:lines.append(f'- {r["source_unit"]} · {r.get("source_title", "原书单元")} → '+', '.join(r['targets'])+'；'+r['adaptation'])
 (ROOT/'french/coverage.md').write_text('\n'.join(lines)+'\n')
 lessons=load_library(ROOT/'french');validate_library(lessons,ROOT/'french/coverage.json')
 (ROOT/'french/catalogue.json').write_text(json.dumps([{k:v for k,v in l.items() if k not in ['markdown','explanation','analogy','application','examples','quiz','references','goal']} for l in lessons],ensure_ascii=False,indent=2))
 print(json.dumps({'books':9,'lessons':len(lessons),'coverage':len(coverage['records']),'sources':len(inventory)},ensure_ascii=False))
if __name__=='__main__':finalize()
