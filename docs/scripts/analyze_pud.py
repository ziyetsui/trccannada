#!/usr/bin/env python3
from pathlib import Path
import urllib.request,hashlib,json,csv,concurrent.futures
ROOT=Path(__file__).resolve().parents[2]; OUT=ROOT/'docs/research/corpus';OUT.mkdir(exist_ok=True)
VERSION='r2.16'
LANGS={'en':'English','fr':'French','zh':'Chinese'}
def load(item):
 lang,name=item;url=f'https://raw.githubusercontent.com/UniversalDependencies/UD_{name}-PUD/{VERSION}/{lang}_pud-ud-test.conllu'
 p=OUT/f'{lang}_pud-ud-test.conllu'
 if not p.exists():p.write_bytes(urllib.request.urlopen(url,timeout=40).read())
 data=p.read_bytes();sents=[]
 for block in data.decode().strip().split('\n\n'):
  rows=[x.split('\t') for x in block.splitlines() if x and not x.startswith('#') and x.split('\t')[0].isdigit()]
  if not rows:continue
  meta=dict(x[2:].split(' = ',1) for x in block.splitlines() if x.startswith('# ') and ' = ' in x)
  sents.append({'id':meta.get('sent_id'),'text':meta.get('text'),'rows':rows})
 stats={'language':lang,'sentences':len(sents),'syntactic_words':sum(len(s['rows']) for s in sents)}
 predicates={
 'sent_with_passive_annotation':lambda r: ':pass' in r[7] or 'Voice=Pass' in r[5],
 'sent_with_pronoun':lambda r:r[3]=='PRON',
 'sent_with_subordinator':lambda r:r[3]=='SCONJ',
 'sent_with_advcl':lambda r:r[7].split(':')[0]=='advcl',
 'sent_with_relative_clause':lambda r:r[7]=='acl:relcl',
 'sent_with_tense_feature':lambda r:'Tense=' in r[5],
 'sent_with_gender_feature':lambda r:'Gender=' in r[5],
 'sent_with_number_feature':lambda r:'Number=' in r[5]}
 for k,test in predicates.items():stats[k]=sum(any(test(r) for r in s['rows']) for s in sents)
 return lang,stats,{'url':url,'release':VERSION,'sha256':hashlib.sha256(data).hexdigest()},sents
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex: results=list(ex.map(load,LANGS.items()))
 stats={l:s for l,s,m,ss in results};manifest={l:m for l,s,m,ss in results}
 assert all(s['sentences']==1000 for s in stats.values())
 ids=[[s['id'] for s in ss] for l,st,m,ss in results]
 assert ids[0]==ids[1]==ids[2], 'Sentence IDs not aligned'
 (OUT/'stats.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2)+'\n');(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 with (OUT/'sentence-flags.csv').open('w') as f:
  w=csv.writer(f);w.writerow(['language','sent_id','passive','pronoun','sconj','advcl','relcl','text'])
  for l,st,m,ss in results:
   for s in ss:
    rr=s['rows'];w.writerow([l,s['id'],int(any(':pass' in r[7] or 'Voice=Pass' in r[5] for r in rr)),int(any(r[3]=='PRON' for r in rr)),int(any(r[3]=='SCONJ' for r in rr)),int(any(r[7].split(':')[0]=='advcl' for r in rr)),int(any(r[7]=='acl:relcl' for r in rr)),s['text']])
 print(json.dumps(stats,ensure_ascii=False,indent=2))
