"""Setup 5.82: multi-tab browser target intelligence."""
from dataclasses import dataclass,asdict
from hashlib import sha256
import json
VERSION=1
def _d(p): return sha256(json.dumps(p,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()[:24]
@dataclass
class BrowserTab:
    tab_id:str; url:str=''; title:str=''; active:bool=False
@dataclass
class TabRegistry:
    tabs:list; active_tab:str=''; digest:str=''
    def seal(self):
        payload={'tabs':[asdict(t) if isinstance(t,BrowserTab) else t for t in self.tabs],'active_tab':self.active_tab}; self.digest=_d(payload); return self
    def to_dict(self): return {'browser_tabs_version':VERSION,'tabs':[asdict(t) if isinstance(t,BrowserTab) else t for t in self.tabs],'active_tab':self.active_tab,'digest':self.digest}
    def valid(self): return _d({'tabs':[asdict(t) if isinstance(t,BrowserTab) else t for t in self.tabs],'active_tab':self.active_tab})==self.digest
def register_tabs(tabs,active_tab=''):
    items=[t if isinstance(t,BrowserTab) else BrowserTab(str(t.get('tab_id','')),str(t.get('url','')),str(t.get('title','')),bool(t.get('active',False))) for t in tabs]
    if active_tab:
        for t in items:t.active=t.tab_id==active_tab
    return TabRegistry(items,active_tab).seal()
def activate(registry,tab_id):
    for t in registry.tabs:
        if t.tab_id==tab_id:
            registry.active_tab=tab_id
            for x in registry.tabs:x.active=x.tab_id==tab_id
            return registry.seal()
    return None
