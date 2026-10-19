import json,sys
d=json.load(open(sys.argv[1]))
DIRS=[(1,0,0),(0,1,0),(0,0,1),(-1,0,0),(0,-1,0),(0,0,-1)]
def v3(s): return tuple(float(x) for x in s.split(','))
def add(a,b): return tuple(x+y for x,y in zip(a,b))
def walk(n,anchor,hdv,out,cab):
    anchor=add(anchor,v3(n['anchor'])) if n.get('anchor') else anchor
    hdv=n.get('hdvDir') or hdv
    if n.get('plankNum'):
        geo=n
        if not n.get('vertices'):
            for c in n.get('children',[]):
                if c.get('vertices'):
                    geo=c; anchor2=add(anchor,v3(c['anchor'])) if c.get('anchor') else anchor
                    break
            else:
                return
            out.append((cab,n,anchor2,hdv,geo)); 
        else:
            out.append((cab,n,anchor,hdv,n))
    for c in n.get('children',[]): walk(c,anchor,hdv,out,cab)
planks=[]
for m in d['models']: walk(m,(0,0,0),None,planks,m['name'])
def world_holes(n,anchor,hdv,geo):
    h,v,dd=[DIRS[int(c)] for c in hdv.split('_')]
    verts=[v3(s) for s in geo['vertices']]
    def proj(vec): return [sum(a*b for a,b in zip(p,vec)) for p in verts]
    ph,pv,pd=proj(h),proj(v),proj(dd)
    W=max(ph)-min(ph); H=max(pv)-min(pv); T=max(pd)-min(pd)
    o=[0,0,0]
    def org(p,vec):
        return min(p) if sum(vec)>0 else max(p)
    for i in range(3): o[i]=org(ph,h)*h[i]+org(pv,v)*v[i]+org(pd,dd)*dd[i]
    res=[]
    for hole in n.get('holes') or []:
        x=hole['ocenter']['x']/1000; y=hole['ocenter']['y']/1000
        z= T if hole['side']==1 else 0
        p=[anchor[i]+o[i]+x*h[i]+y*v[i]+z*dd[i] for i in range(3)]
        res.append((hole['diameter'],hole['deep'],hole['side'],hole['ocenter'],tuple(round(c*1000,1) for c in p)))
    return W*1000,H*1000,res
for cab,n,anchor,hdv,geo in planks:
    parts=[p.get('name') for p in (n.get('partsChildren') or [])]
    holes=n.get('holes') or []
    if any('铰链' in (p or '') for p in parts) or n.get('matCode') in('NPetfrente',) and any(h['diameter']==35 for h in holes):
        W,H,res=world_holes(n,anchor,hdv,geo)
        print(f"\n[{cab}] PUERTA {n['name']} {n['spec']} hdv={hdv} W={W:.1f} H={H:.1f}")
        for r in res: print('   Ø%g x%g side%d  local=%s  world=%s'%(r[0],r[1],r[2],r[3],r[4]))
    small=[h for h in holes if h['diameter'] in (3,5) and h['deep']<=3.5]
    if small and n.get('matCode')!='NPetfrente' or (small and 'Lateral' in n['name']):
        W,H,res=world_holes(n,anchor,hdv,geo)
        print(f"\n[{cab}] LATERAL {n['name']} {n['spec']} hdv={hdv} W={W:.1f} H={H:.1f}")
        for r in res:
            if r[0] in (3,5) and r[1]<=3.5: print('   Ø%g x%g side%d  local=%s  world=%s'%(r[0],r[1],r[2],r[3],r[4]))
