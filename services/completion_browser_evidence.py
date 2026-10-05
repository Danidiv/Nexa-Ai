"""Setup 5.07: screenshot and visual evidence contract.
A driver may expose screenshot(); bytes are represented by metadata/hash, never persisted as raw data here.
"""
from __future__ import annotations
from dataclasses import dataclass,asdict
from hashlib import sha256
import json,time
VERSION=1

def _digest(p):return sha256(json.dumps(p,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()[:24]
@dataclass
class VisualEvidence:
    kind:str='screenshot'; path:str=''; sha256_hex:str=''; captured_at:float=0.0; width:int=0; height:int=0; digest:str=''
    def seal(self):self.digest=_digest({'kind':self.kind,'path':self.path,'sha256_hex':self.sha256_hex,'captured_at':self.captured_at,'width':self.width,'height':self.height});return self
    def to_dict(self):d=asdict(self);d['browser_evidence_version']=VERSION;return d
    def valid(self):return self.digest==_digest({'kind':self.kind,'path':self.path,'sha256_hex':self.sha256_hex,'captured_at':self.captured_at,'width':self.width,'height':self.height})

def capture_screenshot(driver,path):
    if not hasattr(driver,'screenshot'):return VisualEvidence(path=str(path),captured_at=time.time()).seal()
    try:
        data=driver.screenshot(str(path)); raw=data if isinstance(data,(bytes,bytearray)) else b''
        digest=sha256(raw).hexdigest() if raw else ''
        return VisualEvidence(path=str(path),sha256_hex=digest,captured_at=time.time()).seal()
    except Exception:return VisualEvidence(path=str(path),captured_at=time.time()).seal()
