from hashlib import sha256
import json
VERSION=1
def _d(p): return sha256(json.dumps(p,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()[:24]
def inspect_accessibility(html):
 checks=[{'rule':'images-alt','violations':max(0,html.lower().count('<img')-html.lower().count('alt='))},{'rule':'buttons-name','violations':max(0,html.lower().count('<button')-html.lower().count('aria-label'))},{'rule':'inputs-label','violations':max(0,html.lower().count('<input')-html.lower().count('<label'))}]
 payload={'html_length':len(html),'checks':checks}
 return {'version':VERSION,'html_length':len(html),'status':'pass' if all(c['violations']==0 for c in checks) else 'issues','checks':checks,'digest':_d(payload)}
def valid_accessibility(r): return isinstance(r,dict) and r.get('version')==VERSION and r.get('digest')==_d({'html_length':r.get('html_length'),'checks':r.get('checks')})
