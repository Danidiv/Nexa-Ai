from hashlib import sha256
import json
VERSION=1
def _d(p): return sha256(json.dumps(p,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()[:24]
def build_accessibility_repair(report):
 actions=[{'rule':c['rule'],'action':'repair','count':c['violations']} for c in report.get('checks',[]) if c.get('violations',0)]; payload={'source_digest':report.get('digest'),'actions':actions}; return {'version':VERSION,**payload,'digest':_d(payload)}
def valid_accessibility_repair(r,report):
 payload={'source_digest':r.get('source_digest'),'actions':r.get('actions')}; return isinstance(r,dict) and r.get('version')==VERSION and r.get('source_digest')==report.get('digest') and r.get('digest')==_d(payload)
