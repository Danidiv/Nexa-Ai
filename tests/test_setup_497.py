from pathlib import Path
from services.completion_browser_intelligence import discover_browser_surface
def main():
 d=Path("tests/.tmp497");d.mkdir(exist_ok=True);(d/"index.html").write_text("<a href=/x>x</a>");(d/"app.js").write_text("http://localhost:5173/home");r=discover_browser_surface(d);assert r.urls and r.routes and r.valid();x=r.to_dict();assert type(r.from_dict(x)).__name__=="BrowserSurface";print("="*60);print("AZIZ AI SETUP 4.97 TEST");print("="*60);[print("[PASS] "+x) for x in ["preview URL discovered","browser artifacts detected","serialization restores","surface digest validates"]];print("\nSetup 4.97 tests complete.")
if __name__=="__main__":main()
