import os,sys,subprocess,json,time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
repo=Path(__file__).resolve().parents[3]
out=Path(__file__).resolve().parent
a='experiments/E002-admission/results/qwen3-8b';b='experiments/E003-transfer/results/qwen3-8b'
jobs=[]
for e in ['E000-oracle-smoke','E001-memory-coverage','E002-admission','E013-diverse-paths']:
 jobs.append((e+'-tests',['-m','unittest','discover','-s','experiments/'+e],None))
def add(name,mod,args,target): jobs.append((name,['-m',mod]+args,target))
add('E002-replay','src.admission_audit',[a],None)
add('E002','src.admission_report',[a],'experiments/E002-admission/results/aggregate.json')
add('E003','src.transfer_report',[a,b],'experiments/E003-transfer/results/aggregate.json')
add('E004','src.representation_report',[a,b,'experiments/E004-representation/results/qwen3-8b'],'experiments/E004-representation/results/aggregate.json')
jobs.append(('E005',['experiments/E005-fifo-null/verify.py'],None))
add('E006','src.representation_report',[a,b,'experiments/E006-cross-model/results/gemma-e4b','--cross-model'],'experiments/E006-cross-model/results/aggregate.json')
add('E006-completeness','src.gemma_diagnostics',['experiments/E006-cross-model/results/gemma-e4b'],'experiments/E006-cross-model/results/completeness.json')
add('E007','src.path_errors',[a,b],'experiments/E007-error-audit/results/aggregate.json')
add('E008','src.end_to_end',['experiments/E008-end-to-end/results/qwen3-8b','--audit'],'experiments/E008-end-to-end/results/aggregate.json')
add('E009','src.matched_labels',[a,'experiments/E009-matched-labels/results/qwen3-8b','--audit'],'experiments/E009-matched-labels/results/aggregate.json')
add('E010','src.gemma_diagnostics',['experiments/E010-single-query/results/gemma-e4b','--source',a],'experiments/E010-single-query/results/aggregate.json')
add('E011','experiments.E011-manuscript-audit.check',[],'experiments/E011-manuscript-audit/results.json')
c='experiments/E012-rare-only/results/qwen3-8b';d='experiments/E013-diverse-paths/results/qwen3-8b'
add('E012','src.rare_only',[c,'--audit'],c+'/aggregate.json')
add('E013','src.diverse_paths',[a,c,d,'--audit'],d+'/aggregate.json')
def run(job):
 name,args,target=job;t=time.time()
 p=subprocess.run([sys.executable]+args,cwd=repo,capture_output=True,text=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
 (out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr)
 r={'check':name,'command':[sys.executable]+args,'exit_code':p.returncode,'seconds':round(time.time()-t,2)}
 if target:
  try:r['matches_archived_json']=json.loads(p.stdout)==json.loads((repo/target).read_text())
  except Exception as e:r['comparison_error']=str(e)
 r['passed']=p.returncode==0 and r.get('matches_archived_json',True) and 'comparison_error' not in r
 print(json.dumps(r),flush=True);return r
with ThreadPoolExecutor(max_workers=3) as pool: results=list(pool.map(run,jobs))
(out/'checks.json').write_text(json.dumps(results,indent=2)+'\n')
print('TOTAL',sum(r['passed'] for r in results),'/',len(results),flush=True)
