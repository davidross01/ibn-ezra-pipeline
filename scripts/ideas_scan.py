# List the comments where Ibn Ezra touches an idea, his science or a "secret" (docs/rules/notes.md, "Ibn Ezra's
# ideas get a full paragraph", David, 30 Oct 2026). Reads the English commentary, so it finds candidates, not
# certainties: read each one. Verses already done (or judged not to need a paragraph) are listed in
# <folder>/review/ideas.json as {"c:v": "done" | "not needed: <why>"} and are left out.
#   python3 -I scripts/ideas_scan.py <folder>            # candidates not yet in ideas.json
#   scan(folder) -> [(ch, v, [keywords])]                 # used by check_all ("Ideas")
#   python3 -I scripts/ideas_scan.py <folder> --hebrew   # the wider search: Ibn Ezra's own Hebrew (9 Nov 2026)
# The wider search (David, 9 Nov 2026: "In section F why are there only 5 items can there be more?") reads Ibn Ezra's
# Hebrew for words of an idea or of his science, which the English keywords miss. Its finds that are explained in the
# note and were not taken further are recorded in <folder>/review/ideas_he.json ({"c:v": "<what it is; why no row>"}),
# so they are not listed again; ideas.json stays the record of the idea places themselves.
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

HE_KEYS = {'secret': r'סוד(?!ות)', 'soul': r'(?:\bו?ה?נשמ|\b[ובהלכ]{0,2}נפש\b|הנפש)', 'prophecy': r'(?:נבוא|נביא)', 'providence': r'השגח',
           'stars': r'\b[ובהלכ]{0,2}(?:מזל|כוכב)', 'nature': r'\b[ובהלכ]{0,2}טבע', 'medicine': r'(?:רפוא|רופא)', 'spheres': r'\b[ובהלכ]{0,2}גלגל',
           'intellect': r'(?:\bה?שכל\b|משכיל)', 'the upper': r'עליונ', 'elements': r'\bה?יסודות', 'world to come': r'עולם הבא', 'decree': r'\bה?גזרה',
           'angel': r'\b[ובהלכ]{0,2}מלאכ', 'the Glory': r'\bה?כבוד\b', 'the heart': r'(?:עם|ב)ה?לב\b', 'firmament': r'רקיע', 'the air': r'אויר',
           'heat and cold': r'\b[ובהלכ]{0,2}(?:חום|קור)\b', 'sun and moon': r'\b[ובהלכ]{0,2}(?:חמה|לבנה|ירח|שמש)\b', 'equator': r'קו השו',
           'products': r'תולד[תו]', 'hint': r'\bרמז', 'the honored Name': r'הנכבד', 'the body': r'\bה?גוף\b'}

def scan_he(folder):
    """Verses whose Hebrew commentary has a word of an idea or of Ibn Ezra's science, and that are recorded neither in
    ideas.json nor in ideas_he.json. Candidates only: many are a root or a quotation; read each."""
    import unicodedata as ud
    M = json.load(open(os.path.join(ROOT, folder, MODEL.get(folder, 'data/model.json')), encoding='utf-8'))
    d = os.path.join(ROOT, folder, 'review'); seen = {}
    for f in ('ideas.json', 'ideas_he.json'):
        if os.path.exists(os.path.join(d, f)): seen.update(json.load(open(os.path.join(d, f), encoding='utf-8')))
    hc = {}
    for b in M['hc']:
        if b.get('text') and b.get('ch'): hc.setdefault((b['ch'], b['v']), []).append(b['text'])
    out = []
    for (c, v), t in sorted(hc.items()):
        h = re.sub('[\u0591-\u05c7]', '', ud.normalize('NFD', re.sub(r'<[^>]+>|\{/?[a-z]+\}', '', ' '.join(t))))
        ks = [k for k, rx in HE_KEYS.items() if re.search(rx, h)]
        if ks and f'{c}:{v}' not in seen: out.append((c, v, ks))
    return out

def sources_todo(folder):
    """Idea places (every key of ideas.json: done, kept or not needed) with no record yet in review/idea_sources.json
    of what Ibn Ezra's own writings and Saadia's Emunot veDeot add (notes.md, David, 8 Nov 2026)."""
    d = os.path.join(ROOT, folder, 'review')
    ideas = json.load(open(os.path.join(d, 'ideas.json'), encoding='utf-8')) if os.path.exists(os.path.join(d, 'ideas.json')) else {}
    src = json.load(open(os.path.join(d, 'idea_sources.json'), encoding='utf-8')) if os.path.exists(os.path.join(d, 'idea_sources.json')) else {}
    key = lambda k: tuple(int(x) for x in k.split(':'))
    return [k for k in sorted(ideas, key=key) if not (isinstance(src.get(k), dict) and src[k].get('ibn_ezra') and src[k].get('saadia'))]

if __name__ == '__main__':
    out = scan_he(sys.argv[1]) if '--hebrew' in sys.argv else scan(sys.argv[1])
    for c, v, k in out: print(f'{c}:{v}  {", ".join(k)}')
    print(len(out), 'verses to read')
