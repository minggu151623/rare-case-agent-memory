import sys,json,gzip,itertools,hashlib,subprocess,os
from pathlib import Path
from collections import Counter
root=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(root))
from src.planning import Task,Edge,is_correct

def reference(t,a):
    vertices={t['start'],t['goal']}|{e[k] for e in t['edges'] for k in ('source','destination')}
    d={(t['start'],t['start']==t['key_at']):0}
    for _ in range(2*len(vertices)-1):
        old=d.copy()
        for (v,key),cost in old.items():
            for e in t['edges']:
                if e['source']==v and (key or not e['requires_key']):
                    z=(e['destination'],key or e['destination']==t['key_at'])
                    d[z]=min(d.get(z,10**9),cost+1)
    best=min((n for (v,_),n in d.items() if v==t['goal']),default=None)
    if not isinstance(a,dict):return False
    if set(a)=={'unreachable'}:return a['unreachable'] is True and best is None
    if set(a)!={'path'}:return False
    p=a['path']
    if not isinstance(p,list) or not p or any(not isinstance(v,str) for v in p):return False
    if p[0]!=t['start'] or p[-1]!=t['goal'] or len(p)-1!=best:return False
    key=p[0]==t['key_at']
    for v,w in zip(p,p[1:]):
        if not any(e['source']==v and e['destination']==w and (key or not e['requires_key']) for e in t['edges']):return False
        key=key or w==t['key_at']
    return True

experiments=['E002-admission','E003-transfer','E004-representation','E006-cross-model','E008-end-to-end','E009-matched-labels','E010-single-query','E012-rare-only','E013-diverse-paths']
stats={}
for exp in experiments:
    s=Counter()
    for f in sorted((root/'experiments'/exp/'results').rglob('calls.jsonl.gz')):
        for line in gzip.decompress(f.read_bytes()).splitlines():
            row=json.loads(line);p=json.loads(row['prompt']);s['calls']+=1
            try: a=json.loads(row['response']).get('answers',{})
            except (ValueError,AttributeError):a={}
            if not isinstance(a,dict):a={}
            for t in p['tasks']:
                answer=a.get(t['id']);task=Task(t['start'],t['goal'],tuple(Edge(**e) for e in t['edges']),t['key_at'])
                expected=reference(t,answer);actual=is_correct(task,answer)
                if expected!=actual:raise ValueError((exp,f,t['id'],expected,actual))
                s['answer_checks']+=1;s['correct']+=expected
            s['max_prompt_tokens']=max(s['max_prompt_tokens'],row.get('prompt_tokens') or 0)
            s['max_output_tokens']=max(s['max_output_tokens'],row.get('output_tokens') or 0)
    stats[exp]=dict(s)
d=[3,6,-4,2,-1,1]
p=sum(abs(sum(x*y for x,y in zip(s,d)))>=abs(sum(d)) for s in itertools.product((-1,1),repeat=6))/64
result={'independent_scorer':stats,'e009_posthoc_sign_flip':{'differences_out_of_six':d,'p_two_sided':p,'interpretation':'Exploratory sensitivity under sign exchangeability; not a preregistered test or proof of no effect.'}}
print(json.dumps(result,indent=2))
