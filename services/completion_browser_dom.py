"""Setup 5.05: DOM element discovery on supplied page snapshots."""
from __future__ import annotations
from dataclasses import dataclass,asdict
from hashlib import sha256
from html.parser import HTMLParser
import json,re
VERSION=1; MAX_ELEMENTS=320
class _P(HTMLParser):
    def __init__(self):super().__init__();self.items=[];self.stack=[]
    def handle_starttag(self,t,a):
        attrs={str(k):str(v or '') for k,v in a}; item={'tag':t.lower(),'attrs':attrs,'text':''};self.items.append(item);self.stack.append(item)
    def handle_data(self,d):
        if self.stack:self.stack[-1]['text']+=(d or '').strip()
    def handle_endtag(self,t):
        if self.stack:self.stack.pop()
def _digest(p):return sha256(json.dumps(p,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()[:24]
@dataclass
class DOMDiscovery:
    url:str; elements:list[dict]; interactive:list[dict]; digest:str
    def to_dict(self):d=asdict(self);d['browser_dom_version']=VERSION;return d
    @classmethod
    def from_dict(cls,d):
        if not isinstance(d,dict) or d.get('browser_dom_version')!=VERSION:return None
        return cls(str(d.get('url','')),[dict(x) for x in d.get('elements',[])][:MAX_ELEMENTS],[dict(x) for x in d.get('interactive',[])][:MAX_ELEMENTS],str(d.get('digest','')))
    def valid(self):return self.digest==_digest({'url':self.url,'elements':self.elements,'interactive':self.interactive})
def discover(html,url=''):
    p=_P();p.feed(html or '');els=p.items[:MAX_ELEMENTS];interactive=[]
    for i,e in enumerate(els):
        tag=e['tag'];a=e['attrs']
        if tag in {'button','a','input','textarea','select'} or any(k in a for k in ('onclick','role','data-testid','aria-label')):
            selector=('#'+a['id']) if a.get('id') else ('.'+a['class'].split()[0] if a.get('class') else f'{tag}:nth-of-type({i+1})')
            interactive.append({'index':i,'tag':tag,'selector':selector,'text':e['text'],'role':a.get('role',''),'aria_label':a.get('aria-label',''),'test_id':a.get('data-testid',''),'type':a.get('type','')})
    payload={'url':str(url),'elements':els,'interactive':interactive};return DOMDiscovery(**payload,digest=_digest(payload))
