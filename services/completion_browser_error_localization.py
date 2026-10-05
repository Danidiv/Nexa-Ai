"""Setup 5.88: evidence-bound browser error to code localization."""
from dataclasses import dataclass,asdict
from hashlib import sha256
import json,re
VERSION=1
def _d(p):return sha256(json.dumps(p,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()[:24]
@dataclass
class CodeCandidate:
    path:str; reason:str; score:float
def localize_browser_error(error,index):
 q=str(error).lower(); out=[]
 for item in index or []:
  path=str(item.get('path','')); content=str(item.get('content','')).lower(); score=0
  for token in re.findall(r'[a-z_]{4,}',q):
   if token in content:score+=1
  if path.lower().endswith(('.js','.ts','.jsx','.tsx','.py')) and score:out.append(CodeCandidate(path,'error tokens matched source content',min(1,score/5)))
 out.sort(key=lambda x:(-x.score,x.path)); payload={'error':str(error),'candidates':[asdict(x) for x in out[:8]]};return {**payload,'digest':_d(payload)}
def valid_localization(r):return r.get('digest')==_d({'error':r.get('error',''),'candidates':r.get('candidates',[])})
