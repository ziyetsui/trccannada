"""Bind validated local illustrations to the exact sentence and mnemonic."""
import hashlib, json, re
from pathlib import Path
from PIL import Image

def apply_illustrations(lessons, manifest_path, root):
    def unique(pairs):
        data={}
        for k,v in pairs:
            if k in data:raise ValueError('duplicate illustration field: '+k)
            data[k]=v
        return data
    entries=json.loads(manifest_path.read_text(),object_pairs_hook=unique)
    expected={f'{l["id"]}:{i}':e for l in lessons if l['book']=='take-off'
              for i,e in enumerate(l['examples'],1)}
    if entries.keys()!=expected.keys():
        raise ValueError('illustration coverage mismatch')
    root=root.resolve();seen=set();updates=[]
    for key,example in expected.items():
        entry=entries[key];p=example['pronunciation']
        fields={'fr':example['fr'],'zh':example['zh'],'sound':p['sound_joke'],'movie':p['mental_movie']}
        if any(entry.get(k)!=v for k,v in fields.items()):
            raise ValueError('stale illustration: '+key)
        asset=entry.get('asset','')
        if not isinstance(asset,str) or not re.fullmatch(r'assets/[A-Za-z0-9_./-]+\.webp',asset):
            raise ValueError('unsafe illustration path: '+key)
        path=(root/asset).resolve()
        if root not in path.parents or '..' in Path(asset).parts:
            raise ValueError('unsafe illustration path: '+key)
        if path in seen:raise ValueError('reused illustration asset: '+key)
        seen.add(path)
        if not path.is_file():raise ValueError('missing illustration asset: '+key)
        try:
            with Image.open(path) as im:
                if im.format!='WEBP' or min(im.size)<128:
                    raise ValueError('unexpected format or dimensions')
                width,height=im.size;im.verify()
        except Exception:
            raise ValueError('invalid illustration asset: '+key) from None
        if entry.get('sha256') and hashlib.sha256(path.read_bytes()).hexdigest()!=entry['sha256']:
            raise ValueError('invalid illustration checksum: '+key)
        alt=entry.get('alt')
        if not isinstance(alt,str) or not alt.strip():raise ValueError('missing illustration alt: '+key)
        # A Chinese scene caption may name people, but never expose the complete answer.
        if example['fr'] in alt:raise ValueError('answer leaked in illustration alt: '+key)
        updates.append((example,{'id':key,'src':asset,'alt':alt,'width':width,'height':height}))
    for example,illustration in updates:example['illustration']=illustration
    return len(updates)
