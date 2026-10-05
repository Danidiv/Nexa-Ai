"""Setup 4.77: append-only terminal lifecycle transition ledger."""
from dataclasses import dataclass, asdict
from hashlib import sha256
import json
VERSION=1
MAX_ENTRIES=64

def _digest(v): return sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()[:24]
@dataclass
class TransitionEntry:
    sequence:int
    source:str
    target:str
    reason:str
    previous_digest:str=""
    entry_digest:str=""
    def seal(self, previous_digest=""):
        self.previous_digest=previous_digest
        self.entry_digest=_digest({"v":VERSION,"sequence":self.sequence,"source":self.source,"target":self.target,"reason":self.reason,"previous_digest":self.previous_digest})
        return self.entry_digest

@dataclass
class TransitionLedger:
    entries:list
    head_digest:str=""
    def __init__(self, entries=None, head_digest=""):
        self.entries=list(entries or []); self.head_digest=head_digest
    def append(self, source,target,reason="transition"):
        seq=(self.entries[-1].sequence+1) if self.entries else 1
        e=TransitionEntry(seq,str(source),str(target),str(reason)); e.seal(self.head_digest); self.entries.append(e); self.entries=self.entries[-MAX_ENTRIES:]; self.head_digest=e.entry_digest; return e
    def valid(self):
        prev=""; expected=self.entries[0].sequence if self.entries else 1
        for e in self.entries:
            if e.sequence!=expected:return False
            if e.seal(e.previous_digest)!=e.entry_digest:return False
            if expected>self.entries[0].sequence and e.previous_digest!=prev:return False
            prev=e.entry_digest; expected+=1
        return self.head_digest==prev and len(self.entries)<=MAX_ENTRIES
    def to_dict(self): return {"version":VERSION,"entries":[asdict(e) for e in self.entries],"head_digest":self.head_digest}
    @classmethod
    def from_dict(cls,d):
        if not isinstance(d,dict) or d.get("version",VERSION)!=VERSION:return None
        try:
            es=[TransitionEntry(int(x["sequence"]),str(x["source"]),str(x["target"]),str(x["reason"]),str(x.get("previous_digest","")),str(x.get("entry_digest",""))) for x in d.get("entries",[])]
            r=cls(es,str(d.get("head_digest", ""))); return r if r.valid() else None
        except (KeyError,TypeError,ValueError): return None
