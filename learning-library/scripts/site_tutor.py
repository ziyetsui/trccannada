"""Extend the same five learning views to every authored lesson example.

Data is built once into JSON, then checked against the editable Markdown. The
browser needs no runtime phonemizer or network. Known 50-lesson teaching data
is retained rather than regenerated.
"""
from pathlib import Path
import copy,json,re
from pronunciation import TOKEN,norm,words
VOWELS=set('aeiouyɛœøɔɑəɪʊ')
ASPIRATED={'héros','haut','haute','hautes','hauts','honte','huit','haricot','haricots','hasard','haine'}
C_SOUND={'p':'p','b':'b','t':'t','d':'d','k':'k','ɡ':'ɡ','f':'f','v':'v','s':'s','z':'z','ʃ':'ʃ','ʒ':'ʒ','m':'m','n':'n','l':'l','ʁ':'ʁ','ɲ':'ɲ'}

def connection_notes(fr,lex,known):
    tokens=list(TOKEN.finditer(fr));out=[]
    for first,second in zip(tokens,tokens[1:]):
        if fr[first.end():second.start()].strip():continue
        left,right=norm(first.group()),norm(second.group());pair=left+' '+right
        a,b=lex[left]['ipa'],lex[right]['ipa'];label=reason=None
        if pair in known:label,reason=known[pair]
        elif left=='et' and b[0] in VOWELS:
            label='禁止联诵';reason='et 的 t 不发音，也不在后面的元音前联诵。两个词平顺相接，不加 /t/。'
        elif right in ASPIRATED and left in {'les','des','un','mon','mes','tes','ses','deux','trois'}:
            label='h aspiré 阻止联诵';reason='这个 h 不发声，但会阻止前词联诵；不要加 /z/ 或 /n/。'
        elif b[0] in VOWELS and right not in ASPIRATED:
            sound=None
            if left in {'les','des','mes','tes','ses','nos','vos','leurs','deux','trois','aux'}:sound='z'
            elif left in {'un','mon','ton','son'}:sound='n'
            elif left=='vingt':sound='t'
            elif left in {'six','dix'}:sound='z'
            elif left=='neuf' and right in {'ans','heures'}:sound='v'
            if sound:
                label=f'联诵 · /{sound}/'
                reason=f'这里 {first.group()} 与 {second.group()} 紧密相接，连接音为 /{sound}/。先听两个词组合，再听整句；不要另添一个音节。'
            elif left in {'nous','vous','ils','elles'} and right in {'avons','avez','ont','êtes','allons','allez','arrivent','habitez','écoutent','aiment','étudient','aimerions','aurons','aviez','envoyez','épelle'}:
                label='联诵 · /z/';reason='这里代词接元音开头的动词，词尾 s 连接为 /z/；不要把它读成一个独立词。'
            elif left=='on' and right in {'a','est','ira','arrive','avait'}:
                label='联诵 · /n/';reason='这里主语 on 接元音开头动词，联诵 /n/；仍保留 on 的鼻元音。'
            elif a[-1] in C_SOUND:
                sound=C_SOUND[a[-1]];label=f'连读 · 原有 /{sound}/';reason=f'{first.group()} 的独读音本来就以 /{sound}/ 结尾，这个声音直接接到 {second.group()} 的元音前；不再添加第二个辅音。'
        if label:out.append(dict(fr=first.group()+' → '+second.group(),label=label,reason=reason,after=first.end()))
    return out

# Exact idiom sequences stay together even when a literal gloss would be easier.
IDIOMS=[
 'le cœur sur la main','les pieds sur terre','la tête sur les épaules','son sang-froid','sur un coup de tête','la sourde oreille','sur la même longueur d’onde','se serre les coudes','de l’eau dans son vin','aux anges','le moral à zéro','la chair de poule','un coup de main','ses jambes à son cou','levé le petit doigt','les yeux de la tête','l’argent par les fenêtres','de côté','en pleine forme','à plat','du poil de la bête','la route à l’aube','fausse route','dans une impasse','un petit creux','la main à la pâte','sur ma faim','me creuse la tête','du pain sur la planche','les bouchées doubles','les cartes sur table','un terrain d’entente','son épingle du jeu','bat son plein','met l’ambiance','au coude-à-coude','fait match nul','fait la une','couler beaucoup d’encre','sous les projecteurs','de l’huile sur le feu','dans la ligne de mire','une tempête dans un verre d’eau','droit au but','autour du pot','En un mot','cartes sur table','quelque chose à cacher','à demi-mot','une longueur d’avance','à armes égales','des bâtons dans les roues','au pied de la lettre','le sens de l’humour','mâché ses mots','un peu de recul','le bout du tunnel','la part des choses','le pour et le contre','sauter le pas','avec le feu','ça marche','Ça me dit','Tant pis','en bonne et due forme','À défaut de réponse','porter atteinte','comme une marmotte','Petit à petit','Mieux vaut tard que jamais']

def chunks(fr,zh,lex,idiom=False):
    # Sentence/clause punctuation supplies reliable initial boundaries. Within a
    # short clause, keep explicit idioms and prep groups intact where possible.
    result=[]
    for segment in re.split(r'(?<=[,;:?!])\s+|[«»]',fr):
        ts=list(TOKEN.finditer(segment))
        if not ts:continue
        parts=[]
        protected=None
        if idiom:
            for expression in sorted(IDIOMS,key=len,reverse=True):
                match=re.search(re.escape(expression),segment,re.I)
                if match and match.start()>0:
                    protected=match.start();break
        if protected:
            parts=[segment[:protected].strip(),segment[protected:].strip()]
        elif len(ts)>4:
            # Leading subject + verb, then a complete short complement.
            cutoff=2 if norm(ts[0].group()) in {'je','tu','il','elle','nous','vous','ils','elles','on'} else min(3,len(ts)-2)
            pos=ts[cutoff].start();parts=[segment[:pos].strip(),segment[pos:].strip()]
        else:parts=[segment.strip()]
        for part in parts:
            part=part.strip(' .,;:?!')
            if not words(part):continue
            hints=' · '.join(lex[norm(w)]['zh'].split('；')[0] for w in words(part))
            result.append(dict(fr=part,zh=hints,gloss_kind='literal'))
    if len(result)==1:result[0].update(zh=zh,gloss_kind='sentence')
    return result

def expand_library(lessons, content:Path):
    lex=json.loads((content/'site-words.json').read_text())
    annotations=json.loads((content/'site-tutor.json').read_text())
    overrides=json.loads((content/'site-tutor-overrides.json').read_text())
    contexts=json.loads((content/'site-word-contexts.json').read_text())
    known=json.loads((content/'pronunciation-links.json').read_text())
    known['les yeux']=['联诵 · /z/','les 接元音起音的 yeux，必须联诵 /z/：/le.z‿jø/。yeux 的 x 在独读时不发声；这里只要一个 /z/。']
    known['vingt euros']=['联诵 · /t/','vingt 独读 /vɛ̃/；在 euros 前必须联诵 /t/：/vɛ̃.t‿ø.ʁo/。词尾是 t，不能误读成 /z/。']
    known['mets vingt']=['词尾不读','mets 的 ts 不读；vingt 的 t 是否出现看下一词。这里后接 euros，/t/ 连接在 vingt 与 euros 之间，而不是在 mets 后。']
    expected={l['id'] for l in lessons if not l.get('pronunciation_guide')}
    if set(annotations)!=expected:raise ValueError('site tutor lesson coverage mismatch')
    for l in lessons:
        if l['id'] not in expected:continue
        entries=overrides.get(l['id'],annotations[l['id']])
        if len(entries)!=len(l['examples']):raise ValueError('site tutor example count mismatch: '+l['id'])
        for index,(e,data) in enumerate(zip(l['examples'],entries),1):
            if data['fr']!=e['fr']:raise ValueError('site tutor stale sentence: '+l['id'])
            context=contexts.get(f'{l["id"]}:{index}')
            example_lex=lex
            if context:
                if context['fr']!=e['fr']:raise ValueError('stale word context: '+l['id'])
                example_lex={**lex,**{key:{**lex[key],**values} for key,values in context['words'].items()}}
            annotated=[]
            for word in words(e['fr']):
                key=norm(word)
                if key not in example_lex:raise ValueError('site tutor missing word: '+key)
                annotated.append(dict(fr=word,**copy.deepcopy(example_lex[key])))
            groups=data.get('chunks') or chunks(e['fr'],e['zh'],example_lex,l['book']=='idioms')
            if list(map(norm,words(' '.join(c['fr'] for c in groups))))!=list(map(norm,words(e['fr']))):
                raise ValueError('site tutor chunks do not reconstruct: '+l['id'])
            e['pronunciation']=dict(words=annotated,chunks=groups,links=connection_notes(e['fr'],example_lex,known),mnemonic=data['mnemonic'],rule_memory=data['rule_memory'],annotation_source='expanded')
        l['pronunciation_guide']=True
    from sentence_memory import apply_sentence_memories
    apply_sentence_memories(lessons,content)
    return dict(lessons=len(lessons),examples=sum(len(l['examples']) for l in lessons),words=len(lex))
