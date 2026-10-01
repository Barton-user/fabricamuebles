import re,sys,html
src,dst=sys.argv[1],sys.argv[2]
L=open(src,encoding='utf-8').read().split('\n')
def plano(t): return re.sub(r'\*\*|`|_(?=\S)|(?<=\S)_','',t).strip()
def titulo(t,maxc=55):
    m=re.match(r'^\*\*(.+?)\*\*',t.strip())
    if m and len(plano(m.group(1)))<=maxc: return plano(m.group(1)).rstrip(':')
    p=plano(t)
    for sep in [': ',' — ',' → ','. ',' (']:
        i=p.find(sep)
        if 0<i<=maxc: return p[:i]
    if len(p)<=maxc: return p
    c=p[:maxc].rsplit(' ',1)[0]; return c+'…'
class N:
    def __init__(s,t,nota='',nivel=0): s.t,s.nota,s.hijos,s.nivel=t,nota,[],nivel
raiz=N('Perforadora SKH-612HS'); pila=[raiz]; header=None; ultimo=None; para=[]
def actual(): return pila[-1]
def flush():
    global para
    if para:
        txt=' '.join(x.strip() for x in para); 
        if txt.strip(): actual().hijos.append(N(titulo(txt),plano(txt) if len(plano(txt))>len(titulo(txt)) else ''))
    para=[]
for l in L:
    h=re.match(r'^(#{1,4}) (.*)',l)
    if h:
        flush(); nv=len(h.group(1))
        if nv==1: raiz.t=plano(h.group(2)); continue
        while len(pila)>1 and pila[-1].nivel>=nv: pila.pop()
        n=N(plano(h.group(2)),'',nv); actual().hijos.append(n); pila.append(n); header=None; continue
    if l.startswith('|'):
        flush(); cel=[c.strip() for c in l.strip().strip('|').split('|')]
        if all(re.fullmatch(r':?-+:?',c) for c in cel): continue
        if header is None: header=cel; continue
        t=titulo(cel[0]) if cel[0] else titulo(cel[1])
        nota='\n'.join(f'{plano(a)}: {plano(b)}' for a,b in zip(header,cel) if b)
        actual().hijos.append(N(t,nota)); continue
    else:
        if l.strip()=='' : header=None
    b=re.match(r'^\s*(?:[-*]|\d+\.)\s+(.*)',l)
    if b:
        flush(); txt=b.group(1); actual().hijos.append(N(titulo(txt),plano(txt) if len(plano(txt))>len(titulo(txt))+1 else '')); ultimo=actual().hijos[-1]; continue
    if l.startswith('>'): l=l.lstrip('> ')
    if l.strip() in ('','---'): flush(); continue
    if re.match(r'^\s{2,}\S',l) and ultimo is not None and not para:
        ultimo.nota=(ultimo.nota+' '+plano(l)).strip(); continue
    para.append(l)
flush()
def out(n,ind):
    a=f'{ind}<outline text="{html.escape(n.t,quote=True)}"'
    if n.nota: a+=f' _note="{html.escape(n.nota,quote=True)}"'
    if not n.hijos: return a+'/>\n'
    return a+'>\n'+''.join(out(h,ind+'  ') for h in n.hijos)+f'{ind}</outline>\n'
x='<?xml version="1.0" encoding="UTF-8"?>\n<opml version="2.0">\n<head><title>'+html.escape(raiz.t)+'</title></head>\n<body>\n'+out(raiz,'  ')+'</body>\n</opml>\n'
open(dst,'w',encoding='utf-8').write(x)
def cuenta(n): return 1+sum(cuenta(h) for h in n.hijos)
def maxlen(n): return max([len(n.t)]+[maxlen(h) for h in n.hijos])
print('nodos',cuenta(raiz),'título más largo',maxlen(raiz))
