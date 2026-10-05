from services.completion_visual_elements import *
def main():
 r=build_visual_model('http://localhost:1','<button id="go">Go</button><input id="email"></input>',b'img');assert r.valid() and len(r.elements)==2 and r.screenshot_hash;print("="*60);print("AZIZ AI SETUP 5.13 TEST");print("="*60);[print('[PASS] '+x) for x in ['DOM + visual model built','interactive elements mapped','screenshot hash recorded','visual digest validates']];print('\nSetup 5.13 tests complete.')
if __name__=='__main__':main()