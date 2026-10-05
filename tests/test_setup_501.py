from pathlib import Path
from services.completion_browser_runtime_integration import browser_runtime_report, validate_browser_runtime_report

def main():
    d = Path('tests/.tmp501')
    d.mkdir(exist_ok=True)
    (d/'package.json').write_text('{"scripts":{"dev":"vite"},"dependencies":{"react":"1"}}')
    html = '<html><head><title>App</title></head><body><button>Go</button></body></html>'
    (d/'index.html').write_text(html)
    (d/'main.py').write_text('def application():\n    return 1\n')
    r = browser_runtime_report(str(d), html, 'http://localhost:5173', 'application')
    assert r['status'] == 'ready' and validate_browser_runtime_report(r)
    tam = dict(r); tam['digest'] = 'bad'
    assert not validate_browser_runtime_report(tam)
    tam = dict(r); tam['flow'] = dict(r['flow']); tam['flow']['actions'] = []
    assert not validate_browser_runtime_report(tam)
    print('='*60); print('AZIZ AI SETUP 5.01 TEST'); print('='*60)
    for x in ['browser + runtime + codebase contract validates','tampered digest rejected','tampered flow rejected']:
        print('[PASS] ' + x)
    print('\nSetup 5.01 tests complete.')
if __name__ == '__main__': main()
