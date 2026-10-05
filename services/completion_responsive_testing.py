from hashlib import sha256
import json
VERSION=1
def _d(p): return sha256(json.dumps(p,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()[:24]
def test_viewports(url,viewports=None):
 viewports=viewports or [{'name':'mobile','width':390,'height':844},{'name':'tablet','width':768,'height':1024},{'name':'desktop','width':1440,'height':900}]; results=[{'name':v['name'],'width':int(v['width']),'height':int(v['height']),'url':url,'status':'ready'} for v in viewports]; payload={'url':url,'results':results}; return {'version':VERSION,'results':results,'digest':_d(payload)}
def valid_responsive(r):
 results=r.get('results',[]); url=results[0]['url'] if results else ''; return isinstance(r,dict) and r.get('version')==VERSION and r.get('digest')==_d({'url':url,'results':results})
