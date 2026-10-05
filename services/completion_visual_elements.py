"""Setup 5.83: DOM + screenshot visual element intelligence."""
from dataclasses import dataclass,asdict
from hashlib import sha256
import json,re
VERSION=1
def _d(p):return sha256(json.dumps(p,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()[:24]
@dataclass
class VisualElement:
    element_id:str; tag:str; text:str=''; selector:str=''; bbox:dict=None; confidence:float=1.0
    def __post_init__(self):self.bbox=dict(self.bbox or {})
@dataclass
class VisualModel:
    url:str; elements:list; screenshot_hash:str=''; digest:str=''
    def seal(self): self.digest=_d({'url':self.url,'elements':[asdict(x) if isinstance(x,VisualElement) else x for x in self.elements],'screenshot_hash':self.screenshot_hash});return self
    def to_dict(self):return {'visual_model_version':VERSION,'url':self.url,'elements':[asdict(x) if isinstance(x,VisualElement) else x for x in self.elements],'screenshot_hash':self.screenshot_hash,'digest':self.digest}
    def valid(self):return _d({'url':self.url,'elements':[asdict(x) if isinstance(x,VisualElement) else x for x in self.elements],'screenshot_hash':self.screenshot_hash})==self.digest
def build_visual_model(url,dom,screenshot_bytes=b''):
    els=[]
    for i,m in enumerate(re.finditer(r'<(button|input|a|textarea|select)\b([^>]*)>(.*?)</\1>',dom or '',re.I|re.S)):
        tag,attrs,text=m.groups(); text=re.sub(r'<[^>]+>',' ',text).strip(); ident=re.search(r'id=["\']([^"\']+)',attrs,re.I); selector='#'+ident.group(1) if ident else f'{tag.lower()}:nth-of-type({i+1})'; els.append(VisualElement(f'e{i+1}',tag.lower(),text,selector,{},0.95))
    sh=sha256(screenshot_bytes).hexdigest()[:24] if screenshot_bytes else ''; return VisualModel(str(url),els,sh).seal()
