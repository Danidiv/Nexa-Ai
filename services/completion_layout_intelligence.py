from hashlib import sha256
import json,re
VERSION=1
def _d(p): return sha256(json.dumps(p,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()[:24]
def inspect_layout(html):
 items=[]
 for m in re.finditer(r'<([a-zA-Z][\w-]*)([^>]*)>',html):
  a=m.group(2); ident=re.search(r'id=["\']([^"\']+)',a); cls=re.search(r'class=["\']([^"\']+)',a); sel='#'+ident.group(1) if ident else ('.'+cls.group(1).split()[0] if cls else m.group(1)); items.append({'selector':sel,'tag':m.group(1),'box':{'x':0,'y':0,'width':0,'height':0}})
 payload={'elements':items[:32]}; return {'version':VERSION,'elements':items[:32],'digest':_d(payload)}
def valid_layout(r): return isinstance(r,dict) and r.get('version')==VERSION and r.get('digest')==_d({'elements':r.get('elements')})
