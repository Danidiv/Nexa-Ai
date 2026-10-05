"""Setup 4.99: deterministic browser page/DOM inspection.
Parses supplied HTML snapshots without launching a browser or executing scripts.
"""
from __future__ import annotations
from dataclasses import dataclass,asdict
from hashlib import sha256
from html.parser import HTMLParser
import json
VERSION=1; MAX_ELEMENTS=240
class _Parser(HTMLParser):
    def __init__(self): super().__init__(); self.elements=[]; self._stack=[]
    def handle_starttag(self,tag,attrs):
        attrs={str(k):str(v or '') for k,v in attrs}; item={'tag':tag.lower(),'attrs':attrs,'text':''}; self.elements.append(item); self._stack.append(item)
    def handle_data(self,data):
        if self._stack:self._stack[-1]['text']+=(data or '').strip()
    def handle_endtag(self,tag):
        if self._stack:self._stack.pop()
def _digest(p):return sha256(json.dumps(p,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()[:24]
@dataclass
class PageInspection:
    url:str; title:str; elements:list[dict]; forms:int; links:int; buttons:int; digest:str
    def to_dict(self):d=asdict(self);d['page_inspection_version']=VERSION;return d
    @classmethod
    def from_dict(cls,d):
        if not isinstance(d,dict) or d.get('page_inspection_version')!=VERSION:return None
        try:return cls(str(d.get('url','')),str(d.get('title','')),[dict(x) for x in d.get('elements',[])][:MAX_ELEMENTS],int(d.get('forms',0)),int(d.get('links',0)),int(d.get('buttons',0)),str(d.get('digest','')))
        except Exception:return None
    def valid(self):return _digest({'url':self.url,'title':self.title,'elements':self.elements,'forms':self.forms,'links':self.links,'buttons':self.buttons})==self.digest
def inspect_html(html,url=''):
    p=_Parser(); p.feed(html or ''); elems=p.elements[:MAX_ELEMENTS]; title=next((x['text'] for x in elems if x['tag']=='title' and x['text']), '')
    forms=sum(x['tag']=='form' for x in elems); links=sum(x['tag']=='a' for x in elems); buttons=sum(x['tag'] in {'button','input'} and (x['tag']=='button' or x['attrs'].get('type','').lower() in {'button','submit'}) for x in elems)
    payload={'url':str(url),'title':title,'elements':elems,'forms':forms,'links':links,'buttons':buttons}; return PageInspection(**payload,digest=_digest(payload))
