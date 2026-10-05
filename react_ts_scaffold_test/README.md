# React + TypeScript + shadcn/ui Scaffold Test

Real Lovable-parity foundation: TypeScript, real Tailwind build (not CDN),
real shadcn/ui component primitives (Button, Card, Input).

## Test on your machine

```bash
cd react_ts_scaffold_test
npm install
npx tsc --noEmit    # should show zero errors
npm run dev
```

Open http://localhost:5173/ - you should see a real shadcn-styled card
with a working button, dark near-black button background (shadcn's
default "primary" color), rounded corners, subtle shadow.
