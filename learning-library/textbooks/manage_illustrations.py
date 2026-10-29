"""Prepare individual built-in image_gen jobs and import their completed artifacts.

This script never calls a paid API. Generation is through the host tool, one call
per illustration. Imports are sequential and keep the original generated PNG.
"""
import argparse
import datetime
import fcntl
import hashlib
import json
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parent
STYLE='''Use case: illustration-story. Asset: ONE final French sentence memory illustration for an adult beginner, understandable like a simple picture book. Landscape 3:2.
EXACT VISUAL STYLE: a very SIMPLE FLAT PICTURE BOOK drawing, large warm IVORY EMPTY BACKGROUND; BOLD DARK CHARCOAL outlines; flat opaque gouache paint with ONLY a few muted TEAL and TANGERINE areas. Simple friendly expressive ADULT cartoon faces, readable large hands and silhouettes. Almost no shading, no photorealism, no 3D, no elaborate wood textures, no glossy lighting, no ornate furniture, no decorative plants, no scenic clutter. Main action fills most of frame.
One coherent scene, NEVER a collage, comic strip, inset panel or unrelated lineup of objects. Use the sound-hook prop ONLY if it physically participates in the target action, never as arbitrary decoration. Favor ONE especially helpful prop; remove incidental clutter. Preserve the actual sentence's people, quantities, negation, direction, time relation and communicative intention.
NO writing, letters, captions, phonetic Chinese labels, French words, speech bubbles, watermarks or logos ANYWHERE. Names and labels in the memory story are context only; NEVER print them. If spelling/numbers/time are themselves the learning target, only essential concrete letters/digits on actual objects may be shown, with exact quantities checked. Otherwise use clear physical actions, gestures and nonverbal cues.
'''
def dump(path,value):
    temp=path.with_suffix(path.suffix+'.tmp')
    temp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    temp.replace(path)
def current_lessons():
    return {l['id']:l for p in sorted((ROOT/'content').glob('*.json'))
            for l in json.loads(p.read_text())['lessons']}
def prompt_for(lesson):
    a=lesson['anchor']
    return STYLE+f'\nFrench target (context only; NEVER print): {a["fr"]}\nExact intended meaning: {a["zh"]}\nApproximate Chinese sound association (context only; NEVER print): {a["sound"]}\nMemory action to visualize: {a["movie"]}\nDraw this specific action so the meaning can be recalled without reading. The linguistic target takes priority if any incidental story detail conflicts with its meaning.'
def prepare():
    complete=json.loads((ROOT/'illustrations.json').read_text()) if (ROOT/'illustrations.json').exists() else {}
    jobs=[]
    for lid,lesson in current_lessons().items():
        a=lesson['anchor']
        if a.get('reuse_id'):continue
        e=complete.get(lid)
        if e and all(e.get(k)==a[k] for k in ('fr','zh','sound','movie')) and (ROOT/e['asset']).is_file():
            continue
        jobs.append({'id':lid,**{k:a[k] for k in ('fr','zh','sound','movie')},'prompt':prompt_for(lesson)})
    dump(ROOT/'illustration-jobs.json',jobs)
    print(json.dumps({'pending':len(jobs),'ids':[j['id'] for j in jobs]},ensure_ascii=False))
def _import_image(lid,source,prompt=None,revision=None):
    a=current_lessons()[lid]['anchor']
    path=Path(source)
    dest=ROOT/'assets'/(lid+'.webp');dest.parent.mkdir(exist_ok=True)
    manifest_path=ROOT/'illustrations.json'
    entries=json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    if not revision and lid in entries and all(entries[lid].get(k)==a[k] for k in ('fr','zh','sound','movie')) and dest.exists():
        print(json.dumps({'id':lid,'status':'already_imported'}));return
    previous=entries.get(lid)
    if dest.exists():
        version=2
        while (ROOT/'assets'/f'{lid}-v{version}.webp').exists():version+=1
        dest=ROOT/'assets'/f'{lid}-v{version}.webp'
    with Image.open(path) as im:
        if min(im.size)<128:raise ValueError('Image too small')
        im.convert('RGB').save(dest,'WEBP',quality=92,method=6)
        dimensions=list(im.size)
    entries[lid]={**{k:a[k] for k in ('fr','zh','sound','movie')},'asset':'assets/'+dest.name,
                  'alt':'记忆场景：'+a['movie'],
                  'prompt':prompt or prompt_for(current_lessons()[lid]),
                  'model':'image_gen built-in (underlying model not exposed)',
                  'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),
                  'original_png_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                  'dimensions':dimensions,'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  'generation_fingerprint':hashlib.sha256(json.dumps({k:a[k] for k in ('fr','zh','sound','movie')},ensure_ascii=False,sort_keys=True).encode()).hexdigest(),
                  'visual_review':'pending'}
    if previous:
        entries[lid]['previous_versions']=previous.get('previous_versions',[])+[
            {k:v for k,v in previous.items() if k!='previous_versions'}]
        entries[lid]['revision_reason']=revision or 'Anchor binding corrected; new artifact imported and prior asset preserved.'
    dump(manifest_path,entries)
    print(json.dumps({'id':lid,'status':'imported','asset':str(dest.relative_to(ROOT)),'dimensions':dimensions}))
def import_image(lid,source,prompt=None,revision=None):
    with (ROOT/'.illustrations.lock').open('a') as lock:
        fcntl.flock(lock.fileno(),fcntl.LOCK_EX)
        _import_image(lid,source,prompt,revision)
        state_path=ROOT/'.generation-state.json'
        state=json.loads(state_path.read_text()) if state_path.exists() else {}
        state[lid]={'status':'imported'}
        dump(state_path,state)
def claim(limit):
    with (ROOT/'.illustrations.lock').open('a') as lock:
        fcntl.flock(lock.fileno(),fcntl.LOCK_EX)
        state_path=ROOT/'.generation-state.json'
        state=json.loads(state_path.read_text()) if state_path.exists() else {}
        entries=json.loads((ROOT/'illustrations.json').read_text()) if (ROOT/'illustrations.json').exists() else {}
        jobs=[]
        for lid,lesson in current_lessons().items():
            if lesson['anchor'].get('reuse_id') or lid in entries or state.get(lid,{}).get('status')=='running':continue
            a=lesson['anchor'];jobs.append({'id':lid,'prompt':prompt_for(lesson)})
            state[lid]={'status':'running','claimed_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
            if len(jobs)>=limit:break
        dump(state_path,state)
    print(json.dumps(jobs,ensure_ascii=False))
def approve(ids,note):
    with (ROOT/'.illustrations.lock').open('a') as lock:
        fcntl.flock(lock.fileno(),fcntl.LOCK_EX)
        path=ROOT/'illustrations.json';entries=json.loads(path.read_text())
        for lid in ids.split(','):
            entries[lid]['visual_review']='approved'
            entries[lid]['visual_review_note']=note
        dump(path,entries)
    print(json.dumps({'approved':ids.split(',')}))
def sheet(limit,prefix=None):
    entries=json.loads((ROOT/'illustrations.json').read_text())
    ids=[lid for lid,e in entries.items() if e.get('visual_review')!='approved' and (not prefix or lid.startswith(prefix))][:limit]
    if not ids:
        print(json.dumps({'ids':[]}));return
    width=1800;cellw=600;cellh=470
    canvas=Image.new('RGB',(width,((len(ids)+2)//3)*cellh),'#f7f5ef');draw=ImageDraw.Draw(canvas)
    font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',22)
    for i,lid in enumerate(ids):
        e=entries[lid];x=(i%3)*cellw+10;y=(i//3)*cellh+85
        im=Image.open(ROOT/e['asset']);im.thumbnail((580,380));canvas.paste(im,(x,y))
        draw.multiline_text((x,y-76),'\n'.join(textwrap.wrap(lid+' | '+e['fr'],width=47)),font=font,fill='#263b34',spacing=3)
    out=ROOT.parents[3]/'artifacts/french-textbooks-20261027';out.mkdir(parents=True,exist_ok=True)
    path=out/('review-'+ids[0]+'-'+ids[-1]+'.jpg');canvas.save(path,quality=94)
    print(json.dumps({'ids':ids,'path':str(path)},ensure_ascii=False))
if __name__=='__main__':
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest='cmd',required=True);sub.add_parser('prepare')
    c=sub.add_parser('claim');c.add_argument('--limit',type=int,default=6)
    a=sub.add_parser('approve');a.add_argument('--ids',required=True);a.add_argument('--note',required=True)
    s=sub.add_parser('sheet');s.add_argument('--limit',type=int,default=9);s.add_argument('--prefix')
    i=sub.add_parser('import');i.add_argument('--id',required=True);i.add_argument('--source',required=True);i.add_argument('--prompt-file');i.add_argument('--revision')
    args=p.parse_args()
    if args.cmd=='prepare':prepare()
    elif args.cmd=='claim':claim(args.limit)
    elif args.cmd=='approve':approve(args.ids,args.note)
    elif args.cmd=='sheet':sheet(args.limit,args.prefix)
    else:import_image(args.id,args.source,Path(args.prompt_file).read_text() if args.prompt_file else None,args.revision)
