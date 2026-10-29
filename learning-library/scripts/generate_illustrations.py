"""Generate authorized Oxford assets; persist jobs privately and never retry POSTs."""
import argparse, concurrent.futures, hashlib, io, json, os, re, time
from pathlib import Path
from urllib.request import Request, build_opener, HTTPRedirectHandler, urlopen
from urllib.error import HTTPError, URLError
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
MODEL = 'google/gemini-nano-banana-2.1/text-to-image'
ORIGIN = 'https://gptproto.com'
CATALOG = ROOT/'scripts/content/sentence-illustrations.json'

STYLE = '''Use case: illustration-story. Asset: a French sentence memory illustration for an adult absolute beginner, immediately understandable like a simple picture book.
Style: warm ivory background, bold charcoal outlines, flat hand-painted gouache, restrained teal and tangerine accents, friendly expressive ADULT characters, clear silhouettes, simple uncluttered setting, landscape 3:2. One coherent scene, not a comic strip, not a collage, no inset panels. The main action occupies most of the frame. No writing, letters, captions, speech bubbles, watermarks, logos or decorative typography anywhere.
Learning principle: illustrate the MEANING of the sentence clearly. Use the supplied Chinese sound-hook props only when they physically interact with the target action and make it easier to remember. Do not merely line up unrelated sound objects. Do not change the sentence's quantities, participants, negation, spatial relationships or intention. A memory aid must not misrepresent the meaning. The scene below describes a mnemonic, not a literal translation. Keep its central action and most helpful prop, remove incidental clutter. For temporal contrasts use a simple visual cue within one scene. For an abstract phrase, show an everyday situation making the meaning obvious. Never draw the French as text; it is typeset separately on the webpage.
'''

def save_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')
    tmp.replace(path)

def prepare():
    memories = json.loads((ROOT/'scripts/content/sentence-memories.json').read_text())
    existing = json.loads(CATALOG.read_text()) if CATALOG.exists() else {}
    entries = {}
    for key, m in memories.items():
        if not re.fullmatch(r'T\d{2}:\d+', key):
            continue
        prompt = STYLE+f'\nFrench target (context only): {m["fr"]}\nActual intended meaning: {m["zh"]}\nChinese approximate sound association (context only, never print): {m["sound"]}\nMnemonic action to visualize: {m["movie"]}\nDraw this specific action so the actual meaning is recoverable without reading.'
        entry = {**m, 'asset':f'assets/sentence-memory/{key.replace(":","-")}.webp',
                 'alt':m['movie'], 'prompt':prompt, 'model':MODEL}
        old = existing.get(key, {})
        if old and any(old.get(f)!=entry[f] for f in entry):
            raise ValueError('Manifest changed; review existing image before replacing '+key)
        entries[key] = old or entry
    if len(entries)!=163:
        raise ValueError('Expected 163 authorized Oxford examples')
    save_json(CATALOG, entries)
    print('Prepared 163 independent illustration prompts')

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None

def api(path, key, body=None):
    req = Request(ORIGIN+'/api/v3/'+path, data=json.dumps(body).encode() if body else None,
                  headers={'Authorization':'Bearer '+key, 'Content-Type':'application/json',
                           'User-Agent':'Mozilla/5.0 (compatible; FrenchLearningIllustrations/1.0)'})
    try:
        with build_opener(NoRedirect).open(req, timeout=60) as r:
            data=json.load(r)
    except HTTPError as e:
        raise RuntimeError('Provider HTTP '+str(e.code)) from None
    except (URLError, TimeoutError):
        raise RuntimeError('Provider connection interrupted; saved job requires review') from None
    if data.get('code') not in (None,0,200,'0','200'):
        raise RuntimeError('Provider rejected request, code '+str(data.get('code')))
    return data.get('data', data)

def generate(item, key, state_dir):
    sid, entry = item
    asset = ROOT/entry['asset']
    body={'prompt':entry['prompt'], 'aspect_ratio':'3:2', 'size':'1k',
          'output_formart':'png', 'enable_base64_output':False, 'enable_sync_mode':False}
    fingerprint=hashlib.sha256(json.dumps([MODEL,body],sort_keys=True).encode()).hexdigest()
    state_path=state_dir/(sid.replace(':','-')+'.json')
    state=json.loads(state_path.read_text()) if state_path.exists() else None
    if asset.exists():
        checksum=hashlib.sha256(asset.read_bytes()).hexdigest()
        expected=entry.get('sha256') or (state or {}).get('sha256')
        if not expected or checksum!=expected:
            raise RuntimeError('Existing asset checksum mismatch or missing; review before adoption: '+sid)
        recorded=entry.get('generation_fingerprint') or (state or {}).get('fingerprint')
        if recorded!=fingerprint:
            raise RuntimeError('Existing asset fingerprint differs; select a new version to regenerate: '+sid)
        with Image.open(asset) as im:
            im.verify()
        return sid, {'sha256':checksum,'generation_fingerprint':fingerprint}
    if state_path.exists():
        state=json.loads(state_path.read_text())
        if state.get('fingerprint')!=fingerprint or not state.get('id'):
            raise RuntimeError('Saved submission needs manual review: '+sid)
    else:
        state={'fingerprint':fingerprint, 'status':'submitting', 'created_at':time.time()}
        state_path.parent.mkdir(parents=True, exist_ok=True)
        with state_path.open('x') as f:
            json.dump(state, f)
        result=api(MODEL,key,body)
        if not isinstance(result.get('id'),str) or not result['id']:
            raise RuntimeError('Submission returned no task id: '+sid)
        state.update(id=result['id'],status='queued');save_json(state_path,state)
    deadline=time.time()+900
    while time.time()<deadline:
        result=api('predictions/'+state['id']+'/result',key)
        status=str(result.get('status','')).lower()
        state['status']=status;save_json(state_path,state)
        if status in ('completed','succeeded','success'):
            break
        if status in ('failed','error','cancelled','canceled') or result.get('error'):
            raise RuntimeError('Generation failed (no automatic paid retry): '+sid)
        if status not in ('created','queued','pending','starting','processing','running','in_progress','submitted'):
            raise RuntimeError('Unknown task state: '+sid)
        time.sleep(5)
    else:
        raise RuntimeError('Polling timed out; resume saved task: '+sid)
    outputs=result.get('outputs');out=outputs[0] if isinstance(outputs,list) and outputs else outputs
    url=out if isinstance(out,str) else (out or {}).get('url') or (out or {}).get('image_url')
    if not isinstance(url,str) or not url.startswith('https://'):
        raise RuntimeError('No supported media URL: '+sid)
    # Never send the provider key to the asset host.
    with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=90) as r:
        raw=r.read(25_000_001)
    if len(raw)>25_000_000:
        raise RuntimeError('Oversized image: '+sid)
    with Image.open(io.BytesIO(raw)) as im:
        im.load()
        if min(im.size)<512:
            raise RuntimeError('Unexpectedly small image: '+sid)
        asset.parent.mkdir(parents=True,exist_ok=True)
        im.convert('RGB').save(str(asset)+'.tmp',format='WEBP',quality=86)
        Path(str(asset)+'.tmp').replace(asset)
        dimensions=list(im.size)
    checksum=hashlib.sha256(asset.read_bytes()).hexdigest()
    state.update(status='downloaded',sha256=checksum);save_json(state_path,state)
    return sid, {'sha256':checksum,'generation_fingerprint':fingerprint,
                 'dimensions':dimensions,'generated_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare',action='store_true')
    parser.add_argument('--env-file',type=Path)
    parser.add_argument('--state-dir',type=Path)
    parser.add_argument('--limit',type=int,default=163)
    parser.add_argument('--workers',type=int,default=4)
    args=parser.parse_args()
    if args.prepare:
        prepare();return
    if not args.env_file or not args.state_dir:
        parser.error('--env-file and --state-dir are required for authorized generation')
    if ROOT in args.state_dir.resolve().parents:
        parser.error('Private task state must be outside the published site')
    secret=None
    for line in args.env_file.read_text().splitlines():
        m=re.match(r'\s*(?:export\s+)?GPTPROTO_API_KEY\s*=\s*(.*?)\s*$',line)
        if m:secret=m[1].strip('\"\'')
    if not secret:
        raise RuntimeError('GPTProto key not configured')
    entries=json.loads(CATALOG.read_text())
    items=list(entries.items())[:args.limit]
    errors=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1,min(8,args.workers))) as pool:
        futures={pool.submit(generate,item,secret,args.state_dir):item[0] for item in items}
        for f in concurrent.futures.as_completed(futures):
            sid=futures[f]
            try:
                sid,metadata=f.result();entries[sid].update(metadata);save_json(CATALOG,entries)
                print('READY',sid,flush=True)
            except Exception as e:
                errors.append(sid)
                # Exception type and our own sanitized message only. URLs/tokens aren't logged.
                print('FAILED',sid,type(e).__name__,str(e) if isinstance(e,RuntimeError) else '',flush=True)
    print(json.dumps({'requested':len(items),'ready':len(items)-len(errors),'failed':errors}))
    if errors:raise SystemExit(1)

if __name__=='__main__':
    main()
