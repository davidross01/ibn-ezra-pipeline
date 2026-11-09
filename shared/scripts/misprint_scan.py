import json, re, sys, os, collections, unicodedata as ud
# Misprint scan of the Hebrew commentary (from the parasha folder): rare words with a common look-alike,
# references that do not hold the quoted words, quote and heading words that differ from the verse by one letter.
SHARED = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # shared/: scripts, lib, fonts for every parasha
ROOT = os.environ.get('PARASHA_ROOT') or os.getcwd()                   # the parasha's own folder (data/, build/, parasha.json)
M=json.load(open(sys.argv[1] if len(sys.argv)>1 else f'{ROOT}/data/model.json',encoding='utf-8'))
T=json.load(open(f'{ROOT}/src/tanakh.json',encoding='utf-8'))
G={str(i+1):ch for i,ch in enumerate(T['Genesis'])}
IE={'ie':[x['he'] for x in json.load(open(f'{ROOT}/src/ie.json',encoding='utf-8'))]}
try: IE['bereshit']=json.load(open(f'{ROOT}/../bereshit/data/ibnezra_he.json',encoding='utf-8'))
except Exception as e: print(e)
FIN={'ך':'כ','ם':'מ','ן':'נ','ף':'פ','ץ':'צ'}
def cons(s):
    s=re.sub(r'<[^>]+>','',s).replace('&nbsp;',' ').replace('־',' ').replace('׀',' ')
    return ''.join(FIN.get(c,c) for c in ud.normalize('NFD',s) if 'א'<=c<='ת' or c==' ')
def printed(t):
    t=re.sub(r'\[[^\]]*\]','',t); return t
lex=collections.Counter()
def addtxt(x):
    if isinstance(x,list):
        for y in x: addtxt(y)
    elif isinstance(x,str):
        for w in cons(x).split(): lex[w]+=1
for k,v in T.items(): addtxt(v)
for ch in IE.values(): addtxt(ch)
for f in ('src/radak.json','src/ramban.json','src/rashi.json','../bereshit/data/radak_on_ie.json','../bereshit/data/ramban_on_ie.json'):
    try:
        d=json.load(open(f'{ROOT}/'+f,encoding='utf-8')); addtxt(list(d.values()) if isinstance(d,dict) else d)
    except Exception as e: print(f,e)
print('lexicon words',len(lex))
paras=[(p['ch'],p['v'],printed(p['text'])) for p in M['hc']]
SW=[('ד','ה'),('ר','ת'),('ה','ח'),('ד','ר'),('מ','ס'),('ו','ז'),('כ','ב'),('ו','י'),('נ','ג'),('ט','מ'),('ת','ח'),('ע','צ'),('ב','נ'),('ו','א'),('ז','א')]
SW+= [(b,a) for a,b in SW]
found=[]
for c,v,t in paras:
    body=re.sub(r'\{s\}.*?\{/s\}','',t); body=re.sub(r'\{/?[a-z]+\}','',body)
    for w in set(re.sub(r'["\']','',x) for x in re.findall(r'[א-ת֑-ׇ"\']+',body)):
        w=cons(w).strip()
        if len(w)<2 or ' ' in w: continue
        n=lex[w]
        cands=[]
        for i,ch in enumerate(w):
            for p,q in SW:
                if ch==p: cands.append(w[:i]+q+w[i+1:])
        for i in range(len(w)+1):
            for L in 'אבגדהוזחטיכלמנסעפצקרשת': cands.append(w[:i]+L+w[i:])
        swaps=[x for x in cands[:len(cands)] if len(x)==len(w)]
        PRI={('ה','ח'),('ח','ה'),('ד','ר'),('ר','ד'),('ד','ה'),('ה','ד')}
        def pri(x):
            if len(x)!=len(w): return False
            d=[(a,b) for a,b in zip(w,x) if a!=b]
            return len(d)==1 and d[0] in PRI
        good=sorted({x for x in cands if (pri(x) and lex[x]>=5 and lex[x]>=5*max(n,1)) or (lex[x]>=20 and lex[x]>=20*max(n,1))},key=lambda x:(not pri(x),len(x)!=len(w),-lex[x],x))   # x last: ties in a fixed order, so hits don't change between runs
        if n<=3 and good:
            found.append((c,v,'word',w,good[:3],n,[lex[x] for x in good[:3]]))
# references
BOOK={'בראשית':'Genesis','שמות':'Exodus',"דבר'":'Deuteronomy','דברים':'Deuteronomy','דב"ר':'Deuteronomy','תהלים':'Psalms',"ישעי'":'Isaiah','ישעי,':'Isaiah','איוב':'Job','במדבר':'Numbers','ש"א':'I Samuel','ש"א,':'I Samuel','ש"ב':'II Samuel',"יחז'":'Ezekiel','יחזקאל':'Ezekiel',"ירמי'":'Jeremiah','ירמיה':'Jeremiah','יהושע':'Joshua','קהלת':'Ecclesiastes','דניאל':'Daniel','משלי':'Proverbs','נחמיה':'Nehemiah',"נחמי'":'Nehemiah','ויקרא':'Leviticus','מ"א':'I Kings','מ"ב':'II Kings','דה"א':'I Chronicles','דה"ב':'II Chronicles',"שופ'":'Judges',"שופ',":'Judges'}
V={'א':1,'ב':2,'ג':3,'ד':4,'ה':5,'ו':6,'ז':7,'ח':8,'ט':9,'י':10,'כ':20,'ל':30,'מ':40,'נ':50,'ס':60,'ע':70,'פ':80,'צ':90,'ק':100}
def num(s):
    s=s.replace('"','').replace("'",'').strip(',')
    if not s or any(x not in V for x in s): return None
    seq=[V[x] for x in s]
    ok = seq==sorted(seq,reverse=True) and len(set(seq))==len(seq) or s in('טו','טז')
    return sum(seq) if ok else -1
def verse(book,ch,vs):
    try: return cons(T[book][ch-1][vs-1])
    except Exception: return None
def locate(q):
    hits=[]
    for b,chs in T.items():
        if b.startswith('Ibn Ezra'): continue
        for ci,chap in enumerate(chs):
            for vi,vt in enumerate(chap):
                if isinstance(vt,str) and q in cons(vt): hits.append((b,ci+1,vi+1))
    return hits
last={}
for c,v,t in paras:
    for m in re.finditer(r'\{s\}\(([^)]*)\)\{/s\}',t):
        ref=m.group(1); toks=ref.replace(',',' ').split()
        pre=re.sub(r'\{/?[a-z]+\}','',t[:m.start()])
        qm=re.findall(r'"([^"]{3,})"\s*$',pre.rstrip())
        quote=cons(qm[-1] if qm else ' '.join(pre.split()[-4:])).strip()
        qw=quote.split()
        if toks[0]=='שם': book=last.get('b'); nums=toks[1:]
        else: book=BOOK.get(toks[0]); nums=toks[1:]; last['b']=book
        if book is None: found.append((c,v,'ref-book?',ref,'')); continue
        ns=[num(x) for x in nums]
        if any(x==-1 for x in ns): found.append((c,v,'ref-number',ref,'not a valid Hebrew number')); continue
        if len(ns)<2 or None in ns: continue
        txt=verse(book,ns[0],ns[1])
        if txt is None: found.append((c,v,'ref-range',ref,book)); continue
        # quote words present?
        key=[w for w in qw if len(w)>2][-3:]
        if key and sum(w in txt for w in key)<max(1,len(key)-1):
            hits=locate(' '.join(qw[-3:])) if len(qw)>=2 else []
            found.append((c,v,'ref-mismatch',ref,' '.join(qw[-4:]), [h for h in hits if h[0]==book][:3] or hits[:3]))
for f in found: print(f)
print(len(found))

# ---- v4 additions: real-word slips by frequency ratio, quote-vs-verse word diff, heading vs verse
LA=set(SW)
def lookalikes(w):
    for i,ch in enumerate(w):
        for p,q in LA:
            if ch==p: yield w[:i]+q+w[i+1:]
extra=[]
for c,v,t in paras:
    body=re.sub(r'\{s\}.*?\{/s\}','',t); body=re.sub(r'\{/?[a-z]+\}','',body)
    for x in set(re.findall(r'[א-ת֑-ׇ]+',body)):
        w=cons(x).strip()
        if len(w)<2: continue
        best=[y for y in lookalikes(w) if lex[y]>=200 and lex[y]>=60*max(lex[w],1)]
        if best: extra.append((c,v,'ratio',w,best,lex[w],[lex[y] for y in best]))
# quote vs verse
for c,v,t in paras:
    for m in re.finditer(r'"([^"]{3,80})"\s*\{s\}\(([^)]*)\)\{/s\}',t):
        q=cons(re.sub(r'\{/?[a-z]+\}','',m.group(1))).split(); ref=m.group(2); toks=ref.replace(',',' ').split()
        book=BOOK.get(toks[0]); 
        if not book: continue
        ns=[num(x) for x in toks[1:3]]
        if len(ns)<2 or None in ns or -1 in ns: continue
        vt=verse(book,ns[0],ns[1])
        if not vt: continue
        vw=set(vt.split())
        for w in q:
            if w not in vw and len(w)>=2:
                alt=[y for y in lookalikes(w) if y in vw]
                if alt: extra.append((c,v,'quote',w,alt,ref))
# heading vs verse (only chapters we have)
for p in M['hc']:
    m=re.match(r'^\{b\}(.*?)\{/b\}',p['text'])
    if not m: continue
    try: vw=set(cons(G[str(p['ch'])][p['v']-1]).split())
    except Exception: continue
    for w in cons(m.group(1)).split():
        if w not in vw:
            alt=[y for y in lookalikes(w) if y in vw]
            if alt: extra.append((p['ch'],p['v'],'heading',w,alt))
for e in extra: print(e)
