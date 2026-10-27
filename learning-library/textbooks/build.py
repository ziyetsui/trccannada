"""Build original companions; publication refuses unbound or stale illustrations."""
import argparse
import hashlib
import html
import json
import re
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent
LIBRARY = ROOT.parent
SOURCE_NAMES = {
    'jianming-french-volume-1': '简明法语教程上（修订版）',
    'jianming-french-volume-2': '简明法语教程下（修订版）',
    'nihao-a1-student': '你好！法语1·A1学生用书',
    'nihao-b1-student': '你好法语3·B1学生用书',
    'nihao-b1-teacher': '你好法语3·B1教师用书',
    'nihao-4-student': '你好法语4·B1续篇学生用书',
}
EXPECTED_IDS={
    'nihao-a1':{f'NA0{c}' for c in 'ABCD'}|{f'NA1{i:02d}' for i in range(1,37)}|{f'NA1R{i:02d}' for i in range(1,10)},
    'jianming-1':{f'JM1{i:02d}' for i in range(1,31)}|{'JM1R01','JM1R02'},
    'jianming-2':{f'JM2{i:02d}' for i in range(1,29)}|{f'JM2R{i:02d}' for i in range(1,4)},
    'nihao-b1':{f'NB1{i:02d}' for i in range(1,25)}|{f'NB1R{i:02d}' for i in range(1,7)}|{'NB1E01','NB1E02'},
    'nihao-4':{f'N4{i}' for i in range(25,49)}|{f'N4R{i:02d}' for i in range(1,7)}|{'N4E03','N4E04'},
}
def validate_coverage(books):
    if {b['id'] for b in books}!=set(EXPECTED_IDS):
        raise ValueError('source coverage: expected all five learner tracks')
    for book in books:
        actual={l['id'] for l in book['lessons']};expected=EXPECTED_IDS[book['id']]
        if actual!=expected:
            raise ValueError('source coverage mismatch: '+book['id']+' missing '+str(sorted(expected-actual))+' extra '+str(sorted(actual-expected)))
def read_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result: raise ValueError('duplicate JSON key: '+key)
            result[key] = value
        return result
    return json.loads(path.read_text(), object_pairs_hook=unique)

def validate_books(books, library_root=LIBRARY, allow_pending=False):
    library_root = Path(library_root)
    reused = read_json(library_root/'scripts/content/sentence-illustrations.json')
    generated_file = library_root/'textbooks/illustrations.json'
    generated = read_json(generated_file) if generated_file.exists() else {}
    ids, book_ids, asset_owners = set(), set(), {}
    for book in books:
        if book['id'] in book_ids: raise ValueError('duplicate book id')
        book_ids.add(book['id'])
        if not book['lessons']: raise ValueError('empty course book')
        for lesson in book['lessons']:
            lid = lesson['id']
            if not re.fullmatch(r'[A-Z0-9]+', lid) or lid in ids:
                raise ValueError('duplicate or invalid lesson id: '+lid)
            ids.add(lid)
            for field in ('title','source_title','goal','explanation','analogy','application'):
                if not isinstance(lesson.get(field),str) or not lesson[field].strip():
                    raise ValueError(f'{lid}: missing {field}')
            if not lesson.get('self_check') or len(lesson.get('teaching_points',[]))<2:
                raise ValueError(lid+': incomplete teaching or self-check')
            if not lesson.get('sources'): raise ValueError(lid+': missing source locator')
            for source in lesson['sources']:
                loc = source['location']
                if source['book'] not in SOURCE_NAMES or not re.fullmatch(r'(?:pages/\d{4}|chapters/\d{3}-\d{3})\.md',loc):
                    raise ValueError(lid+': unsafe or unknown source location')
                if not source.get('label'): raise ValueError(lid+': missing source label')
            if len(lesson['quiz'])<2: raise ValueError(lid+': insufficient quiz')
            for q in lesson['quiz']:
                if (not q['prompt'] or not q['reason'] or len(q['choices'])<2
                    or len(set(q['choices']))!=len(q['choices'])
                    or type(q['answer']) is not int or not 0<=q['answer']<len(q['choices'])):
                    raise ValueError(lid+': invalid quiz answer or choices')
            anchor = lesson['anchor']
            for field in ('fr','zh','sound','movie','pronunciation'):
                if not anchor.get(field): raise ValueError(lid+': missing anchor '+field)
            reuse_id = anchor.get('reuse_id')
            if reuse_id:
                if reuse_id not in reused: raise ValueError(lid+': unknown illustration reuse')
                entry = reused[reuse_id]
                prefix, image_root = '../', library_root
            else:
                entry = generated.get(lid)
                prefix, image_root = '', library_root/'textbooks'
            if entry is None:
                if allow_pending:
                    anchor['illustration'] = None
                    continue
                raise ValueError(lid+': missing illustration image')
            if any(entry.get(k)!=anchor[k] for k in ('fr','zh','sound','movie')):
                if allow_pending:
                    anchor['illustration']=None
                    continue
                raise ValueError(lid+': stale illustration exact field mismatch')
            if not reuse_id and not allow_pending and entry.get('visual_review')!='approved':
                raise ValueError(lid+': illustration image has not passed visual review')
            asset = entry.get('asset','')
            if not re.fullmatch(r'assets/[A-Za-z0-9_./-]+\.webp',asset) or '..' in Path(asset).parts:
                raise ValueError(lid+': unsafe illustration asset')
            path = (image_root/asset).resolve()
            if image_root.resolve() not in path.parents or not path.is_file():
                raise ValueError(lid+': missing illustration image')
            if not entry.get('sha256') or hashlib.sha256(path.read_bytes()).hexdigest()!=entry['sha256']:
                raise ValueError(lid+': illustration image checksum mismatch')
            try:
                with Image.open(path) as im:
                    if im.format!='WEBP' or min(im.size)<128 or getattr(im,'n_frames',1)!=1:
                        raise ValueError('Expected one static WebP illustration')
                    width,height=im.size
                    im.load()
            except Exception:
                raise ValueError(lid+': invalid or undecodable illustration image') from None
            if not entry.get('alt') or anchor['fr'] in entry['alt']:
                raise ValueError(lid+': illustration alt missing or leaks answer')
            # Reused pedagogical anchors may recur; generated assets belong to exactly one target.
            if not reuse_id and asset in asset_owners:
                raise ValueError(lid+': generated illustration reused for another target')
            if not reuse_id: asset_owners[asset] = lid
            anchor['illustration'] = {'src':prefix+asset,'alt':entry['alt'],'width':width,'height':height,
                                      'origin':reuse_id or lid}
    for book in books:
        for lesson in book['lessons']:
            if any(p not in ids for p in lesson.get('prerequisites',[])):
                raise ValueError(lesson['id']+': missing prerequisite')
    dependencies={l['id']:l.get('prerequisites',[]) for b in books for l in b['lessons']}
    active,visited=set(),set()
    def visit(lid):
        if lid in active:raise ValueError('prerequisite cycle: '+lid)
        if lid in visited:return
        active.add(lid)
        for prior in dependencies[lid]:visit(prior)
        active.remove(lid);visited.add(lid)
    for lid in dependencies:visit(lid)
    return books

def lesson_markdown(lesson,book):
    a=lesson['anchor']
    metadata={k:lesson[k] for k in ('id','number','source_title','minutes','sources','status') if k in lesson}
    metadata.update({'book':book['id'],'book_title':book['title']})
    parts=['---',json.dumps(metadata,ensure_ascii=False,indent=2),'---','',
           '# '+lesson['id']+' · '+lesson['title'],'',
           '> 本站原创中文辅助微课。原书全文保留本机；设备合成朗读不是原录音。','',
           '## 学完能做什么','',lesson['goal'],'','## 讲解','',lesson['explanation'],'',
           *['- '+x for x in lesson['teaching_points']],'','## 给小朋友的比喻','',lesson['analogy'],'',
           '## 例句','',a['fr']+' → '+a['zh'],'','近音钩子：'+a['sound'],'',
           '脑内电影：'+a['movie'],'','发音提示：'+a['pronunciation'],'',
           '近音只帮助提取记忆，准确声音先听法语，再回听核对。','', '## 练习','']
    for i,q in enumerate(lesson['quiz'],1):
        parts+=['### '+str(i)+'. '+q['prompt'],'']
        parts += ['- '+chr(65+j)+'. '+choice for j,choice in enumerate(q['choices'])]+['']
    parts+=['## 答案与原因','']
    for i,q in enumerate(lesson['quiz'],1):
        parts += [f'{i}. {chr(65+q["answer"])} — {q["reason"]}','']
    parts+=['## 一分钟应用','',lesson['application'],'',*['- '+x for x in lesson['self_check']],
            '','## 相关学习','', '先听 → 看图理解 → 分组跟读 → 隐藏文字看图说 → 揭晓回听；隔天、三天后、一周后再回忆。','',
            '## 参考资料','']
    for source in lesson['sources']:
        parts += ['- '+SOURCE_NAMES[source['book']]+'：'+source['label']+'；本机索引 `'+source['book']+'/'+source['location']+'`。']
    if lesson.get('teacher_notes'):
        parts += ['', '教师资料辅助：'+lesson['teacher_notes']]
    return '\n'.join(parts)+'\n'

def build(allow_pending=False):
    names=('nihao-a1','jianming-1','jianming-2','nihao-b1','nihao-4')
    books=[read_json(ROOT/'content'/f'{name}.json') for name in names]
    validate_coverage(books)
    validate_books(books,allow_pending=allow_pending)
    lessons=[lesson for book in books for lesson in book['lessons']]
    markdown_dir=ROOT/'lessons'; markdown_dir.mkdir(exist_ok=True)
    for book in books:
        for lesson in book['lessons']:
            lesson['book']=book['id'];lesson['book_title']=book['title'];lesson['level']=book['level']
            lesson['markdown']=lesson_markdown(lesson,book)
            (markdown_dir/(lesson['id']+'.md')).write_text(lesson['markdown'])
    payload=json.dumps({'books':[{k:v for k,v in b.items() if k!='lessons'} for b in books],
                        'lessons':lessons,'source_names':SOURCE_NAMES},ensure_ascii=False)
    payload=payload.replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    page=(ROOT/'template.html').read_text().replace('/*__CSS__*/',(ROOT/'style.css').read_text())
    page=page.replace('/*__DATA__*/',payload).replace('/*__JS__*/',(ROOT/'app.js').read_text())
    accessible_links=''.join('<li><a href="lessons/'+l['id']+'.md">'+html.escape(l['id']+' · '+l['title'])+'</a></li>' for l in lessons)
    page=page.replace('<!--__NOSCRIPT_LESSONS__-->','<ul>'+accessible_links+'</ul>')
    (ROOT/'index.html').write_text(page)
    report={'books':len(books),'source_books':len(SOURCE_NAMES),'lessons':len(lessons),
            'quizzes':sum(len(l['quiz']) for l in lessons),
            'illustrated':sum(bool(l['anchor'].get('illustration')) for l in lessons),
            'pending': [l['id'] for l in lessons if not l['anchor'].get('illustration')],
            'public_source_fulltext':False,'content_status':'original_companion_draft',
            'counts':{b['id']:len(b['lessons']) for b in books}}
    (ROOT/'build-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    coverage={'source_books':SOURCE_NAMES,'course_counts':report['counts'],
              'records':[{k:l[k] for k in ('id','number','source_title','sources','teaching_points')}
                         for l in lessons],
              'scope':'Original Chinese companion microcourses; all original numbered lessons and named reviews mapped. Original audio remains untested when unavailable.'}
    (ROOT/'source-coverage.json').write_text(json.dumps(coverage,ensure_ascii=False,indent=2))
    print(json.dumps(report,ensure_ascii=False))
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--allow-pending',action='store_true',help='Local authoring preview only; never publish pending images')
    build(parser.parse_args().allow_pending)
