from services.completion_visual_development_agent import *
def main():
 r=development_report('.', 'http://localhost:5173','<button id="go">Go</button>');assert r['status']=='ready' and valid_development_report(r);b=dict(r);b['digest']='bad';assert not valid_development_report(b);print("="*60);print("AZIZ AI SETUP 5.20 TEST");print("="*60);[print('[PASS] '+x) for x in ['full visual development contract validates','browser layers integrated','state and repair evidence integrated','tampered contract rejected']];print('\nSetup 5.20 tests complete.')
if __name__=='__main__':main()