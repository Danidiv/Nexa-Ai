"""Setup 5.03: real browser launch/connection boundary.
Uses Chromium-family executables when available. Launching is explicit; tests may use a supplied executable.
"""
from __future__ import annotations
from dataclasses import dataclass,asdict
from hashlib import sha256
from pathlib import Path
import json, os, shutil, subprocess, time
VERSION=1

def _digest(p): return sha256(json.dumps(p,sort_keys=True,separators=(',',':')).encode()).hexdigest()[:24]

def find_browser(candidates=None):
    names=candidates or ['chrome','chrome.exe','chromium','chromium.exe','msedge','msedge.exe']
    for n in names:
        p=shutil.which(n)
        if p:return p
    windows=[r'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',r'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',r'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe']
    for p in windows:
        if Path(p).exists():return p
    return ''

@dataclass
class BrowserLaunchState:
    status:str='not_started'; executable:str=''; debug_port:int=0; pid:int=0; url:str=''; started_at:float=0.0; digest:str=''
    def seal(self):
        self.digest=_digest({k:getattr(self,k) for k in ('status','executable','debug_port','pid','url','started_at')}); return self
    def to_dict(self):d=asdict(self);d['browser_launch_version']=VERSION;return d
    def valid(self):return self.digest==_digest({k:getattr(self,k) for k in ('status','executable','debug_port','pid','url','started_at')})

class BrowserLauncher:
    def __init__(self,executable='',debug_port=9222,url='about:blank'):
        self.executable=executable or find_browser(); self.debug_port=int(debug_port); self.url=str(url); self.process=None
        self.state=BrowserLaunchState(executable=self.executable,debug_port=self.debug_port,url=self.url).seal()
    def command(self):
        if not self.executable:return []
        return [self.executable,f'--remote-debugging-port={self.debug_port}','--new-window',self.url]
    def start(self):
        if self.state.status=='running':return False
        cmd=self.command()
        if not cmd:return False
        self.process=subprocess.Popen(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        self.state.status='running';self.state.pid=self.process.pid;self.state.started_at=time.time();self.state.seal();return True
    def stop(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
        self.state.status='stopped';self.state.pid=0;self.state.seal();return True
    def healthy(self):return self.state.status=='running' and self.process is not None and self.process.poll() is None
