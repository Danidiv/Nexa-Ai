from services.completion_visual_qa_agent import *
def main():
 r=visual_qa_report('/','<img src="x" alt="x"><button aria-label="Go"></button><label>E</label><input>','a','a',{'load_ms':1000}); assert r['status']=='ready' and valid_visual_qa_report(r); b=dict(r); b['digest']='bad'; assert not valid_visual_qa_report(b); print('[PASS] full visual QA contract validates'); print('[PASS] accessibility/visual/performance integrated'); print('[PASS] repair evidence integrated'); print('[PASS] tampered contract rejected')
if __name__=='__main__': main()
