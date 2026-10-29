"""Keep every teaching example tied to its own reviewed sound joke and movie."""
import json

def apply_sentence_memories(lessons, content):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('duplicate sentence memory field: '+key)
            result[key] = value
        return result
    catalog = json.loads((content/'sentence-memories.json').read_text(),object_pairs_hook=unique)
    expected = {f'{l["id"]}:{i}':e for l in lessons for i,e in enumerate(l['examples'],1)}
    if catalog.keys() != expected.keys():
        raise ValueError(f'sentence memory coverage: missing={sorted(expected.keys()-catalog.keys())}, stale={sorted(catalog.keys()-expected.keys())}')
    for key, example in expected.items():
        entry = catalog[key]
        if not isinstance(entry,dict) or any(not isinstance(entry.get(f),str) or not entry[f].strip() for f in ('fr','zh','sound','movie')):
            raise ValueError('empty sentence memory: '+key)
        if entry['fr'] != example['fr'] or entry['zh'] != example['zh']:
            raise ValueError('stale sentence memory: '+key)
        if len(entry['sound'])>150 or len(entry['movie'])>160:
            raise ValueError('overlong sentence memory: '+key)
        if any(text in entry['sound']+entry['movie'] for text in ('句子小怪兽','发光大招牌')):
            raise ValueError('generic sentence memory template: '+key)
    # Validate the entire catalog before mutating course data.
    for key, example in expected.items():
        entry = catalog[key]
        example['pronunciation'].update(sound_joke=entry['sound'],mental_movie=entry['movie'],
            mnemonic=f'声音梗：{entry["sound"]} 脑内电影：{entry["movie"]}',
            sentence_memory_source='individually-authored')
    return len(catalog)
