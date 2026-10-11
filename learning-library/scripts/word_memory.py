"""Require a reviewed mnemonic for every word actually used in the course."""
import json,re
from pronunciation import norm

METHODS = {'sound', 'action', 'name', 'cognate', 'family'}

def load_memories(path, lessons):
    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('duplicate word memory field: '+key)
            result[key] = value
        return result
    catalog = json.loads(path.read_text(), object_pairs_hook=unique_object)
    expected = {norm(w['fr']) for l in lessons for e in l['examples']
                for w in e['pronunciation']['words']}
    missing, stale = expected-catalog.keys(), catalog.keys()-expected
    if missing or stale:
        raise ValueError(f'word memory coverage: missing={sorted(missing)}, stale={sorted(stale)}')
    for key, item in catalog.items():
        if key != norm(key) or not isinstance(item, dict):
            raise ValueError('invalid word memory: '+key)
        if any(not isinstance(item.get(f), str) or not item[f].strip() for f in ('hook','line','cue','method')):
            raise ValueError('empty word memory: '+key)
        if len(item['hook'])>20 or not re.search(r'[\u3400-\u9fff]',item['hook']):
            raise ValueError('missing Chinese sound hook: '+key)
        if item['method'] not in METHODS or len(item['line']) > 36 or len(item['cue']) > 100:
            raise ValueError('invalid mnemonic method or length: '+key)
    return catalog
