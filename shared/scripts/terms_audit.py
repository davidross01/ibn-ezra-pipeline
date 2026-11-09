import json,re,unicodedata as ud,collections
import sys
M=json.load(open(sys.argv[1] if len(sys.argv)>1 else 'data/model.json',encoding='utf-8'))
def cons(s): return ''.join(c for c in ud.normalize('NFD',s) if 'א'<=c<='ת' or c in ' "\'')
def plain(t): return re.sub(r'\{/?[a-z]+\}','',t)
# Hebrew term (consonant regex) -> (sheet / house meaning, accepted English regexes)
T=[
 ('סמוכ|סמוך|סמיכות','construct',r'construct|bound'),
 ('נפרד','independent / absolute form',r'absolute|independent|separate|standalone|stands alone'),
 ('בנין הקל|הבנין הקל|מהקל|בקל\b','light conjugation (kal)',r'light conjugation|kal'),
 ('הכבד הנוספ|כבד נוספ','heavy w/ added letter = hif\'il',r'added letter|hif'),
 ('הבנין הכבד|מהכבד|בכבד','heavy conjugation = pi\'el',r'heavy conjugation|pi.el'),
 ('נפעל','nif\'al passive/reflexive',r'nif.al|passive|reflexive'),
 ('התפעל|מתפעל','hitpa\'el reflexive',r'hitpa.el|reflexive'),
 ('הפעיל','hif\'il causative',r'hif.il|causative'),
 ('שמ הפועל|שם הפועל','infinitive',r'infinitive'),
 ('פועל יוצא','transitive verb',r'transitive'),
 ('פועל עומד','intransitive verb',r'intransitive|stative'),
 ('שמ התאר|שם התאר|תואר','adjective',r'adjective|attribute|description'),
 ('כנוי|כינוי','pronoun / pronominal suffix',r'pronoun|suffix|byname|euphemism'),
 ('עבר','past',r'past'),
 ('עתיד','future',r'future'),
 ('צווי|ציווי','imperative/command',r'imperative|command'),
 ('קמצ קטנ|קמץ קטן','small kamatz = tzere',r'small .?kamatz|tzere'),
 ('קמצ גדול|קמץ גדול','large kamatz',r'large .?kamatz|kamatz gadol|kamatz'),
 ('פתח קטנ|פתח קטן','small patach = segol',r'small .?patach|segol'),
 ('פתח גדול','large patach',r'large .?patach|patach'),
 ('שוא','sheva',r'sheva'),
 ('חולמ|חולם|חלם','holam',r'holam'),
 ('שורק|שורוק','shuruk',r'shuruk'),
 ('קבוצ|קבוץ','kubutz',r'kubutz'),
 ('חירק|חיריק|חרק','hirik',r'hirik'),
 ('דגש','dagesh',r'dagesh'),
 ('רפה','without dagesh / soft',r'rafe|without .?dagesh|soft|light'),
 ('נח נעלמ|נח נעלם|הנח הנעלמ|הנח הנעלם','hidden quiescent letter',r'quiescent|silent|hidden'),
 ('נוספ|נוסף','added (not of root)',r'added|extra|additional'),
 ('שרש|שורש','root',r'root'),
 ('מגזרת|גזרת','from the root of',r'root|derived'),
 ('משקל','pattern',r'pattern|form'),
 ('חסר','missing',r'missing|lacking|omitted|left out|defective|less'),
 ('יתר|יתיר','extra',r'extra|superfluous|additional'),
 ('טעמ|טעם','sense / reason / accent',r'sense|meaning|reason|accent|taste'),
 ('משרת עצמו|מושכ עצמו|מושך עצמו','serves/draws itself and another',r'itself and another|double duty|serves|draws'),
 ('דרכ קצרה|דרך קצרה','short way of speaking',r'short way|elliptic|briefly'),
 ('דרש','homiletical interpretation (derash)',r'homil|derash|exposition'),
 ('פשט|פשוטו','plain / literal sense',r'plain sense|literal|plain meaning|simple'),
 ('כמשפט','according to rule',r'rule|as is (the )?(usual|proper)|normal|regular'),
 ('ואין לו אח|אין לו אח','unique form, no other like it',r'unique|no (other|parallel|like)|no brother|only (one|place|instance)'),
 ('יש אומרימ|יש אומרים|ויש אומרימ|ויש אומרים|י"א|וי"א','some say',r'some say|some (have )?said|others say|some explain'),
 ('המשכיל יבינ|המשכיל יבין','the wise will understand',r'wise will understand|understanding will understand|enlightened'),
 ('לשונ רבימ|לשון רבים|רבימ|רבים','plural',r'plural|many'),
 ('יחיד','singular',r'singular|one|single|alone'),
 ('זכר','masculine',r'masculine|male|remember|memory'),
 ('נקבה','feminine',r'feminine|female'),
 ('מתחלפימ|מתחלפים|תחת','interchange / in place of',r'interchange|in place of|instead|takes the place|under|beneath'),
]
paras=collections.defaultdict(str); ens=collections.defaultdict(str); notes=collections.defaultdict(str)
for p in M['hc']: paras[(p['ch'],p['v'])]+=' '+cons(plain(p['text']))
for p in M['ec']:
    if p.get('kind')=='p': ens[(p['ch'],p['v'])]+=' '+plain(p['text'])
for p in M['notes']:
    if p.get('kind')=='p': notes[(p.get('ch'),p.get('v'))]+=' '+plain(p['text'])
rep=[]; stats=collections.Counter(); ok=collections.Counter()
for he,mean,en in T:
    for k,h in paras.items():
        n=len(re.findall(r'(?<![א-ת])(?:ו|ה|ב|ל|מ|כ|ש|וה|וב|ול|ומ|וכ|וש|שה|מה|כה|בה)?(?:'+he+r')(?![א-ת])',h))
        if not n: continue
        stats[mean]+=n
        e=ens.get(k,'')+' '+notes.get(k,'')
        if re.search(en,e,re.I): ok[mean]+=n
        else: rep.append((mean,k,n))
print('term | in Hebrew | matched in English')
for he,mean,en in T:
    if stats[mean]: print(f'{mean:40s} {stats[mean]:4d} {ok[mean]:4d}')
import os; os.makedirs('test',exist_ok=True)
json.dump(rep,open('test/terms_missing.json','w'),ensure_ascii=False)
print(len(rep),'term/verse places with no matching English')
for r in rep: print(r)
