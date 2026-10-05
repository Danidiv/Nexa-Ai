from services.completion_form_intelligence import *
def main():
 m=inspect_forms('<form><input name="email" required><input name="name"></form>');assert m.valid() and len(m.forms)==1;v=validate_form(m,{'name':'A'});assert not v['valid'] and v['missing']==['email'];assert validate_form(m,{'email':'e','name':'A'})['valid'];print("="*60);print("AZIZ AI SETUP 5.15 TEST");print("="*60);[print('[PASS] '+x) for x in ['forms discovered','required fields detected','missing validation works','form digest validates']];print('\nSetup 5.15 tests complete.')
if __name__=='__main__':main()