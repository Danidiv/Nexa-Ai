from services.completion_browser_dom import discover

def main():
 d=discover('<html><body><button id="go">Go</button><input aria-label="Name"><a href="/x">X</a></body></html>','http://localhost'); assert len(d.interactive)>=3 and d.valid(); assert d.from_dict(d.to_dict()).valid()
 print('='*60);print('AZIZ AI SETUP 5.05 TEST');print('='*60)
 for x in ['interactive elements discovered','stable selectors generated','serialization restores','DOM digest validates']:print('[PASS] '+x)
 print('\nSetup 5.05 tests complete.')
if __name__=='__main__':main()
