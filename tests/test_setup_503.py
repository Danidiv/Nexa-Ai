import sys
from services.completion_browser_launcher import BrowserLauncher

def main():
 b=BrowserLauncher(sys.executable,9333,'-c'); assert b.command()[0]==sys.executable and '--remote-debugging-port=9333' in b.command(); assert b.state.valid(); b.process=None; b.state.status='ready'; b.state.seal(); assert b.state.valid()
 print('='*60);print('AZIZ AI SETUP 5.03 TEST');print('='*60)
 for x in ['browser command built','debug port configured','lifecycle state validates','launch boundary is explicit']:print('[PASS] '+x)
 print('\nSetup 5.03 tests complete.')
if __name__=='__main__':main()
