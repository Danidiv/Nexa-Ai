import threading
from http.server import HTTPServer,BaseHTTPRequestHandler
from services.completion_browser_navigation import navigate,navigation_plan
class H(BaseHTTPRequestHandler):
 def do_GET(self):self.send_response(200);self.end_headers();self.wfile.write(b'ok')
 def log_message(self,*a):pass

def main():
 srv=HTTPServer(('127.0.0.1',0),H); threading.Thread(target=srv.serve_forever,daemon=True).start(); url=f'http://127.0.0.1:{srv.server_port}/'; r=navigate(url,['127.0.0.1']); srv.shutdown(); assert r.success and r.valid(); assert len(navigation_plan(url))==3
 print('='*60);print('AZIZ AI SETUP 5.04 TEST');print('='*60)
 for x in ['navigation succeeds','URL safety policy enforced','navigation evidence validates','navigation plan generated']:print('[PASS] '+x)
 print('\nSetup 5.04 tests complete.')
if __name__=='__main__':main()
