"""Setup 5.04: page navigation and URL control.
Transport-neutral navigation commands plus an optional HTTP reachability probe.
"""
from __future__ import annotations
from dataclasses import dataclass,asdict
from hashlib import sha256
from urllib.parse import urlparse
from urllib.request import Request,urlopen
import json,time
VERSION=1

def _digest(p):return sha256(json.dumps(p,sort_keys=True,separators=(',',':')).encode()).hexdigest()[:24]
@dataclass
class NavigationResult:
    action:str; requested_url:str; final_url:str=''; status_code:int=0; elapsed_ms:int=0; success:bool=False; error:str=''; digest:str=''
    def seal(self):self.digest=_digest({k:getattr(self,k) for k in ('action','requested_url','final_url','status_code','elapsed_ms','success','error')});return self
    def to_dict(self):d=asdict(self);d['browser_navigation_version']=VERSION;return d
    def valid(self):return self.digest==_digest({k:getattr(self,k) for k in ('action','requested_url','final_url','status_code','elapsed_ms','success','error')})

def validate_url(url,allowed_hosts=None):
    u=urlparse(str(url));
    if u.scheme not in {'http','https'}:return False
    if allowed_hosts is None:return True
    return (u.hostname or '').lower() in {str(x).lower() for x in allowed_hosts}

def navigate(url,allowed_hosts=None,timeout=5):
    started=time.monotonic(); r=NavigationResult('navigate',str(url))
    if not validate_url(url,allowed_hosts):r.error='URL is outside browser safety policy';return r.seal()
    try:
        req=Request(str(url),headers={'User-Agent':'AZIZ-AI-Browser/5.04'})
        with urlopen(req,timeout=timeout) as resp:
            r.final_url=resp.geturl();r.status_code=int(resp.status);r.success=200<=r.status_code<400
    except Exception as e:r.error=f'{type(e).__name__}: {e}'
    r.elapsed_ms=int((time.monotonic()-started)*1000);return r.seal()

def navigation_plan(url):
    return [{'action':'navigate','url':str(url)},{'action':'wait_for_page','timeout_ms':5000},{'action':'read_current_url'}]
