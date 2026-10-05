"""Setup 5.86: bounded user-flow execution through a driver interface."""
from dataclasses import dataclass,asdict
from hashlib import sha256
import json
VERSION=1;MAX_ACTIONS=32
def _d(p):return sha256(json.dumps(p,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()[:24]
@dataclass
class FlowExecution:
    actions:list; results:list; status:str='pending'; digest:str=''
    def seal(self):self.digest=_d({'actions':self.actions,'results':self.results,'status':self.status});return self
    def valid(self):return _d({'actions':self.actions,'results':self.results,'status':self.status})==self.digest
def execute_flow(driver,actions):
 actions=list(actions)[:MAX_ACTIONS]; results=[]
 for a in actions:
  try:
   op=a.get('action'); sel=a.get('selector',''); val=a.get('value','')
   if op=='click':r=driver.click(sel)
   elif op=='type':r=driver.type(sel,val)
   elif op=='select':r=driver.select(sel,val)
   elif op=='press':r=driver.press(val)
   elif op=='navigate':r=driver.navigate(val)
   else:r=False
   results.append({'action':op,'ok':bool(r),'evidence':str(r)})
  except Exception as e:results.append({'action':a.get('action'),'ok':False,'evidence':str(e)})
 status='passed' if all(x['ok'] for x in results) else 'failed';return FlowExecution(actions,results,status).seal()
