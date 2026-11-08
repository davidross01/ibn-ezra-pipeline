# List the comments where Ibn Ezra touches an idea, his science or a "secret" (docs/rules/notes.md, "Ibn Ezra's
# ideas get a full paragraph", David, 30 Oct 2026). Reads the English commentary, so it finds candidates, not
# certainties: read each one. Verses already done (or judged not to need a paragraph) are listed in
# <folder>/review/ideas.json as {"c:v": "done" | "not needed: <why>"} and are left out.
#   python3 -I scripts/ideas_scan.py <folder>            # candidates not yet in ideas.json
#   scan(folder) -> [(ch, v, [keywords])]                 # used by check_all ("Ideas")
import json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL = {'bereshit': 'data/model_final5.json'}
KEYS = re.compile(r"\b(secrets?|soul|the All\b|angels?\b|prophe\w*|glory|intellect\w*|wise will understand|discerning will understand|"
                  r"cannot explain|spheres?\b|constellations?|astrolog\w*|planets?\b|world to come|coming-to-be|upper world|"
                  r"providence|decree|in thought|language of men|human language|likeness|image of God|in our image|"
                  r"(?:God|H\w*ashem\w*|He) knows|knowledge of (?:God|H)|the One\b|free choice|nature)", re.I)

def scan(folder):
    M = json.load(open(os.path.join(ROOT, folder, MODEL.get(folder, 'data/model.json')), encoding='utf-8'))
    p = os.path.join(ROOT, folder, 'review', 'ideas.json')
    done = json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {}
    hits = {}
    for x in M['ec']:
        t = re.sub(r'\{/?[a-z]+\}', '', x.get('text', '')).replace('H{sci}ashem', 'Hashem')
        ks = {m.group(1).lower() for m in KEYS.finditer(t)}
        if ks and x.get('ch'):
            hits.setdefault((x['ch'], x['v']), set()).update(ks)
    return [(c, v, sorted(k)) for (c, v), k in sorted(hits.items()) if f'{c}:{v}' not in done]

def sources_todo(folder):
    """Idea places (every key of ideas.json: done, kept or not needed) with no record yet in review/idea_sources.json
    of what Ibn Ezra's own writings and Saadia's Emunot veDeot add (notes.md, David, 8 Nov 2026)."""
    d = os.path.join(ROOT, folder, 'review')
    ideas = json.load(open(os.path.join(d, 'ideas.json'), encoding='utf-8')) if os.path.exists(os.path.join(d, 'ideas.json')) else {}
    src = json.load(open(os.path.join(d, 'idea_sources.json'), encoding='utf-8')) if os.path.exists(os.path.join(d, 'idea_sources.json')) else {}
    key = lambda k: tuple(int(x) for x in k.split(':'))
    return [k for k in sorted(ideas, key=key) if not (isinstance(src.get(k), dict) and src[k].get('ibn_ezra') and src[k].get('saadia'))]

if __name__ == '__main__':
    out = scan(sys.argv[1])
    for c, v, k in out: print(f'{c}:{v}  {", ".join(k)}')
    print(len(out), 'verses to read')
