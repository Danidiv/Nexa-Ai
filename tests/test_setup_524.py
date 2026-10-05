from services.completion_responsive_testing import *
def main():
 r=test_viewports('http://localhost:5173'); assert valid_responsive(r) and len(r['results'])==3 and r['results'][0]['width']==390; print('[PASS] viewports generated'); print('[PASS] mobile/tablet/desktop covered'); print('[PASS] digest validates'); print('[PASS] bounded results')
if __name__=='__main__': main()
