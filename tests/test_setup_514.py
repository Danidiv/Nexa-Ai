from services.completion_visual_elements import build_visual_model
from services.completion_visual_targeting import *
def main():
 m=build_visual_model('u','<button id="save">Save</button>');t=target_element(m,'Save');assert t['status']=='matched' and valid_target(t);bad=dict(t);bad['selector']='#x';assert not valid_target(bad);assert target_element(m,'missing')['status']=='not_found';print("="*60);print("AZIZ AI SETUP 5.14 TEST");print("="*60);[print('[PASS] '+x) for x in ['visual target matched','target evidence validates','tamper detected','missing target handled']];print('\nSetup 5.14 tests complete.')
if __name__=='__main__':main()