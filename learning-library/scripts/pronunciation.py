"""Explicit, editable word and phrase scaffolding for all pronunciation examples.

No automatic grapheme-to-phoneme or liaison inference: the lexicon and connection
notes are authored data. Build fails if an example has no matching annotation.
"""
from pathlib import Path
import json
import re

TOKEN = re.compile(r"[A-Za-zÀ-ÿŒœ]+(?:[’'-][A-Za-zÀ-ÿŒœ]+)*")

def words(text):
    return TOKEN.findall(text)

def norm(text):
    return text.lower().replace('’', "'")

def enrich(lessons, content: Path):
    lexicon = {}
    for line in (content / 'pronunciation-words.txt').read_text().splitlines():
        if not line or line.startswith('#'):
            continue
        word, ipa, zh, picture, reason = line.split('|')
        if word in lexicon:
            raise ValueError(f'duplicate pronunciation word: {word}')
        lexicon[word] = dict(ipa=ipa, zh=zh, picture=picture, reason=reason)
    groups = {}
    for line in (content / 'pronunciation-chunks.txt').read_text().splitlines():
        if not line or line.startswith('#'):
            continue
        lid, examples = line.split('|', 1)
        if lid in groups:
            raise ValueError(f'duplicate pronunciation lesson: {lid}')
        groups[lid] = [[dict(zip(('fr', 'zh'), chunk.split('~'))) for chunk in ex.split('§')] for ex in examples.split(';;')]
    links = json.loads((content / 'pronunciation-links.json').read_text())
    ids = {l['id'] for l in lessons if l['category'] == '发音'}
    if set(groups) != ids:
        raise ValueError('pronunciation lesson coverage mismatch')
    for lesson in lessons:
        if lesson['id'] not in ids:
            continue
        if len(lesson['examples']) != len(groups[lesson['id']]):
            raise ValueError(f'{lesson["id"]}: pronunciation example count mismatch')
        for index, (example, chunks) in enumerate(zip(lesson['examples'], groups[lesson['id']])):
            tokens = words(example['fr'])
            reconstructed = words(' '.join(c['fr'] for c in chunks))
            if list(map(norm, tokens)) != list(map(norm, reconstructed)):
                raise ValueError(f'{lesson["id"]}.{index}: chunks do not reconstruct the sentence')
            annotated = []
            for token in tokens:
                key = norm(token)
                if key not in lexicon:
                    raise ValueError(f'{lesson["id"]}: missing word {key}')
                entry = dict(fr=token, **lexicon[key])
                # Resolve homographs and the role of small grammatical words here.
                if key == 'son':
                    entry['zh'] = '一个声音中的“声音”' if lesson['id'] == 'M15' else '他／她的（修饰 sac）'
                if key == 'a':
                    entry['zh'] = '有' if lesson['id'] == 'P05' else '过去时助动词（配合 sonné／commencé／dit）'
                if key == 'ai':
                    entry['zh'] = '过去时助动词（第一人称，我）'
                if key == 'sommes':
                    entry['zh'] = '过去时助动词（我们）'
                if key == 'en':
                    entry['zh'] = '前文提到的东西（代词）' if lesson['id'] == 'P04' else '处于……状态（en panne）' if lesson['id'] == 'P08' else '在……中（en résumé：总之）'
                annotated.append(entry)
            notes = []
            # Match only adjacent tokens with no punctuation separating them.
            for match1, match2 in zip(list(TOKEN.finditer(example['fr'])), list(TOKEN.finditer(example['fr']))[1:]):
                if example['fr'][match1.end():match2.start()].strip():
                    continue
                pair = norm(match1.group() + ' ' + match2.group())
                if pair in links:
                    label, reason = links[pair]
                    notes.append(dict(fr=match1.group() + ' → ' + match2.group(), label=label, reason=reason, after=match1.end()))
            example['pronunciation'] = dict(words=annotated, chunks=chunks, links=notes)
        lesson['pronunciation_guide'] = True
    return {'lessons': len(ids), 'examples': sum(len(l['examples']) for l in lessons if l['id'] in ids), 'words': len(lexicon)}
