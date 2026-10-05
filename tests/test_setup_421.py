from services.request_telemetry import RequestTelemetry

def main():
 print('='*60); print('AZIZ AI SETUP 4.21 TEST'); print('='*60)
 t=RequestTelemetry(); t.record(.1); t.record(.3); s=t.snapshot()
 assert s['count']==2 and s['total_seconds']==.4 and s['average_seconds']==.2
 print('[PASS] request timing statistics are accurate')
 assert s['min_seconds']==.1 and s['max_seconds']==.3
 print('[PASS] min/max request duration are tracked')
 t.reset(); assert t.snapshot()['count']==0; print('[PASS] timing statistics can be reset')
 with t.measure(): pass
 assert t.snapshot()['count']==1; print('[PASS] context manager records completed requests')
 assert set(t.snapshot())=={'count','total_seconds','average_seconds','min_seconds','max_seconds'}
 print('[PASS] telemetry diagnostics expose safe fields only')
 print('\nSetup 4.21 tests complete.')
if __name__=='__main__': main()
